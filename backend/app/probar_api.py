"""Pruebas funcionales automatizadas de los 10 casos de la Actividad 7 (Guía SENA).

Requisitos antes de ejecutar:
1. Tener el servidor FastAPI corriendo:
       uvicorn app.main:app --reload --app-dir backend
2. Haber inicializado las claves de prueba:
       python backend/app/inicializar_claves.py
3. Ejecutar este script:
       python backend/app/probar_api.py
"""

import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

BASE_URL = "http://127.0.0.1:8000/api/v1"


def peticion(
    metodo: str, ruta: str, datos: dict | None = None, token: str | None = None
) -> tuple[int, dict | list | str]:
    headers = {"Accept": "application/json"}
    body = None
    if datos is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(datos).encode("utf-8")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = Request(f"{BASE_URL}{ruta}", data=body, headers=headers, method=metodo)
    try:
        with urlopen(req, timeout=10) as resp:
            texto = resp.read().decode("utf-8")
            return resp.status, json.loads(texto) if texto else {}
    except HTTPError as err:
        texto = err.read().decode("utf-8")
        try:
            return err.code, json.loads(texto)
        except Exception:
            return err.code, texto
    except URLError as err:
        print(f"[ERROR] No se pudo conectar con {BASE_URL}: {err}")
        print("Inicia el backend con: uvicorn app.main:app --reload --app-dir backend")
        sys.exit(1)


def iniciar_sesion(email: str, password: str) -> str:
    codigo, resp = peticion("POST", "/auth/login", {"email": email, "password": password})
    assert codigo == 200, f"Login falló para {email}: {codigo} -> {resp}"
    return resp["access_token"]


def ejecutar_pruebas() -> None:
    sufijo = uuid4().hex[:6].upper()
    sku_prueba = f"TST-{sufijo}"
    print("=" * 70)
    print("PRUEBAS FUNCIONALES TECHSTORE - ACTIVIDAD 7 (GUÍA SENA)")
    print("=" * 70)

    token_admin = iniciar_sesion("admin@techstore.com", "Admin123*")
    token_vendedor = iniciar_sesion("vendedor@techstore.com", "Vendedor123*")
    token_bodega = iniciar_sesion("bodega@techstore.com", "Bodega123*")

    # Obtener primera categoría, primer proveedor y primer cliente activos
    _, categorias = peticion("GET", "/categorias/?estado=activa", token=token_admin)
    _, proveedores = peticion("GET", "/proveedores/?estado=activo", token=token_admin)
    _, clientes = peticion("GET", "/clientes/?estado=activo", token=token_admin)
    id_cat = categorias[0]["id_categoria"]
    id_prov = proveedores[0]["id_proveedor"]
    id_cli = clientes[0]["id_cliente"]

    # Caso 1: Registrar producto válido
    codigo, prod = peticion(
        "POST",
        "/productos/",
        {
            "id_categoria": id_cat,
            "sku": sku_prueba,
            "nombre": f"Producto Prueba {sufijo}",
            "marca": "TechTest",
            "precio_compra": 100000,
            "precio_venta": 150000,
            "stock_actual": 3,
            "stock_minimo": 5,
            "estado": "activo",
        },
        token=token_admin,
    )
    assert codigo == 201, f"Caso 1 falló: {codigo} -> {prod}"
    id_prod = prod["id_producto"]
    print(f"[OK] Caso 1  - Registrar producto válido (ID={id_prod}, SKU={sku_prueba})")

    # Caso 2: Registrar código SKU repetido
    codigo, err = peticion(
        "POST",
        "/productos/",
        {
            "id_categoria": id_cat,
            "sku": sku_prueba,
            "nombre": "Duplicado",
            "marca": "TechTest",
            "precio_compra": 100000,
            "precio_venta": 150000,
            "stock_actual": 1,
            "stock_minimo": 1,
            "estado": "activo",
        },
        token=token_admin,
    )
    assert codigo == 409, f"Caso 2 falló: esperado 409, obtenido {codigo} -> {err}"
    print(f"[OK] Caso 2  - SKU repetido rechazado (HTTP {codigo}: {err['detail']})")

    # Caso 3: Registrar una compra -> existencias incrementadas
    codigo, compra = peticion(
        "POST",
        "/compras/",
        {
            "id_proveedor": id_prov,
            "numero_factura": f"FC-TEST-{sufijo}",
            "impuesto_porcentaje": 0,
            "estado": "recibida",
            "detalles": [
                {"id_producto": id_prod, "cantidad": 5, "precio_unitario": 100000}
            ],
        },
        token=token_bodega,
    )
    assert codigo == 201, f"Caso 3 falló: {codigo} -> {compra}"
    _, exist = peticion("GET", f"/productos/{id_prod}/existencias", token=token_bodega)
    assert exist["stock_actual"] == 8, f"Stock esperado 8, actual {exist['stock_actual']}"
    print(f"[OK] Caso 3  - Compra registrada por bodeguero; stock subió 3 -> {exist['stock_actual']}")

    # Caso 4: Registrar una venta -> existencias descontadas
    codigo, venta = peticion(
        "POST",
        "/ventas/",
        {
            "id_cliente": id_cli,
            "metodo_pago": "efectivo",
            "impuesto_porcentaje": 0,
            "detalles": [{"id_producto": id_prod, "cantidad": 2, "descuento": 0}],
        },
        token=token_vendedor,
    )
    assert codigo == 201, f"Caso 4 falló: {codigo} -> {venta}"
    _, exist = peticion("GET", f"/productos/{id_prod}/existencias", token=token_vendedor)
    assert exist["stock_actual"] == 6, f"Stock esperado 6, actual {exist['stock_actual']}"
    print(f"[OK] Caso 4  - Venta registrada por vendedor; stock bajó 8 -> {exist['stock_actual']}")

    # Caso 5: Vender más unidades de las disponibles -> rechazada sin modificar inventario
    codigo, err = peticion(
        "POST",
        "/ventas/",
        {
            "id_cliente": id_cli,
            "metodo_pago": "efectivo",
            "detalles": [{"id_producto": id_prod, "cantidad": 99, "descuento": 0}],
        },
        token=token_vendedor,
    )
    assert codigo == 400, f"Caso 5 falló: esperado 400, obtenido {codigo} -> {err}"
    _, exist = peticion("GET", f"/productos/{id_prod}/existencias", token=token_vendedor)
    assert exist["stock_actual"] == 6, "El inventario se alteró indebidamente"
    print(f"[OK] Caso 5  - Sobreventa rechazada (HTTP {codigo}); inventario intacto ({exist['stock_actual']})")

    # Caso 6: Consultar productos con stock bajo
    codigo, alertas = peticion("GET", "/inventario/alertas-stock", token=token_bodega)
    assert codigo == 200 and isinstance(alertas, list), f"Caso 6 falló: {codigo}"
    print(f"[OK] Caso 6  - Alerta de stock bajo consultada ({len(alertas)} producto(s) en alerta)")

    # Caso 7: Ingresar con rol vendedor -> acceso permitido a ventas/productos/clientes
    codigo, perfil = peticion("GET", "/auth/me", token=token_vendedor)
    assert codigo == 200 and perfil["rol"] == "vendedor"
    print(f"[OK] Caso 7  - Rol vendedor autenticado ({perfil['email']})")

    # Caso 8: Intentar ejecutar una operación no autorizada (vendedor intentando ver auditoría y crear producto)
    c1, _ = peticion("GET", "/auditoria/", token=token_vendedor)
    c2, _ = peticion("GET", "/usuarios/", token=token_vendedor)
    c3, _ = peticion("GET", "/ventas/", token=token_bodega)
    assert c1 == 403 and c2 == 403 and c3 == 403, f"Caso 8 falló: {c1}, {c2}, {c3}"
    print("[OK] Caso 8  - Operaciones no autorizadas rechazadas por el backend (HTTP 403)")

    # Caso 9: Verificar registro de auditoría generado por la venta
    codigo, eventos = peticion(
        "GET", "/auditoria/?modulo=ventas&accion=INSERT&limite=5", token=token_admin
    )
    assert codigo == 200 and any(
        str(e["registro_id"]) == str(venta["id_venta"]) for e in eventos
    ), "Caso 9 falló: no se encontró auditoría para la venta"
    print(f"[OK] Caso 9  - Registro de auditoría verificado para venta ID={venta['id_venta']}")

    # Caso 10: Consultar reporte de ventas
    codigo, rep = peticion("GET", "/reportes/ventas", token=token_admin)
    assert codigo == 200 and rep["cantidad_ventas"] >= 1, f"Caso 10 falló: {codigo}"
    print(
        f"[OK] Caso 10 - Reporte de ventas consistente "
        f"({rep['cantidad_ventas']} ventas, ingresos=${rep['ingresos_totales']:,.0f})"
    )

    print("=" * 70)
    print("TODOS LOS 10 CASOS DE PRUEBA DE LA ACTIVIDAD 7 PASARON EXITOSAMENTE.")
    print("=" * 70)


if __name__ == "__main__":
    ejecutar_pruebas()
