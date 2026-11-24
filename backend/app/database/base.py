"""Clase base declarativa de SQLAlchemy para los modelos de TechStore."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base ORM compartida por todos los modelos de techstore_db."""
