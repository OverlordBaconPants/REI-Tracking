import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, url_for
from utils.utils import admin_required

class TestUtils:
    """Test suite for the utils module."""
    
    def test_admin_required_with_admin_user(self):
        """Test admin_required decorator with an admin user."""
        # Create a mock function to decorate
        mock_func = MagicMock(return_value="Success")
        
        # Create mocks for the imports in the decorator
        with patch('utils.utils.current_user') as mock_user, \
             patch('utils.utils.flash') as mock_flash, \
             patch('utils.utils.redirect') as mock_redirect, \
             patch('utils.utils.url_for') as mock_url_for:
            
            # Configure the mock user as an admin
            mock_user.is_authenticated = True
            mock_user.role = 'Admin'
            
            # Apply the decorator to our mock function
            decorated_func = admin_required(mock_func)
            
            # Call the decorated function
            result = decorated_func()
            
            # Assert the original function was called
            mock_func.assert_called_once()
            
            # Assert the result is from the original function
            assert result == "Success"
            
            # Assert flash and redirect were not called
            mock_flash.assert_not_called()
            mock_redirect.assert_not_called()
            mock_url_for.assert_not_called()
    
    def test_admin_required_with_non_admin_user(self):
        """Test admin_required decorator with a non-admin user."""
        # Create a mock function to decorate
        mock_func = MagicMock(return_value="Success")
        
        # Create mocks for the imports in the decorator
        with patch('utils.utils.current_user') as mock_user, \
             patch('utils.utils.flash') as mock_flash, \
             patch('utils.utils.redirect') as mock_redirect, \
             patch('utils.utils.url_for') as mock_url_for:
            
            # Configure the mock user as a non-admin
            mock_user.is_authenticated = True
            mock_user.role = 'User'
            
            # Configure the redirect
            mock_url_for.return_value = '/index'
            mock_redirect.return_value = ("REDIRECTED", 403)
            
            # Apply the decorator to our mock function
            decorated_func = admin_required(mock_func)
            
            # Call the decorated function
            result = decorated_func()
            
            # Assert the original function was NOT called
            mock_func.assert_not_called()
            
            # Assert the flash message was shown
            mock_flash.assert_called_once_with('You do not have permission to access this page.', 'danger')
            
            # Assert the user was redirected
            mock_url_for.assert_called_once_with('main.index')
            mock_redirect.assert_called_once_with('/index')
            
            # Assert the redirect response was returned
            assert result == (("REDIRECTED", 403), 403)
    
    def test_admin_required_with_unauthenticated_user(self):
        """Test admin_required decorator with an unauthenticated user."""
        # Create a mock function to decorate
        mock_func = MagicMock(return_value="Success")
        
        # Create mocks for the imports in the decorator
        with patch('utils.utils.current_user') as mock_user, \
             patch('utils.utils.flash') as mock_flash, \
             patch('utils.utils.redirect') as mock_redirect, \
             patch('utils.utils.url_for') as mock_url_for:
            
            # Configure the mock user as unauthenticated
            mock_user.is_authenticated = False
            
            # Configure the redirect
            mock_url_for.return_value = '/index'
            mock_redirect.return_value = ("REDIRECTED", 403)
            
            # Apply the decorator to our mock function
            decorated_func = admin_required(mock_func)
            
            # Call the decorated function
            result = decorated_func()
            
            # Assert the original function was NOT called
            mock_func.assert_not_called()
            
            # Assert the flash message was shown
            mock_flash.assert_called_once_with('You do not have permission to access this page.', 'danger')
            
            # Assert the user was redirected
            mock_url_for.assert_called_once_with('main.index')
            mock_redirect.assert_called_once_with('/index')
            
            # Assert the redirect response was returned
            assert result == (("REDIRECTED", 403), 403)
