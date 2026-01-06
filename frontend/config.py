"""
Configuración de la aplicación Streamlit.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Backend
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Universidad por defecto (para demo)
DEFAULT_UNIVERSIDAD_ID = os.getenv("DEFAULT_UNIVERSIDAD_ID", "11111111-1111-1111-1111-111111111111")

# Configuración de la app
APP_TITLE = "Tutor IA - Universidad del Caribe"
APP_ICON = "🎓"

# Límites
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "pdf"]
