import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime

# Configuración de página con diseño ancho y limpio
st.set_page_config(
    page_title="Chone Bachiller | Plataforma Educativa Oficial",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS avanzado para diseño UI/UX Prémium
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: #f4f6f9;
    }

    .stApp {
        background-color: #f4f6f9;
    }

    /* Contenedores tipo Tarjeta Estilizada */
    .cb-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 24px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .cb-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }

    /* Tipografía y Encabezados */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.025em;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }

    /* Botones Profesionales */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: 600;
        padding: 0.65rem 1rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3);
    }

    /* Campos de Entrada de Texto */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        padding: 0.6rem;
        background-color: #ffffff;
    }
    
    /* Ocultar elementos predeterminados de Streamlit para limpieza visual */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Inicialización segura de Base de Datos y control de esquemas
def init_db():
    conn = sqlite3.connect("chone_bachiller.db", check_same_thread=False)
    cursor = conn.cursor()
    
    # Tabla Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY
        )
    """)
    # Migración dinámica segura de columnas para usuarios
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

    # Tabla Preguntas
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

    # Tabla Resultados
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
    
    # Semilla de preguntas iniciales si está vacío
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        seed_default_questions(cursor, conn)
        
    return conn

def seed_default_questions(cursor, conn):
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
                f"Pregunta oficial #{i} evaluada en simuladores de ingreso para {mat}:",
                "Opción A incorrecta o distractor",
                "Opción B correcta analizada bajo norma técnica",
                "Opción C incorrecta",
                "Opción D incorrecta",
                "B",
                f"La respuesta correcta es la B porque fundamenta de manera lógica el núcleo de estudio en {mat}."
            ))
    conn.commit()

conn = init_db()
cursor = conn.cursor()

# Control de Session State
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "profile_complete" not in st.session_state: st.session_state.profile_complete = False
if "current_view" not in st.session_state: st.session_state.current_view = "dashboard"
if "exam_data" not in st.session_state: st.session_state.exam_data = None

# Vistas de la Aplicación
def render_auth():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown('<div class="cb-card">', unsafe_allow_html=True)
        st.markdown('<p class="main-title" style="text-align: center;">Chone Bachiller 🎓</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title" style="text-align: center;">Portal académico de preparación y simuladores de alto rendimiento.</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("Correo electrónico institucional o personal", placeholder="estudiante@correo.com")
            submitted = st.form_submit_button("Acceder a la plataforma 🚀")
            if submitted:
                if email and "@" in email and "." in email:
                    st.session_state.user_email = email.strip().lower()
                    st.session_state.logged_in = True
                    
                    cursor.execute("SELECT nombres FROM users WHERE email = ?", (st.session_state.user_email,))
                    row = cursor.fetchone()
                    st.session_state.profile_complete = True if row and row[0] else False
                    st.rerun()
                else:
                    st.error("Por favor, introduce un correo electrónico válido.")
        st.markdown('</div>', unsafe_allow_html=True)

def render_profile_form():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<p class="main-title">Registro de Perfil Académico</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-title">Completa tus credenciales para habilitar el historial en los simuladores.</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="cb-card">', unsafe_allow_html=True)
        with st.form("profile_form"):
            nombres = st.text_input("Nombres y Apellidos Completos:")
            cedula = st.text_input("Número de Cédula de Identidad:")
            ciudad = st.text_input("Ciudad de Residencia:", value="Chone")
            sector = st.text_input("Sector / Barrio:")
            condicion = st.selectbox("Condición Actual:", ["Bachiller Graduado", "Estudiante en curso secundario"])
            anio_graduacion = st.text_input("Año Previsto o de Graduación:", value="2026")
            unidad_educativa = st.text_input("Unidad Educativa de Origen:")
            
            submitted = st.form_submit_button("Guardar Perfil y Continuar 🎯")
            if submitted:
                if nombres and cedula and unidad_educativa:
                    cursor.execute("""
                        INSERT OR REPLACE INTO users (email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, fecha_registro)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (st.session_state.user_email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, datetime.now()))
                    conn.commit()
                    st.session_state.profile_complete = True
                    st.success("¡Perfil registrado con éxito!")
                    st.rerun()
                else:
                    st.error("Por favor, completa los campos obligatorios principales.")
        st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard():
    st.markdown('<p class="main-title">Panel Académico Principal 📚</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-title">Sesión activa: <b>{st.session_state.user_email}</b>. Selecciona un bloque de evaluación oficial.</p>', unsafe_allow_html=True)
    
    materias = [
        "Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto",
        "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"
    ]
    
    cols = st.columns(3)
    for idx, materia in enumerate(materias):
        col = cols[idx % 3]
        with col:
            st.markdown(f"""
                <div class="cb-card">
                    <h3>📘 {materia}</h3>
                    <p style="color: #64748b; font-size: 0.9rem; min-height: 40px;">Simulador estandarizado con reactivos y retroalimentación teórica.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Iniciar {materia}", key=f"mat_{idx}"):
                start_exam(materia)
                
    if st.session_state.user_email in ["admin@chonebachiller.edu", "admin@admin.com"]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🛠️ Acceder al Panel de Control Administrativo"):
            st.session_state.current_view = "admin"
            st.rerun()

def start_exam(materia):
    cursor.execute("SELECT id, materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion FROM questions WHERE materia = ?", (materia,))
    rows = cursor.fetchall()
    if not rows:
        st.warning("No se encontraron reactivos para esta materia.")
        return
    selected_questions = random.sample(rows, min(15, len(rows)))
    st.session_state.exam_data = {
        "materia": materia,
        "questions": selected_questions,
        "current_idx": 0,
        "answers": {}
    }
    st.session_state.current_view = "exam"
    st.rerun()

def render_exam():
    exam = st.session_state.exam_data
    if not exam:
        st.session_state.current_view = "dashboard"
        st.rerun()
        
    questions = exam["questions"]
    idx = exam["current_idx"]
    q = questions[idx]
    q_id, _, q_text, op_a, op_b, op_c, op_d, _, _ = q
    
    st.markdown(f'<p class="main-title">Simulador: {exam["materia"]}</p>', unsafe_allow_html=True)
    st.progress((idx + 1) / len(questions))
    st.markdown(f"**Pregunta {idx + 1} de {len(questions)}**")
    
    st.markdown(f'<div class="cb-card">', unsafe_allow_html=True)
    st.markdown(f"### {q_text}")
    
    options = {"A": op_a, "B": op_b, "C": op_c, "D": op_d}
    options_list = [f"A) {op_a}", f"B) {op_b}", f"C) {op_c}", f"D) {op_d}"]
    
    current_ans = exam["answers"].get(q_id, None)
    default_idx = 0
    if current_ans in ["A", "B", "C", "D"]:
        default_idx = {"A": 0, "B": 1, "C": 2, "D": 3}[current_ans]
        
    selected = st.radio("Elige una opción:", options_list, index=default_idx, key=f"radio_{q_id}")
    exam["answers"][q_id] = selected.split(")")[0]
    st.markdown('</div>', unsafe_allow_html=True)
    
    col_prev, col_next, col_fin = st.columns(3)
    with col_prev:
        if idx > 0 and st.button("⬅️ Pregunta Anterior"):
            exam["current_idx"] -= 1
            st.rerun()
    with col_next:
        if idx < len(questions) - 1 and st.button("Siguiente Pregunta ➡️"):
            exam["current_idx"] += 1
            st.rerun()
    with col_fin:
        if st.button("Finalizar y Calificar 🏁", type="primary"):
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
    
    st.markdown('<p class="main-title">Resultados y Retroalimentación 📊</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Aciertos Totales", value=f"{score} / {total}")
    with col2:
        st.metric(label="Calificación Equivalente", value=f"{(score/total)*100:.1f}%")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Desglose detallado de reactivos")
    
    for idx, q in enumerate(questions):
        q_id, _, q_text, op_a, op_b, op_c, op_d, correcta, explicacion = q
        user_ans = answers.get(q_id, "No respondida")
        is_correct = (user_ans == correcta)
        
        status_text = "✅ Respuesta Correcta" if is_correct else "❌ Respuesta Incorrecta"
        with st.expander(f"Reactivo {idx + 1} — {status_text}"):
            st.write(f"**Pregunta:** {q_text}")
            st.write(f"Tu selección: **{user_ans}** | Opción correcta: **{correcta}**")
            st.info(f"**Explicación pedagógica:** {explicacion}")
            
    if st.button("Regresar al Dashboard Principal 🏠", type="primary"):
        st.session_state.current_view = "dashboard"
        st.session_state.exam_data = None
        st.rerun()

def render_admin():
    st.markdown('<p class="main-title">Panel Administrativo Global 🛠️</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Control de registros estudiantiles y mantenimiento del banco de preguntas.</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Base de Estudiantes", "Gestión de Preguntas"])
    
    with tab1:
        df_users = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df_users, use_container_width=True)
        if not df_users.empty:
            st.download_button("Descargar Base de Estudiantes (CSV) 📥", data=df_users.to_csv(index=False).encode('utf-8'), file_name="estudiantes_chone_bachiller.csv", mime="text/csv")
            
    with tab2:
        with st.form("add_q_form"):
            materia = st.selectbox("Materia:", ["Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto", "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"])
            pregunta = st.text_area("Enunciado de la Pregunta:")
            op_a = st.text_input("Opción A:")
            op_b = st.text_input("Opción B:")
            op_c = st.text_input("Opción C:")
            op_d = st.text_input("Opción D:")
            correcta = st.selectbox("Opción Correcta:", ["A", "B", "C", "D"])
            explicacion = st.text_area("Explicación de la respuesta:")
            
            submit = st.form_submit_button("Guardar Reactivo 💾")
            if submit:
                if pregunta and op_a and op_b:
                    cursor.execute("""
                        INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (materia, pregunta, op_a, op_b, op_c, op_d, correcta, explicacion))
                    conn.commit()
                    st.success("¡Pregunta agregada exitosamente al sistema!")
                else:
                    st.error("Rellene los campos principales de la pregunta.")
                    
    if st.button("⬅️ Volver al Panel"):
        st.session_state.current_view = "dashboard"
        st.rerun()

# Flujo de enrutamiento principal
if not st.session_state.logged_in:
    render_auth()
elif not st.session_state.profile_complete:
    render_profile_form()
else:
    if st.session_state.current_view == "dashboard":
        render_dashboard()
    elif st.session_state.current_view == "exam":
        render_exam()
    elif st.session_state.current_view == "results":
        render_results()
    elif st.session_state.current_view == "admin":
        render_admin()
