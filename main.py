import os
import sys
from typing import List, Dict, Any
import tempfile

# Set Google API key
if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = "AIzaSyBNLOW7Sel_KtuYAdIoqPR8RuQ89N22O14"

# Import LangChain components
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_core.runnables import RunnablePassthrough

# Document loaders
from langchain_community.document_loaders import (
    CSVLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    JSONLoader
)

# Database connection
DB_CONNECTION = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"
COLLECTION_NAME = "financial_docs"

# System prompt for financial assistant
FINANCIAL_EXPERT_PROMPT = """You are FinWise, an expert financial advisor with deep knowledge of investing, 
financial markets, and personal finance. Your goal is to help users make informed financial decisions.

When responding to questions:
1. Provide clear, accurate financial information
2. Explain complex financial concepts in simple terms
3. Consider the user's best interests and financial well-being
4. Acknowledge the limitations of your advice (you're not a licensed financial advisor)
5. Focus on educational content rather than specific investment recommendations
6. When discussing investments, explain risks, potential returns, and time horizons
7. For Indian users, be aware of the specific financial products, regulations, and market conditions in India

Remember that financial literacy levels vary widely, so tailor your responses to be accessible 
while remaining informative and accurate.

Use the following context to inform your response:
{context}

Question: {question}

Helpful Answer:"""

def setup_llm_and_embeddings():
    """Initialize the language model and embeddings"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0.2,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    return llm, embeddings

def setup_vector_store(embeddings):
    """Initialize the vector store"""
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
    )
    
    return vector_store

def get_loader_for_file(file_path: str):
    """Return the appropriate loader based on file extension"""
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'csv':
        return CSVLoader(file_path=file_path)
    elif file_extension == 'pdf':
        return PyPDFLoader(file_path=file_path)
    elif file_extension in ['txt', 'md']:
        return TextLoader(file_path=file_path)
    elif file_extension in ['xlsx', 'xls']:
        return UnstructuredExcelLoader(file_path=file_path)
    elif file_extension == 'json':
        return JSONLoader(
            file_path=file_path,
            jq_schema='.[]',
            text_content=False
        )
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

def process_file(file_path: str, metadata: Dict[str, Any] = None) -> List[Document]:
    """Process a file and return documents with metadata"""
    try:
        loader = get_loader_for_file(file_path)
        documents = loader.load()
        
        # Add metadata to each document
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
                
                # Add metadata to content for better retrieval
                metadata_str = " ".join([f"{k}: {v}" for k, v in metadata.items()])
                doc.page_content = f"{metadata_str}\n{doc.page_content}"
        
        return documents
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return []

def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into smaller chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    
    return text_splitter.split_documents(documents)

def save_uploaded_file(file_data, file_name=None):
    """Save uploaded file data to a temporary file"""
    temp_dir = tempfile.mkdtemp()
    if not file_name:
        file_name = "uploaded_file"
    file_path = os.path.join(temp_dir, file_name)
    
    with open(file_path, 'wb') as f:
        f.write(file_data)
    
    return file_path

def ingest_files(file_paths: List[str], metadata_list: List[Dict[str, Any]] = None):
    """Ingest files into the vector store"""
    llm, embeddings = setup_llm_and_embeddings()
    vector_store = setup_vector_store(embeddings)
    
    all_documents = []
    
    for i, file_path in enumerate(file_paths):
        metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
        documents = process_file(file_path, metadata)
        all_documents.extend(documents)
    
    # Split documents into chunks
    split_docs = split_documents(all_documents)
    
    # Add documents to vector store
    vector_store.add_documents(split_docs)
    
    return len(split_docs)

def query_financial_assistant(query: str):
    """Query the financial assistant"""
    llm, embeddings = setup_llm_and_embeddings()
    vector_store = setup_vector_store(embeddings)
    
    try:
        # Create prompt template
        prompt = PromptTemplate.from_template(FINANCIAL_EXPERT_PROMPT)
        
        # Create retriever with error handling
        retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 10}
        )
        
        # Create QA chain
        qa_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
        )
        
        # Get response with timeout
        response = qa_chain.invoke(query)
        return response.content
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again or rephrase your question."

def main():
    print("FinWise - Financial Assistant")
    print("============================")
    
    # Example usage
    if len(sys.argv) > 1 and sys.argv[1] == "--ingest":
        # Ingest mode
        print("Ingesting files...")
        # Example: python main.py --ingest file1.csv file2.pdf
        files = sys.argv[2:]
        if not files:
            print("No files specified for ingestion")
            return
        
        count = ingest_files(files)
        print(f"Successfully ingested {count} document chunks")
    else:
        # Query mode
        while True:
            query = input("\nAsk a financial question (or 'exit' to quit): ")
            if query.lower() in ['exit', 'quit', 'q']:
                break
                
            print("\nThinking...")
            response = query_financial_assistant(query)
            print(f"\n{response}")

if __name__ == "__main__":
    main()
