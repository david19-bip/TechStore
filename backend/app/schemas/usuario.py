"""Esquemas Pydantic para la entidad Usuario."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    rol: Literal["administrador", "vendedor", "bodeguero"] = "vendedor"
    estado: Literal["activo", "inactivo"] = "activo"


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6, max_length=128)


class UsuarioUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    apellido: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=128)
    rol: Literal["administrador", "vendedor", "bodeguero"] | None = None
    estado: Literal["activo", "inactivo"] | None = None


class UsuarioOut(UsuarioBase):
    id_usuario: int
    creado_en: datetime
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
