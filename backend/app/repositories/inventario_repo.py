"""Repositorio de acceso a datos para movimientos_inventario (Kardex)."""

from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.movimiento_inventario import MovimientoInventario


def listar_movimientos(
    db: Session,
    id_producto: int | None = None,
    tipo_movimiento: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    limite: int = 200,
) -> list[MovimientoInventario]:
    query = db.query(MovimientoInventario).options(
        joinedload(MovimientoInventario.producto),
        joinedload(MovimientoInventario.usuario),
        joinedload(MovimientoInventario.compra),
        joinedload(MovimientoInventario.venta),
    )
    if id_producto is not None:
        query = query.filter(MovimientoInventario.id_producto == id_producto)
    if tipo_movimiento:
        query = query.filter(MovimientoInventario.tipo_movimiento == tipo_movimiento)
    if fecha_desde:
        query = query.filter(MovimientoInventario.fecha_movimiento >= fecha_desde)
    if fecha_hasta:
        query = query.filter(MovimientoInventario.fecha_movimiento <= fecha_hasta)
    return (
        query.order_by(MovimientoInventario.id_movimiento.desc())
        .limit(limite)
        .all()
    )
