"""Modelo ORM para la tabla proveedores."""

from datetime import datetime

from sqlalchemy import Enum, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nit: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    razon_social: Mapped[str] = mapped_column(String(150), nullable=False)
    nombre_contacto: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(25), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True, unique=True)
    direccion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ciudad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    estado: Mapped[str] = mapped_column(
        Enum("activo", "inactivo", name="estado_proveedor_enum"),
        nullable=False,
        default="activo",
    )
    creado_en: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )
