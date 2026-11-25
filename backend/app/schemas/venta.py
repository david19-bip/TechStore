"""Esquemas Pydantic para Ventas y Detalle de Ventas."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DetalleVentaCreate(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio_unitario: Decimal | None = Field(
        default=None,
        ge=0,
        description="Si se omite, se toma automáticamente el precio_venta vigente del producto",
    )
    descuento: Decimal = Field(default=Decimal("0.00"), ge=0)

    @model_validator(mode="after")
    def validar_descuento(self) -> "DetalleVentaCreate":
        if self.precio_unitario is not None:
            bruto = self.precio_unitario * self.cantidad
            if self.descuento > bruto:
                raise ValueError("El descuento no puede superar el subtotal de la línea.")
        return self


class DetalleVentaOut(BaseModel):
    id_detalle_venta: int
    id_venta: int
    id_producto: int
    producto_sku: str | None = None
    producto_nombre: str | None = None
    cantidad: int
    precio_unitario: Decimal
    descuento: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class VentaCreate(BaseModel):
    id_cliente: int = Field(..., gt=0)
    numero_factura: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Si se omite, el sistema genera un consecutivo único FV-...",
    )
    metodo_pago: Literal["efectivo", "tarjeta", "transferencia", "pse"] = "efectivo"
    impuesto_porcentaje: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        le=100,
        description="Porcentaje de IVA (0 por defecto para el Reto Integrador)",
    )
    observaciones: str | None = Field(default=None, max_length=255)
    detalles: list[DetalleVentaCreate] = Field(..., min_length=1)


class VentaOut(BaseModel):
    id_venta: int
    id_cliente: int
    cliente_nombre: str | None = None
    id_usuario: int
    usuario_nombre: str | None = None
    numero_factura: str
    fecha_venta: datetime
    metodo_pago: str
    subtotal: Decimal
    impuesto: Decimal
    descuento_total: Decimal
    total: Decimal
    estado: str
    observaciones: str | None = None
    detalles: list[DetalleVentaOut] = []

    model_config = ConfigDict(from_attributes=True)
