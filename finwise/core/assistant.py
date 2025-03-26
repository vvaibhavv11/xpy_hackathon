from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from .config import LLM_CONFIG, FINANCIAL_EXPERT_PROMPT
from .database import setup_vector_store
from .visualization_tool import get_visualization_tool, get_visualization_base64_tool
from langchain_core.tools import Tool
from typing import List, Optional
import re
import json
import pandas as pd

class FinancialAssistant:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(**LLM_CONFIG)
        self.vector_store = setup_vector_store()
        self.prompt = PromptTemplate.from_template(FINANCIAL_EXPERT_PROMPT)
        self.tools = {
            "visualization": get_visualization_tool(),
            "visualization_base64": get_visualization_base64_tool()
        }

    def query(self, question: str) -> str:
        """Process a query and return the response"""
        try:
            # Check if this is a visualization request
            visualization_requested = any(keyword in question.lower() for keyword in 
                ["visualize", "visualization", "plot", "chart", "graph", "show me", "display"])
            
            # Get regular response from LLM
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
            content = response.content
            
            # If visualization is requested, try to extract data and create chart
            if visualization_requested:
                # Try to determine chart type from question
                chart_type = self._extract_chart_type(question)
                
                # Try to extract data from the question or from the response
                data = self._extract_data(question, content)
                
                if chart_type and data is not None:
                    # Extract columns based on data structure
                    columns = list(data[0].keys()) if isinstance(data, list) and len(data) > 0 else []
                    
                    # Determine x and y columns if available
                    x_column = columns[0] if len(columns) > 0 else None
                    y_column = columns[1] if len(columns) > 1 else None
                    
                    # Create title from question
                    title = self._create_title(question)
                    
                    # Generate HTML visualization (we're not using Kaleido for image export)
                    visualization_html = self.tools["visualization"].func(
                        chart_type=chart_type,
                        data=data,
                        title=title,
                        x_column=x_column,
                        y_column=y_column
                    )
                    
                    # Combine text and visualization
                    return f"{content}\n\nHere's the visualization you requested:\n\n{visualization_html}"
            
            return content
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or rephrase your question."

    def ingest_documents(self, documents):
        """Add documents to the vector store"""
        self.vector_store.add_documents(documents)
        
    def get_tools(self) -> List[Tool]:
        """Get all available tools"""
        return list(self.tools.values())
        
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool by name"""
        return self.tools.get(tool_name)
    
    def _extract_chart_type(self, text: str) -> str:
        """Extract chart type from text"""
        chart_types = {
            "bar": ["bar chart", "bar graph", "bar plot"],
            "line": ["line chart", "line graph", "line plot", "trend"],
            "pie": ["pie chart", "pie graph", "pie plot", "distribution"],
            "scatter": ["scatter plot", "scatter chart", "scatter graph", "correlation"],
            "histogram": ["histogram", "distribution"],
            "box": ["box plot", "box chart", "box graph"],
            "heatmap": ["heatmap", "heat map", "correlation matrix"]
        }
        
        text = text.lower()
        for chart_type, keywords in chart_types.items():
            if any(keyword in text for keyword in keywords):
                return chart_type
        
        # Default to bar chart if no type specified
        return "bar"
    
    def _extract_data(self, question: str, response: str) -> List[dict]:
        """Try to extract data from question or response"""
        # Look for JSON data in the question or response
        json_pattern = r'\{.*\}|\[.*\]'
        json_match = re.search(json_pattern, question, re.DOTALL)
        
        if not json_match:
            json_match = re.search(json_pattern, response, re.DOTALL)
        
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                if isinstance(data, dict):
                    # Convert single dict to list
                    return [data]
                return data
            except json.JSONDecodeError:
                pass
        
        # If no JSON data found, create some sample data
        return self._generate_sample_data(question)
    
    def _generate_sample_data(self, question: str) -> List[dict]:
        """Generate sample data based on the question"""
        if "expense" in question.lower() or "spending" in question.lower():
            return [
                {"Category": "Groceries", "Amount": 500},
                {"Category": "Rent", "Amount": 1500},
                {"Category": "Utilities", "Amount": 200},
                {"Category": "Entertainment", "Amount": 300},
                {"Category": "Transportation", "Amount": 250}
            ]
        elif "investment" in question.lower() or "portfolio" in question.lower():
            return [
                {"Asset": "Stocks", "Value": 10000},
                {"Asset": "Bonds", "Value": 5000},
                {"Asset": "Real Estate", "Value": 15000},
                {"Asset": "Cash", "Value": 2000},
                {"Asset": "Commodities", "Value": 3000}
            ]
        elif "stock" in question.lower() or "market" in question.lower():
            return [
                {"Month": "Jan", "Value": 100},
                {"Month": "Feb", "Value": 120},
                {"Month": "Mar", "Value": 110},
                {"Month": "Apr", "Value": 130},
                {"Month": "May", "Value": 150},
                {"Month": "Jun", "Value": 140}
            ]
        else:
            # Default data
            return [
                {"X": "A", "Y": 10},
                {"X": "B", "Y": 20},
                {"X": "C", "Y": 15},
                {"X": "D", "Y": 25},
                {"X": "E", "Y": 30}
            ]
    
    def _create_title(self, question: str) -> str:
        """Create a title from the question"""
        # Remove common phrases and clean up
        clean_question = question.replace("show me", "").replace("create", "").replace("visualize", "").strip()
        
        # Capitalize first letter
        if clean_question:
            return clean_question[0].upper() + clean_question[1:]
        
        return "Visualization" 