"""Esquemas Pydantic para Movimientos de Inventario (Kardex) y Ajustes."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AjusteInventarioCreate(BaseModel):
    id_producto: int = Field(..., gt=0)
    tipo_movimiento: Literal["ajuste_positivo", "ajuste_negativo", "devolucion"]
    cantidad: int = Field(..., gt=0)
    motivo: str = Field(..., min_length=3, max_length=255)


class MovimientoInventarioOut(BaseModel):
    id_movimiento: int
    id_producto: int
    producto_sku: str | None = None
    producto_nombre: str | None = None
    id_usuario: int
    usuario_nombre: str | None = None
    id_compra: int | None = None
    compra_factura: str | None = None
    id_venta: int | None = None
    venta_factura: str | None = None
    tipo_movimiento: str
    cantidad: int
    stock_anterior: int
    stock_nuevo: int
    motivo: str | None = None
    fecha_movimiento: datetime

    model_config = ConfigDict(from_attributes=True)
