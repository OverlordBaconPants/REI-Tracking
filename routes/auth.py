# routes/auth.py

from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from __init__ import User
from services.user_service import get_user_by_email, create_user, update_user_password, verify_password
from services.transaction_service import get_properties_for_user  # Add this import
from utils.flash import flash_message
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class PasswordStrength(Enum):
    """Password strength levels"""
    WEAK = "weak"
    MEDIUM = "medium"
    STRONG = "strong"

@dataclass
class UserValidationResult:
    """Data class for validation results"""
    is_valid: bool
    errors: List[Tuple[str, str]]
    sanitized_data: Dict[str, Any]

class AuthValidator:
    """Validator for authentication-related data"""
    
    def __init__(self):
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        self.name_pattern = re.compile(r'^[a-zA-Z\s\-\']+$')
        
        # Password requirements
        self.min_password_length = 8
        self.max_password_length = 128
        self.require_special_char = True
        self.require_number = True
        self.require_uppercase = True
        self.require_lowercase = True
        
        # Name requirements
        self.min_name_length = 2
        self.max_name_length = 50
        
        self.errors: List[Tuple[str, str]] = []

    def validate_email(self, email: Optional[str]) -> str:
        """Validate email format"""
        if not email:
            self.errors.append(('email', 'Email is required'))
            return ''
            
        email = email.strip().lower()
        
        if not self.email_pattern.match(email):
            self.errors.append(('email', 'Invalid email format'))
            return ''
            
        if len(email) > 255:
            self.errors.append(('email', 'Email is too long'))
            return ''
            
        return email

    def validate_password(self, password: Optional[str], field_name: str = 'password') -> str:
        """Validate password strength and format"""
        if not password:
            self.errors.append((field_name, 'Password is required'))
            return ''
            
        if len(password) < self.min_password_length:
            self.errors.append((field_name, 
                f'Password must be at least {self.min_password_length} characters long'))
            return ''
            
        if len(password) > self.max_password_length:
            self.errors.append((field_name,
                f'Password must be less than {self.max_password_length} characters long'))
            return ''
            
        if self.require_special_char and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            self.errors.append((field_name, 'Password must contain at least one special character'))
            
        if self.require_number and not re.search(r'\d', password):
            self.errors.append((field_name, 'Password must contain at least one number'))
            
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            self.errors.append((field_name, 'Password must contain at least one uppercase letter'))
            
        if self.require_lowercase and not re.search(r'[a-z]', password):
            self.errors.append((field_name, 'Password must contain at least one lowercase letter'))
            
        return password if not self.errors else ''

    def check_password_strength(self, password: str) -> PasswordStrength:
            """Check password strength"""
            score = 0
            
            # Length check
            if len(password) >= 12:
                score += 2
            elif len(password) >= 8:
                score += 1
                
            # Complexity checks
            if re.search(r'[A-Z]', password): score += 1
            if re.search(r'[a-z]', password): score += 1
            if re.search(r'\d', password): score += 1
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 1
            
            # Additional complexity
            if re.search(r'[^A-Za-z0-9]', password): score += 1
            if len(set(password)) >= 8: score += 1
            
            # Determine strength
            if score >= 6:
                return PasswordStrength.STRONG
            elif score >= 4:
                return PasswordStrength.MEDIUM
            else:
                return PasswordStrength.WEAK

    def validate_name(self, name: Optional[str], field_name: str) -> str:
        """Validate name format"""
        if not name:
            self.errors.append((field_name, f'{field_name.title()} is required'))
            return ''
            
        name = name.strip()
        
        if len(name) < self.min_name_length:
            self.errors.append((field_name, 
                f'{field_name.title()} must be at least {self.min_name_length} characters long'))
            return ''
            
        if len(name) > self.max_name_length:
            self.errors.append((field_name,
                f'{field_name.title()} must be less than {self.max_name_length} characters long'))
            return ''
            
        if not self.name_pattern.match(name):
            self.errors.append((field_name, 
                f'{field_name.title()} can only contain letters, spaces, hyphens, and apostrophes'))
            return ''
            
        return name

    def validate_phone(self, phone: Optional[str]) -> str:
        """Validate phone number format"""
        if not phone:
            return ''  # Phone is optional
            
        phone = re.sub(r'[^\d+]', '', phone)
        
        if not self.phone_pattern.match(phone):
            self.errors.append(('phone', 'Invalid phone number format'))
            return ''
            
        return phone

    def validate_signup_data(self, data: Dict[str, Any]) -> UserValidationResult:
        """Validate signup form data"""
        self.errors = []
        sanitized = {}
        
        # Basic field validation
        sanitized['email'] = self.validate_email(data.get('email'))
        sanitized['first_name'] = self.validate_name(data.get('first_name'), 'first_name')
        sanitized['last_name'] = self.validate_name(data.get('last_name'), 'last_name')
        sanitized['phone'] = self.validate_phone(data.get('phone'))
        sanitized['password'] = self.validate_password(data.get('password'))
        
        # Confirm password validation
        confirm_password = data.get('confirm_password')
        if not confirm_password:
            self.errors.append(('confirm_password', 'Confirm password is required'))
        elif confirm_password != data.get('password'):
            self.errors.append(('confirm_password', 'Passwords do not match'))
        
        # Password strength check
        if sanitized['password']:
            strength = self.check_password_strength(sanitized['password'])
            if strength == PasswordStrength.WEAK:
                self.errors.append(('password', 
                    'Password is too weak. Please include a mix of uppercase, lowercase, '
                    'numbers, and special characters.'
                ))
        
        # Combine names if both are valid
        if sanitized['first_name'] and sanitized['last_name']:
            sanitized['name'] = f"{sanitized['first_name']} {sanitized['last_name']}"
        
        return UserValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            sanitized_data=sanitized
        )

    def validate_login_data(self, data: Dict[str, Any]) -> UserValidationResult:
        """Validate login form data"""
        self.errors = []
        sanitized = {}
        
        sanitized['email'] = self.validate_email(data.get('email'))
        
        # For login, we don't need to check password strength, just presence
        password = data.get('password')
        if not password:
            self.errors.append(('password', 'Password is required'))
            sanitized['password'] = ''
        else:
            sanitized['password'] = password
            
        # Handle remember me checkbox
        sanitized['remember'] = bool(data.get('remember'))
        
        return UserValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            sanitized_data=sanitized
        )

    def validate_password_reset_data(self, data: Dict[str, Any]) -> UserValidationResult:
        """Validate password reset form data"""
        self.errors = []
        sanitized = {}
        
        sanitized['email'] = self.validate_email(data.get('email'))
        sanitized['password'] = self.validate_password(data.get('password'))
        
        # Confirm password validation
        confirm_password = data.get('confirm_password')
        if not confirm_password:
            self.errors.append(('confirm_password', 'Confirm password is required'))
        elif confirm_password != data.get('password'):
            self.errors.append(('confirm_password', 'Passwords do not match'))
            
        # Password strength check
        if sanitized['password']:
            strength = self.check_password_strength(sanitized['password'])
            if strength == PasswordStrength.WEAK:
                self.errors.append(('password', 
                    'Password is too weak. It should include uppercase, lowercase, '
                    'numbers, and special characters.'
                ))
        
        return UserValidationResult(
            is_valid=len(self.errors) == 0,
            errors=self.errors,
            sanitized_data=sanitized
        )

# Initialize validator
validator = AuthValidator()

def handle_validation_errors(errors: List[Tuple[str, str]]) -> None:
    """Helper function to flash validation errors"""
    for field, message in errors:
        flash_message(f"{message}", 'error')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup with validation"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            # Validate form data
            validation_result = validator.validate_signup_data(request.form)
            
            if not validation_result.is_valid:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': validation_result.errors[0][1]  # Return first error message
                    }), 400
                handle_validation_errors(validation_result.errors)
                return render_template('signup.html', form_data=request.form)
            
            # Check if user already exists
            sanitized_data = validation_result.sanitized_data
            if get_user_by_email(sanitized_data['email']):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Email address already exists'
                    }), 400
                flash_message('Email address already exists', 'error')
                return render_template('signup.html', form_data=request.form)
            
            # Create user with sanitized data
            if create_user(
                email=sanitized_data['email'],
                name=sanitized_data['name'],
                password=sanitized_data['password'],
                phone=sanitized_data['phone']
            ):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': 'Account created successfully. Redirecting to login...',
                        'redirect': url_for('auth.login')
                    })
                flash_message('Account created successfully. Please log in.', 'success')
                return redirect(url_for('auth.login'))
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'An error occurred during account creation.'
                    }), 500
                flash_message('An error occurred during account creation.', 'error')
                return render_template('signup.html', form_data=request.form)
                
        except Exception as e:
            logger.error(f"Error during signup: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'An unexpected error occurred. Please try again.'
                }), 500
            flash_message('An unexpected error occurred. Please try again.', 'error')
            return render_template('signup.html', form_data=request.form)
    
    # GET request - render the signup form
    return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.main'))

    if request.method == 'POST':
        try:
            # Validate login data
            validation_result = validator.validate_login_data(request.form)
            
            if not validation_result.is_valid:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': validation_result.errors[0][1]  # Return first error message
                    }), 400
                handle_validation_errors(validation_result.errors)
                return render_template('login.html', form_data=request.form)
            
            sanitized_data = validation_result.sanitized_data
            user_data = get_user_by_email(sanitized_data['email'])
            
            if not user_data or not verify_password(user_data['password'], sanitized_data['password']):
                logger.warning(f"Invalid login attempt for user: {sanitized_data['email']}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Invalid email or password.'
                    }), 401
                flash_message('Invalid email or password.', 'error')
                return render_template('login.html', form_data=request.form)
            
            try:
                user = User(
                    id=user_data['email'],
                    email=user_data['email'],
                    name=user_data['name'],
                    password=user_data['password'],
                    role=user_data.get('role', 'User')
                )
                
                login_user(user, remember=sanitized_data['remember'])
                logger.info(f"User logged in successfully: {user.email}")
                
                # Check if user has properties
                try:
                    user_properties = get_properties_for_user(
                        user_id=user.email,
                        user_name=user.name
                    )
                    
                    logger.debug(f"Found {len(user_properties)} properties for user {user.name}")
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        redirect_url = url_for('main.main') if user_properties else url_for('main.index')
                        return jsonify({
                            'success': True,
                            'message': 'Logged in successfully.',
                            'redirect': redirect_url
                        })
                    
                    flash_message('Logged in successfully.', 'success')
                    
                    if user_properties:
                        return redirect(url_for('main.main'))
                    else:
                        logger.info(f"User {user.name} has no properties, redirecting to welcome page")
                        return redirect(url_for('main.index'))
                        
                except Exception as e:
                    logger.error(f"Error checking user properties: {str(e)}")
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'success': True,
                            'message': 'Logged in successfully.',
                            'redirect': url_for('main.main')
                        })
                    return redirect(url_for('main.main'))
                
            except Exception as e:
                logger.error(f"Error during login process: {str(e)}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'An error occurred during login.'
                    }), 500
                flash_message('An error occurred during login.', 'error')
                return render_template('login.html', form_data=request.form)
                
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'An unexpected error occurred.'
                }), 500
            flash_message('An unexpected error occurred.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset with validation"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            # Validate password reset data
            validation_result = validator.validate_password_reset_data(request.form)
            
            if not validation_result.is_valid:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': validation_result.errors[0][1]  # Return first error message
                    }), 400
                handle_validation_errors(validation_result.errors)
                return render_template('forgot_password.html', form_data=request.form)
            
            sanitized_data = validation_result.sanitized_data
            user_data = get_user_by_email(sanitized_data['email'])
            
            if not user_data:
                logger.warning(f"Password reset attempted for non-existent email: {sanitized_data['email']}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'If an account exists with this email, you will receive reset instructions.'
                    }), 400
                flash_message(
                    'If an account exists with this email, you will receive reset instructions.', 
                    'info'
                )
                return render_template('forgot_password.html', form_data=request.form)
            
            # Update password
            if update_user_password(sanitized_data['email'], sanitized_data['password']):
                logger.info(f"Password reset successful for user: {sanitized_data['email']}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': 'Password has been reset successfully. Redirecting to login...',
                        'redirect': url_for('auth.login')
                    })
                flash_message(
                    'Password has been reset successfully. Please log in with your new password.', 
                    'success'
                )
                return redirect(url_for('auth.login'))
            else:
                logger.error(f"Password reset failed for user: {sanitized_data['email']}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'An error occurred during password reset. Please try again.'
                    }), 500
                flash_message(
                    'An error occurred during password reset. Please try again.', 
                    'error'
                )
                return render_template('forgot_password.html', form_data=request.form)
                
        except Exception as e:
            logger.error(f"Error during password reset: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'An unexpected error occurred. Please try again.'
                }), 500
            flash_message('An unexpected error occurred. Please try again.', 'error')
            return render_template('forgot_password.html', form_data=request.form)
    
    return render_template('forgot_password.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    try:
        current_email = current_user.email
        logout_user()
        logger.info(f"User logged out successfully: {current_email}")
        flash_message('You have been logged out successfully.', 'success')
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        flash_message('An error occurred during logout.', 'error')
    
    return redirect(url_for('main.index'))

# Security headers
@auth_bp.after_request
def add_security_headers(response):
    """Add security headers to all authentication responses"""
    csp = "; ".join([
        # Default fallback
        "default-src 'self'",
        
        # Script sources
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://code.jquery.com "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com",
        
        # Style sources
        "style-src 'self' 'unsafe-inline' "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com",
        
        # Font sources
        "font-src 'self' "
        "https://cdn.jsdelivr.net "
        "https://cdnjs.cloudflare.com",
        
        # Image sources
        "img-src 'self' data: https:",
        
        # Connect sources
        "connect-src 'self'",
        
        # Object sources
        "object-src 'none'",
        
        # Media sources
        "media-src 'self'",
        
        # Frame sources
        "frame-src 'self'"
    ])
    
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': csp,
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    })
    return response

# Error handlers
@auth_bp.errorhandler(400)
def bad_request_error(error):
    """Handle bad request errors"""
    logger.warning(f"Bad request error: {str(error)}")
    return render_template('errors/400.html'), 400

@auth_bp.errorhandler(404)
def not_found_error(error):
    """Handle not found errors"""
    logger.warning(f"Not found error: {str(error)}")
    return render_template('errors/404.html'), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('errors/500.html'), 500
    
