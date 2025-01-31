import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import json
import urllib.parse
from datetime import datetime, timedelta
from flask_login import current_user
from flask import current_app, url_for
import io
import zipfile
import os
import re
from urllib.parse import unquote
import traceback
import logging
from typing import Dict, List, Optional, Tuple
from services.transaction_service import get_transactions_for_view, get_properties_for_user, format_address
from services.transaction_report_generator import TransactionReportGenerator

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constants
MAX_DESCRIPTION_LENGTH = 500
VALID_TRANSACTION_TYPES = ['income', 'expense']
VALID_REIMBURSEMENT_STATUS = ['all', 'pending', 'completed']
MIN_DATE = '2000-01-01'
MAX_FUTURE_DAYS = 30

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

def validate_property_data(property_data: Dict, username: str) -> Tuple[bool, str]:
    """
    Validate property data structure and required fields.
    
    Args:
        property_data: Dictionary containing property information
        username: Current user's username
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if property data is a dictionary
        if not isinstance(property_data, dict):
            return False, "Property data is not in the correct format"
            
        # Required fields for loan calculations
        loan_fields = ['primary_loan_amount', 'primary_loan_rate', 'primary_loan_term', 
                      'primary_loan_start_date', 'purchase_price']
        missing_loan_fields = [field for field in loan_fields if field not in property_data]
        if missing_loan_fields:
            return False, f"Missing required loan fields: {', '.join(missing_loan_fields)}"
            
        # Validate monthly income structure
        monthly_income = property_data.get('monthly_income', {})
        if not isinstance(monthly_income, dict):
            return False, "Invalid monthly income format"
        
        # Validate monthly expenses structure
        monthly_expenses = property_data.get('monthly_expenses', {})
        if not isinstance(monthly_expenses, dict):
            return False, "Invalid monthly expenses format"
            
        # Validate partners data
        partners = property_data.get('partners', [])
        if not isinstance(partners, list):
            return False, "Invalid partners format"
            
        # Check if user has an equity share
        if not any(partner.get('name') == username for partner in partners):
            return False, f"User {username} has no equity share in this property"
            
        return True, ""
        
    except Exception as e:
        logger.error(f"Error validating property data: {str(e)}")
        logger.error(traceback.format_exc())
        return False, f"Validation error: {str(e)}"

def calculate_loan_metrics(property_data: Dict, username: str) -> Optional[Dict]:
    """Calculate loan and equity metrics for a property, adjusted for user's equity share."""
    try:
        logger.info(f"Calculating loan metrics for property {property_data.get('address')}")
        
        # Validate property data
        is_valid, error_message = validate_property_data(property_data, username)
        if not is_valid:
            logger.error(f"Invalid property data: {error_message}")
            return None
        
        # Get user's equity share
        equity_share = calculate_user_equity_share(property_data, username)
        if equity_share == 0:
            logger.warning(f"No equity share for user {username}")
            return None
            
        # Get and validate loan parameters
        loan_amount = safe_float(property_data.get('primary_loan_amount'))
        interest_rate = safe_float(property_data.get('primary_loan_rate')) / 100
        loan_term_months = safe_float(property_data.get('primary_loan_term'))
        purchase_price = safe_float(property_data.get('purchase_price'))
        
        try:
            loan_start_date = datetime.strptime(
                property_data.get('primary_loan_start_date', date.today().strftime('%Y-%m-%d')), 
                '%Y-%m-%d'
            ).date()
        except ValueError as e:
            logger.error(f"Invalid loan start date: {str(e)}")
            return None
        
        logger.debug(f"Loan parameters - Amount: ${loan_amount:,.2f}, "
                    f"Rate: {interest_rate:.2%}, Term: {loan_term_months} months")
        
        # Calculate monthly payment
        try:
            if interest_rate > 0 and loan_term_months > 0:
                monthly_rate = interest_rate / 12
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** loan_term_months) / \
                                ((1 + monthly_rate) ** loan_term_months - 1)
            else:
                monthly_payment = loan_amount / loan_term_months if loan_term_months > 0 else 0
                
            logger.debug(f"Calculated monthly payment: ${monthly_payment:,.2f}")
                
        except ZeroDivisionError:
            logger.error("Error calculating monthly payment: Division by zero")
            return None
        
        # Calculate cash on cash return
        coc_return = calculate_cash_on_cash_return(property_data, username)
        
        # Calculate months into loan
        today = date.today()
        months_into_loan = relativedelta(today, loan_start_date).months + \
                          relativedelta(today, loan_start_date).years * 12
        
        # Calculate equity and principal paid
        balance = loan_amount
        total_principal_paid = 0
        current_month_principal = 0
        
        for month in range(min(months_into_loan, int(loan_term_months))):
            if balance <= 0:
                break
                
            interest_payment = balance * (interest_rate / 12)
            principal_payment = monthly_payment - interest_payment
            balance = max(0, balance - principal_payment)
            
            if month == months_into_loan - 1:  # Last month
                current_month_principal = principal_payment
            total_principal_paid += principal_payment

        logger.info(f"Loan metrics calculated successfully for {property_data.get('address')}")
        
        # Return metrics adjusted for user's equity share
        return {
            'address': property_data.get('address', 'Unknown'),
            'purchase_price': purchase_price * equity_share,
            'loan_amount': loan_amount * equity_share,
            'current_balance': balance * equity_share,
            'monthly_payment': monthly_payment * equity_share,
            'equity_from_principal': total_principal_paid * equity_share,
            'equity_this_month': current_month_principal * equity_share,
            'total_equity': (purchase_price - balance) * equity_share,
            'months_paid': months_into_loan,
            'equity_share': equity_share * 100,  # Store as percentage
            'cash_on_cash': coc_return  # Add Cash on Cash return
        }
        
    except Exception as e:
        logger.error(f"Error calculating loan metrics: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def calculate_monthly_cashflow(property_data: Dict, username: str) -> Optional[Dict]:
    """Calculate monthly cash flow metrics for a property, adjusted for user's equity share."""
    try:
        logger.info(f"Calculating monthly cash flow for property {property_data.get('address')}")
        
        # Validate property data
        is_valid, error_message = validate_property_data(property_data, username)
        if not is_valid:
            logger.error(f"Invalid property data: {error_message}")
            return None
        
        # Calculate equity share
        equity_share = calculate_user_equity_share(property_data, username)
        if equity_share == 0:
            logger.warning(f"No equity share for user {username}")
            return None
            
        # Calculate total monthly income
        monthly_income_data = property_data.get('monthly_income', {})
        monthly_income = sum([
            safe_float(monthly_income_data.get('rental_income')),
            safe_float(monthly_income_data.get('parking_income')),
            safe_float(monthly_income_data.get('laundry_income')),
            safe_float(monthly_income_data.get('other_income'))
        ])
        
        # Calculate monthly expenses and loan payments
        monthly_expenses = property_data.get('monthly_expenses', {})
        
        # Calculate utilities total
        utilities = monthly_expenses.get('utilities', {})
        total_utilities = sum(safe_float(val) for val in utilities.values())
        
        # Calculate total operating expenses
        operating_expenses = sum([
            safe_float(monthly_expenses.get('property_tax')),
            safe_float(monthly_expenses.get('insurance')),
            safe_float(monthly_expenses.get('repairs')),
            safe_float(monthly_expenses.get('capex')),
            safe_float(monthly_expenses.get('property_management')),
            safe_float(monthly_expenses.get('hoa_fees')),
            safe_float(monthly_expenses.get('other_expenses')),
            total_utilities
        ])
        
        # Calculate primary mortgage payment
        try:
            loan_amount = safe_float(property_data.get('primary_loan_amount'))
            interest_rate = safe_float(property_data.get('primary_loan_rate')) / 100
            loan_term_months = safe_float(property_data.get('primary_loan_term'))
            
            if interest_rate > 0 and loan_term_months > 0:
                monthly_rate = interest_rate / 12
                mortgage_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** loan_term_months) / \
                                 ((1 + monthly_rate) ** loan_term_months - 1)
            else:
                mortgage_payment = loan_amount / loan_term_months if loan_term_months > 0 else 0
        except Exception as e:
            logger.error(f"Error calculating mortgage payment: {str(e)}")
            mortgage_payment = 0

        # Calculate net cash flow
        net_cashflow = monthly_income - operating_expenses - mortgage_payment
        
        # Return metrics adjusted for user's equity share
        return {
            'address': property_data.get('address', 'Unknown'),
            'monthly_income': monthly_income * equity_share,
            'monthly_expenses': operating_expenses * equity_share,
            'mortgage_payment': mortgage_payment * equity_share,
            'net_cashflow': net_cashflow * equity_share,
            'equity_share': equity_share * 100
        }
            
    except Exception as e:
        logger.error(f"Error calculating cash flow metrics: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def calculate_cash_on_cash_return(property_data: Dict, username: str) -> float:
    """
    Calculate Cash on Cash return for a property.
    
    Args:
        property_data: Dictionary containing property information
        username: Current user's username
        
    Returns:
        Cash on Cash return as a percentage
    """
    try:
        # Calculate total cash invested
        total_investment = sum([
            safe_float(property_data.get('down_payment', 0)),
            safe_float(property_data.get('closing_costs', 0)),
            safe_float(property_data.get('renovation_costs', 0)),
            safe_float(property_data.get('marketing_costs', 0)),
            safe_float(property_data.get('holding_costs', 0))
        ])
        
        if total_investment <= 0:
            return 0.0
            
        # Calculate annual cash flow
        cashflow = calculate_monthly_cashflow(property_data, username)
        if not cashflow:
            return 0.0
            
        annual_cashflow = cashflow['net_cashflow'] * 12
        
        # Calculate CoC return
        coc_return = (annual_cashflow / total_investment) * 100
        
        return round(coc_return, 2)
        
    except Exception as e:
        logger.error(f"Error calculating Cash on Cash return: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.0

def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> tuple[bool, str]:
    """Validates the date range for transactions."""
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
    """Checks if a property is wholly owned by the user."""
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

def create_responsive_table(property_metrics, cashflow_metrics):
    """Create a mobile-responsive property details table."""
    try:
        # Create table with bootstrap classes
        return dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Property", className="text-center text-white", 
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0}),
                    html.Th("Share", className="text-center text-white d-none d-md-table-cell",
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0}),
                    html.Th("Monthly Income", className="text-center text-white",
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0}),
                    html.Th("Monthly Expenses", className="text-center text-white d-none d-md-table-cell",
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0}),
                    html.Th("Net Cash Flow", className="text-center text-white",
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0}),
                    html.Th("Total Equity", className="text-center text-white d-none d-md-table-cell",
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0}),
                    html.Th("Monthly Equity Gain", className="text-center text-white d-none d-md-table-cell",
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0}),
                    html.Th("Cash on Cash", className="text-center text-white",
                           style={'backgroundColor': '#000080', 'position': 'sticky', 'top': 0})
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(cm['address'].split(',')[0], className="text-nowrap"),
                    html.Td(f"{cm['equity_share']}%", className="d-none d-md-table-cell"),
                    html.Td(f"${cm['monthly_income']:,.2f}"),
                    html.Td(
                        f"${(cm['monthly_expenses'] + cm['mortgage_payment'] + cm['seller_payment']):,.2f}",
                        className="d-none d-md-table-cell"
                    ),
                    html.Td(
                        html.Span(
                            f"${cm['net_cashflow']:,.2f}",
                            style={'color': 'green' if cm['net_cashflow'] >= 0 else 'red'}
                        )
                    ),
                    html.Td(f"${pm['total_equity']:,.2f}", className="d-none d-md-table-cell"),
                    html.Td(f"${pm['equity_this_month']:,.2f}", className="d-none d-md-table-cell"),
                    html.Td(f"{pm['cash_on_cash']:,.1f}%")
                ], className="align-middle") for cm, pm in zip(cashflow_metrics, property_metrics)
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-4 table-sm")
        
    except Exception as e:
        logger.error(f"Error creating property table: {str(e)}")
        logger.error(traceback.format_exc())
        return html.Div("Error creating property table", className="text-danger p-3")

def create_transactions_dash(flask_app):
    """Creates and configures the mobile-first Dash application for transaction management."""
    template_path = os.path.join(flask_app.root_path, 'templates', 'dashboards', 'dash_transactions.html')
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
            'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js'
        ],
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )

    # Load custom HTML template
    dash_app.index_string = open(template_path).read()

    # Define the mobile-first layout
    dash_app.layout = dbc.Container([
        # State management stores
        dcc.Store(id='refresh-trigger', storage_type='memory'),
        dcc.Store(id='filter-options', storage_type='session'),
        
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
                                {'label': 'All', 'value': 'all'},  # Add this option
                                {'label': 'Incomes', 'value': 'income'},
                                {'label': 'Expenses', 'value': 'expense'}
                            ],
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
                        dcc.DatePickerRange(
                            id='date-range',
                            className='mb-3',
                            style={'width': '100%'}
                        )
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

    # Register callbacks
    @dash_app.callback(
        [Output('transactions-table', 'data'),
        Output('transactions-header', 'children'),
        Output('property-filter', 'options'),
        Output('transactions-table', 'columns'),
        Output('error-display', 'children'),
        Output('error-display', 'is_open')],
        [Input('refresh-trigger', 'data'),
        Input('property-filter', 'value'),
        Input('type-filter', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date'),
        Input('description-search', 'value')],
        [State('reimbursement-filter', 'value')]
    )
    def update_table(refresh_trigger, property_id, transaction_type, 
                    start_date, end_date, description_search, reimbursement_status):
        try:
            logger.debug("=== Starting update_table function ===")
            
            # Get properties
            properties = get_properties_for_user(
                current_user.id,
                current_user.name,
                current_user.role == 'Admin'
            )
            
            # Create property options with standardized addresses
            property_options = [{'label': 'All Properties', 'value': 'all'}]
            for prop in properties:
                if prop.get('address'):
                    # Get the base address for both display and value
                    base_address = format_address(prop['address'], 'base')
                    property_options.append({
                        'label': base_address,  # Show simplified address in dropdown
                        'value': prop['address']  # Keep full address as value
                    })
            logger.debug(f"Created {len(property_options)} property options")

            # Get transactions
            # Get transactions
            effective_property_id = None if not property_id or property_id == 'all' else property_id
            transactions = get_transactions_for_view(
                current_user.id,
                current_user.name,
                effective_property_id,
                reimbursement_status,
                start_date,
                end_date,
                current_user.role == 'Admin'
            )

            logger.debug(f"Retrieved {len(transactions) if transactions else 0} transactions")

            # Process transactions
            df = pd.DataFrame(transactions if transactions else [])
            logger.debug(f"Created DataFrame with {len(df)} rows")
            
            if df.empty:
                logger.debug("DataFrame is empty, returning early")
                return [], "No transactions found", property_options, [], "", False

            # Format property addresses in transactions
            if 'property_id' in df.columns:
                df['property_id'] = df['property_id'].apply(lambda x: format_address(x, 'display'))

            # Apply filters
            if transaction_type and transaction_type != 'all':  # Only filter if a specific type is selected
                logger.debug(f"Filtering by transaction type: {transaction_type}")
                df = df[df['type'].str.lower() == transaction_type.lower()]
                logger.debug(f"After type filter: {len(df)} rows")
                
            if description_search:
                logger.debug(f"Filtering by description: {description_search}")
                df = df[df['description'].str.lower().str.contains(description_search.lower(), na=False)]
                logger.debug(f"After description filter: {len(df)} rows")

            # Format data for display
            df = format_transactions_for_mobile(df, properties, property_id, current_user)
            logger.debug(f"After mobile formatting: {len(df)} rows")
            logger.debug(f"DataFrame columns: {df.columns.tolist()}")

            # Create columns
            columns = create_mobile_columns(property_id, df)
            logger.debug(f"Created {len(columns)} columns")

            # Create header
            header = create_mobile_header(transaction_type, property_id, start_date, end_date, description_search)
            logger.debug(f"Created header: {header}")

            # Prepare final data
            final_data = df.to_dict('records')
            logger.debug(f"Final data has {len(final_data)} rows")

            return (
                final_data,
                header,
                property_options,
                columns,
                "",
                False
            )

        except Exception as e:
            logger.error(f"Error in update_table: {str(e)}")
            logger.error(traceback.format_exc())
            return [], "", property_options, [], f"An error occurred: {str(e)}", True

    @dash_app.callback(
        Output("download-pdf", "data"),
        [Input("download-pdf-btn", "n_clicks")],
        [State("transactions-table", "data"),
        State("property-filter", "value"),
        State("date-range", "start_date"),
        State("date-range", "end_date")]
    )
    def generate_pdf_report(n_clicks, transactions_data, property_id, start_date, end_date):
        """Generate mobile-friendly PDF report."""
        if not n_clicks or not transactions_data:
            return None

        try:
            logger.debug(f"Generating PDF report for {len(transactions_data)} transactions")
            
            # Create metadata for the report
            metadata = {
                'user': current_user.name,
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'property': property_id if property_id else 'All Properties',
                'date_range': f"{start_date} to {end_date}" if start_date and end_date else None
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
        """Generate ZIP archive with transaction documents."""
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
                                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                                if os.path.exists(file_path):
                                    logger.debug(f"Adding document: {filename}")
                                    zip_file.write(file_path, f"documents/{filename}")
                                    added_files.add(filename)
                                    
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
                                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                                if os.path.exists(file_path):
                                    logger.debug(f"Adding document: {filename}")
                                    zip_file.write(file_path, f"documents/{filename}")
                                    added_files.add(filename)
                                        
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
        Input('description-search', 'value')],
        [State('reimbursement-filter', 'value')]
    )
    def update_filter_options(property_id, transaction_type, 
                            start_date, end_date, description_search, reimbursement_status):
        return {
            'property_id': property_id,
            'transaction_type': transaction_type,
            'reimbursement_status': reimbursement_status,
            'start_date': start_date,
            'end_date': end_date,
            'description_search': description_search
        }

    @dash_app.callback(
        [Output('property-filter', 'value'),
        Output('type-filter', 'value'),
        Output('date-range', 'start_date'),
        Output('date-range', 'end_date'),
        Output('description-search', 'value')],
        [Input('refresh-trigger', 'data')],
        [State('filter-options', 'data')]
    )
    def restore_filters(trigger, filter_data):
        if not filter_data:
            return [None, None, None, None, None]
        
        try:
            return [
                filter_data.get('property_id'),
                filter_data.get('transaction_type'),
                filter_data.get('start_date'),
                filter_data.get('end_date'),
                filter_data.get('description_search')
            ]
        except Exception as e:
            logger.error(f"Error restoring filters: {str(e)}")
            return [None, None, None, None, None]

    def check_property_ownership(property_id):
        """Check if a property is wholly owned by the current user."""
        try:
            if property_id and property_id != 'all':
                properties = get_properties_for_user(
                    current_user.id,
                    current_user.name,
                    current_user.role == 'Admin'
                )
                property_data = next((p for p in properties if p['address'] == property_id), None)
                if property_data:
                    return is_wholly_owned_by_user(property_data, current_user.name)
            return False
        except Exception as e:
            logger.error(f"Error checking property ownership: {str(e)}")
            return False

    @dash_app.callback(
        [Output('reimbursement-filter-container', 'style'),
        Output('reimbursement-filter', 'value'),
        Output('reimbursement-info', 'children')],
        [Input('property-filter', 'value'),
        Input('refresh-trigger', 'data')],
        [State('filter-options', 'data')]
    )
    def update_reimbursement_controls(property_id, trigger, filter_data):
        """Single source of truth for all reimbursement-related UI updates."""
        try:
            # Default values
            style = {'display': 'block'}
            filter_value = 'all'
            info = None

            if property_id and property_id != 'all':
                properties = get_properties_for_user(
                    current_user.id,
                    current_user.name,
                    current_user.role == 'Admin'
                )
                property_data = next((p for p in properties if p['address'] == property_id), None)
                
                if property_data and is_wholly_owned_by_user(property_data, current_user.name):
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

    def format_transactions_for_mobile(df, properties, property_id, user):
        """Format transaction data for mobile display with reimbursement handling."""
        try:
            # Store original dates for sorting
            df['sort_date'] = pd.to_datetime(df['date'])
            df['date_for_sort'] = df['sort_date']  # Keep original datetime for sorting
            df['date'] = df['sort_date'].dt.strftime('%m/%d/%Y')

            # Format currency
            df['amount_for_sort'] = df['amount'].astype(float)  # Keep original number for sorting
            df['amount'] = df['amount_for_sort'].apply(lambda x: f"${abs(float(x)):,.2f}")

            # Handle property display and sorting
            if not property_id or property_id == 'all':
                df['property_display'] = df['property_id'].apply(lambda x: ', '.join(x.split(',')[:2]).strip())
            else:
                df['property_display'] = df['property_id'].apply(lambda x: ', '.join(x.split(',')[:2]).strip())

            # Check property ownership
            is_wholly_owned = check_property_ownership(property_id)

            # Format documentation links
            df['documentation_file'] = df['documentation_file'].apply(
                lambda x: create_mobile_button(x, 'View', 'primary') if x else ''
            )

            # Handle notes
            if 'notes' not in df.columns:
                df['notes'] = ''
            df['notes'] = df['notes'].fillna('')

            # Add action buttons
            df['edit'] = df.apply(lambda row: f'<button class="btn btn-sm btn-warning m-1" onclick="window.parent.viewTransactionsModule.handleEditTransaction(\'{row.id}\', \'{row.description}\')">Edit<i class="bi bi-pencil"></i></button>', axis=1)
            df['delete'] = df.apply(lambda row: f'<button class="btn btn-sm btn-danger m-1" onclick="window.parent.viewTransactionsModule.handleDeleteTransaction(\'{row.id}\', \'{row.description}\')">Delete<i class="bi bi-trash"></i></button>', axis=1)

            # Handle reimbursement data
            if not is_wholly_owned and 'date_shared' in df.columns:
                df['sort_date_shared'] = pd.to_datetime(df['date_shared'])
                df['date_shared_for_sort'] = df['sort_date_shared']  # Keep original datetime for sorting
                df['date_shared'] = df['sort_date_shared'].dt.strftime('%m/%d/%Y')
                
                df['reimbursement_documentation'] = df['reimbursement_documentation'].apply(
                    lambda x: create_mobile_button(x, 'View', 'primary') if x else ''
                )
            else:
                for col in ['date_shared', 'reimbursement_documentation', 'sort_date_shared', 'date_shared_for_sort']:
                    if col in df.columns:
                        df = df.drop(columns=[col])

            return df
        except Exception as e:
            logger.error(f"Error formatting transactions: {str(e)}")
            return df

    def create_mobile_columns(property_id, df):
        """Create mobile-optimized column definitions."""
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
            columns.extend([
                {
                    'name': 'Date', 
                    'id': 'date',
                    'sortable': True,
                    'sort_by': 'date_for_sort'  # Sort by the datetime object
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
                    'sort_by': 'amount_for_sort'  # Sort by the numeric value
                },
                {
                    'name': 'Category',
                    'id': 'category',
                    'sortable': True
                },
                {
                    'name': 'Notes',
                    'id': 'notes',
                    'sortable': True
                },
                {
                    'name': 'Doc', 
                    'id': 'documentation_file', 
                    'presentation': 'markdown',
                    'type': 'text',
                    'dangerously_allow_html': True,
                    'sortable': False
                }
            ])

            # Add reimbursement columns if needed
            if property_id and property_id != 'all':
                properties = get_properties_for_user(
                    current_user.id,
                    current_user.name,
                    current_user.role == 'Admin'
                )
                property_data = next((p for p in properties if p['address'] == property_id), None)
                
                if not property_data or not is_wholly_owned_by_user(property_data, current_user.name):
                    if 'date_shared' in df.columns:
                        columns.extend([
                            {
                                'name': 'Reimb Date', 
                                'id': 'date_shared',
                                'sortable': True,
                                'sort_by': 'date_shared_for_sort'  # Sort by the datetime object
                            },
                            {
                                'name': 'Reimb Doc', 
                                'id': 'reimbursement_documentation', 
                                'presentation': 'markdown',
                                'type': 'text',
                                'sortable': False
                            }
                        ])
            else:
                if 'date_shared' in df.columns:
                    columns.extend([
                        {
                            'name': 'Reimb Date', 
                            'id': 'date_shared',
                            'sortable': True,
                            'sort_by': 'date_shared_for_sort'  # Sort by the datetime object
                        },
                        {
                            'name': 'Reimb Doc', 
                            'id': 'reimbursement_documentation', 
                            'presentation': 'markdown',
                            'type': 'text',
                            'dangerously_allow_html': True,
                            'sortable': False
                        }
                    ])

            # Action columns (not sortable)
            columns.extend([
                {
                    'name': 'Edit',
                    'id': 'edit',
                    'presentation': 'markdown',
                    'type': 'text',
                    'sortable': False
                },
                {
                    'name': 'Delete',
                    'id': 'delete',
                    'presentation': 'markdown',
                    'type': 'text',
                    'sortable': False
                }
            ])

            return columns
                
        except Exception as e:
            logger.error(f"Error creating mobile columns: {str(e)}")
            return []

    def create_mobile_header(transaction_type, property_id, start_date, end_date, description_search):
        """Create mobile-friendly header text."""
        type_text = ('Income' if transaction_type == 'income' 
                    else 'Expense' if transaction_type == 'expense' 
                    else 'All')  # Handle 'all' case
        
        property_text = property_id if property_id and property_id != 'all' else 'All Properties'
        if property_text != 'All Properties':
            property_text = ', '.join(property_text.split(',')[:2]).strip()
        
        date_range = f"{start_date or 'Earliest'} to {end_date or 'Latest'}"
        
        header = f"{type_text} Transactions"
        if description_search:
            header += f" matching '{description_search}'"
        
        return header

    def create_mobile_button(link, text, color):
        """Create a mobile-friendly button with proper spacing and icon."""
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

    return dash_app