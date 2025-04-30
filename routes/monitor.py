# routes/monitor.py
from flask import Blueprint, jsonify

monitor_bp = Blueprint('monitor', __name__)

@monitor_bp.route('/health')
def health_check():
    """Basic health check endpoint that always returns 200 OK."""
    return jsonify({
        'status': 'healthy',
        'service': 'property-management-app'
    }), 200