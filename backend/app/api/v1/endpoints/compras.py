"""Endpoints para Compras (/api/v1/compras) — Administrador y Encargado de Inventario."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.compra import CompraCreate, CompraOut
from app.services import compra_service

router = APIRouter(prefix="/compras", tags=["Compras"])

admin_o_bodega = require_roles("administrador", "bodeguero")
solo_admin = require_roles("administrador")


@router.get("/", response_model=list[CompraOut], summary="Listar compras")
def listar_compras(
    id_proveedor: int | None = Query(default=None, gt=0),
    estado: Literal["pendiente", "recibida", "anulada"] | None = Query(default=None),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_bodega),
):
    return compra_service.listar(
        db,
        id_proveedor=id_proveedor,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get(
    "/{id_compra}",
    response_model=CompraOut,
    summary="Consultar una compra con sus detalles",
)
def obtener_compra(
    id_compra: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_bodega),
):
    return compra_service.obtener(db, id_compra)


@router.post(
    "/",
    response_model=CompraOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar compra (encabezado + detalles) y aumentar existencias",
)
def registrar_compra(
    datos: CompraCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(admin_o_bodega),
):
    return compra_service.registrar_compra(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_compra}/recibir",
    response_model=CompraOut,
    summary="Marcar compra pendiente como recibida y sumar existencias",
)
def recibir_compra(
    id_compra: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(admin_o_bodega),
):
    return compra_service.recibir_compra(
        db, id_compra, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_compra}/anular",
    response_model=CompraOut,
    summary="Anular compra (solo Administrador)",
)
def anular_compra(
    id_compra: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return compra_service.anular_compra(
        db, id_compra, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
