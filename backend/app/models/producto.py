"""Modelo ORM para la tabla productos."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, Enum, ForeignKey, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Producto(Base):
    __tablename__ = "productos"

    id_producto: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_categoria: Mapped[int] = mapped_column(
        Integer, ForeignKey("categorias.id_categoria", onupdate="CASCADE"), nullable=False
    )
    sku: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    marca: Mapped[str] = mapped_column(String(80), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    precio_compra: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    precio_venta: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    stock_actual: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stock_minimo: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    estado: Mapped[str] = mapped_column(
        Enum("activo", "inactivo", name="estado_producto_enum"),
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

    categoria = relationship("Categoria", back_populates="productos")

    @property
    def categoria_nombre(self) -> str | None:
        return self.categoria.nombre if self.categoria else None
