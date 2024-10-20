import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from flask_login import current_user
from services.transaction_service import get_transactions_for_view, get_properties_for_user
import plotly.graph_objs as go
from flask import current_app, url_for
import io
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import json

def create_transactions_dash(flask_app):
    print("Creating Dash app for transactions...")
    
    external_stylesheets = [dbc.themes.BOOTSTRAP, '/static/css/styles.css']
    
    dash_app = dash.Dash(__name__, 
                         server=flask_app, 
                         url_base_pathname='/transactions/view/dash/',
                         external_stylesheets=external_stylesheets)

    # Define columns without the 'Edit' column
    base_columns = [
        {'name': 'ID', 'id': 'id', 'hidden': True},
        {'name': 'Category', 'id': 'category'},
        {'name': 'Description', 'id': 'description'},
        {'name': 'Amount', 'id': 'amount'},
        {'name': 'Date Incurred', 'id': 'date'},
        {'name': 'Collector/Payer', 'id': 'collector_payer'},
        {'name': 'Reimb. Date', 'id': 'date_shared'},
        {'name': 'Reimb. Description', 'id': 'share_description'},
        {'name': 'Artifact', 'id': 'documentation_file', 'presentation': 'markdown'},
    ]

    dash_app.layout = dbc.Container([
        dcc.Location(id='url', refresh=False),
        dcc.Store(id='transaction-update-trigger', storage_type='memory'),
        dcc.Store(id='refresh-trigger', storage_type='memory'),
        dcc.Store(id='filter-options', storage_type='session'),
        html.Div(id='hidden-div', style={'display': 'none'}),
        html.Div(id='flash-message-container', className='flash-messages'),
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
        dbc.Row([
            dbc.Col([
                dbc.Label('Report Type'),
                dcc.Dropdown(
                    id='report-type',
                    options=[
                        {'label': 'Summary Report', 'value': 'summary'},
                        {'label': 'Detailed Report', 'value': 'detailed'}
                    ],
                    value='summary',
                    placeholder='Select Report Type'
                ),
                html.Div([
                    html.P("Summary Report: Provides an overview of transactions grouped by category and type, showing totals and date ranges.", className="text-muted mt-2"),
                    html.P("Detailed Report: Includes all individual transaction details as shown in the table above.", className="text-muted")
                ], id="report-description")
            ], width=9),
            dbc.Col([
                dbc.Button("Generate PDF Report", id="generate-report-btn", color="primary", className="mb-2 w-100"),
                html.Div(id="report-link-container", className="w-100")
            ], width=3, className="d-flex flex-column justify-content-end")
        ], className='mb-4'),
        
        html.H2(id='transactions-header', className='mt-4 mb-3'),

        dash_table.DataTable(
            id='transactions-table',
            columns=base_columns,
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'font-family': 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif',
                'font-size': '14px',
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '100px',
                'maxWidth': '180px',
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
            page_action='native',
            page_current=0,
            page_size=10,  # Display 15 transactions per page
            sort_action='native',
            sort_mode='multi',
            filter_action='none'
        ),
        html.Div(id='table-container', style={'height': 'calc(100vh)', 'overflow': 'auto'}),

        dbc.Modal(
            [
                dbc.ModalHeader("Edit Transaction"),
                dbc.ModalBody([
                    html.Iframe(
                        id="edit-transaction-iframe",
                        style={"width": "100%", "height": "100%", "border": "none"}
                    )
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-edit-modal", className="ml-auto")
                ),
            ],
            id="edit-transaction-modal",
            size="xl",          
        ),
        
    ], fluid=True, style={'height': '100vh', 'display': 'flex', 'flexDirection': 'column'})

    @dash_app.callback(
        [Output('transactions-table', 'data'),
         Output('transactions-header', 'children'),
         Output('property-filter', 'options'),
         Output('transactions-table', 'columns')],
        [Input('transaction-update-trigger', 'data'),
         Input('property-filter', 'value'),
         Input('type-filter', 'value'),
         Input('reimbursement-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('refresh-trigger', 'data')]
    )
    def update_table(trigger, property_id, transaction_type, reimbursement_status, start_date, end_date, refresh_trigger):
        try:
            current_app.logger.debug(f"update_table called with: property_id={property_id}, transaction_type={transaction_type}, reimbursement_status={reimbursement_status}, start_date={start_date}, end_date={end_date}")
            
            # Get properties
            properties = get_properties_for_user(current_user.id, current_user.name, current_user.role == 'Admin')
            current_app.logger.debug(f"Properties retrieved: {properties}")
            property_options = [{'label': f"{prop['address'][:15]}..." if len(prop['address']) > 15 else prop['address'], 
                                'value': prop['address']} for prop in properties]
            property_options.insert(0, {'label': 'All Properties', 'value': 'all'})
            
            # Get transactions
            transactions = get_transactions_for_view(current_user.id, current_user.name, property_id, reimbursement_status, start_date, end_date, current_user.role == 'Admin')
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
                    df['edit'] = df.apply(lambda row: f'[Edit]', axis=1)
                
                if 'id' not in df.columns:
                    current_app.logger.warning("Transaction ID not found in data. This may cause issues with editing.")
                else:
                    # Add Edit links for admin users
                    if current_user.is_authenticated and current_user.role == 'Admin':
                        df['edit'] = df.apply(lambda row: f'[Edit](#{row["id"]})', axis=1)

                # Create header
                type_str = 'Income' if transaction_type == 'income' else 'Expense' if transaction_type == 'expense' else 'All'
                property_str = property_id[:20] + '...' if property_id and property_id != 'all' else 'All Properties'
                start_str = start_date if start_date else 'Earliest'
                end_str = end_date if end_date else 'Latest'
                header = f"{type_str} Transactions for {property_str} from {start_str} to {end_str}"
                
                data = df.to_dict('records')
            
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

    @dash_app.callback(
        Output('filter-options', 'data'),
        [Input('property-filter', 'value'),
         Input('type-filter', 'value'),
         Input('reimbursement-filter', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date')]
    )
    def update_filter_options(property_id, transaction_type, reimbursement_status, start_date, end_date):
        return {
            'property_id': property_id,
            'transaction_type': transaction_type,
            'reimbursement_status': reimbursement_status,
            'start_date': start_date,
            'end_date': end_date
        }

    @dash_app.callback(
        [Output("edit-transaction-modal", "is_open"),
        Output("edit-transaction-iframe", "src")],
        [Input("transactions-table", "active_cell"),
        Input("close-edit-modal", "n_clicks")],
        [State("transactions-table", "data"),
        State("transactions-table", "page_current"),
        State("transactions-table", "page_size"),
        State("edit-transaction-modal", "is_open"),
        State("filter-options", "data")]
    )
    def toggle_modal(active_cell, close_clicks, data, page_current, page_size, is_open, filter_options):
        ctx = dash.callback_context
        if not ctx.triggered:
            return is_open, ""
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == "transactions-table" and active_cell and active_cell['column_id'] == 'edit':
            # Calculate the correct row index based on the current page
            row_index = (page_current * page_size) + active_cell['row']
            row = data[row_index]
            transaction_id = row.get('id')
            if transaction_id is None:
                current_app.logger.error(f"Transaction ID not found in row data: {row}")
                return is_open, ""
            
            filter_options_str = json.dumps(filter_options)
            iframe_src = url_for('transactions.edit_transactions', transaction_id=transaction_id, filter_options=filter_options_str)
            current_app.logger.debug(f"Opening edit modal for transaction ID: {transaction_id}")
            return True, iframe_src
        elif trigger_id == "close-edit-modal":
            return False, ""
        
        return is_open, ""

    @dash_app.callback(
        Output('flash-message-container', 'children'),
        Input('transaction-update-trigger', 'data'),
    )
    def display_flash_message(data):
        if data and data.get('message'):
            return dbc.Alert(data['message'], color="success", dismissable=True, duration=2000)
        return []

    dash_app.clientside_callback(
        """
        function(n_clicks) {
            console.log('Initializing closeEditModal function');
            window.closeEditModal = function(shouldRefresh, filterOptions) {
                console.log('closeEditModal called');
                setTimeout(function() {
                    document.getElementById('close-edit-modal').click();
                    console.log('Modal close button clicked');
                    setTimeout(function() {
                        console.log('Triggering Dash update');
                        if (shouldRefresh) {
                            // Apply the stored filter options
                            if (filterOptions) {
                                Object.keys(filterOptions).forEach(key => {
                                    const element = document.getElementById(key + '-filter');
                                    if (element) {
                                        element.value = filterOptions[key];
                                    }
                                });
                            }
                            
                            // Trigger the Dash update
                            if (window.dash_clientside && window.dash_clientside.callback_context) {
                                window.dash_clientside.callback_context.triggered = [{
                                    'prop_id': 'transaction-update-trigger.data',
                                    'value': {'message': 'Transaction updated successfully!', 'refresh': true}
                                }];
                            } else {
                                // Fallback: manually trigger an update
                                console.log('Fallback: Manually triggering update');
                                return {
                                    'transaction-update-trigger': {'time': new Date().getTime()}
                                };
                            }
                            
                            // Trigger a refresh of the transactions table
                            if (window.dash_clientside) {
                                window.dash_clientside.no_update = Symbol('no_update');
                                return {
                                    'refresh-trigger': {'time': new Date().getTime()}
                                };
                            }
                        }
                    }, 500);
                }, 500);
            };

            console.log('Setting up message event listener');
            window.addEventListener('message', function(event) {
                console.log('Received message:', event.data);
                if (event.data.type === 'transactionUpdated') {
                    console.log('Transaction updated message received');
                    if (window.closeEditModal) {
                        console.log('Calling closeEditModal');
                        window.closeEditModal(event.data.shouldRefresh, event.data.filterOptions);
                    } else {
                        console.error('closeEditModal not found');
                    }
                }
            });

            return '';
        }
        """,
        Output('transaction-update-trigger', 'data'),  # Changed from 'hidden-div' to 'transaction-update-trigger'
        Input('close-edit-modal', 'n_clicks'),
    )
  
    @dash_app.callback(
        Output('report-link-container', 'children'),
        Input('generate-report-btn', 'n_clicks'),
        [State('transactions-table', 'data'),
         State('report-type', 'value'),
         State('transactions-header', 'children')]
    )
    def generate_pdf_report(n_clicks, table_data, report_type, header):
        if n_clicks is None:
            return ""

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                                leftMargin=inch, rightMargin=inch,
                                topMargin=inch, bottomMargin=inch)
        elements = []

        # Add logo
        logo_path = "static/images/logo.png"
        img = Image(logo_path, width=1.5*inch, height=1.5*inch)
        img.hAlign = 'RIGHT'
        elements.append(img)
        elements.append(Spacer(1, 0.5*inch))

        # Create a custom style for the title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12
        )

        # Parse the header and add line breaks
        header_parts = header.split(' for ')
        if len(header_parts) == 2:
            transaction_type, rest = header_parts
            address_and_date = rest.split(' from ')
            if len(address_and_date) == 2:
                address, date_range = address_and_date
                formatted_header = f"{transaction_type} Transactions<br/>for {address}<br/>from {date_range}"
            else:
                formatted_header = header.replace(' for ', '<br/>for ').replace(' from ', '<br/>from ')
        else:
            formatted_header = header.replace(' for ', '<br/>for ').replace(' from ', '<br/>from ')

        elements.append(Paragraph(formatted_header, title_style))
        elements.append(Spacer(1, 0.25*inch))

        if report_type == 'summary':
            summary_data = summarize_transactions(table_data)
            table = Table(summary_data)
        else:
            columns_to_include = ['type', 'category', 'description', 'amount', 'date', 'collector_payer','reimbursement_status']
            table_data = [[col for col in columns_to_include]] + \
                         [[row.get(col, '') for col in columns_to_include] for row in table_data]
            table = Table(table_data)

        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)
        elements.append(table)

        doc.build(elements)
        pdf_data = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        return dbc.Button(
            'Download PDF Report',
            href=f"data:application/pdf;base64,{pdf_data}",
            download="transaction_report.pdf",
            external_link=True,
            color="success",
            className="w-100"
        )

    def summarize_transactions(table_data):
        df = pd.DataFrame(table_data)
        summary = df.groupby(['category', 'type']).agg({
            'amount': 'sum',
            'date': ['min', 'max']
        }).reset_index()
        summary.columns = ['Category', 'Type', 'Total Amount', 'Start Date', 'End Date']
        summary = summary.sort_values(['Type', 'Total Amount'], ascending=[True, False])
        return [summary.columns.tolist()] + summary.values.tolist()

    print(f"Dash app created with server: {dash_app.server}")
    return dash_app                