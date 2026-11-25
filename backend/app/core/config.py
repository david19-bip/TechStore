"""Configuración general del backend TechStore (variables de entorno)."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]  # apunta a backend/
load_dotenv(BASE_DIR / ".env")

JWT_SECRET_KEY: str = (
    os.getenv("JWT_SECRET_KEY")
    or "techstore-sena-clave-secreta-cambiar-en-produccion-2026"
)
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM") or "HS256"
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES") or "480")

CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
