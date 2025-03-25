# FinWise - Financial Assistant

A GenAI-powered financial assistant that helps users make better investing decisions by answering questions and providing guidance.

## Setup

1. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```

2. Set up PostgreSQL:
   Make sure you have PostgreSQL running with the correct credentials as specified in the `DB_CONNECTION` variable in `main.py`.

3. Set your Google API key:
   ```
   export GOOGLE_API_KEY="your_api_key_here"
   ```

## Running the Application

### Streamlit UI

Run the Streamlit application:

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
