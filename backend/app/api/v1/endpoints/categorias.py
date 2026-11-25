"""Endpoints CRUD para Categorías (/api/v1/categorias) con roles y auditoría."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from app.services import categoria_service

router = APIRouter(prefix="/categorias", tags=["Categorías"])

todos_roles = require_roles("administrador", "vendedor", "bodeguero")
solo_admin = require_roles("administrador")


@router.get("/", response_model=list[CategoriaOut], summary="Listar categorías")
def listar_categorias(
    estado: Literal["activa", "inactiva"] | None = Query(
        default=None, description="Filtrar por estado (activa / inactiva)"
    ),
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return categoria_service.listar(db, estado=estado)


@router.get(
    "/{id_categoria}",
    response_model=CategoriaOut,
    summary="Consultar una categoría por ID",
)
def obtener_categoria(
    id_categoria: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return categoria_service.obtener(db, id_categoria)


@router.post(
    "/",
    response_model=CategoriaOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva categoría",
)
def crear_categoria(
    datos: CategoriaCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return categoria_service.crear(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.put(
    "/{id_categoria}",
    response_model=CategoriaOut,
    summary="Actualizar una categoría existente",
)
def actualizar_categoria(
    id_categoria: int,
    datos: CategoriaUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return categoria_service.actualizar(
        db, id_categoria, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_categoria}/desactivar",
    response_model=CategoriaOut,
    summary="Desactivar una categoría (borrado lógico)",
)
def desactivar_categoria(
    id_categoria: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return categoria_service.desactivar(
        db, id_categoria, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.delete(
    "/{id_categoria}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría sin productos asociados",
)
def eliminar_categoria(
    id_categoria: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    categoria_service.eliminar(
        db, id_categoria, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
