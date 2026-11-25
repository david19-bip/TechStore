"""Modelo ORM para la tabla clientes."""

from datetime import datetime

from sqlalchemy import Enum, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    tipo_documento: Mapped[str] = mapped_column(
        Enum("CC", "CE", "NIT", "PASAPORTE", name="tipo_doc_cliente_enum"),
        nullable=False,
        default="CC",
    )
    numero_documento: Mapped[str] = mapped_column(String(30), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(25), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True, unique=True)
    direccion: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ciudad: Mapped[str | None] = mapped_column(String(80), nullable=True)
    estado: Mapped[str] = mapped_column(
        Enum("activo", "inactivo", name="estado_cliente_enum"),
        nullable=False,
        default="activo",
    )
    creado_en: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )
