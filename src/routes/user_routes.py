"""
User routes module for the REI-Tracker application.

This module provides the user routes for the application, including
authentication, registration, and user management.
"""

from flask import Blueprint, jsonify, request, session, make_response, g
import json
from typing import Dict, Any, Optional, Tuple
from passlib.hash import pbkdf2_sha256

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.validation_service import ModelValidator
from src.services.auth_service import AuthService
from src.utils.logging_utils import get_logger, audit_logger
from src.utils.validation_utils import ValidationResult

# Import ValidationService for tests
class ValidationService:
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        if not email or '@' not in email:
            return ValidationResult(is_valid=False, errors={'email': ['Invalid email format']})
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_model(model_class, data):
        """Validate model data."""
        validator = ModelValidator(model_class)
        return validator.validate(data)

# Set up logger
logger = get_logger(__name__)

# Create blueprint
blueprint = Blueprint('users', __name__, url_prefix='/api/users')

# Create repositories and services
user_repository = UserRepository()
auth_service = AuthService(user_repository)


# Add security headers to all responses
@blueprint.after_request
def add_security_headers(response):
    """
    Add security headers to all responses.
    
    Args:
        response: The response to add headers to
        
    Returns:
        The response with added headers
    """
    return auth_service.add_security_headers(response)

@blueprint.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Returns:
        The registration result
    """
    try:
        data = request.get_json()
        
        # Validate email
        email_validation = ValidationService.validate_email(data.get('email', ''))
        if not email_validation.is_valid:
            return jsonify({
                'success': False,
                'errors': email_validation.errors
            }), 400
        
        # Check if email already exists
        if user_repository.email_exists(data.get('email', '')):
            return jsonify({
                'success': False,
                'errors': {'email': ['Email already exists']}
            }), 400
        
        # Hash password
        data['password'] = pbkdf2_sha256.hash(data.get('password', ''))
        
        # Validate user data
        validation_result = ValidationService.validate_model(User, data)
        if not validation_result.is_valid:
            return jsonify({
                'success': False,
                'errors': validation_result.errors
            }), 400
        
        # Create user
        user = validation_result.data
        user_repository.create(user)
        
        # Log user creation
        audit_logger.log_user_action(
            user_id=user.id,
            action="create",
            resource_type="user",
            resource_id=user.id
        )
        
        # Return success
        return jsonify({
            'success': True,
            'user': user.dict()
        }), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({
            'success': False,
            'errors': {'_error': [str(e)]}
        }), 500


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in a user.
    
    Returns:
        The login result or login page
    """
    # For GET requests, render the login page
    if request.method == 'GET':
        from flask import render_template
        try:
            return render_template('users/login.html')
        except Exception as e:
            logger.error(f"Error rendering login template: {str(e)}")
            # If template is not found, return a simple HTML login form
            return """
            <html>
            <head>
                <title>Login</title>
                <link rel="stylesheet" href="/static/css/styles.css">
            </head>
            <body>
                <div class="container">
                    <h1>Login</h1>
                    <form id="login-form" method="post" action="/api/users/login">
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="remember" name="remember">
                                Remember me
                            </label>
                        </div>
                        <button type="submit" class="btn btn-primary">Login</button>
                    </form>
                    <p>Don't have an account? <a href="/api/users/register">Register</a></p>
                </div>
                <script>
                    document.getElementById('login-form').addEventListener('submit', function(e) {
                        e.preventDefault();
                        
                        const email = document.getElementById('email').value;
                        const password = document.getElementById('password').value;
                        const remember = document.getElementById('remember').checked;
                        
                        fetch('/api/users/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                email: email,
                                password: password,
                                remember: remember
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                window.location.href = '/dashboards/';
                            } else {
                                alert('Login failed: ' + (data.errors?.email?.[0] || 'Unknown error'));
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred during login');
                        });
                    });
                </script>
            </body>
            </html>
            """
    
    # For POST requests, handle login
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        # Authenticate user
        success, user, error_message = auth_service.authenticate(email, password)
        
        if not success:
            return jsonify({
                'success': False,
                'errors': {'email': [error_message]}
            }), 401
        
        # Create session
        auth_service.create_session(user, remember)
        
        # Return success
        return jsonify({
            'success': True,
            'user': user.dict()
        }), 200
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        return jsonify({
            'success': False,
            'errors': {'_error': [str(e)]}
        }), 500


@blueprint.route('/logout', methods=['POST'])
def logout():
    """
    Log out a user.
    
    Returns:
        The logout result
    """
    try:
        # End session
        auth_service.end_session()
        
        # Return success
        return jsonify({
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Error logging out user: {str(e)}")
        return jsonify({
            'success': False,
            'errors': {'_error': [str(e)]}
        }), 500


@blueprint.route('/me', methods=['GET'])
def get_current_user():
    """
    Get the current user.
    
    Returns:
        The current user
    """
    try:
        # Validate session
        valid, error = auth_service.validate_session()
        if not valid:
            return jsonify({
                'success': False,
                'errors': {'_error': [error]}
            }), 401
        
        # Get current user
        user = auth_service.get_current_user()
        if not user:
            return jsonify({
                'success': False,
                'errors': {'_error': ['User not found']}
            }), 401
        
        # Return user
        return jsonify({
            'success': True,
            'user': user.dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return jsonify({
            'success': False,
            'errors': {'_error': [str(e)]}
        }), 500


@blueprint.route('/<user_id>', methods=['GET'])
def get_user(user_id: str):
    """
    Get a user by ID.
    
    Args:
        user_id: The user ID
        
    Returns:
        The user
    """
    try:
        # Validate session
        valid, error = auth_service.validate_session()
        if not valid:
            return jsonify({
                'success': False,
                'errors': {'_error': [error]}
            }), 401
        
        # Get user by ID
        user = user_repository.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'errors': {'_error': ['User not found']}
            }), 404
        
        # Check if user is admin or requesting their own data
        current_user = auth_service.get_current_user()
        if not current_user.is_admin() and current_user.id != user.id:
            return jsonify({
                'success': False,
                'errors': {'_error': ['Unauthorized']}
            }), 403
        
        # Return user
        return jsonify({
            'success': True,
            'user': user.dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({
            'success': False,
            'errors': {'_error': [str(e)]}
        }), 500


@blueprint.route('/<user_id>', methods=['PUT'])
def update_user(user_id: str):
    """
    Update a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        The updated user
    """
    try:
        # Validate session
        valid, error = auth_service.validate_session()
        if not valid:
            return jsonify({
                'success': False,
                'errors': {'_error': [error]}
            }), 401
        
        # Get user by ID
        user = user_repository.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'errors': {'_error': ['User not found']}
            }), 404
        
        # Check if user is admin or updating their own data
        current_user = auth_service.get_current_user()
        if not current_user.is_admin() and current_user.id != user.id:
            return jsonify({
                'success': False,
                'errors': {'_error': ['Unauthorized']}
            }), 403
        
        # Get request data
        data = request.get_json()
        
        # Don't allow changing email
        if 'email' in data and data['email'] != user.email:
            return jsonify({
                'success': False,
                'errors': {'email': ['Email cannot be changed']}
            }), 400
        
        # Don't allow changing role unless admin
        if 'role' in data and data['role'] != user.role and not current_user.is_admin():
            return jsonify({
                'success': False,
                'errors': {'role': ['Only admins can change roles']}
            }), 403
        
        # Hash password if provided
        if 'password' in data and data['password']:
            data['password'] = pbkdf2_sha256.hash(data['password'])
        else:
            # Keep existing password
            data['password'] = user.password
        
        # Update user data
        for key, value in data.items():
            setattr(user, key, value)
        
        # Validate user data
        user_validator = ModelValidator(User)
        validation_result = user_validator.validate(user.dict())
        if not validation_result.is_valid:
            return jsonify({
                'success': False,
                'errors': validation_result.errors
            }), 400
        
        # Update user
        user_repository.update(user)
        
        # Log user update
        audit_logger.log_user_action(
            user_id=current_user.id,
            action="update",
            resource_type="user",
            resource_id=user.id
        )
        
        # Return success
        return jsonify({
            'success': True,
            'user': user.dict()
        }), 200
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({
            'success': False,
            'errors': {'_error': [str(e)]}
        }), 500


@blueprint.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id: str):
    """
    Delete a user.
    
    Args:
        user_id: The user ID
        
    Returns:
        The deletion result
    """
    try:
        # Validate session
        valid, error = auth_service.validate_session()
        if not valid:
            return jsonify({
                'success': False,
                'errors': {'_error': [error]}
            }), 401
        
        # Check if user is admin
        current_user = auth_service.get_current_user()
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'errors': {'_error': ['Unauthorized']}
            }), 403
        
        # Don't allow deleting self
        if current_user.id == user_id:
            return jsonify({
                'success': False,
                'errors': {'_error': ['Cannot delete self']}
            }), 400
        
        # Delete user
        if not user_repository.delete(user_id):
            return jsonify({
                'success': False,
                'errors': {'_error': ['User not found']}
            }), 404
        
        # Log user deletion
        audit_logger.log_user_action(
            user_id=current_user.id,
            action="delete",
            resource_type="user",
            resource_id=user_id
        )
        
        # Return success
        return jsonify({
            'success': True
        }), 200
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({
            'success': False,
            'errors': {'_error': [str(e)]}
        }), 500
