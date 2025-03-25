import streamlit as st
from .components.sidebar import render_sidebar
from .components.chat import render_chat_interface
from .styles import STYLES

def initialize_session_state():
    """Initialize session state variables"""
    if 'chats' not in st.session_state:
        st.session_state.chats = {}
    if 'active_chats' not in st.session_state:
        st.session_state.active_chats = []
    if 'current_chat' not in st.session_state:
        st.session_state.current_chat = None
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def setup_page():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="FinWise - Financial Assistant",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(STYLES, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    setup_page()
    initialize_session_state()
    
    render_sidebar()
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("FinWise | Powered by Gemini 1.5 Pro")

if __name__ == "__main__":
    main() 