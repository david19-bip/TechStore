"""Lógica de negocio para la gestión de productos."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.producto import Producto
from app.repositories import categoria_repo, producto_repo
from app.schemas.producto import ProductoCreate, ProductoUpdate


def listar(
    db: Session,
    buscar: str | None = None,
    id_categoria: int | None = None,
    estado: str | None = None,
    solo_bajo_stock: bool = False,
) -> list[Producto]:
    return producto_repo.listar_productos(
        db,
        buscar=buscar,
        id_categoria=id_categoria,
        estado=estado,
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


def crear(db: Session, datos: ProductoCreate) -> Producto:
    if not categoria_repo.obtener_por_id(db, datos.id_categoria):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoría con id {datos.id_categoria} no existe.",
        )

    sku_limpio = datos.sku.strip().upper()
    if producto_repo.obtener_por_sku(db, sku_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un producto con el SKU '{sku_limpio}'.",
        )

    nuevo = Producto(
        id_categoria=datos.id_categoria,
        sku=sku_limpio,
        nombre=datos.nombre.strip(),
        marca=datos.marca.strip(),
        descripcion=datos.descripcion,
        precio_compra=datos.precio_compra,
        precio_venta=datos.precio_venta,
        stock_actual=datos.stock_actual,
        stock_minimo=datos.stock_minimo,
        estado=datos.estado,
    )
    return producto_repo.crear_producto(db, nuevo)


def actualizar(
    db: Session, id_producto: int, datos: ProductoUpdate
) -> Producto:
    producto = obtener(db, id_producto)
    cambios = datos.model_dump(exclude_unset=True)

    if "id_categoria" in cambios and cambios["id_categoria"] is not None:
        if not categoria_repo.obtener_por_id(db, cambios["id_categoria"]):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La categoría con id {cambios['id_categoria']} no existe.",
            )

    if "sku" in cambios and cambios["sku"] is not None:
        nuevo_sku = cambios["sku"].strip().upper()
        existente = producto_repo.obtener_por_sku(db, nuevo_sku)
        if existente and existente.id_producto != id_producto:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro producto con el SKU '{nuevo_sku}'.",
            )
        cambios["sku"] = nuevo_sku

    precio_compra_final = cambios.get("precio_compra", producto.precio_compra)
    precio_venta_final = cambios.get("precio_venta", producto.precio_venta)
    if precio_venta_final < precio_compra_final:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El precio_venta debe ser mayor o igual al precio_compra.",
        )

    for campo, valor in cambios.items():
        if campo in ("nombre", "marca") and isinstance(valor, str):
            valor = valor.strip()
        setattr(producto, campo, valor)

    return producto_repo.guardar_producto(db, producto)


def eliminar(db: Session, id_producto: int) -> dict[str, str]:
    producto = obtener(db, id_producto)
    try:
        producto_repo.eliminar_producto(db, producto)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar el producto porque tiene compras, ventas o "
                "movimientos de inventario registrados. Cambia su estado a 'inactivo'."
            ),
        )
    return {"mensaje": f"Producto {id_producto} eliminado correctamente."}
