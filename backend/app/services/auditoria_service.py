"""Servicio centralizado de auditoría (Actividad 6)."""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.auditoria import Auditoria
from app.repositories import auditoria_repo


def _serializar_json(datos: dict[str, Any] | None) -> str | None:
    if datos is None:
        return None

    def _default(obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    return json.dumps(datos, ensure_ascii=False, default=_default)


def registrar_evento(
    db: Session,
    *,
    id_usuario: int | None,
    modulo: str,
    tabla_afectada: str,
    registro_id: int | str,
    accion: str,
    datos_anteriores: dict[str, Any] | None = None,
    datos_nuevos: dict[str, Any] | None = None,
    direccion_ip: str | None = None,
) -> Auditoria:
    """Agrega un registro de auditoría dentro de la transacción activa."""
    evento = Auditoria(
        id_usuario=id_usuario,
        modulo=modulo,
        tabla_afectada=tabla_afectada,
        registro_id=str(registro_id),
        accion=accion,
        datos_anteriores=_serializar_json(datos_anteriores),
        datos_nuevos=_serializar_json(datos_nuevos),
        direccion_ip=direccion_ip,
    )
    db.add(evento)
    return evento


def listar(
    db: Session,
    id_usuario: int | None = None,
    modulo: str | None = None,
    tabla_afectada: str | None = None,
    accion: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    limite: int = 200,
) -> list[Auditoria]:
    return auditoria_repo.listar_auditoria(
        db,
        id_usuario=id_usuario,
        modulo=modulo,
        tabla_afectada=tabla_afectada,
        accion=accion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limite=limite,
    )
