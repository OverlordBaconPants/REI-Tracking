"""
Transactions dashboard for the REI-Tracker application.

This module provides a Dash-based interactive dashboard for viewing, filtering,
and reporting on property transactions, with mobile-responsive design and
comprehensive filtering capabilities.
"""

from typing import Dict, List, Optional, Tuple, Union, Any, Set
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from flask_login import current_user
import traceback
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import io
import zipfile
import os
import re
from urllib.parse import unquote

from src.services.transaction_service import TransactionService
from src.services.property_access_service import PropertyAccessService
from src.services.transaction_report_generator import TransactionReportGenerator
from src.utils.logging_utils import get_logger

# Set up module-level logger
logger = get_logger(__name__)

# Constants
MAX_DESCRIPTION_LENGTH = 500
VALID_TRANSACTION_TYPES = ['income', 'expense']
VALID_REIMBURSEMENT_STATUS = ['all', 'pending', 'in_progress', 'completed']
MIN_DATE = '2000-01-01'
MAX_FUTURE_DAYS = 30
MOBILE_BREAKPOINT = 768

# Mobile-first styling configuration
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

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple[bool, str]:
    """
    Validates the date range for transactions.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not start_date and not end_date:
            return True, ""

        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            min_date = datetime.strptime(MIN_DATE, '%Y-%m-%d')
            if start < min_date:
                return False, f"Start date cannot be before {MIN_DATE}"

        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            max_date = datetime.now() + timedelta(days=MAX_FUTURE_DAYS)
            if end > max_date:
                return False, f"End date cannot be more than {MAX_FUTURE_DAYS} days in the future"

        if start_date and end_date and start > end:
            return False, "Start date cannot be after end date"

        return True, ""
    except ValueError as e:
        return False, f"Invalid date format: {str(e)}"

def is_wholly_owned_by_user(property_data: dict, user_name: str) -> bool:
    """
    Checks if a property is wholly owned by the user.
    
    Args:
        property_data: Dictionary containing property information
        user_name: Name of the user to check
        
    Returns:
        True if the property is wholly owned by the user, False otherwise
    """
    logger.debug(f"Checking ownership for property: {property_data.get('address')} and user: {user_name}")
    
    partners = property_data.get('partners', [])
    if len(partners) == 1:
        partner = partners[0]
        is_user = partner.get('name', '').lower() == user_name.lower()
        equity = float(partner.get('equity_share', 0))
        return is_user and abs(equity - 100.0) < 0.01
    
    user_equity = sum(
        float(partner.get('equity_share', 0))
        for partner in partners
        if partner.get('name', '').lower() == user_name.lower()
    )
    
    return abs(user_equity - 100.0) < 0.01

def format_address(address: str, format_type: str = 'display') -> str:
    """
    Format an address for consistent display.
    
    Args:
        address: Full address string
        format_type: Type of formatting ('display', 'base', 'full')
        
    Returns:
        Formatted address string
    """
    if not address:
        return "Unknown"
        
    parts = address.split(',')
    
    if format_type == 'base':
        # Return just the first part (street address)
        return parts[0].strip()
    elif format_type == 'display':
        # Return first two parts (street address, city)
        if len(parts) >= 2:
            return f"{parts[0].strip()}, {parts[1].strip()}"
        return parts[0].strip()
    else:
        # Return full address
        return address

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
            
    return f'''<button class="btn btn-sm btn-{color} m-1" 
            onclick="window.open('{artifact_url}', '_blank')">
            {text}</button>'''

def create_transactions_dash(flask_app):
    """
    Creates and configures the mobile-first Dash application for transaction management.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dash.Dash: Configured Dash application instance
    """
    try:
        logger.info("Creating transactions dashboard")
        
        # Initialize Dash app
        dash_app = dash.Dash(
            __name__,
            server=flask_app,
            routes_pathname_prefix='/dashboards/_dash/transactions/',
            requests_pathname_prefix='/dashboards/_dash/transactions/',
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        
        logger.debug("Dash app initialized successfully")

        # Define the mobile-first layout
        dash_app.layout = dbc.Container([
            # Responsive viewport meta tag
            html.Meta(name="viewport", content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
            
            # State management stores
            dcc.Store(id='refresh-trigger', storage_type='memory'),
            dcc.Store(id='filter-options', storage_type='session'),
            dcc.Store(id='viewport-size', data={'width': 1200, 'is_mobile': False}),
            
            # Flash messages and error display
            html.Div(id='flash-message-container', className='flash-messages my-2'),
            dbc.Alert(id='error-display', is_open=False, color="danger", className='mb-3'),
            
            # Filters Card
            dbc.Card([
                dbc.CardHeader("Filter Transactions", style=STYLE_CONFIG['header']),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Property", className='mb-1'),
                            dcc.Dropdown(
                                id='property-filter',
                                placeholder='Select Property',
                                className='mb-3'
                            )
                        ], xs=12, md=6),
                        dbc.Col([
                            dbc.Label("Transaction Type", className='mb-1'),
                            dbc.RadioItems(
                                id='type-filter',
                                options=[
                                    {'label': 'All', 'value': 'all'},
                                    {'label': 'Incomes', 'value': 'income'},
                                    {'label': 'Expenses', 'value': 'expense'}
                                ],
                                value='all',
                                inline=True,
                                className='mb-3'
                            )
                        ], xs=12, md=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div(
                                [
                                    dbc.Label("Reimbursement Status", className='mb-1'),
                                    dcc.Dropdown(
                                        id='reimbursement-filter',
                                        options=[
                                            {'label': 'All', 'value': 'all'},
                                            {'label': 'Pending', 'value': 'pending'},
                                            {'label': 'In Progress', 'value': 'in_progress'},
                                            {'label': 'Completed', 'value': 'completed'}
                                        ],
                                        value='all',
                                        className='mb-3'
                                    )
                                ],
                                id='reimbursement-filter-container',
                                style={'display': 'block'}
                            )
                        ], xs=12, md=6),
                        dbc.Col([
                            dbc.Label("Date Range", className='mb-1'),
                            dbc.Row([
                                dbc.Col([
                                    dcc.DatePickerRange(
                                        id='date-range',
                                        className='mb-3',
                                        style={'width': '100%'}
                                    )
                                ], xs=8),  # Take 8/12 of the width
                                dbc.Col([
                                    dbc.Button(
                                        [html.I(className="bi bi-calendar-x me-1"), "Clear"],  # Shorter text with icon
                                        id="clear-date-range",
                                        color="secondary",
                                        size="md",
                                        className="w-100 mb-3",
                                        style={'height': '38px'}  # Match the height of the date picker
                                    )
                                ], xs=4)  # Take 4/12 of the width
                            ], className="g-0")  # Remove gutters between columns
                        ], xs=12, md=6)
                    ]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Search Description", className='mb-1'),
                            dbc.Input(
                                id='description-search',
                                type='text',
                                placeholder='Enter keywords...',
                                debounce=True,
                                className='mb-3'
                            )
                        ], xs=12)
                    ])
                ])
            ], className='mb-4', style=STYLE_CONFIG['card']),
            
            # Actions Card
            dbc.Card([
                dbc.CardHeader("Actions", style=STYLE_CONFIG['header']),
                dbc.CardBody([
                    dbc.Row([
                        # PDF Report Button
                        dbc.Col([
                            dbc.Button(
                                [html.I(className="bi bi-file-pdf me-2"), "PDF Report"],
                                id="download-pdf-btn",
                                color="primary",
                                className="me-2 mb-2 w-100",
                                n_clicks=0
                            )
                        ], xs=12, sm=6, md=4),
                        
                        # Documents ZIP Button
                        dbc.Col([
                            dbc.Button(
                                [html.I(className="bi bi-file-zip me-2"), "Download Documents"],
                                id="download-zip-btn",
                                color="secondary",
                                className="me-2 mb-2 w-100",
                                n_clicks=0
                            )
                        ], xs=12, sm=6, md=4),
                        
                        # Add Transaction Button
                        dbc.Col([
                            html.A(
                                dbc.Button(
                                    [html.I(className="bi bi-plus-lg me-2"), "Add Transaction"],
                                    color="success",
                                    className="w-100"
                                ),
                                href="/transactions/add",
                                className="no-decoration",  # Add this class to remove underline
                                target="_parent"  # Important for proper page navigation
                            )
                        ], xs=12, md=4),
                    ]),
                    
                    # Status and Download components
                    html.Div(id="download-status", className="mt-2"),
                    dcc.Download(id="download-pdf"),
                    dcc.Download(id="download-zip")
                ])
            ], className='mb-4', style=STYLE_CONFIG['card']),
            
            # Transactions Table Card
            dbc.Card([
                dbc.CardHeader(
                    html.H5(id='transactions-header', className='mb-0'),
                    style=STYLE_CONFIG['header']
                ),
                dbc.CardBody([
                    # Info message for wholly-owned properties
                    html.Div(id='reimbursement-info', className='mb-3'),
                    
                    # Mobile-optimized table
                    dash_table.DataTable(
                        id='transactions-table',
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
                            },
                            {
                                'if': {
                                    'column_id': 'amount',
                                    'filter_query': '{type} eq "income"'
                                },
                                'color': 'green'
                            },
                            {
                                'if': {
                                    'column_id': 'amount',
                                    'filter_query': '{type} eq "expense"'
                                },
                                'color': 'red'
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
                        sort_by=[{'column_id': 'date', 'direction': 'desc'}],
                    )
                ])
            ], style=STYLE_CONFIG['card'])
        ], fluid=True, className='p-3')

        @dash_app.callback(
            Output('viewport-size', 'data'),
            [Input('refresh-trigger', 'data')],
            [State('viewport-size', 'data')]
        )
        def update_viewport_size(_, current_size):
            """Update viewport size data for responsive adjustments."""
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate
            
            # We can't access window.innerWidth server-side
            # Just return a default value for now
            width = current_size.get('width', 1200)
            
            return {'width': width, 'is_mobile': width < MOBILE_BREAKPOINT}

        @dash_app.callback(
            [Output('date-range', 'start_date'),
            Output('date-range', 'end_date')],
            [Input('clear-date-range', 'n_clicks')],
            [State('filter-options', 'data'),
            State('date-range', 'start_date'),
            State('date-range', 'end_date')]
        )
        def manage_date_range(clear_clicks, filter_data, current_start, current_end):
            """
            Handle clearing date range and initial loading.
            
            Args:
                clear_clicks: Number of clicks on the clear button
                filter_data: Stored filter options
                current_start: Current start date
                current_end: Current end date
                
            Returns:
                Tuple of (start_date, end_date)
            """
            ctx = dash.callback_context
            
            # Check which input triggered the callback
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
            
            if triggered_id == 'clear-date-range':
                # Clear button was clicked
                return None, None
            elif not current_start and not current_end and filter_data:
                # Only restore from filter_options on initial load when dates are empty
                return filter_data.get('start_date'), filter_data.get('end_date')
            
            # Return current values to prevent unnecessary updates
            return current_start, current_end

        @dash_app.callback(
            Output('property-filter', 'options'),
            Input('refresh-trigger', 'data')
        )
        def populate_property_dropdown(refresh_trigger):
            """
            Populate the property dropdown with available properties.
            
            Args:
                refresh_trigger: Trigger to refresh the dropdown
                
            Returns:
                List of property options
            """
            try:
                with flask_app.app_context():
                    # Check if current_user is authenticated and has necessary attributes
                    if hasattr(current_user, 'id') and hasattr(current_user, 'name'):
                        property_access_service = PropertyAccessService()
                        properties = property_access_service.get_accessible_properties(current_user.id)
                    else:
                        logger.warning("User not authenticated or missing attributes")
                        return []
                
                if not properties:
                    return []
                
                # Create property options with standardized display
                property_options = [{'label': 'All Properties', 'value': 'all'}]
                
                for prop in properties:
                    if prop.address:
                        display_address = format_address(prop.address, 'display')
                        property_options.append({
                            'label': display_address,
                            'value': prop.id  # Use property ID as value
                        })
                
                return property_options
                
            except Exception as e:
                logger.error(f"Error populating property dropdown: {str(e)}")
                logger.error(f"Exception details: {traceback.format_exc()}")
                return []

        @dash_app.callback(
            [Output('transactions-table', 'data'),
            Output('transactions-header', 'children'),
            Output('transactions-table', 'columns'),
            Output('error-display', 'children'),
            Output('error-display', 'is_open')],
            [Input('refresh-trigger', 'data'),
            Input('property-filter', 'value'),
            Input('type-filter', 'value'),
            Input('reimbursement-filter', 'value'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date'),
            Input('description-search', 'value'),
            Input('viewport-size', 'data')]
        )
        def update_table(refresh_trigger, property_id, transaction_type, 
                        reimbursement_status, start_date, end_date, 
                        description_search, viewport):
            """
            Update the transactions table based on filters.
            
            Args:
                refresh_trigger: Trigger to refresh the table
                property_id: Selected property ID
                transaction_type: Selected transaction type
                reimbursement_status: Selected reimbursement status
                start_date: Selected start date
                end_date: Selected end date
                description_search: Description search text
                viewport: Viewport size data
                
            Returns:
                Tuple of (table_data, header_text, table_columns, error_text, error_visible)
            """
            try:
                # Get device type
                is_mobile = viewport.get('is_mobile', True) if viewport else True
                
                # Validate date range
                is_valid, error_message = validate_date_range(start_date, end_date)
                if not is_valid:
                    return [], "Invalid Date Range", [], error_message, True
                
                # Create filters dictionary
                filters = {}
                
                if property_id and property_id != 'all':
                    filters['property_id'] = property_id
                
                if transaction_type and transaction_type != 'all':
                    filters['type'] = transaction_type
                
                if reimbursement_status and reimbursement_status != 'all':
                    filters['reimbursement_status'] = reimbursement_status
                
                if start_date:
                    filters['start_date'] = start_date
                
                if end_date:
                    filters['end_date'] = end_date
                
                if description_search:
                    filters['description'] = description_search
                
                # Get transactions
                with flask_app.app_context():
                    if hasattr(current_user, 'id'):
                        transaction_service = TransactionService()
                        transactions = transaction_service.get_transactions(current_user.id, filters)
                    else:
                        logger.warning("User not authenticated")
                        return [], "Authentication Required", [], "Please log in to view transactions", True
                
                if not transactions:
                    header = "No transactions found"
                    if description_search:
                        header += f" matching '{description_search}'"
                    return [], header, [], "", False
                
                # Convert transactions to DataFrame
                df = pd.DataFrame([t.to_dict() for t in transactions])
                
                # Format data for display
                df = format_transactions_for_display(df, property_id, is_mobile)
                
                # Create columns based on device type
                columns = create_table_columns(property_id, df, is_mobile)
                
                # Create header with filter information
                header = create_table_header(transaction_type, property_id, reimbursement_status, 
                                           start_date, end_date, description_search)
                
                # Prepare final data
                final_data = df.to_dict('records')
                
                return (
                    final_data,
                    header,
                    columns,
                    "",
                    False
                )
                
            except Exception as e:
                logger.error(f"Error in update_table: {str(e)}")
                logger.error(traceback.format_exc())
                return [], "Error", [], f"An error occurred: {str(e)}", True

        @dash_app.callback(
            [Output('reimbursement-filter-container', 'style'),
            Output('reimbursement-filter', 'value'),
            Output('reimbursement-info', 'children')],
            [Input('property-filter', 'value'),
            Input('refresh-trigger', 'data')],
            [State('filter-options', 'data')]
        )
        def update_reimbursement_controls(property_id, trigger, filter_data):
            """
            Update reimbursement controls based on property selection.
            
            Args:
                property_id: Selected property ID
                trigger: Refresh trigger
                filter_data: Stored filter options
                
            Returns:
                Tuple of (container_style, filter_value, info_message)
            """
            try:
                # Default values
                style = {'display': 'block'}
                filter_value = 'all'
                info = None
                
                if property_id and property_id != 'all':
                    with flask_app.app_context():
                        if hasattr(current_user, 'id') and hasattr(current_user, 'name'):
                            property_access_service = PropertyAccessService()
                            properties = property_access_service.get_accessible_properties(current_user.id)
                            property_data = next((p for p in properties if p.id == property_id), None)
                            
                            if property_data and is_wholly_owned_by_user(property_data.to_dict(), current_user.name):
                                return (
                                    {'display': 'none'},
                                    'all',
                                    dbc.Alert(
                                        "Reimbursement elements are hidden because this property is wholly owned.",
                                        color="info",
                                        dismissable=True
                                    )
                                )
                
                # If we have filter data and no property is selected, restore the reimbursement filter
                if not property_id and filter_data and 'reimbursement_status' in filter_data:
                    filter_value = filter_data.get('reimbursement_status', 'all')
                
                return style, filter_value, info
                
            except Exception as e:
                logger.error(f"Error updating reimbursement controls: {str(e)}")
                return {'display': 'block'}, 'all', None

        @dash_app.callback(
            Output("download-pdf", "data"),
            [Input("download-pdf-btn", "n_clicks")],
            [State("transactions-table", "data"),
            State("property-filter", "value"),
            State("date-range", "start_date"),
            State("date-range", "end_date")]
        )
        def generate_pdf_report(n_clicks, transactions_data, property_id, start_date, end_date):
            """
            Generate PDF report for transactions.
            
            Args:
                n_clicks: Number of clicks on the download button
                transactions_data: Transaction data from the table
                property_id: Selected property ID
                start_date: Selected start date
                end_date: Selected end date
                
            Returns:
                PDF report data
            """
            if not n_clicks or not transactions_data:
                return None
            
            try:
                logger.debug(f"Generating PDF report for {len(transactions_data)} transactions")
                
                # Create metadata for the report
                metadata = {
                    'generated_by': current_user.name if hasattr(current_user, 'name') else "Unknown",
                    'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'property_name': property_id if property_id and property_id != 'all' else 'All Properties',
                    'date_range': f"{start_date} to {end_date}" if start_date and end_date else "All Dates",
                    'title': "Transaction Report"
                }
                
                # Format transactions for the report
                formatted_transactions = []
                for t in transactions_data:
                    # Remove HTML buttons and format data
                    transaction = {k: v for k, v in t.items() if k not in ['edit', 'delete']}
                    
                    # Clean up documentation fields (remove HTML)
                    if 'documentation_file' in transaction:
                        transaction['documentation_file'] = bool(transaction['documentation_file'])
                    if 'reimbursement_documentation' in transaction:
                        transaction['reimbursement_documentation'] = bool(transaction['reimbursement_documentation'])
                    
                    formatted_transactions.append(transaction)
                
                # Generate the PDF
                buffer = io.BytesIO()
                report_generator = TransactionReportGenerator()
                report_generator.generate(formatted_transactions, buffer, metadata)
                buffer.seek(0)
                
                return dcc.send_bytes(
                    buffer.getvalue(),
                    f"transactions_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                )
                
            except Exception as e:
                logger.error(f"Error generating PDF: {str(e)}")
                logger.error(traceback.format_exc())
                return None

        @dash_app.callback(
            Output("download-zip", "data"),
            [Input("download-zip-btn", "n_clicks")],
            [State("transactions-table", "data")]
        )
        def generate_zip_archive(n_clicks, transactions_data):
            """
            Generate ZIP archive with transaction documents.
            
            Args:
                n_clicks: Number of clicks on the download button
                transactions_data: Transaction data from the table
                
            Returns:
                ZIP archive data
            """
            if not n_clicks or not transactions_data:
                return None
            
            try:
                logger.debug(f"Generating ZIP for {len(transactions_data)} transactions")
                buffer = io.BytesIO()
                
                with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    added_files = set()
                    
                    for transaction in transactions_data:
                        # Add transaction documents
                        doc_file = transaction.get('documentation_file', '')
                        logger.debug(f"Processing transaction document: {doc_file}")
                        
                        if doc_file:
                            try:
                                # Extract filename if it's a button/link
                                if '<button' in doc_file:
                                    match = re.search(r'/artifact/([^"\']+)', doc_file)
                                    if match:
                                        filename = unquote(match.group(1))
                                    else:
                                        continue
                                else:
                                    filename = doc_file
                                    
                                if filename and filename not in added_files:
                                    file_path = os.path.join(flask_app.config['UPLOAD_FOLDER'], filename)
                                    if os.path.exists(file_path):
                                        logger.debug(f"Adding document: {filename}")
                                        zip_file.write(file_path, f"documents/{filename}")
                                        added_files.add(filename)
                                    else:
                                        logger.warning(f"Document file not found: {filename}")
                            except Exception as e:
                                logger.error(f"Error adding document {filename}: {str(e)}")

                        # Add reimbursement documents
                        reimb_doc = transaction.get('reimbursement_documentation', '')
                        logger.debug(f"Processing reimbursement document: {reimb_doc}")
                        
                        if reimb_doc:
                            try:
                                # Extract filename if it's a button/link
                                if '<button' in reimb_doc:
                                    match = re.search(r'/artifact/([^"\']+)', reimb_doc)
                                    if match:
                                        filename = unquote(match.group(1))
                                    else:
                                        continue
                                else:
                                    filename = reimb_doc

                                if filename and filename not in added_files:
                                    file_path = os.path.join(flask_app.config['UPLOAD_FOLDER'], filename)
                                    if os.path.exists(file_path):
                                        logger.debug(f"Adding document: {filename}")
                                        zip_file.write(file_path, f"documents/{filename}")
                                        added_files.add(filename)
                                    else:
                                        logger.warning(f"Document file not found: {filename}")
                            except Exception as e:
                                logger.error(f"Error adding document {filename}: {str(e)}")

                    # Add a summary text file
                    summary = f"""Document Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Documents: {len(added_files)}

Documents:
{chr(10).join(sorted(added_files))}
"""
                    zip_file.writestr('document_summary.txt', summary)

                buffer.seek(0)
                
                # Log summary
                logger.debug(f"Added {len(added_files)} documents to ZIP")

                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                return dcc.send_bytes(
                    buffer.getvalue(),
                    f"transaction_docs_{timestamp}.zip"
                )
                
            except Exception as e:
                logger.error(f"Error generating ZIP: {str(e)}")
                logger.error(traceback.format_exc())
                return None

        @dash_app.callback(
            Output('filter-options', 'data'),
            [Input('property-filter', 'value'),
            Input('type-filter', 'value'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date'),
            Input('description-search', 'value'),
            Input('clear-date-range', 'n_clicks')],
            [State('reimbursement-filter', 'value')]
        )
        def update_filter_options(property_id, transaction_type, 
                                start_date, end_date, description_search, 
                                clear_date_clicks, reimbursement_status):
            """
            Store filter options in session storage for persistence.
            
            Args:
                property_id: Selected property ID
                transaction_type: Selected transaction type
                start_date: Selected start date
                end_date: Selected end date
                description_search: Description search text
                clear_date_clicks: Number of clicks on the clear date button
                reimbursement_status: Selected reimbursement status
                
            Returns:
                Dictionary of filter options
            """
            ctx = dash.callback_context
            triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
            
            # Clear dates if clear button was clicked
            if triggered_id == 'clear-date-range':
                start_date = None
                end_date = None
            
            # Update filter options
            updated_filters = {
                'property_id': property_id,
                'transaction_type': transaction_type,
                'reimbursement_status': reimbursement_status,
                'start_date': start_date,
                'end_date': end_date,
                'description_search': description_search
            }
            
            return updated_filters

        # And add a separate callback just to update the refresh trigger
        @dash_app.callback(
            Output('refresh-trigger', 'data'),
            [Input('property-filter', 'value'),
            Input('type-filter', 'value'),
            Input('reimbursement-filter', 'value'),
            Input('date-range', 'start_date'),
            Input('date-range', 'end_date'),
            Input('description-search', 'value'),
            Input('clear-date-range', 'n_clicks')]
        )
        def update_refresh_trigger(*args):
            """
            Update refresh trigger with new timestamp when any filter changes.
            
            Args:
                *args: Filter inputs
                
            Returns:
                Dictionary with timestamp
            """
            return {'time': datetime.now().isoformat()}

        def format_transactions_for_display(df, property_id, is_mobile):
            """
            Format transaction data for display in the table.
            
            Args:
                df: DataFrame with transaction data
                property_id: Selected property ID
                is_mobile: Whether the display is for mobile devices
                
            Returns:
                Formatted DataFrame
            """
            try:
                if df.empty:
                    return df
                    
                # Convert dates
                if 'date' in df.columns:
                    df['date_for_sort'] = pd.to_datetime(df['date'])
                    df['date'] = df['date_for_sort'].dt.strftime('%Y-%m-%d')
                
                # Format property display
                if 'property_id' in df.columns:
                    with flask_app.app_context():
                        property_access_service = PropertyAccessService()
                        properties = property_access_service.get_accessible_properties(current_user.id)
                        property_map = {p.id: p.address for p in properties}
                        
                        df['property_display'] = df['property_id'].apply(
                            lambda x: format_address(property_map.get(x, "Unknown"), 'display')
                        )
                
                # Format currency
                if 'amount' in df.columns:
                    df['amount_for_sort'] = df['amount'].astype(float)
                    df['amount'] = df['amount_for_sort'].apply(lambda x: f"${abs(float(x)):,.2f}")
                
                # Format documentation links
                if 'documentation_file' in df.columns:
                    df['documentation_file'] = df['documentation_file'].apply(
                        lambda x: create_mobile_button(x, 'View', 'primary') if x else ''
                    )
                
                # Handle notes
                if 'notes' not in df.columns:
                    df['notes'] = ''
                df['notes'] = df['notes'].fillna('')
                
                # Add action buttons
                df['edit'] = df.apply(
                    lambda row: f'<a href="/transactions/edit/{row.id}?referrer=view" target="_parent" class="btn btn-sm btn-warning m-1">Edit<i class="bi bi-pencil ms-1"></i></a>',
                    axis=1
                )
                df['delete'] = df.apply(
                    lambda row: f'<button class="btn btn-sm btn-danger m-1" onclick="window.parent.viewTransactionsModule.handleDeleteTransaction(\'{row.id}\', \'{row.description}\')">Delete<i class="bi bi-trash"></i></button>',
                    axis=1
                )
                
                # Handle reimbursement data
                if 'reimbursement' in df.columns:
                    # Extract reimbursement data
                    df['reimbursement_status'] = df['reimbursement'].apply(
                        lambda x: x.get('reimbursement_status', '') if isinstance(x, dict) else ''
                    )
                    
                    df['date_shared'] = df['reimbursement'].apply(
                        lambda x: x.get('date_shared', '') if isinstance(x, dict) else ''
                    )
                    
                    df['reimbursement_documentation'] = df['reimbursement'].apply(
                        lambda x: create_mobile_button(x.get('documentation', ''), 'View', 'primary') 
                        if isinstance(x, dict) and x.get('documentation') else ''
                    )
                    
                    # Add sort column for date_shared
                    if 'date_shared' in df.columns:
                        df['date_shared_for_sort'] = pd.to_datetime(df['date_shared'], errors='coerce')
                
                return df
                
            except Exception as e:
                logger.error(f"Error formatting transactions: {str(e)}")
                logger.error(traceback.format_exc())
                return df

        def create_table_columns(property_id, df, is_mobile):
            """
            Create mobile-optimized column definitions for the table.
            
            Args:
                property_id: Selected property ID
                df: DataFrame with transaction data
                is_mobile: Whether the display is for mobile devices
                
            Returns:
                List of column definitions
            """
            try:
                columns = []
                
                # Property column for 'all properties' view
                if not property_id or property_id == 'all':
                    columns.append({
                        'name': 'Property',
                        'id': 'property_display',
                        'presentation': 'markdown',
                        'sortable': True
                    })
                
                # Core columns with sort configuration
                core_columns = [
                    {
                        'name': 'Date', 
                        'id': 'date',
                        'sortable': True,
                        'sort_by': 'date_for_sort'
                    },
                    {
                        'name': 'Description',
                        'id': 'description',
                        'sortable': True
                    },
                    {
                        'name': 'Amount',
                        'id': 'amount',
                        'sortable': True,
                        'sort_by': 'amount_for_sort'
                    }
                ]
                
                # Add category column if not mobile or if we have space
                if not is_mobile or (property_id and property_id != 'all'):
                    core_columns.append({
                        'name': 'Category',
                        'id': 'category',
                        'sortable': True
                    })
                
                # Add notes column if not mobile
                if not is_mobile:
                    core_columns.append({
                        'name': 'Notes',
                        'id': 'notes',
                        'sortable': True
                    })
                
                # Add documentation column
                core_columns.append({
                    'name': 'Doc', 
                    'id': 'documentation_file', 
                    'presentation': 'markdown',
                    'type': 'text',
                    'dangerously_allow_html': True,
                    'sortable': False
                })
                
                columns.extend(core_columns)
                
                # Add reimbursement columns if needed
                if 'reimbursement_status' in df.columns:
                    # Only add reimbursement columns if not wholly owned
                    if not is_mobile or (property_id and property_id != 'all'):
                        columns.append({
                            'name': 'Status',
                            'id': 'reimbursement_status',
                            'sortable': True
                        })
                    
                    if 'date_shared' in df.columns:
                        columns.append({
                            'name': 'Reimb Date', 
                            'id': 'date_shared',
                            'sortable': True,
                            'sort_by': 'date_shared_for_sort'
                        })
                    
                    if 'reimbursement_documentation' in df.columns:
                        columns.append({
                            'name': 'Reimb Doc', 
                            'id': 'reimbursement_documentation', 
                            'presentation': 'markdown',
                            'type': 'text',
                            'dangerously_allow_html': True,
                            'sortable': False
                        })
                
                # Action columns (not sortable)
                action_columns = [
                    {
                        'name': 'Edit',
                        'id': 'edit',
                        'presentation': 'markdown',
                        'type': 'text',
                        'dangerously_allow_html': True,
                        'sortable': False
                    },
                    {
                        'name': 'Delete',
                        'id': 'delete',
                        'presentation': 'markdown',
                        'type': 'text',
                        'dangerously_allow_html': True,
                        'sortable': False
                    }
                ]
                
                columns.extend(action_columns)
                
                return columns
                
            except Exception as e:
                logger.error(f"Error creating table columns: {str(e)}")
                logger.error(traceback.format_exc())
                return []

        def create_table_header(transaction_type, property_id, reimbursement_status, 
                              start_date, end_date, description_search):
            """
            Create header text for the transactions table.
            
            Args:
                transaction_type: Selected transaction type
                property_id: Selected property ID
                reimbursement_status: Selected reimbursement status
                start_date: Selected start date
                end_date: Selected end date
                description_search: Description search text
                
            Returns:
                Header text
            """
            try:
                # Create header with filter information
                header_parts = []
                
                # Add transaction type to header
                if transaction_type and transaction_type != 'all':
                    header_parts.append(transaction_type.capitalize())
                
                # Add "Transactions" to header
                header_parts.append("Transactions")
                
                # Add property information
                if property_id and property_id != 'all':
                    with flask_app.app_context():
                        property_access_service = PropertyAccessService()
                        properties = property_access_service.get_accessible_properties(current_user.id)
                        property_data = next((p for p in properties if p.id == property_id), None)
                        
                        if property_data:
                            property_display = format_address(property_data.address, 'base')
                            header_parts.append(f"for {property_display}")
                
                # Add reimbursement status
                if reimbursement_status and reimbursement_status != 'all':
                    header_parts.append(f"({reimbursement_status.replace('_', ' ')})")
                
                # Add date range
                if start_date and end_date:
                    header_parts.append(f"from {start_date} to {end_date}")
                elif start_date:
                    header_parts.append(f"from {start_date}")
                elif end_date:
                    header_parts.append(f"until {end_date}")
                
                # Add search term
                if description_search:
                    header_parts.append(f"matching '{description_search}'")
                
                header = " ".join(header_parts)
                return header
                
            except Exception as e:
                logger.error(f"Error creating table header: {str(e)}")
                logger.error(traceback.format_exc())
                return "Transactions"

        return dash_app
        
    except Exception as e:
        logger.error(f"Error creating transactions dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        raise
