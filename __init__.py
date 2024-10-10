from flask import Flask
from flask_login import LoginManager, login_required
from config import Config
from models import User
import os
import dash
import logging
from dash_apps.dash_transactions import create_transactions_dash
from dash_apps.dash_amortization import create_amortization_dash
from flask.helpers import get_root_path

login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', 
                static_folder='static', static_url_path='/static')
    app.config.from_object(config_class)

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(dashboards_bp)

    # Set up login loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Create and integrate Dash apps
    app.logger.debug("About to create Dash apps...")
    app.amortization_dash = create_amortization_dash(app)

    if app.amortization_dash is None:
        app.logger.error("Failed to create Amortization Dash app")
    else:
        app.logger.debug("Amortization Dash app created successfully")

    return app