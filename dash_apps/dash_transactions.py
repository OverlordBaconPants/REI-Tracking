# Dash and UI imports
import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc

# Data handling imports
import requests
import pandas as pd
import json
import urllib.parse
from datetime import datetime, timedelta

# Flask imports
from flask_login import current_user
from flask import current_app, url_for, session

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
logger.setLevel(logging.DEBUG)

# Constants for validation
MAX_DESCRIPTION_LENGTH = 500
VALID_TRANSACTION_TYPES = ['income', 'expense']
VALID_REIMBURSEMENT_STATUS = ['all', 'pending', 'completed']
MIN_DATE = '2000-01-01'  # Reasonable minimum date
MAX_FUTURE_DAYS = 30     # Maximum days into future for datesr

# Base columns definition for the transactions table
base_columns = [
        {'name': 'ID', 'id': 'id', 'hidden': True},
        {'name': 'Property', 'id': 'property_id'},  # Add Property column
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

def truncate_address(address):
    """
    Truncates an address to show only house number, street, and city.
    
    Args:
        address (str): Full property address
        
    Returns:
        str: Truncated address
    """
    if not address:
        return ""
    parts = address.split(',')
    return ', '.join(parts[:2]).strip() if len(parts) >= 2 else parts[0]

def is_wholly_owned_by_user(property_data, user_name):
    """
    Checks if a property is wholly owned by a single user.
    
    Args:
        property_data (dict): Property data containing partners information
        user_name (str): Name of the user to check
        
    Returns:
        bool: True if the property is wholly owned by the user, False otherwise
    """
    logger.debug(f"Checking ownership for property: {property_data.get('address')} and user: {user_name}")
    partners = property_data.get('partners', [])
    logger.debug(f"Partners data: {partners}")
    
    # If there's only one partner and it's our user, the property is wholly owned
    if len(partners) == 1:
        logger.debug("Single partner found")
        partner = partners[0]
        is_user = partner.get('name', '').lower() == user_name.lower()
        equity = float(partner.get('equity_share', 0))  # Changed from ownership_percentage to equity_share
        logger.debug(f"Is user the owner? {is_user}, Equity share: {equity}")
        if is_user and equity == 100:
            return True
    
    # Calculate total equity
    total_equity = sum(float(partner.get('equity_share', 0)) for partner in partners)  # Changed from ownership_percentage
    logger.debug(f"Total equity: {total_equity}")
    
    # Find user's equity
    user_equity = sum(  # Changed from ownership_percentage
        float(partner.get('equity_share', 0))
        for partner in partners
        if partner.get('name', '').lower() == user_name.lower()
    )
    logger.debug(f"User equity: {user_equity}")
    
    # Consider it wholly owned if user owns 100% (allowing for small floating point differences)
    is_wholly_owned = abs(user_equity - 100.0) < 0.01
    logger.debug(f"Is wholly owned? {is_wholly_owned}")
    return is_wholly_owned

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
            'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',  # Add jQuery first
            'https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js'
        ]
    )

    # Define the layout
    dash_app.layout = dbc.Container([
        # Add FilterManager at the top
        html.Div(id='filter-manager'),

        # State management stores - consolidated
        dcc.Store(id='refresh-trigger', storage_type='memory', data=datetime.now().isoformat()),
        dcc.Store(id='delete-transaction-id', storage_type='memory'),
        dcc.Store(id='filter-options', storage_type='session'),
        
        # Delete Modal
        dbc.Modal([
            dbc.ModalHeader("Delete Transaction"),
            dbc.ModalBody("Are you sure you want to delete this transaction?"),
            dbc.ModalFooter([
                dbc.Button("Cancel", id="delete-cancel", className="ms-auto"),
                dbc.Button("Delete", id="delete-confirm", color="danger"),
            ]),
        ], id="delete-modal", is_open=False),
        
        # Initialize toastr
        html.Script("""
            window.addEventListener('load', function() {
                toastr.options = {
                    "closeButton": true,
                    "debug": false,
                    "newestOnTop": false,
                    "progressBar": true,
                    "positionClass": "toast-bottom-right",
                    "preventDuplicates": true,
                    "onclick": null,
                    "showDuration": "300",
                    "hideDuration": "1000",
                    "timeOut": "5000",
                    "extendedTimeOut": "1000",
                    "showEasing": "swing",
                    "hideEasing": "linear",
                    "showMethod": "fadeIn",
                    "hideMethod": "fadeOut"
                };
            });
        """),
        
        # Flash messages container
        html.Div(id='flash-message-container', className='flash-messages'),
        
        # Page header
        html.H2('Filter Transactions to View', className='mt-4 mb-4'),
        
        # Filters row
        dbc.Row([
            dbc.Col([
                dbc.Label([
                    html.I(className="bi bi-building me-2"),
                    "Property Address"
                ]),
                dcc.Dropdown(id='property-filter', placeholder='Select Property', multi=False)
            ], width=3),
            dbc.Col([
                dbc.Label([
                    html.I(className="bi bi-tags me-2"),
                    "Transaction Type"
                ]),
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
                dbc.Label([
                    html.I(className="bi bi-arrow-repeat me-2"),
                    "Reimbursement Status"
                ]),
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
                dbc.Label([
                    html.I(className="bi bi-calendar-range me-2"),
                    "Date Range"
                ]),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date_placeholder_text='Start Date',
                    end_date_placeholder_text='End Date'
                )
            ], width=3)
        ], className='mb-4'),

        # Description search
        dbc.Row([
            dbc.Col([
                dbc.Label([
                    html.I(className="bi bi-search me-2"),
                    "Search Description"
                ]),
                dbc.Input(
                    id='description-search',
                    type='text',
                    placeholder='Enter description to search...',
                    debounce=True,
                    className='w-50'  # This makes it take up 50% of the column width
                )
            ], width=12)
        ], className='mb-4'),

        # Add before the transactions table for PDF Report Generation
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.P(
                        "Use these buttons to download all your transactions (filtered above) and supporting documentation.",
                        className="text-muted mb-2"
                    ),
                ]),
                html.Div([
                    # Group the buttons together in a div
                    html.Div([
                        dbc.Button(
                            [
                                html.I(className="bi bi-file-pdf me-2"),
                                "Download PDF Report"
                            ],
                            id="download-pdf-btn",
                            color="primary",
                            className="me-2"
                        ),
                        dcc.Download(id="download-pdf"),
                        dbc.Button(
                            [
                                html.I(className="bi bi-file-zip me-2"),
                                "Download Documents ZIP"
                            ],
                            id="download-zip-btn",
                            color="secondary",
                            className="me-2"  # adds margin to the right
                        ),
                        dcc.Download(id="download-zip"),
                        html.A(
                            dbc.Button(
                                [
                                    html.I(className="bi bi-plus-lg me-2"),
                                    "Add Transaction"
                                ],
                                color="success",
                            ),
                            href="/transactions/add",
                            target="_parent"
                        )
                    ], className="d-flex")
                ], className="d-flex justify-content-start"),  # This pushes the button group to the right
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

        # Reimbursement info message container
        html.Div(id='reimbursement-info', className='mb-3'),
        
        # Transactions table header and table
        html.H2(id='transactions-header', className='mt-4 mb-3'),
        dash_table.DataTable(
            id='transactions-table',
            columns=base_columns,
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
        Output('transactions-table', 'columns'),
        Output('reimbursement-info', 'children')],
        [Input('refresh-trigger', 'data'),
        Input('property-filter', 'value'),
        Input('type-filter', 'value'),
        Input('reimbursement-filter', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        Input('description-search', 'value')]
    )
    def update_table(refresh_trigger, property_id, transaction_type, reimbursement_status, 
                    start_date, end_date, description_search):
        current_app.logger.debug(f"Table refresh triggered. Refresh value: {refresh_trigger}")
        try:
            logger.debug(f"Updating table with filters: property={property_id}, "
                        f"type={transaction_type}, status={reimbursement_status}, "
                        f"dates={start_date} to {end_date}, "
                        f"description_search={description_search}")

            # Initialize reimbursement info message as None
            reimbursement_info = None

            # Validate inputs
            if transaction_type and transaction_type not in VALID_TRANSACTION_TYPES:
                logger.warning(f"Invalid transaction type received: {transaction_type}")
                return [], "Invalid transaction type", [], base_columns, None

            if reimbursement_status not in VALID_REIMBURSEMENT_STATUS:
                logger.warning(f"Invalid reimbursement status received: {reimbursement_status}")
                return [], "Invalid reimbursement status", [], base_columns, None

            date_valid, date_error = validate_date_range(start_date, end_date)
            if not date_valid:
                logger.warning(f"Invalid date range: {date_error}")
                return [], date_error, [], base_columns, None

            # Get and validate properties
            try:
                properties = get_properties_for_user(
                    current_user.id,
                    current_user.name,
                    current_user.role == 'Admin'
                )
                if not validate_property_id(property_id, properties):
                    logger.warning(f"Invalid property ID received: {property_id}")
                    return [], "Invalid property selected", [], base_columns, None
                
            except Exception as e:
                logger.error(f"Error retrieving properties: {str(e)}")
                return [], "Error loading properties", [], base_columns, None

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
                return [], "Error loading transactions", property_options, base_columns, None

            # Process transactions
            try:
                df = pd.DataFrame(transactions)
                if df.empty:
                    logger.info("No transactions found matching criteria")
                    return [], "No transactions found", property_options, base_columns, None

                # Apply type filter
                if transaction_type:
                    df = df[df['type'].str.lower() == transaction_type.lower()]

                # Apply description search filter if provided
                if description_search and not df.empty:
                    description_search = description_search.lower().strip()
                    df = df[df['description'].str.lower().str.contains(description_search, na=False)]
                    if df.empty:
                        logger.info(f"No transactions found matching description: {description_search}")
                        return [], f"No transactions found matching '{description_search}'", property_options, base_columns, None

                # Define columns based on property filter and ownership
                columns = base_columns.copy()
                wholly_owned = False

                # Check property ownership and adjust columns
                if property_id and property_id != 'all':
                    logger.debug(f"Selected specific property: {property_id}")
                    # Remove property column when specific property is selected
                    columns = [col for col in columns if col['id'] != 'property_id']
                    
                    # Check if property is wholly owned by current user
                    property_data = next(
                        (prop for prop in properties if prop['address'] == property_id),
                        None
                    )
                    
                    if property_data:
                        logger.debug(f"Found property data: {property_data}")
                        wholly_owned = is_wholly_owned_by_user(property_data, current_user.name)
                        logger.debug(f"Property {property_id} wholly owned status: {wholly_owned}")
                        
                        if wholly_owned:
                            logger.debug("Removing reimbursement columns for wholly owned property")
                            # Remove reimbursement-related columns for wholly owned properties
                            reimbursement_columns = ['date_shared', 'share_description', 'reimbursement_documentation']
                            columns = [col for col in columns if col['id'] not in reimbursement_columns]
                            
                            # Remove reimbursement data from DataFrame
                            for col in reimbursement_columns:
                                if col in df.columns:
                                    df = df.drop(columns=[col])
                            
                            # Create info message
                            reimbursement_info = html.Div([
                                html.I(className="bi bi-info-circle me-2"),
                                "Reimbursement columns are hidden because this property is wholly owned by you."
                            ], className="alert alert-info")

                else:
                    # Show property column with truncated address for 'all' or no selection
                    df['property_id'] = df['property_id'].apply(lambda x: ', '.join(x.split(',')[:2]).strip() if x else '')

                # Add the documentation columns with markdown presentation
                doc_columns = []
                doc_columns.append({
                    'name': 'Transaction Doc',
                    'id': 'documentation_file',
                    'presentation': 'markdown',
                    'type': 'text'
                })
                
                if not wholly_owned:
                    doc_columns.append({
                        'name': 'Reimb. Doc',
                        'id': 'reimbursement_documentation',
                        'presentation': 'markdown',
                        'type': 'text'
                    })
                
                columns = [col for col in columns if col['id'] not in ['documentation_file', 'reimbursement_documentation']]
                columns.extend(doc_columns)

                # Format amounts with validation
                df['amount'] = df['amount'].apply(
                    lambda x: f"${abs(float(x)):.2f}" if pd.notnull(x) and isinstance(x, (int, float)) else ''
                )

                # Format documentation links
                df['documentation_file'] = df['documentation_file'].apply(
                    lambda x: f'<a href="{url_for("transactions.get_artifact", filename=x)}" target="_blank" class="btn btn-sm btn-primary">View</a>' if x else ''
                )

                if not wholly_owned and 'reimbursement_documentation' in df.columns:
                    df['reimbursement_documentation'] = df.apply(
                        lambda row: (f'<a href="{url_for("transactions.get_artifact", filename=row.get("reimbursement", {}).get("documentation"))}" target="_blank" class="btn btn-sm btn-primary">View</a>'
                                    if isinstance(row.get('reimbursement'), dict) 
                                    and row.get('reimbursement', {}).get('documentation')
                                    else ''),
                        axis=1
                    )

                # Add edit column based on property manager status
                if current_user.is_authenticated:
                    filter_options = {
                        'property_id': property_id,
                        'transaction_type': transaction_type,
                        'reimbursement_status': reimbursement_status,
                        'start_date': start_date,
                        'end_date': end_date,
                        'description_search': description_search
                    }
                    encoded_filter_options = urllib.parse.quote(json.dumps(filter_options))

                    property_manager_status = {}
                    for prop in properties:
                        is_manager = any(
                            partner['name'] == current_user.name and 
                            partner.get('is_property_manager', False)
                            for partner in prop.get('partners', [])
                        )
                        property_manager_status[prop['address']] = is_manager

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

                    # Update the columns definition to include delete button for property managers
                    df['delete'] = df.apply(
                        lambda row: (
                            f'<a href="#" class="btn btn-sm btn-danger" '
                            f'data-action="delete-transaction" '
                            f'data-id="{str(row["id"])}" '
                            f'data-description="{row["description"]}">'
                            f'Delete</a>'
                            if property_manager_status.get(row['property_id'], False)
                            else '<span class="text-muted">Delete Restricted</span>'
                        ),
                        axis=1
                    )
                    columns.append({'name': 'Delete', 'id': 'delete', 'presentation': 'markdown'})

                # Create header
                header = create_header(
                    'Income' if transaction_type == 'income' else 'Expense' if transaction_type == 'expense' else 'All',
                    property_id if property_id and property_id != 'all' else 'All Properties',
                    start_date or 'Earliest',
                    end_date or 'Latest'
                )
                if description_search:
                    header += f" (Filtered by: '{description_search}')"

                logger.debug(f"Returning {len(df)} processed transactions")
                return df.to_dict('records'), header, property_options, columns, reimbursement_info

            except Exception as e:
                logger.error(f"Error processing transactions: {str(e)}")
                return [], "Error processing data", property_options, base_columns, None

        except Exception as e:
            logger.error(f"Unexpected error in update_table: {str(e)}\n{traceback.format_exc()}")
            return [], "An unexpected error occurred", [], base_columns, None
        
    # Filter options update callback
    @dash_app.callback(
        Output('filter-options', 'data'),
        [Input('property-filter', 'value'),
         Input('type-filter', 'value'),
         Input('reimbursement-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('description-search', 'value')]  # Add this new input
    )
    def update_filter_options(property_id, transaction_type, reimbursement_status, 
                            start_date, end_date, description_search):
        return {
            'property_id': property_id,
            'transaction_type': transaction_type,
            'reimbursement_status': reimbursement_status,
            'start_date': start_date,
            'end_date': end_date,
            'description_search': description_search  # Add this new field
        }
    
    @dash_app.callback(
        [Output("delete-modal", "is_open"),
        Output("delete-transaction-id", "data"),
        Output("refresh-trigger", "data")],
        [Input("transactions-table", "active_cell"),
        Input("delete-cancel", "n_clicks"),
        Input("delete-confirm", "n_clicks")],
        [State("transactions-table", "data"),
        State("delete-modal", "is_open"),
        State("delete-transaction-id", "data"),
        State("refresh-trigger", "data")],
        prevent_initial_call=True
    )
    def manage_delete_modal(active_cell, cancel_clicks, confirm_clicks, 
                        table_data, is_open, transaction_id, current_refresh):
        ctx = dash.callback_context
        if not ctx.triggered:
            return False, None, dash.no_update
        
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "transactions-table":
            if active_cell:
                row = table_data[active_cell["row"]]
                if (active_cell["column_id"] == "delete" and 
                    'data-action="delete-transaction"' in row["delete"]):
                    import re
                    match = re.search(r'data-id="([^"]+)"', row["delete"])
                    if match:
                        return True, match.group(1), dash.no_update
        
        elif trigger_id == "delete-confirm" and confirm_clicks:
            if transaction_id:
                try:
                    with current_app.test_client() as client:
                        with client.session_transaction() as sess:
                            for key in session:
                                sess[key] = session[key]
                            sess['_user_id'] = current_user.get_id()
                            sess['_fresh'] = True
                        
                        response = client.delete(f'/transactions/delete/{transaction_id}')
                        
                        if response.status_code == 200:
                            response_data = response.get_json()
                            if response_data and response_data.get('success'):
                                return False, 'deleted', datetime.now().isoformat()
                        
                        return True, transaction_id, dash.no_update
                            
                except Exception as e:
                    current_app.logger.error(f"Error in delete process: {str(e)}")
                    return True, transaction_id, dash.no_update
        
        elif trigger_id == "delete-cancel":
            return False, None, dash.no_update
            
        return is_open, transaction_id, dash.no_update

    # Add clientside callback for showing toastr messages
    dash_app.clientside_callback(
        """
        function(data, columns, header) {
            if (window.delete_transaction_id === 'deleted') {
                setTimeout(() => {
                    try {
                        if (typeof jQuery !== 'undefined' && typeof toastr !== 'undefined') {
                            jQuery(document).ready(function($) {
                                toastr.options = {
                                    "closeButton": true,
                                    "debug": false,
                                    "newestOnTop": false,
                                    "progressBar": true,
                                    "positionClass": "toast-bottom-right",
                                    "preventDuplicates": true,
                                    "onclick": null,
                                    "showDuration": "300",
                                    "hideDuration": "1000",
                                    "timeOut": "5000",
                                    "extendedTimeOut": "1000",
                                    "showEasing": "swing",
                                    "hideEasing": "linear",
                                    "showMethod": "fadeIn",
                                    "hideMethod": "fadeOut"
                                };
                                toastr.success('Transaction deleted successfully');
                            });
                        } else {
                            console.log('jQuery or toastr not loaded yet');
                        }
                    } catch (e) {
                        console.error('Error showing toastr notification:', e);
                    }
                }, 500); // Increased delay to ensure libraries are loaded
                window.delete_transaction_id = null;
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output('transactions-table', 'data', allow_duplicate=True),
        [Input('transactions-table', 'data'),
        Input('transactions-table', 'columns'),
        Input('transactions-header', 'children')],
        prevent_initial_call=True
    )

    # Add store for delete status
    dash_app.clientside_callback(
        """
        function(delete_transaction_id) {
            window.delete_transaction_id = delete_transaction_id;
            return window.dash_clientside.no_update;
        }
        """,
        Output('delete-transaction-id', 'data', allow_duplicate=True),
        Input('delete-transaction-id', 'data'),
        prevent_initial_call=True
    )

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
                                    # Check if it's a reimbursement document (starts with reimb_)
                                    if filename.startswith('reimb_'):
                                        file_path = os.path.join(current_app.config['REIMBURSEMENTS_DIR'], filename)
                                    else:
                                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                                    
                                    if os.path.exists(file_path):
                                        # Add to reimbursements subfolder
                                        zip_file.write(
                                            file_path, 
                                            f"reimbursement_documents/{filename}"
                                        )
                                        added_files['reimbursement_docs'].add(filename)
                                        current_app.logger.debug(f"Added reimbursement document: {filename} from {file_path}")
                                    else:
                                        current_app.logger.warning(f"Reimbursement document not found at {file_path}")
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