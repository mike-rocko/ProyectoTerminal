"""
Pytest configuration and fixtures for Tutor IA tests.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def universidad_id():
    """Default test universidad ID."""
    return "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def sample_kardex():
    """Sample kardex data for testing."""
    return {
        "alumno": {
            "nombre": "Juan",
            "apellido_paterno": "Pérez",
            "matricula": "20210001"
        },
        "creditos": {
            "aprobados": 120,
            "plan": 300,
            "porcentaje_avance": 40.0
        },
        "semestres": [
            {
                "periodo": "2024-1",
                "materias": [
                    {"clave": "MAT101", "nombre": "Cálculo I", "calificacion": 85, "creditos": 8},
                    {"clave": "FIS101", "nombre": "Física I", "calificacion": 75, "creditos": 6},
                    {"clave": "PRG101", "nombre": "Programación I", "calificacion": 60, "creditos": 6}
                ]
            }
        ]
    }


@pytest.fixture
def sample_oferta():
    """Sample oferta académica for testing."""
    return {
        "semestre": "2024-2",
        "materias": [
            {
                "clave": "MAT201",
                "nombre": "Cálculo II",
                "nrc": "10001",
                "creditos": 8,
                "profesor": "Dr. García",
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "09:00", "hora_fin": "11:00"},
                    {"dia": "Miércoles", "hora_inicio": "09:00", "hora_fin": "11:00"}
                ]
            },
            {
                "clave": "MAT201",
                "nombre": "Cálculo II",
                "nrc": "10002",
                "creditos": 8,
                "profesor": "Dra. López",
                "horarios": [
                    {"dia": "Martes", "hora_inicio": "14:00", "hora_fin": "16:00"},
                    {"dia": "Jueves", "hora_inicio": "14:00", "hora_fin": "16:00"}
                ]
            },
            {
                "clave": "FIS201",
                "nombre": "Física II",
                "nrc": "20001",
                "creditos": 6,
                "profesor": "Dr. Martínez",
                "horarios": [
                    {"dia": "Lunes", "hora_inicio": "11:00", "hora_fin": "13:00"},
                    {"dia": "Miércoles", "hora_inicio": "11:00", "hora_fin": "13:00"}
                ]
            },
            {
                "clave": "PRG101",
                "nombre": "Programación I",
                "nrc": "30001",
                "creditos": 6,
                "profesor": "Ing. Rodríguez",
                "horarios": [
                    {"dia": "Viernes", "hora_inicio": "09:00", "hora_fin": "12:00"}
                ]
            },
            {
                "clave": "MAT301",
                "nombre": "Cálculo III",
                "nrc": "40001",
                "creditos": 8,
                "profesor": "Dr. Sánchez",
                "horarios": [
                    {"dia": "Martes", "hora_inicio": "09:00", "hora_fin": "11:00"}
                ]
            }
        ]
    }


@pytest.fixture
def sample_mapa():
    """Sample mapa curricular with prerequisites."""
    return {
        "carrera": "Ingeniería en Sistemas",
        "plan": "2020",
        "semestres": [
            {
                "numero": 1,
                "materias": [
                    {"clave": "MAT101", "nombre": "Cálculo I", "creditos": 8, "prerrequisitos": []},
                    {"clave": "FIS101", "nombre": "Física I", "creditos": 6, "prerrequisitos": []},
                    {"clave": "PRG101", "nombre": "Programación I", "creditos": 6, "prerrequisitos": []}
                ]
            },
            {
                "numero": 2,
                "materias": [
                    {"clave": "MAT201", "nombre": "Cálculo II", "creditos": 8, "prerrequisitos": ["MAT101"]},
                    {"clave": "FIS201", "nombre": "Física II", "creditos": 6, "prerrequisitos": ["FIS101", "MAT101"]}
                ]
            },
            {
                "numero": 3,
                "materias": [
                    {"clave": "MAT301", "nombre": "Cálculo III", "creditos": 8, "prerrequisitos": ["MAT201"]}
                ]
            }
        ]
    }
