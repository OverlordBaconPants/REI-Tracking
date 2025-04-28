"""
Base routes module for the REI-Tracker application.

This module provides the base routes for the application, including
health check and static file routes.
"""

from flask import Blueprint, jsonify, request, send_from_directory, redirect, url_for
import os

from src.config import current_config
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Create blueprint
blueprint = Blueprint('base', __name__)

@blueprint.route('/')
def index():
    """Root route that redirects to the dashboards or login page."""
    logger.info("User accessed root route, redirecting to dashboards")
    return redirect(url_for('dashboards.dashboards'))

@blueprint.route('/login')
def login():
    """Login route that redirects to the user login page."""
    logger.info("User accessed login route, redirecting to user login")
    return redirect(url_for('users.login'))


@blueprint.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0'
    })


@blueprint.route('/uploads/<path:filename>')
def serve_upload(filename):
    """
    Serve uploaded files.
    
    Args:
        filename: The filename to serve
        
    Returns:
        The file
    """
    return send_from_directory(current_config.UPLOADS_DIR, filename)


@blueprint.route('/api/version', methods=['GET'])
def get_version():
    """
    Get the API version.
    
    Returns:
        The API version
    """
    return jsonify({
        'version': '1.0.0',
        'name': 'REI-Tracker API'
    })


@blueprint.errorhandler(404)
def not_found(error):
    """
    Handle 404 errors.
    
    Args:
        error: The error
        
    Returns:
        The error response
    """
    return jsonify({
        'error': {
            'code': 404,
            'message': 'Not Found'
        }
    }), 404


@blueprint.errorhandler(500)
def server_error(error):
    """
    Handle 500 errors.
    
    Args:
        error: The error
        
    Returns:
        The error response
    """
    logger.error(f"Server error: {str(error)}")
    
    return jsonify({
        'error': {
            'code': 500,
            'message': 'Internal Server Error'
        }
    }), 500
