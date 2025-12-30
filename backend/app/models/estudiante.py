"""
Modelo Estudiante - Usuarios del sistema
"""
from sqlalchemy import Column, String, TIMESTAMP, JSON, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid


class Estudiante(Base):
    """Modelo de Estudiante (Usuario)"""
    __tablename__ = "estudiantes"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys - Multi-tenant
    universidad_id = Column(String(36), ForeignKey("universidades.id"), nullable=False, index=True)
    carrera_id = Column(String(36), ForeignKey("carreras.id"), nullable=False, index=True)
    
    # Información Personal
    matricula = Column(String(50), nullable=False, index=True)
    # NOTA: La combinación (universidad_id + matricula) debe ser única
    
    nombre = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Autenticación
    password_hash = Column(String(255), nullable=False)
    
    # Datos Académicos (extraídos del kárdex)
    promedio = Column(Float)
    creditos_acumulados = Column(Integer, default=0)
    semestre_actual = Column(Integer)
    situacion_academica = Column(String(50))  # "Regular", "Irregular", "Baja temporal"
    
    # Historial Académico (del kárdex procesado)
    kardex_data = Column(JSON)
    # {
    #   "materias_aprobadas": ["MAT101", "PRG201", ...],
    #   "materias_reprobadas": ["BD101"],
    #   "materias_cursando": ["WEB301"],
    #   "calificaciones": {
    #     "MAT101": 95,
    #     "PRG201": 88,
    #     "BD101": 65  # reprobada
    #   }
    # }
    
    # Preferencias (para optimización de horarios)
    preferencias = Column(JSON, default={})
    # {
    #   "horario_preferido": "matutino",  # "matutino", "vespertino", "mixto"
    #   "dias_preferidos": ["lunes", "miercoles", "viernes"],
    #   "creditos_deseados": 18,
    #   "evitar_profesores": []
    # }
    
    # Estado
    activo = Column(Boolean, default=True, nullable=False)
    email_verificado = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    ultimo_acceso = Column(TIMESTAMP)
    
    # Relaciones
    # universidad = relationship("Universidad", back_populates="estudiantes")
    # carrera = relationship("Carrera", back_populates="estudiantes")
    # sesiones = relationship("SesionConsultoria", back_populates="estudiante")
    
    def __repr__(self):
        return f"<Estudiante(id={self.id}, matricula={self.matricula}, nombre={self.nombre})>"
