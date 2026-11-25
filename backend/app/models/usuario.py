"""Modelo ORM para la tabla usuarios."""

from datetime import datetime

from sqlalchemy import Enum, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        Enum("administrador", "vendedor", "bodeguero", name="rol_usuario_enum"),
        nullable=False,
        default="vendedor",
    )
    estado: Mapped[str] = mapped_column(
        Enum("activo", "inactivo", name="estado_usuario_enum"),
        nullable=False,
        default="activo",
    )
    creado_en: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )
