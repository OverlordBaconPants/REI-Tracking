# routes/main.py

# Keep routes that are accessible to all authenticated users 
# (Main, Properties, Transactions, Dashboards)

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/main')
@login_required
def main():
    return render_template('main/main.html', name=current_user.name)

@main_bp.route('/properties')
@login_required
def properties():
    return render_template('main/properties.html')

@main_bp.route('/transactions')
@login_required
def transactions():
    return render_template('main/transactions.html')

@main_bp.route('/add_transactions', methods=['GET', 'POST'])
@login_required
def add_transactions():
    if request.method == 'POST':
        # Handle adding transaction
        flash('Transaction added successfully', 'success')
    return render_template('main/add_transactions.html')

@main_bp.route('/dashboards')
@login_required
def dashboards():
    return render_template('main/dashboards.html')