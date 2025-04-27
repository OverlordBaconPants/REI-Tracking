"""
Amortization dashboard for the REI-Tracker application.

This module provides a Dash-based interactive dashboard for visualizing
loan amortization schedules, including principal and interest breakdown,
equity gained, and remaining balance over time.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from flask_login import current_user
import traceback
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from src.services.property_financial_service import get_properties_for_user
from src.services.loan_service import LoanService
from src.models.loan import Loan
from src.utils.money import Money
from src.utils.logging_utils import get_logger

# Set up module-level logger
logger = get_logger(__name__)

# Mobile breakpoint constants
MOBILE_BREAKPOINT = 768
MOBILE_HEIGHT = '100vh'
DESKTOP_HEIGHT = 'calc(100vh - 150px)'

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
        if isinstance(value, Money):
            return float(value.amount)
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

def get_loan_data_for_property(property_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract loan data from property data.
    
    Args:
        property_data: Dictionary containing property information
        
    Returns:
        Optional[Dict]: Dictionary containing loan data or None if not found
    """
    try:
        # Check if property has loan_details
        if 'loan_details' in property_data and property_data['loan_details'].get('has_loans', False):
            loan_details = property_data['loan_details']
            loans = loan_details.get('loans', [])
            
            if not loans:
                logger.warning(f"No loans found in loan_details for property {property_data.get('address')}")
                return None
                
            # For now, just use the first loan (primary loan)
            loan = loans[0]
            
            return {
                'loan_amount': safe_float(loan.get('amount')),
                'interest_rate': safe_float(loan.get('interest_rate')) / 100,  # Convert to decimal
                'term_months': safe_float(loan.get('term_months')),
                'start_date': datetime.strptime(loan.get('start_date', date.today().isoformat()), '%Y-%m-%d').date(),
                'is_interest_only': loan.get('is_interest_only', False),
                'monthly_payment': safe_float(loan.get('monthly_payment')),
                'current_balance': safe_float(loan.get('current_balance')),
                'loan_id': loan.get('id')
            }
        
        # Fall back to legacy loan data
        required_fields = ['primary_loan_amount', 'primary_loan_rate', 'primary_loan_term', 'primary_loan_start_date']
        if all(field in property_data for field in required_fields):
            return {
                'loan_amount': safe_float(property_data.get('primary_loan_amount')),
                'interest_rate': safe_float(property_data.get('primary_loan_rate')) / 100,  # Convert to decimal
                'term_months': safe_float(property_data.get('primary_loan_term')),
                'start_date': datetime.strptime(property_data.get('primary_loan_start_date'), '%Y-%m-%d').date(),
                'is_interest_only': False,  # Default for legacy data
                'monthly_payment': None,  # Will be calculated
                'current_balance': None,  # Will be calculated
                'loan_id': None  # No ID for legacy data
            }
            
        logger.warning(f"No loan data found for property {property_data.get('address')}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting loan data: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def generate_amortization_schedule(loan_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Generate an amortization schedule for a loan.
    
    Args:
        loan_data: Dictionary containing loan parameters
        
    Returns:
        pd.DataFrame: DataFrame containing the amortization schedule
    """
    try:
        loan_amount = loan_data['loan_amount']
        interest_rate = loan_data['interest_rate']
        term_months = loan_data['term_months']
        start_date = loan_data['start_date']
        is_interest_only = loan_data.get('is_interest_only', False)
        
        logger.info(f"Generating amortization schedule: amount=${loan_amount:,.2f}, "
                   f"rate={interest_rate:.4f}, term={term_months} months")
        
        # If we have a loan_id, use the loan service to generate the schedule
        if loan_data.get('loan_id'):
            loan_service = LoanService()
            loan = loan_service.get_loan_by_id(loan_data['loan_id'])
            
            if loan:
                schedule = loan.generate_amortization_schedule()
                df = pd.DataFrame(schedule)
                
                # Convert date strings to datetime
                df['date'] = pd.to_datetime(df['date'])
                
                return df
        
        # Otherwise, calculate the schedule manually
        monthly_rate = interest_rate / 12
        
        # For interest-only loans
        if is_interest_only:
            # Calculate interest-only payment
            payment = loan_amount * monthly_rate
            
            # Create schedule
            data = []
            balance = loan_amount
            cumulative_interest = 0
            cumulative_principal = 0
            
            for month in range(1, int(term_months) + 1):
                interest = balance * monthly_rate
                principal = 0  # No principal payment for interest-only until the end
                
                # Last payment includes the full principal
                if month == int(term_months):
                    principal = balance
                    payment = interest + principal
                
                cumulative_interest += interest
                cumulative_principal += principal
                balance = max(0, balance - principal)
                
                data.append({
                    'period': month,
                    'payment': payment,
                    'principal': principal,
                    'interest': interest,
                    'balance': balance,
                    'cumulative_interest': cumulative_interest,
                    'cumulative_principal': cumulative_principal
                })
                
            df = pd.DataFrame(data)
            
        else:
            # Calculate standard amortizing payment
            payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** term_months) / \
                    ((1 + monthly_rate) ** term_months - 1)
            
            # Create schedule
            data = []
            balance = loan_amount
            cumulative_interest = 0
            cumulative_principal = 0
            
            for month in range(1, int(term_months) + 1):
                interest = balance * monthly_rate
                principal = payment - interest
                
                # Handle final payment rounding issues
                if month == int(term_months):
                    principal = balance
                    payment = principal + interest
                
                balance = max(0, balance - principal)
                cumulative_interest += interest
                cumulative_principal += principal
                
                data.append({
                    'period': month,
                    'payment': payment,
                    'principal': principal,
                    'interest': interest,
                    'balance': balance,
                    'cumulative_interest': cumulative_interest,
                    'cumulative_principal': cumulative_principal
                })
                
            df = pd.DataFrame(data)
        
        # Add date column
        df['date'] = pd.date_range(
            start=start_date,
            periods=len(df),
            freq='M'
        )
        
        # Add formatted date string
        df['date_str'] = df['date'].dt.strftime('%Y-%m')
        
        return df
        
    except Exception as e:
        logger.error(f"Error generating amortization schedule: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def create_responsive_chart(figure, id_prefix):
    """Create a responsive chart container with mobile-friendly settings."""
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
    """Create a mobile-responsive metric card."""
    return dbc.Card([
        dbc.CardBody([
            html.H5(title, className="card-title text-center mb-2 text-sm-start"),
            html.H3(id=id, className=f"text-center {color_class} text-sm-start")
        ])
    ], className="mb-3 shadow-sm")

def update_chart_layouts_for_mobile(fig, is_mobile=True):
    """Update chart layouts for mobile devices."""
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
            font_size=14  # Larger touch targets for hover labels
        )
    }
    fig.update_layout(**mobile_layout)
    return fig

def create_empty_response(error_message: str, is_mobile: bool = True) -> tuple:
    """
    Create a response for when no data can be displayed.
    
    Args:
        error_message: Error message to display
        is_mobile: Whether the display is for mobile devices
        
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
        showarrow=False,
        font=dict(size=16)
    )
    
    empty_fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(l=20, r=20, t=20, b=20)  # Tighter margins for mobile
    )
    
    # Create empty responsive chart
    empty_chart = create_responsive_chart(empty_fig, 'empty')
    
    return (
        html.Div("No loan information available", className="text-center text-muted p-3"),  # loan info
        empty_chart,  # amortization chart
        [],  # table data
        [],  # table columns
        [],  # table styles
        error_message,  # error message
        {'display': 'block', 'color': 'red'}  # error style
    )

def create_amortization_dash(flask_app) -> dash.Dash:
    """
    Create the amortization dashboard application.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dash.Dash: Configured Dash application instance
    """
    try:
        logger.info("Creating amortization dashboard")
        
        # Initialize Dash app
        dash_app = dash.Dash(
            __name__,
            server=flask_app,
            routes_pathname_prefix='/dashboards/_dash/amortization/',
            requests_pathname_prefix='/dashboards/_dash/amortization/',
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        
        logger.debug("Dash app initialized successfully")

        # Mobile-first styling
        style_config = {
            'card_style': {
                'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)',
                'margin-bottom': '20px',
                'border-radius': '15px',
                'background-color': 'white'
            },
            'header_style': {
                'backgroundColor': 'navy',
                'color': 'white',
                'padding': '15px',
                'fontSize': '1.25rem',
                'fontWeight': 'bold',
                'borderTopLeftRadius': '15px',
                'borderTopRightRadius': '15px'
            },
            'table_header': {
                'backgroundColor': 'navy',
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'padding': '12px 8px',
                'fontSize': '0.9rem'
            },
            'table_cell': {
                'textAlign': 'center',
                'padding': '8px 4px',
                'fontSize': '0.85rem'
            }
        }

        # Define layout with responsive design
        dash_app.layout = dbc.Container([
            # Responsive viewport meta tag
            html.Meta(name="viewport", content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
            
            dcc.Store(id='session-store'),
            dcc.Store(id='viewport-size'),  # Store for tracking viewport size
            
            # Error display
            html.Div(id="error-display", className="alert alert-danger mt-3 d-none"),
            
            # Property selector card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Select Property", style=style_config['header_style']),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='property-selector',
                                placeholder='Select Property',
                                className='mb-3',
                                style={'width': '100%'}
                            )
                        ])
                    ], style=style_config['card_style'])
                ], xs=12, md=6, className='mb-4')
            ]),
            
            # Loan information card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Loan Overview", style=style_config['header_style']),
                        dbc.CardBody(id='loan-info')
                    ], style=style_config['card_style'])
                ], xs=12, className='mb-4')
            ]),
            
            # Graph card - full width on mobile
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Amortization Chart", style=style_config['header_style']),
                        dbc.CardBody([
                            html.Div(id='amortization-chart-container', className="chart-container")
                        ])
                    ], style=style_config['card_style'])
                ], xs=12, className='mb-4')
            ]),
            
            # Table card with horizontal scroll on mobile
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Amortization Schedule", style=style_config['header_style']),
                        dbc.CardBody([
                            html.Div([
                                dash_table.DataTable(
                                    id='amortization-table',
                                    style_header=style_config['table_header'],
                                    style_cell=style_config['table_cell'],
                                    style_table={'overflowX': 'auto'},
                                    page_size=12,
                                    page_action='native',
                                    css=[{
                                        'selector': '.dash-spreadsheet',
                                        'rule': 'width: 100%; overflow-x: auto;'
                                    }]
                                )
                            ], className='table-responsive')
                        ])
                    ], style=style_config['card_style'])
                ], xs=12)
            ])
        ], fluid=True, className='px-2 px-sm-3 py-3')

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
            
            # We can't access window.innerWidth server-side
            # Just return a default value for now
            width = 800  # Default to desktop size
            
            return {'width': width, 'is_mobile': width < MOBILE_BREAKPOINT}

        @dash_app.callback(
            Output('property-selector', 'options'),
            Input('property-selector', 'id')
        )
        def populate_property_dropdown(dropdown_id):
            """Populate the property dropdown with available properties."""
            try:
                with flask_app.app_context():
                    # Check if current_user is authenticated and has necessary attributes
                    if hasattr(current_user, 'id') and hasattr(current_user, 'name'):
                        properties = get_properties_for_user(current_user.id, current_user.name)
                    else:
                        logger.warning("User not authenticated or missing attributes")
                        return []
                
                if not properties:
                    return []
                
                options = [{
                    'label': prop['address'].split(',')[0].strip(),
                    'value': prop['address']
                } for prop in properties]
                
                return options
                
            except Exception as e:
                logger.error(f"Error populating property dropdown: {str(e)}")
                logger.error(f"Exception details: {traceback.format_exc()}")
                return []

        @dash_app.callback(
            [Output('loan-info', 'children'),
             Output('amortization-chart-container', 'children'),
             Output('amortization-table', 'data'),
             Output('amortization-table', 'columns'),
             Output('amortization-table', 'style_data_conditional'),
             Output('error-display', 'children'),
             Output('error-display', 'style')],
            [Input('property-selector', 'value'),
             Input('viewport-size', 'data')]
        )
        def update_amortization(selected_property, viewport):
            """Update all amortization components based on selected property."""
            try:
                # Get device type
                is_mobile = viewport.get('is_mobile', True) if viewport else True
                
                if not selected_property:
                    return create_empty_response("No property selected", is_mobile)

                with flask_app.app_context():
                    # Check if current_user is authenticated and has necessary attributes
                    if hasattr(current_user, 'id') and hasattr(current_user, 'name'):
                        properties = get_properties_for_user(current_user.id, current_user.name)
                    else:
                        logger.warning("User not authenticated or missing attributes")
                        return create_empty_response("User authentication required", is_mobile)
                
                property_data = next((p for p in properties if p['address'] == selected_property), None)
                
                if not property_data:
                    return create_empty_response("Property not found", is_mobile)

                # Get loan data
                loan_data = get_loan_data_for_property(property_data)
                if not loan_data:
                    return create_empty_response("No loan information found for this property", is_mobile)

                # Generate amortization schedule
                df = generate_amortization_schedule(loan_data)
                
                # Calculate current position in loan
                today = date.today()
                months_into_loan = max(0, relativedelta(today, loan_data['start_date']).months +
                                    relativedelta(today, loan_data['start_date']).years * 12)

                # Create mobile-optimized components
                loan_info = create_loan_info(df, months_into_loan, loan_data, is_mobile)
                figure = create_amortization_figure(df, today, is_mobile)
                table_data, columns, styles = create_amortization_table(df, months_into_loan, is_mobile)

                return (
                    loan_info, 
                    create_responsive_chart(figure, 'amortization'), 
                    table_data, 
                    columns, 
                    styles, 
                    "", 
                    {'display': 'none'}
                )

            except Exception as e:
                logger.error(f"Error in update_amortization: {str(e)}")
                logger.error(traceback.format_exc())
                return create_empty_response(f"An error occurred: {str(e)}", is_mobile)

        def create_loan_info(df, months_into_loan, loan_data, is_mobile):
            """Create mobile-optimized loan information display."""
            try:
                # Get current month's data
                current_month = df.iloc[months_into_loan - 1] if months_into_loan > 0 and months_into_loan <= len(df) else None
                
                # Calculate equity gained
                equity_gained = df.iloc[:months_into_loan]['principal'].sum() if months_into_loan > 0 else 0
                
                # Calculate remaining balance
                remaining_balance = loan_data['loan_amount'] - equity_gained
                
                # Calculate percentage of loan term completed
                percent_complete = (months_into_loan / loan_data['term_months']) * 100
                
                # Create responsive layout
                if is_mobile:
                    return dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.P("Current Loan Status", className='h5 mb-3'),
                                html.Div([
                                    html.P(f"Months into Loan: {months_into_loan} of {int(loan_data['term_months'])}", className='mb-2'),
                                    html.P(f"Percent Complete: {percent_complete:.1f}%", className='mb-2'),
                                    html.P(f"Monthly Payment: ${loan_data.get('monthly_payment') or (current_month['payment'] if current_month is not None else 0):,.2f}", className='mb-2'),
                                    html.P(f"Current Principal: ${current_month['principal'] if current_month is not None else 0:,.2f}", className='mb-2'),
                                    html.P(f"Current Interest: ${current_month['interest'] if current_month is not None else 0:,.2f}", className='mb-2'),
                                    html.P(f"Total Equity Gained: ${equity_gained:,.2f}", className='mb-2'),
                                    html.P(f"Remaining Balance: ${remaining_balance:,.2f}", className='mb-2')
                                ], className='small')
                            ], className='p-2')
                        ], xs=12)
                    ])
                else:
                    return dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.P("Loan Progress", className='h5 mb-3'),
                                html.Div([
                                    html.P(f"Months into Loan: {months_into_loan} of {int(loan_data['term_months'])}", className='mb-2'),
                                    html.P(f"Percent Complete: {percent_complete:.1f}%", className='mb-2')
                                ])
                            ])
                        ], xs=12, md=4),
                        dbc.Col([
                            html.Div([
                                html.P("Monthly Breakdown", className='h5 mb-3'),
                                html.Div([
                                    html.P(f"Monthly Payment: ${loan_data.get('monthly_payment') or (current_month['payment'] if current_month is not None else 0):,.2f}", className='mb-2'),
                                    html.P(f"Current Principal: ${current_month['principal'] if current_month is not None else 0:,.2f}", className='mb-2'),
                                    html.P(f"Current Interest: ${current_month['interest'] if current_month is not None else 0:,.2f}", className='mb-2')
                                ])
                            ])
                        ], xs=12, md=4),
                        dbc.Col([
                            html.Div([
                                html.P("Loan Balance", className='h5 mb-3'),
                                html.Div([
                                    html.P(f"Total Equity Gained: ${equity_gained:,.2f}", className='mb-2'),
                                    html.P(f"Remaining Balance: ${remaining_balance:,.2f}", className='mb-2')
                                ])
                            ])
                        ], xs=12, md=4)
                    ])
            except Exception as e:
                logger.error(f"Error creating loan info: {str(e)}")
                return html.Div("Error loading loan information", className="text-danger")

        def create_amortization_figure(df, today, is_mobile):
            """Create mobile-optimized amortization chart."""
            try:
                # For mobile, reduce the number of data points to improve performance
                if is_mobile:
                    # Sample every 6 months for mobile
                    df_filtered = df[df.index % 6 == 0].copy()
                else:
                    # Sample every 3 months for desktop
                    df_filtered = df[df.index % 3 == 0].copy()
                
                # Create the graph
                fig = go.Figure()
                
                # Add traces with thicker lines for mobile visibility
                fig.add_trace(go.Scatter(
                    x=df_filtered['date'],
                    y=df_filtered['balance'],
                    name='Balance',
                    line=dict(color='navy', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_filtered['date'],
                    y=df_filtered['cumulative_interest'],
                    name='Interest',
                    line=dict(color='red', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_filtered['date'],
                    y=df_filtered['cumulative_principal'],
                    name='Principal',
                    line=dict(color='green', width=3)
                ))
                
                # Add today's line
                fig.add_shape(
                    type="line",
                    x0=today,
                    x1=today,
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(color="black", width=2, dash="dash")
                )
                
                # Add annotation for today
                fig.add_annotation(
                    x=today,
                    y=1,
                    yref="paper",
                    text="Today",
                    showarrow=False,
                    font=dict(size=12),
                    bgcolor="rgba(255, 255, 255, 0.7)",
                    bordercolor="black",
                    borderwidth=1
                )
                
                # Mobile-optimized layout
                if is_mobile:
                    fig.update_layout(
                        title=None,
                        xaxis_title=None,
                        yaxis_title='Amount ($)',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="left",
                            x=0
                        ),
                        margin=dict(l=40, r=20, t=60, b=80),
                        height=350
                    )
                else:
                    fig.update_layout(
                        title=None,
                        xaxis_title="Date",
                        yaxis_title='Amount ($)',
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=1,
                            xanchor="right",
                            x=1
                        ),
                        margin=dict(l=50, r=30, t=50, b=50),
                        height=450
                    )
                
                # Format y-axis as currency
                fig.update_yaxes(tickprefix='$', tickformat=',')
                
                # Format x-axis dates
                fig.update_xaxes(
                    tickformat='%b %Y',
                    tickangle=-45 if not is_mobile else -30,
                    nticks=10 if not is_mobile else 5
                )
                
                return fig
                
            except Exception as e:
                logger.error(f"Error creating amortization figure: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="Error creating chart",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color='red')
                )
                return empty_fig

        def create_amortization_table(df, months_into_loan, is_mobile):
            """Create mobile-optimized table components with month display."""
            try:
                # Format numeric columns for mobile display
                df = df.copy()
                for col in ['payment', 'principal', 'interest', 'balance', 
                        'cumulative_interest', 'cumulative_principal']:
                    df[col] = df[col].apply(lambda x: f"${x:,.2f}")

                # Format the date as month and year
                df['month_display'] = df['date'].dt.strftime('%b %Y')

                # Mobile-optimized columns
                if is_mobile:
                    columns = [
                        {"name": "Month", "id": "month_display", "width": "100px"},
                        {"name": "Payment", "id": "payment", "width": "90px"},
                        {"name": "Principal", "id": "principal", "width": "90px"},
                        {"name": "Interest", "id": "interest", "width": "90px"},
                        {"name": "Balance", "id": "balance", "width": "100px"}
                    ]
                else:
                    columns = [
                        {"name": "Month", "id": "month_display", "width": "100px"},
                        {"name": "Payment", "id": "payment", "width": "90px"},
                        {"name": "Principal", "id": "principal", "width": "90px"},
                        {"name": "Interest", "id": "interest", "width": "90px"},
                        {"name": "Balance", "id": "balance", "width": "100px"},
                        {"name": "Cumulative Principal", "id": "cumulative_principal", "width": "120px"},
                        {"name": "Cumulative Interest", "id": "cumulative_interest", "width": "120px"}
                    ]
                
                # Mobile-optimized conditional styling
                styles = [
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    },
                    {
                        'if': {'filter_query': f'{{period}} = {months_into_loan}'},
                        'backgroundColor': 'rgba(255, 255, 0, 0.3)',
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'column_type': 'numeric'},
                        'textAlign': 'right'
                    }
                ]
                
                return df.to_dict('records'), columns, styles
                
            except Exception as e:
                logger.error(f"Error creating table: {str(e)}")
                return [], [], []


        return dash_app
    
    except Exception as e:
        logger.error(f"Error creating amortization dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        raise
