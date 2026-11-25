"""Servicio de reportes e indicadores (Dashboard, Ventas, Compras y Reto Integrador)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.cliente import Cliente
from app.models.compra import Compra
from app.models.producto import Producto
from app.models.proveedor import Proveedor
from app.models.venta import DetalleVenta, Venta


def _a_float(valor: Decimal | int | float | None) -> float:
    return float(valor) if valor is not None else 0.0


def obtener_dashboard(db: Session) -> dict:
    total_categorias = (
        db.query(func.count(Categoria.id_categoria))
        .filter(Categoria.estado == "activa")
        .scalar()
        or 0
    )
    total_productos = (
        db.query(func.count(Producto.id_producto))
        .filter(Producto.estado == "activo")
        .scalar()
        or 0
    )
    productos_bajo_stock = (
        db.query(func.count(Producto.id_producto))
        .filter(
            Producto.estado == "activo",
            Producto.stock_actual <= Producto.stock_minimo,
        )
        .scalar()
        or 0
    )
    unidades_inventario = (
        db.query(func.coalesce(func.sum(Producto.stock_actual), 0))
        .filter(Producto.estado == "activo")
        .scalar()
        or 0
    )
    total_proveedores = (
        db.query(func.count(Proveedor.id_proveedor))
        .filter(Proveedor.estado == "activo")
        .scalar()
        or 0
    )
    total_clientes = (
        db.query(func.count(Cliente.id_cliente))
        .filter(Cliente.estado == "activo")
        .scalar()
        or 0
    )

    compras_stats = (
        db.query(
            func.count(Compra.id_compra),
            func.coalesce(func.sum(Compra.total), 0),
        )
        .filter(Compra.estado != "anulada")
        .first()
    )
    ventas_stats = (
        db.query(
            func.count(Venta.id_venta),
            func.coalesce(func.sum(Venta.total), 0),
        )
        .filter(Venta.estado != "anulada")
        .first()
    )

    costo_vendido = (
        db.query(
            func.coalesce(
                func.sum(DetalleVenta.cantidad * Producto.precio_compra), 0
            )
        )
        .join(Venta, Venta.id_venta == DetalleVenta.id_venta)
        .join(Producto, Producto.id_producto == DetalleVenta.id_producto)
        .filter(Venta.estado != "anulada")
        .scalar()
        or 0
    )

    ingresos_ventas = _a_float(ventas_stats[1] if ventas_stats else 0)
    costo_vendido_float = _a_float(costo_vendido)

    return {
        "categorias_activas": int(total_categorias),
        "productos_activos": int(total_productos),
        "productos_bajo_stock": int(productos_bajo_stock),
        "unidades_en_inventario": int(unidades_inventario),
        "proveedores_activos": int(total_proveedores),
        "clientes_activos": int(total_clientes),
        "total_compras_registradas": int(compras_stats[0] if compras_stats else 0),
        "valor_total_compras": _a_float(compras_stats[1] if compras_stats else 0),
        "total_ventas_registradas": int(ventas_stats[0] if ventas_stats else 0),
        "ingresos_totales_ventas": ingresos_ventas,
        "costo_productos_vendidos": costo_vendido_float,
        "utilidad_bruta": round(ingresos_ventas - costo_vendido_float, 2),
    }


def reporte_compras(
    db: Session,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    id_proveedor: int | None = None,
) -> dict:
    query = (
        db.query(
            Compra.id_compra,
            Compra.numero_factura,
            Compra.fecha_compra,
            Compra.subtotal,
            Compra.impuesto,
            Compra.total,
            Compra.estado,
            Proveedor.razon_social.label("proveedor"),
        )
        .join(Proveedor, Proveedor.id_proveedor == Compra.id_proveedor)
        .filter(Compra.estado != "anulada")
    )
    if fecha_desde:
        query = query.filter(Compra.fecha_compra >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Compra.fecha_compra <= fecha_hasta)
    if id_proveedor is not None:
        query = query.filter(Compra.id_proveedor == id_proveedor)

    filas = query.order_by(Compra.fecha_compra.desc()).all()
    items = [
        {
            "id_compra": f.id_compra,
            "numero_factura": f.numero_factura,
            "fecha_compra": f.fecha_compra,
            "proveedor": f.proveedor,
            "subtotal": _a_float(f.subtotal),
            "impuesto": _a_float(f.impuesto),
            "total": _a_float(f.total),
            "estado": f.estado,
        }
        for f in filas
    ]
    return {
        "cantidad_compras": len(items),
        "valor_total_compras": round(sum(i["total"] for i in items), 2),
        "compras": items,
    }


def reporte_ventas(
    db: Session,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    id_cliente: int | None = None,
) -> dict:
    query = (
        db.query(
            Venta.id_venta,
            Venta.numero_factura,
            Venta.fecha_venta,
            Venta.metodo_pago,
            Venta.subtotal,
            Venta.descuento_total,
            Venta.impuesto,
            Venta.total,
            Venta.estado,
            Cliente.nombre.label("cliente_nombre"),
            Cliente.apellido.label("cliente_apellido"),
        )
        .join(Cliente, Cliente.id_cliente == Venta.id_cliente)
        .filter(Venta.estado != "anulada")
    )
    if fecha_desde:
        query = query.filter(Venta.fecha_venta >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Venta.fecha_venta <= fecha_hasta)
    if id_cliente is not None:
        query = query.filter(Venta.id_cliente == id_cliente)

    filas = query.order_by(Venta.fecha_venta.desc()).all()
    items = [
        {
            "id_venta": f.id_venta,
            "numero_factura": f.numero_factura,
            "fecha_venta": f.fecha_venta,
            "cliente": f"{f.cliente_nombre} {f.cliente_apellido}",
            "metodo_pago": f.metodo_pago,
            "subtotal": _a_float(f.subtotal),
            "descuento_total": _a_float(f.descuento_total),
            "impuesto": _a_float(f.impuesto),
            "total": _a_float(f.total),
            "estado": f.estado,
        }
        for f in filas
    ]
    return {
        "cantidad_ventas": len(items),
        "ingresos_totales": round(sum(i["total"] for i in items), 2),
        "descuentos_totales": round(sum(i["descuento_total"] for i in items), 2),
        "ventas": items,
    }


def productos_mas_vendidos(db: Session, limite: int = 10) -> list[dict]:
    filas = (
        db.query(
            Producto.id_producto,
            Producto.sku,
            Producto.nombre,
            Producto.stock_actual,
            func.sum(DetalleVenta.cantidad).label("unidades_vendidas"),
            func.sum(DetalleVenta.subtotal).label("ingresos_generados"),
            func.sum(DetalleVenta.cantidad * Producto.precio_compra).label(
                "costo_total"
            ),
        )
        .join(DetalleVenta, DetalleVenta.id_producto == Producto.id_producto)
        .join(Venta, Venta.id_venta == DetalleVenta.id_venta)
        .filter(Venta.estado != "anulada")
        .group_by(
            Producto.id_producto,
            Producto.sku,
            Producto.nombre,
            Producto.stock_actual,
        )
        .order_by(func.sum(DetalleVenta.cantidad).desc())
        .limit(limite)
        .all()
    )
    resultado = []
    for f in filas:
        ingresos = _a_float(f.ingresos_generados)
        costo = _a_float(f.costo_total)
        resultado.append(
            {
                "id_producto": f.id_producto,
                "sku": f.sku,
                "nombre": f.nombre,
                "stock_actual": int(f.stock_actual),
                "unidades_vendidas": int(f.unidades_vendidas or 0),
                "ingresos_generados": round(ingresos, 2),
                "costo_productos_vendidos": round(costo, 2),
                "utilidad_bruta": round(ingresos - costo, 2),
            }
        )
    return resultado


def resumen_financiero(db: Session) -> dict:
    """Genera el reporte integral exigido en el Reto Integrador de la Guía SENA."""
    valor_compras = (
        db.query(func.coalesce(func.sum(Compra.total), 0))
        .filter(Compra.estado != "anulada")
        .scalar()
        or 0
    )
    ingresos_ventas = (
        db.query(func.coalesce(func.sum(Venta.total), 0))
        .filter(Venta.estado != "anulada")
        .scalar()
        or 0
    )
    costo_vendido = (
        db.query(
            func.coalesce(
                func.sum(DetalleVenta.cantidad * Producto.precio_compra), 0
            )
        )
        .join(Venta, Venta.id_venta == DetalleVenta.id_venta)
        .join(Producto, Producto.id_producto == DetalleVenta.id_producto)
        .filter(Venta.estado != "anulada")
        .scalar()
        or 0
    )

    productos = (
        db.query(Producto)
        .filter(Producto.estado == "activo")
        .order_by(Producto.id_producto.asc())
        .all()
    )
    existencias_finales = [
        {
            "id_producto": p.id_producto,
            "sku": p.sku,
            "nombre": p.nombre,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            "costo_unitario": _a_float(p.precio_compra),
            "precio_venta": _a_float(p.precio_venta),
            "valor_inventario_costo": round(
                p.stock_actual * _a_float(p.precio_compra), 2
            ),
        }
        for p in productos
    ]

    ingresos_f = _a_float(ingresos_ventas)
    costo_f = _a_float(costo_vendido)

    return {
        "valor_total_compras": round(_a_float(valor_compras), 2),
        "ingresos_por_ventas": round(ingresos_f, 2),
        "costo_productos_vendidos": round(costo_f, 2),
        "utilidad_bruta": round(ingresos_f - costo_f, 2),
        "valor_inventario_actual_al_costo": round(
            sum(e["valor_inventario_costo"] for e in existencias_finales), 2
        ),
        "existencias_finales": existencias_finales,
    }
