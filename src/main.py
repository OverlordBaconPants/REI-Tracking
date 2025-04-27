"""
Main application module for the REI-Tracker application.

This module initializes the Flask application and sets up routes, middleware,
and other application components.
"""

import os
from datetime import timedelta
from flask import Flask, jsonify, request, send_from_directory, session
from flask_session import Session
from flask_login import LoginManager
from werkzeug.exceptions import HTTPException

from src.config import current_config
from src.utils.logging_utils import app_logger, audit_logger
from src.services.auth_service import SESSION_TIMEOUT, EXTENDED_SESSION_TIMEOUT
from src.utils.auth_middleware import init_auth_middleware

# Create Flask application
app = Flask(__name__)

# Load configuration
app.config.from_object(current_config)

# Configure application
app.secret_key = current_config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = current_config.MAX_CONTENT_LENGTH

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_PERMANENT_LIFETIME'] = timedelta(seconds=SESSION_TIMEOUT)
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = current_config.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_FILE_DIR'] = os.path.join(current_config.DATA_DIR, 'flask_session')

# Initialize Flask-Session
Session(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

@login_manager.user_loader
def load_user(user_id):
    from src.repositories.user_repository import UserRepository
    user_repo = UserRepository()
    return user_repo.get_by_id(user_id)


# Register error handlers
@app.errorhandler(HTTPException)
def handle_http_exception(error):
    """Handle HTTP exceptions."""
    response = {
        'error': {
            'code': error.code,
            'name': error.name,
            'description': error.description
        }
    }
    return jsonify(response), error.code

# Add response headers to allow framing from same origin
@app.after_request
def add_header(response):
    """Add headers to allow framing from same origin."""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle general exceptions."""
    app_logger.exception("Unhandled exception: %s", str(error))
    
    response = {
        'error': {
            'code': 500,
            'name': 'Internal Server Error',
            'description': 'An unexpected error occurred'
        }
    }
    return jsonify(response), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0'
    })


# Serve static files from the uploads directory
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files."""
    return send_from_directory(current_config.UPLOADS_DIR, filename)


# Import and register routes
def register_routes():
    """Register application routes."""
    # Import route modules
    try:
        from src.routes import blueprints
        
        # Register blueprints
        for blueprint in blueprints:
            app.register_blueprint(blueprint)
        
        app_logger.info("Routes registered successfully")
    except ImportError as e:
        app_logger.error(f"Error registering routes: {str(e)}")
        raise


# Initialize dashboards
def init_dashboards():
    """Initialize Dash applications."""
    try:
        from src.dash_apps.dash_portfolio import create_portfolio_dash
        from src.dash_apps.dash_amortization import create_amortization_dash
        
        # Create and attach portfolio dashboard
        app.portfolio_dash = create_portfolio_dash(app)
        app_logger.info("Portfolio dashboard initialized successfully")
        
        # Create and attach amortization dashboard
        app.amortization_dash = create_amortization_dash(app)
        app_logger.info("Amortization dashboard initialized successfully")
    except Exception as e:
        app_logger.error(f"Error initializing dashboards: {str(e)}")
        app_logger.exception("Dashboard initialization error details:")


# Initialize application
def init_app():
    """Initialize the application."""
    # Log application startup
    app_logger.info("Starting REI-Tracker application")
    audit_logger.log_system_event("startup", "application", {
        "environment": os.getenv("FLASK_ENV", "development")
    })
    
    # Initialize authentication middleware
    init_auth_middleware(app)
    
    # Register routes
    register_routes()
    
    # Initialize dashboards
    init_dashboards()
    
    # Return the configured app
    return app


# Create the application instance
application = init_app()


# Run the application if executed directly
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
