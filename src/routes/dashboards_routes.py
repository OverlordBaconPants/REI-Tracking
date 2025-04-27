"""
Dashboard routes for the REI-Tracker application.

This module provides routes for accessing the various dashboards in the application,
including portfolio, amortization, and transactions dashboards.
"""

from flask import Blueprint, render_template, current_app, redirect, url_for, request, session, g
from flask_login import login_required, current_user
import logging
from functools import wraps

from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Create blueprint
blueprint = Blueprint('dashboards', __name__, url_prefix='/dashboards')

def dashboard_access_required(f):
    """
    Decorator to require dashboard access for a route.
    
    This decorator checks if the user has access to dashboards based on their
    property access permissions.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is authenticated
        if not current_user.is_authenticated:
            logger.warning(f"Unauthenticated user attempted to access dashboard: {request.path}")
            return redirect(url_for('auth.login'))
        
        # Admins have access to all dashboards
        if current_user.is_admin():
            return f(*args, **kwargs)
        
        # Check if user has access to any properties
        if not current_user.get_accessible_properties():
            logger.warning(f"User {current_user.name} attempted to access dashboard without property access")
            return render_template('dashboards/no_access.html', 
                                  message="You don't have access to any properties. Please contact an administrator.")
        
        return f(*args, **kwargs)
    
    return decorated_function

@blueprint.route('/')
@login_required
@dashboard_access_required
def dashboards():
    """Landing page for dashboards section."""
    logger.info(f"User {current_user.name} accessed dashboards landing page")
    return render_template('dashboards/index.html')

@blueprint.route('/portfolio')
@login_required
@dashboard_access_required
def portfolio_view():
    """Portfolio overview page."""
    try:
        logger.info(f"User {current_user.name} accessed portfolio dashboard")
        return render_template('dashboards/portfolio.html')
    except Exception as e:
        logger.error(f"Error rendering portfolio view: {str(e)}")
        raise

@blueprint.route('/amortization')
@login_required
@dashboard_access_required
def amortization_view():
    """Amortization schedule page."""
    try:
        logger.info(f"User {current_user.name} accessed amortization dashboard")
        return render_template('dashboards/amortization.html')
    except Exception as e:
        logger.error(f"Error rendering amortization view: {str(e)}")
        return render_template('dashboards/coming_soon.html', 
                              dashboard_name="Amortization Dashboard")

@blueprint.route('/transactions')
@login_required
@dashboard_access_required
def transactions_view():
    """Transactions dashboard page."""
    try:
        logger.info(f"User {current_user.name} accessed transactions dashboard")
        return render_template('dashboards/transactions.html')
    except Exception as e:
        logger.error(f"Error rendering transactions view: {str(e)}")
        return render_template('dashboards/coming_soon.html', 
                              dashboard_name="Transactions Dashboard")

@blueprint.route('/kpi')
@login_required
@dashboard_access_required
def kpi_view():
    """KPI dashboard page."""
    try:
        logger.info(f"User {current_user.name} accessed KPI dashboard")
        return render_template('dashboards/kpi.html')
    except Exception as e:
        logger.error(f"Error rendering KPI view: {str(e)}")
        return render_template('dashboards/coming_soon.html', 
                              dashboard_name="KPI Dashboard")

@blueprint.route('/_dash/portfolio/<path:path>')
@login_required
@dashboard_access_required
def portfolio_dash(path=''):
    """Handle portfolio dashboard requests."""
    logger.debug(f"User {current_user.name} accessed portfolio dash component: {path}")
    return current_app.portfolio_dash.index()

@blueprint.route('/_dash/amortization/<path:path>')
@login_required
@dashboard_access_required
def amortization_dash(path=''):
    """Handle amortization dashboard requests."""
    logger.debug(f"User {current_user.name} accessed amortization dash component: {path}")
    if hasattr(current_app, 'amortization_dash'):
        return current_app.amortization_dash.index()
    return render_template('dashboards/coming_soon.html', 
                          dashboard_name="Amortization Dashboard")

@blueprint.route('/_dash/transactions/<path:path>')
@login_required
@dashboard_access_required
def transactions_dash(path=''):
    """Handle transactions dashboard requests."""
    logger.debug(f"User {current_user.name} accessed transactions dash component: {path}")
    if hasattr(current_app, 'transactions_dash'):
        return current_app.transactions_dash.index()
    return render_template('dashboards/coming_soon.html', 
                          dashboard_name="Transactions Dashboard")

@blueprint.route('/_dash/kpi/<path:path>')
@login_required
@dashboard_access_required
def kpi_dash(path=''):
    """Handle KPI dashboard requests."""
    logger.debug(f"User {current_user.name} accessed KPI dash component: {path}")
    if hasattr(current_app, 'kpi_dash'):
        return current_app.kpi_dash.index()
    return render_template('dashboards/coming_soon.html', 
                          dashboard_name="KPI Dashboard")
