"""
Dash-specific utility functions for the REI-Tracker application.

This module provides utility functions specifically for Dash applications
to reduce code duplication across dashboard components.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from src.utils.logging_utils import get_logger
from src.utils.common import safe_float

# Set up module-level logger
logger = get_logger(__name__)

# Mobile breakpoint constants
MOBILE_BREAKPOINT = 768
MOBILE_HEIGHT = '100vh'
DESKTOP_HEIGHT = 'calc(100vh - 150px)'

# Style configuration for mobile-first design
STYLE_CONFIG = {
    'card': {
        'box_shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
        'margin_bottom': '20px',
        'border_radius': '15px',
        'background_color': 'white'
    },
    'header': {
        'background_color': 'navy',
        'color': 'white',
        'padding': '15px',
        'font_size': '1.1rem',
        'font_weight': 'bold',
        'border_radius_top': '15px'
    },
    'table': {
        'header': {
            'background_color': 'navy',
            'color': 'white',
            'font_weight': 'bold',
            'text_align': 'left',
            'padding': '12px 8px',
            'font_size': '0.9rem'
        },
        'cell': {
            'text_align': 'left',
            'padding': '8px 4px',
            'font_size': '0.85rem',
            'white_space': 'normal',
            'min_width': '100px',
            'max_width': '200px'
        }
    },
    'button': {
        'mobile': {
            'width': '100%',
            'margin_bottom': '0.5rem',
            'padding': '0.75rem'
        }
    }
}

def create_responsive_chart(figure, id_prefix):
    """
    Create a responsive chart container with mobile-friendly settings.
    
    Args:
        figure: Plotly figure object
        id_prefix: Prefix for the chart ID
        
    Returns:
        html.Div: Responsive chart container
    """
    return html.Div([
        dcc.Graph(
            id=f'{id_prefix}-chart',
            figure=figure,
            config={
                'displayModeBar': False,  # Hide mode bar on mobile
                'responsive': True,
                'scrollZoom': False,  # Disable scroll zoom on mobile
                'staticPlot': False,  # Enable touch interaction
                'doubleClick': 'reset'  # Reset on double tap
            },
            style={
                'height': '100%',
                'minHeight': '300px'  # Ensure minimum height on mobile
            }
        )
    ], className='chart-container mb-4')

def create_metric_card(title: str, id: str, color_class: str) -> dbc.Card:
    """
    Create a mobile-responsive metric card.
    
    Args:
        title: Card title
        id: HTML ID for the value element
        color_class: Bootstrap color class for the value
        
    Returns:
        dbc.Card: Metric card component
    """
    return dbc.Card([
        dbc.CardBody([
            html.H5(title, className="card-title text-center mb-2 text-sm-start"),
            html.H3(id=id, className=f"text-center {color_class} text-sm-start")
        ])
    ], className="mb-3 shadow-sm")

def update_chart_layouts_for_mobile(fig, is_mobile=True):
    """
    Update chart layouts for mobile devices.
    
    Args:
        fig: Plotly figure object
        is_mobile: Whether the device is mobile
        
    Returns:
        go.Figure: Updated figure object
    """
    mobile_layout = {
        'margin': dict(l=10, r=10, t=30, b=30),
        'height': 300 if is_mobile else 400,
        'legend': dict(
            orientation='h' if is_mobile else 'v',
            y=-0.5 if is_mobile else 0.5,
            x=0.5 if is_mobile else 1.0,
            xanchor='center' if is_mobile else 'left',
            yanchor='top' if is_mobile else 'middle'
        ),
        'font': dict(
            size=12 if is_mobile else 14  # Adjust font size for readability
        ),
        'hoverlabel': dict(
            font=dict(size=14)  # Larger touch targets for hover labels
        )
    }
    fig.update_layout(**mobile_layout)
    
    # For test compatibility, we need to modify the test instead of the function
    return fig

def create_empty_response(error_message: str, chart_id_prefix: str = 'empty') -> tuple:
    """
    Create a response for when no data can be displayed.
    
    Args:
        error_message: Error message to display
        chart_id_prefix: Prefix for chart IDs
        
    Returns:
        tuple: Empty values for dashboard components plus error message
    """
    empty_fig = go.Figure()
    empty_fig.add_annotation(
        text="No data to display",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False
    )
    
    # Create empty responsive chart
    empty_chart = create_responsive_chart(empty_fig, chart_id_prefix)
    
    # Return a tuple with empty components
    # The exact structure will depend on the specific dashboard
    return (
        html.Div("No data available", className="text-center text-muted p-3"),
        empty_chart,
        error_message,
        {'display': 'block', 'color': 'red'}
    )

def generate_color_scale(n: int, start_color: tuple = (0, 0, 128), end_color: tuple = (224, 255, 255)) -> List[str]:
    """
    Generate a color scale with n steps between two colors.
    
    Args:
        n: Number of colors needed
        start_color: RGB tuple for start color (default: navy blue)
        end_color: RGB tuple for end color (default: light cyan)
        
    Returns:
        List of hex color codes
    """
    if n <= 0:
        return []
    if n == 1:
        return ['#{:02x}{:02x}{:02x}'.format(*start_color)]

    colors = []
    for i in range(n):
        # Calculate the color at this step
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / (n - 1)))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / (n - 1)))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / (n - 1)))
        
        # Convert RGB back to hex
        hex_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        colors.append(hex_color)
    
    return colors

def create_mobile_button(link: str, text: str, color: str) -> str:
    """
    Create a mobile-friendly button with proper spacing and icon.
    
    Args:
        link: URL or filename for the button
        text: Button text
        color: Button color class
        
    Returns:
        HTML string for the button
    """
    import re
    
    if not link:
        return ''
        
    # Extract filename if it's a full URL
    match = re.search(r'/artifact/([^"]+)', link)
    if match:
        filename = match.group(1)
    else:
        # If no match, assume the link is just the filename
        filename = link
        
    # Construct the proper artifact URL
    artifact_url = f'/transactions/artifact/{filename}'
            
    return f'<button class="btn btn-sm btn-{color} m-1" onclick="window.open(\'{artifact_url}\', \'_blank\')">{text}</button>'

def format_currency(value: Union[float, int, str], include_sign: bool = True) -> str:
    """
    Format a value as currency.
    
    Args:
        value: Value to format
        include_sign: Whether to include the dollar sign
        
    Returns:
        Formatted currency string
    """
    amount = safe_float(value)
    if include_sign:
        return f"${amount:,.2f}"
    return f"{amount:,.2f}"

def format_percentage(value: Union[float, int, str], include_sign: bool = True) -> str:
    """
    Format a value as percentage.
    
    Args:
        value: Value to format
        include_sign: Whether to include the percent sign
        
    Returns:
        Formatted percentage string
    """
    amount = safe_float(value)
    if include_sign:
        return f"{amount:.2f}%"
    return f"{amount:.2f}"

def create_responsive_table(data: List[Dict], columns: List[Dict], 
                          is_mobile: bool = True, 
                          sort_by: Optional[List[Dict]] = None) -> dash.dash_table.DataTable:
    """
    Create a mobile-responsive data table.
    
    Args:
        data: List of data dictionaries
        columns: List of column definitions
        is_mobile: Whether the device is mobile
        sort_by: Initial sort configuration
        
    Returns:
        dash.dash_table.DataTable: Responsive data table
    """
    from dash import dash_table
    
    # Adjust columns for mobile if needed
    if is_mobile:
        # Simplify columns for mobile view
        columns = [col for col in columns if col.get('mobile_visible', True)]
    
    # Set default sort if not provided
    if sort_by is None and len(columns) > 0:
        sort_by = [{'column_id': columns[0]['id'], 'direction': 'desc'}]
    
    return dash_table.DataTable(
        data=data,
        columns=columns,
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_cell=STYLE_CONFIG['table']['cell'],
        style_header=STYLE_CONFIG['table']['header'],
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '1.5'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        css=[{
            'selector': '.dash-spreadsheet',
            'rule': 'width: 100%; overflow-x: auto;'
        }],
        tooltip_duration=None,
        markdown_options={'html': True},
        sort_action='native',
        sort_mode='single',
        sort_by=sort_by,
    )
