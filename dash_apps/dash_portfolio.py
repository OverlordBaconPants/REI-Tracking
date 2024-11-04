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

def calculate_user_equity_share(property_data, username):
    """Calculate the user's equity share percentage for a property."""
    for partner in property_data.get('partners', []):
        if partner['name'] == username:
            return partner['equity_share'] / 100.0
    return 0.0

def calculate_loan_metrics(property_data, username):
    """Calculate loan and equity metrics for a property, adjusted for user's equity share."""
    try:
        # Get user's equity share
        equity_share = calculate_user_equity_share(property_data, username)
        if equity_share == 0:
            return None
            
        loan_amount = float(property_data.get('loan_amount', 0))
        interest_rate = float(property_data.get('primary_loan_rate', 0)) / 100
        loan_term_months = float(property_data.get('primary_loan_term', 360))
        loan_start_date = datetime.strptime(property_data.get('loan_start_date', date.today().strftime('%Y-%m-%d')), '%Y-%m-%d').date()
        purchase_price = float(property_data.get('purchase_price', 0))
        
        # Calculate monthly payment
        if interest_rate > 0 and loan_term_months > 0:
            monthly_rate = interest_rate / 12
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** loan_term_months) / ((1 + monthly_rate) ** loan_term_months - 1)
        else:
            monthly_payment = loan_amount / loan_term_months if loan_term_months > 0 else 0
        
        # Calculate months into loan
        today = date.today()
        months_into_loan = relativedelta(today, loan_start_date).months + relativedelta(today, loan_start_date).years * 12
        
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
        
        # Adjust metrics based on user's equity share
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
        print(f"Error calculating metrics for property: {str(e)}")
        return None

def calculate_monthly_cashflow(property_data, username):
    """Calculate monthly cash flow metrics for a property, adjusted for user's equity share."""
    try:
        equity_share = calculate_user_equity_share(property_data, username)
        if equity_share == 0:
            return None
            
        # Calculate total monthly income
        monthly_income = (
            float(property_data.get('monthly_income', {}).get('rental_income', 0)) +
            float(property_data.get('monthly_income', {}).get('parking_income', 0)) +
            float(property_data.get('monthly_income', {}).get('laundry_income', 0)) +
            float(property_data.get('monthly_income', {}).get('other_income', 0))
        )

        # Calculate total monthly expenses
        monthly_expenses = property_data.get('monthly_expenses', {})
        utilities = monthly_expenses.get('utilities', {})
        total_utilities = sum(float(val) for val in utilities.values())
        
        total_expenses = (
            float(monthly_expenses.get('property_tax', 0)) +
            float(monthly_expenses.get('insurance', 0)) +
            float(monthly_expenses.get('repairs', 0)) +
            float(monthly_expenses.get('capex', 0)) +
            float(monthly_expenses.get('property_management', 0)) +
            float(monthly_expenses.get('hoa_fees', 0)) +
            float(monthly_expenses.get('other_expenses', 0)) +
            total_utilities
        )

        # Calculate mortgage payment
        loan_amount = float(property_data.get('loan_amount', 0))
        interest_rate = float(property_data.get('primary_loan_rate', 0)) / 100
        loan_term_months = float(property_data.get('primary_loan_term', 360))
        
        if interest_rate > 0 and loan_term_months > 0:
            monthly_rate = interest_rate / 12
            mortgage_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** loan_term_months) / ((1 + monthly_rate) ** loan_term_months - 1)
        else:
            mortgage_payment = loan_amount / loan_term_months if loan_term_months > 0 else 0

        # Calculate seller financing payment if applicable
        seller_amount = float(property_data.get('seller_financing_amount', 0))
        seller_rate = float(property_data.get('seller_financing_rate', 0)) / 100
        seller_term = float(property_data.get('seller_financing_term', 0))
        
        if seller_rate > 0 and seller_term > 0:
            monthly_seller_rate = seller_rate / 12
            seller_payment = seller_amount * (monthly_seller_rate * (1 + monthly_seller_rate) ** seller_term) / ((1 + monthly_seller_rate) ** seller_term - 1)
        else:
            seller_payment = seller_amount / seller_term if seller_term > 0 else 0

        # Calculate net cash flow
        net_cashflow = monthly_income - total_expenses - mortgage_payment - seller_payment

        # Create expense breakdown
        expense_breakdown = {
            'Property Tax': float(monthly_expenses.get('property_tax', 0)),
            'Insurance': float(monthly_expenses.get('insurance', 0)),
            'Repairs': float(monthly_expenses.get('repairs', 0)),
            'CapEx': float(monthly_expenses.get('capex', 0)),
            'Property Management': float(monthly_expenses.get('property_management', 0)),
            'HOA Fees': float(monthly_expenses.get('hoa_fees', 0)),
            'Utilities': total_utilities,
            'Other': float(monthly_expenses.get('other_expenses', 0)),
            'Mortgage': mortgage_payment,
            'Seller Financing': seller_payment
        }

        # Filter out zero values from expense breakdown
        expense_breakdown = {k: v for k, v in expense_breakdown.items() if v > 0}

        return {
            'address': property_data.get('address', 'Unknown'),
            'monthly_income': monthly_income * equity_share,
            'monthly_expenses': total_expenses * equity_share,
            'mortgage_payment': mortgage_payment * equity_share,
            'seller_payment': seller_payment * equity_share,
            'net_cashflow': net_cashflow * equity_share,
            'expense_breakdown': {k: v * equity_share for k, v in expense_breakdown.items()},
            'equity_share': equity_share * 100
        }
            
    except Exception as e:
        print(f"Error calculating cash flow metrics for property: {str(e)}")
        return None

def create_portfolio_dash(flask_app):
    """Create the portfolio dashboard."""
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        routes_pathname_prefix='/dashboards/_dash/portfolio/',
        requests_pathname_prefix='/dashboards/_dash/portfolio/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    
    # Define layout
    dash_app.layout = dbc.Container([
        dcc.Store(id='session-store'),
        
        html.Div([
            # Header with user context
            dbc.Row([
                dbc.Col([
                    html.P(id="user-context", className="text-muted")
                ], width=12)
            ], className="mb-4"),
            
            # Summary Cards Row 1
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Portfolio Value", className="card-title text-center mb-3"),
                            html.H3(id="total-portfolio-value", className="text-center text-primary")
                        ])
                    ], className="mb-4")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Total Equity", className="card-title text-center mb-3"),
                            html.H3(id="total-equity", className="text-center text-success")
                        ])
                    ], className="mb-4")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Monthly Equity Gain", className="card-title text-center mb-3"),
                            html.H3(id="equity-gained-month", className="text-center text-info")
                        ])
                    ], className="mb-4")
                , width=4),
            ], className="mb-4"),
            
            # Summary Cards Row 2
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Gross Monthly Income", className="card-title text-center mb-3"),
                            html.H3(id="total-monthly-income", className="text-center text-success")
                        ])
                    ], className="mb-4")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Monthly Expenses", className="card-title text-center mb-3"),
                            html.H3(id="total-monthly-expenses", className="text-center text-danger")
                        ])
                    ], className="mb-4")
                , width=4),
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Net Monthly Cash Flow", className="card-title text-center mb-3"),
                            html.H3(id="total-net-cashflow", className="text-center text-primary")
                        ])
                    ], className="mb-4")
                , width=4),
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
                    html.H4("Monthly Expenses Breakdown", className="text-center mb-4"),
                    dcc.Graph(id='expenses-pie-chart')
                ], width=12),
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

    # Callback remains the same but remove 'Your' from the context
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
         Output('expenses-pie-chart', 'figure'),
         Output('property-table', 'children')],
        [Input('session-store', 'data')]
    )
    def update_metrics(data):
        try:
            # Get property data
            with flask_app.app_context():
                properties = get_properties_for_user(current_user.id, current_user.name)
            
            # Calculate metrics for each property
            property_metrics = []
            cashflow_metrics = []
            total_value = 0
            total_equity = 0
            total_equity_this_month = 0
            total_income = 0
            total_expenses = 0
            total_net_cashflow = 0
            combined_expenses = {}
            
            for prop in properties:
                metrics = calculate_loan_metrics(prop, current_user.name)
                cashflow = calculate_monthly_cashflow(prop, current_user.name)
                
                if metrics and cashflow:  # Only include properties where user has an equity share
                    property_metrics.append(metrics)
                    cashflow_metrics.append(cashflow)
                    
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
            
            # Create equity pie chart
            equity_fig = px.pie(
                values=[m['total_equity'] for m in property_metrics],
                names=[f"{m['address'].split(',')[0]} ({m['equity_share']}%)" for m in property_metrics],
                title='Equity Distribution',
                hole=0.3
            )
            
            # Create cash flow bar chart
            cashflow_fig = px.bar(
                x=[f"{m['address'].split(',')[0]} ({m['equity_share']}%)" for m in cashflow_metrics],
                y=[m['net_cashflow'] for m in cashflow_metrics],
                title='Cash Flow by Property',
                color_discrete_sequence=['green' if cf >= 0 else 'red' for cf in [m['net_cashflow'] for m in cashflow_metrics]]
            )
            cashflow_fig.update_layout(showlegend=False)
            
            # Create expenses pie chart
            expenses_fig = px.pie(
                values=list(combined_expenses.values()),
                names=list(combined_expenses.keys()),
                title='Monthly Expenses Breakdown',
                hole=0.3
            )
            
            # Create property table
            table = dbc.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Property"),
                        html.Th("Share"),
                        html.Th("Monthly Income"),
                        html.Th("Monthly Expenses"),
                        html.Th("Net Cash Flow"),
                        html.Th("Total Equity"),
                        html.Th("Monthly Equity Gain")
                    ])
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
            ], bordered=True, hover=True, responsive=True)
            
            return (
                f"Portfolio data for {current_user.name}",
                f"${total_value:,.2f}",
                f"${total_equity:,.2f}",
                f"${total_equity_this_month:,.2f}",
                f"${total_income:,.2f}",
                f"${total_expenses:,.2f}",
                html.Span(
                    f"${total_net_cashflow:,.2f}",
                    style={'color': 'green' if total_net_cashflow >= 0 else 'red'}
                ),
                equity_fig,
                cashflow_fig,
                expenses_fig,
                table
            )
            
        except Exception as e:
            print(f"Error in update_metrics: {str(e)}")
            raise
    
    return dash_app