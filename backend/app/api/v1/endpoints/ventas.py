"""Endpoints para Ventas (/api/v1/ventas) — Administrador y Vendedor."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.venta import VentaCreate, VentaOut
from app.services import venta_service

router = APIRouter(prefix="/ventas", tags=["Ventas"])

admin_o_vendedor = require_roles("administrador", "vendedor")
solo_admin = require_roles("administrador")


@router.get("/", response_model=list[VentaOut], summary="Listar ventas")
def listar_ventas(
    id_cliente: int | None = Query(default=None, gt=0),
    id_usuario: int | None = Query(default=None, gt=0),
    estado: Literal["pendiente", "pagada", "anulada"] | None = Query(default=None),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_vendedor),
):
    return venta_service.listar(
        db,
        id_cliente=id_cliente,
        id_usuario=id_usuario,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get(
    "/{id_venta}",
    response_model=VentaOut,
    summary="Consultar una venta con sus detalles",
)
def obtener_venta(
    id_venta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_vendedor),
):
    return venta_service.obtener(db, id_venta)


@router.post(
    "/",
    response_model=VentaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar venta (valida stock, calcula totales, descuenta inventario y audita)",
)
def registrar_venta(
    datos: VentaCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(admin_o_vendedor),
):
    return venta_service.registrar_venta(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_venta}/anular",
    response_model=VentaOut,
    summary="Anular venta y reintegrar inventario (solo Administrador)",
)
def anular_venta(
    id_venta: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return venta_service.anular_venta(
        db, id_venta, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
