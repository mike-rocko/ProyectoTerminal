"""
Panel de Administración de Universidades - Tutor IA

Permite a las universidades:
- Configurar su información
- Gestionar carreras y mapas curriculares
- Subir documentos para RAG (reglamentos, calendario, etc.)
- Ver métricas de uso
"""
import streamlit as st
import requests
from typing import Optional, Dict, Any
import os
import json
import base64

# Configuración
API_URL = os.getenv("API_URL", "http://backend:8000")
st.set_page_config(
    page_title="Panel Admin - Tutor IA",
    page_icon="🏛️",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #1E40AF, #3B82F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #f8fafc;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# API Client
# ============================================

class AdminAPIClient:
    def __init__(self):
        self.base_url = API_URL.rstrip("/")
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        self.token = token
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method, url, json=data, headers=self._headers(), timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            try:
                return {"error": e.response.json().get("detail", str(e))}
            except:
                return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
    
    def login(self, email: str, password: str) -> Dict:
        return self._request("POST", "/api/v1/admin/login", {
            "email": email,
            "password": password
        })
    
    def register(self, email: str, password: str, nombre: str, universidad_slug: str) -> Dict:
        return self._request("POST", "/api/v1/admin/register", {
            "email": email,
            "password": password,
            "nombre": nombre,
            "universidad_slug": universidad_slug
        })
    
    def get_universidad(self, universidad_id: str) -> Dict:
        return self._request("GET", f"/api/v1/admin/universidad/{universidad_id}")
    
    def update_universidad(self, universidad_id: str, data: Dict) -> Dict:
        return self._request("PUT", f"/api/v1/admin/universidad/{universidad_id}", data)
    
    def get_carreras(self, universidad_id: str) -> Dict:
        return self._request("GET", f"/api/v1/admin/universidad/{universidad_id}/carreras")
    
    def create_carrera(self, universidad_id: str, nombre: str, clave: str) -> Dict:
        return self._request("POST", f"/api/v1/admin/universidad/{universidad_id}/carreras", {
            "nombre": nombre,
            "clave": clave
        })
    
    def get_documentos(self, universidad_id: str) -> Dict:
        return self._request("GET", f"/api/v1/admin/universidad/{universidad_id}/documentos")
    
    def create_documento(self, universidad_id: str, tipo: str, titulo: str, contenido: str) -> Dict:
        return self._request("POST", f"/api/v1/admin/universidad/{universidad_id}/documentos", {
            "tipo": tipo,
            "titulo": titulo,
            "contenido": contenido
        })
    
    def delete_documento(self, universidad_id: str, documento_id: str) -> Dict:
        return self._request("DELETE", f"/api/v1/admin/universidad/{universidad_id}/documentos/{documento_id}")
    
    def get_dashboard(self, universidad_id: str) -> Dict:
        return self._request("GET", f"/api/v1/admin/universidad/{universidad_id}/dashboard")
    
    def list_universidades(self) -> Dict:
        return self._request("GET", "/api/v1/admin/universidades")
    
    def create_universidad(self, nombre: str, slug: str, email_contacto: str = None, telefono: str = None) -> Dict:
        return self._request("POST", "/api/v1/admin/universidades", {
            "nombre": nombre,
            "slug": slug,
            "email_contacto": email_contacto,
            "telefono": telefono
        })


api = AdminAPIClient()


# ============================================
# Session Persistence (sobrevive refresh)
# ============================================

def save_session_to_storage():
    """Guarda la sesión en localStorage del navegador usando JS."""
    if st.session_state.get("admin_authenticated") and st.session_state.get("admin_token"):
        session_data = {
            "token": st.session_state.admin_token,
            "admin_info": st.session_state.admin_info,
            "universidad_id": st.session_state.universidad_id
        }
        # Codificar en base64 para evitar problemas con caracteres especiales
        encoded = base64.b64encode(json.dumps(session_data).encode()).decode()
        # Inyectar JavaScript para guardar en localStorage
        st.markdown(f"""
        <script>
            localStorage.setItem('admin_session', '{encoded}');
        </script>
        """, unsafe_allow_html=True)


def get_session_from_url():
    """Intenta recuperar sesión desde query params."""
    try:
        params = st.query_params
        if "session" in params:
            encoded = params["session"]
            decoded = json.loads(base64.b64decode(encoded).decode())
            return decoded
    except:
        pass
    return None


def clear_session_storage():
    """Limpia la sesión guardada."""
    st.markdown("""
    <script>
        localStorage.removeItem('admin_session');
    </script>
    """, unsafe_allow_html=True)


# ============================================
# Session State
# ============================================

def init_session():
    """Inicializa el estado de sesión, intentando recuperar de URL primero."""
    # Intentar recuperar sesión de query params
    saved_session = get_session_from_url()
    
    if saved_session and not st.session_state.get("admin_authenticated"):
        # Verificar que el token sigue siendo válido
        st.session_state.admin_token = saved_session.get("token")
        st.session_state.admin_info = saved_session.get("admin_info")
        st.session_state.universidad_id = saved_session.get("universidad_id")
        st.session_state.admin_authenticated = True
        api.set_token(st.session_state.admin_token)
    
    # Inicializar valores por defecto si no existen
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    if "admin_token" not in st.session_state:
        st.session_state.admin_token = None
    if "admin_info" not in st.session_state:
        st.session_state.admin_info = None
    if "universidad_id" not in st.session_state:
        st.session_state.universidad_id = None


def persist_session():
    """Guarda la sesión en la URL para que sobreviva refresh."""
    if st.session_state.get("admin_authenticated") and st.session_state.get("admin_token"):
        session_data = {
            "token": st.session_state.admin_token,
            "admin_info": st.session_state.admin_info,
            "universidad_id": st.session_state.universidad_id
        }
        encoded = base64.b64encode(json.dumps(session_data).encode()).decode()
        st.query_params["session"] = encoded


# ============================================
# Pages
# ============================================

def login_page():
    """Página de login para administradores."""
    st.markdown('<h1 class="main-header">🏛️ Panel de Administración</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Gestiona tu universidad en Tutor IA</p>", unsafe_allow_html=True)
    
    # Enlace al portal de estudiantes
    st.markdown(
        "<p style='text-align: center; margin-bottom: 20px;'>"
        "¿Eres estudiante? "
        "<a href='http://localhost:8501' target='_blank'>🎓 Ir al Portal de Estudiantes</a>"
        "</p>",
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrar Universidad"])
        
        with tab1:
            with st.form("admin_login"):
                email = st.text_input("📧 Email", placeholder="admin@universidad.edu")
                password = st.text_input("🔒 Contraseña", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit and email and password:
                    with st.spinner("Iniciando sesión..."):
                        result = api.login(email, password)
                    
                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    elif "token" in result:
                        st.session_state.admin_token = result["token"]["access_token"]
                        st.session_state.admin_authenticated = True
                        st.session_state.admin_info = result["admin"]
                        st.session_state.universidad_id = result["admin"]["universidad_id"]
                        api.set_token(result["token"]["access_token"])
                        persist_session()  # Guardar en URL
                        st.success("✅ ¡Bienvenido!")
                        st.rerun()
        
        with tab2:
            st.info("💡 Registra tu universidad o únete a una existente.")
            
            # Mostrar universidades disponibles
            unis = api.list_universidades()
            uni_list = unis.get("universidades", [])
            
            # Opción para crear nueva universidad
            crear_nueva = st.checkbox("🆕 Mi universidad no está en la lista - Crear nueva")
            
            if crear_nueva:
                st.subheader("Registrar Nueva Universidad")
                with st.form("create_universidad"):
                    uni_nombre = st.text_input("🏛️ Nombre de la Universidad", placeholder="Universidad del Caribe")
                    uni_slug = st.text_input("🔗 Identificador (slug)", placeholder="unicaribe", 
                                            help="Sin espacios, minúsculas. Ej: 'unam', 'itesm'")
                    uni_email = st.text_input("📧 Email de contacto institucional", placeholder="info@universidad.edu")
                    uni_telefono = st.text_input("📞 Teléfono", placeholder="+52 999 123 4567")
                    
                    st.divider()
                    st.write("**Datos del Administrador:**")
                    admin_nombre = st.text_input("👤 Tu nombre completo")
                    admin_email = st.text_input("📧 Tu email institucional")
                    admin_password = st.text_input("🔒 Contraseña", type="password")
                    
                    submit = st.form_submit_button("🚀 Crear Universidad y Registrarme", use_container_width=True)
                    
                    if submit and all([uni_nombre, uni_slug, admin_nombre, admin_email, admin_password]):
                        with st.spinner("Creando universidad..."):
                            # Primero crear la universidad
                            create_result = api.create_universidad(
                                nombre=uni_nombre,
                                slug=uni_slug.lower().replace(" ", ""),
                                email_contacto=uni_email,
                                telefono=uni_telefono
                            )
                        
                        if "error" in create_result:
                            st.error(f"❌ Error creando universidad: {create_result['error']}")
                        elif create_result.get("success"):
                            # Ahora registrar el admin
                            with st.spinner("Registrando administrador..."):
                                result = api.register(
                                    email=admin_email,
                                    password=admin_password,
                                    nombre=admin_nombre,
                                    universidad_slug=uni_slug.lower().replace(" ", "")
                                )
                            
                            if "error" in result:
                                st.error(f"❌ Error registrando admin: {result['error']}")
                            elif "token" in result:
                                st.session_state.admin_token = result["token"]["access_token"]
                                st.session_state.admin_authenticated = True
                                st.session_state.admin_info = result["admin"]
                                st.session_state.universidad_id = result["admin"]["universidad_id"]
                                api.set_token(result["token"]["access_token"])
                                persist_session()  # Guardar en URL
                                st.success("✅ ¡Universidad creada y registro exitoso!")
                                st.balloons()
                                st.rerun()
            
            elif uni_list:
                uni_options = {u["nombre"]: u["slug"] for u in uni_list}
                
                with st.form("admin_register"):
                    nombre = st.text_input("👤 Nombre completo")
                    email = st.text_input("📧 Email institucional")
                    password = st.text_input("🔒 Contraseña", type="password")
                    universidad = st.selectbox("🏛️ Universidad", list(uni_options.keys()))
                    
                    submit = st.form_submit_button("Registrarse", use_container_width=True)
                    
                    if submit and all([nombre, email, password, universidad]):
                        with st.spinner("Registrando..."):
                            result = api.register(
                                email=email,
                                password=password,
                                nombre=nombre,
                                universidad_slug=uni_options[universidad]
                            )
                        
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        elif "token" in result:
                            st.session_state.admin_token = result["token"]["access_token"]
                            st.session_state.admin_authenticated = True
                            st.session_state.admin_info = result["admin"]
                            st.session_state.universidad_id = result["admin"]["universidad_id"]
                            api.set_token(result["token"]["access_token"])
                            persist_session()  # Guardar en URL
                            st.success("✅ ¡Registro exitoso!")
                            st.rerun()
            else:
                st.warning("⚠️ No hay universidades registradas. Marca la casilla arriba para crear la primera.")


def sidebar():
    """Sidebar con navegación."""
    with st.sidebar:
        admin = st.session_state.admin_info
        st.write(f"👤 **{admin['nombre']}**")
        st.write(f"🏛️ {admin['universidad_nombre']}")
        
        if admin.get("is_super_admin"):
            st.caption("⭐ Super Admin")
        
        st.divider()
        
        page = st.radio(
            "📍 Navegación",
            ["📊 Dashboard", "🏛️ Info Universidad", "📚 Carreras", "📄 Documentos RAG"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.session_state.admin_token = None
            st.session_state.admin_info = None
            st.query_params.clear()  # Limpiar sesión persistida
            st.rerun()
        
        return page


def dashboard_page():
    """Dashboard con métricas."""
    st.header("📊 Dashboard")
    
    result = api.get_dashboard(st.session_state.universidad_id)
    
    if "error" in result:
        st.error(f"❌ {result['error']}")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Estudiantes", result["total_estudiantes"])
    
    with col2:
        st.metric("📚 Carreras", result["total_carreras"])
    
    with col3:
        st.metric("📄 Documentos RAG", result["total_documentos"])
    
    with col4:
        st.metric("📈 Nuevos este mes", result["estudiantes_activos_mes"])
    
    st.divider()
    
    st.subheader("🚀 Acciones Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Agregar Carrera", use_container_width=True):
            st.session_state.nav_page = "📚 Carreras"
            st.session_state.show_add_carrera = True
            st.rerun()
    
    with col2:
        if st.button("📄 Subir Documento", use_container_width=True):
            st.session_state.nav_page = "📄 Documentos RAG"
            st.session_state.show_add_documento = True
            st.rerun()
    
    with col3:
        if st.button("✏️ Editar Info", use_container_width=True):
            st.session_state.nav_page = "🏛️ Info Universidad"
            st.rerun()


def universidad_page():
    """Página de información de la universidad."""
    st.header("🏛️ Información de la Universidad")
    
    result = api.get_universidad(st.session_state.universidad_id)
    
    if "error" in result:
        st.error(f"❌ {result['error']}")
        return
    
    with st.form("update_universidad"):
        nombre = st.text_input("Nombre", value=result.get("nombre", ""))
        logo_url = st.text_input("URL del Logo", value=result.get("logo_url", "") or "")
        email = st.text_input("Email de contacto", value=result.get("email_contacto", "") or "")
        telefono = st.text_input("Teléfono", value=result.get("telefono", "") or "")
        direccion = st.text_area("Dirección", value=result.get("direccion", "") or "")
        
        submit = st.form_submit_button("💾 Guardar Cambios", use_container_width=True)
        
        if submit:
            update_result = api.update_universidad(
                st.session_state.universidad_id,
                {
                    "nombre": nombre,
                    "logo_url": logo_url if logo_url else None,
                    "email_contacto": email if email else None,
                    "telefono": telefono if telefono else None,
                    "direccion": direccion if direccion else None
                }
            )
            
            if "error" in update_result:
                st.error(f"❌ {update_result['error']}")
            else:
                st.success("✅ Información actualizada")


def carreras_page():
    """Gestión de carreras."""
    st.header("📚 Gestión de Carreras")
    
    # Listar carreras existentes
    result = api.get_carreras(st.session_state.universidad_id)
    
    if "error" in result:
        st.error(f"❌ {result['error']}")
    else:
        carreras = result.get("carreras", [])
        
        if carreras:
            st.subheader("Carreras Registradas")
            for carrera in carreras:
                with st.expander(f"📘 {carrera['nombre']} ({carrera['clave']})"):
                    st.write(f"**ID:** {carrera['id']}")
                    st.write(f"**Plan de estudios:** {'✅ Cargado' if carrera.get('tiene_plan') else '❌ Pendiente'}")
                    
                    if not carrera.get('tiene_plan'):
                        st.warning("⚠️ Esta carrera no tiene plan de estudios. Sube una imagen del mapa curricular.")
        else:
            st.info("No hay carreras registradas aún.")
    
    st.divider()
    
    # Agregar nueva carrera
    st.subheader("➕ Agregar Nueva Carrera")
    
    with st.form("add_carrera"):
        nombre = st.text_input("Nombre de la carrera", placeholder="Ingeniería en Sistemas Computacionales")
        clave = st.text_input("Clave", placeholder="ISC")
        
        submit = st.form_submit_button("Agregar Carrera", use_container_width=True)
        
        if submit and nombre and clave:
            create_result = api.create_carrera(
                st.session_state.universidad_id,
                nombre=nombre,
                clave=clave
            )
            
            if "error" in create_result:
                st.error(f"❌ {create_result['error']}")
            else:
                st.success(f"✅ Carrera '{nombre}' creada")
                st.rerun()


def documentos_page():
    """Gestión de documentos para RAG."""
    st.header("📄 Documentos de Información")
    
    st.info("""
    📌 **¿Para qué sirve esto?**
    
    Los documentos que subas aquí serán usados por el chatbot para responder preguntas de los estudiantes.
    Por ejemplo: calendario académico, reglamentos, información de becas, etc.
    """)
    
    # Listar documentos existentes
    result = api.get_documentos(st.session_state.universidad_id)
    
    if "error" in result:
        st.error(f"❌ {result['error']}")
    else:
        docs = result.get("documentos", [])
        
        if docs:
            st.subheader("📋 Documentos Existentes")
            
            for doc in docs:
                with st.expander(f"📝 {doc['titulo']} ({doc['tipo']})"):
                    st.write(doc['contenido_preview'])
                    st.caption(f"Creado: {doc['created_at']}")
                    
                    if st.button("🗑️ Eliminar", key=f"del_{doc['id']}"):
                        del_result = api.delete_documento(
                            st.session_state.universidad_id,
                            doc['id']
                        )
                        if "error" in del_result:
                            st.error(f"❌ {del_result['error']}")
                        else:
                            st.success("✅ Documento eliminado")
                            st.rerun()
        else:
            st.info("No hay documentos cargados aún.")
    
    st.divider()
    
    # Agregar nuevo documento
    st.subheader("➕ Agregar Nuevo Documento")
    
    tipo_opciones = {
        "Misión y Visión": "mision_vision",
        "Calendario Académico": "calendario",
        "Reglamento": "reglamento",
        "Información de Becas": "becas",
        "Trámites": "tramites",
        "Contacto": "contacto",
        "FAQ": "faq",
        "Otro": "otro"
    }
    
    with st.form("add_documento"):
        tipo_display = st.selectbox("Tipo de documento", list(tipo_opciones.keys()))
        titulo = st.text_input("Título", placeholder="Ej: Calendario Académico 2026")
        contenido = st.text_area(
            "Contenido",
            placeholder="Pega aquí el contenido del documento...",
            height=300
        )
        
        submit = st.form_submit_button("📤 Subir Documento", use_container_width=True)
        
        if submit and titulo and contenido:
            with st.spinner("Procesando documento y generando embeddings..."):
                create_result = api.create_documento(
                    st.session_state.universidad_id,
                    tipo=tipo_opciones[tipo_display],
                    titulo=titulo,
                    contenido=contenido
                )
            
            if "error" in create_result:
                st.error(f"❌ {create_result['error']}")
            else:
                st.success(f"✅ {create_result.get('message', 'Documento creado')}")
                st.rerun()
    
    st.divider()
    
    # Plantillas de documentos
    st.subheader("📋 Plantillas de Ejemplo")
    
    with st.expander("Ver plantilla: Misión y Visión"):
        st.code("""
MISIÓN
La Universidad [Nombre] tiene como misión formar profesionales 
competentes, comprometidos con el desarrollo social y tecnológico...

VISIÓN
Ser una institución de educación superior reconocida por su 
excelencia académica y su contribución al desarrollo regional...

VALORES
- Excelencia académica
- Responsabilidad social
- Innovación
- Ética profesional
        """)
    
    with st.expander("Ver plantilla: Calendario Académico"):
        st.code("""
CALENDARIO ACADÉMICO 2026

SEMESTRE PRIMAVERA 2026
- Inscripciones: 15-22 de Enero
- Inicio de clases: 27 de Enero
- Exámenes parciales 1: 3-7 de Marzo
- Semana Santa: 13-20 de Abril (sin clases)
- Exámenes parciales 2: 28 Abril - 2 Mayo
- Último día de clases: 30 de Mayo
- Exámenes finales: 2-6 de Junio
- Publicación de calificaciones: 13 de Junio

SEMESTRE OTOÑO 2026
- Inscripciones: 5-12 de Agosto
- Inicio de clases: 18 de Agosto
...
        """)


# ============================================
# Main
# ============================================

def main():
    init_session()
    
    if not st.session_state.admin_authenticated:
        login_page()
    else:
        api.set_token(st.session_state.admin_token)
        page = sidebar()
        
        # Override page if nav_page is set (from quick actions)
        if "nav_page" in st.session_state and st.session_state.nav_page:
            page = st.session_state.nav_page
            st.session_state.nav_page = None  # Clear after use
        
        if page == "📊 Dashboard":
            dashboard_page()
        elif page == "🏛️ Info Universidad":
            universidad_page()
        elif page == "📚 Carreras":
            carreras_page()
        elif page == "📄 Documentos RAG":
            documentos_page()


if __name__ == "__main__":
    main()
