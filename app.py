import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime

# Configuración inicial de la página a pantalla completa
st.set_page_config(
    page_title="Chone Bachiller | Plataforma Educativa Oficial",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de CSS avanzado tipo SaaS Moderno con diseño de dos columnas simétricas
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }

    /* Ocultar elementos nativos de Streamlit para un look corporativo limpio */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8fafc; }

    /* Contenedor Principal en Dos Columnas */
    .split-layout {
        display: flex;
        flex-direction: row;
        min-height: 100vh;
        width: 100%;
    }

    @media (max-width: 1024px) {
        .split-layout {
            flex-direction: column;
        }
    }

    /* Panel Izquierdo Institucional (Estilo Brand Panel) */
    .brand-panel {
        background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
        color: white;
        padding: 4rem 3rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        flex: 1;
    }

    /* Panel Derecho de Interacción */
    .login-panel {
        background: #ffffff;
        padding: 4rem 3rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        flex: 1;
    }

    .login-box {
        width: 100%;
        max-width: 420px;
    }

    /* Tarjetas de características y contenedores */
    .feature-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.85rem 1rem;
        border-radius: 12px;
        backdrop-filter: blur(5px);
    }

    .dashboard-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px -3px rgba(37, 99, 235, 0.1);
        border-color: #3b82f6;
    }

    /* Botones Profesionales */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: all 0.25s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
    }

    /* Campos de Entrada */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 12px;
        border: 1.5px solid #cbd5e1;
        padding: 0.7rem;
        background-color: #f8fafc;
        font-size: 0.95rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #2563eb;
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización segura de Base de Datos
def init_db():
    conn = sqlite3.connect("chone_bachiller.db", check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY)")
    user_columns = [
        ("nombres", "TEXT"), ("cedula", "TEXT"), ("ciudad", "TEXT"),
        ("sector", "TEXT"), ("condicion", "TEXT"), ("anio_graduacion", "TEXT"),
        ("unidad_educativa", "TEXT"), ("fecha_registro", "TIMESTAMP")
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
    for mat in materias:
        for i in range(1, 11):
            cursor.execute("""
                INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mat,
                f"Reactivo oficial #{i} para pruebas de aptitud y conocimientos en {mat}:",
                "Opción distractor A",
                "Opción correcta validada bajo normativa técnica",
                "Opción distractor C",
                "Opción distractor D",
                "B",
                f"La respuesta correcta es la B debido al fundamento analítico aplicable en {mat}."
            ))
    conn.commit()

conn = init_db()
cursor = conn.cursor()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "profile_complete" not in st.session_state: st.session_state.profile_complete = False
if "current_view" not in st.session_state: st.session_state.current_view = "dashboard"
if "exam_data" not in st.session_state: st.session_state.exam_data = None

def render_auth():
    # Estructura de dos columnas idéntica al diseño de referencia profesional
    col_brand, col_login = st.columns([1.1, 0.9], gap="medium")
    
    with col_brand:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%); color: white; padding: 4rem 3rem; border-radius: 20px; min-height: 85vh; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <span style="background: rgba(255,255,255,0.15); padding: 6px 14px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                        Cantón Chone · Manabí
                    </span>
                    <h1 style="font-size: 2.8rem; font-weight: 800; line-height: 1.2; margin-top: 1.5rem; margin-bottom: 1rem;">
                        Prepárate para tu examen de admisión universitaria
                    </h1>
                    <p style="font-size: 1.05rem; color: rgba(255,255,255,0.85); line-height: 1.5;">
                        Practica con simuladores reales, mide tu tiempo y descubre en qué debes mejorar antes del día decisivo.
                    </p>
                    
                    <div style="margin-top: 2.5rem; display: flex; flex-direction: column; gap: 1rem;">
                        <div style="display: flex; align-items: center; gap: 1rem; background: rgba(255,255,255,0.1); padding: 0.85rem 1rem; border-radius: 12px;">
                            <span style="background: rgba(255,255,255,0.2); width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold;">📋</span>
                            <span style="font-size: 0.95rem; font-weight: 500;">9 materias con banco de reactivos aleatorio</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 1rem; background: rgba(255,255,255,0.1); padding: 0.85rem 1rem; border-radius: 12px;">
                            <span style="background: rgba(255,255,255,0.2); width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold;">⏱️</span>
                            <span style="font-size: 0.95rem; font-weight: 500;">Simulacros cronometrados de alto rendimiento</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 1rem; background: rgba(255,255,255,0.1); padding: 0.85rem 1rem; border-radius: 12px;">
                            <span style="background: rgba(255,255,255,0.2); width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-weight: bold;">📖</span>
                            <span style="font-size: 0.95rem; font-weight: 500;">Retroalimentación detallada por pregunta</span>
                        </div>
                    </div>
                </div>
                <p style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 2rem;">
                    Plataforma educativa comunitaria de acceso libre · Chone Bachiller
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_login:
        st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="padding: 0 1rem;">
                <h2 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;">Inicia sesión</h2>
                <p style="font-size: 0.95rem; color: #64748b; margin-bottom: 2rem;">
                    Usa tu cuenta de Google o correo personal para ingresar. Solo necesitas hacerlo una vez.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            email_input = st.text_input("Correo electrónico personal", placeholder="tucorreo@gmail.com")
            submitted = st.form_submit_button("Continuar con Google 🚀")
            if submitted:
                if email_input and "@" in email_input and "." in email_input:
                    st.session_state.user_email = email_input.strip().lower()
                    st.session_state.logged_in = True
                    cursor.execute("SELECT nombres FROM users WHERE email = ?", (st.session_state.user_email,))
                    row = cursor.fetchone()
                    st.session_state.profile_complete = True if row and row[0] else False
                    st.rerun()
                else:
                    st.error("Introduce un correo electrónico válido.")

        # Cuenta rápida para demostración o acceso del coordinador
        if st.button("🔑 Acceso rápido Coordinación (Admin)"):
            st.session_state.user_email = "admin@chonebachiller.edu"
            st.session_state.logged_in = True
            st.session_state.profile_complete = True
            st.rerun()

        st.markdown("""
            <div style="margin-top: 2rem; display: flex; align-items: flex-start; gap: 0.75rem; background: #f1f5f9; padding: 1rem; border-radius: 12px; font-size: 0.85rem; color: #64748b;">
                <span style="font-size: 1.1rem;">🛡️</span>
                <p style="margin: 0;">Al continuar aceptas completar tu perfil académico. La cuenta con privilegios administrativos abre el panel de control de demostración.</p>
            </div>
        """, unsafe_allow_html=True)

def render_profile_form():
    st.markdown('<h1 style="font-size: 2rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem;">Registro de Perfil Académico</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748b; margin-bottom: 2rem;">Completa tus credenciales institucionales para habilitar el historial de simulacros.</p>', unsafe_allow_html=True)
    
    with st.form("profile_form"):
        nombres = st.text_input("Nombres y Apellidos Completos:")
        cedula = st.text_input("Número de Cédula de Identidad:")
        ciudad = st.text_input("Ciudad de Residencia:", value="Chone")
        sector = st.text_input("Sector / Barrio:")
        condicion = st.selectbox("Condición Actual:", ["Bachiller Graduado", "Estudiante en curso secundario"])
        anio_graduacion = st.text_input("Año Previsto de Graduación:", value="2026")
        unidad_educativa = st.text_input("Unidad Educativa de Origen:")
        
        submitted = st.form_submit_button("Guardar Perfil y Entrar al Sistema 🎯")
        if submitted:
            if nombres and cedula and unidad_educativa:
                cursor.execute("""
                    INSERT OR REPLACE INTO users (email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (st.session_state.user_email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, datetime.now()))
                conn.commit()
                st.session_state.profile_complete = True
                st.success("¡Perfil guardado correctamente!")
                st.rerun()
            else:
                st.error("Por favor, completa los campos obligatorios principales.")

def render_dashboard():
    st.markdown('<h1 style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin-bottom: 0px;">Panel Académico 📚</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #64748b; margin-bottom: 2rem;">Sesión activa: <b>{st.session_state.user_email}</b>. Selecciona una materia para iniciar el simulacro oficial.</p>', unsafe_allow_html=True)
    
    materias = [
        "Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto",
        "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"
    ]
    
    cols = st.columns(3)
    for idx, materia in enumerate(materias):
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
                <div class="dashboard-card">
                    <h3 style="font-size: 1.15rem; font-weight: 700; color: #1e3a8a; margin-bottom: 8px;">📘 {materia}</h3>
                    <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 1rem;">Simulador estandarizado con reactivos y retroalimentación teórica.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Iniciar {materia}", key=f"btn_mat_{idx}"):
                start_exam(materia)
                
    if st.session_state.user_email in ["admin@chonebachiller.edu", "admin@admin.com"]:
        st.markdown("<br><hr>", unsafe_allow_html=True)
        if st.button("🛠️ Acceder al Panel de Control Administrativo"):
            st.session_state.current_view = "admin"
            st.rerun()

def start_exam(materia):
    cursor.execute("SELECT id, materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion FROM questions WHERE materia = ?", (materia,))
    rows = cursor.fetchall()
    selected = random.sample(rows, min(15, len(rows)))
    st.session_state.exam_data = {
        "materia": materia,
        "questions": selected,
        "current_idx": 0,
        "answers": {}
    }
    st.session_state.current_view = "exam"
    st.rerun()

def render_exam():
    exam = st.session_state.exam_data
    questions = exam["questions"]
    idx = exam["current_idx"]
    q = questions[idx]
    q_id, _, q_text, op_a, op_b, op_c, op_d, _, _ = q
    
    st.markdown(f'<h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a;">Simulador: {exam["materia"]}</h1>', unsafe_allow_html=True)
    st.progress((idx + 1) / len(questions))
    st.markdown(f"**Reactivo {idx + 1} de {len(questions)}**")
    
    st.markdown(f"""
        <div class="dashboard-card" style="margin-top: 1rem;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 1rem;">{q_text}</h3>
    """, unsafe_allow_html=True)
    
    options_list = [f"A) {op_a}", f"B) {op_b}", f"C) {op_c}", f"D) {op_d}"]
    current_ans = exam["answers"].get(q_id, None)
    default_idx = {"A": 0, "B": 1, "C": 2, "D": 3}.get(current_ans, 0)
    
    chosen = st.radio("Selecciona tu respuesta:", options_list, index=default_idx, key=f"radio_{q_id}")
    exam["answers"][q_id] = chosen.split(")")[0]
    st.markdown("</div>", unsafe_allow_html=True)
    
    col_prev, col_next, col_fin = st.columns(3)
    with col_prev:
        if idx > 0 and st.button("⬅️ Anterior"):
            exam["current_idx"] -= 1
            st.rerun()
    with col_next:
        if idx < len(questions) - 1 and st.button("Siguiente ➡️"):
            exam["current_idx"] += 1
            st.rerun()
    with col_fin:
        if st.button("Finalizar 🏁", type="primary"):
            finish_exam()

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
    exam = st.session_state.exam_data
    questions = exam["questions"]
    answers = exam["answers"]
    score = sum(1 for q in questions if answers.get(q[0]) == q[7])
    total = len(questions)
    
    st.markdown('<h1 style="font-size: 2rem; font-weight: 800; color: #0f172a;">Resultados Oficiales 📊</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1: st.metric(label="Puntaje Obtenido", value=f"{score} / {total}")
    with col2: st.metric(label="Porcentaje de Éxito", value=f"{(score/total)*100:.1f}%")
    
    st.markdown("<br><h3>Revisión Detallada de Reactivos</h3>", unsafe_allow_html=True)
    for idx, q in enumerate(questions):
        q_id, _, q_text, op_a, op_b, op_c, op_d, correcta, explicacion = q
        user_ans = answers.get(q_id, "No respondida")
        is_correct = (user_ans == correcta)
        status = "✅ Correcta" if is_correct else "❌ Incorrecta"
        
        with st.expander(f"Reactivo {idx + 1} — {status}"):
            st.write(f"**Enunciado:** {q_text}")
            st.write(f"Tu respuesta: **{user_ans}** | Correcta: **{correcta}**")
            st.info(f"**Explicación teórica:** {explicacion}")
            
    if st.button("Volver al Panel Principal 🏠", type="primary"):
        st.session_state.current_view = "dashboard"
        st.session_state.exam_data = None
        st.rerun()

def render_admin():
    st.markdown('<h1 style="font-size: 2rem; font-weight: 800; color: #0f172a;">Panel Administrativo 🛠️</h1>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Base de Estudiantes", "Gestión de Banco de Preguntas"])
    
    with tab1:
        df_users = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df_users, use_container_width=True)
        if not df_users.empty:
            st.download_button("Descargar CSV de Estudiantes 📥", data=df_users.to_csv(index=False).encode('utf-8'), file_name="estudiantes.csv", mime="text/csv")
            
    with tab2:
        with st.form("add_q"):
            materia = st.selectbox("Materia:", ["Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto", "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"])
            pregunta = st.text_area("Enunciado:")
            op_a, op_b, op_c, op_d = st.text_input("A:"), st.text_input("B:"), st.text_input("C:"), st.text_input("D:")
            correcta = st.selectbox("Correcta:", ["A", "B", "C", "D"])
            explicacion = st.text_area("Explicación:")
            if st.form_submit_button("Guardar Pregunta"):
                if pregunta and op_a:
                    cursor.execute("INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion) VALUES (?,?,?,?,?,?,?,?)",
                                   (materia, pregunta, op_a, op_b, op_c, op_d, correcta, explicacion))
                    conn.commit()
                    st.success("Pregunta agregada con éxito.")
                else:
                    st.error("Completa los campos obligatorios.")
                    
    if st.button("⬅️ Volver"):
        st.session_state.current_view = "dashboard"
        st.rerun()

# Enrutador principal de pantallas
if not st.session_state.logged_in:
    render_auth()
elif not st.session_state.profile_complete:
    render_profile_form()
else:
    if st.session_state.current_view == "dashboard": render_dashboard()
    elif st.session_state.current_view == "exam": render_exam()
    elif st.session_state.current_view == "results": render_results()
    elif st.session_state.current_view == "admin": render_admin()
