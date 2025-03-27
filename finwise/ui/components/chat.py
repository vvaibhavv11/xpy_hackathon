import streamlit as st
import json
import re
from ...core.assistant import FinancialAssistant

def render_chat_interface():
    """Render the main chat interface"""
    if st.session_state.current_chat:
        chat_messages = st.session_state.chats[st.session_state.current_chat]
        
        st.title("FinWise - Your Financial Assistant")
        st.markdown("""
        Ask me anything about investing, financial markets, or personal finance. 
        I can help with calculations and create visualizations too!
        """)
        
        render_chat_messages(chat_messages)
        handle_user_input(chat_messages)
    else:
        st.info("Start a new chat or select an existing one from the sidebar!")

def render_chat_messages(chat_messages):
    """Render existing chat messages"""
    for idx, message in enumerate(chat_messages):
        with st.chat_message(message["role"]):
            content = message["content"]
            
            # Check if the message contains HTML visualization
            if isinstance(content, str) and ("<html" in content or "<div" in content or "<script" in content):
                # Split text and HTML
                parts = re.split(r'(<(?:html|div|script)[^>]*>.*?</(?:html|div|script)>)', content, flags=re.DOTALL)
                
                for part in parts:
                    if part.strip():
                        if part.startswith('<'):
                            # Create a unique key for this visualization
                            viz_key = f"viz_{idx}"
                            # Add a button to toggle visualization
                            if viz_key not in st.session_state:
                                st.session_state[viz_key] = False
                            
                            if st.button("📊 Show/Hide Visualization", key=f"btn_{viz_key}"):
                                st.session_state[viz_key] = not st.session_state[viz_key]
                            
                            # Show visualization if button is toggled
                            if st.session_state[viz_key]:
                                st.components.v1.html(part, height=500, scrolling=True)
                        else:
                            # Render regular text
                            st.markdown(part)
            else:
                st.markdown(content)

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
                    
                    # Process query
                    response = assistant.query(user_input)
                    
                    # Store response in chat history
                    chat_messages.append({"role": "assistant", "content": response})
                    
                    # Render response with visualization support
                    if isinstance(response, str) and ("<html" in response or "<div" in response or "<script" in response):
                        # Split text and HTML
                        parts = re.split(r'(<(?:html|div|script)[^>]*>.*?</(?:html|div|script)>)', response, flags=re.DOTALL)
                        
                        for part in parts:
                            if part.strip():
                                if part.startswith('<'):
                                    # Render HTML visualization
                                    st.components.v1.html(part, height=500, scrolling=True)
                                else:
                                    # Render regular text
                                    st.markdown(part)
                    else:
                        st.markdown(response)
                    
                    # Update chat history
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error processing message: {str(e)}") 