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

def calculate_loan_metrics(property_data):
    """Calculate loan and equity metrics for a property."""
    try:
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
            interest_payment = balance * (interest_rate / 12)
            principal_payment = monthly_payment - interest_payment
            balance = max(0, balance - principal_payment)
            
            if month == months_into_loan - 1:  # Last month
                current_month_principal = principal_payment
            total_principal_paid += principal_payment
        
        # Calculate metrics
        property_metrics = {
            'address': property_data.get('address', 'Unknown'),
            'purchase_price': purchase_price,
            'loan_amount': loan_amount,
            'current_balance': balance,
            'monthly_payment': monthly_payment,
            'equity_from_principal': total_principal_paid,
            'equity_this_month': current_month_principal,
            'total_equity': purchase_price - balance,  # Simple equity calculation
            'months_paid': months_into_loan
        }
        
        return property_metrics
        
    except Exception as e:
        print(f"Error calculating metrics for property: {str(e)}")
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
        html.Div([
            # Summary Cards Row - Now with 4 cards
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Portfolio Value", className="card-title text-center"),
                            html.H2(id="total-portfolio-value", className="text-center text-primary")
                        ])
                    ], className="mb-4")
                , width=3),  # Changed from width=4 to width=3
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Monthly Payments", className="card-title text-center"),
                            html.H2(id="total-monthly-payments", className="text-center text-danger")
                        ])
                    ], className="mb-4")
                , width=3),  # Changed from width=4 to width=3
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Equity", className="card-title text-center"),
                            html.H2(id="total-equity", className="text-center text-success")
                        ])
                    ], className="mb-4")
                , width=3),  # Changed from width=4 to width=3
                dbc.Col(
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Equity Gained This Month", className="card-title text-center"),
                            html.H2(id="equity-gained-month", className="text-center text-info")
                        ])
                    ], className="mb-4")
                , width=3),  # New card with width=3
            ], className="mb-4"),
            
            # Rest of the layout remains the same...
            dbc.Row([
                dbc.Col([
                    html.H4("Equity Distribution", className="text-center mb-4"),
                    dcc.Graph(id='equity-pie-chart')
                ], width=6),
                dbc.Col([
                    html.H4("Monthly Payments by Property", className="text-center mb-4"),
                    dcc.Graph(id='payments-bar-chart')
                ], width=6),
            ], className="mb-4"),
            
            # Property Details Table
            dbc.Row([
                dbc.Col([
                    html.H4("Property Details", className="text-center mb-4"),
                    html.Div(id='property-table')
                ], width=12)
            ]),
            
            dcc.Interval(
                id='interval-component',
                interval=60*1000,  # Update every minute
                n_intervals=0
            )
        ])
    ], fluid=True)
    
    @dash_app.callback(
        [Output('total-portfolio-value', 'children'),
         Output('total-monthly-payments', 'children'),
         Output('total-equity', 'children'),
         Output('equity-gained-month', 'children'),  # Added new output
         Output('equity-pie-chart', 'figure'),
         Output('payments-bar-chart', 'figure'),
         Output('property-table', 'children')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_metrics(n):
        # Get property data
        with flask_app.app_context():
            properties = get_properties_for_user(current_user.id, current_user.name)
        
        # Calculate metrics for each property
        property_metrics = []
        total_value = 0
        total_payments = 0
        total_equity = 0
        total_equity_this_month = 0
        
        for prop in properties:
            metrics = calculate_loan_metrics(prop)
            if metrics:
                property_metrics.append(metrics)
                total_value += metrics['purchase_price']
                total_payments += metrics['monthly_payment']
                total_equity += metrics['total_equity']
                total_equity_this_month += metrics['equity_this_month']
        
        # Create equity pie chart
        equity_fig = px.pie(
            values=[m['total_equity'] for m in property_metrics],
            names=[m['address'].split(',')[0] for m in property_metrics],
            title='Equity Distribution',
            hole=0.3
        )
        
        # Create payments bar chart
        payments_fig = px.bar(
            x=[m['address'].split(',')[0] for m in property_metrics],
            y=[m['monthly_payment'] for m in property_metrics],
            title='Monthly Payments by Property'
        )
        
        # Create property table
        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Property"),
                    html.Th("Purchase Price"),
                    html.Th("Current Balance"),
                    html.Th("Monthly Payment"),
                    html.Th("Total Equity"),
                    html.Th("Equity This Month")
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(m['address'].split(',')[0]),
                    html.Td(f"${m['purchase_price']:,.2f}"),
                    html.Td(f"${m['current_balance']:,.2f}"),
                    html.Td(f"${m['monthly_payment']:,.2f}"),
                    html.Td(f"${m['total_equity']:,.2f}"),
                    html.Td(f"${m['equity_this_month']:,.2f}")
                ]) for m in property_metrics
            ])
        ], bordered=True, hover=True, responsive=True)
        
        return (
            f"${total_value:,.2f}",
            f"${total_payments:,.2f}",
            f"${total_equity:,.2f}",
            f"${total_equity_this_month:,.2f}",  # Added new return value
            equity_fig,
            payments_fig,
            table
        )
    
    return dash_app