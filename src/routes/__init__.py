"""
Routes package for the REI-Tracker application.

This package provides the routes for the application, including
base, user, property, transaction, and analysis routes.
"""

from src.routes.base_routes import blueprint as base_blueprint
from src.routes.user_routes import blueprint as user_blueprint
from src.routes.analysis_routes import analysis_bp as analysis_blueprint

# Import other blueprints as they are created
# from src.routes.property_routes import blueprint as property_blueprint
# from src.routes.transaction_routes import blueprint as transaction_blueprint

# List of all blueprints
blueprints = [
    base_blueprint,
    user_blueprint,
    analysis_blueprint,
    # property_blueprint,
    # transaction_blueprint,
]

__all__ = [
    'blueprints',
    'base_blueprint',
    'user_blueprint',
    'analysis_blueprint',
    # 'property_blueprint',
    # 'transaction_blueprint',
]
