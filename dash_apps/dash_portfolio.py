import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from flask_login import current_user
from services.transaction_service import get_properties_for_user
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import plotly.graph_objs as go
import plotly.express as px
from decimal import Decimal
import logging
import traceback
from typing import Dict, List, Optional, Tuple, Union
import numpy as np

# Set up module-level logger
logger = logging.getLogger(__name__)

def safe_float(value: Union[str, int, float, None], default: float = 0.0) -> float:
    """
    Safely convert a value to float, handling various input types and formats.
    
    Args:
        value: The value to convert (can be string, int, float, or None)
        default: Default value to return if conversion fails
        
    Returns:
        float: Converted value or default
    """
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols, commas, and spaces
            cleaned = value.replace('$', '').replace(',', '').replace(' ', '').strip()
            return float(cleaned) if cleaned else default
        return default
    except (ValueError, TypeError) as e:
        logger.warning(f"Error converting value to float: {value}, using default {default}. Error: {str(e)}")
        return default

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
        loan_fields = ['loan_amount', 'primary_loan_rate', 'primary_loan_term', 
                      'loan_start_date', 'purchase_price']
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
            
        # Get and validate loan parameters
        loan_amount = safe_float(property_data.get('loan_amount'))
        interest_rate = safe_float(property_data.get('primary_loan_rate')) / 100
        loan_term_months = safe_float(property_data.get('primary_loan_term'))
        purchase_price = safe_float(property_data.get('purchase_price'))
        
        try:
            loan_start_date = datetime.strptime(
                property_data.get('loan_start_date', date.today().strftime('%Y-%m-%d')), 
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
            'equity_share': equity_share * 100  # Store as percentage
        }
        
    except Exception as e:
        logger.error(f"Error calculating loan metrics for property {property_data.get('address')}: {str(e)}")
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
            loan_amount = safe_float(property_data.get('loan_amount'))
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
            seller_amount = safe_float(property_data.get('seller_financing_amount'))
            seller_rate = safe_float(property_data.get('seller_financing_rate')) / 100
            seller_term = safe_float(property_data.get('seller_financing_term'))
            
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
    
def generate_color_scale(n: int) -> List[str]:
    """
    Generate a color scale from navy to light cyan with n steps.
    
    Args:
        n: Number of colors needed
        
    Returns:
        List of hex color codes
    """
    if n <= 0:
        return []
    if n == 1:
        return ['#000080']  # Navy blue

    # Convert hex to RGB
    start_color = (0, 0, 128)      # RGB for #000080 (navy)
    end_color = (224, 255, 255)    # RGB for #E0FFFF (light cyan)
    
    colors = []
    for i in range(n):
        # Calculate the color at this step
        r = int(start_color[0] + (end_color[0] - start_color[0]) * (i / (n - 1)))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * (i / (n - 1)))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * (i / (n - 1)))
        
        # Convert RGB back to hex
        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        colors.append(hex_color)
    
    return colors

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
        
        # Define layout components
        def create_metric_card(title: str, id: str, color_class: str) -> dbc.Card:
            """Create a metric display card with consistent styling."""
            return dbc.Card([
                dbc.CardBody([
                    html.H5(title, className="card-title text-center mb-3"),
                    html.H3(id=id, className=f"text-center {color_class}")
                ])
            ], className="mb-4")

        # Define layout
        dash_app.layout = dbc.Container([
            dcc.Store(id='session-store'),
            
            html.Div([
                # Error display div for showing any errors
                html.Div(id="error-display", className="alert alert-danger", style={'display': 'none'}),
                
                # Header with user context
                dbc.Row([
                    dbc.Col([
                        html.P(id="user-context", className="text-muted")
                    ], width=12)
                ], className="mb-4"),
                
                # Summary Cards Row 1
                dbc.Row([
                    dbc.Col(create_metric_card(
                        "Portfolio Value", "total-portfolio-value", "text-primary"), width=4),
                    dbc.Col(create_metric_card(
                        "Total Equity", "total-equity", "text-success"), width=4),
                    dbc.Col(create_metric_card(
                        "Monthly Equity Gain", "equity-gained-month", "text-info"), width=4),
                ], className="mb-4"),
                
                # Summary Cards Row 2
                dbc.Row([
                    dbc.Col(create_metric_card(
                        "Gross Monthly Income", "total-monthly-income", "text-success"), width=4),
                    dbc.Col(create_metric_card(
                        "Monthly Expenses", "total-monthly-expenses", "text-danger"), width=4),
                    dbc.Col(create_metric_card(
                        "Net Monthly Cash Flow", "total-net-cashflow", "text-primary"), width=4),
                ], className="mb-4"),
                
                # Charts Row 1
                dbc.Row([
                    dbc.Col([
                        html.H4("Equity Distribution", className="text-center mb-4"),
                        dcc.Graph(id='equity-pie-chart')
                    ], width=6),
                    dbc.Col([
                        html.H4("Cash Flow by Property", className="text-center mb-4"),
                        dcc.Graph(id='cashflow-bar-chart')
                    ], width=6),
                ], className="mb-4"),
                
                # Charts Row 2
                dbc.Row([
                    dbc.Col([
                        html.H4("Monthly Income by Property", className="text-center mb-4"),
                        dcc.Graph(id='income-pie-chart')
                    ], width=6),
                    dbc.Col([
                        html.H4("Monthly Expenses Breakdown", className="text-center mb-4"),
                        dcc.Graph(id='expenses-pie-chart')
                    ], width=6),
                ], className="mb-4"),
                
                # Property Details Table
                dbc.Row([
                    dbc.Col([
                        html.H4("Property Details", className="text-center mb-4"),
                        html.Div(id='property-table')
                    ], width=12)
                ]),
            ])
        ], fluid=True)

        logger.debug("Dashboard layout created successfully")

        @dash_app.callback(
            [Output('user-context', 'children'),
             Output('total-portfolio-value', 'children'),
             Output('total-equity', 'children'),
             Output('equity-gained-month', 'children'),
             Output('total-monthly-income', 'children'),
             Output('total-monthly-expenses', 'children'),
             Output('total-net-cashflow', 'children'),
             Output('equity-pie-chart', 'figure'),
             Output('cashflow-bar-chart', 'figure'),
             Output('income-pie-chart', 'figure'),
             Output('expenses-pie-chart', 'figure'),
             Output('property-table', 'children'),
             Output('error-display', 'children'),
             Output('error-display', 'style')],
            [Input('session-store', 'data')]
        )
        def update_metrics(data):
            """Update all dashboard metrics and visualizations."""
            try:
                logger.info(f"Updating metrics for user: {current_user.name}")
                
                # Get property data
                with flask_app.app_context():
                    properties = get_properties_for_user(current_user.id, current_user.name)
                
                if not properties:
                    logger.warning(f"No properties found for user: {current_user.name}")
                    return create_empty_response("No properties found in your portfolio.")
                
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
                logger.debug(f"Number of properties: Equity={len(equity_data)}, "
                            f"Income={len(income_data)}, Expenses={len(expense_data)}")
                
                # Create color scales for each chart
                equity_colors = generate_color_scale(len(equity_data))
                income_colors = generate_color_scale(len(income_data))
                expense_colors = generate_color_scale(len(expense_data))
                cashflow_colors = generate_color_scale(len(sorted_cashflow))

                # Create charts with sorted data
                logger.debug("Creating charts")

                # Log data going into charts for debugging
                logger.debug("Creating charts with data:")
                logger.debug(f"Equity data: {equity_data}")
                logger.debug(f"Income data: {income_data}")
                logger.debug(f"Expense data: {expense_data}")

                # Create equity distribution chart
                try:
                    equity_fig = px.pie(
                        values=[float(item['value']) for item in equity_data],
                        names=[str(item['name']) for item in equity_data],
                        title='Equity Distribution',
                        hole=0.5,
                        color_discrete_sequence=equity_colors[:len(equity_data)]
                    )
                    logger.debug("Created equity chart successfully")
                except Exception as e:
                    logger.error(f"Error creating equity chart: {str(e)}")
                    raise

                # Create equity distribution chart
                try:
                    equity_fig = px.pie(
                        values=[float(item['value']) for item in equity_data],
                        names=[str(item['name']) for item in equity_data],
                        hole=0.4,
                        color_discrete_sequence=equity_colors
                    )
                    logger.debug("Created equity chart successfully")
                except Exception as e:
                    logger.error(f"Error creating equity chart: {str(e)}")
                    raise

                # Create cash flow bar chart
                try:
                    cashflow_fig = px.bar(
                        x=[str(m['address']).split(',')[0] + f" ({m['equity_share']}%)" 
                            for m in sorted_cashflow],
                        y=[float(m['net_cashflow']) for m in sorted_cashflow],
                        title='Cash Flow by Property',
                        color=[float(m['net_cashflow']) for m in sorted_cashflow],
                        color_continuous_scale=[[0, cashflow_colors[-1]], [1, cashflow_colors[0]]]
                    )
                    # Remove colorbar
                    cashflow_fig.update_coloraxes(showscale=False)
                    logger.debug("Created cashflow chart successfully")
                except Exception as e:
                    logger.error(f"Error creating cashflow chart: {str(e)}")
                    raise

                # Create income breakdown chart
                try:
                    income_fig = px.pie(
                        values=[float(item['value']) for item in income_data],
                        names=[str(item['name']) for item in income_data],
                        hole=0.4,
                        color_discrete_sequence=income_colors
                    )
                    logger.debug("Created income chart successfully")
                except Exception as e:
                    logger.error(f"Error creating income chart: {str(e)}")
                    raise

                # Create expenses breakdown chart
                try:
                    expenses_fig = px.pie(
                        values=[float(item['value']) for item in expense_data],
                        names=[str(item['name']) for item in expense_data],
                        hole=0.4,
                        color_discrete_sequence=expense_colors
                    )
                    logger.debug("Created expenses chart successfully")
                except Exception as e:
                    logger.error(f"Error creating expenses chart: {str(e)}")
                    raise

                # Update all pie charts
                for fig in [equity_fig, income_fig, expenses_fig]:
                    try:
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent',
                            hovertemplate="<b>%{label}</b><br>$%{value:,.2f}<br>%{percent:.1%}<extra></extra>"
                        )
                        fig.update_layout(
                            margin=dict(r=200, t=50, b=50, l=50),
                            showlegend=True,
                            legend=dict(
                                yanchor="middle",
                                y=0.5,
                                xanchor="left",
                                x=1.0,
                                orientation='v',
                                title=None,
                                font=dict(size=12)
                            ),
                            height=400
                        )
                    except Exception as e:
                        logger.error(f"Error updating pie chart layout: {str(e)}")
                        raise

                # Update bar chart layout
                try:
                    cashflow_fig.update_layout(
                        showlegend=False,
                        xaxis_title="Property",
                        yaxis_title="Monthly Cash Flow ($)",
                        yaxis_tickformat="$,.2f",
                        margin=dict(l=50, r=50, t=50, b=100),
                        height=400,
                        xaxis=dict(
                            tickangle=-45,
                            automargin=True
                        )
                    )
                    cashflow_fig.update_traces(
                        hovertemplate="<b>%{x}</b><br>Cash Flow: $%{y:,.2f}<extra></extra>"
                    )
                except Exception as e:
                    logger.error(f"Error updating bar chart layout: {str(e)}")
                    raise

                logger.info("Successfully created all charts")
                
                try:
                    # Create property table with bootstrap classes
                    table = dbc.Table(
                        [
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Property", style={'backgroundColor': '#000080'}, className="text-center text-white fw-bold"),
                                        html.Th("Share", style={'backgroundColor': '#000080'}, className="text-center text-white fw-bold"),
                                        html.Th("Monthly Income", style={'backgroundColor': '#000080'}, className="text-center text-white fw-bold"),
                                        html.Th("Monthly Expenses", style={'backgroundColor': '#000080'}, className="text-center text-white fw-bold"),
                                        html.Th("Net Cash Flow", style={'backgroundColor': '#000080'}, className="text-center text-white fw-bold"),
                                        html.Th("Total Equity", style={'backgroundColor': '#000080'}, className="text-center text-white fw-bold"),
                                        html.Th("Monthly Equity Gain", style={'backgroundColor': '#000080'}, className="text-center text-white fw-bold")
                                    ],
                                )
                            ),
                            html.Tbody([
                                html.Tr([
                                    html.Td(cm['address'].split(',')[0]),
                                    html.Td(f"{cm['equity_share']}%"),
                                    html.Td(f"${cm['monthly_income']:,.2f}"),
                                    html.Td(f"${(cm['monthly_expenses'] + cm['mortgage_payment'] + cm['seller_payment']):,.2f}"),
                                    html.Td(
                                        html.Span(
                                            f"${cm['net_cashflow']:,.2f}",
                                            style={'color': 'green' if cm['net_cashflow'] >= 0 else 'red'}
                                        )
                                    ),
                                    html.Td(f"${pm['total_equity']:,.2f}"),
                                    html.Td(f"${pm['equity_this_month']:,.2f}")
                                ]) for cm, pm in zip(cashflow_metrics, property_metrics)
                            ])
                        ],
                        bordered=True,
                        hover=True,
                        striped=True,  # Add this parameter
                        responsive=True,
                        className="align-middle"
                    )
                    
                except Exception as e:
                    logger.error(f"Error creating property table: {str(e)}")
                    logger.error(traceback.format_exc())
                    return create_empty_response("Error creating property table.")
                
                logger.info("Successfully updated all metrics and visualizations")
                
                # Return all components
                return (
                    "",  # context
                    f"${total_value:,.2f}",                    # portfolio value
                    f"${total_equity:,.2f}",                   # total equity
                    f"${total_equity_this_month:,.2f}",        # equity gained
                    f"${total_income:,.2f}",                   # monthly income
                    f"${total_expenses:,.2f}",                 # monthly expenses
                    html.Span(
                        f"${total_net_cashflow:,.2f}",
                        style={'color': 'green' if total_net_cashflow >= 0 else 'red'}
                    ),                                         # net cashflow
                    equity_fig,                                # equity chart
                    cashflow_fig,                              # cashflow chart
                    income_fig,                                # income chart
                    expenses_fig,                              # expenses chart
                    table,                                     # property table
                    "",                                        # error message
                    {'display': 'none'}                        # error style
                )
                
            except Exception as e:
                logger.error(f"Error in update_metrics: {str(e)}")
                logger.error(traceback.format_exc())
                return create_empty_response(f"An error occurred: {str(e)}")

        def create_empty_response(error_message: str) -> tuple:
            """
            Create a response for when no data can be displayed.
            
            Args:
                error_message: Error message to display
                
            Returns:
                tuple: Empty values for all dashboard components plus error message
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
            
            return (
                "",  # context
                "$0.00",                                    # portfolio value
                "$0.00",                                    # total equity
                "$0.00",                                    # equity gained
                "$0.00",                                    # monthly income
                "$0.00",                                    # monthly expenses
                html.Span("$0.00"),                         # net cashflow
                empty_fig,                                  # equity chart
                empty_fig,                                  # cashflow chart
                empty_fig,                                  # income chart
                empty_fig,                                  # expenses chart
                "No data to display",                       # table
                error_message,                              # error message
                {'display': 'block', 'color': 'red'}        # error style
            )
        
        logger.info("Portfolio dashboard created successfully")
        return dash_app
        
    except Exception as e:
        logger.error(f"Error creating portfolio dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        raise