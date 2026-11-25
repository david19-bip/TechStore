"""Endpoints CRUD para Productos (/api/v1/productos) con existencias, roles y auditoría."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.producto import ProductoCreate, ProductoOut, ProductoUpdate
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["Productos"])

todos_roles = require_roles("administrador", "vendedor", "bodeguero")
solo_admin = require_roles("administrador")


@router.get("/", response_model=list[ProductoOut], summary="Listar productos")
def listar_productos(
    id_categoria: int | None = Query(default=None, gt=0),
    estado: Literal["activo", "inactivo"] | None = Query(default=None),
    buscar: str | None = Query(default=None, description="Buscar por nombre, SKU o marca"),
    solo_bajo_stock: bool = Query(default=False, description="Solo stock_actual <= stock_minimo"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return producto_service.listar(
        db,
        id_categoria=id_categoria,
        estado=estado,
        buscar=buscar,
        solo_bajo_stock=solo_bajo_stock,
    )


@router.get(
    "/bajo-stock",
    response_model=list[ProductoOut],
    summary="Consultar productos con stock bajo",
)
def listar_productos_bajo_stock(
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return producto_service.listar(db, estado="activo", solo_bajo_stock=True)


@router.get(
    "/{id_producto}",
    response_model=ProductoOut,
    summary="Consultar un producto por ID",
)
def obtener_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return producto_service.obtener(db, id_producto)


@router.get(
    "/{id_producto}/existencias",
    summary="Consultar existencias disponibles de un producto",
)
def consultar_existencias_producto(
    id_producto: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return producto_service.consultar_existencias(db, id_producto)


@router.post(
    "/",
    response_model=ProductoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo producto",
)
def crear_producto(
    datos: ProductoCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return producto_service.crear(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.put(
    "/{id_producto}",
    response_model=ProductoOut,
    summary="Actualizar un producto existente",
)
def actualizar_producto(
    id_producto: int,
    datos: ProductoUpdate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return producto_service.actualizar(
        db, id_producto, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.patch(
    "/{id_producto}/desactivar",
    response_model=ProductoOut,
    summary="Desactivar un producto (borrado lógico)",
)
def desactivar_producto(
    id_producto: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    return producto_service.desactivar(
        db, id_producto, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )


@router.delete(
    "/{id_producto}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto sin historial comercial",
)
def eliminar_producto(
    id_producto: int,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(solo_admin),
):
    producto_service.eliminar(
        db, id_producto, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
