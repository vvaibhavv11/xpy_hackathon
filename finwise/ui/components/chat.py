import streamlit as st
from ...core.assistant import FinancialAssistant

def render_chat_interface():
    """Render the main chat interface"""
    if st.session_state.current_chat:
        chat_messages = st.session_state.chats[st.session_state.current_chat]
        
        st.title("FinWise - Your Financial Assistant")
        st.markdown("""
        Ask me anything about investing, financial markets, or personal finance. 
        I'm here to help you make informed financial decisions!
        """)
        
        render_chat_messages(chat_messages)
        handle_user_input(chat_messages)
    else:
        st.info("Start a new chat or select an existing one from the sidebar!")

def render_chat_messages(chat_messages):
    """Render existing chat messages"""
    for message in chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_user_input(chat_messages):
    """Handle user input and get assistant response"""
    user_input = st.chat_input("Ask a financial question...")
    
    if user_input:
        # Add user message
        chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get assistant response
        try:
            with st.spinner("Thinking..."):
                with st.chat_message("assistant"):
                    assistant = FinancialAssistant()
                    response = assistant.query(user_input)
                    st.markdown(response)
                    chat_messages.append({"role": "assistant", "content": response})
                    
                    # Update chat history
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error processing message: {str(e)}") 