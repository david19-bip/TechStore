"""Lógica de negocio para la entidad Producto (con existencias, desactivación y auditoría)."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.compra import DetalleCompra
from app.models.movimiento_inventario import MovimientoInventario
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta
from app.repositories import categoria_repo, producto_repo
from app.schemas.producto import ProductoCreate, ProductoUpdate
from app.services import auditoria_service


def _snapshot(p: Producto) -> dict:
    return {
        "id_producto": p.id_producto,
        "id_categoria": p.id_categoria,
        "sku": p.sku,
        "nombre": p.nombre,
        "marca": p.marca,
        "precio_compra": p.precio_compra,
        "precio_venta": p.precio_venta,
        "stock_actual": p.stock_actual,
        "stock_minimo": p.stock_minimo,
        "estado": p.estado,
    }


def listar(
    db: Session,
    id_categoria: int | None = None,
    estado: str | None = None,
    buscar: str | None = None,
    solo_bajo_stock: bool = False,
) -> list[Producto]:
    return producto_repo.listar_productos(
        db,
        id_categoria=id_categoria,
        estado=estado,
        buscar=buscar,
        solo_bajo_stock=solo_bajo_stock,
    )


def obtener(db: Session, id_producto: int) -> Producto:
    producto = producto_repo.obtener_por_id(db, id_producto)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el producto con id {id_producto}.",
        )
    return producto


def consultar_existencias(db: Session, id_producto: int) -> dict:
    producto = obtener(db, id_producto)
    return {
        "id_producto": producto.id_producto,
        "sku": producto.sku,
        "nombre": producto.nombre,
        "categoria_nombre": producto.categoria_nombre,
        "stock_actual": producto.stock_actual,
        "stock_minimo": producto.stock_minimo,
        "bajo_stock": producto.stock_actual <= producto.stock_minimo,
        "precio_compra": producto.precio_compra,
        "precio_venta": producto.precio_venta,
        "estado": producto.estado,
    }


def crear(
    db: Session,
    datos: ProductoCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Producto:
    if not categoria_repo.obtener_por_id(db, datos.id_categoria):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la categoría con id {datos.id_categoria}.",
        )

    sku_limpio = datos.sku.strip().upper()
    if producto_repo.obtener_por_sku(db, sku_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto registrado con el código SKU '{sku_limpio}'.",
        )

    nuevo = Producto(
        id_categoria=datos.id_categoria,
        sku=sku_limpio,
        nombre=datos.nombre.strip(),
        marca=datos.marca.strip(),
        descripcion=datos.descripcion.strip() if datos.descripcion else None,
        precio_compra=datos.precio_compra,
        precio_venta=datos.precio_venta,
        stock_actual=datos.stock_actual,
        stock_minimo=datos.stock_minimo,
        estado=datos.estado,
    )
    try:
        db.add(nuevo)
        db.flush()
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="productos",
            tabla_afectada="productos",
            registro_id=nuevo.id_producto,
            accion="INSERT",
            datos_nuevos=_snapshot(nuevo),
            direccion_ip=direccion_ip,
        )
        db.commit()
        return obtener(db, nuevo.id_producto)
    except Exception:
        db.rollback()
        raise


def actualizar(
    db: Session,
    id_producto: int,
    datos: ProductoUpdate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Producto:
    producto = obtener(db, id_producto)
    antes = _snapshot(producto)
    cambios = datos.model_dump(exclude_unset=True)

    if "id_categoria" in cambios and cambios["id_categoria"] is not None:
        if not categoria_repo.obtener_por_id(db, cambios["id_categoria"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe la categoría con id {cambios['id_categoria']}.",
            )

    if "sku" in cambios and cambios["sku"] is not None:
        nuevo_sku = cambios["sku"].strip().upper()
        existente = producto_repo.obtener_por_sku(db, nuevo_sku)
        if existente and existente.id_producto != id_producto:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro producto con el código SKU '{nuevo_sku}'.",
            )
        cambios["sku"] = nuevo_sku

    precio_compra_final = cambios.get("precio_compra", producto.precio_compra)
    precio_venta_final = cambios.get("precio_venta", producto.precio_venta)
    if precio_venta_final < precio_compra_final:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El precio_venta debe ser mayor o igual al precio_compra.",
        )

    for campo in ("nombre", "descripcion", "marca"):
        if campo in cambios and cambios[campo] is not None:
            cambios[campo] = cambios[campo].strip()

    for campo, valor in cambios.items():
        setattr(producto, campo, valor)

    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="productos",
            tabla_afectada="productos",
            registro_id=producto.id_producto,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(producto),
            direccion_ip=direccion_ip,
        )
        db.commit()
        return obtener(db, producto.id_producto)
    except Exception:
        db.rollback()
        raise


def desactivar(
    db: Session,
    id_producto: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Producto:
    producto = obtener(db, id_producto)
    antes = _snapshot(producto)
    producto.estado = "inactivo"
    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="productos",
            tabla_afectada="productos",
            registro_id=producto.id_producto,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(producto),
            direccion_ip=direccion_ip,
        )
        db.commit()
        return obtener(db, producto.id_producto)
    except Exception:
        db.rollback()
        raise


def eliminar(
    db: Session,
    id_producto: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> None:
    producto = obtener(db, id_producto)
    tiene_historial = (
        db.query(DetalleCompra)
        .filter(DetalleCompra.id_producto == id_producto)
        .first()
        is not None
        or db.query(DetalleVenta)
        .filter(DetalleVenta.id_producto == id_producto)
        .first()
        is not None
        or db.query(MovimientoInventario)
        .filter(MovimientoInventario.id_producto == id_producto)
        .first()
        is not None
    )
    if tiene_historial:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar físicamente el producto porque tiene compras, "
                "ventas o movimientos históricos. Desactívalo con PATCH /desactivar."
            ),
        )
    antes = _snapshot(producto)
    try:
        db.delete(producto)
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="productos",
            tabla_afectada="productos",
            registro_id=id_producto,
            accion="DELETE",
            datos_anteriores=antes,
            direccion_ip=direccion_ip,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
