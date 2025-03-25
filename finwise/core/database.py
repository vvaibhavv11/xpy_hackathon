from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from .config import DB_CONNECTION, COLLECTION_NAME

def setup_vector_store():
    """Initialize and return the vector store"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
    )
    
    return vector_store 