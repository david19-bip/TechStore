"""Endpoints CRUD para Proveedores (/api/v1/proveedores)."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.proveedor import ProveedorCreate, ProveedorOut, ProveedorUpdate
from app.services import proveedor_service

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

admin_o_bodega = require_roles("administrador", "bodeguero")
solo_admin = require_roles("administrador")


@router.get("/", response_model=list[ProveedorOut], summary="Listar proveedores")
def listar_proveedores(
    buscar: str | None = Query(default=None, description="Buscar por razón social, NIT o ciudad"),
    estado: Literal["activo", "inactivo"] | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_bodega),
):
    return proveedor_service.listar(db, buscar=buscar, estado=estado)


@router.get(
    "/{id_proveedor}",
    response_model=ProveedorOut,
    summary="Consultar un proveedor por ID",
)
def obtener_proveedor(
    id_proveedor: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_bodega),
):
    return proveedor_service.obtener(db, id_proveedor)


@router.post(
    "/",
    response_model=ProveedorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo proveedor",
)
def crear_proveedor(
    datos: ProveedorCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return proveedor_service.crear(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.put(
    "/{id_proveedor}",
    response_model=ProveedorOut,
    summary="Actualizar un proveedor existente",
)
def actualizar_proveedor(
    id_proveedor: int,
    datos: ProveedorUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return proveedor_service.actualizar(
        db, id_proveedor, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_proveedor}/desactivar",
    response_model=ProveedorOut,
    summary="Desactivar un proveedor",
)
def desactivar_proveedor(
    id_proveedor: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return proveedor_service.desactivar(
        db, id_proveedor, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
