# routes/main.py

# Keep routes that are accessible to all authenticated users 
# (Main, Properties, Transactions, Dashboards)

from flask import Blueprint, render_template
from flask_login import login_required, current_user
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/main')
@login_required
def main():
    return render_template('main.html', name=current_user.name)

@main_bp.route('/properties')
@login_required
def properties():
    return render_template('properties.html')

@main_bp.route('/transactions')
@login_required
def transactions():
    return render_template('transactions.html')

@main_bp.route('/dashboards')
@login_required
def dashboards():
    return render_template('dashboards.html')