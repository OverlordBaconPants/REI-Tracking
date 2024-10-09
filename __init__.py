from flask import Flask
from flask_login import LoginManager, login_required
from config import Config
from models import User
import os
import logging
from dash_apps.dash_transactions import create_transactions_dash

# Import blueprints
from routes.auth import auth_bp
from routes.main import main_bp
from routes.properties import properties_bp
from routes.transactions import transactions_bp
from routes.api import api_bp

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
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Set up additional file logging for errors
    if not app.debug:
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)

    # Set up login loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Create and integrate Dash app
    app.logger.debug("About to create Dash app...")
    dash_app = create_transactions_dash(app)
    if dash_app is None:
        app.logger.error("Failed to create Dash app")
    else:
        app.logger.debug(f"Dash app created with routes: {dash_app.server.url_map}")

    return app

# If you want to set up caching, you can add it here
# from flask_caching import Cache
# cache = Cache()
# 
# def init_cache(app):
#     cache.init_app(app, config={'CACHE_TYPE': 'simple'})