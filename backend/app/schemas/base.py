"""
Schemas base compartidos entre módulos.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Schema base con configuración común."""
    
    model_config = ConfigDict(
        from_attributes=True,  # Permite crear desde objetos SQLAlchemy
        populate_by_name=True
    )


class TimestampMixin(BaseModel):
    """Mixin para campos de timestamp."""
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """Mixin para campo ID."""
    id: UUID
