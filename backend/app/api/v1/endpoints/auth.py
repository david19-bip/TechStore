"""Endpoints de autenticación JWT (/api/v1/auth)."""

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import get_current_user, obtener_ip_cliente
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuario import UsuarioOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión con JSON (correo y contraseña)",
)
def login(
    datos: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return auth_service.autenticar_usuario(
        db,
        email=datos.email,
        password=datos.password,
        direccion_ip=obtener_ip_cliente(request),
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="Token OAuth2 (compatible con el botón Authorize de Swagger UI)",
)
def login_oauth2(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return auth_service.autenticar_usuario(
        db,
        email=form_data.username,
        password=form_data.password,
        direccion_ip=obtener_ip_cliente(request),
    )


@router.get(
    "/me",
    response_model=UsuarioOut,
    summary="Obtener el perfil del usuario autenticado",
)
def perfil_actual(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.post("/logout", summary="Cerrar sesión y registrar evento en auditoría")
def logout(
    request: Request,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return auth_service.cerrar_sesion(
        db, usuario=usuario, direccion_ip=obtener_ip_cliente(request)
    )
