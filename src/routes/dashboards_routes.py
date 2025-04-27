"""
Dashboard routes for the REI-Tracker application.

This module provides routes for accessing the various dashboards in the application,
including portfolio, amortization, and transactions dashboards.
"""

from flask import Blueprint, render_template, current_app
from flask_login import login_required

# Create blueprint
blueprint = Blueprint('dashboards', __name__, url_prefix='/dashboards')

@blueprint.route('/')
@login_required
def dashboards():
    """Landing page for dashboards section."""
    return render_template('dashboards/index.html')

@blueprint.route('/portfolio')
@login_required
def portfolio_view():
    """Portfolio overview page."""
    try:
        return render_template('dashboards/portfolio.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering portfolio view: {str(e)}")
        raise

@blueprint.route('/_dash/portfolio/<path:path>')
@login_required
def portfolio_dash(path=''):
    """Handle portfolio dashboard requests."""
    return current_app.portfolio_dash.index()
