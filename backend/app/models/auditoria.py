"""Modelo ORM para la tabla auditoria."""

from datetime import datetime

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    id_usuario: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuarios.id_usuario", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    modulo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tabla_afectada: Mapped[str] = mapped_column(String(64), nullable=False)
    registro_id: Mapped[str] = mapped_column(String(64), nullable=False)
    accion: Mapped[str] = mapped_column(
        Enum("INSERT", "UPDATE", "DELETE", "LOGIN", "LOGOUT", name="accion_auditoria_enum"),
        nullable=False,
    )
    datos_anteriores: Mapped[str | None] = mapped_column(Text, nullable=True)
    datos_nuevos: Mapped[str | None] = mapped_column(Text, nullable=True)
    direccion_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    fecha_evento: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )

    usuario = relationship("Usuario")

    @property
    def usuario_email(self) -> str | None:
        return self.usuario.email if self.usuario else None

    @property
    def usuario_nombre(self) -> str | None:
        return f"{self.usuario.nombre} {self.usuario.apellido}" if self.usuario else None
