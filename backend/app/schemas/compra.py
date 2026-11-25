"""Esquemas Pydantic para Compras y Detalle de Compras."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DetalleCompraCreate(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)


class DetalleCompraOut(BaseModel):
    id_detalle_compra: int
    id_compra: int
    id_producto: int
    producto_sku: str | None = None
    producto_nombre: str | None = None
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class CompraCreate(BaseModel):
    id_proveedor: int = Field(..., gt=0)
    numero_factura: str = Field(..., min_length=2, max_length=50)
    impuesto_porcentaje: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="Porcentaje de IVA (0 por defecto para el Reto Integrador)",
    )
    estado: Literal["pendiente", "recibida"] = "recibida"
    observaciones: str | None = Field(default=None, max_length=255)
    detalles: list[DetalleCompraCreate] = Field(..., min_length=1)


class CompraOut(BaseModel):
    id_compra: int
    id_proveedor: int
    proveedor_nombre: str | None = None
    id_usuario: int
    usuario_nombre: str | None = None
    numero_factura: str
    fecha_compra: datetime
    subtotal: Decimal
    impuesto: Decimal
    total: Decimal
    estado: str
    observaciones: str | None = None
    detalles: list[DetalleCompraOut] = []

    model_config = ConfigDict(from_attributes=True)
