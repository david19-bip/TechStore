"""Lógica de negocio para la gestión de usuarios (solo Administrador)."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.usuario import Usuario
from app.repositories import usuario_repo
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services import auditoria_service


def _snapshot(u: Usuario) -> dict:
    return {
        "id_usuario": u.id_usuario,
        "nombre": u.nombre,
        "apellido": u.apellido,
        "email": u.email,
        "rol": u.rol,
        "estado": u.estado,
    }


def listar(
    db: Session, rol: str | None = None, estado: str | None = None
) -> list[Usuario]:
    return usuario_repo.listar_usuarios(db, rol=rol, estado=estado)


def obtener(db: Session, id_usuario: int) -> Usuario:
    usuario = usuario_repo.obtener_por_id(db, id_usuario)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el usuario con id {id_usuario}.",
        )
    return usuario


def crear(
    db: Session,
    datos: UsuarioCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Usuario:
    email_limpio = datos.email.strip().lower()
    if usuario_repo.obtener_por_email(db, email_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un usuario registrado con el correo '{email_limpio}'.",
        )

    nuevo = Usuario(
        nombre=datos.nombre.strip(),
        apellido=datos.apellido.strip(),
        email=email_limpio,
        password_hash=hash_password(datos.password),
        rol=datos.rol,
        estado=datos.estado,
    )
    try:
        usuario_repo.crear_usuario(db, nuevo)
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="usuarios",
            tabla_afectada="usuarios",
            registro_id=nuevo.id_usuario,
            accion="INSERT",
            datos_nuevos=_snapshot(nuevo),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception:
        db.rollback()
        raise


def actualizar(
    db: Session,
    id_usuario: int,
    datos: UsuarioUpdate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Usuario:
    usuario = obtener(db, id_usuario)
    antes = _snapshot(usuario)
    cambios = datos.model_dump(exclude_unset=True)

    if "email" in cambios and cambios["email"] is not None:
        nuevo_email = cambios["email"].strip().lower()
        existente = usuario_repo.obtener_por_email(db, nuevo_email)
        if existente and existente.id_usuario != id_usuario:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro usuario con el correo '{nuevo_email}'.",
            )
        cambios["email"] = nuevo_email

    if "password" in cambios and cambios["password"]:
        usuario.password_hash = hash_password(cambios.pop("password"))
    else:
        cambios.pop("password", None)

    for campo, valor in cambios.items():
        if campo in ("nombre", "apellido") and isinstance(valor, str):
            valor = valor.strip()
        setattr(usuario, campo, valor)

    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="usuarios",
            tabla_afectada="usuarios",
            registro_id=usuario.id_usuario,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(usuario),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception:
        db.rollback()
        raise


def desactivar(
    db: Session,
    id_usuario: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Usuario:
    if id_usuario == actor.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta de administrador.",
        )
    usuario = obtener(db, id_usuario)
    antes = _snapshot(usuario)
    usuario.estado = "inactivo"
    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="usuarios",
            tabla_afectada="usuarios",
            registro_id=usuario.id_usuario,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(usuario),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception:
        db.rollback()
        raise
