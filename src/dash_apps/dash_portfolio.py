"""
Portfolio dashboard for the REI-Tracker application.

This module provides a Dash-based interactive dashboard for visualizing
portfolio metrics, including equity distribution, cash flow, income, and expenses.
"""

from typing import Dict, List, Optional, Tuple, Union
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask_login import current_user
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
import traceback

from src.services.property_financial_service import get_properties_for_user
from src.utils.money import Money
from src.utils.logging_utils import get_logger
from src.utils.common import safe_float
from src.utils.dash_helpers import (
    create_responsive_chart, 
    create_metric_card, 
    update_chart_layouts_for_mobile, 
    create_empty_response,
    generate_color_scale
)
from src.utils.financial_helpers import calculate_cash_on_cash_return

# Set up module-level logger
logger = get_logger(__name__)

# Mobile breakpoint constants
MOBILE_BREAKPOINT = 768
MOBILE_HEIGHT = '100vh'
DESKTOP_HEIGHT = 'calc(100vh - 150px)'

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

def calculate_user_equity_share(property_data: Dict, username: str) -> float:
    """
    Calculate the user's equity share percentage for a property.
    
    Args:
        property_data: Dictionary containing property information
        username: Current user's username
        
    Returns:
        User's equity share as a decimal (0.0 to 1.0)
    """
    try:
        logger.debug(f"Calculating equity share for user {username} in property {property_data.get('address')}")
        
        partners = property_data.get('partners', [])
        if not partners:
            logger.warning(f"No partners data found for property {property_data.get('address')}")
            return 0.0
            
        for partner in partners:
            if partner.get('name') == username:
                equity_share = safe_float(partner.get('equity_share', 0)) / 100.0
                logger.debug(f"Found equity share for {username}: {equity_share:.2%}")
                return equity_share
                
        logger.warning(f"No equity share found for user {username} in property {property_data.get('address')}")
        return 0.0
        
    except Exception as e:
        logger.error(f"Error calculating equity share: {str(e)}")
        logger.error(traceback.format_exc())
        return 0.0
    
def calculate_loan_metrics(property_data: Dict, username: str) -> Optional[Dict]:
    """
    Calculate loan and equity metrics for a property, adjusted for user's equity share.
    
    Args:
        property_data: Dictionary containing property information
        username: Current user's username
        
    Returns:
        Dictionary containing calculated metrics or None if calculation fails
    """
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
        
        # Get loan details from the property data
        loan_details = property_data.get('loan_details', {})
        if not loan_details or not loan_details.get('has_loans', False):
            # Fall back to legacy calculation if no loan details are available
            return calculate_legacy_loan_metrics(property_data, username, equity_share)
        
        # Get total debt and monthly payment
        total_debt = safe_float(loan_details.get('total_debt', 0))
        monthly_payment = safe_float(loan_details.get('monthly_payment', 0))
        
        # Get purchase price
        purchase_price = safe_float(property_data.get('purchase_price'))
        
        # Calculate total initial loan balance and monthly equity gain
        initial_loan_balance = 0
        monthly_equity_gain = 0
        equity_from_principal = 0
        
        for loan in loan_details.get('loans', []):
            loan_amount = safe_float(loan.get('amount', 0))
            initial_loan_balance += loan_amount
            monthly_equity_gain += safe_float(loan.get('monthly_principal', 0))
            equity_from_principal += safe_float(loan.get('equity_from_principal', 0))
        
        # Calculate total equity
        total_equity = purchase_price - total_debt
        
        # Calculate cash on cash return
        coc_return = calculate_cash_on_cash_return(property_data, username)
        
        logger.info(f"Loan metrics calculated successfully for {property_data.get('address')}")
        
        # Return metrics adjusted for user's equity share
        return {
            'address': property_data.get('address', 'Unknown'),
            'purchase_price': purchase_price * equity_share,
            'loan_amount': initial_loan_balance * equity_share,
            'current_balance': total_debt * equity_share,
            'monthly_payment': monthly_payment * equity_share,
            'equity_from_principal': equity_from_principal * equity_share,
            'equity_this_month': monthly_equity_gain * equity_share,
            'total_equity': total_equity * equity_share,
            'equity_share': equity_share * 100,  # Store as percentage
            'cash_on_cash': coc_return,  # Add Cash on Cash return
            'has_multiple_loans': len(loan_details.get('loans', [])) > 1,
            'loan_count': len(loan_details.get('loans', [])),
            'loan_details': loan_details
        }
        
    except Exception as e:
        logger.error(f"Error calculating loan metrics for property {property_data.get('address')}: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def calculate_legacy_loan_metrics(property_data: Dict, username: str, equity_share: float) -> Dict:
    """
    Calculate loan metrics using the legacy method (for backward compatibility).
    
    Args:
        property_data: Dictionary containing property information
        username: Current user's username
        equity_share: User's equity share as a decimal
        
    Returns:
        Dictionary containing calculated metrics
    """
    try:
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
        
        logger.debug(f"Legacy loan parameters - Amount: ${loan_amount:,.2f}, "
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

        # Calculate cash on cash return
        coc_return = calculate_cash_on_cash_return(property_data, username)

        logger.info(f"Legacy loan metrics calculated successfully for {property_data.get('address')}")
        
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
            'cash_on_cash': coc_return,  # Add Cash on Cash return
            'has_multiple_loans': False,
            'loan_count': 1
        }
        
    except Exception as e:
        logger.error(f"Error calculating legacy loan metrics: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def calculate_monthly_cashflow(property_data: Dict, username: str) -> Optional[Dict]:
    """
    Calculate monthly cash flow metrics for a property, adjusted for user's equity share.
    
    Args:
        property_data: Dictionary containing property information
        username: Current user's username
        
    Returns:
        Dictionary containing calculated cash flow metrics or None if calculation fails
    """
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
        
        logger.debug(f"Total monthly income: ${monthly_income:,.2f}")

        # Calculate monthly expenses
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
        
        logger.debug(f"Total operating expenses: ${operating_expenses:,.2f}")

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
                
            logger.debug(f"Primary mortgage payment: ${mortgage_payment:,.2f}")
                
        except Exception as e:
            logger.error(f"Error calculating mortgage payment: {str(e)}")
            mortgage_payment = 0

        # Calculate seller financing payment if applicable
        try:
            seller_amount = safe_float(property_data.get('secondary_loan_amount'))
            seller_rate = safe_float(property_data.get('secondary_loan_rate')) / 100
            seller_term = safe_float(property_data.get('secondary_loan_term'))
            
            if seller_rate > 0 and seller_term > 0:
                monthly_seller_rate = seller_rate / 12
                seller_payment = seller_amount * (monthly_seller_rate * (1 + monthly_seller_rate) ** seller_term) / \
                                ((1 + monthly_seller_rate) ** seller_term - 1)
            else:
                seller_payment = seller_amount / seller_term if seller_term > 0 else 0
                
            logger.debug(f"Seller financing payment: ${seller_payment:,.2f}")
                
        except Exception as e:
            logger.error(f"Error calculating seller financing payment: {str(e)}")
            seller_payment = 0

        # Calculate net cash flow
        net_cashflow = monthly_income - operating_expenses - mortgage_payment - seller_payment
        logger.debug(f"Net cash flow: ${net_cashflow:,.2f}")

        # Create expense breakdown
        expense_breakdown = {
            'Property Tax': safe_float(monthly_expenses.get('property_tax')),
            'Insurance': safe_float(monthly_expenses.get('insurance')),
            'Repairs': safe_float(monthly_expenses.get('repairs')),
            'CapEx': safe_float(monthly_expenses.get('capex')),
            'Property Management': safe_float(monthly_expenses.get('property_management')),
            'HOA Fees': safe_float(monthly_expenses.get('hoa_fees')),
            'Utilities': total_utilities,
            'Other': safe_float(monthly_expenses.get('other_expenses')),
            'Mortgage': mortgage_payment,
            'Seller Financing': seller_payment
        }

        # Filter out zero values from expense breakdown
        expense_breakdown = {k: v for k, v in expense_breakdown.items() if v > 0}
        
        logger.info(f"Cash flow calculation completed for {property_data.get('address')}")

        # Return metrics adjusted for user's equity share
        return {
            'address': property_data.get('address', 'Unknown'),
            'monthly_income': monthly_income * equity_share,
            'monthly_expenses': operating_expenses * equity_share,
            'mortgage_payment': mortgage_payment * equity_share,
            'seller_payment': seller_payment * equity_share,
            'net_cashflow': net_cashflow * equity_share,
            'expense_breakdown': {k: v * equity_share for k, v in expense_breakdown.items()},
            'equity_share': equity_share * 100
        }
            
    except Exception as e:
        logger.error(f"Error calculating cash flow metrics for property {property_data.get('address')}: {str(e)}")
        logger.error(traceback.format_exc())
        return None
    

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

def create_equity_chart(equity_data):
    """Create the equity distribution pie chart."""
    return px.pie(
        values=[float(item['value']) for item in equity_data],
        names=[str(item['name']) for item in equity_data],
        hole=0.4,
        title="Equity Distribution"
    )

def create_cashflow_chart(cashflow_data):
    """Create the cash flow bar chart."""
    return px.bar(
        x=[str(m['address']).split(',')[0] + f" ({m['equity_share']}%)" for m in cashflow_data],
        y=[float(m['net_cashflow']) for m in cashflow_data],
        color=[float(m['net_cashflow']) for m in cashflow_data],
        color_continuous_scale=[[0, '#E0FFFF'], [1, '#000080']],
        title="Cash Flow by Property"
    )

def create_income_chart(income_data):
    """Create the income breakdown pie chart."""
    return px.pie(
        values=[float(item['value']) for item in income_data],
        names=[str(item['name']) for item in income_data],
        hole=0.4,
        title="Monthly Income by Property"
    )

def create_expenses_chart(expense_data):
    """Create the expenses breakdown pie chart."""
    return px.pie(
        values=[float(item['value']) for item in expense_data],
        names=[str(item['name']) for item in expense_data],
        hole=0.4,
        title="Monthly Expenses Breakdown"
    )


def create_portfolio_dash(flask_app) -> dash.Dash:
    """
    Create the portfolio dashboard application.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dash.Dash: Configured Dash application instance
    """
    try:
        logger.info("Creating portfolio dashboard")
        
        # Initialize Dash app
        dash_app = dash.Dash(
            __name__,
            server=flask_app,
            routes_pathname_prefix='/dashboards/_dash/portfolio/',
            requests_pathname_prefix='/dashboards/_dash/portfolio/',
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        
        logger.debug("Dash app initialized successfully")

        # Define layout with time period filter
        dash_app.layout = dbc.Container([
            # Responsive viewport meta tag
            html.Meta(name="viewport", content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
            
            dcc.Store(id='session-store'),
            dcc.Store(id='viewport-size'),  # Store for tracking viewport size
            
            # Error display
            html.Div(id="error-display", className="alert alert-danger d-none"),
            
            # User context
            dbc.Row([
                dbc.Col([
                    html.P(id="user-context", className="text-muted mb-3")
                ], width=12)
            ]),
            
            # Filtering options
            dbc.Row([
                dbc.Col([
                    html.H5("Filter Options", className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Time Period"),
                            dcc.Dropdown(
                                id="time-period-filter",
                                options=[
                                    {"label": "Last 30 Days", "value": "30"},
                                    {"label": "Last 90 Days", "value": "90"},
                                    {"label": "Last 6 Months", "value": "180"},
                                    {"label": "Last 12 Months", "value": "365"},
                                    {"label": "All Time", "value": "all"}
                                ],
                                value="all",
                                clearable=False,
                                className="mb-3"
                            )
                        ], xs=12, md=6),
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Mobile-first metric cards
            dbc.Row([
                dbc.Col([create_metric_card(
                    "Portfolio Value", "total-portfolio-value", "text-primary")], 
                    xs=12, sm=6, md=4),
                dbc.Col([create_metric_card(
                    "Total Equity", "total-equity", "text-success")],
                    xs=12, sm=6, md=4),
                dbc.Col([create_metric_card(
                    "Monthly Equity Gain", "equity-gained-month", "text-info")],
                    xs=12, sm=6, md=4),
            ], className="g-2 mb-3"),  # Use spacing utility
            
            # Second row of metric cards
            dbc.Row([
                dbc.Col([create_metric_card(
                    "Gross Monthly Income", "total-monthly-income", "text-success")],
                    xs=12, sm=6, md=4),
                dbc.Col([create_metric_card(
                    "Monthly Expenses", "total-monthly-expenses", "text-danger")],
                    xs=12, sm=6, md=4),
                dbc.Col([create_metric_card(
                    "Net Monthly Cash Flow", "total-net-cashflow", "text-primary")],
                    xs=12, sm=6, md=4),
            ], className="g-2 mb-4"),
            
            # Charts with mobile-first layout
            dbc.Row([
                dbc.Col([
                    html.H4("Equity Distribution", className="text-center mb-3"),
                    html.Div(id='equity-pie-container', className="chart-container")
                ], xs=12, md=6, className="mb-4"),
                dbc.Col([
                    html.H4("Cash Flow by Property", className="text-center mb-3"),
                    html.Div(id='cashflow-bar-container', className="chart-container")
                ], xs=12, md=6, className="mb-4"),
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Monthly Income by Property", className="text-center mb-3"),
                    html.Div(id='income-pie-container', className="chart-container")
                ], xs=12, md=6, className="mb-4"),
                dbc.Col([
                    html.H4("Monthly Expenses Breakdown", className="text-center mb-3"),
                    html.Div(id='expenses-pie-container', className="chart-container")
                ], xs=12, md=6, className="mb-4"),
            ]),
            
            # Responsive table
            dbc.Row([
                dbc.Col([
                    html.H4("Property Details", className="text-center mb-3"),
                    html.Div(id='property-table-container', className="table-responsive")
                ], width=12)
            ]),
        ], fluid=True, className="px-2 px-sm-3 py-3")

        logger.debug("Dashboard layout created successfully")

        @dash_app.callback(
            Output('viewport-size', 'data'),
            [Input('session-store', 'data')],
            [State('viewport-size', 'data')]
        )
        def update_viewport_size(_, current_size):
            """Update viewport size data for responsive adjustments."""
            ctx = dash.callback_context
            if not ctx.triggered:
                raise PreventUpdate
            
            # Get window width from client side
            width = dash.no_update
            try:
                width = int(window.innerWidth)
            except:
                pass
            
            return {'width': width, 'is_mobile': width < MOBILE_BREAKPOINT}

        @dash_app.callback(
            [Output('user-context', 'children'),
             Output('total-portfolio-value', 'children'),
             Output('total-equity', 'children'),
             Output('equity-gained-month', 'children'),
             Output('total-monthly-income', 'children'),
             Output('total-monthly-expenses', 'children'),
             Output('total-net-cashflow', 'children'),
             Output('equity-pie-container', 'children'),
             Output('cashflow-bar-container', 'children'),
             Output('income-pie-container', 'children'),
             Output('expenses-pie-container', 'children'),
             Output('property-table-container', 'children'),
             Output('error-display', 'children'),
             Output('error-display', 'style')],
            [Input('session-store', 'data'),
             Input('viewport-size', 'data'),
             Input('time-period-filter', 'value')]
        )
        def update_metrics(data, viewport, time_period):
            """Update all dashboard metrics and visualizations."""
            try:
                logger.info(f"Updating metrics for user: {current_user.name}")
                
                # Get device type
                is_mobile = viewport.get('is_mobile', True) if viewport else True
                
                # Get property data
                with flask_app.app_context():
                    properties = get_properties_for_user(current_user.id, current_user.name)
                
                if not properties:
                    logger.warning(f"No properties found for user: {current_user.name}")
                    return create_empty_response("No properties found in your portfolio.")

                # Process properties and generate metrics
                logger.debug(f"Found {len(properties)} properties")
                
                # Initialize aggregation variables
                property_metrics = []
                cashflow_metrics = []
                property_income = {}
                total_value = 0
                total_equity = 0
                total_equity_this_month = 0
                total_income = 0
                total_expenses = 0
                total_net_cashflow = 0
                combined_expenses = {}
                
                # Process each property
                valid_properties = 0
                
                for prop in properties:
                    try:
                        metrics = calculate_loan_metrics(prop, current_user.name)
                        cashflow = calculate_monthly_cashflow(prop, current_user.name)
                        
                        if metrics and cashflow:  # Only include properties where calculations succeeded
                            valid_properties += 1
                            property_metrics.append(metrics)
                            cashflow_metrics.append(cashflow)
                            
                            # Get property's short name
                            property_name = f"{prop['address'].split(',')[0]} ({cashflow['equity_share']}%)"
                            
                            # Store total monthly income for this property
                            property_income[property_name] = cashflow['monthly_income']
                            
                            # Aggregate totals
                            total_value += metrics['purchase_price']
                            total_equity += metrics['total_equity']
                            total_equity_this_month += metrics['equity_this_month']
                            
                            total_income += cashflow['monthly_income']
                            total_expenses += (cashflow['monthly_expenses'] + 
                                            cashflow['mortgage_payment'] + 
                                            cashflow['seller_payment'])
                            total_net_cashflow += cashflow['net_cashflow']
                            
                            # Aggregate expenses by category
                            for category, amount in cashflow['expense_breakdown'].items():
                                combined_expenses[category] = combined_expenses.get(category, 0) + amount
                                
                    except Exception as e:
                        logger.error(f"Error processing property {prop.get('address')}: {str(e)}")
                        logger.error(traceback.format_exc())
                        continue
                
                if valid_properties == 0:
                    logger.warning("No valid property metrics calculated")
                    return create_empty_response("Unable to calculate property metrics.")

                # Sort properties by income for consistent color assignment
                property_income = dict(sorted(property_income.items(), 
                                        key=lambda x: x[1], 
                                        reverse=True))
                
                # Prepare all sorted data first
                logger.debug("Preparing sorted data for charts")

                # Sort and prepare equity data
                equity_data = sorted([
                    {'name': f"{m['address'].split(',')[0]} ({m['equity_share']}%)",
                        'value': m['total_equity']} 
                    for m in property_metrics
                ], key=lambda x: x['value'], reverse=True)

                # Sort and prepare cashflow data
                sorted_cashflow = sorted(cashflow_metrics, 
                                        key=lambda x: x['net_cashflow'], 
                                        reverse=True)

                # Sort and prepare income data
                income_data = sorted([
                    {'name': name, 'value': value} 
                    for name, value in property_income.items()
                ], key=lambda x: x['value'], reverse=True)

                # Sort and prepare expense data
                expense_data = sorted([
                    {'name': name, 'value': value} 
                    for name, value in combined_expenses.items()
                ], key=lambda x: x['value'], reverse=True)

                logger.debug("Data preparation complete")
                
                # Create and update charts for mobile
                equity_fig = create_equity_chart(equity_data)
                cashflow_fig = create_cashflow_chart(sorted_cashflow)
                income_fig = create_income_chart(income_data)
                expenses_fig = create_expenses_chart(expense_data)
                
                # Update layouts for mobile/desktop
                charts = [equity_fig, cashflow_fig, income_fig, expenses_fig]
                for chart in charts:
                    update_chart_layouts_for_mobile(chart, is_mobile)
                
                # Create responsive chart components
                equity_chart = create_responsive_chart(equity_fig, 'equity')
                cashflow_chart = create_responsive_chart(cashflow_fig, 'cashflow')
                income_chart = create_responsive_chart(income_fig, 'income')
                expenses_chart = create_responsive_chart(expenses_fig, 'expenses')
                
                # Create mobile-optimized table
                table = create_responsive_table(property_metrics, cashflow_metrics)
                
                return (
                    f"Time Period: {time_period if time_period != 'all' else 'All Time'}",  # context
                    f"${total_value:,.2f}",
                    f"${total_equity:,.2f}",
                    f"${total_equity_this_month:,.2f}",
                    f"${total_income:,.2f}",
                    f"${total_expenses:,.2f}",
                    html.Span(f"${total_net_cashflow:,.2f}",
                             style={'color': 'green' if total_net_cashflow >= 0 else 'red'}),
                    equity_chart,
                    cashflow_chart,
                    income_chart,
                    expenses_chart,
                    table,
                    "",
                    {'display': 'none'}
                )
                
            except Exception as e:
                logger.error(f"Error in update_metrics: {str(e)}")
                logger.error(traceback.format_exc())
                return create_empty_response(f"An error occurred: {str(e)}")
        
        logger.info("Portfolio dashboard created successfully")
        return dash_app
        
    except Exception as e:
        logger.error(f"Error creating portfolio dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        raise
