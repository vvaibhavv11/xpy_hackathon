from typing import List, Dict, Any, Optional, Union, Tuple
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from io import StringIO

# Schema definitions for tool inputs
class CSVVisualizationInput(BaseModel):
    chart_type: str = Field(
        description="Type of chart (line, bar, scatter, pie, area, box, violin, histogram)"
    )
    csv_data: str = Field(description="CSV data as a string")
    x_column: str = Field(description="Column name for x-axis")
    y_column: str = Field(description="Column name for y-axis")
    title: str = Field(description="Title of the chart")
    color_column: Optional[str] = Field(None, description="Column name for color grouping")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

# Tool implementations
@tool(response_format="content_and_artifact")
def create_csv_visualization(
    chart_type: str,
    csv_data: str,
    x_column: str,
    y_column: str,
    title: str,
    color_column: Optional[str] = None
) -> Tuple[str, str]:
    """Create a visualization from CSV data using Plotly.
    
    Args:
        chart_type: Type of chart (line, bar, scatter, pie, area, box, violin, histogram)
        csv_data: CSV data as a string
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        title: Title of the chart
        color_column: Optional column name for color grouping
    
    Returns:
        A tuple containing (description, HTML string) of the visualization
    """
    try:
        # Convert CSV string to DataFrame
        df = pd.read_csv(StringIO(csv_data))
        
        # Validate columns exist
        for col in [x_column, y_column]:
            if col not in df.columns:
                return f"Error: Column '{col}' not found in CSV data", ""
        if color_column and color_column not in df.columns:
            return f"Error: Color column '{color_column}' not found in CSV data", ""
        
        # Create figure based on chart type
        fig = None
        
        if chart_type.lower() == 'line':
            fig = px.line(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type.lower() == 'bar':
            fig = px.bar(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type.lower() == 'scatter':
            fig = px.scatter(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type.lower() == 'pie':
            fig = px.pie(df, values=y_column, names=x_column, title=title)
        elif chart_type.lower() == 'area':
            fig = px.area(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type.lower() == 'box':
            fig = px.box(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type.lower() == 'violin':
            fig = px.violin(df, x=x_column, y=y_column, color=color_column, title=title)
        elif chart_type.lower() == 'histogram':
            fig = px.histogram(df, x=x_column, color=color_column, title=title)
        else:
            return f"Error: Unsupported chart type '{chart_type}'", ""
        
        # Update layout for dark mode and responsiveness
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=80, b=50),
            height=500,
            width=None  # Responsive width
        )
        
        # Add hover tooltips
        fig.update_traces(
            hovertemplate="<br>".join([
                f"{x_column}: %{{x}}",
                f"{y_column}: %{{y}}",
                "<extra></extra>"
            ])
        )
        
        # Convert to HTML
        html = fig.to_html(
            include_plotlyjs="cdn",
            full_html=False,
            config={
                'displayModeBar': False,
                'responsive': True
            }
        )
        
        description = f"Created a {chart_type} chart titled '{title}' using columns {x_column} and {y_column}"
        if color_column:
            description += f", grouped by {color_column}"
        print("--------------------------------description")
        print(description)
        print("--------------------------------html")
        print(html)
        print("--------------------------------")
        return description, html
        
    except Exception as e:
        return f"Error creating visualization from CSV: {str(e)}", ""

# Function to get all available tools
def get_financial_tools() -> List[BaseTool]:
    """Get a list of all available financial tools."""
    return [
        create_csv_visualization
    ] 