"""
Endpoints para RAG (Retrieval Augmented Generation).

POST /api/v1/rag/ingest - Ingestar documento
POST /api/v1/rag/query - Buscar información
POST /api/v1/rag/ask - Generar respuesta con LLM
DELETE /api/v1/rag/documents - Eliminar documentos
GET /api/v1/rag/stats/{universidad_id} - Estadísticas
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.rag import (
    DocumentoIngestRequest,
    DocumentoIngestResponse,
    DocumentoDeleteRequest,
    DocumentoDeleteResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGAnswerRequest,
    RAGAnswerResponse,
)
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post(
    "/ingest",
    response_model=DocumentoIngestResponse,
    summary="Ingestar documento",
    description="""
    Ingesta un documento de la universidad para búsqueda RAG.
    
    El documento se divide automáticamente en chunks con embeddings
    vectoriales para búsqueda semántica.
    
    Tipos válidos: mision, vision, reglamento, calendario, tramite, 
    contacto, faq, carrera, servicio, beca, otro
    """
)
async def ingest_document(
    request: DocumentoIngestRequest,
    db: AsyncSession = Depends(get_db)
) -> DocumentoIngestResponse:
    """Ingesta un documento dividiéndolo en chunks."""
    
    try:
        logger.info(f"Ingestando documento: {request.titulo} ({request.tipo})")
        
        service = get_rag_service()
        response = await service.ingest_document(db, request)
        
        logger.info(f"Documento ingestado: {response.chunks_creados} chunks")
        
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception(f"Error ingestando documento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando documento: {str(e)}"
        )


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    summary="Buscar información",
    description="""
    Realiza búsqueda semántica en los documentos de la universidad.
    
    Retorna los chunks más relevantes ordenados por similitud.
    Útil para obtener contexto sin generar respuesta.
    """
)
async def query_documents(
    request: RAGQueryRequest,
    db: AsyncSession = Depends(get_db)
) -> RAGQueryResponse:
    """Búsqueda semántica en documentos."""
    
    try:
        logger.info(f"Query RAG: {request.query[:50]}...")
        
        service = get_rag_service()
        response = await service.search_similar(db, request)
        
        logger.info(f"Encontrados: {response.total_encontrados} resultados")
        
        return response
        
    except Exception as e:
        logger.exception(f"Error en búsqueda: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )


@router.post(
    "/ask",
    response_model=RAGAnswerResponse,
    summary="Preguntar con respuesta generada",
    description="""
    Genera una respuesta a la pregunta del usuario usando RAG.
    
    1. Busca documentos relevantes
    2. Usa el contexto para generar respuesta con LLM
    3. Incluye fuentes citadas
    
    Ideal para el agente y chat directo.
    """
)
async def ask_question(
    request: RAGAnswerRequest,
    db: AsyncSession = Depends(get_db)
) -> RAGAnswerResponse:
    """Genera respuesta usando RAG + LLM."""
    
    try:
        logger.info(f"Pregunta RAG: {request.query[:50]}...")
        
        service = get_rag_service()
        response = await service.generate_answer(db, request)
        
        logger.info(f"Respuesta generada, confianza: {response.confianza:.2f}")
        
        return response
        
    except Exception as e:
        logger.exception(f"Error generando respuesta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando respuesta: {str(e)}"
        )


@router.delete(
    "/documents",
    response_model=DocumentoDeleteResponse,
    summary="Eliminar documentos",
    description="Elimina documentos de una universidad. Puede filtrar por tipo y/o título."
)
async def delete_documents(
    request: DocumentoDeleteRequest,
    db: AsyncSession = Depends(get_db)
) -> DocumentoDeleteResponse:
    """Elimina documentos."""
    
    try:
        logger.info(f"Eliminando documentos de universidad {request.universidad_id}")
        
        service = get_rag_service()
        count = await service.delete_documents(
            db,
            universidad_id=request.universidad_id,
            tipo=request.tipo,
            titulo=request.titulo
        )
        
        logger.info(f"Eliminados: {count} chunks")
        
        return DocumentoDeleteResponse(
            success=True,
            chunks_eliminados=count
        )
        
    except Exception as e:
        logger.exception(f"Error eliminando: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando documentos: {str(e)}"
        )


@router.get(
    "/stats/{universidad_id}",
    summary="Estadísticas de documentos",
    description="Obtiene estadísticas de documentos indexados por universidad."
)
async def get_stats(
    universidad_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene estadísticas de documentos."""
    
    try:
        service = get_rag_service()
        stats = await service.get_stats(db, universidad_id)
        
        return {
            "success": True,
            "universidad_id": str(universidad_id),
            **stats
        }
        
    except Exception as e:
        logger.exception(f"Error obteniendo stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.post(
    "/ingest-test",
    response_model=DocumentoIngestResponse,
    summary="Ingestar datos de prueba",
    description="Ingesta documentos de ejemplo para testing"
)
async def ingest_test_data(
    universidad_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> DocumentoIngestResponse:
    """Ingesta datos de prueba para una universidad."""
    
    # Documentos de ejemplo de UniCaribe
    test_documents = [
        {
            "tipo": "calendario",
            "titulo": "Calendario Académico 2025-1",
            "contenido": """
            CALENDARIO ACADÉMICO SEMESTRE 2025-1
            
            Inscripciones Ordinarias: 6 al 10 de enero de 2025
            Inscripciones Extemporáneas: 13 al 17 de enero de 2025
            Inicio de Clases: 20 de enero de 2025
            
            Primer Parcial: 17 al 21 de febrero de 2025
            Segundo Parcial: 17 al 21 de marzo de 2025
            
            Semana Santa (vacaciones): 14 al 21 de abril de 2025
            
            Tercer Parcial: 21 al 25 de abril de 2025
            Exámenes Finales: 12 al 16 de mayo de 2025
            Exámenes Extraordinarios: 19 al 23 de mayo de 2025
            
            Fin del Semestre: 23 de mayo de 2025
            
            Periodo de Verano: 2 de junio al 25 de julio de 2025
            """
        },
        {
            "tipo": "reglamento",
            "titulo": "Reglamento de Inscripciones",
            "contenido": """
            REGLAMENTO DE INSCRIPCIONES
            
            Artículo 15. Los estudiantes pueden inscribir un mínimo de 3 materias 
            y un máximo de 6 materias por semestre regular, equivalente a un 
            mínimo de 12 créditos y máximo de 24 créditos.
            
            Artículo 16. Los estudiantes con promedio igual o superior a 9.0 
            pueden solicitar autorización para inscribir hasta 7 materias 
            (máximo 28 créditos) mediante solicitud en Servicios Escolares.
            
            Artículo 17. Para inscribir una materia, el estudiante debe haber 
            aprobado todas las materias prerrequisito establecidas en el plan 
            de estudios.
            
            Artículo 18. Las materias reprobadas tienen prioridad de inscripción 
            y deben ser re-cursadas en la primera oportunidad disponible.
            
            Artículo 20. Las bajas de materias se permiten hasta la tercera 
            semana del semestre sin afectar el kárdex. Después de esa fecha, 
            la baja se registra como NP (No Presentó).
            """
        },
        {
            "tipo": "contacto",
            "titulo": "Información de Contacto",
            "contenido": """
            CONTACTOS IMPORTANTES
            
            Servicios Escolares:
            - Teléfono: (998) 881-4400 ext. 1100
            - Email: servicios.escolares@unicaribe.edu.mx
            - Horario: Lunes a Viernes 9:00 - 17:00
            - Ubicación: Edificio A, Planta Baja
            
            Tutorías y Asesorías:
            - Teléfono: (998) 881-4400 ext. 1200
            - Email: tutorias@unicaribe.edu.mx
            
            Becas y Financiamiento:
            - Teléfono: (998) 881-4400 ext. 1300
            - Email: becas@unicaribe.edu.mx
            
            Centro de Cómputo:
            - Teléfono: (998) 881-4400 ext. 1400
            - Horario: Lunes a Sábado 7:00 - 21:00
            """
        },
        {
            "tipo": "beca",
            "titulo": "Programa de Becas 2025",
            "contenido": """
            PROGRAMA DE BECAS 2025
            
            Beca de Excelencia Académica:
            - Requisitos: Promedio mínimo de 9.5, sin materias reprobadas
            - Beneficio: 50% de descuento en colegiatura
            - Renovable cada semestre si se mantiene el promedio
            
            Beca Socioeconómica:
            - Requisitos: Estudio socioeconómico, promedio mínimo 8.0
            - Beneficio: 25% a 75% según evaluación
            - Documentos: INE, comprobante de domicilio, carta de ingresos
            
            Beca Deportiva:
            - Requisitos: Pertenecer a equipo representativo, promedio 8.0
            - Beneficio: Hasta 40% de descuento
            
            Beca de Servicio Social:
            - Requisitos: Cumplir 480 horas de servicio social
            - Beneficio: 30% en último semestre
            
            FECHAS DE SOLICITUD:
            - Primera convocatoria: 15 de enero al 15 de febrero
            - Segunda convocatoria: 15 de agosto al 15 de septiembre
            """
        },
        {
            "tipo": "mision",
            "titulo": "Misión y Visión",
            "contenido": """
            MISIÓN
            
            La Universidad del Caribe es una institución pública de educación 
            superior comprometida con la formación integral de profesionales 
            competentes, con valores éticos y responsabilidad social, capaces 
            de contribuir al desarrollo sustentable de la región y el país.
            
            VISIÓN 2030
            
            Ser una universidad de excelencia reconocida nacional e 
            internacionalmente por la calidad de sus programas educativos, 
            la investigación de impacto y la vinculación efectiva con los 
            sectores productivos y sociales.
            
            VALORES
            - Excelencia académica
            - Integridad y ética
            - Responsabilidad social
            - Innovación y creatividad
            - Respeto a la diversidad
            - Sustentabilidad ambiental
            """
        }
    ]
    
    try:
        service = get_rag_service()
        total_chunks = 0
        all_chunks = []
        
        for doc in test_documents:
            request = DocumentoIngestRequest(
                universidad_id=universidad_id,
                tipo=doc["tipo"],
                titulo=doc["titulo"],
                contenido=doc["contenido"],
                metadata={"source": "test_data"},
                chunk_size=400,
                chunk_overlap=50
            )
            
            response = await service.ingest_document(db, request)
            total_chunks += response.chunks_creados
            all_chunks.extend(response.chunks)
        
        return DocumentoIngestResponse(
            success=True,
            mensaje=f"Ingestados {len(test_documents)} documentos de prueba",
            chunks_creados=total_chunks,
            chunks=all_chunks[:10],  # Solo mostrar primeros 10
            tiempo_procesamiento_ms=0
        )
        
    except Exception as e:
        logger.exception(f"Error en ingest-test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
