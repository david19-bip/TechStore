"""Esquemas Pydantic para la entidad Producto."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductoBase(BaseModel):
    id_categoria: int = Field(..., gt=0)
    sku: str = Field(..., min_length=2, max_length=50)
    nombre: str = Field(..., min_length=2, max_length=150)
    marca: str = Field(..., min_length=1, max_length=80)
    descripcion: str | None = None
    precio_compra: Decimal = Field(..., ge=0)
    precio_venta: Decimal = Field(..., ge=0)
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=5, ge=0)
    estado: Literal["activo", "inactivo"] = "activo"

    @model_validator(mode="after")
    def validar_precios(self) -> "ProductoBase":
        if self.precio_venta < self.precio_compra:
            raise ValueError(
                "El precio_venta debe ser mayor o igual al precio_compra."
            )
        return self


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    id_categoria: int | None = Field(default=None, gt=0)
    sku: str | None = Field(default=None, min_length=2, max_length=50)
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    marca: str | None = Field(default=None, min_length=1, max_length=80)
    descripcion: str | None = None
    precio_compra: Decimal | None = Field(default=None, ge=0)
    precio_venta: Decimal | None = Field(default=None, ge=0)
    stock_actual: int | None = Field(default=None, ge=0)
    stock_minimo: int | None = Field(default=None, ge=0)
    estado: Literal["activo", "inactivo"] | None = None


class ProductoOut(ProductoBase):
    id_producto: int
    categoria_nombre: str | None = None
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
