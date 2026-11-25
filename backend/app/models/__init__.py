"""Registro centralizado de modelos ORM de TechStore."""

from app.models.auditoria import Auditoria
from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.compra import Compra, DetalleCompra
from app.models.movimiento_inventario import MovimientoInventario
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.models.usuario import Usuario
from app.models.venta import DetalleVenta, Venta

__all__ = [
    "Auditoria",
    "Categoria",
    "Cliente",
    "Compra",
    "DetalleCompra",
    "DetalleVenta",
    "MovimientoInventario",
    "Producto",
    "Proveedor",
    "Usuario",
    "Venta",
]
