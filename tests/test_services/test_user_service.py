import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from flask import Flask
from services.user_service import (
    load_users, save_users, get_user_by_email, create_user,
    hash_password, verify_password, update_user_password,
    update_user_mao_defaults, get_user_mao_defaults
)

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
                "phone": "123-456-7890",
                "role": "User"
            },
            "admin@example.com": {
                "name": "Admin User",
                "email": "admin@example.com",
                "password": "admin_password",
                "phone": "987-654-3210",
                "role": "Admin"
            }
        }
        json.dump(users, f)
        f.flush()
        yield f.name
    
    # Clean up
    os.unlink(f.name)

def test_load_users(app, mock_users_file):
    """Test loading users from file."""
    app.config['USERS_FILE'] = mock_users_file
    
    with app.app_context():
        users = load_users()
        assert len(users) == 2
        assert "test@example.com" in users
        assert "admin@example.com" in users
        assert users["test@example.com"]["name"] == "Test User"
        assert users["admin@example.com"]["role"] == "Admin"

def test_load_users_file_not_found(app):
    """Test loading users when file doesn't exist."""
    app.config['USERS_FILE'] = "nonexistent_file.json"
    
    with app.app_context():
        users = load_users()
        assert users == {}

def test_load_users_invalid_json(app, tmp_path):
    """Test loading users with invalid JSON."""
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("This is not valid JSON")
    
    app.config['USERS_FILE'] = str(invalid_file)
    
    with app.app_context():
        users = load_users()
        assert users == {}

def test_save_users(app, mock_users_file):
    """Test saving users to file."""
    app.config['USERS_FILE'] = mock_users_file
    
    with app.app_context():
        # Load existing users
        users = load_users()
        
        # Add a new user
        users["new@example.com"] = {
            "name": "New User",
            "email": "new@example.com",
            "password": "new_password",
            "phone": "555-555-5555",
            "role": "User"
        }
        
        # Save users
        save_users(users)
        
        # Load users again to verify
        updated_users = load_users()
        assert len(updated_users) == 3
        assert "new@example.com" in updated_users
        assert updated_users["new@example.com"]["name"] == "New User"

def test_get_user_by_email(app, mock_users_file):
    """Test getting a user by email."""
    app.config['USERS_FILE'] = mock_users_file
    
    with app.app_context():
        # Test getting existing user
        user = get_user_by_email("test@example.com")
        assert user is not None
        assert user["name"] == "Test User"
        
        # Test getting non-existent user
        user = get_user_by_email("nonexistent@example.com")
        assert user is None

def test_create_user(app, mock_users_file):
    """Test creating a new user."""
    app.config['USERS_FILE'] = mock_users_file
    
    with app.app_context():
        # Test creating a new user
        result = create_user(
            "new@example.com", 
            "New User", 
            "password123", 
            "555-555-5555"
        )
        assert result is True
        
        # Verify user was created
        users = load_users()
        assert "new@example.com" in users
        assert users["new@example.com"]["name"] == "New User"
        assert users["new@example.com"]["role"] == "User"  # Default role
        
        # Test creating a user with a custom role
        result = create_user(
            "admin2@example.com", 
            "Admin 2", 
            "admin123", 
            "666-666-6666", 
            role="Admin"
        )
        assert result is True
        
        # Verify user was created with custom role
        users = load_users()
        assert "admin2@example.com" in users
        assert users["admin2@example.com"]["role"] == "Admin"
        
        # Test creating a user that already exists
        result = create_user(
            "test@example.com", 
            "Duplicate User", 
            "password456", 
            "777-777-7777"
        )
        assert result is False

def test_hash_password():
    """Test password hashing."""
    password = "test_password"
    hashed = hash_password(password)
    
    # Verify the hash is not the original password
    assert hashed != password
    
    # Verify the hash starts with the method identifier
    assert hashed.startswith("pbkdf2:sha256")

def test_verify_password():
    """Test password verification."""
    password = "test_password"
    hashed = hash_password(password)
    
    # Verify correct password
    assert verify_password(hashed, password) is True
    
    # Verify incorrect password
    assert verify_password(hashed, "wrong_password") is False

def test_update_user_password(app, mock_users_file):
    """Test updating a user's password."""
    app.config['USERS_FILE'] = mock_users_file
    
    with app.app_context():
        # Test updating password for existing user
        result = update_user_password("test@example.com", "new_password")
        assert result is True
        
        # Verify password was updated
        users = load_users()
        assert users["test@example.com"]["password"] != "hashed_password"
        
        # Test updating password for non-existent user
        result = update_user_password("nonexistent@example.com", "new_password")
        assert result is False

def test_update_user_mao_defaults(app, mock_users_file):
    """Test updating a user's MAO defaults."""
    app.config['USERS_FILE'] = mock_users_file
    
    with app.app_context():
        # Test updating MAO defaults for existing user
        mao_defaults = {
            "ltv_percentage": 80.0,
            "monthly_holding_costs": 500,
            "max_cash_left": 5000
        }
        
        result = update_user_mao_defaults("test@example.com", mao_defaults)
        assert result is True
        
        # Verify MAO defaults were updated
        users = load_users()
        assert "mao_defaults" in users["test@example.com"]
        assert users["test@example.com"]["mao_defaults"]["ltv_percentage"] == 80.0
        assert users["test@example.com"]["mao_defaults"]["monthly_holding_costs"] == 500
        assert users["test@example.com"]["mao_defaults"]["max_cash_left"] == 5000
        
        # Test updating only one field
        partial_update = {
            "ltv_percentage": 70.0
        }
        
        result = update_user_mao_defaults("test@example.com", partial_update)
        assert result is True
        
        # Verify only the specified field was updated
        users = load_users()
        assert users["test@example.com"]["mao_defaults"]["ltv_percentage"] == 70.0
        assert users["test@example.com"]["mao_defaults"]["monthly_holding_costs"] == 500
        assert users["test@example.com"]["mao_defaults"]["max_cash_left"] == 5000
        
        # Test updating MAO defaults for non-existent user
        result = update_user_mao_defaults("nonexistent@example.com", mao_defaults)
        assert result is False

def test_get_user_mao_defaults(app, mock_users_file):
    """Test getting a user's MAO defaults."""
    app.config['USERS_FILE'] = mock_users_file
    
    with app.app_context():
        # First, set some MAO defaults
        mao_defaults = {
            "ltv_percentage": 80.0,
            "monthly_holding_costs": 500,
            "max_cash_left": 5000
        }
        
        update_user_mao_defaults("test@example.com", mao_defaults)
        
        # Test getting MAO defaults for existing user with defaults set
        defaults = get_user_mao_defaults("test@example.com")
        assert defaults is not None
        assert defaults["ltv_percentage"] == 80.0
        assert defaults["monthly_holding_costs"] == 500
        assert defaults["max_cash_left"] == 5000
        
        # Test getting MAO defaults for existing user without defaults set
        defaults = get_user_mao_defaults("admin@example.com")
        assert defaults is not None
        assert "ltv_percentage" in defaults
        assert "monthly_holding_costs" in defaults
        assert "max_cash_left" in defaults
        assert defaults["ltv_percentage"] == 75.0  # Default value
        assert defaults["monthly_holding_costs"] == 0  # Default value
        assert defaults["max_cash_left"] == 10000  # Default value
        
        # Test getting MAO defaults for non-existent user
        defaults = get_user_mao_defaults("nonexistent@example.com")
        assert defaults is not None
        assert "ltv_percentage" in defaults
        assert "monthly_holding_costs" in defaults
        assert "max_cash_left" in defaults
        assert defaults["ltv_percentage"] == 75.0  # Default value
        assert defaults["monthly_holding_costs"] == 0  # Default value
        assert defaults["max_cash_left"] == 10000  # Default value
