# 🚀 Guía de Deploy a Google Cloud Run

## Prerrequisitos

### 1. Cuenta de Google Cloud
- Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com)
- Habilita la facturación (el free tier cubre el uso básico)

### 2. APIs Necesarias
Habilita estas APIs en tu proyecto:
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 3. Instalar Google Cloud CLI
```bash
# Ubuntu/Debian
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

## Configuración Inicial

### 1. Configurar proyecto
```bash
export GCP_PROJECT_ID="tu-proyecto-id"
gcloud config set project $GCP_PROJECT_ID
```

### 2. Crear Artifact Registry (para imágenes Docker)
```bash
gcloud artifacts repositories create tutor-ia \
  --repository-format=docker \
  --location=us-central1 \
  --description="Tutor IA Docker images"
```

### 3. Configurar base de datos (Supabase - Gratis)

1. Ve a [supabase.com](https://supabase.com) y crea un proyecto
2. Copia la connection string de Settings > Database
3. Guárdala como secret:

```bash
echo -n "postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres" | \
  gcloud secrets create DATABASE_URL --data-file=-
```

### 4. Configurar Redis (Upstash - Gratis)

1. Ve a [upstash.com](https://upstash.com) y crea una base de datos Redis
2. Copia la URL de conexión
3. Guárdala como secret:

```bash
echo -n "redis://default:PASSWORD@xxx.upstash.io:6379" | \
  gcloud secrets create REDIS_URL --data-file=-
```

### 5. Configurar Google API Key (Gemini)

```bash
echo -n "tu-api-key-de-google-ai-studio" | \
  gcloud secrets create GOOGLE_API_KEY --data-file=-
```

### 6. Crear Secret Key para JWT

```bash
openssl rand -hex 32 | \
  gcloud secrets create SECRET_KEY --data-file=-
```

## Deploy

### Opción 1: Deploy Manual (Script)

```bash
# Dar permisos de ejecución
chmod +x deploy.sh

# Deploy todo
./deploy.sh all

# O deploy individual
./deploy.sh backend
./deploy.sh frontend
```

### Opción 2: GitHub Actions (Automático)

#### Configurar Secrets en GitHub

1. Ve a tu repo > Settings > Secrets and variables > Actions
2. Agrega estos secrets:

| Secret | Descripción |
|--------|-------------|
| `GCP_PROJECT_ID` | ID de tu proyecto en GCP |
| `GCP_SA_KEY` | JSON de Service Account (ver abajo) |
| `DATABASE_URL` | URL de PostgreSQL (Supabase) |
| `REDIS_URL` | URL de Redis (Upstash) |
| `GOOGLE_API_KEY` | API Key de Google AI Studio |
| `SECRET_KEY` | Key para JWT (genera con openssl) |

#### Crear Service Account para CI/CD

```bash
# Crear service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Dar permisos necesarios
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Crear key JSON
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@$GCP_PROJECT_ID.iam.gserviceaccount.com

# Copiar contenido de key.json al secret GCP_SA_KEY en GitHub
cat key.json

# ⚠️ Eliminar archivo local
rm key.json
```

#### Trigger Deploy

```bash
# Push a main triggerea el deploy automático
git add .
git commit -m "feat: deploy to cloud run"
git push origin main
```

## URLs Finales

Después del deploy, obtienes URLs como:
- **Backend:** `https://tutor-ia-backend-xxxxx.run.app`
- **Frontend:** `https://tutor-ia-frontend-xxxxx.run.app`

## Costos Esperados (Free Tier)

| Servicio | Free Tier | Uso Estimado |
|----------|-----------|--------------|
| Cloud Run | 2M requests/mes | ~50K requests |
| Artifact Registry | 500MB | ~200MB |
| Cloud Build | 120 min/día | ~5 min/deploy |
| Supabase | 500MB DB | ~50MB |
| Upstash Redis | 10K commands/día | ~1K commands |
| Gemini API | 1M tokens/día | ~100K tokens |

**Costo total estimado: $0/mes** ✅

## Troubleshooting

### Error: Permission denied
```bash
gcloud auth login
gcloud config set project $GCP_PROJECT_ID
```

### Error: Image not found
```bash
# Verificar que la imagen existe
gcloud artifacts docker images list us-central1-docker.pkg.dev/$GCP_PROJECT_ID/tutor-ia
```

### Error: Service unavailable
```bash
# Ver logs
gcloud run logs read tutor-ia-backend --region us-central1 --limit 50
```

### Verificar estado de servicios
```bash
gcloud run services list --region us-central1
```

## Rollback

```bash
# Listar revisiones
gcloud run revisions list --service tutor-ia-backend --region us-central1

# Rollback a revisión anterior
gcloud run services update-traffic tutor-ia-backend \
  --region us-central1 \
  --to-revisions=tutor-ia-backend-00001-abc=100
```
