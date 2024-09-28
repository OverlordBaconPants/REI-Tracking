# routes/admin.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from functools import wraps
import logging

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index')), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/properties')
@login_required
@admin_required
def properties():
    # Here you would typically fetch properties data
    # For now, we'll just render the template
    return render_template('admin/properties.html')

@admin_bp.route('/partners')
@login_required
@admin_required
def partners():
    # Here you would typically fetch partners data
    # For now, we'll just render the template
    return render_template('admin/partners.html')

@admin_bp.route('/transactions')
@login_required
@admin_required
def transactions():
    # Here you would typically fetch transactions data
    # For now, we'll just render the template
    return render_template('admin/transactions.html')

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    # Here you would typically fetch user data
    # For now, we'll just render the template
    return render_template('admin/users.html')

@admin_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        # Handle user creation
        # This is where you'd call your user service to create a new user
        flash('User created successfully', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/create_user.html')

@admin_bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    # Here you would fetch the user data and handle editing
    if request.method == 'POST':
        # Handle user update
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', user_id=user_id)

@admin_bp.route('/delete_user/<user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    # Handle user deletion
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.users'))