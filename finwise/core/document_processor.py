from typing import List, Dict, Any
from pathlib import Path
import tempfile
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    CSVLoader, PyPDFLoader, TextLoader, 
    UnstructuredExcelLoader, JSONLoader
)
from .config import CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    @staticmethod
    def get_loader_for_file(file_path: str):
        """Return the appropriate loader based on file extension"""
        file_extension = Path(file_path).suffix.lower()[1:]
        
        loaders = {
            'csv': CSVLoader,
            'pdf': PyPDFLoader,
            'txt': TextLoader,
            'md': TextLoader,
            'xlsx': UnstructuredExcelLoader,
            'xls': UnstructuredExcelLoader,
            'json': lambda fp: JSONLoader(fp, jq_schema='.[]', text_content=False)
        }
        
        loader_class = loaders.get(file_extension)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {file_extension}")
            
        return loader_class(file_path)

    @staticmethod
    def process_file(file_path: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """Process a file and return documents with metadata"""
        try:
            loader = DocumentProcessor.get_loader_for_file(file_path)
            documents = loader.load()
            
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
                    metadata_str = " ".join([f"{k}: {v}" for k, v in metadata.items()])
                    doc.page_content = f"{metadata_str}\n{doc.page_content}"
            
            return documents
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return []

    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
        return text_splitter.split_documents(documents)

    @staticmethod
    def save_uploaded_file(file_data, file_name=None):
        """Save uploaded file data to a temporary file"""
        temp_dir = tempfile.mkdtemp()
        if not file_name:
            file_name = "uploaded_file"
        file_path = Path(temp_dir) / file_name
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return str(file_path) 