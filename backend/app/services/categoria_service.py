"""Lógica de negocio para la gestión de categorías."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.repositories import categoria_repo
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


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


def crear(db: Session, datos: CategoriaCreate) -> Categoria:
    nombre_limpio = datos.nombre.strip()
    if categoria_repo.obtener_por_nombre(db, nombre_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una categoría con el nombre '{nombre_limpio}'.",
        )

    nueva = Categoria(
        nombre=nombre_limpio,
        descripcion=datos.descripcion,
        estado=datos.estado,
    )
    return categoria_repo.crear_categoria(db, nueva)


def actualizar(
    db: Session, id_categoria: int, datos: CategoriaUpdate
) -> Categoria:
    categoria = obtener(db, id_categoria)
    cambios = datos.model_dump(exclude_unset=True)

    if "nombre" in cambios and cambios["nombre"] is not None:
        nuevo_nombre = cambios["nombre"].strip()
        existente = categoria_repo.obtener_por_nombre(db, nuevo_nombre)
        if existente and existente.id_categoria != id_categoria:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra categoría con el nombre '{nuevo_nombre}'.",
            )
        cambios["nombre"] = nuevo_nombre

    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)

    return categoria_repo.guardar_categoria(db, categoria)


def eliminar(db: Session, id_categoria: int) -> dict[str, str]:
    categoria = obtener(db, id_categoria)
    try:
        categoria_repo.eliminar_categoria(db, categoria)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No se puede eliminar la categoría porque tiene productos asociados. "
                "Puedes cambiar su estado a 'inactiva'."
            ),
        )
    return {"mensaje": f"Categoría {id_categoria} eliminada correctamente."}
