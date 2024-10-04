from flask import Flask
from flask_login import LoginManager
# from flask_caching import Cache
from config import Config
from __init__ import register_blueprints
from models import User

def create_app():
    app = Flask(__name__, template_folder='templates', 
                static_folder='static', static_url_path='/static')
    app.config.from_object(Config)

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Set up caching
  # cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    
    # Register blueprints from routes module
    register_blueprints(app)
    
    # Set up login loader in a separate service module
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)