"""Endpoints CRUD para Clientes (/api/v1/clientes)."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteUpdate
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])

admin_o_vendedor = require_roles("administrador", "vendedor")
solo_admin = require_roles("administrador")


@router.get("/", response_model=list[ClienteOut], summary="Listar clientes")
def listar_clientes(
    buscar: str | None = Query(default=None, description="Buscar por nombre, documento o email"),
    estado: Literal["activo", "inactivo"] | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_vendedor),
):
    return cliente_service.listar(db, buscar=buscar, estado=estado)


@router.get(
    "/{id_cliente}",
    response_model=ClienteOut,
    summary="Consultar un cliente por ID",
)
def obtener_cliente(
    id_cliente: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_vendedor),
):
    return cliente_service.obtener(db, id_cliente)


@router.post(
    "/",
    response_model=ClienteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo cliente",
)
def crear_cliente(
    datos: ClienteCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return cliente_service.crear(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.put(
    "/{id_cliente}",
    response_model=ClienteOut,
    summary="Actualizar un cliente existente",
)
def actualizar_cliente(
    id_cliente: int,
    datos: ClienteUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return cliente_service.actualizar(
        db, id_cliente, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_cliente}/desactivar",
    response_model=ClienteOut,
    summary="Desactivar un cliente",
)
def desactivar_cliente(
    id_cliente: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return cliente_service.desactivar(
        db, id_cliente, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
