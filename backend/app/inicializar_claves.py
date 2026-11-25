"""Asigna contraseñas reales cifradas con bcrypt a los usuarios de prueba de techstore_db.

Ejecutar una sola vez después de importar backend/app/database/techstore_db.sql:
    python backend/app/inicializar_claves.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.security import hash_password
from app.database.conexion import SessionLocal
from app.models.usuario import Usuario

CLAVES_PRUEBA = {
    "admin@techstore.com": "Admin123*",
    "vendedor@techstore.com": "Vendedor123*",
    "bodega@techstore.com": "Bodega123*",
}


def inicializar() -> None:
    db = SessionLocal()
    try:
        actualizados = 0
        for email, clave_plana in CLAVES_PRUEBA.items():
            usuario = db.query(Usuario).filter(Usuario.email == email).first()
            if usuario:
                usuario.password_hash = hash_password(clave_plana)
                actualizados += 1
                print(f"[OK] Clave actualizada -> {email} ({usuario.rol}) | clave: {clave_plana}")
            else:
                print(f"[!] Usuario no encontrado en techstore_db: {email}")
        db.commit()
        print(f"\nTotal usuarios actualizados: {actualizados}")
    finally:
        db.close()


if __name__ == "__main__":
    inicializar()
