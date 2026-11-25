"""Lógica de negocio para la gestión de proveedores."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.proveedor import Proveedor
from app.models.usuario import Usuario
from app.repositories import proveedor_repo
from app.schemas.proveedor import ProveedorCreate, ProveedorUpdate
from app.services import auditoria_service


def _snapshot(p: Proveedor) -> dict:
    return {
        "id_proveedor": p.id_proveedor,
        "nit": p.nit,
        "razon_social": p.razon_social,
        "telefono": p.telefono,
        "email": p.email,
        "ciudad": p.ciudad,
        "estado": p.estado,
    }


def listar(
    db: Session, buscar: str | None = None, estado: str | None = None
) -> list[Proveedor]:
    return proveedor_repo.listar_proveedores(db, buscar=buscar, estado=estado)


def obtener(db: Session, id_proveedor: int) -> Proveedor:
    proveedor = proveedor_repo.obtener_por_id(db, id_proveedor)
    if not proveedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el proveedor con id {id_proveedor}.",
        )
    return proveedor


def crear(
    db: Session,
    datos: ProveedorCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Proveedor:
    nit_limpio = datos.nit.strip()
    if proveedor_repo.obtener_por_nit(db, nit_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un proveedor con el NIT '{nit_limpio}'.",
        )
    email_limpio = datos.email.strip().lower() if datos.email else None
    if email_limpio and proveedor_repo.obtener_por_email(db, email_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un proveedor con el correo '{email_limpio}'.",
        )

    nuevo = Proveedor(
        nit=nit_limpio,
        razon_social=datos.razon_social.strip(),
        nombre_contacto=datos.nombre_contacto.strip() if datos.nombre_contacto else None,
        telefono=datos.telefono.strip() if datos.telefono else None,
        email=email_limpio,
        direccion=datos.direccion.strip() if datos.direccion else None,
        ciudad=datos.ciudad.strip() if datos.ciudad else None,
        estado=datos.estado,
    )
    try:
        db.add(nuevo)
        db.flush()
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="proveedores",
            tabla_afectada="proveedores",
            registro_id=nuevo.id_proveedor,
            accion="INSERT",
            datos_nuevos=_snapshot(nuevo),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception:
        db.rollback()
        raise


def actualizar(
    db: Session,
    id_proveedor: int,
    datos: ProveedorUpdate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Proveedor:
    proveedor = obtener(db, id_proveedor)
    antes = _snapshot(proveedor)
    cambios = datos.model_dump(exclude_unset=True)

    if "nit" in cambios and cambios["nit"] is not None:
        nuevo_nit = cambios["nit"].strip()
        existente = proveedor_repo.obtener_por_nit(db, nuevo_nit)
        if existente and existente.id_proveedor != id_proveedor:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro proveedor con el NIT '{nuevo_nit}'.",
            )
        cambios["nit"] = nuevo_nit

    if "email" in cambios and cambios["email"] is not None:
        nuevo_email = cambios["email"].strip().lower()
        existente = proveedor_repo.obtener_por_email(db, nuevo_email)
        if existente and existente.id_proveedor != id_proveedor:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro proveedor con el correo '{nuevo_email}'.",
            )
        cambios["email"] = nuevo_email

    for campo, valor in cambios.items():
        if isinstance(valor, str):
            valor = valor.strip()
        setattr(proveedor, campo, valor)

    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="proveedores",
            tabla_afectada="proveedores",
            registro_id=proveedor.id_proveedor,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(proveedor),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(proveedor)
        return proveedor
    except Exception:
        db.rollback()
        raise


def desactivar(
    db: Session,
    id_proveedor: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Proveedor:
    proveedor = obtener(db, id_proveedor)
    antes = _snapshot(proveedor)
    proveedor.estado = "inactivo"
    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="proveedores",
            tabla_afectada="proveedores",
            registro_id=proveedor.id_proveedor,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(proveedor),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(proveedor)
        return proveedor
    except Exception:
        db.rollback()
        raise
