"""Endpoints CRUD y consulta de bajo stock para productos."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.schemas.producto import ProductoCreate, ProductoOut, ProductoUpdate
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("/", response_model=list[ProductoOut])
def listar_productos(
    buscar: str | None = Query(
        default=None, description="Buscar por nombre, SKU o marca"
    ),
    id_categoria: int | None = Query(
        default=None, gt=0, description="Filtrar por ID de categoría"
    ),
    estado: Literal["activo", "inactivo"] | None = Query(
        default=None, description="Filtrar por estado"
    ),
    solo_bajo_stock: bool = Query(
        default=False, description="Solo productos con stock_actual <= stock_minimo"
    ),
    db: Session = Depends(get_db),
):
    return producto_service.listar(
        db,
        buscar=buscar,
        id_categoria=id_categoria,
        estado=estado,
        solo_bajo_stock=solo_bajo_stock,
    )


@router.get("/bajo-stock", response_model=list[ProductoOut])
def listar_productos_bajo_stock(db: Session = Depends(get_db)):
    return producto_service.listar(db, estado="activo", solo_bajo_stock=True)


@router.get("/{id_producto}", response_model=ProductoOut)
def obtener_producto(id_producto: int, db: Session = Depends(get_db)):
    return producto_service.obtener(db, id_producto)


@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED)
def crear_producto(datos: ProductoCreate, db: Session = Depends(get_db)):
    return producto_service.crear(db, datos)


@router.put("/{id_producto}", response_model=ProductoOut)
def actualizar_producto(
    id_producto: int, datos: ProductoUpdate, db: Session = Depends(get_db)
):
    return producto_service.actualizar(db, id_producto, datos)


@router.delete("/{id_producto}")
def eliminar_producto(id_producto: int, db: Session = Depends(get_db)):
    return producto_service.eliminar(db, id_producto)
