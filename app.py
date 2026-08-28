import streamlit as st
from config import init_state
from ui import inject_css, render_private_view, render_public_view

def main() -> None:
    st.set_page_config(
        page_title="CareBOT — Cuidado con empatía",
        page_icon="💚",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    
    # 1. Inicializar la memoria
    init_state()
    
    # 2. Inyectar estilos visuales
    inject_css(private=(st.session_state.current_page == "private"))

    # 3. Enrutador de páginas
    if st.session_state.current_page == "private" and st.session_state.logged_in:
        render_private_view()
    else:
        render_public_view()

if __name__ == "__main__":
    main()