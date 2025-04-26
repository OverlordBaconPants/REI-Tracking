"""
Authentication middleware module for the REI-Tracker application.

This module provides middleware functions for authentication and session management.
"""

from functools import wraps
from typing import Callable, Any, List, Optional

from flask import request, session, jsonify, current_app, g

from src.services.auth_service import AuthService
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


def init_auth_middleware(app: Any) -> None:
    """
    Initialize authentication middleware.
    
    Args:
        app: The Flask application
    """
    auth_service = AuthService()
    
    @app.before_request
    def validate_session() -> Optional[Any]:
        """
        Validate the current session before each request.
        
        Returns:
            None if the session is valid, or a response if the session is invalid
        """
        # Skip validation for public routes
        if _is_public_route(request.path):
            return None
        
        # Skip validation for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return None
        
        # Validate session
        valid, error = auth_service.validate_session()
        if not valid:
            # Only return 401 for API routes
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'errors': {'_error': [error]}
                }), 401
        
        # Store current user in g for easy access
        g.current_user = auth_service.get_current_user()
        
        return None
    
    @app.after_request
    def add_security_headers(response: Any) -> Any:
        """
        Add security headers to all responses.
        
        Args:
            response: The response to add headers to
            
        Returns:
            The response with added headers
        """
        return auth_service.add_security_headers(response)


def _is_public_route(path: str) -> bool:
    """
    Check if a route is public (doesn't require authentication).
    
    Args:
        path: The route path
        
    Returns:
        Whether the route is public
    """
    public_routes = [
        '/health',
        '/api/users/login',
        '/api/users/register',
        '/static/',
        '/favicon.ico',
    ]
    
    return any(path.startswith(route) for route in public_routes)


def login_required(f: Callable) -> Callable:
    """
    Decorator to require login for a route.
    
    Args:
        f: The route function
        
    Returns:
        The decorated function
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'errors': {'_error': ['Authentication required']}
                }), 401
            else:
                # For non-API routes, redirect to login page
                # This would be implemented if we had HTML routes
                pass
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f: Callable) -> Callable:
    """
    Decorator to require admin role for a route.
    
    Args:
        f: The route function
        
    Returns:
        The decorated function
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'errors': {'_error': ['Authentication required']}
                }), 401
            else:
                # For non-API routes, redirect to login page
                # This would be implemented if we had HTML routes
                pass
        
        if 'user_role' not in session or session['user_role'] != 'Admin':
            return jsonify({
                'success': False,
                'errors': {'_error': ['Admin privileges required']}
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
