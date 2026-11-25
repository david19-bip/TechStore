"""Repositorio de acceso a datos para la tabla usuarios."""

from sqlalchemy.orm import Session

from app.models.usuario import Usuario


def listar_usuarios(
    db: Session, rol: str | None = None, estado: str | None = None
) -> list[Usuario]:
    query = db.query(Usuario)
    if rol:
        query = query.filter(Usuario.rol == rol)
    if estado:
        query = query.filter(Usuario.estado == estado)
    return query.order_by(Usuario.id_usuario.asc()).all()


def obtener_por_id(db: Session, id_usuario: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()


def obtener_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def crear_usuario(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.flush()
    return usuario
