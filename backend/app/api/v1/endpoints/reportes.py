"""Endpoints de Reportes e Indicadores (/api/v1/reportes)."""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.services import reporte_service

router = APIRouter(prefix="/reportes", tags=["Reportes"])

todos_roles = require_roles("administrador", "vendedor", "bodeguero")
admin_o_bodega = require_roles("administrador", "bodeguero")
admin_o_vendedor = require_roles("administrador", "vendedor")
solo_admin = require_roles("administrador")


@router.get("/dashboard", summary="Indicadores generales del Dashboard")
def dashboard(
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return reporte_service.obtener_dashboard(db)


@router.get("/compras", summary="Reporte de compras por fecha y proveedor")
def reporte_compras(
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    id_proveedor: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_bodega),
):
    return reporte_service.reporte_compras(
        db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        id_proveedor=id_proveedor,
    )


@router.get("/ventas", summary="Reporte de ventas por fecha y cliente")
def reporte_ventas(
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    id_cliente: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_vendedor),
):
    return reporte_service.reporte_ventas(
        db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        id_cliente=id_cliente,
    )


@router.get(
    "/productos-mas-vendidos",
    summary="Ranking de productos más vendidos con utilidad bruta",
)
def productos_mas_vendidos(
    limite: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_vendedor),
):
    return reporte_service.productos_mas_vendidos(db, limite=limite)


@router.get(
    "/resumen-financiero",
    summary="Resumen financiero integral (existencias, compras, ventas, costo vendido y utilidad bruta)",
)
def resumen_financiero(
    db: Session = Depends(get_db),
    _: Usuario = Depends(solo_admin),
):
    return reporte_service.resumen_financiero(db)
