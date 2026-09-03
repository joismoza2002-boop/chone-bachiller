import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime

# Configuración de página optimizada
st.set_page_config(
    page_title="Chone Bachiller | Plataforma Educativa Oficial",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inyección CSS de Alta Gama (Modo SaaS Moderno)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
    }

    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
        background-attachment: fixed;
    }

    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Contenedor principal elegante estilo Tarjeta SaaS */
    .auth-container {
        background: #ffffff;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(226, 232, 240, 0.8);
        max-width: 480px;
        width: 100%;
        margin: 3rem auto;
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

    /* Tipografía de Títulos */
    .app-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    
    .app-subtitle {
        font-size: 0.95rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
        line-height: 1.4;
    }

    /* Botones de Acción Profesional */
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

    /* Campos de Entrada Estilizados */
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

# Inicialización robusta de Base de Datos
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
                "Opción de distractor A",
                "Opción correcta validada técnicamente",
                "Opción de distractor C",
                "Opción de distractor D",
                "B",
                f"La respuesta correcta es la B por el cumplimiento del principio analítico aplicable en {mat}."
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
    st.markdown("""
        <div class="auth-container">
            <div class="app-title">Chone Bachiller 🎓</div>
            <div class="app-subtitle">Plataforma oficial de alto rendimiento y simuladores de examen en Chone, Manabí.</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Correo electrónico personal", placeholder="tucorreo@gmail.com")
        submitted = st.form_submit_button("Ingresar a la Plataforma 🚀")
        if submitted:
            if email and "@" in email and "." in email:
                st.session_state.user_email = email.strip().lower()
                st.session_state.logged_in = True
                cursor.execute("SELECT nombres FROM users WHERE email = ?", (st.session_state.user_email,))
                row = cursor.fetchone()
                st.session_state.profile_complete = True if row and row[0] else False
                st.rerun()
            else:
                st.error("Ingresa un correo electrónico válido.")
                
    st.markdown("</div>", unsafe_allow_html=True)

def render_profile_form():
    st.markdown("""
        <div class="auth-container" style="max-width: 600px;">
            <div class="app-title">Registro de Perfil</div>
            <div class="app-subtitle">Completa tus datos oficiales para habilitar el seguimiento académico.</div>
    """, unsafe_allow_html=True)
    
    with st.form("profile_form"):
        nombres = st.text_input("Nombres y Apellidos:")
        cedula = st.text_input("Número de Cédula:")
        ciudad = st.text_input("Ciudad:", value="Chone")
        sector = st.text_input("Sector / Barrio:")
        condicion = st.selectbox("Condición:", ["Bachiller Graduado", "Estudiante en curso"])
        anio_graduacion = st.text_input("Año de Graduación:", value="2026")
        unidad_educativa = st.text_input("Unidad Educativa de origen:")
        
        submitted = st.form_submit_button("Guardar y Acceder al Sistema 🎯")
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
                st.error("Completa los campos obligatorios principales.")
    st.markdown("</div>", unsafe_allow_html=True)

def render_dashboard():
    st.markdown('<h1 style="font-size: 2.2rem; font-weight: 800; color: #0f172a; margin-bottom: 0px;">Panel Académico 📚</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: #64748b; margin-bottom: 2rem;">Estudiante: <b>{st.session_state.user_email}</b>. Selecciona un simulador oficial para comenzar.</p>', unsafe_allow_html=True)
    
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
                    <p style="color: #64748b; font-size: 0.88rem; margin-bottom: 1rem;">Simulador oficial con reactivos tipo examen y retroalimentación.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Iniciar {materia}", key=f"btn_mat_{idx}"):
                start_exam(materia)
                
    if st.session_state.user_email in ["admin@chonebachiller.edu", "admin@admin.com"]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🛠️ Panel de Control Administrativo"):
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

if not st.session_state.logged_in:
    render_auth()
elif not st.session_state.profile_complete:
    render_profile_form()
else:
    if st.session_state.current_view == "dashboard": render_dashboard()
    elif st.session_state.current_view == "exam": render_exam()
    elif st.session_state.current_view == "results": render_results()
    elif st.session_state.current_view == "admin": render_admin()
