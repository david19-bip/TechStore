"""Esquemas Pydantic para Auditoría."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditoriaOut(BaseModel):
    id_auditoria: int
    id_usuario: int | None = None
    usuario_nombre: str | None = None
    usuario_email: str | None = None
    modulo: str | None = None
    tabla_afectada: str
    registro_id: str
    accion: str
    datos_anteriores: str | None = None
    datos_nuevos: str | None = None
    direccion_ip: str | None = None
    fecha_evento: datetime

    model_config = ConfigDict(from_attributes=True)
