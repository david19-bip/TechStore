"""Repositorio de acceso a datos para la tabla auditoria."""

from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.auditoria import Auditoria


def listar_auditoria(
    db: Session,
    id_usuario: int | None = None,
    modulo: str | None = None,
    tabla_afectada: str | None = None,
    accion: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    limite: int = 200,
) -> list[Auditoria]:
    query = db.query(Auditoria).options(joinedload(Auditoria.usuario))
    if id_usuario is not None:
        query = query.filter(Auditoria.id_usuario == id_usuario)
    if modulo:
        query = query.filter(Auditoria.modulo == modulo)
    if tabla_afectada:
        query = query.filter(Auditoria.tabla_afectada == tabla_afectada)
    if accion:
        query = query.filter(Auditoria.accion == accion)
    if fecha_desde:
        query = query.filter(Auditoria.fecha_evento >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Auditoria.fecha_evento <= fecha_hasta)
    return query.order_by(Auditoria.id_auditoria.desc()).limit(limite).all()
