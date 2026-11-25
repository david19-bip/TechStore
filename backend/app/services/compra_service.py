"""Lógica transaccional para Compras (encabezado, detalles, stock, kardex y auditoría)."""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.compra import Compra, DetalleCompra
from app.models.movimiento_inventario import MovimientoInventario
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.repositories import compra_repo, proveedor_repo
from app.schemas.compra import CompraCreate
from app.services import auditoria_service

DOS_DECIMALES = Decimal("0.01")


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def listar(
    db: Session,
    id_proveedor: int | None = None,
    estado: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
) -> list[Compra]:
    return compra_repo.listar_compras(
        db,
        id_proveedor=id_proveedor,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


def obtener(db: Session, id_compra: int) -> Compra:
    compra = compra_repo.obtener_por_id(db, id_compra)
    if not compra:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la compra con id {id_compra}.",
        )
    return compra


def registrar_compra(
    db: Session,
    datos: CompraCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Compra:
    """Registra una compra en una única transacción atómica (COMMIT o ROLLBACK)."""
    proveedor = proveedor_repo.obtener_por_id(db, datos.id_proveedor)
    if not proveedor or proveedor.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un proveedor activo con id {datos.id_proveedor}.",
        )

    factura_limpia = datos.numero_factura.strip()
    if compra_repo.obtener_por_proveedor_factura(db, datos.id_proveedor, factura_limpia):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"El proveedor '{proveedor.razon_social}' ya tiene registrada "
                f"la factura '{factura_limpia}'."
            ),
        )

    ids_productos = [item.id_producto for item in datos.detalles]
    if len(ids_productos) != len(set(ids_productos)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten productos repetidos dentro de la misma compra.",
        )

    try:
        # Bloquear productos ordenados por ID para evitar condiciones de carrera
        productos_bloqueados = (
            db.query(Producto)
            .filter(Producto.id_producto.in_(sorted(ids_productos)))
            .with_for_update()
            .all()
        )
        mapa_productos = {p.id_producto: p for p in productos_bloqueados}

        for item in datos.detalles:
            if item.id_producto not in mapa_productos:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No existe el producto con id {item.id_producto}.",
                )

        subtotal = sum(
            (Decimal(item.cantidad) * item.precio_unitario for item in datos.detalles),
            Decimal("0.00"),
        )
        subtotal = _redondear(subtotal)
        impuesto = _redondear(subtotal * (datos.impuesto_porcentaje / Decimal("100")))
        total = _redondear(subtotal + impuesto)

        compra = Compra(
            id_proveedor=datos.id_proveedor,
            id_usuario=actor.id_usuario,
            numero_factura=factura_limpia,
            subtotal=subtotal,
            impuesto=impuesto,
            total=total,
            estado=datos.estado,
            observaciones=datos.observaciones.strip() if datos.observaciones else None,
        )
        db.add(compra)
        db.flush()

        for item in datos.detalles:
            producto = mapa_productos[item.id_producto]
            detalle = DetalleCompra(
                id_compra=compra.id_compra,
                id_producto=producto.id_producto,
                cantidad=item.cantidad,
                precio_unitario=_redondear(item.precio_unitario),
            )
            db.add(detalle)

            if datos.estado == "recibida":
                stock_anterior = producto.stock_actual
                stock_nuevo = stock_anterior + item.cantidad
                producto.stock_actual = stock_nuevo

                # Actualizar costo de compra si mantiene precio_venta >= precio_compra
                if item.precio_unitario <= producto.precio_venta:
                    producto.precio_compra = _redondear(item.precio_unitario)

                movimiento = MovimientoInventario(
                    id_producto=producto.id_producto,
                    id_usuario=actor.id_usuario,
                    id_compra=compra.id_compra,
                    id_venta=None,
                    tipo_movimiento="entrada_compra",
                    cantidad=item.cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    motivo=f"Ingreso por compra factura {factura_limpia}",
                )
                db.add(movimiento)

        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="compras",
            tabla_afectada="compras",
            registro_id=compra.id_compra,
            accion="INSERT",
            datos_nuevos={
                "id_compra": compra.id_compra,
                "id_proveedor": compra.id_proveedor,
                "numero_factura": compra.numero_factura,
                "subtotal": compra.subtotal,
                "impuesto": compra.impuesto,
                "total": compra.total,
                "estado": compra.estado,
                "items": len(datos.detalles),
            },
            direccion_ip=direccion_ip,
        )

        db.commit()
        return obtener(db, compra.id_compra)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la compra; la transacción fue revertida: {exc}",
        )


def recibir_compra(
    db: Session,
    id_compra: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Compra:
    """Marca una compra 'pendiente' como 'recibida' e incrementa el inventario."""
    compra = obtener(db, id_compra)
    if compra.estado != "pendiente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo se pueden recibir compras en estado 'pendiente' (estado actual: '{compra.estado}').",
        )

    try:
        ids_productos = sorted(d.id_producto for d in compra.detalles)
        productos_bloqueados = (
            db.query(Producto)
            .filter(Producto.id_producto.in_(ids_productos))
            .with_for_update()
            .all()
        )
        mapa = {p.id_producto: p for p in productos_bloqueados}

        estado_anterior = compra.estado
        compra.estado = "recibida"

        for det in compra.detalles:
            producto = mapa[det.id_producto]
            stock_anterior = producto.stock_actual
            stock_nuevo = stock_anterior + det.cantidad
            producto.stock_actual = stock_nuevo

            db.add(
                MovimientoInventario(
                    id_producto=producto.id_producto,
                    id_usuario=actor.id_usuario,
                    id_compra=compra.id_compra,
                    id_venta=None,
                    tipo_movimiento="entrada_compra",
                    cantidad=det.cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    motivo=f"Recepción de compra factura {compra.numero_factura}",
                )
            )

        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="compras",
            tabla_afectada="compras",
            registro_id=compra.id_compra,
            accion="UPDATE",
            datos_anteriores={"estado": estado_anterior},
            datos_nuevos={"estado": "recibida"},
            direccion_ip=direccion_ip,
        )
        db.commit()
        return obtener(db, compra.id_compra)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recibir la compra; la transacción fue revertida: {exc}",
        )


def anular_compra(
    db: Session,
    id_compra: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Compra:
    """Anula una compra; si ya estaba recibida, revierte existencias de forma segura."""
    compra = obtener(db, id_compra)
    if compra.estado == "anulada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La compra ya se encuentra anulada.",
        )

    try:
        estado_anterior = compra.estado
        if estado_anterior == "recibida":
            ids_productos = sorted(d.id_producto for d in compra.detalles)
            productos_bloqueados = (
                db.query(Producto)
                .filter(Producto.id_producto.in_(ids_productos))
                .with_for_update()
                .all()
            )
            mapa = {p.id_producto: p for p in productos_bloqueados}

            for det in compra.detalles:
                producto = mapa[det.id_producto]
                if producto.stock_actual < det.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"No se puede anular la compra: el producto '{producto.nombre}' "
                            f"tiene stock {producto.stock_actual} y se requieren {det.cantidad} unidades para revertir."
                        ),
                    )
            for det in compra.detalles:
                producto = mapa[det.id_producto]
                stock_anterior = producto.stock_actual
                stock_nuevo = stock_anterior - det.cantidad
                producto.stock_actual = stock_nuevo
                db.add(
                    MovimientoInventario(
                        id_producto=producto.id_producto,
                        id_usuario=actor.id_usuario,
                        id_compra=None,
                        id_venta=None,
                        tipo_movimiento="ajuste_negativo",
                        cantidad=det.cantidad,
                        stock_anterior=stock_anterior,
                        stock_nuevo=stock_nuevo,
                        motivo=f"Reversión por anulación de compra factura {compra.numero_factura}",
                    )
                )

        compra.estado = "anulada"
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="compras",
            tabla_afectada="compras",
            registro_id=compra.id_compra,
            accion="UPDATE",
            datos_anteriores={"estado": estado_anterior},
            datos_nuevos={"estado": "anulada"},
            direccion_ip=direccion_ip,
        )
        db.commit()
        return obtener(db, compra.id_compra)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al anular la compra; la transacción fue revertida: {exc}",
        )
