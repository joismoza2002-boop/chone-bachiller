import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime
from streamlit_google_auth import Authenticate

st.set_page_config(
    page_title="Chone Bachiller | Plataforma Educativa Oficial",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #0f172a;
        background-color: #f8fafc;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8fafc; }

    .dashboard-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        border: 1px solid #e2e8f0;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 1rem;
        box-sizing: border-box;
        transition: all 0.25s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -3px rgba(37, 99, 235, 0.08);
        border-color: #2563eb;
    }

    .stButton>button {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        padding: 0.6rem 1rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
    }

    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px;
        border: 1.5px solid #cbd5e1;
        padding: 0.65rem;
        background-color: #ffffff;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect("chone_bachiller.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY)")
    user_columns = [
        ("nombres", "TEXT"), ("cedula", "TEXT"), ("ciudad", "TEXT"),
        ("sector", "TEXT"), ("condicion", "TEXT"), ("anio_graduacion", "TEXT"),
        ("unidad_educativa", "TEXT"), ("carrera_deseada", "TEXT"), ("fecha_registro", "TIMESTAMP")
    ]
    for col, ctype in user_columns:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {ctype}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia TEXT,
            pregunta TEXT,
            opcion_a TEXT,
            opcion_b TEXT,
            opcion_c TEXT,
            opcion_d TEXT,
            correcta TEXT,
            explicacion TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            materia TEXT,
            puntaje INTEGER,
            total INTEGER,
            fecha TIMESTAMP,
            FOREIGN KEY(email) REFERENCES users(email)
        )
    """)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        seed_questions(cursor, conn)
    return conn

def seed_questions(cursor, conn):
    materias = [
        "Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto",
        "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"
    ]
    
    banco_real = [
        ("Razonamiento Numérico", "¿Qué número continúa en la siguiente serie: 2, 6, 12, 20, 30, ...?", "40", "42", "44", "48", "B", "La diferencia entre términos aumenta de 2 en 2: +4, +6, +8, +10, por tanto el siguiente incremento es +12 (30 + 12 = 42)."),
        ("Razonamiento Numérico", "Si un artículo cuesta $80 y tiene un descuento del 20%, ¿cuál es su precio final?", "$60", "$64", "$68", "$70", "B", "El 20% de 80 es 16. Restando 80 - 16 se obtiene 64."),
        ("Razonamiento Verbal", "Elija el sinónimo de la palabra: 'Benevolencia'", "Severidad", "Indulgencia", "Indiferencia", "Austeridad", "B", "La benevolencia implica comprensión y tolerancia, siendo sinónimo de indulgencia."),
        ("Razonamiento Verbal", "Complete la analogía: Guante es a mano como zapato es a:", "Pie", "Suela", "Cordón", "Media", "A", "El guante cubre la mano de forma directa, tal como el zapato cubre el pie."),
        ("Razonamiento Abstracto", "Identifique la figura que completa la matriz lógica basándose en la rotación horaria de 90 grados.", "Figura en cruz superior", "Figura rotada a 90° derecha", "Figura invertida verticalmente", "Figura simétrica opuesta", "B", "Al aplicar una rotación constante de 90 grados en sentido horario, el elemento adopta la posición B."),
        ("Biología", "¿Cuál es la organela celular encargada de la respiración celular y producción de ATP?", "Ribosoma", "Mitocondria", "Aparato de Golgi", "Lisosoma", "B", "Las mitocondrias son las centrales energéticas de la célula eucariota donde se produce ATP."),
        ("Química", "Indique el símbolo químico correspondiente al elemento Oro:", "Ag", "Au", "Pb", "Fe", "B", "El símbolo químico 'Au' proviene del latín aurum."),
        ("Física", "Un móvil viaja a una velocidad constante de 20 m/s durante 5 segundos. ¿Qué distancia recorre?", "50 metros", "80 metros", "100 metros", "120 metros", "C", "La distancia se calcula multiplicando velocidad por tiempo: 20 m/s * 5 s = 100 metros."),
        ("Matemáticas", "Resuelva la ecuación de primer grado: 3x - 5 = 16", "x = 5", "x = 7", "x = 9", "x = 11", "B", "Despejando x: 3x = 16 + 5 => 3x = 21 => x = 7."),
        ("Lengua y Literatura", "Identifique la oración que presenta correcta ortografía y acentuación:", "El examen sera dificil para todos.", "Él examen será difícil para todos.", "El examen será difícil para todos.", "El examen sera dificil para todos.", "C", "Lleva tilde en 'será' por ser aguda terminada en vocal, y en 'difícil' por ser grave."),
        ("Historia", "¿En qué año se firmó la Primera Constitución del Ecuador en la ciudad de Riobamba?", "1822", "1830", "1845", "1860", "B", "La primera Constitución del Estado del Ecuador se emitió el 23 de septiembre de 1830 en Riobamba.")
    ]
    
    for mat in materias:
        match_base = [q for q in banco_real if q[0] == mat]
        for i in range(1, 31):
            if match_base:
                base = match_base[(i - 1) % len(match_base)]
                cursor.execute("""
                    INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (mat, f"Reactivo oficial #{i} - {base[1]}", base[2], base[3], base[4], base[5], base[6], base[7]))
            else:
                cursor.execute("""
                    INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (mat, f"Reactivo oficial de evaluación # {i} para el dominio de {mat}.", "Opción analítica A", "Opción correcta validada B", "Opción distractor C", "Opción distractor D", "B", f"Fundamento teórico correcto validado para {mat}."))
    conn.commit()

conn = init_db()
cursor = conn.cursor()

# ==========================================
# CONFIGURACIÓN DE GOOGLE OAUTH Y ADMINS
# ==========================================
ADMIN_EMAILS = ["admin@chonebachiller.edu", "Joismoza2002@gmail.com"]

import json

# Generamos el archivo json localmente en memoria al arrancar la app
creds_data = {
    "web": {
        "client_id": st.secrets["client_id"],
        "project_id": st.secrets.get("project_id", "chone-507511"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": st.secrets["client_secret"],
        "redirect_uris": [st.secrets["redirect_uri"]]
    }
}

with open("google_credentials.json", "w") as f:
    json.dump(creds_data, f)

authenticator = Authenticate(
    secret_credentials_path="google_credentials.json",
    cookie_name=st.secrets["cookie_name"],
    cookie_key=st.secrets["cookie_key"],
    redirect_uri=st.secrets["redirect_uri"],
    cookie_expiry_days=30
)


if "profile_complete" not in st.session_state: st.session_state.profile_complete = False
if "current_view" not in st.session_state: st.session_state.current_view = "dashboard"
if "exam_data" not in st.session_state: st.session_state.exam_data = None

def render_auth():
    col_brand, col_login = st.columns([1.1, 0.9], gap="large")
    with col_brand:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color: white; padding: 3.5rem 3rem; border-radius: 20px; min-height: 82vh; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <span style="background: rgba(255,255,255,0.15); padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #ffffff;">
                        Cantón Chone - Manabí
                    </span>
                    <h1 style="font-size: 2.6rem; font-weight: 800; line-height: 1.2; margin-top: 1.5rem; margin-bottom: 1rem; color: white;">
                        Prepárate para tu examen de admisión universitaria
                    </h1>
                    <p style="font-size: 1.05rem; color: #e2e8f0; line-height: 1.5;">
                        Practica con simuladores oficiales de 30 preguntas y 30 minutos, mide tu tiempo y asegura tu cupo.
                    </p>
                </div>
                <p style="font-size: 0.8rem; color: #cbd5e1; margin-top: 2rem;">
                    Plataforma educativa comunitaria - Chone Bachiller
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_login:
        st.markdown("<div style='height: 2.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("## Inicia sesión")
        st.markdown("Usa tu cuenta institucional o personal de Google para ingresar al sistema.")
        
        # Botón oficial de Google OAuth
        authenticator.login()

def render_profile_form():
    st.markdown("## Registro de Perfil Académico")
    st.markdown("Completa tus credenciales institucionales para habilitar el historial de simulacros.")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            nombres = st.text_input("Nombres y Apellidos Completos:")
            cedula = st.text_input("Número de Cédula de Identidad:")
            ciudad = st.text_input("Ciudad de Residencia:", value="Chone")
            sector = st.text_input("Sector / Barrio:")
        with col2:
            condicion = st.selectbox("Condición Actual:", ["BACHILLER GRADUADO", "BACHILLER EN FORMACIÓN"])
            anio_graduacion = st.text_input("Año Previsto de Graduación:", value="2026")
            unidad_educativa = st.text_input("Unidad Educativa de Origen:")
            carrera_deseada = st.text_input("Carrera Deseada:")
        
        submitted = st.form_submit_button("Guardar Perfil y Entrar al Sistema")
        if submitted:
            if nombres and cedula and unidad_educativa:
                cursor.execute("""
                    INSERT OR REPLACE INTO users (email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, carrera_deseada, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (st.session_state.user_email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, carrera_deseada, datetime.now()))
                conn.commit()
                st.session_state.profile_complete = True
                st.success("Perfil guardado correctamente.")
                st.rerun()
            else:
                st.error("Por favor, completa los campos obligatorios principales.")

def render_top_navbar():
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); padding: 0.8rem 1.2rem; border-radius: 12px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <span style="color: white; font-weight: 800; font-size: 1rem;">Chone Bachiller</span>
            <span style="color: #ffffff; font-size: 0.85rem;">{st.session_state.user_email}</span>
        </div>
    """, unsafe_allow_html=True)
    
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
    with col_nav1:
        if st.button("Simuladores", use_container_width=True, key="nav_sim"):
            st.session_state.current_view = "dashboard"
            st.session_state.exam_data = None
            st.rerun()
    with col_nav2:
        if st.button("Mi Perfil", use_container_width=True, key="nav_perfil"):
            st.session_state.current_view = "profile_edit"
            st.rerun()
    with col_nav3:
        if st.session_state.user_email in ADMIN_EMAILS:
            if st.button("Panel Admin", use_container_width=True, key="nav_admin"):
                st.session_state.current_view = "admin"
                st.rerun()
        else:
            st.markdown("")
    with col_nav4:
        if st.button("Cerrar Sesión", use_container_width=True, key="nav_logout"):
            authenticator.logout()
            st.rerun()
    st.markdown("<hr style='border-color: #cbd5e1; margin: 1rem 0 1.5rem 0;'>", unsafe_allow_html=True)

def render_profile_edit():
    render_top_navbar()
    st.markdown("## Gestión de Perfil y Datos")
    st.markdown("Actualiza tu información personal e institucional registrada en la plataforma.")
    
    cursor.execute("SELECT nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, carrera_deseada FROM users WHERE email = ?", (st.session_state.user_email,))
    user = cursor.fetchone()
    
    if user:
        nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, carrera_deseada = user
    else:
        nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, carrera_deseada = "", "", "Chone", "", "BACHILLER GRADUADO", "2026", "", ""

    with st.form("edit_profile_form"):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            new_nombres = st.text_input("Nombres y Apellidos:", value=nombres)
            new_cedula = st.text_input("Número de Cédula:", value=cedula)
            new_ciudad = st.text_input("Ciudad:", value=ciudad)
            new_sector = st.text_input("Sector / Barrio:", value=sector)
        with col2:
            cond_list = ["BACHILLER GRADUADO", "BACHILLER EN FORMACIÓN"]
            idx_cond = cond_list.index(condicion) if condicion in cond_list else 0
            new_condicion = st.selectbox("Condición Actual:", cond_list, index=idx_cond)
            new_anio = st.text_input("Año de Graduación:", value=anio_graduacion)
            new_colegio = st.text_input("Unidad Educativa:", value=unidad_educativa)
            new_carrera = st.text_input("Carrera Deseada:", value=carrera_deseada if carrera_deseada else "")
        
        submitted = st.form_submit_button("Actualizar Datos del Perfil")
        if submitted:
            cursor.execute("""
                UPDATE users SET nombres=?, cedula=?, ciudad=?, sector=?, condicion=?, anio_graduacion=?, unidad_educativa=?, carrera_deseada=?
                WHERE email=?
            """, (new_nombres, new_cedula, new_ciudad, new_sector, new_condicion, new_anio, new_colegio, new_carrera, st.session_state.user_email))
            conn.commit()
            st.success("Perfil actualizado con éxito.")

def render_dashboard():
    render_top_navbar()
    st.markdown("## Panel Académico")
    st.markdown("Selecciona una materia para iniciar tu simulacro oficial (30 preguntas en 30 minutos).")
    
    materias = [
        "Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto",
        "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"
    ]
    
    for i in range(0, len(materias), 3):
        cols = st.columns(3, gap="medium")
        for j in range(3):
            if i + j < len(materias):
                materia = materias[i + j]
                with cols[j]:
                    st.markdown(f"""
                        <div class='dashboard-card'>
                            <div>
                                <h3 style='font-size: 1.05rem; font-weight: 700; color: #1e3a8a; margin-bottom: 8px;'>{materia}</h3>
                                <p style='color: #64748b; font-size: 0.85rem; line-height: 1.4; margin-bottom: 0;'>Simulador oficial con 30 reactivos estandarizados y retroalimentación teórica.</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Iniciar {materia}", key=f"btn_mat_{i+j}", use_container_width=True):
                        start_exam(materia)

def start_exam(materia):
    cursor.execute("SELECT id, materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion FROM questions WHERE materia = ?", (materia,))
    rows = cursor.fetchall()
    
    if not rows:
        for k in range(1, 31):
            cursor.execute("""
                INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (materia, f"Reactivo oficial dinámico #{k} para {materia}", "Opción A", "Opción B", "Opción C", "Opción D", "B", f"Explicación teórica de respaldo para {materia}."))
        conn.commit()
        cursor.execute("SELECT id, materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion FROM questions WHERE materia = ?", (materia,))
        rows = cursor.fetchall()

    selected = random.sample(rows, min(30, len(rows)))
    
    st.session_state.exam_data = {
        "materia": materia,
        "questions": selected,
        "current_idx": 0,
        "answers": {},
        "start_time": datetime.now()
    }
    st.session_state.current_view = "exam"
    st.rerun()

@st.fragment(run_every=1)
def render_exam():
    render_top_navbar()
    exam = st.session_state.exam_data
    if not exam or "questions" not in exam or not exam["questions"]:
        st.error("Error al cargar las preguntas del simulacro. Vuelve al panel principal.")
        if st.button("Volver al Dashboard"):
            st.session_state.current_view = "dashboard"
            st.rerun()
        return

    questions = exam["questions"]
    
    elapsed_seconds = (datetime.now() - exam["start_time"]).total_seconds()
    remaining_seconds = max(0, 1800 - int(elapsed_seconds))
    
    if remaining_seconds <= 0:
        st.warning("El tiempo del simulacro ha finalizado.")
        finish_exam()
        return

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    timer_html = f"""
        <div style="background: #0f172a; color: #ffffff; padding: 1rem 1.5rem; border-radius: 12px; font-weight: 700; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15); margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 1.05rem;">Simulacro Oficial - {exam['materia']}</span>
            <span style="font-size: 1.25rem; color: #38bdf8; font-family: monospace;">{time_str}</span>
        </div>
    """
    
    st.markdown(timer_html, unsafe_allow_html=True)
    
    idx = exam["current_idx"]
    if idx >= len(questions):
        idx = len(questions) - 1
        exam["current_idx"] = idx

    q = questions[idx]
    q_id, _, q_text, op_a, op_b, op_c, op_d, _, _ = q
    
    st.progress((idx + 1) / len(questions))
    st.markdown(f"**Reactivo {idx + 1} de {len(questions)}**")
    
    st.markdown(f"""
        <div class="dashboard-card" style="height: auto; min-height: 120px; margin-top: 0.8rem; margin-bottom: 1.2rem; width: 100%;">
            <h3 style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin-bottom: 0;">{q_text}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    options_list = [f"A) {op_a}", f"B) {op_b}", f"C) {op_c}", f"D) {op_d}"]
    current_ans = exam["answers"].get(q_id, None)
    default_idx = {"A": 0, "B": 1, "C": 2, "D": 3}.get(current_ans, 0)
    
    chosen = st.radio("Selecciona tu respuesta:", options_list, index=default_idx, key=f"radio_{q_id}")
    exam["answers"][q_id] = chosen.split(")")[0]
    
    col_prev, col_next, col_fin = st.columns(3)
    with col_prev:
        if idx > 0 and st.button("Anterior", use_container_width=True):
            exam["current_idx"] -= 1
            st.rerun()
    with col_next:
        if idx < len(questions) - 1 and st.button("Siguiente", use_container_width=True):
            exam["current_idx"] += 1
            st.rerun()
    with col_fin:
        answered_count = len(exam["answers"])
        total_q = len(questions)
        if answered_count == total_q:
            if st.button("Finalizar y Enviar", type="primary", use_container_width=True):
                finish_exam()
        else:
            st.markdown(f"<p style='color: #64748b; font-size: 0.8rem; text-align: center; margin-top: 10px;'>Faltan {total_q - answered_count} por responder</p>", unsafe_allow_html=True)

def finish_exam():
    exam = st.session_state.exam_data
    questions = exam["questions"]
    answers = exam["answers"]
    score = sum(1 for q in questions if answers.get(q[0]) == q[7])
    total = len(questions)
    
    cursor.execute("""
        INSERT INTO results (email, materia, puntaje, total, fecha)
        VALUES (?, ?, ?, ?, ?)
    """, (st.session_state.user_email, exam["materia"], score, total, datetime.now()))
    conn.commit()
    
    st.session_state.current_view = "results"
    st.rerun()

def render_results():
    render_top_navbar()
    exam = st.session_state.exam_data
    questions = exam["questions"]
    answers = exam["answers"]
    score = sum(1 for q in questions if answers.get(q[0]) == q[7])
    total = len(questions)
    
    st.markdown("## Resultados Oficiales")
    col1, col2 = st.columns(2)
    with col1: st.metric(label="Puntaje Obtenido", value=f"{score} / {total}")
    with col2: st.metric(label="Porcentaje de Éxito", value=f"{(score/total)*100:.1f}%")
    
    st.markdown("<br><h3>Revisión Detallada de Reactivos</h3>", unsafe_allow_html=True)
    for idx, q in enumerate(questions):
        q_id, _, q_text, op_a, op_b, op_c, op_d, correcta, explicacion = q
        user_ans = answers.get(q_id, "No respondida")
        is_correct = (user_ans == correcta)
        status = "Correcta" if is_correct else "Incorrecta"
        
        with st.expander(f"Reactivo {idx + 1} - {status}"):
            st.write(f"**Enunciado:** {q_text}")
            st.write(f"Tu respuesta: **{user_ans}** | Correcta: **{correcta}**")
            st.info(f"**Explicación teórica:** {explicacion}")
            
    if st.button("Volver al Panel Principal", type="primary"):
        st.session_state.current_view = "dashboard"
        st.session_state.exam_data = None
        st.rerun()

def render_admin():
    render_top_navbar()
    st.markdown("## ⚙️ Panel de Administración y Control")
    st.markdown("Supervisa el rendimiento general, gestiona el banco de reactivos y revisa a los aspirantes registrados.")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM results")
    total_exams = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_questions = cursor.fetchone()[0]

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Estudiantes Registrados", total_users)
    with col_m2:
        st.metric("Simulacros Realizados", total_exams)
    with col_m3:
        st.metric("Banco de Preguntas", total_questions)

    st.markdown("<hr style='border-color: #cbd5e1; margin: 1.5rem 0;'>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👥 Base de Estudiantes", "📊 Historial de Resultados", "📝 Gestión de Preguntas"])

    with tab1:
        st.markdown("### Estudiantes Registrados en el Sistema")
        df_users = pd.read_sql_query("SELECT * FROM users", conn)
        if not df_users.empty:
            st.dataframe(df_users, use_container_width=True)
            csv_users = df_users.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Descargar Base de Estudiantes (CSV)", 
                data=csv_users, 
                file_name="estudiantes_chone_bachiller.csv", 
                mime="text/csv"
            )
        else:
            st.info("Aún no hay estudiantes registrados.")

    with tab2:
        st.markdown("### Registro de Evaluaciones de Simulacros")
        df_results = pd.read_sql_query("SELECT * FROM results ORDER BY fecha DESC", conn)
        if not df_results.empty:
            st.dataframe(df_results, use_container_width=True)
            csv_results = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Descargar Historial de Resultados (CSV)", 
                data=csv_results, 
                file_name="resultados_simulacros.csv", 
                mime="text/csv"
            )
        else:
            st.info("Aún no se han completado simulacros.")

    with tab3:
        st.markdown("### Gestión del Banco de Reactivos")
        
        sub_tab1, sub_tab2 = st.tabs(["➕ Agregar Pregunta", "🗑️ Ver / Eliminar Preguntas"])
        
        with sub_tab1:
            with st.form("add_question_form"):
                materia = st.selectbox("Materia / Dominio:", [
                    "Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto",
                    "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"
                ])
                pregunta = st.text_area("Enunciado de la Pregunta:")
                col_op1, col_op2 = st.columns(2)
                with col_op1:
                    op_a = st.text_input("Opción A:")
                    op_b = st.text_input("Opción B:")
                with col_op2:
                    op_c = st.text_input("Opción C:")
                    op_d = st.text_input("Opción D:")
                
                correcta = st.selectbox("Opción Correcta:", ["A", "B", "C", "D"])
                explicacion = st.text_area("Explicación Teórica de la Respuesta:")
                
                submitted_q = st.form_submit_button("Guardar Nueva Pregunta")
                if submitted_q:
                    if pregunta and op_a and op_b and op_c and op_d:
                        cursor.execute("""
                            INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (materia, pregunta, op_a, op_b, op_c, op_d, correcta, explicacion))
                        conn.commit()
                        st.success("¡Pregunta agregada con éxito al banco oficial!")
                    else:
                        st.error("Por favor, completa todos los campos obligatorios.")

        with sub_tab2:
            materias_disponibles = [
                "Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto",
                "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"
            ]
            filtro_materia = st.selectbox("Filtrar por materia para revisar o eliminar:", materias_disponibles, key="filter_mat_admin")
            
            cursor.execute("SELECT id, pregunta, correcta FROM questions WHERE materia = ?", (filtro_materia,))
            preguntas_filtro = cursor.fetchall()
            
            if preguntas_filtro:
                st.markdown(f"**Total de reactivos en {filtro_materia}:** {len(preguntas_filtro)}")
                for q_item in preguntas_filtro:
                    q_id, q_text, q_corr = q_item
                    col_q_info, col_q_btn = st.columns([4, 1])
                    with col_q_info:
                        st.markdown(f"**ID {q_id}** (Correcta: {q_corr}): {q_text}")
                    with col_q_btn:
                        if st.button("Eliminar", key=f"del_q_{q_id}", use_container_width=True):
                            cursor.execute("DELETE FROM questions WHERE id = ?", (q_id,))
                            conn.commit()
                            st.success(f"Pregunta {q_id} eliminada.")
                            st.rerun()
            else:
                st.info(f"No hay preguntas registradas para {filtro_materia}.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Volver al Panel Principal", type="primary"):
        st.session_state.current_view = "dashboard"
        st.rerun()

# ==========================================
# GESTIÓN DE ESTADOS DE SESIÓN (GOOGLE AUTH)
# ==========================================
if not st.session_state.get("connected", False):
    render_auth()
else:
    # Extraer el email autenticado por Google
    user_info = st.session_state.get("user_info", {})
    st.session_state.user_email = user_info.get("email", "").lower()
    
    # Verificar si el usuario ya tiene perfil registrado en SQLite
    cursor.execute("SELECT nombres FROM users WHERE email = ?", (st.session_state.user_email,))
    row = cursor.fetchone()
    st.session_state.profile_complete = True if row and row[0] else False

    if not st.session_state.profile_complete:
        render_profile_form()
    else:
        if st.session_state.current_view == "dashboard":
            render_dashboard()
        elif st.session_state.current_view == "profile_edit":
            render_profile_edit()
        elif st.session_state.current_view == "exam":
            render_exam()
        elif st.session_state.current_view == "results":
            render_results()
        elif st.session_state.current_view == "admin":
            # Validación RBAC estricta para administradores
            if st.session_state.user_email in ADMIN_EMAILS:
                render_admin()
            else:
                st.error("No tienes permisos de administrador para acceder a esta sección.")
                if st.button("Volver al Dashboard"):
                    st.session_state.current_view = "dashboard"
                    st.rerun()
