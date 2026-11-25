"""Endpoints CRUD para Usuarios (/api/v1/usuarios) — Solo Administrador."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

solo_admin = require_roles("administrador")


@router.get("/", response_model=list[UsuarioOut], summary="Listar usuarios")
def listar_usuarios(
    rol: Literal["administrador", "vendedor", "bodeguero"] | None = Query(default=None),
    estado: Literal["activo", "inactivo"] | None = Query(default=None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(solo_admin),
):
    return usuario_service.listar(db, rol=rol, estado=estado)


@router.get("/{id_usuario}", response_model=UsuarioOut, summary="Consultar usuario por ID")
def obtener_usuario(
    id_usuario: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(solo_admin),
):
    return usuario_service.obtener(db, id_usuario)


@router.post(
    "/",
    response_model=UsuarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
def crear_usuario(
    datos: UsuarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return usuario_service.crear(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.put("/{id_usuario}", response_model=UsuarioOut, summary="Actualizar usuario")
def actualizar_usuario(
    id_usuario: int,
    datos: UsuarioUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return usuario_service.actualizar(
        db, id_usuario, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_usuario}/desactivar",
    response_model=UsuarioOut,
    summary="Desactivar usuario",
)
def desactivar_usuario(
    id_usuario: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return usuario_service.desactivar(
        db, id_usuario, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
