import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from flask_login import current_user
from services.transaction_service import get_transactions_for_user

def create_transactions_dash(server):
    dash_app = dash.Dash(__name__, server=server, url_base_pathname='/transactions/')
    
    dash_app.layout = html.Div([
        html.H1('Transactions'),
        dcc.Dropdown(id='property-filter', placeholder='Select Property'),
        dcc.DatePickerRange(id='date-range'),
        dash_table.DataTable(id='transactions-table')
    ])

    @dash_app.callback(
        Output('transactions-table', 'data'),
        [Input('property-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_table(property_id, start_date, end_date):
        transactions = get_transactions_for_user(current_user.id, property_id, start_date, end_date)
        return transactions

    return dash_app