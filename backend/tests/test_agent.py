"""
Tests for the agent chat endpoint.
"""
import pytest


class TestAgentChat:
    """Tests for /agent/chat endpoint."""
    
    def test_chat_greeting(self, client, universidad_id):
        """Test greeting intent detection."""
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "universidad_id": universidad_id,
                "message": "Hola, buenos días"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "intent" in data
        assert "response" in data
        assert data["intent"] == "greeting"
        # Should greet back
        assert any(word in data["response"].lower() for word in ["hola", "bienvenido", "asistente"])
    
    def test_chat_schedule_intent(self, client, universidad_id):
        """Test schedule intent detection."""
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "universidad_id": universidad_id,
                "message": "Quiero armar mi horario del próximo semestre"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] == "schedule"
        # Should mention uploading documents
        assert any(word in data["response"].lower() for word in ["kardex", "oferta", "documento"])
    
    def test_chat_info_intent(self, client, universidad_id):
        """Test info/RAG intent detection."""
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "universidad_id": universidad_id,
                "message": "¿Cuándo son las inscripciones?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] == "info"
    
    def test_chat_general_intent(self, client, universidad_id):
        """Test general/off-topic intent detection."""
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "universidad_id": universidad_id,
                "message": "¿Cuál es la capital de Francia?"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["intent"] == "general"
        # Should redirect to academic topics
        assert any(word in data["response"].lower() for word in ["universidad", "académico", "ayudar"])
    
    def test_chat_empty_message(self, client, universidad_id):
        """Test with empty message."""
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "universidad_id": universidad_id,
                "message": ""
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_chat_with_context(self, client, universidad_id):
        """Test chat with kardex/oferta context."""
        response = client.post(
            "/api/v1/agent/chat",
            json={
                "universidad_id": universidad_id,
                "message": "¿Qué materias puedo cursar?",
                "kardex_data": {
                    "semestres": [
                        {"materias": [{"clave": "MAT101", "calificacion": 85}]}
                    ]
                },
                "oferta_data": {
                    "materias": [
                        {"clave": "MAT201", "nombre": "Cálculo II"}
                    ]
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
