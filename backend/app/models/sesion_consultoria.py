"""
Modelo Sesión de Consultoría - Historial de interacciones del agente
"""
from sqlalchemy import Column, String, TIMESTAMP, JSON, Enum, Integer, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base
import enum
import uuid


class TipoConsultoria(str, enum.Enum):
    """Tipos de consultoría que ofrece el sistema"""
    HORARIO = "horario"  # Armar horario completo
    MATERIAS = "materias"  # Qué materias tomar
    COMBINADO = "combinado"  # Ambos
    CHAT = "chat"  # Consulta general (RAG)


class EstadoSesion(str, enum.Enum):
    """Estados de la sesión"""
    PROCESANDO = "procesando"
    COMPLETADA = "completada"
    ERROR = "error"
    CANCELADA = "cancelada"


class SesionConsultoria(Base):
    """Modelo de Sesión de Consultoría"""
    __tablename__ = "sesiones_consultoria"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign Keys
    estudiante_id = Column(String(36), ForeignKey("estudiantes.id"), nullable=False, index=True)
    universidad_id = Column(String(36), ForeignKey("universidades.id"), nullable=False, index=True)
    
    # Tipo y Estado
    tipo = Column(Enum(TipoConsultoria), nullable=False)
    estado = Column(Enum(EstadoSesion), default=EstadoSesion.PROCESANDO, nullable=False)
    
    # Input del Usuario (documentos subidos)
    img_oferta_url = Column(String(500))  # URL en GCS
    img_mapa_url = Column(String(500))
    img_kardex_url = Column(String(500))
    
    # Datos Extraídos (por Vision AI)
    oferta_data = Column(JSON)  # Oferta académica procesada
    mapa_data = Column(JSON)    # Mapa curricular procesado
    kardex_data = Column(JSON)   # Kárdex procesado
    
    # Input del Usuario (preferencias)
    disponibilidad = Column(JSON)  # {"lunes": ["9-11", "14-16"], ...}
    creditos_deseados = Column(Integer)
    
    # Output del Sistema (recomendación)
    horario_recomendado = Column(JSON)
    # {
    #   "opcion_1": {
    #     "materias": [...],
    #     "score": 0.95,
    #     "creditos": 18,
    #     "huecos": 0
    #   },
    #   "opcion_2": {...},
    #   "opcion_3": {...}
    # }
    
    materias_sugeridas = Column(JSON)  # Lista priorizada de materias
    explicacion = Column(Text)  # Explicación en lenguaje natural
    
    # Feedback del Usuario
    satisfaccion = Column(Integer)  # 1-5 estrellas
    comentarios = Column(Text)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    completed_at = Column(TIMESTAMP)
    duracion_segundos = Column(Integer)  # Para métricas
    
    # Relaciones
    # estudiante = relationship("Estudiante", back_populates="sesiones")
    # universidad = relationship("Universidad")
    
    def __repr__(self):
        return f"<SesionConsultoria(id={self.id}, tipo={self.tipo}, estado={self.estado})>"
