"""Punto de entrada principal del backend FastAPI de TechStore."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router

app = FastAPI(
    title="TechStore API",
    description="API REST para la gestión de inventario, compras y ventas de TechStore.",
    version="1.0.0",
)

# Permite peticiones desde el frontend en React + Vite (TypeScript)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Sistema"])
def inicio():
    return {
        "mensaje": "Bienvenido a TechStore API",
        "documentacion": "/docs",
        "salud": "/api/v1/health",
    }


app.include_router(api_router, prefix="/api/v1")
