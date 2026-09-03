import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime

st.set_page_config(
    page_title="Chone Bachiller | Plataforma Educativa",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_db():
    conn = sqlite3.connect("chone_bachiller.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            nombres TEXT,
            cedula TEXT,
            ciudad TEXT,
            sector TEXT,
            condicion TEXT,
            anio_graduacion TEXT,
            unidad_educativa TEXT,
            fecha_registro TIMESTAMP
        )
    """)
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
        for i in range(1, 36):
            q_text = f"Pregunta mock #{i} de {mat}: ¿Cuál es el concepto o solución correcta para este reactivo?"
            cursor.execute("""
                INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mat, q_text, "Opción A incorrecta", "Opción B correcta", "Opción C incorrecta", "Opción D incorrecta", "B",
                f"La respuesta correcta es la B porque en {mat} se aplica el principio fundamental analizado en este reactivo."
            ))
    conn.commit()

conn = init_db()
cursor = conn.cursor()

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 700; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem; }
    .card { background-color: #FFFFFF; border: 1px solid #E5E7EB; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "profile_complete" not in st.session_state: st.session_state.profile_complete = False
if "current_view" not in st.session_state: st.session_state.current_view = "dashboard"
if "exam_active" not in st.session_state: st.session_state.exam_active = False
if "exam_data" not in st.session_state: st.session_state.exam_data = None

def render_auth():
    st.markdown("<div class='main-header'>Chone Bachiller 🎓</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Plataforma oficial de preparación académica y simuladores de examen en Chone, Manabí.</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Iniciar Sesión")
        st.write("Accede con tu correo para registrar tu progreso.")
        google_email = st.text_input("Correo electrónico:", placeholder="tucorreo@gmail.com")
        if st.button("Continuar 🚀", use_container_width=True):
            if google_email and "@" in google_email:
                st.session_state.user_email = google_email.strip().lower()
                st.session_state.logged_in = True
                cursor.execute("SELECT nombres FROM users WHERE email = ?", (st.session_state.user_email,))
                user_row = cursor.fetchone()
                st.session_state.profile_complete = True if user_row else False
                st.rerun()
            else:
                st.error("Por favor, ingresa un correo electrónico válido.")
        st.markdown("</div>", unsafe_allow_html=True)

def render_profile_form():
    st.markdown("<div class='main-header'>Completar Perfil de Estudiante</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Es obligatorio completar esta información para acceder a los simuladores.</div>", unsafe_allow_html=True)
    with st.form("profile_form"):
        nombres = st.text_input("Nombres completos:")
        cedula = st.text_input("Número de Cédula de Identidad:")
        ciudad = st.text_input("Ciudad:", value="Chone")
        sector = st.text_input("Sector / Barrio donde vive:")
        condicion = st.selectbox("Condición académica:", ["Bachiller Graduado", "Estudiante en formación"])
        anio_graduacion = st.text_input("Año de graduación (si aplica):", value="2026")
        unidad_educativa = st.text_input("Unidad Educativa de origen:")
        submitted = st.form_submit_button("Guardar Perfil y Acceder 📝", use_container_width=True)
        if submitted:
            if nombres and cedula and ciudad and sector and unidad_educativa:
                cursor.execute("""
                    INSERT OR REPLACE INTO users (email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, fecha_registro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (st.session_state.user_email, nombres, cedula, ciudad, sector, condicion, anio_graduacion, unidad_educativa, datetime.now()))
                conn.commit()
                st.session_state.profile_complete = True
                st.success("¡Perfil guardado con éxito!")
                st.rerun()
            else:
                st.error("Por favor, completa todos los campos obligatorios.")

def render_dashboard():
    st.markdown("<div class='main-header'>Panel de Control - Chone Bachiller</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>Bienvenido, {st.session_state.user_email}. Selecciona una materia para iniciar tu simulador oficial.</div>", unsafe_allow_html=True)
    materias = [
        "Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto",
        "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"
    ]
    cols = st.columns(3)
    for idx, materia in enumerate(materias):
        col = cols[idx % 3]
        with col:
            st.markdown(f"<div class='card'><h4>📚 {materia}</h4><p>Simulador con 30 preguntas aleatorias.</p></div>", unsafe_allow_html=True)
            if st.button(f"Iniciar {materia}", key=f"btn_{idx}", use_container_width=True):
                start_exam(materia)
    if st.session_state.user_email in ["admin@chonebachiller.edu", "admin@admin.com"]:
        st.divider()
        if st.button("🛠️ Panel de Administrador"):
            st.session_state.current_view = "admin"
            st.rerun()

def start_exam(materia):
    cursor.execute("SELECT id, materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion FROM questions WHERE materia = ?", (materia,))
    rows = cursor.fetchall()
    selected_questions = random.sample(rows, min(30, len(rows)))
    st.session_state.exam_data = {
        "materia": materia,
        "questions": selected_questions,
        "current_idx": 0,
        "answers": {},
        "start_time": datetime.now()
    }
    st.session_state.current_view = "exam"
    st.rerun()

def render_exam():
    exam = st.session_state.exam_data
    materia = exam["materia"]
    questions = exam["questions"]
    idx = exam["current_idx"]
    st.markdown(f"<div class='main-header'>Simulador: {materia}</div>", unsafe_allow_html=True)
    col_prog, col_time = st.columns([2, 1])
    with col_prog:
        st.progress((idx + 1) / len(questions))
        st.write(f"Pregunta **{idx + 1}** de **{len(questions)}**")
    with col_time:
        st.markdown("⏱️ **Tiempo:** 30:00 min")
    st.divider()
    q = questions[idx]
    q_id, _, q_text, op_a, op_b, op_c, op_d, _, _ = q
    st.subheader(f"Pregunta {idx + 1}:")
    st.write(q_text)
    options = {"A": op_a, "B": op_b, "C": op_c, "D": op_d}
    current_answer = exam["answers"].get(q_id, None)
    current_index_sel = list(options.keys()).index(current_answer) if current_answer in options else None
    selected_option = st.radio("Selecciona una opción:", options=list(options.keys()), format_func=lambda x: f"{x}) {options[x]}", index=current_index_sel, key=f"q_radio_{q_id}")
    exam["answers"][q_id] = selected_option
    st.divider()
    col_prev, col_next, col_fin = st.columns(3)
    with col_prev:
        if idx > 0 and st.button("⬅️ Anterior", use_container_width=True):
            exam["current_idx"] -= 1
            st.rerun()
    with col_next:
        if idx < len(questions) - 1 and st.button("Siguiente ➡️", use_container_width=True):
            exam["current_idx"] += 1
            st.rerun()
    with col_fin:
        if st.button("Finalizar 🏁", type="primary", use_container_width=True):
            finish_exam()

def finish_exam():
    exam = st.session_state.exam_data
    questions = exam["questions"]
    answers = exam["answers"]
    score = sum(1 for q in questions if answers.get(q[0]) == q[7])
    cursor.execute("INSERT INTO results (email, materia, puntaje, total, fecha) VALUES (?, ?, ?, ?, ?)", (st.session_state.user_email, exam["materia"], score, len(questions), datetime.now()))
    conn.commit()
    st.session_state.current_view = "results"
    st.rerun()

def render_results():
    exam = st.session_state.exam_data
    questions = exam["questions"]
    answers = exam["answers"]
    score = sum(1 for q in questions if answers.get(q[0]) == q[7])
    total = len(questions)
    st.markdown("<div class='main-header'>Resultados 📊</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.metric(label="Puntaje Final", value=f"{score} / {total}")
    with col2: st.metric(label="Calificación", value=f"{(score / total) * 100:.1f}%")
    st.divider()
    st.subheader("Reporte de revisión")
    for idx, q in enumerate(questions):
        q_id, _, q_text, op_a, op_b, op_c, op_d, correcta, explicacion = q
        user_ans = answers.get(q_id, "No respondida")
        options = {"A": op_a, "B": op_b, "C": op_c, "D": op_d}
        is_correct = (user_ans == correcta)
        with st.expander(f"Pregunta {idx + 1} - {'Correcta ✅' if is_correct else 'Incorrecta ❌'}"):
            st.write(f"**Pregunta:** {q_text}")
            st.write(f"Tu respuesta: **{user_ans}**")
            st.write(f"Respuesta correcta: **{correcta}**")
            st.info(f"**Explicación:** {explicacion}")
    if st.button("Volver al Dashboard 🏠", type="primary"):
        st.session_state.current_view = "dashboard"
        st.session_state.exam_active = False
        st.session_state.exam_data = None
        st.rerun()

def render_admin():
    st.markdown("<div class='main-header'>Panel de Administración 🛠️</div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Estudiantes", "Preguntas"])
    with tab1:
        df_users = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df_users, use_container_width=True)
        st.download_button("Descargar CSV 📥", data=df_users.to_csv(index=False).encode('utf-8'), file_name='estudiantes.csv', mime='text/csv')
    with tab2:
        with st.form("add_q"):
            materia_q = st.selectbox("Materia:", ["Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto", "Biología", "Química", "Física", "Matemáticas", "Lengua y Literatura", "Historia"])
            pregunta_txt = st.text_area("Pregunta:")
            op_a, op_b, op_c, op_d = st.text_input("A:"), st.text_input("B:"), st.text_input("C:"), st.text_input("D:")
            correcta = st.selectbox("Correcta:", ["A", "B", "C", "D"])
            explicacion = st.text_input("Explicación:")
            if st.form_submit_button("Guardar"):
                cursor.execute("INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion) VALUES (?,?,?,?,?,?,?,?)", (materia_q, pregunta_txt, op_a, op_b, op_c, op_d, correcta, explicacion))
                conn.commit()
                st.success("Guardado")
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
