import streamlit as st
import pandas as pd
from datetime import datetime
import random
import json

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="ORASIC COMMUNITY", layout="wide", page_icon="🏘️")

COLORS = {
    "bg": "#080A0F", "violet": "#A78BFA", "cyan": "#22D3EE", 
    "pink": "#F472B6", "orange": "#FB923C", "text": "#FFFFFF"
}

st.markdown(f"""
<style>
    .main {{ background-color: {COLORS['bg']}; color: {COLORS['text']}; }}
    .stButton > button {{ background-color: {COLORS['violet']}; color: white; border-radius: 8px; border: none; padding: 10px 20px; font-weight: bold; }}
    .card {{ background-color: #1F2937; padding: 15px; border-radius: 10px; border-left: 4px solid {COLORS['cyan']}; margin-bottom: 10px; }}
    h1, h2, h3 {{ color: {COLORS['text']}; }}
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS EVOLUTIVA (AI-READY) ---
def init_db():
    if 'db' not in st.session_state:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.db = {
            "users": [
                {"id": 1, "name": "Fernando Perez", "role": "admin", "email": "admin@orasic.com", "pass": "123", 
                 "permissions": ["dashboard", "censo", "vehiculos", "incidencias", "garitas", "camaras"]},
                {"id": 2, "name": "Juan Vecino", "role": "vecino", "email": "juan@vecino.com", "pass": "123", "lote": "154",
                 "permissions": ["inicio", "visitas", "reportar", "directorio"]}
            ],
            "viviendas": [
                {"lote": "154", "propietario": "Juan Vecino", "estado": "Ocupada", "cuota": 0, 
                 "camera_id": "CAM-154-FRONT", "stream_url": "", "created_at": now},
                {"lote": "155", "propietario": "Maria Lopez", "estado": "Ocupada", "cuota": 150, 
                 "camera_id": None, "stream_url": "", "created_at": now},
                {"lote": "156", "propietario": "Carlos Ruiz", "estado": "Vacía", "cuota": 0, 
                 "camera_id": None, "stream_url": "", "created_at": now}
            ],
            "vehiculos": [
                {"placa": "ABC-123", "marca": "Toyota", "lote": "154", "authorized": True, "created_at": now},
                {"placa": "XYZ-987", "marca": "Kia", "lote": "155", "authorized": True, "created_at": now}
            ],
            "incidencias": [
                {"id": 101, "tipo": "Iluminación", "desc": "Luz apagada Calle Conchán", "estado": "Nueva", 
                 "lote": "154", "fecha": now, "ai_category": "mantenimiento_iluminacion", "priority": "alta"},
                {"id": 102, "tipo": "Seguridad", "desc": "Puerta garita dañada", "estado": "En Proceso", 
                 "lote": "Garita 1", "fecha": now, "ai_category": "seguridad_infraestructura", "priority": "critica"}
            ],
            "visitas": [
                {"id": 501, "nombre": "Técnico Internet", "lote_destino": "154", "hora": "11:30", 
                 "estado": "Pendiente", "qr": "QR-TECH-001", "created_at": now}
            ],
            # TABLA DE EVENTOS PARA IA (FASE 6)
            "events": [
                {"event_type": "system_init", "timestamp": now, "metadata": {"version": "1.0", "phase": "1"}}
            ]
        }

init_db()

# --- UTILIDAD PARA REGISTRO DE EVENTOS (AI-READY) ---
def log_event(event_type, metadata=None):
    """Registra cada acción para análisis futuro con IA"""
    event = {
        "event_type": event_type,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metadata": metadata or {}
    }
    st.session_state.db["events"].append(event)

# --- LOGIN CON VALIDACIÓN DE PERMISOS ---
def login_screen():
    st.title("️ ORASIC COMMUNITY")
    st.subheader("La Encantada de Villa - Acceso Seguro")
    
    email = st.text_input("Usuario / Email")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar al Sistema"):
        user = next((u for u in st.session_state.db["users"] if u["email"] == email and u["pass"] == password), None)
        if user:
            st.session_state.current_user = user
            log_event("user_login", {"user_id": user["id"], "role": user["role"]})
            st.rerun()
        else:
            st.error("Credenciales no válidas.")
            log_event("login_failed", {"email": email})

# --- APP ADMIN ---
def admin_dashboard():
    st.sidebar.title("🛡️ ORASIC ADMIN")
    st.sidebar.write(f"Operador: {st.session_state.current_user['name']}")
    
    menu = st.sidebar.radio("Navegación", [
        "📊 Dashboard", "🏠 Censo Viviendas", "🚗 Vehículos", 
        "🚨 Incidencias", "👮 Garitas", "📹 Cámaras (F2)"
    ])

    if menu == "📊 Dashboard":
        st.header("Panel de Control General")
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Viviendas Totales", len(st.session_state.db["viviendas"]))
        with c2: st.metric("Vehículos Registrados", len(st.session_state.db["vehiculos"]))
        with c3: st.metric("Incidencias Abiertas", len([i for i in st.session_state.db["incidencias"] if i['estado'] != "Resuelta"]))
        with c4: st.metric("Visitas Hoy", len(st.session_state.db["visitas"]))

        st.subheader("⚠️ Alertas Recientes")
        for inc in st.session_state.db["incidencias"]:
            if inc['estado'] == "Nueva":
                st.warning(f"**#{inc['id']}** ({inc['tipo']}): {inc['desc']} - Lote {inc['lote']}")

    elif menu == " Censo Viviendas":
        st.header("Censo de la Urbanización")
        # Usamos st.table en lugar de dataframe para evitar error pyarrow
        df = pd.DataFrame(st.session_state.db["viviendas"])
        st.table(df)
        
        st.divider()
        st.subheader("Registrar Nueva Vivienda")
        col1, col2 = st.columns(2)
        with col1: lote = st.text_input("Número de Lote")
        with col2: prop = st.text_input("Nombre del Propietario")
        
        if st.button("Guardar Vivienda"):
            if lote and prop:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.db["viviendas"].append({
                    "lote": lote, "propietario": prop, "estado": "Ocupada", "cuota": 0,
                    "camera_id": None, "stream_url": "", "created_at": now
                })
                log_event("vivienda_created", {"lote": lote, "propietario": prop})
                st.success(f"Vivienda {lote} registrada exitosamente.")
                st.rerun()
            else:
                st.error("Completa ambos campos.")

    elif menu == "🚗 Vehículos":
        st.header("Registro de Vehículos")
        df_v = pd.DataFrame(st.session_state.db["vehiculos"])
        st.table(df_v)

    elif menu == " Incidencias":
        st.header("Gestión de Incidencias")
        for inc in st.session_state.db["incidencias"]:
            with st.expander(f"Incidencia #{inc['id']} - {inc['estado']}"):
                st.write(f"**Tipo:** {inc['tipo']}")
                st.write(f"**Descripción:** {inc['desc']}")
                st.write(f"**Ubicación:** {inc['lote']}")
                st.write(f"**Categoría IA:** {inc.get('ai_category', 'N/A')}")
                if inc['estado'] != "Resuelta":
                    if st.button(f"Marcar como Resuelta", key=f"res_{inc['id']}"):
                        inc['estado'] = "Resuelta"
                        log_event("incidencia_resolved", {"id": inc['id'], "tipo": inc['tipo']})
                        st.success("Incidencia cerrada.")
                        st.rerun()

    elif menu == "👮 Garitas":
        st.header("Control de Accesos - Garita Principal")
        st.subheader("Visitas Esperadas")
        if not st.session_state.db["visitas"]:
            st.info("No hay visitas pendientes.")
            
        for v in st.session_state.db["visitas"]:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1: st.write(f"👤 **{v['nombre']}** → Lote {v['lote_destino']}")
            with col2: st.write(f"⏰ {v['hora']}")
            with col3: 
                if v['estado'] == "Pendiente":
                    if st.button("✅ Permitir", key=f"acc_{v['id']}"):
                        v['estado'] = "Dentro"
                        log_event("access_granted", {"visit_id": v['id'], "lote": v['lote_destino']})
                        st.rerun()
                else:
                    st.success(v['estado'])

    elif menu == " Cámaras (F2)":
        st.header("Monitoreo de Cámaras (Fase 2 - Preparación)")
        st.info("Esta sección está preparada para integrar streams RTSP en la Fase 2.")
        
        # Mostrar cámaras configuradas
        cams = [v for v in st.session_state.db["viviendas"] if v.get('camera_id')]
        if cams:
            for cam in cams:
                st.markdown(f"""
                <div class="card">
                    <h4>📹 {cam['camera_id']} - Lote {cam['lote']}</h4>
                    <p>Estado: {'🟢 Activa' if cam.get('stream_url') else '⚪ Pendiente de configuración'}</p>
                    <p>URL Stream: {cam.get('stream_url', 'No configurado')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("No hay cámaras configuradas aún. Agregue camera_id en el censo de viviendas.")

# --- APP VECINO ---
def villa_alerta_app():
    user = st.session_state.current_user
    lote = user.get('lote', 'N/A')
    
    st.sidebar.title("🚨 VILLA ALERTA")
    st.sidebar.write(f"Vecino: {user['name']}")
    st.sidebar.write(f"Lote: {lote}")
    
    menu = st.sidebar.radio("Menú Vecino", ["🏠 Inicio", "👥 Mis Visitas", "📢 Reportar", "📞 Directorio"])

    if menu == "🏠 Inicio":
        st.header(f"Bienvenido a La Encantada, Lote {lote}")
        
        if st.button("🔴 SOS / EMERGENCIA INMEDIATA"):
            st.error("¡ALERTA ENVIADA A LA GARITA PRINCIPAL!")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_inc = {
                "id": random.randint(200, 999), 
                "tipo": "EMERGENCIA SOS", 
                "desc": f"SOS activado desde App por Lote {lote}", 
                "estado": "Nueva", 
                "lote": lote, 
                "fecha": now,
                "ai_category": "emergencia_sos",
                "priority": "critica"
            }
            st.session_state.db["incidencias"].insert(0, new_inc)
            log_event("sos_triggered", {"lote": lote, "user_id": user['id']})
            st.balloons()

        st.subheader("Mis Datos Rápidos")
        my_cars = [c for c in st.session_state.db["vehiculos"] if c['lote'] == lote]
        if my_cars:
            for car in my_cars:
                st.info(f"🚗 {car['placa']} - {car['marca']}")
        else:
            st.write("No tienes vehículos registrados.")

    elif menu == "👥 Mis Visitas":
        st.header("Autorizar Visita")
        with st.form("visit_form"):
            name = st.text_input("Nombre del Visitante")
            time = st.time_input("Hora estimada")
            if st.form_submit_button("Generar QR de Acceso"):
                qr_id = f"QR-{random.randint(1000, 9999)}"
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.db["visitas"].append({
                    "id": len(st.session_state.db["visitas"]) + 1, 
                    "nombre": name, 
                    "lote_destino": lote, 
                    "hora": time.strftime("%H:%M"), 
                    "estado": "Pendiente", 
                    "qr": qr_id,
                    "created_at": now
                })
                log_event("visit_registered", {"lote": lote, "visitor": name})
                st.success(f"Visita registrada. Código QR: {qr_id}")
                st.rerun()

    elif menu == "📢 Reportar":
        st.header("Reportar Problema")
        tipo = st.selectbox("Categoría", ["Iluminación", "Limpieza", "Seguridad", "Áreas Verdes", "Ruidos"])
        desc = st.text_area("Detalles del problema")
        
        if st.button("Enviar Reporte"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ai_cat = f"reporte_vecino_{tipo.lower().replace(' ', '_')}"
            st.session_state.db["incidencias"].append({
                "id": random.randint(200, 999), 
                "tipo": tipo, 
                "desc": desc, 
                "estado": "Nueva", 
                "lote": lote, 
                "fecha": now,
                "ai_category": ai_cat,
                "priority": "media"
            })
            log_event("report_created", {"lote": lote, "tipo": tipo})
            st.success("Reporte enviado a administración.")
            st.rerun()

    elif menu == "📞 Directorio":
        st.header("Servicios Recomendados")
        servicios = [
            {"nombre": "Jardinería Verde", "tel": "999-888-777"},
            {"nombre": "Seguridad Privada XYZ", "tel": "999-111-222"}
        ]
        for s in servicios:
            st.markdown(f"**{s['nombre']}** - 📞 {s['tel']}")

# --- EJECUCIÓN PRINCIPAL ---
if 'current_user' not in st.session_state:
    login_screen()
else:
    # Validación estricta de roles
    role = st.session_state.current_user['role']
    if role == 'admin':
        admin_dashboard()
    elif role == 'vecino':
        villa_alerta_app()
    else:
        st.error("Rol no reconocido. Contacte al administrador.")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar Sesión"):
        log_event("user_logout", {"user_id": st.session_state.current_user['id']})
        del st.session_state.current_user
        st.rerun()