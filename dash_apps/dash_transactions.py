# Dash and UI imports
import dash
from dash import dcc, html, dash_table, Input, Output, State, clientside_callback
import dash_bootstrap_components as dbc

# Data handling imports
import pandas as pd
import json
import urllib.parse
from datetime import datetime, timedelta

# Flask imports
from flask_login import current_user
from flask import current_app, url_for

# PDF Report imports
import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# Utility imports
import traceback
import logging
from typing import Dict, List, Optional, Union, Any

# Local imports
from services.transaction_service import get_transactions_for_view, get_properties_for_user

# Configure logging
logger = logging.getLogger(__name__)

# Constants for validation
MAX_DESCRIPTION_LENGTH = 500
VALID_TRANSACTION_TYPES = ['income', 'expense']
VALID_REIMBURSEMENT_STATUS = ['all', 'pending', 'completed']
MIN_DATE = '2000-01-01'  # Reasonable minimum date
MAX_FUTURE_DAYS = 30     # Maximum days into future for datesr

# Base columns definition for the transactions table
base_columns = [
    {'name': 'ID', 'id': 'id', 'hidden': True},
    {'name': 'Category', 'id': 'category'},
    {'name': 'Description', 'id': 'description'},
    {'name': 'Amount', 'id': 'amount'},
    {'name': 'Date Incurred', 'id': 'date'},
    {'name': 'Collector/Payer', 'id': 'collector_payer'},
    {'name': 'Transaction Doc', 'id': 'documentation_file', 'presentation': 'markdown'},
    {'name': 'Reimb. Date', 'id': 'date_shared'},
    {'name': 'Reimb. Description', 'id': 'share_description'},
    {'name': 'Reimb. Doc', 'id': 'reimbursement_documentation', 'presentation': 'markdown'},
]

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple[bool, str]:
    """
    Validates the date range for transactions.
    
    Args:
        start_date: Start date string in YYYY-MM-DD format
        end_date: End date string in YYYY-MM-DD format
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    try:
        # Allow None values for open-ended ranges
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

def validate_property_id(property_id: Optional[str], available_properties: List[Dict]) -> bool:
    """
    Validates that the property ID exists in the available properties list.
    
    Args:
        property_id: Property ID to validate
        available_properties: List of available properties
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not property_id or property_id == 'all':
        return True
    return any(prop['address'] == property_id for prop in available_properties)

def create_transactions_dash(flask_app):
    """
    Creates and configures the Dash application for transaction management.
    """
    dash_app = dash.Dash(
        __name__, 
        server=flask_app, 
        url_base_pathname='/transactions/view/dash/',
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            '/static/css/styles.css',
            'https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css'
        ],
        external_scripts=[
            'https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js'
        ]
    )

    # Define the layout
    dash_app.layout = dbc.Container([
        # Add FilterManager at the top
        html.Div(id='filter-manager'),

        # State management stores
        dcc.Store(id='refresh-trigger', storage_type='memory'),
        dcc.Store(id='filter-options', storage_type='session'),
        
        # Initialize toastr
        html.Script("""
            window.addEventListener('load', function() {
                if (window.toastr) {
                    toastr.options = {
                        closeButton: true,
                        newestOnTop: false,
                        progressBar: true,
                        positionClass: "toast-bottom-right",
                        preventDuplicates: false,
                        timeOut: 5000
                    };
                }
            });
        """),
        
        # Flash messages container
        html.Div(id='flash-message-container', className='flash-messages'),
        
        # Page header
        html.H2('Filter Transactions to View', className='mt-4 mb-4'),
        
        # Filters row
        dbc.Row([
            dbc.Col([
                dbc.Label('Property Address'),
                dcc.Dropdown(id='property-filter', placeholder='Select Property', multi=False)
            ], width=3),
            dbc.Col([
                dbc.Label('Transaction Type'),
                dcc.Dropdown(
                    id='type-filter',
                    options=[
                        {'label': 'Incomes', 'value': 'income'},
                        {'label': 'Expenses', 'value': 'expense'}
                    ],
                    placeholder='Select Transaction Type'
                )
            ], width=3),
            dbc.Col([
                dbc.Label('Reimbursement Status'),
                dcc.Dropdown(
                    id='reimbursement-filter',
                    options=[
                        {'label': 'All', 'value': 'all'},
                        {'label': 'Pending', 'value': 'pending'},
                        {'label': 'Completed', 'value': 'completed'}
                    ],
                    value='all',
                    placeholder='Select Reimbursement Status'
                )
            ], width=3),
            dbc.Col([
                dbc.Label('Date Range'),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date_placeholder_text='Start Date',
                    end_date_placeholder_text='End Date'
                )
            ], width=3)
        ], className='mb-4'),
        
        # Report controls
        dbc.Row([
            dbc.Col([
                dbc.Label('Report Type'),
                dcc.Dropdown(
                    id='report-type',
                    options=[
                        {'label': 'Summary Report', 'value': 'summary'},
                        {'label': 'Detailed Report', 'value': 'detailed'}
                    ],
                    value='summary',
                    placeholder='Select Report Type'
                ),
                html.Div([
                    html.P("Summary Report: Provides an overview of transactions grouped by category and type.", 
                          className="text-muted mt-2"),
                    html.P("Detailed Report: Includes all individual transaction details.", 
                          className="text-muted")
                ], id="report-description")
            ], width=9),
            dbc.Col([
                dbc.Button(
                    "Generate PDF Report",
                    id="generate-report-btn",
                    color="primary",
                    className="mb-2 w-100"
                ),
                html.Div(id="report-link-container", className="w-100")
            ], width=3, className="d-flex flex-column justify-content-end")
        ], className='mb-4'),
        
        # Transactions table header and table
        html.H2(id='transactions-header', className='mt-4 mb-3'),
        dash_table.DataTable(
            id='transactions-table',
            columns=[
                *[col for col in base_columns if col['id'] not in ['documentation_file', 'reimbursement_documentation']],
                {
                    'name': 'Transaction Doc',
                    'id': 'documentation_file',
                    'presentation': 'markdown',
                    'type': 'text'
                },
                {
                    'name': 'Reimb. Doc',
                    'id': 'reimbursement_documentation',
                    'presentation': 'markdown',
                    'type': 'text'
                },
                # Updated edit column for direct navigation
                {
                    'name': 'Edit',
                    'id': 'edit',
                    'presentation': 'markdown',
                    'type': 'text'
                }
            ],
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'font-family': 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif',
                'font-size': '14px',
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100px',
                'maxWidth': '180px',
                'textOverflow': 'ellipsis',
            },
            style_header={
                'backgroundColor': 'navy',
                'fontWeight': 'bold',
                'color': 'white',
                'border': '1px solid #dee2e6',
                'whiteSpace': 'nowrap',
                'height': '40px',
                'lineHeight': '40px',
                'padding': '0 10px',
                'textOverflow': 'ellipsis',
                'overflow': 'hidden'
            },
            style_data={
                'border': '1px solid #dee2e6',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': ['documentation_file', 'reimbursement_documentation']},
                    'width': '130px',
                    'minWidth': '130px',
                    'maxWidth': '130px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                }
            ],
            style_data_conditional=[
                {
                    'if': {'column_id': 'amount'},
                    'color': 'green'
                },
                {
                    'if': {'column_id': ['documentation_file', 'reimbursement_documentation']},
                    'textAlign': 'center',
                }
            ],
            tooltip_duration=None,
            markdown_options={'html': True},
            page_action='native',
            page_current=0,
            page_size=10,
            sort_action='native',
            sort_mode='multi',
            filter_action='none'
        ),
    ], fluid=True)

    def create_header(type_str, property_str, start_str, end_str):
        """Helper function to create header with truncated address"""
        # If property string exists and isn't 'All Properties', truncate it
        if property_str and property_str != 'All Properties':
            # Split by commas and take only the first two parts
            parts = property_str.split(',')
            if len(parts) >= 2:
                property_str = ', '.join(parts[:2]).strip()
            
        return f"{type_str} Transactions for {property_str} from {start_str} to {end_str}"

    # Register callbacks
    @dash_app.callback(
        [Output('transactions-table', 'data'),
         Output('transactions-header', 'children'),
         Output('property-filter', 'options'),
         Output('transactions-table', 'columns')],
        [Input('refresh-trigger', 'data'),
         Input('property-filter', 'value'),
         Input('type-filter', 'value'),
         Input('reimbursement-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_table(refresh_trigger, property_id, transaction_type, reimbursement_status, start_date, end_date):
        """
        Updates the transactions table based on filter criteria.
        
        Args:
            refresh_trigger: Trigger for refresh
            property_id: Selected property ID
            transaction_type: Type of transaction (income/expense)
            reimbursement_status: Status of reimbursement
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            tuple: (table_data, header, property_options, columns)
        """
        try:
            logger.debug(f"Updating table with filters: property={property_id}, "
                        f"type={transaction_type}, status={reimbursement_status}, "
                        f"dates={start_date} to {end_date}")

            # Validate inputs
            if transaction_type and transaction_type not in VALID_TRANSACTION_TYPES:
                logger.warning(f"Invalid transaction type received: {transaction_type}")
                return [], "Invalid transaction type", [], base_columns

            if reimbursement_status not in VALID_REIMBURSEMENT_STATUS:
                logger.warning(f"Invalid reimbursement status received: {reimbursement_status}")
                return [], "Invalid reimbursement status", [], base_columns

            date_valid, date_error = validate_date_range(start_date, end_date)
            if not date_valid:
                logger.warning(f"Invalid date range: {date_error}")
                return [], date_error, [], base_columns

            # Get and validate properties
            try:
                properties = get_properties_for_user(
                    current_user.id,
                    current_user.name,
                    current_user.role == 'Admin'
                )
                if not validate_property_id(property_id, properties):
                    logger.warning(f"Invalid property ID received: {property_id}")
                    return [], "Invalid property selected", [], base_columns
                
            except Exception as e:
                logger.error(f"Error retrieving properties: {str(e)}")
                return [], "Error loading properties", [], base_columns

            # Create property options
            property_options = [{'label': 'All Properties', 'value': 'all'}]
            for prop in properties:
                if prop.get('address'):
                    parts = prop['address'].split(',')
                    display_address = ', '.join(parts[:2]).strip() if len(parts) >= 2 else parts[0]
                    property_options.append({
                        'label': display_address,
                        'value': prop['address']
                    })

            # Get transactions with error handling
            try:
                effective_property_id = None if property_id == 'all' or not property_id else property_id
                transactions = get_transactions_for_view(
                    current_user.id,
                    current_user.name,
                    effective_property_id,
                    reimbursement_status,
                    start_date,
                    end_date,
                    current_user.role == 'Admin'
                )
                logger.info(f"Retrieved {len(transactions)} transactions for user {current_user.id}")
                
            except Exception as e:
                logger.error(f"Error retrieving transactions: {str(e)}")
                return [], "Error loading transactions", property_options, base_columns

            # Process transactions
            try:
                df = pd.DataFrame(transactions)
                if df.empty:
                    logger.info("No transactions found matching criteria")
                    return [], "No transactions found", property_options, base_columns

                # Apply type filter
                if transaction_type:
                    df = df[df['type'].str.lower() == transaction_type.lower()]

                # Format amounts with validation
                df['amount'] = df['amount'].apply(
                    lambda x: f"${abs(float(x)):.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else ''
                )

                # Format documentation links
                df['documentation_file'] = df['documentation_file'].apply(
                    lambda x: f'[View/Download]({url_for("transactions.get_artifact", filename=x)})' if x else ''
                )

                # Handle reimbursement documentation with validation
                df['reimbursement_documentation'] = df.apply(
                    lambda row: (f'[View/Download]({url_for("transactions.get_artifact", filename=row.get("reimbursement", {}).get("documentation"))})'
                                if isinstance(row.get('reimbursement'), dict) 
                                and row.get('reimbursement', {}).get('documentation')
                                else ''),
                    axis=1
                )

                # Add edit links for admin users
                columns = base_columns.copy()
                if current_user.is_authenticated and current_user.role == 'Admin':
                    filter_options = {
                        'property_id': property_id,
                        'transaction_type': transaction_type,
                        'reimbursement_status': reimbursement_status,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                    encoded_filter_options = urllib.parse.quote(json.dumps(filter_options))
                    
                    df['edit'] = df.apply(
                        lambda row: f'<a href="/transactions/edit/{str(row["id"])}?filters={encoded_filter_options}" target="_parent" class="btn btn-sm btn-primary">Edit</a>', 
                        axis=1
                    )
                    columns.append({'name': 'Edit', 'id': 'edit', 'presentation': 'markdown'})

                # Create header
                header = create_header(
                    'Income' if transaction_type == 'income' else 'Expense' if transaction_type == 'expense' else 'All',
                    property_id if property_id and property_id != 'all' else 'All Properties',
                    start_date or 'Earliest',
                    end_date or 'Latest'
                )

                logger.debug(f"Returning {len(df)} processed transactions")
                return df.to_dict('records'), header, property_options, columns

            except Exception as e:
                logger.error(f"Error processing transactions: {str(e)}")
                return [], "Error processing data", property_options, base_columns

        except Exception as e:
            logger.error(f"Unexpected error in update_table: {str(e)}\n{traceback.format_exc()}")
            return [], "An unexpected error occurred", [], base_columns
        
    # Filter options update callback
    @dash_app.callback(
        Output('filter-options', 'data'),
        [Input('property-filter', 'value'),
         Input('type-filter', 'value'),
         Input('reimbursement-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_filter_options(property_id, transaction_type, reimbursement_status, start_date, end_date):
        return {
            'property_id': property_id,
            'transaction_type': transaction_type,
            'reimbursement_status': reimbursement_status,
            'start_date': start_date,
            'end_date': end_date
        }

    # PDF Report generation callback (keeping existing implementation)
    @dash_app.callback(
        Output("report-link-container", "children"),
        Input("generate-report-btn", "n_clicks"),
        [State("transactions-table", "data"),
         State("report-type", "value")]
    )
    def generate_report(n_clicks, data, report_type):
        if n_clicks is None or not data:
            return None

        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Add title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            elements.append(Paragraph("Transaction Report", title_style))
            elements.append(Spacer(1, 12))

            if report_type == 'summary':
                # Create summary report
                summary_data = process_summary_data(data)
                elements.extend(create_summary_report(summary_data, styles))
            else:
                # Create detailed report
                elements.extend(create_detailed_report(data, styles))

            # Build PDF
            doc.build(elements)
            pdf_data = buffer.getvalue()
            buffer.close()

            # Encode PDF
            encoded_pdf = base64.b64encode(pdf_data).decode('utf-8')
            
            # Return download link
            return html.A(
                "Download Report",
                href=f"data:application/pdf;base64,{encoded_pdf}",
                download=f"transactions_report_{report_type}.pdf",
                className="btn btn-success w-100"
            )

        except Exception as e:
            current_app.logger.error(f"Error generating report: {str(e)}")
            return html.Div("Error generating report", className="text-danger")

    # Initial data load clientside callback
    dash_app.clientside_callback(
        """
        function(n) {
            return '';
        }
        """,
        Output('refresh-trigger', 'data'),
        Input('refresh-trigger', 'data'),
        prevent_initial_call=False
    )

    @dash_app.callback(
        [Output('property-filter', 'value'),
        Output('type-filter', 'value'),
        Output('reimbursement-filter', 'value'),
        Output('date-range', 'start_date'),
        Output('date-range', 'end_date')],
        [Input('refresh-trigger', 'data')],
        [State('filter-options', 'data')]
    )
    def restore_filters(trigger, filter_data):
        if not filter_data:
            return [None, None, 'all', None, None]
        
        try:
            return [
                filter_data.get('property_id'),
                filter_data.get('transaction_type'),
                filter_data.get('reimbursement_status', 'all'),
                filter_data.get('start_date'),
                filter_data.get('end_date')
            ]
        except Exception as e:
            current_app.logger.error(f"Error restoring filters: {str(e)}")
            return [None, None, 'all', None, None]

    return dash_app

# Helper functions with added validation
def process_summary_data(data: List[Dict]) -> Dict:
    """
    Process transaction data for summary report with validation.
    
    Args:
        data: List of transaction dictionaries
        
    Returns:
        Dict: Processed summary data
    """
    try:
        df = pd.DataFrame(data)
        if df.empty:
            logger.warning("No data provided for summary processing")
            return {'income': pd.DataFrame(), 'expense': pd.DataFrame()}

        # Validate amount column
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        invalid_amounts = df['amount'].isna().sum()
        if invalid_amounts > 0:
            logger.warning(f"Found {invalid_amounts} invalid amount values")

        summary = {
            'income': df[df['type'] == 'income'].groupby('category')['amount'].agg(['count', 'sum']),
            'expense': df[df['type'] == 'expense'].groupby('category')['amount'].agg(['count', 'sum'])
        }
        return summary
    except Exception as e:
        logger.error(f"Error processing summary data: {str(e)}")
        return {'income': pd.DataFrame(), 'expense': pd.DataFrame()}

def create_summary_report(summary_data, styles):
    """Create summary report elements"""
    elements = []
    
    for trans_type, data in summary_data.items():
        # Add section title
        elements.append(Paragraph(f"{trans_type.title()} Summary", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Create table data
        table_data = [['Category', 'Count', 'Total Amount']]
        for category, row in data.iterrows():
            table_data.append([
                category,
                str(int(row['count'])),
                f"${row['sum']:.2f}"
            ])
        
        # Create table
        table = Table(table_data, colWidths=[250, 100, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
    
    return elements

def create_detailed_report(data, styles):
    """Create detailed report elements"""
    elements = []
    
    # Create table data
    table_data = [['Date', 'Type', 'Category', 'Description', 'Amount']]
    for row in data:
        table_data.append([
            row['date'],
            row['type'].title(),
            row['category'],
            row['description'],
            row['amount']
        ])
    
    # Create table
    table = Table(table_data, colWidths=[80, 70, 100, 200, 70])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)

    return elements   