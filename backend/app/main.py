"""Punto de entrada principal del backend TechStore (FastAPI)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

import app.models  # noqa: F401  # Registra todos los modelos ORM en SQLAlchemy
from app.api.v1.api import api_router
from app.core.config import CORS_ORIGINS
from app.database.conexion import engine

app = FastAPI(
    title="TechStore API",
    description=(
        "API REST para la gestión de inventario, compras, ventas, seguridad por roles, "
        "auditoría y reportes de TechStore (Guía de Aprendizaje SENA)."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Sistema"], summary="Bienvenida a la API")
def raiz():
    return {
        "proyecto": "TechStore API",
        "version": "1.0.0",
        "documentacion": "/docs",
        "salud": "/api/v1/health",
    }


@app.get("/api/v1/health", tags=["Sistema"], summary="Verificar salud de API y BD")
def health_check():
    with engine.connect() as conn:
        bd = conn.execute(text("SELECT DATABASE()")).scalar()
    return {
        "estado": "ok",
        "base_de_datos": bd,
    }
