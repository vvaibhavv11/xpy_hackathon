import streamlit as st
from datetime import datetime
from ...core.document_processor import DocumentProcessor
from ...core.assistant import FinancialAssistant

def render_sidebar():
    """Render the sidebar with file upload and chat management"""
    with st.sidebar:
        st.title("FinWise 💰")
        
        # New Chat Button
        if st.button("🆕 New Chat", key="new_chat"):
            create_new_chat()
        
        render_file_upload_section()
        render_chat_history()

def create_new_chat():
    """Create a new chat session"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chat_id = f"chat_{timestamp}"
    
    st.session_state.chats[chat_id] = []
    st.session_state.active_chats.append(chat_id)
    st.session_state.current_chat = chat_id
    st.session_state.chat_history = []
    st.rerun()

def render_file_upload_section():
    """Render the file upload section"""
    st.subheader("📁 Upload Financial Documents")
    upload_option = st.selectbox("Choose Upload Type", 
        ["Single File", "Multiple Files"]
    )
    
    # Metadata inputs
    st.subheader("Document Metadata (Optional)")
    metadata = {
        "source": st.text_input("Source (e.g., annual_report, market_data)"),
        "company": st.text_input("Company Name or Ticker Symbol"),
        "year": st.text_input("Year")
    }
    
    handle_file_upload(upload_option, metadata)

def handle_file_upload(upload_option, metadata):
    """Handle file upload based on selected option"""
    if upload_option == "Single File":
        uploaded_file = st.file_uploader(
            "Upload a file", 
            type=['txt', 'pdf', 'doc', 'docx', 'csv', 'xlsx', 'json']
        )
        if uploaded_file:
            process_uploaded_file(uploaded_file, metadata)
    else:
        uploaded_files = st.file_uploader(
            "Upload multiple files", 
            accept_multiple_files=True,
            type=['txt', 'pdf', 'doc', 'docx', 'csv', 'xlsx', 'json']
        )
        if uploaded_files:
            for file in uploaded_files:
                process_uploaded_file(file, metadata)

def process_uploaded_file(file, metadata):
    """Process an uploaded file"""
    if file.name not in [f.name for f in st.session_state.uploaded_files]:
        st.session_state.uploaded_files.append(file)
        st.success(f"Added {file.name}")
        
        # Process the file
        file_path = DocumentProcessor.save_uploaded_file(file.getbuffer(), file.name)
        documents = DocumentProcessor.process_file(file_path, metadata)
        split_docs = DocumentProcessor.split_documents(documents)
        
        # Add to vector store
        assistant = FinancialAssistant()
        assistant.ingest_documents(split_docs)

def render_chat_history():
    """Render the chat history section"""
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