"""Esquemas Pydantic para la entidad Proveedor."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProveedorBase(BaseModel):
    nit: str = Field(..., min_length=4, max_length=30)
    razon_social: str = Field(..., min_length=2, max_length=150)
    nombre_contacto: str | None = Field(default=None, max_length=120)
    telefono: str | None = Field(default=None, max_length=25)
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)
    ciudad: str | None = Field(default=None, max_length=80)
    estado: Literal["activo", "inactivo"] = "activo"


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nit: str | None = Field(default=None, min_length=4, max_length=30)
    razon_social: str | None = Field(default=None, min_length=2, max_length=150)
    nombre_contacto: str | None = Field(default=None, max_length=120)
    telefono: str | None = Field(default=None, max_length=25)
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)
    ciudad: str | None = Field(default=None, max_length=80)
    estado: Literal["activo", "inactivo"] | None = None


class ProveedorOut(ProveedorBase):
    id_proveedor: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
