"""Repositorio de acceso a datos para la tabla proveedores."""

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.proveedor import Proveedor


def listar_proveedores(
    db: Session, buscar: str | None = None, estado: str | None = None
) -> list[Proveedor]:
    query = db.query(Proveedor)
    if buscar:
        patron = f"%{buscar.strip()}%"
        query = query.filter(
            or_(
                Proveedor.razon_social.ilike(patron),
                Proveedor.nit.ilike(patron),
                Proveedor.ciudad.ilike(patron),
            )
        )
    if estado:
        query = query.filter(Proveedor.estado == estado)
    return query.order_by(Proveedor.id_proveedor.asc()).all()


def obtener_por_id(db: Session, id_proveedor: int) -> Proveedor | None:
    return (
        db.query(Proveedor)
        .filter(Proveedor.id_proveedor == id_proveedor)
        .first()
    )


def obtener_por_nit(db: Session, nit: str) -> Proveedor | None:
    return db.query(Proveedor).filter(Proveedor.nit == nit).first()


def obtener_por_email(db: Session, email: str) -> Proveedor | None:
    return db.query(Proveedor).filter(Proveedor.email == email).first()
