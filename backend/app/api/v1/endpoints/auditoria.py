"""Endpoints para consulta de Auditoría (/api/v1/auditoria) — Solo Administrador."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.auditoria import AuditoriaOut
from app.services import auditoria_service

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])

solo_admin = require_roles("administrador")


@router.get(
    "/",
    response_model=list[AuditoriaOut],
    summary="Consultar bitácora de auditoría del sistema",
)
def listar_auditoria(
    id_usuario: int | None = Query(default=None, gt=0),
    modulo: str | None = Query(default=None),
    tabla_afectada: str | None = Query(default=None),
    accion: Literal["INSERT", "UPDATE", "DELETE", "LOGIN", "LOGOUT"] | None = Query(
        default=None
    ),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    limite: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: Usuario = Depends(solo_admin),
):
    return auditoria_service.listar(
        db,
        id_usuario=id_usuario,
        modulo=modulo,
        tabla_afectada=tabla_afectada,
        accion=accion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limite=limite,
    )
