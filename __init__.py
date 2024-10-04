from routes.auth import auth_bp
from routes.main import main_bp
from routes.admin import admin_bp
from routes.transactions import transactions_bp
from routes.api import api_bp

def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(transactions_bp, url_prefix='/transactions')
    app.register_blueprint(api_bp)