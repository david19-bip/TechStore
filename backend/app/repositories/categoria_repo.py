"""Repositorio de acceso a datos para la tabla categorias."""

from sqlalchemy.orm import Session

from app.models.categoria import Categoria


def listar_categorias(db: Session, estado: str | None = None) -> list[Categoria]:
    query = db.query(Categoria)
    if estado:
        query = query.filter(Categoria.estado == estado)
    return query.order_by(Categoria.id_categoria.asc()).all()


def obtener_por_id(db: Session, id_categoria: int) -> Categoria | None:
    return (
        db.query(Categoria)
        .filter(Categoria.id_categoria == id_categoria)
        .first()
    )


def obtener_por_nombre(db: Session, nombre: str) -> Categoria | None:
    return db.query(Categoria).filter(Categoria.nombre == nombre).first()


def crear_categoria(db: Session, categoria: Categoria) -> Categoria:
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def guardar_categoria(db: Session, categoria: Categoria) -> Categoria:
    db.commit()
    db.refresh(categoria)
    return categoria


def eliminar_categoria(db: Session, categoria: Categoria) -> None:
    db.delete(categoria)
    db.commit()
