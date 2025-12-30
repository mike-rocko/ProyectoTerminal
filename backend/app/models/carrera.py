"""
Modelo Carrera - Programas académicos de cada universidad
"""
from sqlalchemy import Column, String, TIMESTAMP, JSON, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid


class Carrera(Base):
    """Modelo de Carrera (Programa Académico)"""
    __tablename__ = "carreras"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Key - Multi-tenant
    universidad_id = Column(String(36), ForeignKey("universidades.id"), nullable=False, index=True)
    
    # Información Básica
    nombre = Column(String(255), nullable=False)
    # Ej: "Ingeniería en Desarrollo de Software"
    
    clave = Column(String(50), nullable=False)
    # Ej: "IDS", "ISW"
    
    descripcion = Column(Text)
    duracion_semestres = Column(Integer)  # Ej: 8, 9
    creditos_totales = Column(Integer)  # Ej: 360
    
    # Mapa Curricular (Estructura completa del plan de estudios)
    mapa_curricular = Column(JSON, nullable=False)
    # Estructura:
    # {
    #   "materias": [
    #     {
    #       "clave": "MAT101",
    #       "nombre": "Cálculo Diferencial",
    #       "creditos": 6,
    #       "semestre_sugerido": 1,
    #       "tipo": "obligatoria",
    #       "prerrequisitos": [],
    #       "desbloquea": ["MAT102", "FIS101"]
    #     }
    #   ],
    #   "seriacion_estricta": true,
    #   "ciclos": ["básico", "profesionalizante", "especialización"]
    # }
    
    # Grafo de Prerrequisitos (para algoritmo rápido)
    grafo_prerrequisitos = Column(JSON)
    # Estructura optimizada para NetworkX:
    # {
    #   "nodes": ["MAT101", "MAT102", ...],
    #   "edges": [["MAT101", "MAT102"], ...]  # [prerequisito, materia]
    # }
    
    # Metadata
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relaciones
    # universidad = relationship("Universidad", back_populates="carreras")
    # estudiantes = relationship("Estudiante", back_populates="carrera")
    
    def __repr__(self):
        return f"<Carrera(id={self.id}, nombre={self.nombre}, clave={self.clave})>"
