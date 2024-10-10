from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from services.transaction_service import get_properties_for_user

dashboards_bp = Blueprint('dashboards', __name__)

@dashboards_bp.route('/dashboards')
@login_required
def dashboards():
    properties = get_properties_for_user(current_user.id, current_user.name)
    return render_template('main/dashboards.html', properties=properties)

@dashboards_bp.route('/dashboards/amortization/')
@login_required
def amortization_dash():
    return current_app.amortization_dash.index()