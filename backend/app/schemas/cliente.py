"""Esquemas Pydantic para la entidad Cliente."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteBase(BaseModel):
    tipo_documento: Literal["CC", "CE", "NIT", "PASAPORTE"] = "CC"
    numero_documento: str = Field(..., min_length=4, max_length=30)
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    telefono: str | None = Field(default=None, max_length=25)
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)
    ciudad: str | None = Field(default=None, max_length=80)
    estado: Literal["activo", "inactivo"] = "activo"


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    tipo_documento: Literal["CC", "CE", "NIT", "PASAPORTE"] | None = None
    numero_documento: str | None = Field(default=None, min_length=4, max_length=30)
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    apellido: str | None = Field(default=None, min_length=2, max_length=100)
    telefono: str | None = Field(default=None, max_length=25)
    email: EmailStr | None = None
    direccion: str | None = Field(default=None, max_length=200)
    ciudad: str | None = Field(default=None, max_length=80)
    estado: Literal["activo", "inactivo"] | None = None


class ClienteOut(ClienteBase):
    id_cliente: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
