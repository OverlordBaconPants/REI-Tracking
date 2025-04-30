import dash
import os
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from flask_login import current_user
from services.transaction_service import get_properties_for_user
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import traceback
import logging

# Set up module-level logger
logger = logging.getLogger(__name__)

def validate_loan_data(loan_amount, annual_rate, years):
    """Validate loan input parameters."""
    try:
        if not loan_amount or loan_amount <= 0:
            return False, "Loan amount must be greater than 0"
        if not annual_rate or annual_rate <= 0:
            return False, "Interest rate must be greater than 0"
        if not years or years <= 0:
            return False, "Loan term must be greater than 0"
        return True, ""
    except Exception as e:
        logger.error(f"Error validating loan data: {str(e)}")
        return False, f"Validation error: {str(e)}"

def amortize(principal, annual_rate, years):
    """Calculate amortization schedule with cumulative totals."""
    try:
        logger.info(f"Calculating amortization schedule: principal=${principal:,.2f}, rate={annual_rate:.4f}, years={years}")
        
        # Validate inputs
        is_valid, error_message = validate_loan_data(principal, annual_rate, years)
        if not is_valid:
            logger.error(f"Invalid loan data: {error_message}")
            raise ValueError(error_message)
        
        monthly_rate = annual_rate / 12
        num_payments = int(years * 12)
        payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
        
        balance = principal
        cumulative_interest = 0
        cumulative_principal = 0
        
        for month in range(1, num_payments + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest
            balance = max(0, balance - principal_paid)
            
            cumulative_interest += interest
            cumulative_principal += principal_paid
            
            if month % 12 == 0:
                logger.debug(f"Year {month//12} summary - Balance: ${balance:,.2f}")
            
            yield {
                'month': month,
                'payment': round(payment, 2),
                'principal': round(principal_paid, 2),
                'interest': round(interest, 2),
                'balance': round(balance, 2),
                'cumulative_interest': round(cumulative_interest, 2),
                'cumulative_principal': round(cumulative_principal, 2)
            }
            
    except Exception as e:
        logger.error(f"Error in amortization calculation: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def create_amortization_dash(flask_app):
    """Create and configure the mobile-first amortization dashboard."""
    try:
        logger.info("Initializing mobile-first amortization dashboard")
        
        template_path = os.path.join(str(flask_app.root_path), 'templates', 'dashboards', 'dash_amortization.html')
        dash_app = dash.Dash(
            __name__,
            server=flask_app,
            routes_pathname_prefix='/dashboards/_dash/amortization/',
            requests_pathname_prefix='/dashboards/_dash/amortization/',  
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            index_string=open(template_path).read()
        )

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

        # Layout definition with mobile-first approach
        dash_app.layout = dbc.Container([
            # Error display for better mobile visibility
            dbc.Row([
                dbc.Col([
                    html.Div(
                        id='error-display',
                        className='alert alert-danger mt-3',
                        style={'display': 'none', 'width': '100%'}
                    )
                ])
            ]),
            
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
                            dcc.Graph(
                                id='amortization-graph',
                                config={
                                    'displayModeBar': True,
                                    'responsive': True,
                                    'scrollZoom': True
                                },
                                style={'height': '50vh'}  # Responsive height
                            )
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
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 'odd'},
                                            'backgroundColor': 'rgb(248, 248, 248)'
                                        }
                                    ],
                                    # page_size=10,  # Show all rows on mobile
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
        ], fluid=True, className='p-3')

        @dash_app.callback(
            Output('property-selector', 'options'),
            Input('property-selector', 'id')
        )
        def populate_property_dropdown(dropdown_id):
            """Populate the property dropdown with available properties."""
            try:
                with flask_app.app_context():
                    properties = get_properties_for_user(current_user.id, current_user.name)
                
                if not properties:
                    return []
                
                options = [{
                    'label': prop['address'].split(',')[0].strip(),
                    'value': prop['address']
                } for prop in properties]
                
                return options
                
            except Exception as e:
                logger.error(f"Error populating property dropdown: {str(e)}")
                return []

        @dash_app.callback(
            [Output('loan-info', 'children'),
             Output('amortization-graph', 'figure'),
             Output('amortization-table', 'data'),
             Output('amortization-table', 'columns'),
             Output('amortization-table', 'style_data_conditional'),
             Output('error-display', 'children'),
             Output('error-display', 'style')],
            [Input('property-selector', 'value')]
        )
        def update_amortization(selected_property):
            """Update all amortization components based on selected property."""
            try:
                if not selected_property:
                    return create_empty_state()

                properties = get_properties_for_user(current_user.id, current_user.name)
                property_data = next((p for p in properties if p['address'] == selected_property), None)
                
                if not property_data:
                    return create_error_response("Property not found")

                # Validate and parse loan data
                required_fields = ['primary_loan_amount', 'primary_loan_rate', 'primary_loan_term', 'primary_loan_start_date']
                if not all(property_data.get(f) for f in required_fields):
                    return create_error_response("Missing required loan information")

                try:
                    loan_amount = float(property_data['primary_loan_amount'])
                    interest_rate = float(property_data['primary_loan_rate']) / 100
                    loan_term = float(property_data['primary_loan_term']) / 12
                    loan_start_date = datetime.strptime(property_data['primary_loan_start_date'], '%Y-%m-%d').date()
                except ValueError as e:
                    return create_error_response(f"Invalid loan data: {str(e)}")

                # Calculate amortization and prepare data
                schedule = list(amortize(loan_amount, interest_rate, loan_term))
                df = pd.DataFrame(schedule)
                
                # Create date column as datetime series
                df['date'] = pd.date_range(
                    start=loan_start_date,
                    periods=len(df),
                    freq='M'
                )
                
                # Format date strings
                df['date_str'] = df['date'].dt.strftime('%Y-%m')

                # Calculate current position in loan
                months_into_loan = max(0, relativedelta(date.today(), loan_start_date).months +
                                    relativedelta(date.today(), loan_start_date).years * 12)

                # Create mobile-optimized components
                loan_info = create_loan_info(df, months_into_loan)
                figure = create_mobile_figure(df, date.today())
                table_data, columns, styles = create_mobile_table(df, months_into_loan)

                return loan_info, figure, table_data, columns, styles, "", {'display': 'none'}

            except Exception as e:
                logger.error(f"Error in update_amortization: {str(e)}")
                return create_error_response(f"An error occurred: {str(e)}")

        def create_empty_state():
            """Create empty state display for mobile."""
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Select a property to view the amortization schedule",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16)
            )
            empty_fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                margin=dict(l=20, r=20, t=20, b=20)  # Tighter margins for mobile
            )
            
            return (
                html.Div("No property selected", className='text-center text-muted'),
                empty_fig,
                [],
                [],
                [],
                "",
                {'display': 'none'}
            )

        def create_loan_info(df, months_into_loan):
            """Create mobile-optimized loan information display."""
            try:
                last_month = df.iloc[months_into_loan - 1] if months_into_loan > 0 else pd.Series()
                equity_gained = df.iloc[:months_into_loan]['principal'].sum() if months_into_loan > 0 else 0
                
                return dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.P("Current Loan Status", className='h6 mb-3'),
                            html.Div([
                                html.P(f"Months into Loan: {months_into_loan}", className='mb-2'),
                                html.P(f"Last Month's Principal: ${last_month.get('principal', 0):,.2f}", className='mb-2'),
                                html.P(f"Total Equity Gained: ${equity_gained:,.2f}", className='mb-2')
                            ], className='small')
                        ], className='p-2')
                    ], xs=12)
                ])
            except Exception as e:
                logger.error(f"Error creating loan info: {str(e)}")
                return html.Div("Error loading loan information")

        def create_mobile_figure(df, today):
            """Create mobile-optimized figure."""
            try:
                df_filtered = df[df.index % 6 == 0].copy()
                
                fig = go.Figure()
                
                # Add traces with thicker lines for mobile visibility
                fig.add_trace(go.Scatter(
                    x=df_filtered['date_str'],
                    y=df_filtered['balance'],
                    name='Balance',
                    line=dict(color='navy', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_filtered['date_str'],
                    y=df_filtered['cumulative_interest'],
                    name='Interest',
                    line=dict(color='red', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_filtered['date_str'],
                    y=df_filtered['cumulative_principal'],
                    name='Principal',
                    line=dict(color='green', width=3)
                ))
                
                # Add today's line
                today_str = today.strftime('%Y-%m')
                fig.add_shape(
                    type="line",
                    x0=today_str,
                    x1=today_str,
                    y0=0,
                    y1=1,
                    yref="paper",
                    line=dict(color="black", width=2, dash="solid")
                )
                
                # Mobile-optimized layout
                # For the chart, only show start and end dates
                first_date = df_filtered['date_str'].iloc[0]
                last_date = df_filtered['date_str'].iloc[-1]
                
                # Create the graph
                fig = go.Figure()
                
                # Add traces with thicker lines for mobile visibility
                fig.add_trace(go.Scatter(
                    x=df_filtered['date_str'],
                    y=df_filtered['balance'],
                    name='Balance',
                    line=dict(color='navy', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_filtered['date_str'],
                    y=df_filtered['cumulative_interest'],
                    name='Interest',
                    line=dict(color='red', width=3)
                ))
                fig.add_trace(go.Scatter(
                    x=df_filtered['date_str'],
                    y=df_filtered['cumulative_principal'],
                    name='Principal',
                    line=dict(color='green', width=3)
                ))
                
                # Add today's line
                today_str = today.strftime('%Y-%m')
                if today_str >= first_date and today_str <= last_date:
                    fig.add_shape(
                        type="line",
                        x0=today_str,
                        x1=today_str,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(color="black", width=2, dash="solid")
                    )
                
                # Simplified mobile layout with only start/end dates
                fig.update_layout(
                    title=None,
                    xaxis_title=None,  # Remove x-axis title to save space
                    yaxis_title='Amount ($)',
                    xaxis=dict(
                        tickmode='array',
                        tickvals=[first_date, last_date],
                        ticktext=[
                            f"Start: {first_date}",
                            f"End: {last_date}"
                        ],
                        tickangle=0,  # Horizontal text since we have fewer labels
                        tickfont=dict(size=12)  # Slightly larger font since we have fewer labels
                    ),
                    legend=dict(
                        orientation="h",  # Horizontal legend for mobile
                        yanchor="bottom",
                        y=1.02,
                        xanchor="left",
                        x=0
                    ),
                    margin=dict(l=40, r=20, t=60, b=80),  # Adjusted margins for mobile
                    height=350  # Fixed height for mobile
                )
                
                return fig
                
            except Exception as e:
                logger.error(f"Error creating figure: {str(e)}")
                return go.Figure()

        def create_mobile_table(df, months_into_loan):
            """Create mobile-optimized table components with month display."""
            try:
                # Format numeric columns for mobile display
                df = df.copy()
                for col in ['payment', 'principal', 'interest', 'balance', 
                        'cumulative_interest', 'cumulative_principal']:
                    df[col] = df[col].apply(lambda x: f"${x:,.0f}")

                # Format the date as month and year
                df['month_display'] = df['date'].dt.strftime('%b %Y')

                # Mobile-optimized columns
                columns = [
                    {"name": "Month", "id": "month_display", "width": "100px"},
                    {"name": "Payment", "id": "payment", "width": "90px"},
                    {"name": "Principal", "id": "principal", "width": "90px"},
                    {"name": "Interest", "id": "interest", "width": "90px"},
                    {"name": "Balance", "id": "balance", "width": "100px"}
                ]
                
                # Mobile-optimized conditional styling
                styles = [
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    },
                    {
                        'if': {'filter_query': f'{{month}} = {months_into_loan}'},
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

        def create_error_response(error_msg):
            """Create mobile-friendly error response."""
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Error loading data",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color='red')
            )
            empty_fig.update_layout(
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(showgrid=False, zeroline=False, visible=False),
                margin=dict(l=20, r=20, t=20, b=20)  # Compact margins for mobile
            )
            
            return (
                html.Div("Error loading loan information", className='text-danger'),
                empty_fig,
                [],
                [],
                [],
                error_msg,
                {'display': 'block', 'color': 'red', 'marginBottom': '20px'}
            )

        return dash_app
    
    except Exception as e:
        logger.error(f"Error creating amortization dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        raise