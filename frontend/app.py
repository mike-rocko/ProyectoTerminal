"""
🎓 Tutor IA - Asistente Académico Inteligente

Aplicación Streamlit para interactuar con el sistema de tutoría.
"""
import streamlit as st
from config import APP_TITLE, APP_ICON, DEFAULT_UNIVERSIDAD_ID
from api_client import api

# Configuración de página
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E40AF;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E0E7FF;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F3F4F6;
        margin-right: 20%;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Inicializa el estado de la sesión."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "token" not in st.session_state:
        st.session_state.token = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "universidad_id" not in st.session_state:
        st.session_state.universidad_id = DEFAULT_UNIVERSIDAD_ID
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = {
            "kardex": None,
            "oferta": None,
            "mapa": None
        }
    if "generated_schedules" not in st.session_state:
        st.session_state.generated_schedules = None
    if "conflictos" not in st.session_state:
        st.session_state.conflictos = []  # Bloques donde NO puede asistir
    if "bloques_oferta" not in st.session_state:
        st.session_state.bloques_oferta = None  # Bloques extraídos de la oferta
    if "pending_suggestion" not in st.session_state:
        st.session_state.pending_suggestion = None  # Sugerencia pendiente de procesar


def login_page():
    """Página de login/registro."""
    st.markdown('<h1 class="main-header">🎓 Tutor IA</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Asistente Académico Inteligente</p>", unsafe_allow_html=True)
    
    # Enlace al panel de administración
    st.markdown(
        "<p style='text-align: center; margin-bottom: 20px;'>"
        "¿Eres administrador de universidad? "
        "<a href='http://localhost:8502' target='_blank'>🏛️ Ir al Panel de Administración</a>"
        "</p>",
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="tu.email@universidad.edu")
                password = st.text_input("🔒 Contraseña", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    if email and password:
                        with st.spinner("Iniciando sesión..."):
                            result = api.login(email, password)
                        
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        elif "token" in result and "access_token" in result["token"]:
                            token = result["token"]["access_token"]
                            st.session_state.token = token
                            st.session_state.authenticated = True
                            st.session_state.user = result.get("user", {})
                            api.set_token(token)
                            st.success("✅ ¡Bienvenido!")
                            st.rerun()
                        else:
                            st.error("❌ Respuesta inesperada del servidor")
                    else:
                        st.warning("⚠️ Completa todos los campos")
        
        with tab2:
            with st.form("register_form"):
                reg_email = st.text_input("📧 Email institucional", placeholder="matricula@universidad.edu")
                reg_matricula = st.text_input("🎫 Matrícula", placeholder="Ej: 210300001")
                reg_password = st.text_input("🔒 Contraseña", type="password", key="reg_pass")
                reg_password2 = st.text_input("🔒 Confirmar contraseña", type="password")
                reg_submit = st.form_submit_button("Registrarse", use_container_width=True)
                
                if reg_submit:
                    if reg_password != reg_password2:
                        st.error("❌ Las contraseñas no coinciden")
                    elif reg_email and reg_matricula and reg_password:
                        with st.spinner("Registrando..."):
                            result = api.register(
                                email=reg_email,
                                password=reg_password,
                                matricula=reg_matricula,
                                universidad_id=st.session_state.universidad_id
                            )
                        
                        if "error" in result:
                            st.error(f"❌ {result['error']}")
                        else:
                            st.success("✅ ¡Registro exitoso! Ahora inicia sesión.")
                    else:
                        st.warning("⚠️ Completa todos los campos")
        
        # Demo mode
        st.divider()
        if st.button("🚀 Modo Demo (sin login)", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user = {"email": "demo@universidad.edu", "matricula": "DEMO001"}
            st.rerun()


def sidebar():
    """Barra lateral con navegación y estado."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=UniCaribe", use_column_width=True)
        st.divider()
        
        if st.session_state.authenticated:
            user = st.session_state.user or {"email": "demo@universidad.edu"}
            st.write(f"👤 **{user.get('email', 'Usuario')}**")
            
            st.divider()
            
            # Navegación
            page = st.radio(
                "📍 Navegación",
                ["💬 Chat", "📄 Documentos", "📅 Horarios", "ℹ️ Info Universidad"],
                label_visibility="collapsed"
            )
            
            st.divider()
            
            # Estado de documentos
            st.write("📊 **Documentos cargados:**")
            data = st.session_state.extracted_data
            st.write(f"{'✅' if data['kardex'] else '❌'} Kárdex")
            st.write(f"{'✅' if data['oferta'] else '❌'} Oferta Académica")
            st.write(f"{'✅' if data['mapa'] else '❌'} Mapa Curricular")
            
            st.divider()
            
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            
            return page
    
    return None


def chat_page():
    """Página principal de chat."""
    st.header("💬 Chat con Tutor IA")
    
    # Procesar sugerencia pendiente PRIMERO (antes de renderizar)
    if st.session_state.pending_suggestion:
        pending = st.session_state.pending_suggestion
        st.session_state.pending_suggestion = None
        
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": pending})
        
        # Obtener respuesta del agente
        result = api.chat(
            message=pending,
            universidad_id=st.session_state.universidad_id
        )
        
        if "error" in result:
            response = f"❌ Error: {result['error']}"
        else:
            response = result.get("response", "No pude procesar tu mensaje.")
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Mostrar mensajes
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🎓"):
                    st.write(msg["content"])
    
    # Input de mensaje
    if prompt := st.chat_input("Escribe tu mensaje..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        # Obtener respuesta
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("Pensando..."):
                result = api.chat(
                    message=prompt,
                    universidad_id=st.session_state.universidad_id
                )
            
            if "error" in result:
                response = f"❌ Error: {result['error']}"
            else:
                response = result.get("response", "No pude procesar tu mensaje.")
            
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Sugerencias rápidas
    st.divider()
    st.write("💡 **Sugerencias:**")
    
    suggestions = [
        "Quiero armar mi horario",
        "¿Cuál es la fecha de inscripciones?",
        "¿Cuántas materias puedo inscribir?"
    ]
    
    # Usar form para manejar los botones mejor
    for i, suggestion in enumerate(suggestions):
        if st.button(suggestion, key=f"sug_{i}"):
            # Agregar mensaje del usuario inmediatamente
            st.session_state.messages.append({"role": "user", "content": suggestion})
            
            # Mostrar mensaje del usuario
            with st.chat_message("user"):
                st.write(suggestion)
            
            # Obtener y mostrar respuesta
            with st.chat_message("assistant", avatar="🎓"):
                with st.spinner("Pensando..."):
                    result = api.chat(
                        message=suggestion,
                        universidad_id=st.session_state.universidad_id
                    )
                
                if "error" in result:
                    response = f"❌ Error: {result['error']}"
                else:
                    response = result.get("response", "No pude procesar tu mensaje.")
                
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})


def documents_page():
    """Página de carga de documentos."""
    st.header("📄 Cargar Documentos")
    
    st.info("""
    📌 **Instrucciones:**
    1. Sube tu **Kárdex** para saber qué materias puedes cursar
    2. Sube la **Oferta Académica** para ver los horarios disponibles
    3. (Opcional) Sube el **Mapa Curricular** si no está en el sistema
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Kárdex / Historial")
        kardex_file = st.file_uploader(
            "Sube tu kárdex",
            type=["jpg", "jpeg", "png", "pdf"],
            key="kardex_upload"
        )
        
        if kardex_file:
            if kardex_file.type.startswith("image"):
                st.image(kardex_file, caption="Vista previa", use_column_width=True)
            else:
                st.write(f"📄 {kardex_file.name}")
            
            if st.button("🔍 Analizar Kárdex", key="analyze_kardex"):
                with st.spinner("Analizando con IA... (puede tardar ~30s)"):
                    result = api.analyze_document(
                        file_bytes=kardex_file.getvalue(),
                        filename=kardex_file.name,
                        doc_type="kardex",
                        universidad_id=st.session_state.universidad_id
                    )
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state.extracted_data["kardex"] = result.get("data")
                    st.success("✅ Kárdex analizado correctamente")
                    with st.expander("Ver datos extraídos"):
                        st.json(result.get("data"))
    
    with col2:
        st.subheader("📋 Oferta Académica")
        oferta_file = st.file_uploader(
            "Sube la oferta del semestre",
            type=["jpg", "jpeg", "png", "pdf"],
            key="oferta_upload"
        )
        
        if oferta_file:
            if oferta_file.type.startswith("image"):
                st.image(oferta_file, caption="Vista previa", use_column_width=True)
            else:
                st.write(f"📄 {oferta_file.name}")
            
            if st.button("🔍 Analizar Oferta", key="analyze_oferta"):
                with st.spinner("Analizando con IA... (puede tardar ~30s)"):
                    result = api.analyze_document(
                        file_bytes=oferta_file.getvalue(),
                        filename=oferta_file.name,
                        doc_type="oferta",
                        universidad_id=st.session_state.universidad_id
                    )
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state.extracted_data["oferta"] = result.get("data")
                    # Extraer bloques horarios para el selector de conflictos
                    bloques_result = api.extract_bloques(result.get("data"))
                    if "error" not in bloques_result:
                        st.session_state.bloques_oferta = bloques_result
                    st.success("✅ Oferta analizada correctamente")
                    with st.expander("Ver datos extraídos"):
                        st.json(result.get("data"))
    
    # Sección para Mapa Curricular (opcional)
    st.divider()
    with st.expander("📐 Mapa Curricular (opcional - para validar prerrequisitos)"):
        st.info("""
        📌 **¿Para qué sirve?**
        
        Si subes el mapa curricular de tu carrera, el sistema verificará que 
        cumples los prerrequisitos de cada materia antes de incluirla en el horario.
        """)
        
        mapa_file = st.file_uploader(
            "Sube el mapa curricular de tu carrera",
            type=["jpg", "jpeg", "png", "pdf"],
            key="mapa_upload"
        )
        
        if mapa_file:
            if mapa_file.type.startswith("image"):
                st.image(mapa_file, caption="Vista previa", use_column_width=True)
            else:
                st.write(f"📄 {mapa_file.name}")
            
            if st.button("🔍 Analizar Mapa Curricular", key="analyze_mapa"):
                with st.spinner("Analizando con IA... (puede tardar ~30s)"):
                    result = api.analyze_document(
                        file_bytes=mapa_file.getvalue(),
                        filename=mapa_file.name,
                        doc_type="mapa",
                        universidad_id=st.session_state.universidad_id
                    )
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state.extracted_data["mapa"] = result.get("data")
                    st.success("✅ Mapa curricular analizado correctamente")
                    with st.expander("Ver datos extraídos"):
                        st.json(result.get("data"))
        
        # Mostrar si ya hay mapa cargado
        if st.session_state.extracted_data.get("mapa"):
            st.success("✅ Mapa curricular cargado - Se validarán prerrequisitos")
    
    # Resumen
    st.divider()
    data = st.session_state.extracted_data
    
    if data["kardex"] or data["oferta"]:
        st.subheader("📊 Resumen de Datos")
        
        if data["kardex"]:
            st.write("**Kárdex:**")
            kardex = data["kardex"]
            cols = st.columns(4)
            cols[0].metric("Alumno", kardex.get("alumno", {}).get("apellido_paterno", "N/A"))
            cols[1].metric("Matrícula", kardex.get("alumno", {}).get("matricula", "N/A"))
            cols[2].metric("Créditos", f"{kardex.get('creditos', {}).get('aprobados', 0)}/{kardex.get('creditos', {}).get('plan', 0)}")
            cols[3].metric("Avance", f"{kardex.get('creditos', {}).get('porcentaje_avance', 0):.1f}%")
        
        # Botón de generar horarios automáticamente
        if data["kardex"] and data["oferta"]:
            st.divider()
            st.subheader("🚀 Generar Horarios")
            st.success("✅ Tienes kárdex y oferta cargados. ¡Puedes generar horarios!")
            
            # ===== SELECTOR DE CONFLICTOS =====
            if st.session_state.bloques_oferta and st.session_state.bloques_oferta.get("bloques"):
                with st.expander("⏰ **Marcar horarios donde NO puedes asistir** (opcional)", expanded=False):
                    st.info("""
                    📌 **¿Trabajas o tienes otro compromiso?**
                    
                    Marca los bloques horarios donde **NO puedes tomar clases**.
                    Solo verás los horarios que existen en la oferta académica.
                    """)
                    
                    bloques = st.session_state.bloques_oferta.get("bloques", [])
                    dias_info = st.session_state.bloques_oferta.get("dias_con_clases", [])
                    
                    st.write(f"📆 **Días con clases:** {', '.join(dias_info)}")
                    st.write(f"🕐 **Horarios:** {st.session_state.bloques_oferta.get('hora_mas_temprana', '?')} - {st.session_state.bloques_oferta.get('hora_mas_tardia', '?')}")
                    
                    st.divider()
                    
                    # Agrupar bloques por día
                    bloques_por_dia = {}
                    for bloque in bloques:
                        dia = bloque["dia"]
                        if dia not in bloques_por_dia:
                            bloques_por_dia[dia] = []
                        bloques_por_dia[dia].append(bloque)
                    
                    # Mostrar checkboxes por día
                    conflictos_seleccionados = []
                    
                    for dia in dias_info:
                        if dia in bloques_por_dia:
                            st.write(f"**{dia}:**")
                            cols_dia = st.columns(min(len(bloques_por_dia[dia]), 4))
                            
                            for idx, bloque in enumerate(bloques_por_dia[dia]):
                                col_idx = idx % 4
                                with cols_dia[col_idx]:
                                    label = f"{bloque['hora_inicio']}-{bloque['hora_fin']}"
                                    tooltip = f"{bloque['materias_en_bloque']} materias en este horario"
                                    key = f"conflict_{dia}_{bloque['hora_inicio']}_{bloque['hora_fin']}"
                                    
                                    if st.checkbox(label, key=key, help=tooltip):
                                        conflictos_seleccionados.append({
                                            "dia": dia,
                                            "hora_inicio": bloque["hora_inicio"],
                                            "hora_fin": bloque["hora_fin"],
                                            "motivo": "Marcado por usuario"
                                        })
                    
                    # Guardar conflictos seleccionados
                    st.session_state.conflictos = conflictos_seleccionados
                    
                    if conflictos_seleccionados:
                        st.warning(f"⚠️ Marcaste **{len(conflictos_seleccionados)} bloques** como no disponibles. Se excluirán materias en esos horarios.")
            
            st.divider()
            
            # Opciones de configuración
            col1, col2, col3 = st.columns(3)
            with col1:
                max_materias = st.number_input("Máx. materias", min_value=3, max_value=8, value=5)
            with col2:
                creditos_min = st.number_input("Créditos mín.", min_value=6, max_value=30, value=12)
            with col3:
                creditos_max = st.number_input("Créditos máx.", min_value=12, max_value=36, value=24)
            
            if st.button("📅 Generar Horarios Optimizados", type="primary", use_container_width=True):
                with st.spinner("🤖 Analizando datos y generando horarios..."):
                    # Preparar conflictos para enviar
                    conflictos_enviar = st.session_state.conflictos if st.session_state.conflictos else None
                    
                    result = api.generate_from_vision(
                        kardex_data=data["kardex"],
                        oferta_data=data["oferta"],
                        mapa_data=data.get("mapa"),
                        conflictos=conflictos_enviar,
                        max_materias=max_materias,
                        creditos_minimos=creditos_min,
                        creditos_maximos=creditos_max
                    )
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state.generated_schedules = result
                    st.success(f"✅ ¡Horarios generados! Se encontraron {result.get('total_validos', 0)} opciones válidas.")
                    st.info("👉 Ve a la sección **📅 Horarios** para ver los resultados.")


def schedules_page():
    """Página de horarios generados."""
    st.header("📅 Horarios Generados")
    
    # Verificar si hay datos suficientes
    data = st.session_state.extracted_data
    
    # Si hay datos de Vision pero no horarios generados
    if data["kardex"] and data["oferta"] and not st.session_state.generated_schedules:
        st.info("✅ Tienes documentos cargados. Genera tus horarios ahora.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            max_materias = st.number_input("Máx. materias", min_value=3, max_value=8, value=5, key="sch_max")
        with col2:
            creditos_min = st.number_input("Créditos mín.", min_value=6, max_value=30, value=12, key="sch_min")
        with col3:
            creditos_max = st.number_input("Créditos máx.", min_value=12, max_value=36, value=24, key="sch_max_cred")
        
        if st.button("📅 Generar Horarios", type="primary", use_container_width=True):
            with st.spinner("🤖 Generando horarios optimizados..."):
                # Incluir conflictos si hay
                conflictos_enviar = st.session_state.conflictos if st.session_state.conflictos else None
                
                result = api.generate_from_vision(
                    kardex_data=data["kardex"],
                    oferta_data=data["oferta"],
                    mapa_data=data.get("mapa"),
                    conflictos=conflictos_enviar,
                    max_materias=max_materias,
                    creditos_minimos=creditos_min,
                    creditos_maximos=creditos_max
                )
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.session_state.generated_schedules = result
                st.rerun()
        
        st.divider()
    
    # Si no hay datos ni horarios
    elif not data["kardex"] and not data["oferta"] and not st.session_state.generated_schedules:
        st.warning("⚠️ Primero debes subir tu Kárdex y la Oferta Académica en la sección de Documentos.")
        
        if st.button("📄 Ir a Documentos"):
            st.session_state.current_page = "📄 Documentos"
            st.rerun()
        
        st.divider()
        st.info("💡 Mientras tanto, puedes ver un ejemplo con datos de prueba:")
        
        if st.button("🧪 Generar Horario de Prueba", use_container_width=True):
            with st.spinner("Generando horarios..."):
                result = api.generate_schedule_test()
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.session_state.generated_schedules = result
                st.rerun()
    
    # Mostrar horarios generados
    if st.session_state.generated_schedules:
        schedules = st.session_state.generated_schedules
        
        # Botón para regenerar
        if st.button("🔄 Regenerar Horarios", use_container_width=False):
            st.session_state.generated_schedules = None
            st.rerun()
        
        # Mostrar mensaje de éxito o advertencia
        if schedules.get("success", True):
            st.success(f"✅ {schedules.get('mensaje', 'Horarios generados')}")
        else:
            st.error(f"❌ {schedules.get('mensaje', 'No se pudieron generar horarios')}")
        
        # Mostrar advertencias (prerrequisitos faltantes, etc.)
        advertencias = schedules.get("advertencias", [])
        if advertencias:
            with st.expander(f"⚠️ Advertencias ({len(advertencias)})", expanded=True):
                for adv in advertencias:
                    st.warning(adv)
        
        horarios = schedules.get("horarios", [])
        
        for idx, horario in enumerate(horarios):
            with st.expander(f"🏆 Opción {horario['ranking']} - Score: {horario['score']:.0f}/100", expanded=(idx == 0)):
                
                # Métricas
                cols = st.columns(5)
                cols[0].metric("📚 Materias", len(horario["materias"]))
                cols[1].metric("📊 Créditos", horario["total_creditos"])
                cols[2].metric("⏰ Horas/semana", f"{horario['total_horas_semana']:.0f}")
                cols[3].metric("📆 Días con clase", horario["dias_con_clase"])
                cols[4].metric("🕐 Huecos", f"{horario['huecos_minutos']} min")
                
                st.divider()
                
                # Explicación
                st.write(f"💬 **{horario['explicacion']}**")
                
                # Pros y contras
                col1, col2 = st.columns(2)
                with col1:
                    st.write("✅ **Ventajas:**")
                    for pro in horario.get("pros", []):
                        st.write(f"  • {pro}")
                
                with col2:
                    st.write("⚠️ **Consideraciones:**")
                    for contra in horario.get("contras", []):
                        st.write(f"  • {contra}")
                
                st.divider()
                
                # Tabla de materias
                st.write("📋 **Materias incluidas:**")
                
                import pandas as pd
                
                materias_data = []
                for mat in horario["materias"]:
                    horarios_str = ", ".join([
                        f"{h['dia'][:3]} {h['hora_inicio']}-{h['hora_fin']}"
                        for h in mat["horarios"]
                    ])
                    materias_data.append({
                        "NRC": mat["nrc"],
                        "Materia": mat["nombre"],
                        "Créditos": mat["creditos"],
                        "Profesor": mat.get("profesor") or "Por definir",
                        "Horarios": horarios_str,
                        "Reprobada": "⚠️ Sí" if mat.get("es_reprobada") else ""
                    })
                
                df = pd.DataFrame(materias_data)
                st.dataframe(df, use_container_width=True, hide_index=True)


def info_page():
    """Página de información de la universidad."""
    st.header("ℹ️ Información de la Universidad")
    
    st.info("💡 Pregunta cualquier cosa sobre la universidad: fechas, trámites, reglamentos, becas...")
    
    # Inicializar faq_query si no existe
    if "faq_query" not in st.session_state:
        st.session_state.faq_query = None
    
    # Procesar FAQ pendiente
    query_to_search = None
    if st.session_state.faq_query:
        query_to_search = st.session_state.faq_query
        st.session_state.faq_query = None
    
    query = st.text_input(
        "🔍 ¿Qué quieres saber?", 
        value=query_to_search or "",
        placeholder="Ej: ¿Cuál es la fecha límite de inscripciones?"
    )
    
    # Buscar automáticamente si hay query pendiente o si el usuario presiona buscar
    should_search = query_to_search is not None or st.button("Buscar", use_container_width=True)
    
    if should_search and query:
        with st.spinner("Buscando información..."):
            result = api.ask_rag(
                query=query,
                universidad_id=st.session_state.universidad_id
            )
        
        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            st.write("### 📝 Respuesta:")
            st.write(result.get("respuesta", "No encontré información sobre eso."))
            
            if result.get("fuentes"):
                with st.expander("📚 Fuentes consultadas"):
                    for fuente in result["fuentes"]:
                        st.write(f"• **{fuente['titulo']}** ({fuente['tipo']}) - Relevancia: {fuente['relevancia']:.0%}")
    
    st.divider()
    
    # Preguntas frecuentes
    st.subheader("❓ Preguntas Frecuentes")
    
    faqs = [
        "¿Cuántas materias puedo inscribir?",
        "¿Cuáles son los requisitos para beca?",
        "¿Cuál es el horario de servicios escolares?",
        "¿Cuándo son los exámenes finales?"
    ]
    
    cols = st.columns(2)
    for i, faq in enumerate(faqs):
        with cols[i % 2]:
            if st.button(faq, key=f"faq_{i}", use_container_width=True):
                st.session_state.faq_query = faq
                st.rerun()


def main():
    """Función principal de la aplicación."""
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        page = sidebar()
        
        if page == "💬 Chat":
            chat_page()
        elif page == "📄 Documentos":
            documents_page()
        elif page == "📅 Horarios":
            schedules_page()
        elif page == "ℹ️ Info Universidad":
            info_page()
        else:
            chat_page()


if __name__ == "__main__":
    main()
