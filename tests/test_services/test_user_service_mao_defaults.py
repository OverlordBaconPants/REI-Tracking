import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from flask import Flask
from services.user_service import update_user_mao_defaults, get_user_mao_defaults

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def mock_users_file():
    """Create a temporary users file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        # Create test users
        users = {
            "test@example.com": {
                "name": "Test User",
                "email": "test@example.com",
                "password": "hashed_password",
                "role": "User"
            },
            "test_with_defaults@example.com": {
                "name": "Test User With Defaults",
                "email": "test_with_defaults@example.com",
                "password": "hashed_password",
                "role": "User",
                "mao_defaults": {
                    "ltv_percentage": 80.0,
                    "monthly_holding_costs": 500,
                    "max_cash_left": 15000
                }
            }
        }
        json.dump(users, f)
        f.flush()
        yield f.name
    
    # Clean up
    os.unlink(f.name)

def test_update_user_mao_defaults(app, mock_users_file):
    """Test updating MAO defaults for a user."""
    # Configure app
    app.config['USERS_FILE'] = mock_users_file
    
    # Use app context
    with app.app_context():
        # Test updating defaults for existing user
        mao_defaults = {
            'ltv_percentage': 85.0,
            'monthly_holding_costs': 600,
            'max_cash_left': 12000
        }
        result = update_user_mao_defaults("test@example.com", mao_defaults)
        assert result is True
        
        # Verify defaults were saved
        with open(mock_users_file, 'r') as f:
            users = json.load(f)
            assert 'mao_defaults' in users["test@example.com"]
            assert users["test@example.com"]["mao_defaults"]["ltv_percentage"] == 85.0
            assert users["test@example.com"]["mao_defaults"]["monthly_holding_costs"] == 600
            assert users["test@example.com"]["mao_defaults"]["max_cash_left"] == 12000
        
        # Test updating defaults for non-existent user
        result = update_user_mao_defaults("nonexistent@example.com", mao_defaults)
        assert result is False

def test_get_user_mao_defaults(app, mock_users_file):
    """Test getting MAO defaults for a user."""
    # Configure app
    app.config['USERS_FILE'] = mock_users_file
    
    # Use app context
    with app.app_context():
        # Test getting defaults for user with no defaults set
        defaults = get_user_mao_defaults("test@example.com")
        assert defaults['ltv_percentage'] == 75.0  # Default value
        assert defaults['monthly_holding_costs'] == 0  # Default value
        assert defaults['max_cash_left'] == 10000  # Default value
        
        # Test getting defaults for user with defaults set
        defaults = get_user_mao_defaults("test_with_defaults@example.com")
        assert defaults['ltv_percentage'] == 80.0
        assert defaults['monthly_holding_costs'] == 500
        assert defaults['max_cash_left'] == 15000
        
        # Test getting defaults for non-existent user
        defaults = get_user_mao_defaults("nonexistent@example.com")
        assert defaults['ltv_percentage'] == 75.0  # Default value
        assert defaults['monthly_holding_costs'] == 0  # Default value
        assert defaults['max_cash_left'] == 10000  # Default value
