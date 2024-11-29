from flask import Flask
from flask_login import LoginManager, login_required, UserMixin
from config import get_config
import os
import dash
import logging
from logging.handlers import RotatingFileHandler
from dash_apps.dash_transactions import create_transactions_dash
from dash_apps.dash_amortization import create_amortization_dash
from dash_apps.dash_portfolio import create_portfolio_dash
from flask.helpers import get_root_path

# Make User available for import from this module
__all__ = ['User', 'create_app']

# Move User class here
class User(UserMixin):
    def __init__(self, id, email, name, password, role):
        self.id = id
        self.email = email
        self.name = name
        self.password = password
        self.role = role

    def get_id(self):
        return self.email

    @staticmethod
    def get(user_id):
        from services.user_service import load_users
        users = load_users()
        user_data = users.get(user_id)
        if user_data:
            return User(
                id=user_data['email'],
                email=user_data['email'],
                name=user_data['name'],
                password=user_data['password'],
                role=user_data.get('role', 'User')
            )
        return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

login_manager = LoginManager()

def configure_logging(app):
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Set up file handler
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Remove default handlers
    app.logger.handlers = []
    
    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    
    # Add console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app.logger.addHandler(console_handler)
    
    # Set overall logging level based on config
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.info(f'Application startup in {os.environ.get("FLASK_ENV", "development")} mode')

def create_app(config_class=None):
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static', 
                static_url_path='/static')
    
    # Get configuration based on environment
    if config_class is None:
        config_class = get_config()
    
    # Apply configuration
    app.config.from_object(config_class)
    
    # Log the environment and base directory being used
    app.logger.info(f"Running with BASE_DIR: {config_class.BASE_DIR}")
    app.logger.info(f"Environment: {'Production' if os.environ.get('RENDER') else 'Development'}")

    # Configure logging
    configure_logging(app)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['ANALYSES_DIR'], exist_ok=True)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.properties import properties_bp
    from routes.transactions import transactions_bp
    from routes.api import api_bp
    from routes.dashboards import dashboards_bp
    from routes.analyses import analyses_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(analyses_bp, url_prefix='/analyses')

    # Set up login loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Create and integrate Dash apps
    app.logger.debug("About to create Dash apps...")
    
    try:
        # Create Amortization Dashboard
        app.logger.debug("Creating Amortization Dashboard...")
        app.amortization_dash = create_amortization_dash(app)
        if app.amortization_dash is None:
            app.logger.error("Failed to create Amortization Dash app")
        else:
            app.logger.debug("Amortization Dash app created successfully")

        # Create Portfolio Dashboard
        app.logger.debug("Creating Portfolio Dashboard...")
        app.portfolio_dash = create_portfolio_dash(app)
        if app.portfolio_dash is None:
            app.logger.error("Failed to create Portfolio Dash app")
        else:
            app.logger.debug("Portfolio Dash app created successfully")

        # Create Transactions Dashboard
        app.logger.debug("Creating Transactions Dashboard...")
        app.transactions_dash = create_transactions_dash(app)
        if app.transactions_dash is None:
            app.logger.error("Failed to create Transactions Dash app")
        else:
            app.logger.debug("Transactions Dash app created successfully")

    except Exception as e:
        app.logger.error(f"Error creating Dash apps: {str(e)}")
        app.logger.exception("Full traceback:")
        raise

    app.logger.info("All Dash apps initialized successfully")
    return app