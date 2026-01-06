"""
Agente de Tutoría Inteligente con LangGraph.

Versión mejorada que usa las tools reales (RAG, Schedule).
Compatible con langgraph 0.0.20.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from app.core.config import settings
from app.services.rag_service import RAGService
from app.services.cache_service import cache, CacheService

logger = logging.getLogger(__name__)


# ============================================
# Estado del Agente
# ============================================

class TutorState(TypedDict):
    """Estado del agente."""
    messages: List[Dict[str, str]]
    universidad_id: str
    estudiante_id: Optional[str]
    current_intent: Optional[str]
    tool_result: Optional[Dict[str, Any]]
    response: Optional[str]
    error: Optional[str]
    kardex_data: Optional[Dict[str, Any]]
    oferta_data: Optional[Dict[str, Any]]


# ============================================
# LLM
# ============================================

def get_llm(temperature: float = 0.7):
    """Obtiene instancia del LLM."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.google_api_key,
        temperature=temperature,
        max_output_tokens=1024,
        convert_system_message_to_human=True,  # Fix para SystemMessage
    )


# ============================================
# Router con keywords (sin LLM extra)
# ============================================

def router_node(state: TutorState) -> TutorState:
    """Determina el intent del usuario con keywords."""
    messages = state.get("messages", [])
    if not messages:
        state["current_intent"] = "greeting"
        return state
    
    last_message = messages[-1].get("content", "")
    last_lower = last_message.lower()
    
    # Clasificación por keywords - PRIORIZAR contenido sobre saludos
    # Primero buscar intents específicos, luego greeting
    
    schedule_keywords = ["horario", "inscribir", "materia", "kardex", "oferta", 
                         "semestre", "clase", "nrc", "creditos", "créditos"]
    info_keywords = ["fecha", "calendario", "inscripcion", "inscripción", "reglamento", 
                    "beca", "tramite", "trámite", "cuando", "donde", "dónde", "requisito", 
                    "contacto", "mision", "misión", "vision", "visión", "universidad",
                    "info", "información", "horarios de atención", "telefono", "teléfono",
                    "direccion", "dirección", "campus"]
    greeting_only = ["hola", "buenos días", "buenas tardes", "buenas noches", 
                     "hey", "hi", "saludos", "que tal", "qué tal"]
    
    # Prioridad: schedule > info > greeting > general
    if any(w in last_lower for w in schedule_keywords):
        state["current_intent"] = "schedule"
    elif any(w in last_lower for w in info_keywords):
        state["current_intent"] = "info"
    elif any(w in last_lower for w in greeting_only) and len(last_lower.split()) <= 5:
        # Solo greeting si es un mensaje corto (solo saludo)
        state["current_intent"] = "greeting"
    else:
        state["current_intent"] = "general"
    
    logger.info(f"Intent: {state['current_intent']} para: {last_message[:50]}")
    return state


# ============================================
# Nodos
# ============================================

def greeting_node(state: TutorState) -> TutorState:
    """Responde a saludos."""
    state["response"] = """¡Hola! 👋 Soy tu asistente académico.

Puedo ayudarte con:
📅 **Armar tu horario** - Sube tu kárdex y oferta
📚 **Qué materias tomar** - Recomendaciones personalizadas
❓ **Info universidad** - Fechas, trámites, becas

¿En qué te ayudo?"""
    return state


def schedule_node(state: TutorState) -> TutorState:
    """Responde sobre horarios."""
    kardex = state.get("kardex_data")
    oferta = state.get("oferta_data")
    
    if kardex and oferta:
        state["response"] = """¡Tienes tus documentos listos! 🎉

Ve a **📅 Horarios** en el menú para generar opciones optimizadas.

El sistema priorizará:
✅ Materias reprobadas
✅ Menos huecos entre clases
✅ Horarios compactos

¿Tienes preferencias? (ej: "solo mañanas", "máximo 5 materias")"""
    else:
        missing = []
        if not kardex:
            missing.append("Kárdex")
        if not oferta:
            missing.append("Oferta Académica")
        
        state["response"] = f"""Para armar tu horario necesito: **{' y '.join(missing)}**

📄 **Pasos:**
1. Ve a **📄 Documentos** en el menú
2. Sube foto o PDF de cada documento
3. Haz clic en "Analizar"
4. Regresa aquí o ve a **📅 Horarios**

💡 Puedes tomar foto con tu celular, la IA lee los datos automáticamente."""
    
    return state


def info_node(state: TutorState) -> TutorState:
    """Responde usando RAG real con caché."""
    messages = state.get("messages", [])
    last_message = messages[-1].get("content", "") if messages else ""
    universidad_id = state.get("universidad_id")
    
    # Intentar obtener del caché (respuestas RAG similares)
    cache_key = cache.key_rag_response(universidad_id, last_message)
    
    # Ejecutar caché de forma síncrona (workaround para langgraph sync)
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si ya hay un loop, usar run_coroutine_threadsafe
            import concurrent.futures
            future = asyncio.run_coroutine_threadsafe(cache.get(cache_key), loop)
            cached = future.result(timeout=2)
        else:
            cached = asyncio.run(cache.get(cache_key))
    except:
        cached = None
    
    if cached:
        logger.info(f"🎯 Cache HIT para RAG: {last_message[:30]}...")
        state["response"] = cached.get("response", "")
        state["tool_result"] = cached.get("tool_result")
        return state
    
    try:
        rag_service = RAGService()
        results = rag_service.buscar_similar(
            query=last_message,
            universidad_id=universidad_id,
            limite=3
        )
        
        if results:
            context = "\n\n".join([
                f"[{r.get('tipo', 'doc')}] {r.get('contenido', '')[:500]}"
                for r in results
            ])
            
            llm = get_llm(temperature=0.3)
            prompt = f"""Eres un asistente académico. Responde la pregunta usando SOLO esta información:

{context}

Pregunta: {last_message}

Respuesta (sé conciso y útil):"""
            
            response = llm.invoke([HumanMessage(content=prompt)])
            fuentes = [r.get('titulo', r.get('tipo')) for r in results[:2]]
            
            state["response"] = response.content
            if fuentes:
                state["response"] += f"\n\n📚 *Fuentes: {', '.join([str(f) for f in fuentes if f])}*"
            state["tool_result"] = {"sources": results}
            
            # Guardar en caché (10 minutos)
            cache_data = {
                "response": state["response"],
                "tool_result": state["tool_result"]
            }
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        cache.set(cache_key, cache_data, CacheService.TTL_MEDIUM * 2), 
                        loop
                    )
                else:
                    asyncio.run(cache.set(cache_key, cache_data, CacheService.TTL_MEDIUM * 2))
            except:
                pass  # Ignorar errores de caché
        else:
            state["response"] = """No encontré información específica sobre eso.

Puedo ayudarte con:
- 📅 Calendario académico
- 📖 Reglamentos
- 🎓 Becas y trámites

Intenta preguntar: "¿Cuándo son las inscripciones?" o "¿Requisitos para beca?"

💡 También puedes ir a **ℹ️ Info Universidad** para más consultas."""
            
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"RAG error: {e}")
        
        # Respuesta alternativa cuando hay rate limit o error de embeddings
        if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
            state["response"] = """⏳ El servicio de búsqueda está temporalmente limitado.

Mientras tanto, aquí tienes información útil de **Universidad del Caribe**:

📞 **Servicios Escolares:** (998) 881-4400 ext. 1100
📧 **Email:** servicios.escolares@ucaribe.edu.mx
🌐 **Portal:** www.unicaribe.mx
📍 **Dirección:** SM 78, Mz 1, L1, Fracc. Tabachines, Cancún, Q.Roo

📅 **Calendario 2026:**
- Inscripciones: Enero 15-22
- Inicio clases: Enero 27
- Exámenes parciales: Marzo 16-20

Intenta de nuevo en unos minutos o consulta el portal web."""
        else:
            state["response"] = """No pude buscar la información ahora. 

Consulta directamente en:
📞 Servicios Escolares: (998) 881-4400
🌐 Portal: www.unicaribe.mx"""
        state["error"] = error_msg
    
    return state


def general_node(state: TutorState) -> TutorState:
    """Responde con LLM para consultas generales."""
    messages = state.get("messages", [])
    
    try:
        llm = get_llm()
        
        # Construir historial
        history = []
        # Añadir contexto como primer mensaje
        history.append(HumanMessage(content="""Eres un asistente académico de la Universidad del Caribe.
Ayudas a estudiantes con horarios, materias e información universitaria.
Sé conciso, amable y útil. Responde en español."""))
        history.append(AIMessage(content="Entendido, soy un asistente académico listo para ayudar."))
        
        # Añadir historial reciente
        for m in messages[-5:]:
            if m["role"] == "user":
                history.append(HumanMessage(content=m["content"]))
            else:
                history.append(AIMessage(content=m["content"]))
        
        response = llm.invoke(history)
        state["response"] = response.content
        
    except Exception as e:
        logger.error(f"LLM error: {e}")
        state["response"] = """No pude procesar tu mensaje. 

¿Podrías reformularlo? O intenta una de estas opciones:
- "Quiero armar mi horario"
- "¿Cuándo son las inscripciones?"
- "¿Qué materias me recomiendas?" """
        state["error"] = str(e)
    
    return state


def finalize_node(state: TutorState) -> TutorState:
    """Finaliza respuesta."""
    if not state.get("response"):
        state["response"] = "¿En qué te puedo ayudar hoy?"
    return state


# ============================================
# Grafo
# ============================================

def create_tutor_graph() -> StateGraph:
    """Crea el grafo del agente."""
    workflow = StateGraph(TutorState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("schedule", schedule_node)
    workflow.add_node("info", info_node)
    workflow.add_node("general", general_node)
    workflow.add_node("finalize", finalize_node)
    
    def route_by_intent(state: TutorState) -> str:
        return state.get("current_intent", "general")
    
    workflow.set_entry_point("router")
    workflow.add_conditional_edges("router", route_by_intent, {
        "greeting": "greeting",
        "schedule": "schedule",
        "info": "info",
        "general": "general",
    })
    
    workflow.add_edge("greeting", "finalize")
    workflow.add_edge("schedule", "finalize")
    workflow.add_edge("info", "finalize")
    workflow.add_edge("general", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# ============================================
# Clase Wrapper
# ============================================

class TutorAgent:
    """Agente de tutoría con tools reales."""
    
    def __init__(self, universidad_id: str, estudiante_id: Optional[str] = None):
        self.universidad_id = universidad_id
        self.estudiante_id = estudiante_id
        self.graph = create_tutor_graph()
        self.history: List[Dict[str, str]] = []
        self.kardex_data: Optional[Dict] = None
        self.oferta_data: Optional[Dict] = None
    
    def set_context(self, kardex_data: Optional[Dict] = None, oferta_data: Optional[Dict] = None):
        """Establece contexto de documentos."""
        if kardex_data:
            self.kardex_data = kardex_data
        if oferta_data:
            self.oferta_data = oferta_data
    
    async def chat(self, message: str) -> Dict[str, Any]:
        """Procesa mensaje."""
        self.history.append({"role": "user", "content": message})
        
        state: TutorState = {
            "messages": self.history.copy(),
            "universidad_id": self.universidad_id,
            "estudiante_id": self.estudiante_id,
            "current_intent": None,
            "tool_result": None,
            "response": None,
            "error": None,
            "kardex_data": self.kardex_data,
            "oferta_data": self.oferta_data,
        }
        
        try:
            result = self.graph.invoke(state)
            response_text = result.get("response", "No pude procesar tu mensaje.")
            self.history.append({"role": "assistant", "content": response_text})
            
            return {
                "success": True,
                "response": response_text,
                "intent": result.get("current_intent"),
                "tool_result": result.get("tool_result"),
            }
        except Exception as e:
            logger.exception(f"Agent error: {e}")
            return {"success": False, "response": f"Error: {str(e)[:100]}", "error": str(e)}
    
    def clear_history(self):
        self.history = []


_agents: Dict[str, TutorAgent] = {}


def get_agent(universidad_id: str, estudiante_id: Optional[str] = None) -> TutorAgent:
    """Obtiene agente."""
    key = f"{universidad_id}:{estudiante_id or 'anon'}"
    if key not in _agents:
        _agents[key] = TutorAgent(universidad_id, estudiante_id)
    return _agents[key]


def clear_agent(universidad_id: str, estudiante_id: Optional[str] = None):
    """Elimina agente del cache."""
    key = f"{universidad_id}:{estudiante_id or 'anon'}"
    if key in _agents:
        del _agents[key]
