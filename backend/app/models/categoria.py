"""Modelo ORM para la tabla categorias."""

from datetime import datetime

from sqlalchemy import Enum, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id_categoria: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    nombre: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estado: Mapped[str] = mapped_column(
        Enum("activa", "inactiva", name="estado_categoria_enum"),
        nullable=False,
        default="activa",
    )
    creado_en: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )

    productos = relationship("Producto", back_populates="categoria")
