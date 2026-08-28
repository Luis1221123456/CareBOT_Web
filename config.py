from pathlib import Path
import streamlit as st
import textwrap

# Rutas
APP_DIR = Path(__file__).resolve().parent
HERO_IMAGE = APP_DIR / "assets" / "hero-carebot.png"

# Paleta de colores
PALETTE = {
    "bg": "#F4F9F9",
    "ink": "#092327",
    "deep": "#0B5351",
    "slate": "#4E8098",
    "accent": "#00A9A5",
    "mist": "#90C2E7",
}

# Logo y Mensajes
LOGO_SVG = """
<svg viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="24" cy="24" r="24" fill="#00A9A5"/>
  <path d="M16 24c0-3.4 2.4-6 5.4-6 1.6 0 3 .7 3.6 1.8.6-1.1 2-1.8 3.6-1.8 3 0 5.4 2.6 5.4 6 0 6.2-9 11-9 11s-9-4.8-9-11z"
        fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M14 24h4l2 4 3-8 2 4h5" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

WELCOME_MESSAGES = [
    (
        "Hola, soy CareBOT. Voy a acompañar a su familiar día y noche. "
        "Para empezar, ¿cómo se llama la persona a la que cuidaremos y cómo le gusta que la llamen?"
    ),
    (
        "Después me contará sus rutinas: hora de levantarse, comidas, medicamentos "
        "y los momentos del día en que prefiere conversar."
    ),
]

# Utilidades HTML
def html(content: str) -> None:
    st.markdown(textwrap.dedent(content).strip(), unsafe_allow_html=True)

# Inicializador de Memoria
def init_state() -> None:
    defaults = {
        "logged_in": False,
        "current_page": "public",
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