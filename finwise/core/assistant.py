from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from .config import LLM_CONFIG, FINANCIAL_EXPERT_PROMPT
from .database import setup_vector_store

class FinancialAssistant:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(**LLM_CONFIG)
        self.vector_store = setup_vector_store()
        self.prompt = PromptTemplate.from_template(FINANCIAL_EXPERT_PROMPT)

    def query(self, question: str) -> str:
        """Process a query and return the response"""
        try:
            retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 5, "fetch_k": 10}
            )
            
            qa_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
            )
            
            response = qa_chain.invoke(question)
            return response.content
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or rephrase your question."

    def ingest_documents(self, documents):
        """Add documents to the vector store"""
        self.vector_store.add_documents(documents) 