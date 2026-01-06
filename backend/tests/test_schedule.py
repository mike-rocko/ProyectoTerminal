"""
Tests for schedule generation endpoints.
"""
import pytest


class TestExtractBloques:
    """Tests for /schedule/extract-bloques endpoint."""
    
    def test_extract_bloques_success(self, client, sample_oferta):
        """Test extracting unique time blocks from oferta."""
        response = client.post(
            "/api/v1/schedule/extract-bloques",
            json={"oferta_data": sample_oferta}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_bloques" in data
        assert "bloques" in data
        assert "dias_con_clases" in data
        assert data["total_bloques"] > 0
        assert len(data["bloques"]) == data["total_bloques"]
    
    def test_extract_bloques_counts_materias(self, client):
        """Test that blocks count how many subjects are in each time slot."""
        oferta = {
            "materias": [
                {"nombre": "Mat A", "horario": {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"}},
                {"nombre": "Mat B", "horario": {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"}},
                {"nombre": "Mat C", "horario": {"dia": "Martes", "hora_inicio": "09:00", "hora_fin": "11:00"}}
            ]
        }
        
        response = client.post(
            "/api/v1/schedule/extract-bloques",
            json={"oferta_data": oferta}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have 2 unique blocks
        assert data["total_bloques"] == 2
        
        # Find the Lunes block - should have 2 materias
        lunes_block = next(b for b in data["bloques"] if b["dia"] == "Lunes")
        assert lunes_block["materias_en_bloque"] == 2
    
    def test_extract_bloques_empty_oferta(self, client):
        """Test with empty oferta."""
        response = client.post(
            "/api/v1/schedule/extract-bloques",
            json={"oferta_data": {"materias": []}}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_bloques"] == 0


class TestFromVision:
    """Tests for /schedule/from-vision endpoint."""
    
    def test_from_vision_basic(self, client, sample_kardex, sample_oferta):
        """Test basic schedule generation from vision data."""
        response = client.post(
            "/api/v1/schedule/from-vision",
            json={
                "kardex_data": sample_kardex,
                "oferta_data": sample_oferta,
                "max_materias": 4,
                "creditos_minimos": 6
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data
        assert "horarios" in data
        assert "mensaje" in data
    
    def test_from_vision_excludes_approved(self, client, sample_kardex, sample_oferta):
        """Test that approved subjects are excluded."""
        response = client.post(
            "/api/v1/schedule/from-vision",
            json={
                "kardex_data": sample_kardex,
                "oferta_data": sample_oferta,
                "max_materias": 5,
                "creditos_minimos": 6
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # MAT101 and FIS101 are approved, should not be in any schedule
        for horario in data.get("horarios", []):
            for materia in horario.get("materias", []):
                assert materia["clave"] not in ["MAT101", "FIS101"]
    
    def test_from_vision_includes_failed(self, client, sample_kardex, sample_oferta):
        """Test that failed subjects (PRG101 with 60) are included."""
        response = client.post(
            "/api/v1/schedule/from-vision",
            json={
                "kardex_data": sample_kardex,
                "oferta_data": sample_oferta,
                "max_materias": 5,
                "creditos_minimos": 6
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # PRG101 was failed (60 < 70), should be available
        all_materias = []
        for horario in data.get("horarios", []):
            for materia in horario.get("materias", []):
                all_materias.append(materia["clave"])
        
        # PRG101 should appear in at least one schedule
        assert "PRG101" in all_materias
    
    def test_from_vision_with_prerequisites(self, client, sample_kardex, sample_oferta, sample_mapa):
        """Test that prerequisites are validated when mapa is provided."""
        response = client.post(
            "/api/v1/schedule/from-vision",
            json={
                "kardex_data": sample_kardex,
                "oferta_data": sample_oferta,
                "mapa_data": sample_mapa,
                "max_materias": 5,
                "creditos_minimos": 6
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # MAT301 requires MAT201 (not approved), should be excluded
        for horario in data.get("horarios", []):
            for materia in horario.get("materias", []):
                assert materia["clave"] != "MAT301"
        
        # Should have warning about MAT301
        advertencias = data.get("advertencias", [])
        mat301_warning = any("MAT301" in adv for adv in advertencias)
        assert mat301_warning, "Should warn about MAT301 missing prerequisites"
    
    def test_from_vision_with_conflicts(self, client, sample_kardex, sample_oferta):
        """Test that time conflicts are respected."""
        response = client.post(
            "/api/v1/schedule/from-vision",
            json={
                "kardex_data": sample_kardex,
                "oferta_data": sample_oferta,
                "conflictos": [
                    {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00", "motivo": "Trabajo"}
                ],
                "max_materias": 5,
                "creditos_minimos": 6
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # No schedule should have a subject on Lunes 09:00-11:00
        for horario in data.get("horarios", []):
            for materia in horario.get("materias", []):
                for h in materia.get("horarios", []):
                    if h["dia"] == "Lunes":
                        # If it's Lunes, should not overlap with 09:00-11:00
                        assert not (h["hora_inicio"] == "09:00" and h["hora_fin"] == "11:00")
    
    def test_from_vision_no_eligible_subjects(self, client):
        """Test when no subjects are eligible."""
        # All subjects are already approved
        kardex = {
            "semestres": [
                {"materias": [
                    {"clave": "MAT101", "calificacion": 100}
                ]}
            ]
        }
        oferta = {
            "materias": [
                {"clave": "MAT101", "nombre": "Cálculo I", "nrc": "1001", "creditos": 8,
                 "horarios": [{"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"}]}
            ]
        }
        
        response = client.post(
            "/api/v1/schedule/from-vision",
            json={
                "kardex_data": kardex,
                "oferta_data": oferta
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == False
        assert "elegibles" in data["mensaje"].lower()


class TestGenerateSchedule:
    """Tests for /schedule/generate endpoint."""
    
    def test_generate_schedule_basic(self, client):
        """Test basic schedule generation."""
        request = {
            "materias_elegibles": [
                {
                    "clave": "MAT101",
                    "nombre": "Cálculo I",
                    "creditos": 8,
                    "es_reprobada": False,
                    "es_obligatoria": True,
                    "opciones": [
                        {
                            "nrc": "1001",
                            "clave": "MAT101",
                            "nombre": "Cálculo I",
                            "creditos": 8,
                            "horarios": [
                                {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"}
                            ]
                        }
                    ]
                }
            ],
            "creditos_minimos": 6,
            "max_materias": 5
        }
        
        response = client.post("/api/v1/schedule/generate", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert len(data["horarios"]) > 0
    
    def test_generate_schedule_test_endpoint(self, client):
        """Test the test data endpoint."""
        response = client.post("/api/v1/schedule/generate-test")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert len(data["horarios"]) > 0
        assert data["horarios"][0]["ranking"] == 1
