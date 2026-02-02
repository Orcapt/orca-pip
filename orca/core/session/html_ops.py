"""
HTML Operations
===============

Handles HTML rendering operations for a session.
Ultra-focused: ONLY HTML handling for interactive content like plots.
"""

import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class HtmlOperations:
    """
    Manages HTML content streaming.
    
    Ultra-focused on HTML operations only.
    Single Responsibility: HTML rendering handling.
    
    Use cases:
    - Matplotlib/Plotly charts
    - Interactive visualizations
    - Custom HTML content
    """
    
    def __init__(self, stream_func):
        """
        Initialize HTML operations.
        
        Args:
            stream_func: Function to stream content
        """
        self._stream = stream_func
    
    def send(self, html: str) -> None:
        """
        Stream HTML content with Orca markers.
        
        The HTML will be rendered in a sandboxed iframe on the frontend
        for security isolation.
        
        Args:
            html: HTML content string
            
        Example:
            session.html.send("<div>Hello World</div>")
            session.html.send("<script>console.log('test')</script>")
        """
        if not html:
            logger.warning("HTML content is empty, skipping")
            return
        
        payload = f"[orca.html.start]{html}[orca.html.end]"
        self._stream(payload)
    
    def send_figure(self, figure: Any, format: str = "svg") -> None:
        """
        Send a matplotlib figure as HTML.
        
        Converts the figure to SVG (default) or PNG and wraps it in HTML
        for proper display.
        
        Args:
            figure: matplotlib figure or pyplot module
            format: Output format - 'svg' (default, vector) or 'png' (raster)
            
        Example:
            import matplotlib.pyplot as plt
            plt.plot([1, 2, 3], [1, 4, 9])
            plt.title("My Plot")
            session.html.send_figure(plt)
            
            # Or with a figure object
            fig, ax = plt.subplots()
            ax.bar(['A', 'B', 'C'], [10, 20, 30])
            session.html.send_figure(fig)
        """
        import io
        
        # Handle both pyplot module and figure objects
        if hasattr(figure, 'gcf'):
            # It's pyplot module, get current figure
            fig = figure.gcf()
        else:
            # It's already a figure object
            fig = figure
        
        if format == "svg":
            buffer = io.StringIO()
            fig.savefig(buffer, format='svg', bbox_inches='tight')
            content = buffer.getvalue()
            # Wrap SVG in a centered container
            html = f'''<div style="width:100%;display:flex;justify-content:center;align-items:center;padding:10px;">
{content}
</div>'''
        elif format == "png":
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            import base64
            encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
            html = f'''<div style="width:100%;display:flex;justify-content:center;align-items:center;padding:10px;">
<img src="data:image/png;base64,{encoded}" style="max-width:100%;height:auto;" />
</div>'''
        else:
            logger.error(f"Unsupported format: {format}. Use 'svg' or 'png'")
            return
        
        self.send(html)
        
        # Close the figure to free memory
        try:
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception:
            pass
    
    def send_plotly(self, figure: Any) -> None:
        """
        Send a Plotly figure as HTML.
        
        Converts the Plotly figure to standalone HTML.
        
        Args:
            figure: Plotly figure object
            
        Example:
            import plotly.express as px
            fig = px.bar(x=['A', 'B', 'C'], y=[10, 20, 30])
            session.html.send_plotly(fig)
        """
        try:
            html = figure.to_html(
                include_plotlyjs='cdn',
                full_html=False,
                config={'responsive': True}
            )
            # Wrap in container for proper sizing
            wrapped_html = f'''<div style="width:100%;min-height:400px;">
{html}
</div>'''
            self.send(wrapped_html)
        except Exception as e:
            logger.error(f"Failed to convert Plotly figure: {e}")
            raise
