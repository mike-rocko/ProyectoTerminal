"""
Modelo Carrera - Plan de estudios de una universidad.
Contiene el mapa curricular con materias y prerrequisitos.
"""
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class Carrera(Base):
    """
    Representa una carrera/programa académico.
    
    Contiene:
    - Información básica (nombre, clave)
    - Plan de estudios completo en JSONB
    - Relación con universidad (multi-tenant)
    """
    
    # Relación con universidad (multi-tenant)
    universidad_id = Column(
        UUID(as_uuid=True),
        ForeignKey("universidads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Información básica
    nombre = Column(String(255), nullable=False)
    # Ejemplo: "Ingeniería en Software"
    
    clave = Column(String(50), nullable=False)
    # Ejemplo: "ISW", "LIA", "LCC"
    
    descripcion = Column(Text, nullable=True)
    
    total_creditos = Column(String(10), nullable=True)
    # Ejemplo: "300"
    
    duracion_semestres = Column(String(10), nullable=True)
    # Ejemplo: "9"
    
    # Plan de estudios completo (mapa curricular)
    # Estructura esperada:
    # {
    #   "semestres": [
    #     {
    #       "numero": 1,
    #       "materias": [
    #         {
    #           "clave": "MAT101",
    #           "nombre": "Cálculo I",
    #           "creditos": 8,
    #           "prerrequisitos": [],
    #           "tipo": "obligatoria"
    #         }
    #       ]
    #     }
    #   ]
    # }
    plan_estudios = Column(JSONB, default={}, nullable=False)
    
    # Relaciones
    universidad = relationship("Universidad", back_populates="carreras")
    estudiantes = relationship("Estudiante", back_populates="carrera")
    
    def __repr__(self) -> str:
        return f"<Carrera {self.clave}: {self.nombre}>"
