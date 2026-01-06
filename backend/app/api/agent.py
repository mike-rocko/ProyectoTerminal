"""
Endpoints para el Agente de Tutoría Inteligente.

POST /api/v1/agent/chat - Enviar mensaje al agente
POST /api/v1/agent/upload - Subir documento para análisis
GET /api/v1/agent/state - Obtener estado de la sesión
POST /api/v1/agent/reset - Reiniciar conversación
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.agents.tutor_agent import TutorAgent, get_agent
from app.services.vision_service import get_vision_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["Agent"])


# ============================================
# Schemas
# ============================================

class ChatRequest(BaseModel):
    """Request para enviar mensaje al agente."""
    universidad_id: str = Field(..., description="UUID de la universidad")
    estudiante_id: Optional[str] = Field(None, description="UUID del estudiante")
    message: str = Field(..., min_length=1, max_length=2000, description="Mensaje del usuario")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "universidad_id": "11111111-1111-1111-1111-111111111111",
                "message": "Hola, quiero armar mi horario para el próximo semestre"
            }
        }
    }


class ChatResponse(BaseModel):
    """Response del agente."""
    success: bool
    response: str = Field(..., description="Respuesta del agente")
    intent: Optional[str] = Field(None, description="Intent detectado")
    pending_info: List[str] = Field(default=[], description="Información pendiente")
    tools_used: List[str] = Field(default=[], description="Tools ejecutados")


class UploadDocumentRequest(BaseModel):
    """Metadata para upload de documento."""
    universidad_id: str
    estudiante_id: Optional[str] = None
    doc_type: str = Field(..., description="Tipo: oferta, kardex, mapa")


class StateResponse(BaseModel):
    """Estado actual de la sesión."""
    universidad_id: str
    estudiante_id: Optional[str]
    has_oferta: bool
    has_kardex: bool
    has_mapa: bool
    has_disponibilidad: bool
    has_horarios: bool
    message_count: int
    tools_called: List[str]


# ============================================
# Endpoints
# ============================================

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Enviar mensaje al agente",
    description="""
    Envía un mensaje al Tutor IA y recibe una respuesta.
    
    El agente puede:
    - Responder preguntas sobre la universidad (RAG)
    - Ayudar a armar horarios (si tiene los documentos)
    - Solicitar información faltante
    - Mantener conversación contextual
    """
)
async def chat(request: ChatRequest) -> ChatResponse:
    """Procesa un mensaje del usuario."""
    
    try:
        logger.info(f"Chat request: {request.message[:50]}...")
        
        # Obtener o crear agente
        agent = get_agent(
            universidad_id=request.universidad_id,
            estudiante_id=request.estudiante_id
        )
        
        # Procesar mensaje (async)
        result = await agent.chat(request.message)
        
        return ChatResponse(
            success=result.get("success", False),
            response=result.get("response", ""),
            intent=result.get("intent"),
            pending_info=[],
            tools_used=[]
        )
        
    except Exception as e:
        logger.exception(f"Error en chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando mensaje: {str(e)}"
        )


@router.post(
    "/upload",
    response_model=ChatResponse,
    summary="Subir documento y analizarlo",
    description="""
    Sube un documento (oferta, kárdex, mapa) para que el agente lo analice.
    
    El documento se procesa con Vision AI y los datos extraídos
    se almacenan en la sesión del agente.
    """
)
async def upload_document(
    file: UploadFile = File(...),
    universidad_id: str = Form(...),
    estudiante_id: Optional[str] = Form(None),
    doc_type: str = Form(..., description="oferta, kardex, mapa")
) -> ChatResponse:
    """Sube y analiza un documento."""
    
    try:
        logger.info(f"Upload: {doc_type} from {file.filename}")
        
        # Validar tipo
        valid_types = ["oferta", "kardex", "mapa"]
        if doc_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo inválido. Debe ser uno de: {valid_types}"
            )
        
        # Validar archivo
        if not file.content_type or not file.content_type.startswith(("image/", "application/pdf")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen o PDF"
            )
        
        # Leer archivo
        content = await file.read()
        
        # Guardar temporalmente
        import tempfile
        import os
        
        suffix = ".pdf" if "pdf" in file.content_type else ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Analizar con Vision
            vision_service = get_vision_service()
            result = await vision_service.analyze_document(tmp_path, doc_type)
            
            # Obtener agente
            agent = get_agent(universidad_id, estudiante_id)
            
            # Guardar datos en el estado
            if result.get("success"):
                data = result.get("data", {})
                
                if doc_type == "oferta":
                    agent.set_oferta_data(data)
                    response_text = f"✅ ¡Oferta académica analizada! Encontré {len(data.get('materias', []))} materias."
                elif doc_type == "kardex":
                    agent.set_kardex_data(data)
                    response_text = f"✅ ¡Kárdex analizado! Veo que llevas {data.get('creditos_cursados', 'N/A')} créditos."
                elif doc_type == "mapa":
                    agent.state["mapa_data"] = data
                    response_text = "✅ ¡Mapa curricular analizado!"
                
                # Agregar siguiente paso
                state = agent.get_state()
                if not state.get("oferta_data"):
                    response_text += "\n\n📄 Ahora necesito tu **oferta académica**."
                elif not state.get("kardex_data"):
                    response_text += "\n\n📊 Ahora necesito tu **kárdex**."
                elif not state.get("disponibilidad"):
                    response_text += "\n\n🕐 ¿Cuáles son tus **horarios disponibles**?"
                else:
                    response_text += "\n\n🎓 ¡Tengo todo! ¿Quieres que genere opciones de horario?"
                
            else:
                response_text = f"⚠️ No pude analizar el documento: {result.get('error', 'Error desconocido')}"
            
            return ChatResponse(
                success=result.get("success", False),
                response=response_text,
                intent="cargar_documento",
                pending_info=[],
                tools_used=["vision"]
            )
            
        finally:
            # Limpiar archivo temporal
            os.unlink(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error en upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando documento: {str(e)}"
        )


@router.get(
    "/state",
    response_model=StateResponse,
    summary="Obtener estado de la sesión",
    description="Retorna el estado actual del agente para una sesión."
)
async def get_state(
    universidad_id: str,
    estudiante_id: Optional[str] = None
) -> StateResponse:
    """Obtiene el estado de la sesión."""
    
    try:
        agent = get_agent(universidad_id, estudiante_id)
        state = agent.get_state()
        
        return StateResponse(
            universidad_id=universidad_id,
            estudiante_id=estudiante_id,
            has_oferta=bool(state.get("oferta_data")),
            has_kardex=bool(state.get("kardex_data")),
            has_mapa=bool(state.get("mapa_data")),
            has_disponibilidad=bool(state.get("disponibilidad")),
            has_horarios=bool(state.get("horarios_generados")),
            message_count=len(state.get("messages", [])),
            tools_called=state.get("tools_called", [])
        )
        
    except Exception as e:
        logger.exception(f"Error obteniendo estado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.post(
    "/reset",
    summary="Reiniciar conversación",
    description="Reinicia el estado del agente, borrando todos los datos de la sesión."
)
async def reset_session(
    universidad_id: str,
    estudiante_id: Optional[str] = None
):
    """Reinicia la sesión del agente."""
    
    try:
        agent = get_agent(universidad_id, estudiante_id)
        agent.reset()
        
        return {
            "success": True,
            "message": "Sesión reiniciada. ¡Hola! ¿En qué puedo ayudarte hoy? 😊"
        }
        
    except Exception as e:
        logger.exception(f"Error reiniciando: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.post(
    "/set-disponibilidad",
    response_model=ChatResponse,
    summary="Establecer disponibilidad",
    description="Establece los horarios disponibles del estudiante."
)
async def set_disponibilidad(
    universidad_id: str,
    estudiante_id: Optional[str] = None,
    disponibilidad: Dict[str, Any] = None
) -> ChatResponse:
    """Establece la disponibilidad del estudiante."""
    
    try:
        agent = get_agent(universidad_id, estudiante_id)
        
        if disponibilidad:
            agent.set_disponibilidad(disponibilidad)
            response = "✅ ¡Disponibilidad registrada!"
            
            # Verificar si podemos generar horarios
            state = agent.get_state()
            if state.get("oferta_data") and state.get("kardex_data"):
                response += "\n\n🎓 ¡Tengo todo lo necesario! ¿Quieres que genere opciones de horario?"
            elif not state.get("oferta_data"):
                response += "\n\n📄 Aún necesito tu **oferta académica**."
            elif not state.get("kardex_data"):
                response += "\n\n📊 Aún necesito tu **kárdex**."
        else:
            response = "⚠️ No recibí datos de disponibilidad."
        
        return ChatResponse(
            success=True,
            response=response,
            intent="especificar_disponibilidad",
            pending_info=[],
            tools_used=[]
        )
        
    except Exception as e:
        logger.exception(f"Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
