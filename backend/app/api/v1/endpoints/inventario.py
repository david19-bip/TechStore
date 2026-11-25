"""Endpoints para Inventario / Kardex (/api/v1/inventario)."""

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.core.security import obtener_ip_cliente, require_roles
from app.database.conexion import get_db
from app.models.usuario import Usuario
from app.schemas.inventario import AjusteInventarioCreate, MovimientoInventarioOut
from app.schemas.producto import ProductoOut
from app.services import inventario_service

router = APIRouter(prefix="/inventario", tags=["Inventario"])

admin_o_bodega = require_roles("administrador", "bodeguero")
todos_roles = require_roles("administrador", "vendedor", "bodeguero")


@router.get(
    "/movimientos",
    response_model=list[MovimientoInventarioOut],
    summary="Consultar historial de movimientos de inventario (Kardex)",
)
def listar_movimientos(
    id_producto: int | None = Query(default=None, gt=0),
    tipo_movimiento: Literal[
        "entrada_compra",
        "salida_venta",
        "ajuste_positivo",
        "ajuste_negativo",
        "devolucion",
    ]
    | None = Query(default=None),
    fecha_desde: datetime | None = Query(default=None),
    fecha_hasta: datetime | None = Query(default=None),
    limite: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: Usuario = Depends(admin_o_bodega),
):
    return inventario_service.listar_movimientos(
        db,
        id_producto=id_producto,
        tipo_movimiento=tipo_movimiento,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limite=limite,
    )


@router.get(
    "/alertas-stock",
    response_model=list[ProductoOut],
    summary="Consultar alertas de productos con stock bajo (stock_actual <= stock_minimo)",
)
def consultar_alertas_stock(
    db: Session = Depends(get_db),
    _: Usuario = Depends(todos_roles),
):
    return inventario_service.alertas_stock_bajo(db)


@router.post(
    "/ajustes",
    response_model=MovimientoInventarioOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrada, salida o devolución manual de inventario",
)
def registrar_ajuste_inventario(
    datos: AjusteInventarioCreate,
    request: Request,
    db: Session = Depends(get_db),
    actor: Usuario = Depends(admin_o_bodega),
):
    return inventario_service.registrar_ajuste(
        db, datos, actor=actor, direccion_ip=obtener_ip_cliente(request)
    )
