import streamlit as st
import os
import tempfile
from main import ingest_files, query_financial_assistant

# Set page configuration
st.set_page_config(
    page_title="FinWise - Financial Assistant",
    page_icon="💰",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

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

# Sidebar for file upload
with st.sidebar:
    st.title("FinWise 💰")
    st.subheader("Upload Financial Documents")
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "pdf", "txt", "xlsx", "xls", "json"])
    
    # Metadata inputs
    st.subheader("Document Metadata (Optional)")
    source = st.text_input("Source (e.g., annual_report, market_data)")
    company = st.text_input("Company Name or Ticker Symbol")
    year = st.text_input("Year")
    
    if uploaded_file is not None and st.button("Upload and Process"):
        with st.spinner("Processing document..."):
            # Save the file
            file_path = save_uploaded_file(uploaded_file)
            
            if file_path:
                # Create metadata dictionary
                metadata = {}
                if source:
                    metadata["source"] = source
                if company:
                    metadata["company"] = company
                if year:
                    metadata["year"] = year
                
                # Ingest the file
                try:
                    metadata_list = [metadata] if metadata else None
                    count = ingest_files([file_path], metadata_list)
                    st.success(f"Successfully processed {count} document chunks from {uploaded_file.name}")
                    
                    # Clean up
                    os.unlink(file_path)
                except Exception as e:
                    st.error(f"Error processing file: {e}")

# Main chat interface
st.title("FinWise - Your Financial Assistant")
st.markdown("""
Ask me anything about investing, financial markets, or personal finance. 
I'm here to help you make informed financial decisions!
""")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_query = st.chat_input("Ask a financial question...")

if user_query:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = query_financial_assistant(user_query)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response}) 