"""
Cliente API para comunicarse con el backend FastAPI.
"""
import requests
from typing import Any, Dict, List, Optional
from config import API_URL


class APIClient:
    """Cliente HTTP para el backend."""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """Establece el token JWT."""
        self.token = token
    
    def _headers(self) -> Dict[str, str]:
        """Headers para las requests."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Realiza una request HTTP."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if files:
                # Multipart form data
                headers = {}
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"
                response = requests.request(
                    method, url, data=data, files=files, headers=headers, timeout=120
                )
            else:
                response = requests.request(
                    method, url, json=data, headers=self._headers(), timeout=60
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            return {"error": "Timeout: La solicitud tardó demasiado"}
        except requests.exceptions.ConnectionError:
            return {"error": "Error de conexión: No se puede conectar al servidor"}
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            return {"error": error_detail}
        except Exception as e:
            return {"error": str(e)}
    
    # ========== Auth ==========
    
    def register(self, email: str, password: str, matricula: str, universidad_id: str) -> Dict:
        """Registra un nuevo estudiante."""
        return self._request("POST", "/api/v1/auth/register", {
            "email": email,
            "password": password,
            "matricula": matricula,
            "universidad_id": universidad_id
        })
    
    def login(self, email: str, password: str) -> Dict:
        """Inicia sesión y obtiene token JWT."""
        return self._request("POST", "/api/v1/auth/login", {
            "email": email,
            "password": password
        })
    
    def get_me(self) -> Dict:
        """Obtiene info del usuario actual."""
        return self._request("GET", "/api/v1/auth/me")
    
    # ========== Agent ==========
    
    def chat(self, message: str, universidad_id: str, estudiante_id: Optional[str] = None) -> Dict:
        """Envía mensaje al agente."""
        return self._request("POST", "/api/v1/agent/chat", {
            "message": message,
            "universidad_id": universidad_id,
            "estudiante_id": estudiante_id
        })
    
    # ========== Vision ==========
    
    def analyze_document(
        self,
        file_bytes: bytes,
        filename: str,
        doc_type: str,
        universidad_id: str
    ) -> Dict:
        """Analiza un documento con Vision API."""
        files = {"file": (filename, file_bytes)}
        data = {
            "doc_type": doc_type,
            "universidad_id": universidad_id
        }
        return self._request("POST", "/api/v1/vision/analyze", data=data, files=files)
    
    # ========== Schedule ==========
    
    def generate_schedule(self, materias_elegibles: List[Dict], **kwargs) -> Dict:
        """Genera horarios optimizados."""
        return self._request("POST", "/api/v1/schedule/generate", {
            "materias_elegibles": materias_elegibles,
            **kwargs
        })
    
    def generate_schedule_test(self) -> Dict:
        """Genera horarios con datos de prueba."""
        return self._request("POST", "/api/v1/schedule/generate-test")
    
    def generate_from_vision(
        self, 
        kardex_data: Dict, 
        oferta_data: Dict,
        mapa_data: Optional[Dict] = None,
        disponibilidad: Optional[Dict] = None,
        conflictos: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict:
        """
        Flujo completo: genera horarios a partir de datos de Vision.
        
        Args:
            kardex_data: JSON extraído del kárdex
            oferta_data: JSON extraído de la oferta académica
            mapa_data: JSON del mapa curricular (opcional)
            disponibilidad: Dict con disponibilidad por día
            conflictos: Lista de bloques donde NO puede asistir
        """
        return self._request("POST", "/api/v1/schedule/from-vision", {
            "kardex_data": kardex_data,
            "oferta_data": oferta_data,
            "mapa_data": mapa_data,
            "disponibilidad": disponibilidad,
            "conflictos": conflictos,
            **kwargs
        })
    
    def extract_bloques(self, oferta_data: Dict) -> Dict:
        """
        Extrae bloques horarios únicos de la oferta.
        
        Args:
            oferta_data: JSON extraído de la oferta académica
            
        Returns:
            Lista de bloques únicos con días y horas
        """
        return self._request("POST", "/api/v1/schedule/extract-bloques", {
            "oferta_data": oferta_data
        })
    
    # ========== RAG ==========
    
    def ask_rag(self, query: str, universidad_id: str) -> Dict:
        """Pregunta al sistema RAG."""
        return self._request("POST", "/api/v1/rag/ask", {
            "query": query,
            "universidad_id": universidad_id
        })
    
    # ========== Health ==========
    
    def health_check(self) -> Dict:
        """Verifica estado del backend."""
        return self._request("GET", "/health")


# Instancia global
api = APIClient()
