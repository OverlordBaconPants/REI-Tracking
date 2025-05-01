import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
import routes.analyses

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['WTF_CSRF_ENABLED'] = False
    return app

def test_get_mao_defaults_route(app):
    """Test the get_mao_defaults route."""
    # Create a test user
    test_user = MagicMock()
    test_user.email = "test@example.com"
    
    # Mock the necessary functions
    with patch('services.user_service.get_user_mao_defaults') as mock_get_defaults, \
         patch('flask_login.current_user', test_user):
        
        # Set up the mock to return test data
        mock_get_defaults.return_value = {
            'ltv_percentage': 80.0,
            'monthly_holding_costs': 500,
            'max_cash_left': 15000
        }
        
        # Create a request context
        with app.test_request_context('/analyses/get_mao_defaults'):
            # Call the function directly
            with patch('flask.jsonify', side_effect=lambda x: x) as mock_jsonify:
                result = routes.analyses.get_mao_defaults()
                
                # Verify the result
                assert result['success'] is True
                assert 'mao_defaults' in result
                assert result['mao_defaults']['ltv_percentage'] == 80.0
                assert result['mao_defaults']['monthly_holding_costs'] == 500
                assert result['mao_defaults']['max_cash_left'] == 15000
                
                # Verify the function was called with the correct email
                mock_get_defaults.assert_called_once_with('test@example.com')

def test_update_mao_defaults_route(app):
    """Test the update_mao_defaults route."""
    # Create a test user
    test_user = MagicMock()
    test_user.email = "test@example.com"
    
    # Mock the necessary functions
    with patch('services.user_service.update_user_mao_defaults') as mock_update_defaults, \
         patch('flask_login.current_user', test_user):
        
        # Set up the mock to return success
        mock_update_defaults.return_value = True
        
        # Test valid update
        mao_defaults = {
            'ltv_percentage': 85.0,
            'monthly_holding_costs': 600,
            'max_cash_left': 12000
        }
        
        # Create a request context
        with app.test_request_context('/analyses/update_mao_defaults', 
                                     method='POST',
                                     json=mao_defaults):
            # Call the function directly
            with patch('flask.jsonify', side_effect=lambda x: x) as mock_jsonify:
                result = routes.analyses.update_mao_defaults()
                
                # Verify the result
                assert result['success'] is True
                assert result['message'] == 'MAO defaults updated successfully'
                
                # Verify the function was called with the correct arguments
                mock_update_defaults.assert_called_once_with('test@example.com', mao_defaults)
        
        # Reset mock
        mock_update_defaults.reset_mock()
        
        # Test invalid update (missing field)
        invalid_defaults = {
            'ltv_percentage': 85.0,
            'monthly_holding_costs': 600
            # missing max_cash_left
        }
        
        # Create a request context
        with app.test_request_context('/analyses/update_mao_defaults', 
                                     method='POST',
                                     json=invalid_defaults):
            # Call the function directly
            result = routes.analyses.update_mao_defaults()
            
            # Verify the result
            assert isinstance(result, tuple)
            assert result[0]['success'] is False
            assert 'Missing required field' in result[0]['message']
            assert result[1] == 400
            
            # Verify the function was not called
            mock_update_defaults.assert_not_called()
        
        # Test invalid update (invalid value)
        invalid_defaults = {
            'ltv_percentage': 150.0,  # Invalid: > 100%
            'monthly_holding_costs': 600,
            'max_cash_left': 12000
        }
        
        # Create a request context
        with app.test_request_context('/analyses/update_mao_defaults', 
                                     method='POST',
                                     json=invalid_defaults):
            # Call the function directly
            result = routes.analyses.update_mao_defaults()
            
            # Verify the result
            assert isinstance(result, tuple)
            assert result[0]['success'] is False
            assert 'LTV percentage must be between 0 and 100' in result[0]['message']
            assert result[1] == 400
            
            # Verify the function was not called
            mock_update_defaults.assert_not_called()
        
        # Test update failure
        mock_update_defaults.return_value = False
        
        # Create a request context
        with app.test_request_context('/analyses/update_mao_defaults', 
                                     method='POST',
                                     json=mao_defaults):
            # Call the function directly
            result = routes.analyses.update_mao_defaults()
            
            # Verify the result
            assert isinstance(result, tuple)
            assert result[0]['success'] is False
            assert result[0]['message'] == 'Failed to update MAO defaults'
            assert result[1] == 500
