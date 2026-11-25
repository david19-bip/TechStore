"""Utilidades de seguridad: hash bcrypt, tokens JWT y control de roles."""

from datetime import datetime, timedelta, timezone
from typing import Callable

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY
from app.database.conexion import get_db
from app.models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def hash_password(password: str) -> str:
    """Genera un hash seguro con bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano contra su hash bcrypt."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def create_access_token(user: Usuario) -> str:
    """Crea un JWT firmado con los datos del usuario autenticado."""
    ahora = datetime.now(timezone.utc)
    expira = ahora + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id_usuario),
        "email": user.email,
        "rol": user.rol,
        "iat": ahora,
        "exp": expira,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """Obtiene el usuario autenticado a partir del Bearer token JWT."""
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión expirada. Inicia sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise credenciales_invalidas
        id_usuario = int(sub)
    except (jwt.PyJWTError, ValueError):
        raise credenciales_invalidas

    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario or usuario.estado != "activo":
        raise credenciales_invalidas
    return usuario


def require_roles(*roles_permitidos: str) -> Callable:
    """Dependencia FastAPI que restringe un endpoint a los roles indicados."""

    def verificar_rol(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol not in roles_permitidos:
            roles_txt = ", ".join(roles_permitidos)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acceso denegado para el rol '{usuario.rol}'. "
                    f"Perfiles autorizados: {roles_txt}."
                ),
            )
        return usuario

    return verificar_rol


def obtener_ip_cliente(request: Request) -> str | None:
    """Extrae la IP del cliente para registrar en auditoría."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:45]
    if request.client:
        return request.client.host[:45]
    return None
