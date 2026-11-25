"""Modelo ORM para la tabla movimientos_inventario."""

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"

    id_movimiento: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    id_producto: Mapped[int] = mapped_column(
        Integer, ForeignKey("productos.id_producto", onupdate="CASCADE"), nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id_usuario", onupdate="CASCADE"), nullable=False
    )
    id_compra: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("compras.id_compra", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    id_venta: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("ventas.id_venta", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    tipo_movimiento: Mapped[str] = mapped_column(
        Enum(
            "entrada_compra",
            "salida_venta",
            "ajuste_positivo",
            "ajuste_negativo",
            "devolucion",
            name="tipo_movimiento_enum",
        ),
        nullable=False,
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_anterior: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_nuevo: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fecha_movimiento: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    producto = relationship("Producto")
    usuario = relationship("Usuario")
    compra = relationship("Compra")
    venta = relationship("Venta")

    @property
    def producto_nombre(self) -> str | None:
        return self.producto.nombre if self.producto else None

    @property
    def producto_sku(self) -> str | None:
        return self.producto.sku if self.producto else None

    @property
    def usuario_nombre(self) -> str | None:
        return f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else None

    @property
    def compra_factura(self) -> str | None:
        return self.compra.numero_factura if self.compra else None

    @property
    def venta_factura(self) -> str | None:
        return self.venta.numero_factura if self.venta else None
