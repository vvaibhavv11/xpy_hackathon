import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Any, Union
from langchain_core.tools import Tool
import base64
from io import BytesIO

# Set default for Kaleido availability
has_kaleido = False

# Try to import kaleido but don't require it
try:
    import kaleido
    has_kaleido = True
except ImportError:
    # We'll use HTML as fallback, so no need to raise an error
    pass

class PlotlyVisualizationTool:
    """Tool for creating visualizations using Plotly."""
    
    def __init__(self):
        """Initialize the visualization tool."""
        self.name = "visualization_tool"
    
    def create_visualization(self, 
                            chart_type: str, 
                            data: Union[str, List[Dict[str, Any]], pd.DataFrame],
                            title: str = "",
                            x_label: str = "",
                            y_label: str = "",
                            x_column: Optional[str] = None,
                            y_column: Optional[str] = None,
                            color_column: Optional[str] = None,
                            size_column: Optional[str] = None,
                            category_column: Optional[str] = None,
                            height: int = 500,
                            width: int = 800) -> str:
        """
        Create a visualization using Plotly.
        
        Args:
            chart_type: Type of chart (bar, line, pie, scatter, histogram, box, heatmap)
            data: JSON string, list of dictionaries, or pandas DataFrame containing the data
            title: Title of the chart
            x_label: Label for the x-axis
            y_label: Label for the y-axis
            x_column: Column to use for x-axis
            y_column: Column to use for y-axis
            color_column: Column to use for color differentiation
            size_column: Column to use for size in scatter plots
            category_column: Column to use for categories in pie charts
            height: Height of the chart in pixels
            width: Width of the chart in pixels
            
        Returns:
            HTML string of the visualization or error message
        """
        try:
            # Parse data if it's a string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return "Error: Invalid JSON data format"
            
            # Convert to DataFrame if it's a list
            if isinstance(data, list):
                data = pd.DataFrame(data)
            
            # Create the appropriate chart based on chart_type
            fig = None
            
            if chart_type.lower() == 'bar':
                fig = px.bar(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'line':
                fig = px.line(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'pie':
                fig = px.pie(
                    data,
                    values=y_column,
                    names=category_column or x_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'scatter':
                fig = px.scatter(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    size=size_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'histogram':
                fig = px.histogram(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'box':
                fig = px.box(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'heatmap':
                fig = px.imshow(
                    data.pivot(index=y_column, columns=x_column, values=color_column or 'value'),
                    title=title,
                    height=height,
                    width=width
                )
            
            else:
                return f"Error: Unsupported chart type '{chart_type}'. Supported types: bar, line, pie, scatter, histogram, box, heatmap"
            
            # Update layout with labels
            fig.update_layout(
                xaxis_title=x_label or x_column,
                yaxis_title=y_label or y_column,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            # Convert to HTML
            html = fig.to_html(include_plotlyjs="cdn", full_html=False)
            return html
            
        except Exception as e:
            return f"Error creating visualization: {str(e)}"
    
    def create_visualization_base64(self, 
                                   chart_type: str, 
                                   data: Union[str, List[Dict[str, Any]], pd.DataFrame],
                                   title: str = "",
                                   x_label: str = "",
                                   y_label: str = "",
                                   x_column: Optional[str] = None,
                                   y_column: Optional[str] = None,
                                   color_column: Optional[str] = None,
                                   size_column: Optional[str] = None,
                                   category_column: Optional[str] = None,
                                   height: int = 500,
                                   width: int = 800) -> str:
        """
        Create a visualization and return it as a base64-encoded PNG.
        
        Parameters are the same as create_visualization.
        
        Returns:
            Base64-encoded PNG image string or error message
        """
        try:
            # Parse data if it's a string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return "Error: Invalid JSON data format"
            
            # Convert to DataFrame if it's a list
            if isinstance(data, list):
                data = pd.DataFrame(data)
            
            # Create the appropriate chart based on chart_type
            fig = None
            
            # (Same chart creation code as in create_visualization)
            if chart_type.lower() == 'bar':
                fig = px.bar(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'line':
                fig = px.line(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'pie':
                fig = px.pie(
                    data,
                    values=y_column,
                    names=category_column or x_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'scatter':
                fig = px.scatter(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    size=size_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'histogram':
                fig = px.histogram(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'box':
                fig = px.box(
                    data,
                    x=x_column,
                    y=y_column,
                    color=color_column,
                    title=title,
                    height=height,
                    width=width
                )
            
            elif chart_type.lower() == 'heatmap':
                fig = px.imshow(
                    data.pivot(index=y_column, columns=x_column, values=color_column or 'value'),
                    title=title,
                    height=height,
                    width=width
                )
            
            else:
                return f"Error: Unsupported chart type '{chart_type}'. Supported types: bar, line, pie, scatter, histogram, box, heatmap"
            
            # Update layout with labels
            fig.update_layout(
                xaxis_title=x_label or x_column,
                yaxis_title=y_label or y_column,
                margin=dict(l=50, r=50, t=80, b=50)
            )
            
            # Convert to PNG base64
            # Check if kaleido is available
            if has_kaleido:
                # Use kaleido to generate image
                buffer = BytesIO()
                fig.write_image(buffer, format="png")
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                return f"data:image/png;base64,{img_base64}"
            else:
                # Fallback to HTML if kaleido is not available
                html = fig.to_html(include_plotlyjs="cdn", full_html=False)
                return f"Kaleido not available for PNG export. Using HTML visualization instead:\n\n{html}"
            
        except Exception as e:
            return f"Error creating visualization: {str(e)}"

def get_visualization_tool() -> Tool:
    """Get the visualization tool as a LangChain tool."""
    vis_tool = PlotlyVisualizationTool()
    
    return Tool(
        name="visualization_tool",
        func=vis_tool.create_visualization,
        description="""
        Create data visualizations using Plotly.
        
        Parameters:
        - chart_type (str): Type of chart (bar, line, pie, scatter, histogram, box, heatmap)
        - data (str or list): JSON string or list of dictionaries containing the data
        - title (str, optional): Title of the chart
        - x_label (str, optional): Label for the x-axis
        - y_label (str, optional): Label for the y-axis
        - x_column (str, optional): Column to use for x-axis
        - y_column (str, optional): Column to use for y-axis
        - color_column (str, optional): Column to use for color differentiation
        - size_column (str, optional): Column to use for size in scatter plots
        - category_column (str, optional): Column to use for categories in pie charts
        - height (int, optional): Height of the chart in pixels
        - width (int, optional): Width of the chart in pixels
        
        Returns HTML representation of the visualization.
        """,
    )

def get_visualization_base64_tool() -> Tool:
    """Get the base64 visualization tool as a LangChain tool."""
    vis_tool = PlotlyVisualizationTool()
    
    return Tool(
        name="visualization_base64_tool",
        func=vis_tool.create_visualization_base64,
        description="""
        Create data visualizations using Plotly and return as base64 encoded PNG image.
        
        Parameters:
        - chart_type (str): Type of chart (bar, line, pie, scatter, histogram, box, heatmap)
        - data (str or list): JSON string or list of dictionaries containing the data
        - title (str, optional): Title of the chart
        - x_label (str, optional): Label for the x-axis
        - y_label (str, optional): Label for the y-axis
        - x_column (str, optional): Column to use for x-axis
        - y_column (str, optional): Column to use for y-axis
        - color_column (str, optional): Column to use for color differentiation
        - size_column (str, optional): Column to use for size in scatter plots
        - category_column (str, optional): Column to use for categories in pie charts
        - height (int, optional): Height of the chart in pixels
        - width (int, optional): Width of the chart in pixels
        
        Returns base64 PNG image representation of the visualization.
        """,
    ) 