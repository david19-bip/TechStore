"""Repositorio de acceso a datos para la tabla productos."""

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.producto import Producto


def listar_productos(
    db: Session,
    buscar: str | None = None,
    id_categoria: int | None = None,
    estado: str | None = None,
    solo_bajo_stock: bool = False,
) -> list[Producto]:
    query = db.query(Producto).options(joinedload(Producto.categoria))

    if buscar:
        patron = f"%{buscar.strip()}%"
        query = query.filter(
            or_(
                Producto.nombre.ilike(patron),
                Producto.sku.ilike(patron),
                Producto.marca.ilike(patron),
            )
        )
    if id_categoria is not None:
        query = query.filter(Producto.id_categoria == id_categoria)
    if estado:
        query = query.filter(Producto.estado == estado)
    if solo_bajo_stock:
        query = query.filter(Producto.stock_actual <= Producto.stock_minimo)

    return query.order_by(Producto.id_producto.asc()).all()


def obtener_por_id(db: Session, id_producto: int) -> Producto | None:
    return (
        db.query(Producto)
        .options(joinedload(Producto.categoria))
        .filter(Producto.id_producto == id_producto)
        .first()
    )


def obtener_por_sku(db: Session, sku: str) -> Producto | None:
    return db.query(Producto).filter(Producto.sku == sku).first()


def crear_producto(db: Session, producto: Producto) -> Producto:
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return obtener_por_id(db, producto.id_producto) or producto


def guardar_producto(db: Session, producto: Producto) -> Producto:
    db.commit()
    db.refresh(producto)
    return obtener_por_id(db, producto.id_producto) or producto


def eliminar_producto(db: Session, producto: Producto) -> None:
    db.delete(producto)
    db.commit()
