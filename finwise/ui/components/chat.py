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
            # Check if the message contains HTML for visualization
            content = message["content"]
            
            # Look for HTML visualization content
            if "<!DOCTYPE html>" in content or "<div" in content or "<html" in content or "<script" in content:
                # Find all HTML content
                html_pattern = r'(<(?:div|html|!DOCTYPE html|script)[^>]*>.*?</(?:div|html|script)>)'
                text_parts = re.split(html_pattern, content, flags=re.DOTALL)
                
                for i, part in enumerate(text_parts):
                    if part.strip():
                        if part.startswith('<') and any(tag in part for tag in ['</div>', '</html>', '</script>']):
                            # This is HTML - render it
                            try:
                                st.components.v1.html(part, height=500, scrolling=True)
                            except Exception as e:
                                st.error(f"Error rendering visualization: {str(e)}")
                                st.code(part, language="html")
                        else:
                            # This is regular text
                            st.markdown(part)
            # Check for base64 image data
            elif "data:image/png;base64," in content:
                # Split text and image
                parts = content.split("data:image/png;base64,")
                
                # Display text before the image
                if parts[0].strip():
                    st.markdown(parts[0])
                
                # Display the image
                if len(parts) > 1:
                    img_data = parts[1].split('"')[0].split("'")[0].split(')')[0].split('\\n')[0]  # Extract just the base64 data
                    st.image(f"data:image/png;base64,{img_data}")
                    
                    # Display any text after the image if it exists
                    remaining_parts = parts[1].split('"', 1)
                    if len(remaining_parts) > 1:
                        st.markdown(remaining_parts[1])
            else:
                # Regular message with no visualization
                st.markdown(content)

def handle_user_input(chat_messages):
    """Handle user input and get assistant response"""
    user_input = st.chat_input("Ask a financial question...")
    
    if user_input:
        # Add user message
        chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Check if visualization is requested
        visualization_requested = any(keyword in user_input.lower() for keyword in 
            ["visualize", "visualization", "plot", "chart", "graph", "show me", "display"])
        
        # Get assistant response
        try:
            with st.spinner("Thinking..."):
                with st.chat_message("assistant"):
                    assistant = FinancialAssistant()
                    
                    # Process query
                    response = assistant.query(user_input)
                    
                    # Store response in chat history
                    chat_messages.append({"role": "assistant", "content": response})
                    
                    # Render the response with appropriate handling for visualizations
                    if "<html" in response or "<div" in response or "<script" in response:
                        # Handle HTML content
                        html_pattern = r'(<(?:div|html|!DOCTYPE html|script)[^>]*>.*?</(?:div|html|script)>)'
                        parts = re.split(html_pattern, response, flags=re.DOTALL)
                        
                        for part in parts:
                            if part.strip():
                                if part.startswith('<') and any(tag in part for tag in ['</div>', '</html>', '</script>']):
                                    # This is HTML - render it
                                    try:
                                        st.components.v1.html(part, height=500, scrolling=True)
                                    except Exception as e:
                                        st.error(f"Error rendering visualization: {str(e)}")
                                        st.code(part, language="html")
                                else:
                                    # This is regular text
                                    st.markdown(part)
                    elif "data:image/png;base64," in response:
                        # Split text and image
                        parts = response.split("data:image/png;base64,")
                        
                        # Display text before the image
                        if parts[0].strip():
                            st.markdown(parts[0])
                        
                        # Display the image
                        if len(parts) > 1:
                            img_data = parts[1].split('"')[0].split("'")[0].split(')')[0].split('\\n')[0]
                            st.image(f"data:image/png;base64,{img_data}")
                            
                            # Display any text after the image if it exists
                            remaining_parts = parts[1].split('"', 1)
                            if len(remaining_parts) > 1:
                                st.markdown(remaining_parts[1])
                    else:
                        # Display regular text response
                        st.markdown(response)
                    
                    # Update chat history
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Error processing message: {str(e)}") 