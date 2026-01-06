"""
Base declarativa para modelos SQLAlchemy.
Todos los modelos heredan de Base.
"""
from datetime import datetime
from typing import Any
import uuid

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos SQLAlchemy.
    
    Incluye:
    - id: UUID generado automáticamente
    - created_at: Timestamp de creación
    - updated_at: Timestamp de última actualización
    """
    
    # Genera nombre de tabla automáticamente desde el nombre de la clase
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Convierte CamelCase a snake_case para nombre de tabla."""
        name = cls.__name__
        # Convierte CamelCase a snake_case
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower() + 's'
    
    # Columnas comunes a todos los modelos
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convierte el modelo a diccionario."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
