"""
HTML Render Example
===================

This example demonstrates how to use the HTML rendering feature
to display matplotlib plots and interactive HTML content in chat.

Usage:
    # In your agent handler:
    
    # For matplotlib plots
    import matplotlib.pyplot as plt
    plt.plot([1, 2, 3], [1, 4, 9])
    session.html.send_figure(plt)
    
    # For raw HTML
    session.html.send("<div>Hello World</div>")
    
    # For Plotly (if installed)
    import plotly.express as px
    fig = px.bar(x=['A', 'B', 'C'], y=[10, 20, 30])
    session.html.send_plotly(fig)
"""

# Example mock agent handler showing the HTML feature

def example_matplotlib_handler(session):
    """Example: Send a matplotlib plot to chat."""
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Create sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
    plt.fill_between(x, y, alpha=0.3)
    plt.xlabel('X Axis')
    plt.ylabel('Y Axis')
    plt.title('Sine Wave Example')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Send to chat - this converts to SVG and displays in iframe
    session.html.send_figure(plt)
    
    # Stream some text after
    session.stream("Here's the sine wave plot you requested!")


def example_bar_chart_handler(session):
    """Example: Send a bar chart."""
    import matplotlib.pyplot as plt
    
    categories = ['Product A', 'Product B', 'Product C', 'Product D']
    values = [25, 40, 30, 55]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=2)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                str(value), ha='center', va='bottom', fontweight='bold')
    
    ax.set_ylabel('Sales (units)')
    ax.set_title('Q4 Sales by Product')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Send the figure
    session.html.send_figure(fig)
    session.stream("The bar chart shows Q4 sales performance across products.")


def example_raw_html_handler(session):
    """Example: Send raw HTML content."""
    
    # You can send any HTML - it will be sandboxed in an iframe
    html_content = """
    <div style="padding: 20px; font-family: system-ui;">
        <h2 style="color: #333; margin-bottom: 16px;">Custom HTML Content</h2>
        <p style="color: #666;">This is raw HTML rendered in a sandboxed iframe.</p>
        <div style="display: flex; gap: 10px; margin-top: 16px;">
            <div style="background: #FF6B6B; color: white; padding: 12px 24px; border-radius: 8px;">
                Item 1
            </div>
            <div style="background: #4ECDC4; color: white; padding: 12px 24px; border-radius: 8px;">
                Item 2
            </div>
            <div style="background: #45B7D1; color: white; padding: 12px 24px; border-radius: 8px;">
                Item 3
            </div>
        </div>
    </div>
    """
    
    session.html.send(html_content)
    session.stream("Here's some custom HTML content!")


def example_plotly_handler(session):
    """Example: Send a Plotly interactive chart."""
    try:
        import plotly.express as px
        
        # Create an interactive Plotly chart
        df = px.data.gapminder().query("year == 2007")
        fig = px.scatter(
            df, 
            x="gdpPercap", 
            y="lifeExp",
            size="pop",
            color="continent",
            hover_name="country",
            log_x=True,
            title="GDP vs Life Expectancy (2007)"
        )
        
        # Send Plotly figure - this creates fully interactive chart
        session.html.send_plotly(fig)
        session.stream("Here's an interactive Plotly scatter plot!")
        
    except ImportError:
        session.stream("Plotly is not installed. Install with: pip install plotly")


# The markers that are generated:
# [orca.html.start]<html content>[orca.html.end]
#
# These are rendered by OrcaHtml.vue component in orca-components
# which displays the content in a sandboxed iframe for security.
