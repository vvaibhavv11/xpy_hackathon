STYLES = """
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
""" 