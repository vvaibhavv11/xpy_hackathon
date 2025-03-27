from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, ToolMessage
from .config import LLM_CONFIG, FINANCIAL_EXPERT_PROMPT
from .database import setup_vector_store
from langchain_core.tools import Tool
from typing import List, Optional
from .tools import get_financial_tools

class FinancialAssistant:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(**LLM_CONFIG)
        self.vector_store = setup_vector_store()
        self.prompt = PromptTemplate.from_template(FINANCIAL_EXPERT_PROMPT)
        self.tools = get_financial_tools()
        self.model_with_tools = self.llm.bind_tools(self.tools)
        self.tool_mapping = {
            "create_csv_visualization": self.tools[0],
        }
        self.messages = []

    def query(self, question: str) -> str:
        """Process a query and return the response"""
        try:
            # Get relevant documents from vector store
            docs = self.vector_store.similarity_search(
                question,
                k=10
            )
            print("--------------------------------docs")
            print(docs)
            print("--------------------------------")
            # Prepare context from retrieved documents
            context = "\n".join([doc.page_content for doc in docs])

            print("--------------------------------context")
            print(context)
            print("--------------------------------")
            
            # Format prompt with context and question
            formatted_prompt = self.prompt.format(
                context=context,
                question=question
            )
            print("--------------------------------formatted_prompt")
            print(formatted_prompt)
            print("--------------------------------")
            # Get response from LLM
            self.messages.append(HumanMessage(formatted_prompt))
            response = self.model_with_tools.invoke(self.messages)
            response.tool_calls
            if response.tool_calls:
                print("--------------------------------response.tool_calls")
                print(response.tool_calls)
                print("--------------------------------")
                for tool_call in response.tool_calls:
                    tool = self.tool_mapping[tool_call["name"]]
                    tool_output = tool.invoke(tool_call["args"])
                    # Handle tuple output from visualization tool
                    if isinstance(tool_output, tuple):
                        description, html = tool_output
                        # Store HTML in the message but add a note about the visualization
                        tool_message = f"{description}\n\nI've created a visualization for you! Click the '📊 Show/Hide Visualization' button above to view it.\n\n{html}"
                    else:
                        tool_message = tool_output
                    self.messages.append(ToolMessage(content=tool_message, tool_call_id=tool_call["id"]))

            main_response = self.model_with_tools.invoke(self.messages)
            print("--------------------------------main_response")
            print(main_response)
            print("--------------------------------")
            return main_response.content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or rephrase your question."

    def ingest_documents(self, documents):
        """Add documents to the vector store"""
        self.vector_store.add_documents(documents) 