# routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import User
from services.user_service import get_user_by_email, create_user, update_user_password, hash_password, verify_password
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        user = get_user_by_email(email)
        if user:
            flash('Email address already exists', 'danger')
            return redirect(url_for('auth.signup'))
        
        if create_user(email, name, password):
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        logger.debug(f"Login attempt for email: {email}")
        
        user_data = get_user_by_email(email)
        if not user_data or not verify_password(user_data['password'], password):
            logger.warning(f"Invalid login attempt for user: {email}")
            flash('Please check your login details and try again.', 'danger')
        else:
            logger.debug(f"User found: {user_data}")
            try:
                user = User(
                    id=user_data['email'],
                    email=user_data['email'],
                    name=user_data['name'],
                    password=user_data['password'],
                    role=user_data.get('role', 'User')
                )
                login_user(user, remember=remember)
                logger.info(f"User logged in successfully: {email}")
                flash('Logged in successfully.', 'success')
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('main.main')
                logger.debug(f"Redirecting to: {next_page}")
                return redirect(next_page)
            except Exception as e:
                logger.error(f"Error during login process: {str(e)}")
                flash('An error occurred during login. Please try again.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        logger.debug(f"Password reset attempt for email: {email}")

        user_data = get_user_by_email(email)

        if not user_data:
            logger.warning(f"Email not found for password reset: {email}")
            flash('Email address not found. Please check and try again.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        if password != confirm_password:
            logger.warning(f"Passwords do not match for reset attempt: {email}")
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        # If all checks pass, update the user's password
        if update_user_password(email, password):
            logger.info(f"Password successfully reset for user: {email}")
            flash('Your password has been successfully reset. Please log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            logger.error(f"Error occurred while resetting password for user: {email}")
            flash('An error occurred while resetting your password. Please try again.', 'danger')
            return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')