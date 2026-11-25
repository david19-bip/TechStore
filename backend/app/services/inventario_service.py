"""Lógica de negocio para el control de inventario (Kardex, alertas y ajustes)."""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.movimiento_inventario import MovimientoInventario
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.repositories import inventario_repo, producto_repo
from app.schemas.inventario import AjusteInventarioCreate
from app.services import auditoria_service


def listar_movimientos(
    db: Session,
    id_producto: int | None = None,
    tipo_movimiento: str | None = None,
    fecha_desde: datetime | None = None,
    fecha_hasta: datetime | None = None,
    limite: int = 200,
) -> list[MovimientoInventario]:
    return inventario_repo.listar_movimientos(
        db,
        id_producto=id_producto,
        tipo_movimiento=tipo_movimiento,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limite=limite,
    )


def alertas_stock_bajo(db: Session) -> list[Producto]:
    return producto_repo.listar_productos(
        db, estado="activo", solo_bajo_stock=True
    )


def registrar_ajuste(
    db: Session,
    datos: AjusteInventarioCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> MovimientoInventario:
    """Registra una entrada o salida manual de inventario en una transacción."""
    try:
        producto = (
            db.query(Producto)
            .filter(Producto.id_producto == datos.id_producto)
            .with_for_update()
            .first()
        )
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe el producto con id {datos.id_producto}.",
            )

        stock_anterior = producto.stock_actual
        if datos.tipo_movimiento == "ajuste_negativo":
            if stock_anterior < datos.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"No se puede descontar {datos.cantidad} unidades de '{producto.nombre}': "
                        f"stock actual disponible es {stock_anterior}."
                    ),
                )
            stock_nuevo = stock_anterior - datos.cantidad
        else:
            stock_nuevo = stock_anterior + datos.cantidad

        producto.stock_actual = stock_nuevo

        movimiento = MovimientoInventario(
            id_producto=producto.id_producto,
            id_usuario=actor.id_usuario,
            id_compra=None,
            id_venta=None,
            tipo_movimiento=datos.tipo_movimiento,
            cantidad=datos.cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            motivo=datos.motivo.strip(),
        )
        db.add(movimiento)
        db.flush()

        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="inventario",
            tabla_afectada="movimientos_inventario",
            registro_id=movimiento.id_movimiento,
            accion="INSERT",
            datos_anteriores={"stock_actual": stock_anterior},
            datos_nuevos={
                "id_producto": producto.id_producto,
                "tipo_movimiento": datos.tipo_movimiento,
                "cantidad": datos.cantidad,
                "stock_nuevo": stock_nuevo,
                "motivo": movimiento.motivo,
            },
            direccion_ip=direccion_ip,
        )

        db.commit()
        movimientos = inventario_repo.listar_movimientos(
            db, id_producto=producto.id_producto, limite=1
        )
        return movimientos[0]
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar el ajuste de inventario: {exc}",
        )
