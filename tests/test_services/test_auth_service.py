"""
Test module for the authentication service.

This module contains tests for the AuthService class.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import time

from src.services.auth_service import AuthService, SESSION_TIMEOUT, EXTENDED_SESSION_TIMEOUT, LOGIN_COOLDOWN_PERIOD
from src.models.user import User
from src.repositories.user_repository import UserRepository


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    repo = MagicMock(spec=UserRepository)
    
    # Create a test user
    test_user = User(
        id="test-user-id",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="$pbkdf2-sha256$29000$uXcOobS2FiIkJCQEwBjj3A$1t8iyB2A.WF/Z5JZv.lfCBPNLm6ABzOX5kzz5RxRY1M",  # "password"
        role="User"
    )
    
    # Set up repository methods
    repo.get_by_email.return_value = test_user
    repo.get_by_id.return_value = test_user
    
    return repo


@pytest.fixture
def auth_service(mock_user_repository):
    """Create an AuthService instance with a mock repository."""
    return AuthService(mock_user_repository)


@pytest.fixture
def mock_session():
    """Create a mock session dictionary."""
    with patch("src.services.auth_service.session", {}) as mock_session:
        yield mock_session


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = MagicMock()
    response.headers = {}
    return response


class TestAuthService:
    """Test cases for the AuthService class."""
    
    def test_authenticate_success(self, auth_service, mock_user_repository):
        """Test successful authentication."""
        # Arrange
        email = "test@example.com"
        password = "password"
        
        # Mock password verification
        with patch("src.services.auth_service.pbkdf2_sha256.verify", return_value=True):
            # Act
            success, user, error = auth_service.authenticate(email, password)
            
            # Assert
            assert success is True
            assert user is not None
            assert user.email == email
            assert error is None
            mock_user_repository.get_by_email.assert_called_once_with(email)
    
    def test_authenticate_invalid_password(self, auth_service, mock_user_repository):
        """Test authentication with invalid password."""
        # Arrange
        email = "test@example.com"
        password = "wrong-password"
        
        # Mock password verification
        with patch("src.services.auth_service.pbkdf2_sha256.verify", return_value=False):
            # Act
            success, user, error = auth_service.authenticate(email, password)
            
            # Assert
            assert success is False
            assert user is None
            assert error == "Invalid email or password"
            mock_user_repository.get_by_email.assert_called_once_with(email)
    
    def test_authenticate_user_not_found(self, auth_service, mock_user_repository):
        """Test authentication with non-existent user."""
        # Arrange
        email = "nonexistent@example.com"
        password = "password"
        mock_user_repository.get_by_email.return_value = None
        
        # Act
        success, user, error = auth_service.authenticate(email, password)
        
        # Assert
        assert success is False
        assert user is None
        assert error == "Invalid email or password"
        mock_user_repository.get_by_email.assert_called_once_with(email)
    
    def test_create_session(self, auth_service, mock_session, mock_user_repository):
        """Test session creation."""
        # Arrange
        user = mock_user_repository.get_by_email("test@example.com")
        
        # Act
        auth_service.create_session(user, remember=False)
        
        # Assert
        assert mock_session['user_id'] == user.id
        assert mock_session['user_email'] == user.email
        assert mock_session['user_role'] == user.role
        assert 'login_time' in mock_session
        assert mock_session['remember'] is False
        assert 'expires_at' in mock_session
    
    def test_create_extended_session(self, auth_service, mock_session, mock_user_repository):
        """Test extended session creation."""
        # Arrange
        user = mock_user_repository.get_by_email("test@example.com")
        
        # Act
        auth_service.create_session(user, remember=True)
        
        # Assert
        assert mock_session['user_id'] == user.id
        assert mock_session['user_email'] == user.email
        assert mock_session['user_role'] == user.role
        assert 'login_time' in mock_session
        assert mock_session['remember'] is True
        assert 'expires_at' in mock_session
    
    def test_validate_session_valid(self, auth_service, mock_session, mock_user_repository):
        """Test session validation with valid session."""
        # Arrange
        user = mock_user_repository.get_by_email("test@example.com")
        mock_session['user_id'] = user.id
        mock_session['expires_at'] = (datetime.now() + timedelta(hours=1)).isoformat()
        
        # Act
        valid, error = auth_service.validate_session()
        
        # Assert
        assert valid is True
        assert error is None
    
    def test_validate_session_expired(self, auth_service, mock_session, mock_user_repository):
        """Test session validation with expired session."""
        # Arrange
        user = mock_user_repository.get_by_email("test@example.com")
        mock_session['user_id'] = user.id
        mock_session['expires_at'] = (datetime.now() - timedelta(hours=1)).isoformat()
        
        # Act
        valid, error = auth_service.validate_session()
        
        # Assert
        assert valid is False
        assert error == "Session expired"
        assert len(mock_session) == 0  # Session should be cleared
    
    def test_validate_session_not_logged_in(self, auth_service, mock_session):
        """Test session validation when not logged in."""
        # Arrange - empty session
        
        # Act
        valid, error = auth_service.validate_session()
        
        # Assert
        assert valid is False
        assert error == "Not logged in"
    
    def test_end_session(self, auth_service, mock_session, mock_user_repository):
        """Test ending a session."""
        # Arrange
        user = mock_user_repository.get_by_email("test@example.com")
        mock_session['user_id'] = user.id
        mock_session['user_email'] = user.email
        mock_session['user_role'] = user.role
        
        # Act
        auth_service.end_session()
        
        # Assert
        assert len(mock_session) == 0
    
    def test_get_current_user(self, auth_service, mock_session, mock_user_repository):
        """Test getting the current user."""
        # Arrange
        user = mock_user_repository.get_by_email("test@example.com")
        mock_session['user_id'] = user.id
        
        # Act
        current_user = auth_service.get_current_user()
        
        # Assert
        assert current_user is not None
        assert current_user.id == user.id
        mock_user_repository.get_by_id.assert_called_once_with(user.id)
    
    def test_get_current_user_not_logged_in(self, auth_service, mock_session):
        """Test getting the current user when not logged in."""
        # Arrange - empty session
        
        # Act
        current_user = auth_service.get_current_user()
        
        # Assert
        assert current_user is None
    
    def test_get_current_user_not_found(self, auth_service, mock_session, mock_user_repository):
        """Test getting the current user when the user is not found."""
        # Arrange
        mock_session['user_id'] = "nonexistent-user-id"
        mock_user_repository.get_by_id.return_value = None
        
        # Act
        current_user = auth_service.get_current_user()
        
        # Assert
        assert current_user is None
        assert len(mock_session) == 0  # Session should be cleared
    
    def test_add_security_headers(self, auth_service, mock_response):
        """Test adding security headers to a response."""
        # Act
        response = auth_service.add_security_headers(mock_response)
        
        # Assert
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert 'Strict-Transport-Security' in response.headers
        assert 'Content-Security-Policy' in response.headers
        assert 'Permissions-Policy' in response.headers
        assert 'Referrer-Policy' in response.headers
    
    def test_rate_limiting(self, auth_service):
        """Test login rate limiting."""
        # Arrange
        email = "test@example.com"
        
        # Act - Record multiple failed attempts
        for _ in range(5):
            auth_service._record_failed_attempt(email)
        
        # Assert
        assert auth_service._is_rate_limited(email) is True
        
        # Act - Reset login attempts
        auth_service._reset_login_attempts(email)
        
        # Assert
        assert auth_service._is_rate_limited(email) is False
    
    def test_rate_limiting_cooldown(self, auth_service):
        """Test login rate limiting cooldown."""
        # Arrange
        email = "test@example.com"
        
        # Act - Record multiple failed attempts
        for _ in range(5):
            auth_service._record_failed_attempt(email)
        
        # Assert
        assert auth_service._is_rate_limited(email) is True
        
        # Simulate cooldown period passing
        auth_service._login_attempts[email]['last_attempt'] = time.time() - (LOGIN_COOLDOWN_PERIOD + 10)
        
        # Assert
        assert auth_service._is_rate_limited(email) is False
