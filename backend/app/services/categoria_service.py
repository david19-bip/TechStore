"""Lógica de negocio para la entidad Categoría (con desactivación y auditoría)."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.repositories import categoria_repo
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate
from app.services import auditoria_service


def _snapshot(c: Categoria) -> dict:
    return {
        "id_categoria": c.id_categoria,
        "nombre": c.nombre,
        "descripcion": c.descripcion,
        "estado": c.estado,
    }


def listar(db: Session, estado: str | None = None) -> list[Categoria]:
    return categoria_repo.listar_categorias(db, estado=estado)


def obtener(db: Session, id_categoria: int) -> Categoria:
    categoria = categoria_repo.obtener_por_id(db, id_categoria)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró la categoría con id {id_categoria}.",
        )
    return categoria


def crear(
    db: Session,
    datos: CategoriaCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Categoria:
    nombre_limpio = datos.nombre.strip()
    if categoria_repo.obtener_por_nombre(db, nombre_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría llamada '{nombre_limpio}'.",
        )

    nueva = Categoria(
        nombre=nombre_limpio,
        descripcion=datos.descripcion.strip() if datos.descripcion else None,
        estado=datos.estado,
    )
    try:
        db.add(nueva)
        db.flush()
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="categorias",
            tabla_afectada="categorias",
            registro_id=nueva.id_categoria,
            accion="INSERT",
            datos_nuevos=_snapshot(nueva),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(nueva)
        return nueva
    except Exception:
        db.rollback()
        raise


def actualizar(
    db: Session,
    id_categoria: int,
    datos: CategoriaUpdate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Categoria:
    categoria = obtener(db, id_categoria)
    antes = _snapshot(categoria)
    cambios = datos.model_dump(exclude_unset=True)

    if "nombre" in cambios and cambios["nombre"] is not None:
        nuevo_nombre = cambios["nombre"].strip()
        existente = categoria_repo.obtener_por_nombre(db, nuevo_nombre)
        if existente and existente.id_categoria != id_categoria:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra categoría llamada '{nuevo_nombre}'.",
            )
        cambios["nombre"] = nuevo_nombre

    if "descripcion" in cambios and cambios["descripcion"] is not None:
        cambios["descripcion"] = cambios["descripcion"].strip()

    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)

    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="categorias",
            tabla_afectada="categorias",
            registro_id=categoria.id_categoria,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(categoria),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(categoria)
        return categoria
    except Exception:
        db.rollback()
        raise


def desactivar(
    db: Session,
    id_categoria: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Categoria:
    categoria = obtener(db, id_categoria)
    antes = _snapshot(categoria)
    categoria.estado = "inactiva"
    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="categorias",
            tabla_afectada="categorias",
            registro_id=categoria.id_categoria,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(categoria),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(categoria)
        return categoria
    except Exception:
        db.rollback()
        raise


def eliminar(
    db: Session,
    id_categoria: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> None:
    categoria = obtener(db, id_categoria)
    tiene_productos = (
        db.query(Producto)
        .filter(Producto.id_categoria == id_categoria)
        .first()
        is not None
    )
    if tiene_productos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar la categoría porque tiene productos asociados. "
                "Usa el endpoint PATCH /desactivar en su lugar."
            ),
        )
    antes = _snapshot(categoria)
    try:
        db.delete(categoria)
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="categorias",
            tabla_afectada="categorias",
            registro_id=id_categoria,
            accion="DELETE",
            datos_anteriores=antes,
            direccion_ip=direccion_ip,
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
