"""
Pytest configuration and fixtures for the REI-Tracker application.

This module provides pytest fixtures for testing the application.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path

from src.config import current_config


@pytest.fixture
def temp_data_dir():
    """
    Create a temporary data directory for testing.
    
    This fixture creates a temporary directory for test data files,
    and updates the configuration to use this directory.
    
    Yields:
        The path to the temporary directory
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create subdirectories
    uploads_dir = os.path.join(temp_dir, 'uploads')
    analyses_dir = os.path.join(temp_dir, 'analyses')
    logs_dir = os.path.join(temp_dir, 'logs')
    
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(analyses_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    
    # Store original paths
    original_data_dir = current_config.DATA_DIR
    original_uploads_dir = current_config.UPLOADS_DIR
    original_analyses_dir = current_config.ANALYSES_DIR
    original_logs_dir = current_config.LOG_FILE.parent
    
    # Update configuration
    current_config.DATA_DIR = Path(temp_dir)
    current_config.UPLOADS_DIR = Path(uploads_dir)
    current_config.ANALYSES_DIR = Path(analyses_dir)
    current_config.LOG_FILE = Path(logs_dir) / 'app.log'
    
    # Update file paths
    current_config.USERS_FILE = Path(temp_dir) / 'test_users.json'
    current_config.PROPERTIES_FILE = Path(temp_dir) / 'test_properties.json'
    current_config.TRANSACTIONS_FILE = Path(temp_dir) / 'test_transactions.json'
    current_config.CATEGORIES_FILE = Path(temp_dir) / 'test_categories.json'
    
    # Yield the temporary directory
    yield temp_dir
    
    # Restore original paths
    current_config.DATA_DIR = original_data_dir
    current_config.UPLOADS_DIR = original_uploads_dir
    current_config.ANALYSES_DIR = original_analyses_dir
    current_config.LOG_FILE = original_logs_dir / 'app.log'
    
    # Clean up
    shutil.rmtree(temp_dir)


@pytest.fixture
def app_client():
    """
    Create a Flask test client.
    
    This fixture creates a Flask test client for testing routes.
    
    Returns:
        A Flask test client
    """
    from src.main import app
    
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Create a test client
    with app.test_client() as client:
        yield client


@pytest.fixture
def client(app_client):
    """
    Alias for app_client fixture.
    
    This fixture is an alias for the app_client fixture.
    
    Returns:
        A Flask test client
    """
    return app_client


@pytest.fixture
def auth_headers():
    """
    Create authentication headers for testing.
    
    This fixture creates authentication headers for testing routes
    that require authentication.
    
    Returns:
        A dictionary of authentication headers
    """
    from unittest.mock import patch
    
    # Mock the current_user in flask_login
    with patch('flask_login.utils._get_user') as mock_get_user:
        # Create a mock user
        mock_user = type('User', (), {
            'id': 'test-user-id',
            'is_authenticated': True,
            'is_active': True
        })
        mock_get_user.return_value = mock_user
        
        # Return headers with a mock session token
        return {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
