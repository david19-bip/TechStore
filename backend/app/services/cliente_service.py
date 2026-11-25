"""Lógica de negocio para la gestión de clientes."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.repositories import cliente_repo
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.services import auditoria_service


def _snapshot(c: Cliente) -> dict:
    return {
        "id_cliente": c.id_cliente,
        "tipo_documento": c.tipo_documento,
        "numero_documento": c.numero_documento,
        "nombre": c.nombre,
        "apellido": c.apellido,
        "telefono": c.telefono,
        "email": c.email,
        "estado": c.estado,
    }


def listar(
    db: Session, buscar: str | None = None, estado: str | None = None
) -> list[Cliente]:
    return cliente_repo.listar_clientes(db, buscar=buscar, estado=estado)


def obtener(db: Session, id_cliente: int) -> Cliente:
    cliente = cliente_repo.obtener_por_id(db, id_cliente)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró el cliente con id {id_cliente}.",
        )
    return cliente


def crear(
    db: Session,
    datos: ClienteCreate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Cliente:
    doc_limpio = datos.numero_documento.strip()
    if cliente_repo.obtener_por_documento(db, datos.tipo_documento, doc_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Ya existe un cliente registrado con "
                f"{datos.tipo_documento} {doc_limpio}."
            ),
        )
    email_limpio = datos.email.strip().lower() if datos.email else None
    if email_limpio and cliente_repo.obtener_por_email(db, email_limpio):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un cliente con el correo '{email_limpio}'.",
        )

    nuevo = Cliente(
        tipo_documento=datos.tipo_documento,
        numero_documento=doc_limpio,
        nombre=datos.nombre.strip(),
        apellido=datos.apellido.strip(),
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
            modulo="clientes",
            tabla_afectada="clientes",
            registro_id=nuevo.id_cliente,
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
    id_cliente: int,
    datos: ClienteUpdate,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Cliente:
    cliente = obtener(db, id_cliente)
    antes = _snapshot(cliente)
    cambios = datos.model_dump(exclude_unset=True)

    tipo_final = cambios.get("tipo_documento", cliente.tipo_documento)
    doc_final = (
        cambios["numero_documento"].strip()
        if "numero_documento" in cambios and cambios["numero_documento"] is not None
        else cliente.numero_documento
    )
    existente_doc = cliente_repo.obtener_por_documento(db, tipo_final, doc_final)
    if existente_doc and existente_doc.id_cliente != id_cliente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe otro cliente con {tipo_final} {doc_final}.",
        )
    if "numero_documento" in cambios and cambios["numero_documento"] is not None:
        cambios["numero_documento"] = doc_final

    if "email" in cambios and cambios["email"] is not None:
        nuevo_email = cambios["email"].strip().lower()
        existente = cliente_repo.obtener_por_email(db, nuevo_email)
        if existente and existente.id_cliente != id_cliente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otro cliente con el correo '{nuevo_email}'.",
            )
        cambios["email"] = nuevo_email

    for campo, valor in cambios.items():
        if isinstance(valor, str):
            valor = valor.strip()
        setattr(cliente, campo, valor)

    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="clientes",
            tabla_afectada="clientes",
            registro_id=cliente.id_cliente,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(cliente),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(cliente)
        return cliente
    except Exception:
        db.rollback()
        raise


def desactivar(
    db: Session,
    id_cliente: int,
    actor: Usuario,
    direccion_ip: str | None = None,
) -> Cliente:
    cliente = obtener(db, id_cliente)
    antes = _snapshot(cliente)
    cliente.estado = "inactivo"
    try:
        auditoria_service.registrar_evento(
            db,
            id_usuario=actor.id_usuario,
            modulo="clientes",
            tabla_afectada="clientes",
            registro_id=cliente.id_cliente,
            accion="UPDATE",
            datos_anteriores=antes,
            datos_nuevos=_snapshot(cliente),
            direccion_ip=direccion_ip,
        )
        db.commit()
        db.refresh(cliente)
        return cliente
    except Exception:
        db.rollback()
        raise
