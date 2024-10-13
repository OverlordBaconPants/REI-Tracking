import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from flask_login import current_user
from services.transaction_service import get_transactions_for_view, get_properties_for_user
import plotly.graph_objs as go
import traceback
from flask import current_app, url_for
import requests

def create_transactions_dash(flask_app):
    print("Creating Dash app for transactions...")
    
    external_stylesheets = [dbc.themes.BOOTSTRAP, '/static/css/styles.css']
    
    dash_app = dash.Dash(__name__, 
                         server=flask_app, 
                         url_base_pathname='/transactions/view/dash/',
                         external_stylesheets=external_stylesheets)

    # Define columns without the 'Edit' column
    base_columns = [
        {'name': 'Category', 'id': 'category'},
        {'name': 'Description', 'id': 'description'},
        {'name': 'Amount', 'id': 'amount'},
        {'name': 'Date Incurred', 'id': 'date'},
        {'name': 'Collector/Payer', 'id': 'collector_payer'},
        {'name': 'Reimb. Date', 'id': 'reimbursement_date'},
        {'name': 'Reimb. Description', 'id': 'reimbursement_description'},
        {'name': 'Artifact', 'id': 'documentation_file', 'presentation': 'markdown'},
    ]

    dash_app.layout = dbc.Container([
        dcc.Location(id='url', refresh=False),
        html.H2('Filter Transactions to View', className='mt-4 mb-4'),
        dbc.Row([
            dbc.Col([
                dbc.Label('Property Address'),
                dcc.Dropdown(id='property-filter', placeholder='Select Property', multi=False)
            ], width=3),
            dbc.Col([
                dbc.Label('Transaction Type'),
                dcc.Dropdown(
                    id='type-filter',
                    options=[
                        {'label': 'Incomes', 'value': 'income'},
                        {'label': 'Expenses', 'value': 'expense'}
                    ],
                    placeholder='Select Transaction Type'
                )
            ], width=3),
            dbc.Col([
                dbc.Label('Reimbursement Status'),
                dcc.Dropdown(
                    id='reimbursement-filter',
                    options=[
                        {'label': 'All', 'value': 'all'},
                        {'label': 'Pending', 'value': 'pending'},
                        {'label': 'Completed', 'value': 'completed'}
                    ],
                    value='all',
                    placeholder='Select Reimbursement Status'
                )
            ], width=3),
            dbc.Col([
                dbc.Label('Date Range'),
                dcc.DatePickerRange(
                    id='date-range',
                    start_date_placeholder_text='Start Date',
                    end_date_placeholder_text='End Date'
                )
            ], width=3)
        ], className='mb-4'),
        
        html.H2(id='transactions-header', className='mt-4 mb-3'),
        dash_table.DataTable(
            id='transactions-table',
            columns=base_columns,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'font-family': 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif',
                'font-size': '14px',
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100px',
                'maxWidth': '180px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'border': '1px solid #dee2e6',
                'whiteSpace': 'nowrap',
                'height': '40px',
                'lineHeight': '40px',
                'padding': '0 10px',
                'textOverflow': 'ellipsis',
                'overflow': 'hidden',
            },
            style_data={
                'border': '1px solid #dee2e6',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'amount'},
                    'color': 'green'
                }
            ],
            tooltip_duration=None,
            markdown_options={'html': True},
            page_size=10,
            page_action='native',
            sort_action='native',
            sort_mode='multi',
            filter_action='none'
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("Edit Transaction"),
                dbc.ModalBody(id="edit-transaction-content"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-edit-modal", className="ml-auto")
                ),
            ],
            id="edit-transaction-modal",
            size="lg",
        ),
    ], fluid=True)

    @dash_app.callback(
        [Output('transactions-table', 'data'),
         Output('transactions-header', 'children'),
         Output('property-filter', 'options'),
         Output('transactions-table', 'columns')],
        [Input('property-filter', 'value'),
         Input('type-filter', 'value'),
         Input('reimbursement-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_table(property_id, transaction_type, reimbursement_status, start_date, end_date):
        try:
            current_app.logger.debug(f"update_table called with: property_id={property_id}, transaction_type={transaction_type}, reimbursement_status={reimbursement_status}, start_date={start_date}, end_date={end_date}")
            
            # Get transactions
            transactions = get_transactions_for_view(current_user.id, current_user.name, property_id, reimbursement_status, start_date, end_date)
            current_app.logger.debug(f"Transactions retrieved: {transactions}")
            
            df = pd.DataFrame(transactions)
            
            current_app.logger.debug(f"DataFrame created. Columns: {df.columns}")
            
            if df.empty:
                current_app.logger.debug("DataFrame is empty")
                header = "No transactions found for the selected criteria"
                data = []
            else:
                current_app.logger.debug(f"DataFrame before filtering: {df.to_string()}")
                if transaction_type:
                    df = df[df['type'] == transaction_type]
                
                current_app.logger.debug(f"DataFrame after filtering: {df.to_string()}")
                
                if 'amount' in df.columns:
                    df['amount'] = df.apply(lambda row: f"${abs(float(row['amount'])):.2f}", axis=1)
                
                # Add artifact links
                if 'documentation_file' in df.columns:
                    df['documentation_file'] = df['documentation_file'].apply(
                        lambda x: f'[View/Download]({url_for("transactions.get_artifact", filename=x)})' if x else ''
                    )
        
                # Add Edit links for admin users
            if current_user.is_authenticated and current_user.role == 'Admin':
                df['edit'] = df.apply(lambda row: f'[Edit]({url_for("transactions.edit_transactions", transaction_id=row["id"])})', axis=1)

                # Create header
                type_str = 'Income' if transaction_type == 'income' else 'Expense' if transaction_type == 'expense' else 'All'
                property_str = property_id[:20] + '...' if property_id else 'All Properties'
                start_str = start_date if start_date else 'Earliest'
                end_str = end_date if end_date else 'Latest'
                header = f"{type_str} Transactions for {property_str} from {start_str} to {end_str}"
                
                data = df.to_dict('records')
            
            # Get property options
            properties = get_properties_for_user(current_user.id, current_user.name)
            current_app.logger.debug(f"Properties retrieved: {properties}")
            property_options = [{'label': f"{prop['address'][:15]}..." if len(prop['address']) > 15 else prop['address'], 
                                'value': prop['address']} for prop in properties]
            property_options.insert(0, {'label': 'All Properties', 'value': 'all'})
            
            # Determine columns based on user role
            columns = base_columns.copy()
            if current_user.is_authenticated and current_user.role == 'Admin':
                columns.append({'name': 'Edit', 'id': 'edit', 'presentation': 'markdown'})
            
            current_app.logger.debug(f"User role: {current_user.role if current_user.is_authenticated else 'Not authenticated'}")
            current_app.logger.debug(f"Columns: {columns}")
            
            current_app.logger.debug(f"Returning: data={data}, header={header}, property_options={property_options}, columns={columns}")
            return data, header, property_options, columns
        except Exception as e:
            current_app.logger.error(f"Error in update_table: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            raise

       
    print(f"Dash app created with server: {dash_app.server}")
    return dash_app