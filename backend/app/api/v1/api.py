"""Agrupador de rutas de la API v1 de TechStore."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auditoria,
    auth,
    categorias,
    clientes,
    compras,
    inventario,
    productos,
    proveedores,
    reportes,
    usuarios,
    ventas,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(categorias.router)
api_router.include_router(productos.router)
api_router.include_router(proveedores.router)
api_router.include_router(clientes.router)
api_router.include_router(compras.router)
api_router.include_router(ventas.router)
api_router.include_router(inventario.router)
api_router.include_router(auditoria.router)
api_router.include_router(reportes.router)
