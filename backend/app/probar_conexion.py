"""Script de prueba de conexión y verificación de la base de datos techstore_db."""

import sys
from pathlib import Path

# Permite ejecutar tanto `python app/probar_conexion.py` como `python -m app.probar_conexion`
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.database.conexion import DB_HOST, DB_NAME, DB_PORT, DB_USER, engine

TABLAS_ESPERADAS = [
    "auditoria",
    "categorias",
    "clientes",
    "compras",
    "detalle_compras",
    "detalle_ventas",
    "movimientos_inventario",
    "productos",
    "proveedores",
    "usuarios",
    "ventas",
]


def probar_conexion() -> None:
    print("=" * 65)
    print("  PRUEBA DE CONEXIÓN A BASE DE DATOS - TECHSTORE")
    print("=" * 65)
    print(f"Servidor : {DB_HOST}:{DB_PORT}")
    print(f"Usuario  : {DB_USER}")
    print(f"Base DB  : {DB_NAME}")
    print("-" * 65)

    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT VERSION()")).scalar()
            db_actual = conn.execute(text("SELECT DATABASE()")).scalar()
            print("[OK] Conexión exitosa.")
            print(f"     Motor activo : {version}")
            print(f"     Base activa  : {db_actual}")
            print("-" * 65)

            # 1. Verificar tablas existentes
            tablas = [
                fila[0]
                for fila in conn.execute(text("SHOW TABLES")).fetchall()
            ]
            tablas_ordenadas = sorted(tablas)
            print(f"[1] Tablas encontradas ({len(tablas_ordenadas)}):")
            for tabla in tablas_ordenadas:
                print(f"    - {tabla}")

            faltantes = set(TABLAS_ESPERADAS) - set(tablas_ordenadas)
            if faltantes:
                print(f"[!] Faltan tablas esperadas: {sorted(faltantes)}")
            else:
                print("[OK] Todas las 11 tablas requeridas existen.")

            print("-" * 65)

            # 2. Conteo de registros principales
            print("[2] Conteo de registros en tablas maestras y catálogo:")
            for tabla in ["usuarios", "categorias", "proveedores", "clientes", "productos"]:
                if tabla in tablas_ordenadas:
                    total = conn.execute(text(f"SELECT COUNT(*) FROM `{tabla}`")).scalar()
                    print(f"    - {tabla:<15}: {total} registros")

            print("-" * 65)

            # 3. Consulta JOIN de prueba (productos + categorias)
            print("[3] Muestra de productos con su categoría (primeros 5):")
            consulta = text(
                """
                SELECT p.sku, p.nombre, c.nombre AS categoria,
                       p.precio_venta, p.stock_actual
                FROM productos p
                JOIN categorias c ON c.id_categoria = p.id_categoria
                ORDER BY p.id_producto
                LIMIT 5
                """
            )
            filas = conn.execute(consulta).fetchall()
            if not filas:
                print("    (No hay productos cargados todavía)")
            else:
                for sku, nombre, categoria, precio_venta, stock in filas:
                    print(
                        f"    - [{sku}] {nombre} | Cat: {categoria} "
                        f"| Precio: ${precio_venta:,.2f} | Stock: {stock}"
                    )

            print("=" * 65)
            print("  VERIFICACIÓN COMPLETADA SIN ERRORES")
            print("=" * 65)

    except OperationalError as err:
        print("[ERROR] No se pudo conectar a MySQL/MariaDB.")
        print("Revisa que:")
        print("  1. MySQL esté encendido en el Panel de Control de XAMPP.")
        print("  2. Ya hayas importado backend/app/database/techstore_db.sql en phpMyAdmin.")
        print("  3. Los datos en backend/.env (host, puerto, usuario, clave) sean correctos.")
        print(f"\nDetalle técnico: {err.orig}")
        sys.exit(1)

    except SQLAlchemyError as err:
        print(f"[ERROR] Error de SQLAlchemy al consultar la base de datos: {err}")
        sys.exit(1)


if __name__ == "__main__":
    probar_conexion()
