import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(
    page_title="Chone Bachiller | Plataforma Educativa",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Estilos CSS Profesionales (Modo Elegante y Moderno)
st.markdown("""
    <style>
    /* Estilos globales y tipografía */
    .main {
        background-color: #f8fafc;
    }
    .stApp {
        background: #f8fafc;
    }
    
    /* Encabezados y títulos */
    h1, h2, h3 {
        color: #0f172a;
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 2.25rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 2rem;
    }

    /* Tarjetas contenedoras elegantes */
    .custom-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    /* Botones personalizados */
    .stButton>button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
    }

    /* Campos de entrada */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        padding: 0.65rem;
        background-color: #ffffff;
    }
    
    /* Métricas y resultados */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #1e3a8a;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión a Base de Datos SQLite
conn = sqlite3.connect('chone_bachiller.db', check_same_thread=False)
cursor = conn.cursor()

# Inicializar tablas si no existen
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        nombre TEXT,
        colegio TEXT,
        telefono TEXT
    )
''')

cursor.execute('''
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
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        materia TEXT,
        puntaje INTEGER,
        total INTEGER,
        fecha TEXT
    )
''')
conn.commit()

# Insertar preguntas de ejemplo si la tabla está vacía
cursor.execute('SELECT COUNT(*) FROM questions')
if cursor.fetchone()[0] == 0:
    preguntas_iniciales = [
        ("Razonamiento Numérico", "¿Cuál es el 20% de 300?", "30", "60", "90", "120", "B", "El 20% de 300 se calcula multiplicando 300 por 0.20, lo que da como resultado 60."),
        ("Razonamiento Verbal", "Elija el sinónimo de la palabra 'Efímero':", "Duradero", "Pasajero", "Eterno", "Constante", "B", "Efímero significa que dura poco tiempo, por lo que su sinónimo es pasajero."),
        ("Razonamiento Abstracto", "Identifique la figura que continúa la serie (Simulado):", "Opción A", "Opción B", "Opción C", "Opción D", "A", "Patrón lógico secuencial de rotación horaria de 90 grados.")
    ]
    cursor.executemany("INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", preguntas_iniciales)
    conn.commit()

# Control de Estado en Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'current_view' not in st.session_state:
    st.session_state.current_view = "dashboard"
if 'exam_data' not in st.session_state:
    st.session_state.exam_data = None

# Pantalla de Autenticación / Registro
def render_auth():
    st.markdown('<p class="main-title">Chone Bachiller 🎓</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Plataforma oficial de preparación académica y simuladores de examen en Chone, Manabí.</p>', unsafe_allow_html=True)
    
    st.markdown("### Acceso a la Plataforma")
    st.markdown("Ingresa con tu correo electrónico para registrar tu progreso y simuladores.")
    
    with st.form("auth_form"):
        email_input = st.text_input("Correo electrónico", placeholder="tucorreo@gmail.com")
        submit_auth = st.form_submit_button("Ingresar a la plataforma 🚀")
        
        if submit_auth:
            if email_input and "@" in email_input:
                st.session_state.user_email = email_input.strip().lower()
                
                # Verificar si el usuario ya existe en la base de datos
                cursor.execute("SELECT * FROM users WHERE email = ?", (st.session_state.user_email,))
                user_record = cursor.fetchone()
                
                if user_record or st.session_state.user_email in ["admin@chonebachiller.edu", "admin@admin.com"]:
                    st.session_state.logged_in = True
                    st.session_state.current_view = "dashboard"
                else:
                    st.session_state.logged_in = True
                    st.session_state.current_view = "profile_setup"
                st.rerun()
            else:
                st.error("Por favor, ingresa un correo electrónico válido.")

# Registro de Perfil Inicial
def render_profile_form():
    st.markdown('<p class="main-title">Completa tu Perfil 📝</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Queremos conocerte mejor para personalizar tu experiencia académica.</p>', unsafe_allow_html=True)
    
    with st.form("profile_form"):
        nombre = st.text_input("Nombre completo")
        colegio = st.text_input("Colegio de procedencia en Chone")
        telefono = st.text_input("Número de celular / WhatsApp")
        submit_profile = st.form_submit_button("Guardar y Continuar 🎯")
        
        if submit_profile:
            if nombre and colegio:
                cursor.execute("INSERT OR REPLACE INTO users (email, nombre, colegio, telefono) VALUES (?, ?, ?, ?)",
                               (st.session_state.user_email, nombre, colegio, telefono))
                conn.commit()
                st.session_state.current_view = "dashboard"
                st.rerun()
            else:
                st.error("Por favor llena al menos tu nombre y colegio.")

# Panel Principal (Dashboard)
def render_dashboard():
    # Detectar si es administrador
    is_admin = st.session_state.user_email in ["admin@chonebachiller.edu", "admin@admin.com"]
    
    st.markdown(f'<p class="main-title">Panel Académico 📚</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">Bienvenido, estudiante. Selecciona un simulador para evaluar tus conocimientos.</p>', unsafe_allow_html=True)
    
    if is_admin:
        if st.button("🛠️ Ir al Panel de Administración"):
            st.session_state.current_view = "admin"
            st.rerun()
        st.divider()

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔢 Numérico")
        st.write("Prueba tus habilidades en resolución de problemas matemáticos y cálculo.")
        if st.button("Iniciar Numérico"):
            start_exam("Razonamiento Numérico")
            
    with col2:
        st.markdown("### 📖 Verbal")
        st.write("Evalúa comprensión lectora, sinónimos, antónimos y analogías.")
        if st.button("Iniciar Verbal"):
            start_exam("Razonamiento Verbal")
            
    with col3:
        st.markdown("### 🧩 Abstracto")
        st.write("Practica con series gráficas y patrones espaciales y lógicos.")
        if st.button("Iniciar Abstracto"):
            start_exam("Razonamiento Abstracto")

def start_exam(materia):
    cursor.execute("SELECT id, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion FROM questions WHERE materia = ?", (materia,))
    qs = cursor.fetchall()
    if not qs:
        st.warning(f"No hay preguntas cargadas todavía para {materia}.")
        return
    st.session_state.exam_data = {
        "materia": materia,
        "questions": qs,
        "current_idx": 0,
        "answers": {}
    }
    st.session_state.current_view = "exam"
    st.rerun()

# Pantalla de Examen Activo
def render_exam():
    exam = st.session_state.exam_data
    if not exam:
        st.session_state.current_view = "dashboard"
        st.rerun()
        
    questions = exam["questions"]
    idx = exam["current_idx"]
    q = questions[idx]
    q_id, q_text, op_a, op_b, op_c, op_d, correcta, explicacion = q
    
    st.markdown(f"### Simulador: {exam['materia']}")
    st.progress((idx + 1) / len(questions))
    st.markdown(f"**Pregunta {idx + 1} de {len(questions)}**")
    
    st.markdown(f"#### {q_text}")
    
    opciones = {"A": op_a, "B": op_b, "C": op_c, "D": op_d}
    opciones_lista = [f"A) {op_a}", f"B) {op_b}", f"C) {op_c}", f"D) {op_d}"]
    
    current_ans = exam["answers"].get(q_id, None)
    default_idx = 0
    if current_ans:
        mapping = {"A": 0, "B": 1, "C": 2, "D": 3}
        default_idx = mapping.get(current_ans, 0)
        
    chosen = st.radio("Selecciona tu respuesta:", opciones_lista, index=default_idx)
    selected_letter = chosen.split(")")[0]
    exam["answers"][q_id] = selected_letter
    
    st.write("")
    col_prev, col_next, col_fin = st.columns([1, 1, 1])
    
    with col_prev:
        if idx > 0 and st.button("⬅️ Anterior"):
            exam["current_idx"] -= 1
            st.rerun()
            
    with col_next:
        if idx < len(questions) - 1:
            if st.button("Siguiente ➡️"):
                exam["current_idx"] += 1
                st.rerun()
                
    with col_fin:
        if idx == len(questions) - 1:
            if st.button("Finalizar Examen 🏁", type="primary"):
                finish_exam()

def finish_exam():
    exam = st.session_state.exam_data
    questions = exam["questions"]
    answers = exam["answers"]
    
    score = sum(1 for q in questions if answers.get(q[0]) == q[6])
    total = len(questions)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    cursor.execute("INSERT INTO results (email, materia, puntaje, total, fecha) VALUES (?, ?, ?, ?, ?)",
                   (st.session_state.user_email, exam["materia"], score, total, fecha))
    conn.commit()
    
    st.session_state.current_view = "results"
    st.rerun()

# Pantalla de Resultados
def render_results():
    exam = st.session_state.exam_data
    questions = exam["questions"]
    answers = exam["answers"]
    
    score = sum(1 for q in questions if answers.get(q[0]) == q[6])
    total = len(questions)
    
    st.markdown('<p class="main-title">Resultados del Simulador 📊</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Puntaje Final", value=f"{score} / {total}")
    with col2:
        calificacion = (score / total) * 100 if total > 0 else 0
        st.metric(label="Efectividad", value=f"{calificacion:.1f}%")
        
    st.divider()
    st.subheader("Reporte de Revisión Detallada")
    
    for idx, q in enumerate(questions):
        q_id, q_text, op_a, op_b, op_c, op_d, correcta, explicacion = q
        user_ans = answers.get(q_id, "No respondida")
        is_correct = (user_ans == correcta)
        
        status_icon = "✅ Correcta" if is_correct else "❌ Incorrecta"
        with st.expander(f"Pregunta {idx + 1} - {status_icon}"):
            st.write(f"**Pregunta:** {q_text}")
            st.write(f"**Tu respuesta:** {user_ans}")
            st.write(f"**Respuesta correcta:** {correcta}")
            st.info(f"**Explicación:** {explicacion}")
            
    if st.button("Volver al Dashboard principal 🏠", type="primary"):
        st.session_state.current_view = "dashboard"
        st.session_state.exam_data = None
        st.rerun()

# Panel de Administración
def render_admin():
    st.markdown('<p class="main-title">Panel de Administración 🛠️</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Gestión de estudiantes y banco de preguntas.</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Estudiantes Registrados", "Agregar Preguntas"])
    
    with tab1:
        df_users = pd.read_sql_query("SELECT * FROM users", conn)
        st.dataframe(df_users, use_container_width=True)
        if not df_users.empty:
            st.download_button("Descargar Reporte CSV 📥", data=df_users.to_csv(index=False).encode('utf-8'), file_name="estudiantes_chone.csv", mime="text/csv")
            
    with tab2:
        with st.form("add_question_form"):
            materia = st.selectbox("Materia", ["Razonamiento Numérico", "Razonamiento Verbal", "Razonamiento Abstracto"])
            pregunta_txt = st.text_area("Texto de la Pregunta")
            op_a = st.text_input("Opción A")
            op_b = st.text_input("Opción B")
            op_c = st.text_input("Opción C")
            op_d = st.text_input("Opción D")
            correcta = st.selectbox("Respuesta Correcta", ["A", "B", "C", "D"])
            explicacion = st.text_input("Explicación de la respuesta")
            
            submit_q = st.form_submit_button("Guardar Pregunta 💾")
            if submit_q:
                if pregunta_txt and op_a and op_b:
                    cursor.execute("INSERT INTO questions (materia, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, correcta, explicacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                   (materia, pregunta_txt, op_a, op_b, op_c, op_d, correcta, explicacion))
                    conn.commit()
                    st.success("¡Pregunta guardada con éxito en la base de datos!")
                else:
                    st.error("Por favor completa los campos principales de la pregunta.")
                    
    if st.button("⬅️ Volver al Dashboard"):
        st.session_state.current_view = "dashboard"
        st.rerun()

# Enrutador principal de pantallas
if not st.session_state.logged_in:
    render_auth()
elif st.session_state.current_view == "profile_setup":
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

