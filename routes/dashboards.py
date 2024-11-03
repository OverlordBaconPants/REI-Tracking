from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from services.transaction_service import get_properties_for_user
import json

dashboards_bp = Blueprint('dashboards', __name__)

@dashboards_bp.route('/dashboards')
@login_required
def dashboards():
    """Landing page for dashboards section"""
    return render_template('main/dashboards.html')

@dashboards_bp.route('/dashboards/portfolio/view')
@login_required
def portfolio_view():
    """Portfolio overview page"""
    try:
        dash_app = current_app.portfolio_dash
        return render_template(
            'main/portfolio.html',
            dash_app=dash_app
        )
    except Exception as e:
        current_app.logger.error(f"Error rendering portfolio view: {str(e)}")
        raise

@dashboards_bp.route('/dashboards/amortization/view')
@login_required
def amortization_view():
    """Amortization schedule page"""
    try:
        dash_app = current_app.amortization_dash
        return render_template(
            'main/amortization.html',
            dash_app=dash_app
        )
    except Exception as e:
        current_app.logger.error(f"Error rendering amortization view: {str(e)}")
        raise

@dashboards_bp.route('/dashboards/_dash/amortization/<path:path>')
@login_required
def amortization_dash(path=''):
    """Handle amortization dashboard requests"""
    return current_app.amortization_dash.index()

@dashboards_bp.route('/dashboards/_dash/portfolio/<path:path>')
@login_required
def portfolio_dash(path=''):
    """Handle portfolio dashboard requests"""
    return current_app.portfolio_dash.index()