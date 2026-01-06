"""
Modelo SesionConsultoria - Registro de cada consulta del estudiante.
Almacena documentos subidos, datos extraídos y recomendaciones.
"""
from sqlalchemy import Column, String, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class TipoConsultoria(str, enum.Enum):
    """Tipos de consultoría disponibles."""
    HORARIO = "horario"           # Armar horario completo
    MATERIAS = "materias"         # Solo qué materias tomar
    COMBINADO = "combinado"       # Ambos
    CHAT = "chat"                 # Solo preguntas RAG


class EstadoSesion(str, enum.Enum):
    """Estados posibles de una sesión."""
    INICIADA = "iniciada"         # Recién creada
    DOCUMENTOS = "documentos"     # Documentos subidos
    PROCESANDO = "procesando"     # Agente trabajando
    COMPLETADA = "completada"     # Recomendación lista
    ERROR = "error"               # Hubo un error


class SesionConsultoria(Base):
    """
    Representa una sesión de consultoría con el agente IA.
    
    Flujo:
    1. Estudiante inicia sesión (tipo: horario/materias/combinado)
    2. Sube documentos (oferta, kardex, mapa opcional)
    3. Especifica disponibilidad
    4. Agente procesa y genera recomendación
    5. Estudiante recibe resultado
    """
    
    # Relación con estudiante
    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("estudiantes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Tipo y estado
    tipo = Column(
        Enum(TipoConsultoria),
        default=TipoConsultoria.COMBINADO,
        nullable=False
    )
    
    estado = Column(
        Enum(EstadoSesion),
        default=EstadoSesion.INICIADA,
        nullable=False
    )
    
    # URLs de imágenes subidas (Google Cloud Storage)
    img_oferta_url = Column(String(500), nullable=True)
    img_mapa_url = Column(String(500), nullable=True)
    img_kardex_url = Column(String(500), nullable=True)
    
    # Datos extraídos por Vision AI
    # Estructura oferta_data:
    # {
    #   "semestre": "2026-1",
    #   "materias": [
    #     {"nrc": "12345", "nombre": "Cálculo I", "creditos": 8, "horario": {...}}
    #   ]
    # }
    oferta_data = Column(JSONB, default=None, nullable=True)
    
    # Estructura mapa_data:
    # {
    #   "semestres": [...],
    #   "materias_con_prerrequisitos": [...]
    # }
    mapa_data = Column(JSONB, default=None, nullable=True)
    
    # Estructura kardex_data:
    # {
    #   "materias_aprobadas": [...],
    #   "materias_reprobadas": [...],
    #   "promedio": 8.5
    # }
    kardex_data = Column(JSONB, default=None, nullable=True)
    
    # Disponibilidad del estudiante para esta sesión
    # Estructura:
    # {
    #   "lunes": ["09:00-11:00", "14:00-18:00"],
    #   "martes": ["09:00-15:00"],
    #   ...
    # }
    disponibilidad = Column(JSONB, default=None, nullable=True)
    
    # Resultado de la consultoría
    # Estructura recomendacion:
    # {
    #   "horarios": [
    #     {
    #       "ranking": 1,
    #       "materias": [...],
    #       "metricas": {"huecos": 0, "amplitud": "9-15"}
    #     }
    #   ]
    # }
    recomendacion = Column(JSONB, default=None, nullable=True)
    
    # Explicación en lenguaje natural del agente
    explicacion = Column(Text, nullable=True)
    
    # Feedback del estudiante (1-5 estrellas)
    calificacion = Column(String(1), nullable=True)
    comentario_feedback = Column(Text, nullable=True)
    
    # Relaciones
    estudiante = relationship("Estudiante", back_populates="sesiones")
    
    def __repr__(self) -> str:
        return f"<SesionConsultoria {self.id} ({self.tipo.value}: {self.estado.value})>"
