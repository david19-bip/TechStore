"""Repositorio de acceso a datos para ventas y detalle_ventas."""

from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.venta import DetalleVenta, Venta


def listar_ventas(
    db: Session,
    id_cliente: int | None = None,
    id_usuario: int | None = None,
    estado: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
) -> list[Venta]:
    query = db.query(Venta).options(
        joinedload(Venta.cliente),
        joinedload(Venta.usuario),
        joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
    )
    if id_cliente is not None:
        query = query.filter(Venta.id_cliente == id_cliente)
    if id_usuario is not None:
        query = query.filter(Venta.id_usuario == id_usuario)
    if estado:
        query = query.filter(Venta.estado == estado)
    if fecha_desde:
        query = query.filter(Venta.fecha_venta >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Venta.fecha_venta <= fecha_hasta)
    return query.order_by(Venta.id_venta.desc()).all()


def obtener_por_id(db: Session, id_venta: int) -> Venta | None:
    return (
        db.query(Venta)
        .options(
            joinedload(Venta.cliente),
            joinedload(Venta.usuario),
            joinedload(Venta.detalles).joinedload(DetalleVenta.producto),
        )
        .filter(Venta.id_venta == id_venta)
        .first()
    )


def obtener_por_factura(db: Session, numero_factura: str) -> Venta | None:
    return (
        db.query(Venta)
        .filter(Venta.numero_factura == numero_factura)
        .first()
    )
