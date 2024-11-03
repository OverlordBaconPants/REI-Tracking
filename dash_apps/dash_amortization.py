import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from flask_login import current_user
from services.transaction_service import get_properties_for_user
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import current_app
import traceback

def amortize(principal, annual_rate, years):
    """Calculate amortization schedule with cumulative totals."""
    monthly_rate = annual_rate / 12
    num_payments = int(years * 12)
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    balance = principal
    cumulative_interest = 0
    cumulative_principal = 0
    
    for month in range(1, num_payments + 1):
        interest = balance * monthly_rate
        principal_paid = payment - interest
        balance -= principal_paid
        
        cumulative_interest += interest
        cumulative_principal += principal_paid
        
        yield {
            'month': month,
            'payment': payment,
            'principal': principal_paid,
            'interest': interest,
            'balance': max(0, balance),
            'cumulative_interest': cumulative_interest,
            'cumulative_principal': cumulative_principal
        }

def create_amortization_dash(flask_app):
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        routes_pathname_prefix='/dashboards/_dash/amortization/',
        requests_pathname_prefix='/dashboards/_dash/amortization/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    # Define table styles
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

    dash_app.layout = dbc.Container([
        html.H2('Amortization Schedule', className='mt-4 mb-4'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Select Property'),
                dcc.Dropdown(id='property-selector', placeholder='Select Property')
            ], width=6),
        ], className='mb-4'),
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
        try:
            with flask_app.app_context():
                properties = get_properties_for_user(current_user.id, current_user.name)
            return [{'label': f"{prop['address'][:15]}..." if len(prop['address']) > 15 else prop['address'], 
                                    'value': prop['address']} for prop in properties]
        except Exception as e:
            print(f"Error in populate_property_dropdown: {str(e)}")
            print(traceback.format_exc())
            return []

    @dash_app.callback(
        [Output('loan-info', 'children'),
        Output('amortization-graph', 'figure'),
        Output('amortization-table', 'data'),
        Output('amortization-table', 'columns'),
        Output('amortization-table', 'style_data_conditional')],
        [Input('property-selector', 'value')]
    )
    def update_amortization(selected_property):
        if not selected_property:
            # Create a figure with a text annotation
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
            
            # Return empty data for other components
            return html.Div("No property selected"), go.Figure(), [], [], []
        
        try:
            properties = get_properties_for_user(current_user.id, current_user.name)
            
            if not selected_property:
                return html.Div("No property selected"), {}, [], []

            property_data = next((prop for prop in properties if prop['address'] == selected_property), None)
            if not property_data:
                return html.Div("Property not found"), {}, [], []

            loan_amount = float(property_data['loan_amount'])
            interest_rate = float(property_data['primary_loan_rate']) / 100
            loan_term = float(property_data['primary_loan_term']) / 12  # Convert months to years
            loan_start_date = datetime.strptime(property_data['loan_start_date'], '%Y-%m-%d').date()

            schedule = list(amortize(loan_amount, interest_rate, loan_term))
            df = pd.DataFrame(schedule)

            # Calculate current loan status
            today = date.today()
            current_month = (today.year - loan_start_date.year) * 12 + today.month - loan_start_date.month + 1
            months_into_loan = relativedelta(today, loan_start_date).months + relativedelta(today, loan_start_date).years * 12
            last_month_equity = df.iloc[months_into_loan - 1]['principal'] if months_into_loan > 0 else 0

            # Calculate equity gained since acquisition
            equity_gained_since_acquisition = df.iloc[:months_into_loan]['principal'].sum() if months_into_loan > 0 else 0

            # Create loan_info content
            loan_info = html.Div([
                dbc.Row([
                    dbc.Col(html.P(f"Months into Loan Repayment: {months_into_loan}", className='font-weight-bold mb-0'), width=4),
                    dbc.Col(html.P(f"Equity Gained Last Month: ${last_month_equity:.2f}", className='font-weight-bold mb-0'), width=4),
                    dbc.Col(html.P(f"Equity Gained Since Acquisition: ${equity_gained_since_acquisition:,.2f}", className='font-weight-bold mb-0'), width=4)
                ])
            ])

            # Create date strings manually without using .dt accessor
            df['date'] = [loan_start_date + relativedelta(months=i) for i in range(len(df))]
            df['date_str'] = [d.strftime('%y-%m') for d in df['date']]

            # Filter data points for every 6 months and create an explicit copy
            df_filtered = df[df.index % 24 == 0].copy()

            # Debug: Print the shape of df_filtered
            print(f"\nShape of df_filtered: {df_filtered.shape}")

            # Debug: Print the last few rows to check final cumulative values
            print("\nLast few rows with cumulative values:")
            print(df_filtered[['date_str', 'interest', 'principal', 'cumulative_interest', 'cumulative_principal']].tail())

            # Create the figure
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_filtered['date_str'], y=df_filtered['balance'], name='Loan Balance'))
            fig.add_trace(go.Scatter(x=df_filtered['date_str'], y=df_filtered['cumulative_interest'], name='Cumulative Interest'))
            fig.add_trace(go.Scatter(x=df_filtered['date_str'], y=df_filtered['cumulative_principal'], name='Cumulative Principal'))

            # Add a vertical line for today's date
            today_str = date.today().strftime('%y-%m')
            fig.add_shape(
                type="line",
                x0=today_str,
                x1=today_str,
                y0=0,
                y1=1,
                yref="paper",
                line=dict(color="black", width=2, dash="solid"),
            )

            # Add annotation for today's date
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

            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Amount ($)',
                xaxis=dict(
                    tickmode='array',
                    tickvals=df_filtered['date_str'],
                    ticktext=[d[:4] for d in df_filtered['date_str']],  # Show only the year
                    tickangle=45
                )
            )
            
            # Debug: Print the range of values for each trace
            print("\nValue ranges:")
            print(f"Loan Balance: {df_filtered['balance'].min()} to {df_filtered['balance'].max()}")
            print(f"Cumulative Interest: {df_filtered['cumulative_interest'].min()} to {df_filtered['cumulative_interest'].max()}")
            print(f"Cumulative Principal: {df_filtered['cumulative_principal'].min()} to {df_filtered['cumulative_principal'].max()}")

            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Amount ($)',
                xaxis=dict(
                    tickangle=90,
                    tickmode='array',
                    tickvals=df_filtered['date_str'],
                    ticktext=df_filtered['date_str']
                )
            )

            # Format numeric columns
            for col in ['payment', 'principal', 'interest', 'balance', 'cumulative_interest', 'cumulative_principal']:
                df[col] = df[col].apply(lambda x: f"${x:,.2f}")

            # Prepare table data
            table_data = df.to_dict('records')

            # Prepare table columns with title case headers
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

            style_data_conditional = [
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'filter_query': f'{{month}} = {current_month}'},
                    'backgroundColor': 'yellow',
                    'fontWeight': 'bold'
                }
            ]

            return loan_info, fig, table_data, columns, style_data_conditional

        except Exception as e:
            print(f"Error in update_amortization: {str(e)}")
            print(traceback.format_exc())
            return html.Div(f"An error occurred: {str(e)}"), go.Figure(), [], []

    return dash_app