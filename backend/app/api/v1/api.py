"""Enrutador principal de la API v1 de TechStore."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.endpoints import categorias, productos
from app.database.conexion import get_db

api_router = APIRouter()


@api_router.get("/health", tags=["Sistema"])
def verificar_estado(db: Session = Depends(get_db)):
    """Verifica que el servidor FastAPI y la base de datos techstore_db respondan."""
    db_activa = db.execute(text("SELECT DATABASE()")).scalar()
    return {
        "status": "ok",
        "servicio": "TechStore API v1",
        "base_datos": db_activa,
    }


api_router.include_router(categorias.router)
api_router.include_router(productos.router)
