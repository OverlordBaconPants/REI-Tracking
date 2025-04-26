"""
Test module for user routes.

This module contains tests for the user routes, including authentication endpoints.
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from flask import Flask, session

from src.routes.user_routes import blueprint as user_routes
from src.models.user import User
from src.services.auth_service import AuthService


@pytest.fixture
def app():
    """Create a Flask application for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SERVER_NAME'] = 'localhost'  # Required for URL generation
    
    # Register blueprint with proper URL prefix
    app.register_blueprint(user_routes)
    
    # Create application context
    with app.app_context():
        yield app


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
    
    def test_register_success(self, app, client):
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
    
    def test_register_email_exists(self, app, client):
        """Test registration with existing email."""
        # Arrange
        with patch('src.routes.user_routes.user_repository') as mock_repo, \
             patch('src.routes.user_routes.ValidationService') as mock_validation:
            # Mock validation
            mock_validation.validate_email.return_value = MagicMock(is_valid=True)
            
            # Mock repository
            mock_repo.email_exists.return_value = True
            
            # Act
            response = client.post(
                '/api/users/register',
                json={
                    'email': 'existing@example.com',
                    'first_name': 'Existing',
                    'last_name': 'User',
                    'password': 'password123'
                },
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert 'email' in data['errors']
            assert 'Email already exists' in data['errors']['email'][0]
            mock_repo.create.assert_not_called()
    
    def test_register_invalid_email(self, app, client):
        """Test registration with invalid email."""
        # Arrange
        with patch('src.routes.user_routes.ValidationService') as mock_validation:
            # Mock validation
            mock_validation.validate_email.return_value = MagicMock(
                is_valid=False,
                errors={'email': ['Invalid email format']}
            )
            
            # Act
            response = client.post(
                '/api/users/register',
                json={
                    'email': 'invalid-email',
                    'first_name': 'New',
                    'last_name': 'User',
                    'password': 'password123'
                },
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert 'email' in data['errors']
    
    def test_login_success(self, app, client, mock_user):
        """Test successful login."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Mock authentication
            mock_auth.authenticate.return_value = (True, mock_user, None)
            
            # Act
            with app.test_client() as test_client:
                response = test_client.post(
                    '/api/users/login',
                    json={
                        'email': 'test@example.com',
                        'password': 'password123',
                        'remember': True
                    },
                    content_type='application/json'
                )
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'user' in data
            assert data['user']['email'] == 'test@example.com'
            mock_auth.authenticate.assert_called_once_with(
                'test@example.com', 'password123'
            )
            mock_auth.create_session.assert_called_once_with(mock_user, True)
    
    def test_login_invalid_credentials(self, app, client):
        """Test login with invalid credentials."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Mock authentication
            mock_auth.authenticate.return_value = (
                False, None, "Invalid email or password"
            )
            
            # Act
            with app.test_client() as test_client:
                response = test_client.post(
                    '/api/users/login',
                    json={
                        'email': 'test@example.com',
                        'password': 'wrong-password'
                    },
                    content_type='application/json'
                )
            
            # Assert
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert 'email' in data['errors']
            assert 'Invalid email or password' in data['errors']['email'][0]
            mock_auth.authenticate.assert_called_once_with(
                'test@example.com', 'wrong-password'
            )
            mock_auth.create_session.assert_not_called()
    
    def test_logout(self, app, client):
        """Test logout."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Act
            with app.test_client() as test_client:
                response = test_client.post('/api/users/logout')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            mock_auth.end_session.assert_called_once()
    
    def test_get_current_user_success(self, app, client, mock_user):
        """Test getting current user with valid session."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = mock_user
            
            # Act
            with app.test_client() as test_client:
                response = test_client.get('/api/users/me')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'user' in data
            assert data['user']['email'] == 'test@example.com'
            mock_auth.validate_session.assert_called_once()
            mock_auth.get_current_user.assert_called_once()
    
    def test_get_current_user_invalid_session(self, app, client):
        """Test getting current user with invalid session."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Mock session validation
            mock_auth.validate_session.return_value = (False, "Session expired")
            
            # Act
            with app.test_client() as test_client:
                response = test_client.get('/api/users/me')
            
            # Assert
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert '_error' in data['errors']
            assert 'Session expired' in data['errors']['_error'][0]
            mock_auth.validate_session.assert_called_once()
            mock_auth.get_current_user.assert_not_called()
    
    def test_get_current_user_not_found(self, app, client):
        """Test getting current user when user not found."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = None
            
            # Act
            with app.test_client() as test_client:
                response = test_client.get('/api/users/me')
            
            # Assert
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert '_error' in data['errors']
            assert 'User not found' in data['errors']['_error'][0]
            mock_auth.validate_session.assert_called_once()
            mock_auth.get_current_user.assert_called_once()
    
    def test_get_user_by_id_success(self, app, client, mock_user):
        """Test getting user by ID with valid session."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth, \
             patch('src.routes.user_routes.user_repository') as mock_repo:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = mock_user
            
            # Mock repository
            mock_repo.get_by_id.return_value = mock_user
            
            # Act
            with app.test_client() as test_client:
                response = test_client.get(f'/api/users/{mock_user.id}')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'user' in data
            assert data['user']['email'] == 'test@example.com'
            mock_auth.validate_session.assert_called_once()
            mock_repo.get_by_id.assert_called_once_with(mock_user.id)
    
    def test_get_user_by_id_not_found(self, app, client, mock_user):
        """Test getting user by ID when user not found."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth, \
             patch('src.routes.user_routes.user_repository') as mock_repo:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = mock_user
            
            # Mock repository
            mock_repo.get_by_id.return_value = None
            
            # Act
            with app.test_client() as test_client:
                response = test_client.get('/api/users/nonexistent-id')
            
            # Assert
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert '_error' in data['errors']
            assert 'User not found' in data['errors']['_error'][0]
            mock_auth.validate_session.assert_called_once()
            mock_repo.get_by_id.assert_called_once_with('nonexistent-id')
    
    def test_get_user_by_id_unauthorized(self, app, client, mock_user):
        """Test getting user by ID without permission."""
        # Arrange
        other_user = User(
            id="other-user-id",
            email="other@example.com",
            first_name="Other",
            last_name="User",
            password="hashed-password",
            role="User"
        )
        
        with patch('src.routes.user_routes.auth_service') as mock_auth, \
             patch('src.routes.user_routes.user_repository') as mock_repo:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = mock_user
            
            # Mock repository
            mock_repo.get_by_id.return_value = other_user
            
            # Act
            with app.test_client() as test_client:
                response = test_client.get(f'/api/users/{other_user.id}')
            
            # Assert
            assert response.status_code == 403
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert '_error' in data['errors']
            assert 'Unauthorized' in data['errors']['_error'][0]
            mock_auth.validate_session.assert_called_once()
            mock_repo.get_by_id.assert_called_once_with(other_user.id)
    
    def test_update_user_success(self, app, client, mock_user):
        """Test updating user with valid session."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth, \
             patch('src.routes.user_routes.user_repository') as mock_repo, \
             patch('src.routes.user_routes.ValidationService') as mock_validation:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = mock_user
            
            # Mock repository
            mock_repo.get_by_id.return_value = mock_user
            
            # Mock validation
            mock_validation.validate_model.return_value = MagicMock(
                is_valid=True,
                data=mock_user
            )
            
            # Act
            with app.test_client() as test_client:
                response = test_client.put(
                    f'/api/users/{mock_user.id}',
                    json={
                        'first_name': 'Updated',
                        'last_name': 'User'
                    },
                    content_type='application/json'
                )
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'user' in data
            mock_auth.validate_session.assert_called_once()
            mock_repo.update.assert_called_once()
    
    def test_delete_user_success(self, app, client, mock_user):
        """Test deleting user with admin privileges."""
        # Arrange
        admin_user = User(
            id="admin-user-id",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="hashed-password",
            role="Admin"
        )
        
        with patch('src.routes.user_routes.auth_service') as mock_auth, \
             patch('src.routes.user_routes.user_repository') as mock_repo:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = admin_user
            
            # Mock repository
            mock_repo.delete.return_value = True
            
            # Act
            with app.test_client() as test_client:
                response = test_client.delete(f'/api/users/{mock_user.id}')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            mock_auth.validate_session.assert_called_once()
            mock_repo.delete.assert_called_once_with(mock_user.id)
    
    def test_delete_user_not_admin(self, app, client, mock_user):
        """Test deleting user without admin privileges."""
        # Arrange
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = mock_user  # Non-admin user
            
            # Act
            with app.test_client() as test_client:
                response = test_client.delete(f'/api/users/other-user-id')
            
            # Assert
            assert response.status_code == 403
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert '_error' in data['errors']
            assert 'Unauthorized' in data['errors']['_error'][0]
            mock_auth.validate_session.assert_called_once()
    
    def test_delete_self(self, app, client, mock_user):
        """Test deleting own user account."""
        # Arrange
        admin_user = User(
            id="admin-user-id",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="hashed-password",
            role="Admin"
        )
        
        with patch('src.routes.user_routes.auth_service') as mock_auth:
            # Mock session validation
            mock_auth.validate_session.return_value = (True, None)
            mock_auth.get_current_user.return_value = admin_user
            
            # Act
            with app.test_client() as test_client:
                response = test_client.delete(f'/api/users/{admin_user.id}')
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'errors' in data
            assert '_error' in data['errors']
            assert 'Cannot delete self' in data['errors']['_error'][0]
            mock_auth.validate_session.assert_called_once()
