"""Modelos ORM para las tablas ventas y detalle_ventas."""

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


class Venta(Base):
    __tablename__ = "ventas"

    id_venta: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_cliente: Mapped[int] = mapped_column(
        Integer, ForeignKey("clientes.id_cliente", onupdate="CASCADE"), nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario", onupdate="CASCADE"), nullable=False
    )
    numero_factura: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    fecha_venta: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    metodo_pago: Mapped[str] = mapped_column(
        Enum("efectivo", "tarjeta", "transferencia", "pse", name="metodo_pago_enum"),
        nullable=False,
        default="efectivo",
    )
    subtotal: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2), nullable=False, default=Decimal("0.00")
    )
    impuesto: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2), nullable=False, default=Decimal("0.00")
    )
    descuento_total: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2), nullable=False, default=Decimal("0.00")
    )
    total: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2), nullable=False, default=Decimal("0.00")
    )
    estado: Mapped[str] = mapped_column(
        Enum("pendiente", "pagada", "anulada", name="estado_venta_enum"),
        nullable=False,
        default="pagada",
    )
    observaciones: Mapped[str | None] = mapped_column(String(255), nullable=True)

    cliente = relationship("Cliente")
    usuario = relationship("Usuario")
    detalles = relationship(
        "DetalleVenta", back_populates="venta", cascade="all, delete-orphan"
    )

    @property
    def cliente_nombre(self) -> str | None:
        return f"{self.cliente.nombre} {self.cliente.apellido}" if self.cliente else None

    @property
    def usuario_nombre(self) -> str | None:
        return f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else None


class DetalleVenta(Base):
    __tablename__ = "detalle_ventas"

    id_detalle_venta: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_venta: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ventas.id_venta", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    id_producto: Mapped[int] = mapped_column(
        Integer, ForeignKey("productos.id_producto", onupdate="CASCADE"), nullable=False
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    descuento: Mapped[Decimal] = mapped_column(
        DECIMAL(12, 2), nullable=False, default=Decimal("0.00")
    )
    subtotal: Mapped[Decimal] = mapped_column(
        DECIMAL(14, 2),
        Computed("cantidad * precio_unitario - descuento", persisted=True),
        nullable=False,
    )

    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")

    @property
    def producto_nombre(self) -> str | None:
        return self.producto.nombre if self.producto else None

    @property
    def producto_sku(self) -> str | None:
        return self.producto.sku if self.producto else None
