"""Servicio de autenticación (login, token JWT y cierre de sesión con auditoría)."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.usuario import Usuario
from app.repositories import usuario_repo
from app.services import auditoria_service


def autenticar_usuario(
    db: Session, email: str, password: str, direccion_ip: str | None = None
) -> dict:
    usuario = usuario_repo.obtener_por_email(db, email.strip().lower())
    if not usuario or not verify_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )
    if usuario.estado != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario se encuentra inactivo. Contacta al administrador.",
        )

    token = create_access_token(usuario)
    auditoria_service.registrar_evento(
        db,
        id_usuario=usuario.id_usuario,
        modulo="autenticacion",
        tabla_afectada="usuarios",
        registro_id=usuario.id_usuario,
        accion="LOGIN",
        datos_nuevos={"email": usuario.email, "rol": usuario.rol},
        direccion_ip=direccion_ip,
    )
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": usuario,
    }


def cerrar_sesion(
    db: Session, usuario: Usuario, direccion_ip: str | None = None
) -> dict[str, str]:
    auditoria_service.registrar_evento(
        db,
        id_usuario=usuario.id_usuario,
        modulo="autenticacion",
        tabla_afectada="usuarios",
        registro_id=usuario.id_usuario,
        accion="LOGOUT",
        datos_nuevos={"email": usuario.email, "rol": usuario.rol},
        direccion_ip=direccion_ip,
    )
    db.commit()
    return {"mensaje": "Sesión cerrada correctamente."}
