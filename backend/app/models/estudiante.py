"""
Modelo Estudiante - Usuario del sistema.
Pertenece a una universidad y una carrera.
"""
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class Estudiante(Base):
    """
    Representa un estudiante registrado en el sistema.
    
    Contiene:
    - Información de autenticación
    - Relación con universidad y carrera
    - Preferencias personales
    """
    
    # Relación con universidad (multi-tenant)
    universidad_id = Column(
        UUID(as_uuid=True),
        ForeignKey("universidads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Relación con carrera
    carrera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("carreras.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Información de autenticación
    matricula = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Información personal
    nombre = Column(String(100), nullable=True)
    apellido = Column(String(100), nullable=True)
    
    # Estado
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Preferencias del estudiante
    # Estructura esperada:
    # {
    #   "disponibilidad_default": {
    #     "lunes": ["09:00-11:00", "14:00-18:00"],
    #     "martes": ["09:00-15:00"]
    #   },
    #   "preferencias_horario": {
    #     "evitar_huecos": true,
    #     "preferir_mañanas": false,
    #     "max_materias": 6
    #   }
    # }
    preferencias = Column(JSONB, default={}, nullable=False)
    
    # Relaciones
    universidad = relationship("Universidad", back_populates="estudiantes")
    carrera = relationship("Carrera", back_populates="estudiantes")
    sesiones = relationship("SesionConsultoria", back_populates="estudiante", cascade="all, delete-orphan")
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del estudiante."""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre or self.email
    
    def __repr__(self) -> str:
        return f"<Estudiante {self.matricula}: {self.email}>"
