"""Módulo de conexión a la base de datos techstore_db (MySQL / MariaDB)."""

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Carga backend/.env automáticamente (sin importar desde qué carpeta se ejecute)
BASE_DIR = Path(__file__).resolve().parents[2]  # apunta a backend/
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1") or "127.0.0.1"
DB_PORT = os.getenv("DB_PORT", "3306") or "3306"
DB_USER = os.getenv("DB_USER", "root") or "root"
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "techstore_db") or "techstore_db"

_password_escaped = quote_plus(DB_PASSWORD)
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{_password_escaped}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Generador de sesiones de base de datos (listo para usar en FastAPI)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
