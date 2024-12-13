# Dash and UI imports
import dash
from dash import dcc, html, dash_table, Input, Output, State
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
import zipfile

# Download file imports
import os
import re
from urllib.parse import unquote

# Utility imports
import traceback
import logging
from typing import Dict, List, Optional

# Local imports
from services.transaction_service import get_transactions_for_view, get_properties_for_user
from services.transaction_report_generator import TransactionReportGenerator
from services.report_generator import ReportGenerator

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

        # Add before the transactions table for PDF Report Generation
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P(
                        "Use these buttons to download all your transactions (filtered above) and supporting documentation.",
                        className="text-muted mb-2"  # mb-2 adds margin bottom for spacing
                    ),
                ]),
                html.Div([
                    dbc.Button(
                        [
                            html.I(className="fas fa-file-pdf me-2"),
                            "Download PDF Report"
                        ],
                        id="download-pdf-btn",
                        color="primary",
                        className="me-2"
                    ),
                    dcc.Download(id="download-pdf"),
                    dbc.Button(
                        [
                            html.I(className="fas fa-file-archive me-2"),
                            "Download Documents ZIP"
                        ],
                        id="download-zip-btn",
                        color="secondary",
                        className="me-2"
                    ),
                    dcc.Download(id="download-zip"),
                ], className="d-flex align-items-center"),
                dbc.Spinner(
                    html.Div(id="download-status"),
                    color="primary",
                    type="border",
                    size="sm"
                ),
                dbc.Tooltip(
                    "Download a PDF report of all transactions matching your current filter criteria",
                    target="download-pdf-btn",
                ),
                dbc.Tooltip(
                    "Download a ZIP file containing all transaction documentation for matching transactions",
                    target="download-zip-btn",
                ),
            ], width=12)
        ], className="mb-4"),
        
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
                    lambda x: f'<a href="{url_for("transactions.get_artifact", filename=x)}" target="_blank" class="btn btn-sm btn-primary">View</a>' if x else ''
                )

                # Handle reimbursement documentation with validation
                df['reimbursement_documentation'] = df.apply(
                    lambda row: (f'<a href="{url_for("transactions.get_artifact", filename=row.get("reimbursement", {}).get("documentation"))}" target="_blank" class="btn btn-sm btn-primary">View</a>'
                                if isinstance(row.get('reimbursement'), dict) 
                                and row.get('reimbursement', {}).get('documentation')
                                else ''),
                    axis=1
                )

                # Add edit column based on property manager status
                columns = base_columns.copy()
                if current_user.is_authenticated:
                    filter_options = {
                        'property_id': property_id,
                        'transaction_type': transaction_type,
                        'reimbursement_status': reimbursement_status,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                    encoded_filter_options = urllib.parse.quote(json.dumps(filter_options))

                    # Create a dictionary mapping property addresses to whether current user is property manager
                    property_manager_status = {}
                    for prop in properties:
                        is_manager = any(
                            partner['name'] == current_user.name and 
                            partner.get('is_property_manager', False)
                            for partner in prop.get('partners', [])
                        )
                        property_manager_status[prop['address']] = is_manager

                    # Add edit column based on property manager status
                    df['edit'] = df.apply(
                        lambda row: (
                            f'<a href="/transactions/edit/{str(row["id"])}?filters={encoded_filter_options}" '
                            f'target="_parent" class="btn btn-sm btn-primary">Edit</a>'
                            if property_manager_status.get(row['property_id'], False)
                            else '<span class="text-muted">Edit Restricted for Property Manager</span>'
                        ),
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
    
    @dash_app.callback(
        Output("download-pdf", "data"),
        Output("download-status", "children", allow_duplicate=True),
        Input("download-pdf-btn", "n_clicks"),
        [State("property-filter", "value"),
        State("type-filter", "value"),
        State("date-range", "start_date"),
        State("date-range", "end_date"),
        State("transactions-table", "data")],
        prevent_initial_call=True
    )
    def generate_pdf_report(n_clicks, property_id, transaction_type, start_date, end_date, transactions_data):
        """Generate and return PDF report of transactions"""
        if not n_clicks or not transactions_data:
            return None, ""
        
        try:
            # Create buffer for PDF
            buffer = io.BytesIO()
            
            # Prepare metadata for the report
            metadata = {
                'user': current_user.name,
                'date_range': f"{start_date or 'earliest'} to {end_date or 'latest'}",
                'property': property_id if property_id and property_id != 'all' else 'All Properties'
            }
            
            # Generate report using our new generator
            report_generator = TransactionReportGenerator()
            report_generator.generate(transactions_data, buffer, metadata)
            
            # Prepare buffer for download
            buffer.seek(0)
            
            return dcc.send_bytes(
                buffer.getvalue(),
                f"transactions_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            ), html.Div("Report generated successfully", className="text-success")
            
        except Exception as e:
            current_app.logger.error(f"Error generating PDF: {str(e)}")
            return None, html.Div("Error generating PDF report", className="text-danger")

    @dash_app.callback(
        Output("download-zip", "data"),
        Output("download-status", "children", allow_duplicate=True),
        Input("download-zip-btn", "n_clicks"),
        State("transactions-table", "data"),
        prevent_initial_call=True
    )
    def generate_zip_archive(n_clicks, transactions_data):
        """Generate ZIP file containing all transaction documentation"""
        if not n_clicks or not transactions_data:
            return None, ""
        
        try:
            # Create buffer for ZIP
            buffer = io.BytesIO()
            
            # Create ZIP file
            with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Track files and organize by type
                added_files = {
                    'transaction_docs': set(),
                    'reimbursement_docs': set()
                }
                
                for transaction in transactions_data:
                    # Handle transaction documentation
                    doc_file = transaction.get('documentation_file', '')
                    if doc_file:
                        try:
                            # Extract filename from HTML link if necessary
                            match = re.search(r'/artifact/([^"]+)', doc_file)
                            if match:
                                filename = unquote(match.group(1))
                                if filename not in added_files['transaction_docs']:
                                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                                    if os.path.exists(file_path):
                                        # Add to transactions subfolder
                                        zip_file.write(
                                            file_path, 
                                            f"transaction_documents/{filename}"
                                        )
                                        added_files['transaction_docs'].add(filename)
                        except Exception as e:
                            current_app.logger.warning(f"Error adding transaction doc {doc_file}: {str(e)}")
                    
                    # Handle reimbursement documentation
                    reimb_doc = transaction.get('reimbursement_documentation', '')
                    if reimb_doc:
                        try:
                            match = re.search(r'/artifact/([^"]+)', reimb_doc)
                            if match:
                                filename = unquote(match.group(1))
                                if filename not in added_files['reimbursement_docs']:
                                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                                    if os.path.exists(file_path):
                                        # Add to reimbursements subfolder
                                        zip_file.write(
                                            file_path, 
                                            f"reimbursement_documents/{filename}"
                                        )
                                        added_files['reimbursement_docs'].add(filename)
                        except Exception as e:
                            current_app.logger.warning(f"Error adding reimbursement doc {reimb_doc}: {str(e)}")
                
                # Add a README file
                readme_content = f"""Transaction Documents Export
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Generated by: {current_user.name}

    Contents:
    - Transaction Documents: {len(added_files['transaction_docs'])} files
    - Reimbursement Documents: {len(added_files['reimbursement_docs'])} files

    Note: Documents are organized in separate folders for transactions and reimbursements.
    """
                zip_file.writestr('README.txt', readme_content)
            
            # Prepare buffer for download
            buffer.seek(0)
            
            total_files = sum(len(files) for files in added_files.values())
            if total_files == 0:
                return None, html.Div("No documentation files found", className="text-warning")
            
            return dcc.send_bytes(
                buffer.getvalue(),
                f"transaction_documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            ), html.Div(
                f"Successfully exported {total_files} documents",
                className="text-success"
            )
            
        except Exception as e:
            current_app.logger.error(f"Error generating ZIP: {str(e)}")
            return None, html.Div("Error generating ZIP archive", className="text-danger")


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