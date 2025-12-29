"""
Base models and mixins for SQLAlchemy ORM
"""
from datetime import datetime
from typing import Any
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""
    
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when record was last updated"
    )


class UUIDMixin:
    """Mixin to add UUID primary key"""
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Unique identifier"
    )


def generate_uuid() -> uuid.UUID:
    """Generate a new UUID"""
    return uuid.uuid4()