# app.py

from flask import Flask
from flask_login import LoginManager
from models import User
from services.user_service import get_user_by_email
import logging

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object('config.Config')

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        user_data = get_user_by_email(user_id)
        if user_data:
            return User(
                id=user_data['email'],  # Use email as id
                name=user_data['name'],
                email=user_data['email'],
                password=user_data['password'],
                role=user_data.get('role', 'User')
            )
        return None

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)