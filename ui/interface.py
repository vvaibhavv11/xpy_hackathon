import streamlit as st
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import tempfile

# Add the parent directory to sys.path to allow importing main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import query_financial_assistant, ingest_files  # Importing the main functionality

# Set page config for dark mode and wide layout
st.set_page_config(
    page_title="FinWise - Financial Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced dark mode and styling
st.markdown("""
    <style>
    /* Dark mode background and text */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #1E1E1E;
        border-radius: 15px;
        padding: 15px;
    }
    
    /* Buttons with rounded corners and hover effects */
    .stButton>button {
        background-color: #2C2C2C;
        color: #FFFFFF;
        border-radius: 20px;
        padding: 10px 20px;
        border: 1px solid #3C3C3C;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #3C3C3C;
        transform: scale(1.05);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        background-color: #2C2C2C;
        color: #FFFFFF;
        border-radius: 15px;
        border: 1px solid #3C3C3C;
    }
    
    /* Chat message styling */
    .chat-container {
        max-height: 70vh;
        overflow-y: auto;
        padding: 10px;
        border-radius: 15px;
        background-color: #1E1E1E;
    }
    .chat-message {
        margin-bottom: 10px;
        padding: 12px;
        border-radius: 12px;
        max-width: 90%;
    }
    .user-message {
        background-color: #2C2C2C;
        align-self: flex-end;
    }
    .assistant-message {
        background-color: #3C3C3C;
        align-self: flex-start;
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: #2C2C2C;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #4C4C4C;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for managing multiple chats
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
if 'messages' not in st.session_state:  # Add this for chat messages
    st.session_state.messages = []

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a temporary location"""
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Write the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# Sidebar Layout
def render_sidebar():
    with st.sidebar:
        st.title("FinWise 💰")
        
        # New Chat Button
        if st.button("🆕 New Chat", key="new_chat"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chat_id = f"chat_{timestamp}"
            
            # Create new chat
            st.session_state.chats[chat_id] = []
            st.session_state.active_chats.append(chat_id)
            st.session_state.current_chat = chat_id
            # Reset chat history for new chat
            st.session_state.chat_history = []
            st.rerun()
        
        # File Upload with Dropdown
        st.subheader("📁 Upload Financial Documents")
        upload_option = st.selectbox("Choose Upload Type", 
            ["Single File", "Multiple Files"]
        )
        
        # Metadata inputs
        st.subheader("Document Metadata (Optional)")
        source = st.text_input("Source (e.g., annual_report, market_data)")
        company = st.text_input("Company Name or Ticker Symbol")
        year = st.text_input("Year")
        
        if upload_option == "Single File":
            uploaded_file = st.file_uploader(
                "Upload a file", 
                type=['txt', 'pdf', 'doc', 'docx', 'csv', 'xlsx', 'json']
            )
            if uploaded_file:
                if uploaded_file.name not in [f.name for f in st.session_state.uploaded_files]:
                    st.session_state.uploaded_files.append(uploaded_file)
                    st.success(f"Added {uploaded_file.name}")
        else:
            uploaded_files = st.file_uploader(
                "Upload multiple files", 
                accept_multiple_files=True,
                type=['txt', 'pdf', 'doc', 'docx', 'csv', 'xlsx', 'json']
            )
            if uploaded_files:
                for file in uploaded_files:
                    if file.name not in [f.name for f in st.session_state.uploaded_files]:
                        st.session_state.uploaded_files.append(file)
                        st.success(f"Added {file.name}")
        
        # Show uploaded files
        if st.session_state.uploaded_files:
            st.subheader("📄 Uploaded Files")
            for file in st.session_state.uploaded_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {file.name}")
                with col2:
                    if st.button("❌", key=f"remove_{file.name}"):
                        st.session_state.uploaded_files.remove(file)
                        st.rerun()
            
            if st.button("Process Files"):
                with st.spinner("Processing files..."):
                    try:
                        # Save uploaded files temporarily
                        temp_files = []
                        metadata_list = []
                        
                        for file in st.session_state.uploaded_files:
                            file_path = save_uploaded_file(file)
                            if file_path:
                                temp_files.append(file_path)
                                
                                # Create metadata dictionary
                                metadata = {}
                                if source:
                                    metadata["source"] = source
                                if company:
                                    metadata["company"] = company
                                if year:
                                    metadata["year"] = year
                                
                                metadata_list.append(metadata)
                        
                        # Ingest files
                        if temp_files:
                            metadata_list = metadata_list if any(metadata_list) else None
                            count = ingest_files(temp_files, metadata_list)
                            st.success(f"Successfully processed {count} document chunks!")
                    except Exception as e:
                        st.error(f"Error processing files: {str(e)}")
        
        # Chat History Section
        st.subheader("💬 Chat History")
        for chat_id in st.session_state.active_chats:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"Chat {chat_id.split('_')[1]}", key=chat_id):
                    st.session_state.current_chat = chat_id
                    st.rerun()
            with col2:
                if st.button("❌", key=f"close_{chat_id}"):
                    st.session_state.active_chats.remove(chat_id)
                    if chat_id == st.session_state.current_chat:
                        st.session_state.current_chat = None
                    st.rerun()

# Main Chat Interface
def render_chat_interface():
    if st.session_state.current_chat:
        chat_messages = st.session_state.chats[st.session_state.current_chat]
        
        st.title("FinWise - Your Financial Assistant")
        st.markdown("""
        Ask me anything about investing, financial markets, or personal finance. 
        I'm here to help you make informed financial decisions!
        """)
        
        # Chat Messages Container using st.chat_message
        for message in chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat Input using st.chat_input
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
                        response = query_financial_assistant(user_input)
                        st.markdown(response)
                        chat_messages.append({"role": "assistant", "content": response})
                        
                        # Update chat history
                        st.session_state.chat_history.append({"role": "user", "content": user_input})
                        st.session_state.chat_history.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error processing message: {str(e)}")
    else:
        st.info("Start a new chat or select an existing one from the sidebar!")

# Main App Rendering
def main():
    render_sidebar()
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("FinWise | Powered by Gemini 1.5 Pro")

# Run the app
if __name__ == "__main__":
    main()