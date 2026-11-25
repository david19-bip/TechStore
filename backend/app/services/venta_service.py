"""Lógica transaccional para Ventas (validación de stock, cálculos, kardex y auditoría)."""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.movimiento_inventario import MovimientoInventario
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta, Venta
from app.repositories import cliente_repo, venta_repo
from app.schemas.venta import VentaCreate
from app.services import auditoria_service

DOS_DECIMALES = Decimal("0.01")


def _redondear(valor: Decimal) -> Decimal:
    return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def _generar_numero_factura() -> str:
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d")
    sufijo = uuid4().hex[:6].upper()
    return f"FV-{fecha}-{sufijo}"


def listar(
    db: Session,
    id_cliente: int | None = None,
    id_usuario: int | None = None,
    estado: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
) -> list[Venta]:
    return venta_repo.listar_ventas(
        db,
        id_cliente=id_cliente,
        id_usuario=id_usuario,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


def obtener(db: Session, id_venta: int) -> Venta:
    venta = venta_repo.obtener_por_id(db, id_venta)
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la venta con id {id_venta}.",
        )
    return venta


def registrar_venta(
    db: Session,
    datos: VentaCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Venta:
    """Registra una venta en una transacción atómica impidiendo vender más del stock."""
    cliente = cliente_repo.obtener_por_id(db, datos.id_cliente)
    if not cliente or cliente.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un cliente activo con id {datos.id_cliente}.",
        )

    numero_factura = (
        datos.numero_factura.strip()
        if datos.numero_factura
        else _generar_numero_factura()
    )
    if venta_repo.obtener_por_factura(db, numero_factura):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una venta registrada con la factura '{numero_factura}'.",
        )

    ids_productos = [item.id_producto for item in datos.detalles]
    if len(ids_productos) != len(set(ids_productos)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten productos repetidos dentro de la misma venta.",
        )

    try:
        # Bloquear productos en orden determinista para evitar sobreventa concurrente
        productos_bloqueados = (
            db.query(Producto)
            .filter(Producto.id_producto.in_(sorted(ids_productos)))
            .with_for_update()
            .all()
        )
        mapa_productos = {p.id_producto: p for p in productos_bloqueados}

        subtotal_acumulado = Decimal("0.00")
        descuento_acumulado = Decimal("0.00")
        lineas_preparadas: list[tuple[Producto, int, Decimal, Decimal]] = []

        for item in datos.detalles:
            producto = mapa_productos.get(item.id_producto)
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No existe el producto con id {item.id_producto}.",
                )
            if producto.estado != "activo":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El producto '{producto.nombre}' se encuentra inactivo.",
                )
            if producto.stock_actual < item.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Stock insuficiente para '{producto.nombre}' (SKU {producto.sku}): "
                        f"disponible {producto.stock_actual}, solicitado {item.cantidad}."
                    ),
                )

            precio_unit = _redondear(
                item.precio_unitario
                if item.precio_unitario is not None
                else producto.precio_venta
            )
            bruto_linea = _redondear(Decimal(item.cantidad) * precio_unit)
            descuento_linea = _redondear(item.descuento)
            if descuento_linea > bruto_linea:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"El descuento (${descuento_linea}) del producto '{producto.nombre}' "
                        f"no puede superar el valor bruto de la línea (${bruto_linea})."
                    ),
                )

            subtotal_linea = _redondear(bruto_linea - descuento_linea)
            subtotal_acumulado += subtotal_linea
            descuento_acumulado += descuento_linea
            lineas_preparadas.append(
                (producto, item.cantidad, precio_unit, descuento_linea)
            )

        subtotal_acumulado = _redondear(subtotal_acumulado)
        descuento_acumulado = _redondear(descuento_acumulado)
        impuesto = _redondear(
            subtotal_acumulado * (datos.impuesto_porcentaje / Decimal("100"))
        )
        total = _redondear(subtotal_acumulado + impuesto)

        venta = Venta(
            id_cliente=datos.id_cliente,
            id_usuario=actor.id_usuario,
            numero_factura=numero_factura,
            metodo_pago=datos.metodo_pago,
            subtotal=subtotal_acumulado,
            impuesto=impuesto,
            descuento_total=descuento_acumulado,
            total=total,
            estado="pagada",
            observaciones=datos.observaciones.strip() if datos.observaciones else None,
        )
        db.add(venta)
        db.flush()

        for producto, cantidad, precio_unit, descuento_linea in lineas_preparadas:
            db.add(
                DetalleVenta(
                    id_venta=venta.id_venta,
                    id_producto=producto.id_producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unit,
                    descuento=descuento_linea,
                )
            )

            stock_anterior = producto.stock_actual
            stock_nuevo = stock_anterior - cantidad
            producto.stock_actual = stock_nuevo

            db.add(
                MovimientoInventario(
                    id_producto=producto.id_producto,
                    id_usuario=actor.id_usuario,
                    id_compra=None,
                    id_venta=venta.id_venta,
                    tipo_movimiento="salida_venta",
                    cantidad=cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    motivo=f"Salida por venta factura {numero_factura}",
                )
            )

        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="ventas",
            tabla_afectada="ventas",
            registro_id=venta.id_venta,
            accion="INSERT",
            datos_nuevos={
                "id_venta": venta.id_venta,
                "id_cliente": venta.id_cliente,
                "numero_factura": venta.numero_factura,
                "metodo_pago": venta.metodo_pago,
                "subtotal": venta.subtotal,
                "descuento_total": venta.descuento_total,
                "impuesto": venta.impuesto,
                "total": venta.total,
                "items": len(lineas_preparadas),
            },
            direccion_ip=direccion_ip,
        )

        db.commit()
        return obtener(db, venta.id_venta)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar la venta; la transacción fue revertida: {exc}",
        )


def anular_venta(
    db: Session,
    id_venta: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Venta:
    """Anula una venta y reintegra las existencias al inventario."""
    venta = obtener(db, id_venta)
    if venta.estado == "anulada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La venta ya se encuentra anulada.",
        )

    try:
        estado_anterior = venta.estado
        ids_productos = sorted(d.id_producto for d in venta.detalles)
        productos_bloqueados = (
            db.query(Producto)
            .filter(Producto.id_producto.in_(ids_productos))
            .with_for_update()
            .all()
        )
        mapa = {p.id_producto: p for p in productos_bloqueados}

        for det in venta.detalles:
            producto = mapa[det.id_producto]
            stock_anterior = producto.stock_actual
            stock_nuevo = stock_anterior + det.cantidad
            producto.stock_actual = stock_nuevo
            db.add(
                MovimientoInventario(
                    id_producto=producto.id_producto,
                    id_usuario=actor.id_usuario,
                    id_compra=None,
                    id_venta=None,
                    tipo_movimiento="devolucion",
                    cantidad=det.cantidad,
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    motivo=f"Devolución por anulación de venta factura {venta.numero_factura}",
                )
            )

        venta.estado = "anulada"
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="ventas",
            tabla_afectada="ventas",
            registro_id=venta.id_venta,
            accion="UPDATE",
            datos_anteriores={"estado": estado_anterior},
            datos_nuevos={"estado": "anulada"},
            direccion_ip=direccion_ip,
        )
        db.commit()
        return obtener(db, venta.id_venta)
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al anular la venta; la transacción fue revertida: {exc}",
        )
