#!/bin/bash
# ============================================================
# Deploy Manual a Google Cloud Run
# ============================================================
# Uso: ./deploy.sh [backend|frontend|all]
# ============================================================

set -e

# Configuración
PROJECT_ID="${GCP_PROJECT_ID:-tutor-ia-prod}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE="tutor-ia-backend"
FRONTEND_SERVICE="tutor-ia-frontend"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploy Tutor IA a Cloud Run${NC}"
echo "========================================"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI no está instalado${NC}"
    echo "Instala desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1; then
    echo -e "${YELLOW}⚠️ No hay cuenta de GCP autenticada${NC}"
    echo "Ejecuta: gcloud auth login"
    exit 1
fi

# Función para deploy del backend
deploy_backend() {
    echo -e "${GREEN}📦 Construyendo Backend...${NC}"
    cd backend
    
    # Build
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
        --timeout=600s
    
    # Deploy
    echo -e "${GREEN}🚀 Desplegando Backend...${NC}"
    gcloud run deploy $BACKEND_SERVICE \
        --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars="ENVIRONMENT=production" \
        --memory 1Gi \
        --cpu 2 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 60s
    
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Backend desplegado: $BACKEND_URL${NC}"
    
    cd ..
    echo $BACKEND_URL
}

# Función para deploy del frontend
deploy_frontend() {
    BACKEND_URL=$1
    
    if [ -z "$BACKEND_URL" ]; then
        BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region $REGION --format 'value(status.url)' 2>/dev/null || echo "")
    fi
    
    if [ -z "$BACKEND_URL" ]; then
        echo -e "${RED}❌ No se encontró URL del backend${NC}"
        echo "Despliega el backend primero o proporciona BACKEND_URL"
        exit 1
    fi
    
    echo -e "${GREEN}📦 Construyendo Frontend...${NC}"
    echo "Backend URL: $BACKEND_URL"
    cd frontend
    
    # Build con la URL del backend
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
        --timeout=600s
    
    # Deploy
    echo -e "${GREEN}🚀 Desplegando Frontend...${NC}"
    gcloud run deploy $FRONTEND_SERVICE \
        --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --set-env-vars="API_URL=$BACKEND_URL" \
        --memory 512Mi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 5 \
        --timeout 60s
    
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region $REGION --format 'value(status.url)')
    echo -e "${GREEN}✅ Frontend desplegado: $FRONTEND_URL${NC}"
    
    cd ..
}

# Main
case "${1:-all}" in
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend "${2:-}"
        ;;
    all)
        BACKEND_URL=$(deploy_backend)
        deploy_frontend $BACKEND_URL
        echo ""
        echo -e "${GREEN}🎉 Deploy completo!${NC}"
        echo "========================================"
        echo -e "Backend:  ${YELLOW}$BACKEND_URL${NC}"
        FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region $REGION --format 'value(status.url)')
        echo -e "Frontend: ${YELLOW}$FRONTEND_URL${NC}"
        ;;
    *)
        echo "Uso: $0 [backend|frontend|all]"
        exit 1
        ;;
esac
