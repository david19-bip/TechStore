"""Repositorio de acceso a datos para compras y detalle_compras."""

from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.compra import Compra, DetalleCompra


def listar_compras(
    db: Session,
    id_proveedor: int | None = None,
    estado: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
) -> list[Compra]:
    query = db.query(Compra).options(
        joinedload(Compra.proveedor),
        joinedload(Compra.usuario),
        joinedload(Compra.detalles).joinedload(DetalleCompra.producto),
    )
    if id_proveedor is not None:
        query = query.filter(Compra.id_proveedor == id_proveedor)
    if estado:
        query = query.filter(Compra.estado == estado)
    if fecha_desde:
        query = query.filter(Compra.fecha_compra >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Compra.fecha_compra <= fecha_hasta)
    return query.order_by(Compra.id_compra.desc()).all()


def obtener_por_id(db: Session, id_compra: int) -> Compra | None:
    return (
        db.query(Compra)
        .options(
            joinedload(Compra.proveedor),
            joinedload(Compra.usuario),
            joinedload(Compra.detalles).joinedload(DetalleCompra.producto),
        )
        .filter(Compra.id_compra == id_compra)
        .first()
    )


def obtener_por_proveedor_factura(
    db: Session, id_proveedor: int, numero_factura: str
) -> Compra | None:
    return (
        db.query(Compra)
        .filter(
            Compra.id_proveedor == id_proveedor,
            Compra.numero_factura == numero_factura,
        )
        .first()
    )
