#!/bin/bash
# run.sh - Script para ejecutar el frontend Streamlit

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎓 Tutor IA - Frontend Streamlit${NC}"
echo "=================================="

# Verificar que existe .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado. Creando desde .env.example...${NC}"
    cp .env.example .env 2>/dev/null || echo "API_URL=http://localhost:8000" > .env
fi

# Verificar que el backend está corriendo
echo "🔍 Verificando conexión con backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend corriendo en http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  Backend no detectado. Asegúrate de ejecutar 'docker compose up -d' primero.${NC}"
fi

echo ""
echo "🚀 Iniciando Streamlit..."
echo ""

# Ejecutar Streamlit
streamlit run app.py --server.port 8501 --server.address localhost
