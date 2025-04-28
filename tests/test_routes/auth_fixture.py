"""
Authentication fixtures for testing.

This module provides fixtures for testing authentication in the application.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import session
from flask_login import login_user

from src.models.user import User, PropertyAccess


class AuthActions:
    """Authentication actions for testing."""

    def __init__(self, client):
        """Initialize with the test client."""
        self._client = client
        self._user = None

    def login(self, email="test@example.com", password="password"):
        """Log in as a regular user with property access."""
        # Create a mock user with property access
        property_access = [
            PropertyAccess(property_id="prop1", access_level="owner", equity_share=100.0)
        ]
        
        self._user = User(
            id="user1",
            email=email,
            first_name="Test",
            last_name="User",
            password="hashed_password",
            role="User",
            property_access=property_access
        )
        
        # Mock the login
        with self._client.session_transaction() as sess:
            sess.clear()  # Clear any existing session data
            sess["user_id"] = self._user.id
            sess["user_email"] = self._user.email
            sess["user_role"] = self._user.role
            sess["login_time"] = "2025-04-27T11:00:00"
            sess["remember"] = False
            sess["expires_at"] = "2025-04-27T12:00:00"
            sess["_test_mode"] = True
        
        # Mock the current_user
        with patch("flask_login.utils._get_user") as mock_get_user:
            mock_get_user.return_value = self._user
            
        # Mock the user repository to return the user when get_by_id is called
        with patch("src.services.auth_service.UserRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = self._user
            mock_repo_class.return_value = mock_repo
        
        return self._user

    def login_as_admin(self, email="admin@example.com", password="admin_password"):
        """Log in as an admin user."""
        # Create a mock admin user
        self._user = User(
            id="admin1",
            email=email,
            first_name="Admin",
            last_name="User",
            password="hashed_password",
            role="Admin",
            property_access=[]
        )
        
        # Mock the login
        with self._client.session_transaction() as sess:
            sess.clear()  # Clear any existing session data
            sess["user_id"] = self._user.id
            sess["user_email"] = self._user.email
            sess["user_role"] = self._user.role
            sess["login_time"] = "2025-04-27T11:00:00"
            sess["remember"] = False
            sess["expires_at"] = "2025-04-27T12:00:00"
            sess["_test_mode"] = True
        
        # Mock the current_user
        with patch("flask_login.utils._get_user") as mock_get_user:
            mock_get_user.return_value = self._user
            
        # Mock the user repository to return the user when get_by_id is called
        with patch("src.services.auth_service.UserRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = self._user
            mock_repo_class.return_value = mock_repo
        
        return self._user

    def login_no_properties(self, email="noprop@example.com", password="password"):
        """Log in as a user with no property access."""
        # Create a mock user with no property access
        self._user = User(
            id="user2",
            email=email,
            first_name="No",
            last_name="Properties",
            password="hashed_password",
            role="User",
            property_access=[]
        )
        
        # Mock the login
        with self._client.session_transaction() as sess:
            sess.clear()  # Clear any existing session data
            sess["user_id"] = self._user.id
            sess["user_email"] = self._user.email
            sess["user_role"] = self._user.role
            sess["login_time"] = "2025-04-27T11:00:00"
            sess["remember"] = False
            sess["expires_at"] = "2025-04-27T12:00:00"
            sess["_test_mode"] = True
        
        # Mock the current_user
        with patch("flask_login.utils._get_user") as mock_get_user:
            mock_get_user.return_value = self._user
            
        # Mock the user repository to return the user when get_by_id is called
        with patch("src.services.auth_service.UserRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = self._user
            mock_repo_class.return_value = mock_repo
        
        return self._user

    def logout(self):
        """Log out the current user."""
        return self._client.get("/auth/logout", follow_redirects=True)


@pytest.fixture
def auth(client):
    """Authentication fixture for testing."""
    return AuthActions(client)
