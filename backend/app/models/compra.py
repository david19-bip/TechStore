"""Modelos ORM para las tablas compras y detalle_compras."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Computed,
    DECIMAL,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Compra(Base):
    __tablename__ = "compras"

    id_compra: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_proveedor: Mapped[int] = mapped_column(
        Integer, ForeignKey("proveedores.id_proveedor", onupdate="CASCADE"), nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario", onupdate="CASCADE"), nullable=False
    )
    numero_factura: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_compra: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    subtotal: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2), nullable=False, default=Decimal("0.00")
    )
    impuesto: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2), nullable=False, default=Decimal("0.00")
    )
    total: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2), nullable=False, default=Decimal("0.00")
    )
    estado: Mapped[str] = mapped_column(
        Enum("pendiente", "recibida", "anulada", name="estado_compra_enum"),
        nullable=False,
        default="pendiente",
    )
    observaciones: Mapped[str | None] = mapped_column(String(255), nullable=True)

    proveedor = relationship("Proveedor")
    usuario = relationship("Usuario")
    detalles = relationship(
        "DetalleCompra", back_populates="compra", cascade="all, delete-orphan"
    )

    @property
    def proveedor_nombre(self) -> str | None:
        return self.proveedor.razon_social if self.proveedor else None

    @property
    def usuario_nombre(self) -> str | None:
        return f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else None


class DetalleCompra(Base):
    __tablename__ = "detalle_compras"

    id_detalle_compra: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_compra: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("compras.id_compra", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        Integer, ForeignKey("productos.id_producto", onupdate="CASCADE"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2),
        Computed("cantidad * precio_unitario", persisted=True),
        nullable=False,
    )

    compra = relationship("Compra", back_populates="detalles")
    producto = relationship("Producto")

    @property
    def producto_nombre(self) -> str | None:
        return self.producto.nombre if self.producto else None

    @property
    def producto_sku(self) -> str | None:
        return self.producto.sku if self.producto else None
