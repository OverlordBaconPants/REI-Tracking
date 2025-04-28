"""
KPI dashboard for the REI-Tracker application.

This module provides a Dash-based interactive dashboard for visualizing
key performance indicators (KPIs) for properties, including NOI, cap rate,
cash-on-cash return, and DSCR, with comparison to projected values.
"""

from typing import Dict, List, Optional, Tuple, Union, Any
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from flask_login import current_user
import traceback
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging

from src.services.property_financial_service import get_properties_for_user, PropertyFinancialService
from src.utils.money import Money
from src.utils.logging_utils import get_logger
from src.utils.common import safe_float, format_address
from src.utils.dash_helpers import (
    create_responsive_chart, 
    create_metric_card, 
    update_chart_layouts_for_mobile, 
    create_empty_response
)

# Set up module-level logger
logger = get_logger(__name__)

# Mobile breakpoint constants
MOBILE_BREAKPOINT = 768
MOBILE_HEIGHT = '100vh'
DESKTOP_HEIGHT = 'calc(100vh - 150px)'

def create_kpi_dash(flask_app) -> dash.Dash:
    """
    Create the KPI dashboard application.
    
    Args:
        flask_app: Flask application instance
        
    Returns:
        dash.Dash: Configured Dash application instance
    """
    try:
        logger.info("Creating KPI dashboard")
        
        # Initialize Dash app
        dash_app = dash.Dash(
            __name__,
            server=flask_app,
            routes_pathname_prefix='/dashboards/_dash/kpi/',
            requests_pathname_prefix='/dashboards/_dash/kpi/',
            external_stylesheets=[dbc.themes.BOOTSTRAP]
        )
        
        logger.debug("Dash app initialized successfully")

        # Define layout with responsive design
        dash_app.layout = dbc.Container([
            # Responsive viewport meta tag
            html.Meta(name="viewport", content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"),
            
            dcc.Store(id='session-store'),
            dcc.Store(id='viewport-size'),  # Store for tracking viewport size
            
            # Error display
            html.Div(id="error-display", className="alert alert-danger d-none"),
            
            # Property selector card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Select Property", className="bg-navy text-white"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='property-selector',
                                placeholder='Select Property',
                                className='mb-3',
                                style={'width': '100%'}
                            )
                        ])
                    ], className="mb-4 shadow-sm")
                ], xs=12, md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Analysis Comparison", className="bg-navy text-white"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id='analysis-selector',
                                placeholder='Select Analysis',
                                className='mb-3',
                                style={'width': '100%'}
                            )
                        ])
                    ], className="mb-4 shadow-sm")
                ], xs=12, md=6)
            ]),
            
            # Property information card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Property Information", className="bg-navy text-white"),
                        dbc.CardBody(id='property-info')
                    ], className="mb-4 shadow-sm")
                ], xs=12)
            ]),
            
            # KPI metrics card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("KPI Metrics", className="bg-navy text-white"),
                        dbc.CardBody(id='kpi-metrics')
                    ], className="mb-4 shadow-sm")
                ], xs=12)
            ]),
            
            # Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Income vs. Expenses", className="bg-navy text-white"),
                        dbc.CardBody([
                            html.Div(id='income-expense-chart', className="chart-container")
                        ])
                    ], className="mb-4 shadow-sm")
                ], xs=12, md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("NOI and Cash Flow", className="bg-navy text-white"),
                        dbc.CardBody([
                            html.Div(id='noi-cashflow-chart', className="chart-container")
                        ])
                    ], className="mb-4 shadow-sm")
                ], xs=12, md=6)
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Investment Metrics", className="bg-navy text-white"),
                        dbc.CardBody([
                            html.Div(id='metrics-chart', className="chart-container")
                        ])
                    ], className="mb-4 shadow-sm")
                ], xs=12)
            ]),
            
            # Data quality info
            dbc.Row([
                dbc.Col([
                    html.Div(id='data-quality-info')
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
            
            # Get window width from client side
            width = dash.no_update
            try:
                width = int(window.innerWidth)
            except:
                pass
            
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
                    'label': format_address(prop['address'], 'display'),
                    'value': prop['id']
                } for prop in properties]
                
                return options
                
            except Exception as e:
                logger.error(f"Error populating property dropdown: {str(e)}")
                logger.error(f"Exception details: {traceback.format_exc()}")
                return []

        @dash_app.callback(
            Output('analysis-selector', 'options'),
            [Input('property-selector', 'value')]
        )
        def populate_analysis_dropdown(property_id):
            """Populate the analysis dropdown with available analyses for the selected property."""
            try:
                if not property_id:
                    return []
                
                with flask_app.app_context():
                    # Check if current_user is authenticated and has necessary attributes
                    if hasattr(current_user, 'id') and hasattr(current_user, 'name'):
                        property_financial_service = PropertyFinancialService()
                        comparison_data = property_financial_service.compare_actual_to_projected(
                            property_id, 
                            current_user.id
                        )
                    else:
                        logger.warning("User not authenticated or missing attributes")
                        return []
                
                if not comparison_data or 'available_analyses' not in comparison_data:
                    return []
                
                analyses = comparison_data.get('available_analyses', [])
                
                options = [{'label': 'None (Actual Only)', 'value': 'none'}]
                options.extend([{
                    'label': analysis.get('name', f"Analysis {i+1}"),
                    'value': analysis.get('id')
                } for i, analysis in enumerate(analyses)])
                
                return options
                
            except Exception as e:
                logger.error(f"Error populating analysis dropdown: {str(e)}")
                logger.error(f"Exception details: {traceback.format_exc()}")
                return []

        @dash_app.callback(
            [Output('property-info', 'children'),
             Output('kpi-metrics', 'children'),
             Output('income-expense-chart', 'children'),
             Output('noi-cashflow-chart', 'children'),
             Output('metrics-chart', 'children'),
             Output('error-display', 'children'),
             Output('error-display', 'style')],
            [Input('property-selector', 'value'),
             Input('analysis-selector', 'value'),
             Input('viewport-size', 'data')]
        )
        def update_kpi_dashboard(property_id, analysis_id, viewport):
            """Update all KPI dashboard components based on selected property and analysis."""
            try:
                # Get device type
                is_mobile = viewport.get('is_mobile', True) if viewport else True
                
                if not property_id:
                    return create_empty_response("No property selected")

                with flask_app.app_context():
                    # Check if current_user is authenticated and has necessary attributes
                    if hasattr(current_user, 'id') and hasattr(current_user, 'name'):
                        property_financial_service = PropertyFinancialService()
                        
                        # Get KPI data
                        if analysis_id and analysis_id != 'none':
                            comparison_data = property_financial_service.compare_actual_to_projected(
                                property_id, 
                                current_user.id,
                                analysis_id=analysis_id
                            )
                        else:
                            # Get actual metrics only
                            metrics = property_financial_service.calculate_cash_flow_metrics(
                                property_id, 
                                current_user.id
                            )
                            comparison_data = {
                                'property_id': property_id,
                                'actual_metrics': metrics,
                                'projected_metrics': None,
                                'comparison': None
                            }
                    else:
                        logger.warning("User not authenticated or missing attributes")
                        return create_empty_response("User authentication required")
                
                if not comparison_data:
                    return create_empty_response("No KPI data available for this property")

                # Create mobile-optimized components
                property_info = create_property_info(comparison_data, is_mobile)
                kpi_metrics = create_kpi_metrics(comparison_data, is_mobile)
                
                # Create charts
                income_expense_chart = create_income_expense_chart(comparison_data, is_mobile)
                noi_cashflow_chart = create_noi_cashflow_chart(comparison_data, is_mobile)
                metrics_chart = create_metrics_chart(comparison_data, is_mobile)

                # Create data quality info
                data_quality_info = create_data_quality_info(comparison_data)

                return (
                    property_info,
                    kpi_metrics,
                    create_responsive_chart(income_expense_chart, 'income-expense'),
                    create_responsive_chart(noi_cashflow_chart, 'noi-cashflow'),
                    create_responsive_chart(metrics_chart, 'metrics'),
                    "",
                    {'display': 'none'}
                )

            except Exception as e:
                logger.error(f"Error in update_kpi_dashboard: {str(e)}")
                logger.error(traceback.format_exc())
                return create_empty_response(f"An error occurred: {str(e)}")

        def create_property_info(comparison_data, is_mobile):
            """Create mobile-optimized property information display."""
            try:
                address = comparison_data.get('address', 'Unknown')
                
                # Get analysis details if available
                analysis_details = comparison_data.get('analysis_details', {})
                analysis_name = analysis_details.get('name', 'N/A')
                analysis_type = analysis_details.get('type', 'N/A')
                
                # Create responsive layout
                if is_mobile:
                    return html.Div([
                        html.H5(format_address(address, 'display'), className="mb-3"),
                        html.Div([
                            html.P(f"Analysis: {analysis_name}", className="mb-2") if analysis_name != 'N/A' else None,
                            html.P(f"Type: {analysis_type}", className="mb-2") if analysis_type != 'N/A' else None
                        ], className="small")
                    ])
                else:
                    return html.Div([
                        html.H5(format_address(address, 'display'), className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.P(f"Analysis: {analysis_name}", className="mb-2") if analysis_name != 'N/A' else None,
                            ], xs=12, md=6),
                            dbc.Col([
                                html.P(f"Type: {analysis_type}", className="mb-2") if analysis_type != 'N/A' else None,
                            ], xs=12, md=6)
                        ])
                    ])
            except Exception as e:
                logger.error(f"Error creating property info: {str(e)}")
                return html.Div("Error loading property information", className="text-danger")

        def create_kpi_metrics(comparison_data, is_mobile):
            """Create mobile-optimized KPI metrics display."""
            try:
                # Get actual metrics
                actual_metrics = comparison_data.get('actual_metrics', {})
                
                # Get projected metrics if available
                projected_metrics = comparison_data.get('projected_metrics', {})
                
                # Get comparison data if available
                comparison = comparison_data.get('comparison', {})
                
                # Extract metrics
                monthly_income = safe_float(actual_metrics.get('total_income', {}).get('monthly', 0))
                monthly_expenses = safe_float(actual_metrics.get('total_expenses', {}).get('monthly', 0))
                monthly_noi = safe_float(actual_metrics.get('net_operating_income', {}).get('monthly', 0))
                monthly_cash_flow = safe_float(actual_metrics.get('cash_flow', {}).get('monthly', 0))
                cap_rate = safe_float(actual_metrics.get('cap_rate', 0))
                cash_on_cash = safe_float(actual_metrics.get('cash_on_cash_return', 0))
                dscr = safe_float(actual_metrics.get('debt_service_coverage_ratio', 0))
                
                # Create metrics cards
                if is_mobile:
                    return dbc.Row([
                        dbc.Col([create_metric_card("Monthly NOI", "noi-metric", "text-success")], xs=12, className="mb-2"),
                        dbc.Col([
                            html.Div([
                                html.H3(f"${monthly_noi:,.2f}", className="text-success text-center")
                            ])
                        ], xs=12, className="mb-3"),
                        
                        dbc.Col([create_metric_card("Monthly Cash Flow", "cash-flow-metric", "text-primary")], xs=12, className="mb-2"),
                        dbc.Col([
                            html.Div([
                                html.H3(f"${monthly_cash_flow:,.2f}", className="text-primary text-center")
                            ])
                        ], xs=12, className="mb-3"),
                        
                        dbc.Col([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H5("Cap Rate", className="text-center"),
                                        html.H4(f"{cap_rate:.2f}%", className="text-center")
                                    ])
                                ], xs=4),
                                dbc.Col([
                                    html.Div([
                                        html.H5("Cash on Cash", className="text-center"),
                                        html.H4(f"{cash_on_cash:.2f}%", className="text-center")
                                    ])
                                ], xs=4),
                                dbc.Col([
                                    html.Div([
                                        html.H5("DSCR", className="text-center"),
                                        html.H4(f"{dscr:.2f}", className="text-center")
                                    ])
                                ], xs=4)
                            ])
                        ], xs=12)
                    ])
                else:
                    return dbc.Row([
                        dbc.Col([
                            html.Div([
                                html.H5("Monthly Income", className="text-center"),
                                html.H3(f"${monthly_income:,.2f}", className="text-success text-center")
                            ])
                        ], xs=12, md=3),
                        dbc.Col([
                            html.Div([
                                html.H5("Monthly Expenses", className="text-center"),
                                html.H3(f"${monthly_expenses:,.2f}", className="text-danger text-center")
                            ])
                        ], xs=12, md=3),
                        dbc.Col([
                            html.Div([
                                html.H5("Monthly NOI", className="text-center"),
                                html.H3(f"${monthly_noi:,.2f}", className="text-success text-center")
                            ])
                        ], xs=12, md=3),
                        dbc.Col([
                            html.Div([
                                html.H5("Monthly Cash Flow", className="text-center"),
                                html.H3(f"${monthly_cash_flow:,.2f}", className="text-primary text-center")
                            ])
                        ], xs=12, md=3),
                        
                        dbc.Col([
                            html.Div([
                                html.H5("Cap Rate", className="text-center"),
                                html.H3(f"{cap_rate:.2f}%", className="text-center")
                            ])
                        ], xs=12, md=4, className="mt-4"),
                        dbc.Col([
                            html.Div([
                                html.H5("Cash on Cash Return", className="text-center"),
                                html.H3(f"{cash_on_cash:.2f}%", className="text-center")
                            ])
                        ], xs=12, md=4, className="mt-4"),
                        dbc.Col([
                            html.Div([
                                html.H5("DSCR", className="text-center"),
                                html.H3(f"{dscr:.2f}", className="text-center")
                            ])
                        ], xs=12, md=4, className="mt-4")
                    ])
            except Exception as e:
                logger.error(f"Error creating KPI metrics: {str(e)}")
                return html.Div("Error loading KPI metrics", className="text-danger")

        def create_income_expense_chart(comparison_data, is_mobile):
            """Create income vs. expenses chart."""
            try:
                # Get actual metrics
                actual_metrics = comparison_data.get('actual_metrics', {})
                
                # Get projected metrics if available
                projected_metrics = comparison_data.get('projected_metrics', {})
                
                # Extract data
                actual_income = safe_float(actual_metrics.get('total_income', {}).get('monthly', 0))
                actual_expenses = safe_float(actual_metrics.get('total_expenses', {}).get('monthly', 0))
                
                projected_income = safe_float(projected_metrics.get('total_income', {}).get('monthly', 0)) if projected_metrics else None
                projected_expenses = safe_float(projected_metrics.get('total_expenses', {}).get('monthly', 0)) if projected_metrics else None
                
                # Create figure
                fig = go.Figure()
                
                # Set up bar positions
                bar_width = 0.35
                x = [0, 1]  # Positions for income and expenses
                
                # Add actual bars
                fig.add_trace(go.Bar(
                    x=['Income', 'Expenses'],
                    y=[actual_income, actual_expenses],
                    name='Actual',
                    marker_color='#0047AB',  # Navy blue
                    text=[f"${actual_income:,.0f}", f"${actual_expenses:,.0f}"],
                    textposition='auto'
                ))
                
                # Add projected bars if available
                if projected_income is not None and projected_expenses is not None:
                    fig.add_trace(go.Bar(
                        x=['Income', 'Expenses'],
                        y=[projected_income, projected_expenses],
                        name='Projected',
                        marker_color='#4285F4',  # Light blue
                        text=[f"${projected_income:,.0f}", f"${projected_expenses:,.0f}"],
                        textposition='auto'
                    ))
                
                # Update layout
                fig.update_layout(
                    title=None,
                    xaxis_title=None,
                    yaxis_title='Amount ($)',
                    barmode='group',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Format y-axis as currency
                fig.update_yaxes(tickprefix='$', tickformat=',')
                
                # Update layout for mobile if needed
                if is_mobile:
                    update_chart_layouts_for_mobile(fig, is_mobile)
                
                return fig
                
            except Exception as e:
                logger.error(f"Error creating income expense chart: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="Error creating chart",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color='red')
                )
                return empty_fig

        def create_noi_cashflow_chart(comparison_data, is_mobile):
            """Create NOI and cash flow chart."""
            try:
                # Get actual metrics
                actual_metrics = comparison_data.get('actual_metrics', {})
                
                # Get projected metrics if available
                projected_metrics = comparison_data.get('projected_metrics', {})
                
                # Extract data
                actual_noi = safe_float(actual_metrics.get('net_operating_income', {}).get('monthly', 0))
                actual_cashflow = safe_float(actual_metrics.get('cash_flow', {}).get('monthly', 0))
                
                projected_noi = safe_float(projected_metrics.get('net_operating_income', {}).get('monthly', 0)) if projected_metrics else None
                projected_cashflow = safe_float(projected_metrics.get('cash_flow', {}).get('monthly', 0)) if projected_metrics else None
                
                # Create figure
                fig = go.Figure()
                
                # Add actual bars
                fig.add_trace(go.Bar(
                    x=['NOI', 'Cash Flow'],
                    y=[actual_noi, actual_cashflow],
                    name='Actual',
                    marker_color='#0047AB',  # Navy blue
                    text=[f"${actual_noi:,.0f}", f"${actual_cashflow:,.0f}"],
                    textposition='auto'
                ))
                
                # Add projected bars if available
                if projected_noi is not None and projected_cashflow is not None:
                    fig.add_trace(go.Bar(
                        x=['NOI', 'Cash Flow'],
                        y=[projected_noi, projected_cashflow],
                        name='Projected',
                        marker_color='#4285F4',  # Light blue
                        text=[f"${projected_noi:,.0f}", f"${projected_cashflow:,.0f}"],
                        textposition='auto'
                    ))
                
                # Update layout
                fig.update_layout(
                    title=None,
                    xaxis_title=None,
                    yaxis_title='Amount ($)',
                    barmode='group',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Format y-axis as currency
                fig.update_yaxes(tickprefix='$', tickformat=',')
                
                # Update layout for mobile if needed
                if is_mobile:
                    update_chart_layouts_for_mobile(fig, is_mobile)
                
                return fig
                
            except Exception as e:
                logger.error(f"Error creating NOI cash flow chart: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="Error creating chart",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color='red')
                )
                return empty_fig

        def create_metrics_chart(comparison_data, is_mobile):
            """Create investment metrics chart."""
            try:
                # Get actual metrics
                actual_metrics = comparison_data.get('actual_metrics', {})
                
                # Get projected metrics if available
                projected_metrics = comparison_data.get('projected_metrics', {})
                
                # Extract data
                metrics = []
                actual_values = []
                projected_values = []
                
                # Cap Rate
                if 'cap_rate' in actual_metrics:
                    metrics.append('Cap Rate')
                    actual_values.append(safe_float(actual_metrics.get('cap_rate', 0)))
                    if projected_metrics and 'cap_rate' in projected_metrics:
                        projected_values.append(safe_float(projected_metrics.get('cap_rate', 0)))
                
                # Cash on Cash Return
                if 'cash_on_cash_return' in actual_metrics:
                    metrics.append('Cash on Cash')
                    actual_values.append(safe_float(actual_metrics.get('cash_on_cash_return', 0)))
                    if projected_metrics and 'cash_on_cash_return' in projected_metrics:
                        projected_values.append(safe_float(projected_metrics.get('cash_on_cash_return', 0)))
                
                # DSCR
                if 'debt_service_coverage_ratio' in actual_metrics:
                    metrics.append('DSCR')
                    actual_values.append(safe_float(actual_metrics.get('debt_service_coverage_ratio', 0)))
                    if projected_metrics and 'debt_service_coverage_ratio' in projected_metrics:
                        projected_values.append(safe_float(projected_metrics.get('debt_service_coverage_ratio', 0)))
                
                # Create figure
                fig = go.Figure()
                
                # Add actual bars
                fig.add_trace(go.Bar(
                    x=metrics,
                    y=actual_values,
                    name='Actual',
                    marker_color='#0047AB',  # Navy blue
                    text=[f"{val:.2f}" + ("%" if metric != 'DSCR' else "") for val, metric in zip(actual_values, metrics)],
                    textposition='auto'
                ))
                
                # Add projected bars if available
                if projected_metrics and len(projected_values) == len(metrics):
                    fig.add_trace(go.Bar(
                        x=metrics,
                        y=projected_values,
                        name='Projected',
                        marker_color='#4285F4',  # Light blue
                        text=[f"{val:.2f}" + ("%" if metric != 'DSCR' else "") for val, metric in zip(projected_values, metrics)],
                        textposition='auto'
                    ))
                
                # Update layout
                fig.update_layout(
                    title=None,
                    xaxis_title=None,
                    yaxis_title='Value',
                    barmode='group',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Update layout for mobile if needed
                if is_mobile:
                    update_chart_layouts_for_mobile(fig, is_mobile)
                
                return fig
                
            except Exception as e:
                logger.error(f"Error creating metrics chart: {str(e)}")
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="Error creating chart",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color='red')
                )
                return empty_fig
                
        def create_data_quality_info(comparison_data):
            """Create data quality information display."""
            try:
                # Get metadata from actual metrics
                actual_metrics = comparison_data.get('actual_metrics', {})
                metadata = actual_metrics.get('metadata', {})
                
                if not metadata:
                    return html.Div()  # Return empty div if no metadata
                
                # Get data quality info
                has_complete_history = metadata.get('has_complete_history', False)
                confidence_level = metadata.get('data_quality', {}).get('confidence_level', 'low')
                refinance_info = metadata.get('data_quality', {}).get('refinance_info', {})
                
                # Create alert with data quality info
                alert_color = 'success' if confidence_level == 'high' else 'warning' if confidence_level == 'medium' else 'danger'
                
                content = []
                
                # Add data completeness info
                if has_complete_history:
                    content.append(html.P("Data Quality: Complete transaction history available", className="mb-1"))
                else:
                    content.append(html.P("Data Quality Warning: Incomplete transaction history", className="mb-1"))
                
                # Add confidence level
                content.append(html.P(f"Confidence Level: {confidence_level.capitalize()}", className="mb-1"))
                
                # Add refinance info if available
                if refinance_info and refinance_info.get('has_refinanced', False):
                    content.append(html.P("Refinance detected: Metrics may be affected by refinancing", className="mb-1"))
                
                return dbc.Alert(
                    content,
                    color=alert_color,
                    className="mt-3",
                    dismissable=True
                )
                
            except Exception as e:
                logger.error(f"Error creating data quality info: {str(e)}")
                return html.Div()  # Return empty div on error

        return dash_app
        
    except Exception as e:
        logger.error(f"Error creating KPI dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        raise
