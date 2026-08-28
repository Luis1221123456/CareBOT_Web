import base64
import streamlit as st
from config import html, HERO_IMAGE, LOGO_SVG, WELCOME_MESSAGES, PALETTE
from database import save_messages_to_db, save_patient_data, obtener_pacientes_del_cuidador, crear_nuevo_perfil, registrar_usuario, verificar_usuario
from cerebro import consultar_claude
from database import obtener_contexto_completo, archivar_chat_actual

def inject_css(private: bool = False) -> None:
    max_width = "100%" if private else "1180px"
    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,650;9..144,700&family=Source+Sans+3:wght@400;500;600;700&display=swap');

          :root {{
            --bg: {PALETTE["bg"]};
            --ink: {PALETTE["ink"]};
            --deep: {PALETTE["deep"]};
            --slate: {PALETTE["slate"]};
            --accent: {PALETTE["accent"]};
            --mist: {PALETTE["mist"]};
            --radius: 15px;
          }}

          @keyframes fadeUp {{
            from {{ opacity: 0; transform: translateY(24px); }}
            to {{ opacity: 1; transform: translateY(0); }}
          }}

          html, body {{
            scroll-behavior: smooth !important;
          }}

          html, body, [data-testid="stAppViewContainer"], .stApp {{
            background: var(--bg) !important;
            color: var(--ink);
            font-family: "Source Sans 3", "Segoe UI", sans-serif;
            scroll-behavior: smooth !important;
          }}

          [data-testid="stAppViewContainer"],
          section.main {{
            scroll-behavior: smooth !important;
          }}

          [data-testid="stHeader"] {{
            background: transparent !important;
          }}

          [data-testid="stToolbar"], #MainMenu, footer, header {{
            visibility: hidden;
            height: 0;
          }}

          .block-container {{
            padding-top: 0.6rem !important;
            padding-bottom: 2rem !important;
            max-width: {max_width} !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
          }}

          [data-testid="stHorizontalBlock"] {{
            align-items: stretch !important;
            gap: 1rem;
          }}

          [data-testid="column"] {{
            display: flex !important;
            flex-direction: column !important;
            height: 100%;
            overflow: visible !important;
          }}

          [data-testid="column"] > div {{
            height: 100%;
            display: flex;
            flex-direction: column;
          }}

          [data-testid="stMarkdownContainer"],
          [data-testid="stMarkdownContainer"] > div {{
            height: 100%;
          }}

          h1, h2, h3 {{
            font-family: Fraunces, Georgia, serif !important;
            color: var(--ink);
            letter-spacing: -0.02em;
          }}

          .fadeUp, .section {{
            animation: fadeUp 0.8s ease both;
          }}

          .section-anchor {{
            scroll-margin-top: 96px;
            height: 1px;
          }}

          .carebot-header {{
            position: sticky;
            top: 0;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: rgba(255, 255, 255, 0.96);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 0.55rem 1rem;
            margin-bottom: 0.4rem;
            box-shadow: 0 8px 24px rgba(9, 35, 39, 0.08);
          }}

          .brand {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            font-family: Fraunces, Georgia, serif;
            font-weight: 700;
            font-size: 1.35rem;
            color: var(--deep);
            text-decoration: none !important;
          }}

          .brand svg {{ width: 38px; height: 38px; }}

          .nav-links {{
            display: flex;
            align-items: center;
            gap: 1.45rem;
          }}

          .nav-links a {{
            color: #3a4d50 !important;
            text-decoration: none !important;
            font-weight: 500;
            font-size: 0.98rem;
          }}

          .nav-links a:hover {{
            color: var(--accent) !important;
          }}

          div[data-testid="stButton"] > button,
          button[kind="primary"],
          .stButton > button {{
            background: #00A9A5 !important;
            color: #fff !important;
            border: none !important;
            border-radius: 999px !important;
            padding: 10px 20px !important;
            font-weight: 650 !important;
            white-space: nowrap !important;
            min-height: 44px !important;
            box-shadow: 0 8px 18px rgba(0, 169, 165, 0.25);
          }}

          button[kind="secondary"] {{
            background: #fff !important;
            color: #00A9A5 !important;
            border: 1.5px solid #00A9A5 !important;
            box-shadow: none !important;
          }}

          .badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            background: #e7f3fb;
            color: var(--deep);
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.86rem;
            font-weight: 600;
            margin-bottom: 1rem;
          }}

          .hero-copy h1 {{
            font-size: clamp(2.1rem, 4vw, 3.15rem);
            line-height: 1.12;
            margin: 0 0 0.85rem;
          }}

          .lead {{
            color: #3d5558;
            font-size: 1.08rem;
            line-height: 1.55;
            max-width: 40rem;
            margin-bottom: 1.2rem;
          }}

          .hero-visual {{
            position: relative;
          }}

          .hero-visual img {{
            width: 100%;
            border-radius: 22px;
            box-shadow: 0 18px 40px rgba(9, 35, 39, 0.12);
            object-fit: cover;
            min-height: 340px;
          }}

          .float-card {{
            position: absolute;
            left: 18px;
            bottom: 18px;
            background: #fff;
            border-radius: var(--radius);
            box-shadow: 0 10px 28px rgba(9, 35, 39, 0.14);
            padding: 0.85rem 1.05rem;
            min-width: 210px;
          }}

          .float-card strong {{
            display: block;
            color: var(--deep);
            font-size: 0.98rem;
          }}

          .float-card span {{
            color: #6b7c7e;
            font-size: 0.88rem;
          }}

          .section {{
            padding: 1.6rem 0 0.4rem;
          }}

          .section-head {{
            text-align: center;
            margin: 0 auto 1.7rem;
            max-width: 44rem;
          }}

          .section-head h2 {{
            font-size: clamp(1.85rem, 3vw, 2.45rem);
            margin: 0 0 0.45rem;
          }}

          .section-head p {{
            color: #4a5f62;
            font-size: 1.02rem;
            margin: 0;
          }}

          .card-aurora {{
            height: 100%;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            background: #fff;
            color: var(--ink);
            border-radius: 15px;
            padding: 1.4rem 1.3rem;
            box-shadow: 0 10px 28px rgba(11, 83, 81, 0.08);
            box-sizing: border-box;
            transition: all 0.3s ease;
            cursor: default;
          }}

          .card-aurora:hover {{
            transform: scale(1.02);
            background: #0B5351;
            color: #fff;
            box-shadow: 0 16px 36px rgba(11, 83, 81, 0.22);
          }}

          .card-aurora h3,
          .card-aurora p,
          .card-aurora li {{
            color: inherit;
          }}

          .card-aurora h3 {{
            margin: 0 0 0.55rem;
            font-size: 1.28rem;
          }}

          .card-aurora p,
          .card-aurora li {{
            line-height: 1.5;
            font-size: 0.98rem;
          }}

          .card-aurora ul {{
            margin: 0.4rem 0 0;
            padding: 0;
            list-style: none;
          }}

          .card-aurora li {{
            display: flex;
            gap: 0.5rem;
            margin: 0.45rem 0;
          }}

          .icon-pill {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: #e4f1fb;
            color: var(--deep);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.85rem;
            flex-shrink: 0;
          }}

          .card-aurora:hover .icon-pill {{
            background: rgba(0, 169, 165, 0.28);
            color: #fff;
          }}

          .check {{
            color: var(--accent);
            font-weight: 700;
          }}

          .card-aurora:hover .check {{
            color: var(--mist);
          }}

          .muted {{
            color: #6a7c7f;
            font-size: 0.86rem;
            margin-bottom: 0.15rem;
          }}

          .card-aurora:hover .muted {{
            color: rgba(255,255,255,0.82);
          }}

          .step-title {{
            color: var(--accent);
            font-family: "Source Sans 3", sans-serif;
            font-weight: 700;
            font-size: 1.08rem;
            margin: 0.2rem 0 0.45rem;
          }}

          .card-aurora:hover .step-title {{
            color: var(--mist);
          }}

          .site-footer {{
            background: var(--deep);
            color: #fff;
            border-radius: 18px;
            text-align: center;
            padding: 1.7rem 1rem;
            margin-top: 2rem;
          }}

          .site-footer strong {{
            font-family: Fraunces, Georgia, serif;
            font-size: 1.2rem;
            display: block;
            margin-bottom: 0.35rem;
          }}

          .private-top {{
            width: 100%;
            background: var(--deep);
            color: #fff;
            border-radius: 16px;
            padding: 1.15rem 1.25rem 1.25rem;
            margin-bottom: 1.1rem;
            box-sizing: border-box;
          }}

          .private-top-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.85rem;
          }}

          .private-who {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
          }}

          .private-who svg {{ width: 36px; height: 36px; }}

          .private-who small {{
            display: block;
            opacity: 0.78;
            font-size: 0.82rem;
          }}

          .private-top h1 {{
            color: #fff !important;
            font-size: clamp(1.7rem, 3vw, 2.35rem);
            margin: 0 0 0.45rem;
          }}

          .private-top .lead {{
            color: rgba(255,255,255,0.88);
            margin-bottom: 0.85rem;
            max-width: none;
          }}

          .status-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
          }}

          .chip {{
            border-radius: 999px;
            padding: 0.38rem 0.85rem;
            font-size: 0.84rem;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.28);
            color: var(--deep);
            background: #fff;
          }}

          .chip.solid {{
            background: var(--mist);
            border-color: transparent;
          }}

          .chat-head {{
            background: var(--deep);
            color: #fff;
            border-radius: 15px;
            padding: 0.85rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin: 0.4rem 0 0.8rem;
          }}

          .chat-head svg {{ width: 32px; height: 32px; }}

          .online {{
            font-size: 0.82rem;
            opacity: 0.9;
          }}

          .online::before {{
            content: "";
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #6ee7b7;
            border-radius: 50%;
            margin-right: 0.4rem;
          }}

          .logout-btn button {{
            background: transparent !important;
            color: #fff !important;
            border: 1px solid rgba(255,255,255,0.55) !important;
            box-shadow: none !important;
          }}

          [data-testid="stTextInput"] input {{
            border-radius: 12px !important;
            border: 1px solid #d5e1e3 !important;
          }}

          [data-testid="stChatMessage"] {{
            background: #fff;
            border-radius: 14px;
          }}

          @media (max-width: 900px) {{
            .nav-links {{ display: none; }}
          }}

          {"" if not private else """
          .private-header-anchor {{
            display: none;
          }}

          div:has(> .private-header-anchor) + div [data-testid="stHorizontalBlock"] {{
            background-color: #0B5351 !important;
            border-radius: 15px !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
            align-items: center !important;
          }}

          div:has(> .private-header-anchor) + div [data-testid="stHorizontalBlock"] h2 {{
            color: #fff !important;
            margin: 0 0 0.25rem 0 !important;
          }}

          div:has(> .private-header-anchor) + div button {{
            background: #00A9A5 !important;
            color: #fff !important;
            border: none !important;
            border-radius: 999px !important;
            padding: 10px 20px !important;
            font-weight: 650 !important;
            box-shadow: none !important;
          }}
          """}
        </style>
        """
        ,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "logged_in": False,
        "current_page": "public",  # <--- ¡Esta es la línea nueva que la memoria necesita!
        "user_email": "",
        "messages": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.messages:
        st.session_state.messages = [
            {"role": "assistant", "content": text} for text in WELCOME_MESSAGES
        ]


@st.dialog("Acceso al Portal del Cuidador")
def login_dialog() -> None:
    html("<p style='margin-top:0;color:#4a5f62;'>Sistema de autenticación seguro. Credenciales requeridas.</p>")
    
    # Creamos dos pestañas en la ventana emergente
    tab_login, tab_register = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
    
    # --- PESTAÑA DE INGRESO ---
    with tab_login:
        email_login = st.text_input("Correo Electrónico", key="login_email")
        pass_login = st.text_input("Contraseña", type="password", key="login_pass")
        
        if st.button("Ingresar", use_container_width=True):
            email_limpio = email_login.strip()
            
            # Verificamos contra MongoDB de forma segura
            if verificar_usuario(email_limpio, pass_login):
                st.session_state.logged_in = True
                st.session_state.current_page = "private" 
                st.session_state.user_email = email_limpio
                
                # Cargamos o creamos el perfil como lo hacíamos antes
                mis_pacientes = obtener_pacientes_del_cuidador(email_limpio)
                if mis_pacientes:
                    p = mis_pacientes[0]
                    st.session_state.paciente_activo_id = p["_id"]
                    st.session_state.messages = p.get("messages", [])
                    st.session_state.perfil_completado = p.get("perfil_completado", False)
                    st.session_state.datos_paciente = p.get("datos_paciente", {})
                else:
                    nuevo_p = crear_nuevo_perfil(email_limpio)
                    st.session_state.paciente_activo_id = nuevo_p["_id"]
                    st.session_state.messages = nuevo_p["messages"]
                    st.session_state.perfil_completado = False
                    st.session_state.datos_paciente = {}
                    
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Intente nuevamente.")
                
    # --- PESTAÑA DE REGISTRO ---
    with tab_register:
        email_reg = st.text_input("Nuevo Correo", key="reg_email")
        pass_reg = st.text_input("Crear Contraseña", type="password", key="reg_pass")
        
        if st.button("Registrarse", type="primary", use_container_width=True):
            email_limpio = email_reg.strip()
            
            # Evitamos correos y contraseñas vacías
            if len(email_limpio) < 3 or len(pass_reg) < 4:
                st.warning("Ingrese un correo válido y una contraseña de al menos 4 caracteres.")
            elif registrar_usuario(email_limpio, pass_reg):
                st.success("¡Cuenta creada exitosamente! Ahora puede iniciar sesión en la pestaña de al lado.")
            else:
                st.error("Ese correo ya se encuentra registrado en el sistema.")


def render_public_header() -> None:
    brand, nav, cta = st.columns([1.5, 3.3, 1.6], vertical_alignment="center")
    with brand:
        html(
            f"""
            <div class="carebot-header" style="box-shadow:none;padding:0;margin:0;background:transparent;">
              <a class="brand" href="#inicio" target="_self">{LOGO_SVG} CareBOT</a>
            </div>
            """
        )
    with nav:
        html(
            """
            <nav class="nav-links" style="justify-content:center;padding-top:0.55rem;">
              <a href="#identidad" target="_self">Identidad</a>
              <a href="#como" target="_self">¿Cómo funciona?</a>
              <a href="#modelos" target="_self">Modelos</a>
            </nav>
            """
        )
    with cta:
        if st.session_state.logged_in:
            # Aquí usamos el nuevo Popover de Streamlit para el menú de perfil
            with st.popover("👤 Mi Perfil", use_container_width=True):
                st.markdown(f"**Cuidador:**<br><small>{st.session_state.user_email}</small>", unsafe_allow_html=True)
                st.divider()
                
                st.markdown("**Mis Pacientes:**")
                
                # 1. Cargamos todos los pacientes de la base de datos
                mis_pacientes = obtener_pacientes_del_cuidador(st.session_state.user_email)
                
                # 2. Creamos un botón por cada paciente
                for p in mis_pacientes:
                    nombre_btn = p.get("datos_paciente", {}).get("datos_personales", {}).get("nombre_completo", "Perfil en configuración")
                    if st.button(f"📄 {nombre_btn}", key=str(p["_id"]), use_container_width=True):
                        st.session_state.paciente_activo_id = p["_id"]
                        st.session_state.messages = p.get("messages", [])
                        st.session_state.perfil_completado = p.get("perfil_completado", False)
                        st.session_state.datos_paciente = p.get("datos_paciente", {})
                        st.rerun()
                st.divider()
                
                # Botones de acción dentro del menú flotante
                if st.button("➕ Añadir nuevo paciente", use_container_width=True):
                    nuevo_p = crear_nuevo_perfil(st.session_state.user_email)
                    st.session_state.paciente_activo_id = nuevo_p["_id"]
                    st.session_state.messages = nuevo_p["messages"]
                    st.session_state.perfil_completado = False
                    st.session_state.datos_paciente = {}
                    st.rerun()
                    
                st.divider()
                
                if st.button("Volver al Inicio", use_container_width=True):
                    st.session_state.current_page = "public"
                    st.rerun()
                    
                if st.button("Cerrar Sesión", type="primary", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.current_page = "public"
                    st.rerun()
        else:
            if st.button("Configurar Asistente", key="btn_login", use_container_width=True):
                login_dialog()


def render_hero() -> None:
    html('<div id="inicio" class="section-anchor"></div>')
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        html(
            """
            <div class="hero-copy fadeUp">
              <div class="badge">Cuidado asistido por IA, supervisado por humanos</div>
              <h1>CareBOT: Inteligencia Artificial con Empatía</h1>
              <p class="lead">
                El puente entre la tecnología de vanguardia y la calidez humana
                para el cuidado del adulto mayor.
              </p>
            </div>
            """
        )
        b1, b2, _ = st.columns([1, 1, 1.4])
        with b1:
            # =========================================================
            # MAGIA CONDICIONAL: Cambia el botón si ya hay sesión
            # =========================================================
            if st.session_state.get("logged_in", False):
                if st.button("Ir al Portal", key="btn_hero_portal", use_container_width=True):
                    st.session_state.current_page = "private"
                    st.rerun()
            else:
                # Nota: Cambié width="stretch" por use_container_width=True que es el estándar de Streamlit
                if st.button("Configurar Asistente", key="btn_login_hero", use_container_width=True):
                    login_dialog()
            # =========================================================
            
        with b2:
            html(
                """
                <div style="padding-top:0.15rem;">
                  <a href="#como" target="_self"
                     style="display:inline-flex;align-items:center;justify-content:center;
                            height:44px;padding:10px 20px;border-radius:999px;
                            border:1.5px solid #00A9A5;color:#00A9A5;text-decoration:none;
                            font-weight:650;white-space:nowrap;background:#fff;">
                    Ver cómo funciona
                  </a>
                </div>
                """
            )
    with right:
        if HERO_IMAGE.exists():
            encoded = base64.b64encode(HERO_IMAGE.read_bytes()).decode("ascii")
            src = f"data:image/png;base64,{encoded}"
        else:
            src = "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=1200&q=80"
        html(
            f"""
            <div class="hero-visual fadeUp">
              <img alt="Adulto mayor acompañado en casa" src="{src}"/>
              <div class="float-card">
                <strong>Acompañamiento continuo</strong>
                <span>24 horas, todos los días</span>
              </div>
            </div>
            """
        )

def render_identidad() -> None:
    html('<div id="identidad" class="section-anchor"></div>')
    html(
        """
        <section class="section fadeUp">
          <div class="section-head">
            <h2>Identidad Corporativa</h2>
            <p>Somos un equipo clínico y tecnológico que construye cuidado digno, medible y cercano.</p>
          </div>
        </section>
        """
    )
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        html(
            """
            <div class="card-aurora">
              <div class="icon-pill">1</div>
              <h3>Misión</h3>
              <p>Acompañar a los adultos mayores en su día a día a través de interacciones de voz que se sientan naturales y cálidas, evitando la soledad, cuidando la salud mediante monitoreo silencioso y conectándolos con sus seres queridos sin que tengan que aprender nuevas tecnologías.</p>
            </div>
            """
        )
    with c2:
        html(
            """
            <div class="card-aurora">
              <div class="icon-pill">2</div>
              <h3>Visión</h3>
              <p>La visión que tiene este proyecto es que los adultos mayores no se sientan solos o abandonados, y que la tecnología sea una forma de conectar ese sentimiento de calidez humana, la salud y la tranquilidad en cada hogar.</p>
            </div>
            """
        )
    with c3:
        html(
            """
            <div class="card-aurora">
              <div class="icon-pill">3</div>
              <h3>Objetivos</h3>
              <ul>
                <li><span class="check">✓</span> Reducir el agotamiento del cuidador con apoyo continuo y reportes claros.</li>
                <li><span class="check">✓</span> Ofrecer acompañamiento 24/7 con conversación natural y respetuosa.</li>
                <li><span class="check">✓</span> Asegurar la adherencia médica mediante recordatorios verificados.</li>
              </ul>
            </div>
            """
        )


def render_como_funciona() -> None:
    html('<div id="como" class="section-anchor"></div>')
    html(
        """
        <section class="section fadeUp">
          <div class="section-head">
            <h2>¿Cómo Funciona?</h2>
            <p>Tres pasos continuos que convierten la conversación cotidiana en cuidado preventivo.</p>
          </div>
        </section>
        """
    )
    c1, c2, c3 = st.columns(3, gap="medium")
    steps = [
        ("1", "1. Escucha Activa", "CareBOT conversa con naturalidad y registra lo importante: ánimo, dolores, apetito y hábitos de sueño."),
        ("2", "2. Análisis Silencioso", "En segundo plano, los modelos detectan cambios de patrón y señales tempranas sin interrumpir la vida diaria."),
        ("3", "3. Alertas en Tiempo Real", "La familia y el personal de salud reciben avisos priorizados con contexto suficiente para actuar rápido."),
    ]
    for col, (icon, title, text) in zip((c1, c2, c3), steps):
        with col:
            html(
                f"""
                <div class="card-aurora">
                  <div class="icon-pill">{icon}</div>
                  <p class="step-title">{title}</p>
                  <p>{text}</p>
                </div>
                """
            )


def render_modelos() -> None:
    html('<div id="modelos" class="section-anchor"></div>')
    html(
        """
        <section class="section fadeUp">
          <div class="section-head">
            <h2>Modelos de Asistencia</h2>
            <p>Elija el modo de operación de CareBOT según el nivel de apoyo que necesita la persona cuidada.</p>
          </div>
        </section>
        """
    )
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        html(
            """
            <div class="card-aurora">
              <div class="icon-pill">1</div>
              <p class="muted">Modelo 1</p>
              <h3>Básico / Recordatorios</h3>
              <p class="muted">Para rutinas médicas estrictas.</p>
              <ul>
                <li><span class="check">✓</span> Alarmas de medicación</li>
                <li><span class="check">✓</span> Recordatorios de citas e hidratación</li>
                <li><span class="check">✓</span> Reporte diario de adherencia</li>
                <li><span class="check">✓</span> Aviso al cuidador ante dosis omitidas</li>
              </ul>
            </div>
            """
        )
    with c2:
        html(
            """
            <div class="card-aurora">
              <div class="icon-pill">2</div>
              <p class="muted">Modelo 2</p>
              <h3>Compañía / Charla</h3>
              <p>Para quienes pasan muchas horas solos.</p>
              <ul>
                <li><span class="check">✓</span> Conversación casual y escucha activa</li>
                <li><span class="check">✓</span> Recuerdos, música y lecturas guiadas</li>
                <li><span class="check">✓</span> Detección de soledad y bajo ánimo</li>
                <li><span class="check">✓</span> Incluye todo el modelo Básico</li>
              </ul>
            </div>
            """
        )
    with c3:
        html(
            """
            <div class="card-aurora">
              <div class="icon-pill">3</div>
              <p class="muted">Modelo 3</p>
              <h3>Proactivo Integral</h3>
              <p class="muted">Acompañamiento participativo y completo.</p>
              <ul>
                <li><span class="check">✓</span> Inicia conversaciones según el contexto</li>
                <li><span class="check">✓</span> Análisis de estados psicológicos</li>
                <li><span class="check">✓</span> Integración IoT del hogar completa</li>
                <li><span class="check">✓</span> Panel clínico para el equipo de salud</li>
              </ul>
            </div>
            """
        )


def render_footer() -> None:
    html(
        """
        <div class="site-footer fadeUp">
          <strong>CareBOT</strong>
          Inteligencia artificial con empatía para el cuidado del adulto mayor.
        </div>
        """
    )


def render_public_view() -> None:
    render_public_header()
    render_hero()
    render_identidad()
    render_como_funciona()
    render_modelos()
    render_footer()


def assistant_reply(user_text: str) -> str:
    text = user_text.lower()
    if any(word in text for word in ("me llam", "se llama", "nombre")):
        return (
            "Gracias. Registraré ese nombre con respeto y lo usaré en las conversaciones. "
            "Ahora cuénteme la hora habitual de despertarse y si hay medicamentos fijos por la mañana."
        )
    if any(word in text for word in ("medic", "pastilla", "dosis")):
        return (
            "Anotado. Armaré recordatorios verificables para esa pauta. "
            "¿Hay contactos de emergencia que deban recibir aviso si se omite una dosis?"
        )
    if any(word in text for word in ("emergencia", "hijo", "hija", "familiar", "tel")):
        return (
            "Perfecto. El canal familiar quedará listo para alertas priorizadas. "
            "¿En qué momentos del día prefiere conversar la persona cuidada?"
        )
    return (
        "Lo estoy incorporando al perfil de cuidado. "
        "Puede seguir con rutinas, comidas, preferencias de conversación o contactos de emergencia."
    )


def render_private_view() -> None:
    st.sidebar.markdown("## 🗂️ Historial de Consultas")
    
    # Buscamos los chats guardados en los datos del paciente actual
    historial_chats = st.session_state.get("datos_paciente", {}).get("historial_chats", [])
    
    if historial_chats:
        # Usamos 'reversed' para que las consultas más recientes salgan primero arriba
        for sesion in reversed(historial_chats):
            # Creamos un menú desplegable por cada fecha
            with st.sidebar.expander(f"🕒 Fecha: {sesion['fecha']}"):
                for msg in sesion["mensajes"]:
                    if msg["role"] == "user":
                        st.markdown(f"**Tú:** {msg['content']}")
                    elif msg["role"] == "assistant":
                        # Solo mostramos los primeros 60 caracteres de CareBOT para no saturar la vista
                        st.caption(f"🤖 {msg['content'][:60]}...")
    else:
        st.sidebar.info("Aún no hay consultas anteriores guardadas para este paciente.")
    
    # ============================================================
    # LÓGICA DE AUTO-LIMPIEZA AL ENTRAR
    # ============================================================
    paciente_actual = st.session_state.get("paciente_activo_id")
    
    if st.session_state.get("ultimo_paciente_limpiado") != paciente_actual:
        if len(st.session_state.get("messages", [])) > 1:
            archivar_chat_actual(paciente_actual, st.session_state.messages)
        
        st.session_state.messages = [{"role": "assistant", "content": "¡Bienvenido! ¿Qué deseas consultar sobre el expediente hoy?"}]
        st.session_state.ultimo_paciente_limpiado = paciente_actual
        st.rerun()
      # ============================================================

      # ... a partir de aquí sigue tu código normal ...
      # (ej. el contenedor_chat que hicimos en el paso anterior)
      # 1. Inyección de CSS
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"]:first-of-type {
        background-color: #0B5351 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        margin-bottom: 25px !important;
        align-items: center !important;
    }
    
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stPopover"] button {
        background-color: #00A9A5 !important;
        color: white !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: bold !important;
    }
    
    div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stPopover"] button:hover {
        transform: scale(1.02);
        transition: 0.3s ease;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. Header Unificado (2 Columnas)
    col1, col2 = st.columns([8, 2], vertical_alignment="center")
    
    with col1:
        st.markdown('''
        <div style="background-color: transparent;">
            <h2 style="margin: 0; color: white; font-weight: 600;">Portal del Cuidador</h2>
            <div style="display: flex; align-items: center; gap: 15px; margin-top: 5px;">
                <small style="color: #90C2E7; font-size: 0.9em;">Configuración activa</small>
                <small style="color: #00A9A5; font-size: 0.9em; font-weight: bold;">● En línea</small>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        # Menú desplegable interactivo conectado a MongoDB
        with st.popover("👤 Mi Perfil", use_container_width=True):
            st.markdown(f"**Cuidador:**<br><small>{st.session_state.user_email}</small>", unsafe_allow_html=True)
            st.divider()
            
            st.markdown("**Mis Pacientes:**")
            
            # 1. Cargamos todos los pacientes de la base de datos
            mis_pacientes = obtener_pacientes_del_cuidador(st.session_state.user_email)
            
            # 2. Creamos un botón por cada paciente
            for p in mis_pacientes:
                nombre_btn = p.get("datos_paciente", {}).get("datos_personales", {}).get("nombre_completo", "Perfil en configuración")
                if st.button(f"📄 {nombre_btn}", key=f"priv_{str(p['_id'])}", use_container_width=True):
                    st.session_state.paciente_activo_id = p["_id"]
                    st.session_state.messages = p.get("messages", [])
                    st.session_state.perfil_completado = p.get("perfil_completado", False)
                    st.session_state.datos_paciente = p.get("datos_paciente", {})
                    # ¡AQUÍ ESTÁ LA MAGIA! Cargamos el historial a la memoria RAM de la web
                    st.session_state.historial_chats = p.get("historial_chats", [])
                    st.rerun()
            
            st.divider()
            
            # 3. Botón para crear un nuevo perfil
            if st.button("➕ Añadir nuevo paciente", key="btn_add_priv", use_container_width=True):
                nuevo_p = crear_nuevo_perfil(st.session_state.user_email)
                st.session_state.paciente_activo_id = nuevo_p["_id"]
                st.session_state.messages = nuevo_p["messages"]
                st.session_state.perfil_completado = False
                st.session_state.datos_paciente = {}
                st.session_state.historial_chats = [] # Nuevo paciente, historial en blanco
                st.rerun()
                
            st.divider()
            
            # 4. BOTÓN: LIMPIAR Y ARCHIVAR LA CONSULTA ACTUAL
            if st.button("➕ Iniciar Nueva Consulta", key="btn_nueva_consulta", use_container_width=True):
                # Guardamos en la base de datos
                archivar_chat_actual(st.session_state.paciente_activo_id, st.session_state.messages)
                
                # Actualizamos la RAM inmediatamente para verlo sin cambiar de paciente
                import datetime
                if "historial_chats" not in st.session_state:
                    st.session_state.historial_chats = []
                    
                st.session_state.historial_chats.append({
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "mensajes": st.session_state.messages
                })
                
                # Mensaje personalizado
                nombre_paciente = st.session_state.get("datos_paciente", {}).get("datos_personales", {}).get("nombre_completo", "el paciente")
                mensaje_amigable = f"Hola, ¿qué desea consultar hoy sobre {nombre_paciente}?"
                
                st.session_state.messages = [{"role": "assistant", "content": mensaje_amigable}]
                st.rerun()
                
            st.divider()
            
            # Navegación y salida
            if st.button("Volver al Inicio", key="btn_volver_priv", use_container_width=True):
                st.session_state.current_page = "public"
                st.rerun()
                
            if st.button("Cerrar Sesión", key="btn_salir_priv", type="primary", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_page = "public"
                st.rerun()

    # ============================================================
    # NUEVO VISOR DE HISTORIAL (EN LA PANTALLA PRINCIPAL)
    # ============================================================
    if "historial_chats" in st.session_state and st.session_state.historial_chats:
        # 1. Un botón principal que abre una ventana flotante limpia
        with st.popover("🗂️ Ver Consultas Anteriores", use_container_width=True):
            st.markdown("### 🗄️ Archivo Clínico")
            
            # 2. Reversed para mostrar las fechas más nuevas primero
            for sesion in reversed(st.session_state.historial_chats):
                
                # 3. Cada fecha es una "carpeta" retraíble independiente
                with st.expander(f"📅 Consulta del: {sesion['fecha']}"):
                    for msg in sesion["mensajes"]:
                        if msg["role"] == "user":
                            st.markdown(f"**Tú:** {msg['content']}")
                        elif msg["role"] == "assistant":
                            # Como ahora está colapsado por defecto, podemos mostrar todo el texto de Claude sin recortarlo
                            st.caption(f"🤖 {msg['content']}")
                st.divider()

    # ============================================================
    # EL CHAT ACTUAL
    # ============================================================
    contenedor_chat = st.container(height=700, border=False)
    
    with contenedor_chat:
        for message in st.session_state.messages:
            avatar = "💚" if message["role"] == "assistant" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    # 4. Input del Chat (Conectado a la IA y a Mongo)
    if st.session_state.get("perfil_completado", False):
        # Intentamos obtener el nombre de la base de datos, si no hay, decimos "el paciente"
        nombre = st.session_state.datos_paciente.get("datos_personales", {}).get("nombre_completo", "el paciente")
        placeholder_text = f"Bienvenido, ¿tiene alguna consulta sobre el expediente de {nombre}?"
    else:
        placeholder_text = "Escriba su mensaje aquí..."

    # Usamos nuestra variable dinámica en el input
    prompt = st.chat_input(placeholder_text)
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 1. Copiamos el perfil básico
        datos_completos_para_ia = st.session_state.get("datos_paciente", {}).copy()
        
        # 2. Le inyectamos TODA la base de datos (El Mega-Paquete)
        if st.session_state.get("perfil_completado", False):
            contexto_total = obtener_contexto_completo(st.session_state.paciente_activo_id)
            datos_completos_para_ia["db_completa"] = contexto_total
        
        # 3. Llamamos a Claude
        respuesta_ia, datos_json = consultar_claude(
            prompt, 
            st.session_state.messages,
            st.session_state.get("perfil_completado", False),
            datos_completos_para_ia 
        )

     # Mostramos la respuesta de la IA
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

        # ... (el resto de tu código de guardado se mantiene igual)
        save_messages_to_db(st.session_state.paciente_activo_id, st.session_state.messages)

        if datos_json:
            st.success("¡Perfil completado! CareBOT ahora funciona en Modo Consultor.")
            save_patient_data(st.session_state.paciente_activo_id, datos_json) 
            st.session_state.perfil_completado = True
            st.session_state.datos_paciente = datos_json

        st.rerun()