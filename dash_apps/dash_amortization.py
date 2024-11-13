import dash
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
    """
    Validate loan input parameters.
    
    Args:
        loan_amount (float): Principal loan amount
        annual_rate (float): Annual interest rate as decimal (e.g., 0.05 for 5%)
        years (float): Loan term in years
        
    Returns:
        tuple: (bool, str) - (is_valid, error_message)
    """
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
    """
    Calculate amortization schedule with cumulative totals.
    
    Args:
        principal (float): Principal loan amount
        annual_rate (float): Annual interest rate as decimal
        years (float): Loan term in years
        
    Yields:
        dict: Monthly payment details including cumulative totals
    """
    try:
        logger.info(f"Calculating amortization schedule: principal=${principal:,.2f}, rate={annual_rate:.4f}, years={years}")
        
        # Validate inputs
        is_valid, error_message = validate_loan_data(principal, annual_rate, years)
        if not is_valid:
            logger.error(f"Invalid loan data: {error_message}")
            raise ValueError(error_message)
        
        # Calculate monthly values
        monthly_rate = annual_rate / 12
        num_payments = int(years * 12)
        
        # Calculate monthly payment using amortization formula
        payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
        logger.debug(f"Calculated monthly payment: ${payment:,.2f}")
        
        balance = principal
        cumulative_interest = 0
        cumulative_principal = 0
        
        for month in range(1, num_payments + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest
            balance = max(0, balance - principal_paid)  # Prevent negative balance
            
            cumulative_interest += interest
            cumulative_principal += principal_paid
            
            # Log every 12th month for debugging
            if month % 12 == 0:
                logger.debug(f"Year {month//12} summary - "
                           f"Balance: ${balance:,.2f}, "
                           f"Cumulative Interest: ${cumulative_interest:,.2f}, "
                           f"Cumulative Principal: ${cumulative_principal:,.2f}")
            
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
    """
    Create and configure the amortization dashboard.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dash.Dash: Configured Dash application
    """
    try:
        logger.info("Initializing amortization dashboard")
        
        dash_app = dash.Dash(
            __name__,
            server=flask_app,
            routes_pathname_prefix='/dashboards/_dash/amortization/',
            requests_pathname_prefix='/dashboards/_dash/amortization/',
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )

        # Define styling
        table_header_style = {
            'backgroundColor': 'navy',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'fontFamily': 'Arial, Helvetica, sans-serif'
        }
        
        table_cell_style = {
            'textAlign': 'center',
            'fontFamily': 'Arial, Helvetica, sans-serif'
        }

        # Layout definition
        dash_app.layout = dbc.Container([
            html.H2('Amortization Schedule', className='mt-4 mb-4'),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Select Property'),
                    dcc.Dropdown(
                        id='property-selector',
                        placeholder='Select Property',
                        className='mb-3'
                    )
                ], width=6),
            ], className='mb-4'),
            # Add error display div
            html.Div(id='error-display', className='alert alert-danger', style={'display': 'none'}),
            dcc.Graph(id='amortization-graph'),
            dbc.Card(
                dbc.CardBody(id='loan-info'),
                className="mb-4",
                style={"border-radius": "15px"}
            ),
            html.H3('Amortization Table', className='mt-4 mb-3'),
            dash_table.DataTable(
                id='amortization-table',
                style_header=table_header_style,
                style_cell=table_cell_style,
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            )
        ], fluid=True)

        @dash_app.callback(
            Output('property-selector', 'options'),
            Input('property-selector', 'id')
        )
        def populate_property_dropdown(dropdown_id):
            """Populate the property dropdown with available properties."""
            try:
                logger.info(f"Populating property dropdown for user: {current_user.id}")
                
                with flask_app.app_context():
                    properties = get_properties_for_user(current_user.id, current_user.name)
                
                if not properties:
                    logger.warning(f"No properties found for user: {current_user.id}")
                    return []
                
                options = []
                for prop in properties:
                    # Split address at first comma and use first part
                    street_address = prop['address'].split(',')[0].strip()
                    options.append({
                        'label': street_address,
                        'value': prop['address']  # Keep full address as value for backend lookup
                    })
                
                logger.debug(f"Generated {len(options)} dropdown options")
                return options
                
            except Exception as e:
                logger.error(f"Error populating property dropdown: {str(e)}")
                logger.error(traceback.format_exc())
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
            """
            Update all amortization components based on selected property.
            
            Args:
                selected_property (str): Selected property address
                
            Returns:
                tuple: (loan_info, figure, table_data, columns, styles, error_msg, error_style)
            """
            try:
                logger.info(f"Updating amortization for property: {selected_property}")
                
                # Handle no selection
                if not selected_property:
                    logger.debug("No property selected, showing default view")
                    
                    # Create empty figure with instruction text
                    fig = go.Figure()
                    fig.add_annotation(
                        text="Please select a property to view an Amortization Chart and Table.",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(size=16)
                    )
                    fig.update_layout(
                        xaxis=dict(showgrid=False, zeroline=False, visible=False),
                        yaxis=dict(showgrid=False, zeroline=False, visible=False)
                    )
                    
                    return (
                        html.Div("No property selected"),  # loan_info
                        fig,                              # figure
                        [],                              # table_data
                        [],                              # columns
                        [],                              # style_data_conditional
                        "",                              # error_msg
                        {'display': 'none'}              # error_style
                    )

                # Get property data
                properties = get_properties_for_user(current_user.id, current_user.name)
                property_data = next((prop for prop in properties if prop['address'] == selected_property), None)
                
                if not property_data:
                    logger.error(f"Property not found: {selected_property}")
                    return create_error_response("Property not found")

                # Validate required loan fields
                required_fields = ['loan_amount', 'primary_loan_rate', 'primary_loan_term', 'loan_start_date']
                missing_fields = [field for field in required_fields if not property_data.get(field)]
                if missing_fields:
                    error_msg = f"Missing required loan information: {', '.join(missing_fields)}"
                    logger.error(error_msg)
                    return create_error_response(error_msg)

                # Parse loan data with validation
                try:
                    loan_amount = float(property_data['loan_amount'])
                    interest_rate = float(property_data['primary_loan_rate']) / 100
                    loan_term = float(property_data['primary_loan_term']) / 12  # Convert months to years
                    loan_start_date = datetime.strptime(property_data['loan_start_date'], '%Y-%m-%d').date()
                except (ValueError, TypeError) as e:
                    error_msg = f"Error parsing loan data: {str(e)}"
                    logger.error(error_msg)
                    return create_error_response(error_msg)

                # Calculate amortization schedule
                try:
                    schedule = list(amortize(loan_amount, interest_rate, loan_term))
                    df = pd.DataFrame(schedule)
                except Exception as e:
                    error_msg = f"Error calculating amortization schedule: {str(e)}"
                    logger.error(error_msg)
                    return create_error_response(error_msg)

                # Calculate current loan status
                today = date.today()
                months_into_loan = relativedelta(today, loan_start_date).months + relativedelta(today, loan_start_date).years * 12
                
                if months_into_loan < 0:
                    logger.warning(f"Loan start date is in the future: {loan_start_date}")
                    months_into_loan = 0
                
                # Calculate metrics with safe handling
                try:
                    last_month_equity = df.iloc[months_into_loan - 1]['principal'] if months_into_loan > 0 else 0
                    equity_gained_since_acquisition = df.iloc[:months_into_loan]['principal'].sum() if months_into_loan > 0 else 0
                    
                    logger.debug(f"Loan metrics calculated - Months into loan: {months_into_loan}, "
                               f"Last month equity: ${last_month_equity:.2f}, "
                               f"Total equity gained: ${equity_gained_since_acquisition:.2f}")
                except Exception as e:
                    error_msg = f"Error calculating loan metrics: {str(e)}"
                    logger.error(error_msg)
                    return create_error_response(error_msg)

                # Create loan info display
                loan_info = html.Div([
                    dbc.Row([
                        dbc.Col(
                            html.P(f"Months into Loan Repayment: {months_into_loan}", 
                                  className='font-weight-bold mb-0'), 
                            width=4
                        ),
                        dbc.Col(
                            html.P(f"Equity Gained Last Month: ${last_month_equity:.2f}", 
                                  className='font-weight-bold mb-0'), 
                            width=4
                        ),
                        dbc.Col(
                            html.P(f"Equity Gained Since Acquisition: ${equity_gained_since_acquisition:,.2f}", 
                                  className='font-weight-bold mb-0'), 
                            width=4
                        )
                    ])
                ])

                # Generate graph data
                try:
                    # Create date strings
                    df['date'] = [loan_start_date + relativedelta(months=i) for i in range(len(df))]
                    df['date_str'] = [d.strftime('%y-%m') for d in df['date']]
                    
                    # Filter for every 24 months (2 years) for better readability
                    df_filtered = df[df.index % 24 == 0].copy()
                    
                    logger.debug(f"Created graph data with {len(df_filtered)} points")
                    
                except Exception as e:
                    error_msg = f"Error preparing graph data: {str(e)}"
                    logger.error(error_msg)
                    return create_error_response(error_msg)

                # Create the graph
                try:
                    fig = go.Figure()
                    
                    # Add the three main traces
                    fig.add_trace(go.Scatter(
                        x=df_filtered['date_str'], 
                        y=df_filtered['balance'], 
                        name='Loan Balance',
                        line=dict(color='navy')
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_filtered['date_str'], 
                        y=df_filtered['cumulative_interest'], 
                        name='Cumulative Interest',
                        line=dict(color='red')
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_filtered['date_str'], 
                        y=df_filtered['cumulative_principal'], 
                        name='Cumulative Principal',
                        line=dict(color='green')
                    ))
                    
                    # Add vertical line for today
                    today_str = date.today().strftime('%y-%m')
                    fig.add_shape(
                        type="line",
                        x0=today_str,
                        x1=today_str,
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(color="black", width=2, dash="solid")
                    )
                    
                    # Add "Today" annotation
                    fig.add_annotation(
                        x=today_str,
                        y=1,
                        yref="paper",
                        text="Today",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="black",
                        font=dict(size=12, color="black"),
                        align="center",
                        xanchor="left",
                        yanchor="bottom"
                    )
                    
                    # Update layout
                    fig.update_layout(
                        title="Loan Amortization Over Time",
                        xaxis_title='Date',
                        yaxis_title='Amount ($)',
                        xaxis=dict(
                            tickangle=45,
                            tickmode='array',
                            tickvals=df_filtered['date_str'],
                            ticktext=[d[:4] for d in df_filtered['date_str']]
                        ),
                        showlegend=True,
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01
                        )
                    )
                    
                except Exception as e:
                    error_msg = f"Error creating graph: {str(e)}"
                    logger.error(error_msg)
                    return create_error_response(error_msg)

                # Prepare table data
                try:
                    # Format numeric columns
                    for col in ['payment', 'principal', 'interest', 'balance', 
                              'cumulative_interest', 'cumulative_principal']:
                        df[col] = df[col].apply(lambda x: f"${x:,.2f}")

                    table_data = df.to_dict('records')
                    columns = [
                        {"name": "Month", "id": "month"},
                        {"name": "Date", "id": "date_str"},
                        {"name": "Payment", "id": "payment"},
                        {"name": "Principal", "id": "principal"},
                        {"name": "Interest", "id": "interest"},
                        {"name": "Balance", "id": "balance"},
                        {"name": "Cumulative Interest", "id": "cumulative_interest"},
                        {"name": "Cumulative Principal", "id": "cumulative_principal"}
                    ]
                    
                    # Highlight current month
                    style_data_conditional = [
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        },
                        {
                            'if': {'filter_query': f'{{month}} = {months_into_loan}'},
                            'backgroundColor': 'yellow',
                            'fontWeight': 'bold'
                        }
                    ]
                    
                except Exception as e:
                    error_msg = f"Error preparing table data: {str(e)}"
                    logger.error(error_msg)
                    return create_error_response(error_msg)

                logger.info(f"Successfully updated amortization for property: {selected_property}")
                return (
                    loan_info,
                    fig,
                    table_data,
                    columns,
                    style_data_conditional,
                    "",                # No error message
                    {'display': 'none'} # Hide error display
                )

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(f"Error in update_amortization: {error_msg}")
                logger.error(traceback.format_exc())
                return create_error_response(error_msg)

        def create_error_response(error_msg):
            """Create a standardized error response for the callback."""
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text="Error loading amortization data",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color='red')
            )
            
            return (
                html.Div("Error loading loan information"),  # loan_info
                empty_fig,                                   # figure
                [],                                         # table_data
                [],                                         # columns
                [],                                         # style_data_conditional
                error_msg,                                  # error_msg
                {'display': 'block', 'color': 'red'}        # error_style
            )

        return dash_app
    
    except Exception as e:
        logger.error(f"Error creating amortization dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        # Re-raise the exception after logging
        raise