"""Endpoints CRUD para categorías."""

from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.conexion import get_db
from app.schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from app.services import categoria_service

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(
    estado: Literal["activa", "inactiva"] | None = Query(
        default=None, description="Filtrar por estado"
    ),
    db: Session = Depends(get_db),
):
    return categoria_service.listar(db, estado=estado)


@router.get("/{id_categoria}", response_model=CategoriaOut)
def obtener_categoria(id_categoria: int, db: Session = Depends(get_db)):
    return categoria_service.obtener(db, id_categoria)


@router.post("/", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED)
def crear_categoria(datos: CategoriaCreate, db: Session = Depends(get_db)):
    return categoria_service.crear(db, datos)


@router.put("/{id_categoria}", response_model=CategoriaOut)
def actualizar_categoria(
    id_categoria: int, datos: CategoriaUpdate, db: Session = Depends(get_db)
):
    return categoria_service.actualizar(db, id_categoria, datos)


@router.delete("/{id_categoria}")
def eliminar_categoria(id_categoria: int, db: Session = Depends(get_db)):
    return categoria_service.eliminar(db, id_categoria)
