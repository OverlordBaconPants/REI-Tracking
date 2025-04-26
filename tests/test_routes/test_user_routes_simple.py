"""
Simple test module for user routes.

This module contains simplified tests for the user routes, focusing on authentication endpoints.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask

from src.routes.user_routes import blueprint as user_routes
from src.models.user import User


@pytest.fixture
def app():
    """Create a Flask application for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SERVER_NAME'] = 'localhost'  # Add this to ensure proper URL generation
    
    # Register blueprint with proper URL prefix
    app.register_blueprint(user_routes)
    
    # This is important - push an application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    # Clean up context after test
    ctx.pop()


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def mock_user():
    """Create a mock user."""
    return User(
        id="test-user-id",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="hashed-password",
        role="User"
    )


class TestUserRoutes:
    """Test cases for user routes."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        # Arrange
        with patch('src.routes.user_routes.user_repository') as mock_repo, \
             patch('src.routes.user_routes.ValidationService') as mock_validation:
            # Mock validation
            mock_validation.validate_email.return_value = MagicMock(is_valid=True)
            mock_validation.validate_model.return_value = MagicMock(
                is_valid=True,
                data=User(
                    id="new-user-id",
                    email="new@example.com",
                    first_name="New",
                    last_name="User",
                    password="hashed-password"
                )
            )
            
            # Mock repository
            mock_repo.email_exists.return_value = False
            
            # Act
            response = client.post(
                '/api/users/register',
                json={
                    'email': 'new@example.com',
                    'first_name': 'New',
                    'last_name': 'User',
                    'password': 'password123'
                },
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'user' in data
            assert data['user']['email'] == 'new@example.com'
            mock_repo.create.assert_called_once()
    

