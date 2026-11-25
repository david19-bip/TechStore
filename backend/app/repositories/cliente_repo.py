"""Repositorio de acceso a datos para la tabla clientes."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.cliente import Cliente


def listar_clientes(
    db: Session, buscar: str | None = None, estado: str | None = None
) -> list[Cliente]:
    query = db.query(Cliente)
    if buscar:
        patron = f"%{buscar.strip()}%"
        query = query.filter(
            or_(
                Cliente.nombre.ilike(patron),
                Cliente.apellido.ilike(patron),
                Cliente.numero_documento.ilike(patron),
                Cliente.email.ilike(patron),
            )
        )
    if estado:
        query = query.filter(Cliente.estado == estado)
    return query.order_by(Cliente.id_cliente.asc()).all()


def obtener_por_id(db: Session, id_cliente: int) -> Cliente | None:
    return db.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()


def obtener_por_documento(
    db: Session, tipo_documento: str, numero_documento: str
) -> Cliente | None:
    return (
        db.query(Cliente)
        .filter(
            Cliente.tipo_documento == tipo_documento,
            Cliente.numero_documento == numero_documento,
        )
        .first()
    )


def obtener_por_email(db: Session, email: str) -> Cliente | None:
    return db.query(Cliente).filter(Cliente.email == email).first()
