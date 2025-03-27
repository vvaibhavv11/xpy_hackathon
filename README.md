# FinWise - Financial Assistant

FinWise is an AI-powered financial assistant that helps users make informed financial decisions. It uses Gemini 1.5 Pro to provide clear, accurate financial information and explain complex financial concepts in simple terms.

## Features

- Chat-based interface for asking financial questions
- Document upload and processing for context-aware responses
- Support for multiple file formats (PDF, CSV, TXT, XLSX, JSON)
- Metadata tagging for better document organization
- Multiple chat sessions management
- Dark mode UI for comfortable usage

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Google API key for Gemini 1.5 Pro

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL database:
   ```
   docker run -d --name postgres-vector -p 6024:5432 -e POSTGRES_USER=langchain -e POSTGRES_PASSWORD=langchain -e POSTGRES_DB=langchain ankane/pgvector
   ```
4. Set your Google API key:
   ```
   export GOOGLE_API_KEY="your_api_key_here"
   ```

### Running the Application

Start the Streamlit app:

```
streamlit run streamlit_app.py
```

This will start the web interface where users can:
- Upload financial documents
- Chat with the financial assistant
- Get answers to their financial questions

### Command Line Usage

You can also use the application from the command line:

1. To ingest files:
   ```
   python main.py --ingest path/to/file1.csv path/to/file2.pdf
   ```

2. To query the assistant in interactive mode:
   ```
   python main.py
   ```

## Project Structure

- `main.py` - Core functionality for document processing and querying
- `streamlit_app.py` - Streamlit UI for user interaction
- `requirements.txt` - Dependencies for the project

## Supported File Types

- CSV (.csv)
- PDF (.pdf)
- Text (.txt)
- Excel (.xlsx, .xls)
- JSON (.json)
