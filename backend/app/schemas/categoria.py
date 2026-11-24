"""Esquemas Pydantic para la entidad Categoria."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)
    estado: Literal["activa", "inactiva"] = "activa"


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)
    estado: Literal["activa", "inactiva"] | None = None


class CategoriaOut(CategoriaBase):
    id_categoria: int
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
