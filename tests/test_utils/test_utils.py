import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, flash, url_for
from flask_login import current_user
from utils.utils import admin_required

class TestUtils(unittest.TestCase):
    """Test suite for utility functions."""

    def setUp(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = self.app.test_client()
        
        # Create test route
        @self.app.route('/admin_test')
        @admin_required
        def admin_test():
            return 'Admin access granted'
        
        @self.app.route('/')
        def index():
            return 'Index page'

    def test_admin_required_with_admin(self):
        """Test admin_required decorator with admin user."""
        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                # Configure mock admin user
                mock_user.is_authenticated = True
                mock_user.role = 'Admin'
                
                # Create decorated function
                @admin_required
                def test_func():
                    return 'Success'
                
                # Test the function
                result = test_func()
                self.assertEqual(result, 'Success')

    def test_admin_required_with_regular_user(self):
        """Test admin_required decorator with regular user."""
        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                # Configure mock regular user
                mock_user.is_authenticated = True
                mock_user.role = 'User'
                
                # Create decorated function
                @admin_required
                def test_func():
                    return 'Success'
                
                # Test the function
                result, status_code = test_func()
                self.assertEqual(status_code, 403)
                self.assertIsInstance(result, str)  # Should be redirect response

    def test_admin_required_unauthenticated(self):
        """Test admin_required decorator with unauthenticated user."""
        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                # Configure mock unauthenticated user
                mock_user.is_authenticated = False
                
                # Create decorated function
                @admin_required
                def test_func():
                    return 'Success'
                
                # Test the function
                result, status_code = test_func()
                self.assertEqual(status_code, 403)
                self.assertIsInstance(result, str)  # Should be redirect response

    def test_admin_required_flash_message(self):
        """Test flash message when access is denied."""
        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                # Configure mock regular user
                mock_user.is_authenticated = True
                mock_user.role = 'User'
                
                # Create decorated function
                @admin_required
                def test_func():
                    return 'Success'
                
                # Test the function with flash message capture
                with self.app.test_client() as client:
                    test_func()
                    # Get flashed messages
                    messages = [msg for msg in self.app._get_current_object().session.get('_flashes', [])]
                    self.assertTrue(any('permission' in msg[1] for msg in messages))

    def test_admin_required_redirect(self):
        """Test redirect when access is denied."""
        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                # Configure mock regular user
                mock_user.is_authenticated = True
                mock_user.role = 'User'
                
                # Create decorated function
                @admin_required
                def test_func():
                    return 'Success'
                
                # Test the function
                result, _ = test_func()
                self.assertIn('/', result.location)  # Should redirect to index

class TestUtilsIntegration(unittest.TestCase):
    """Integration tests for utility functions."""

    def setUp(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        
        # Register routes
        @self.app.route('/admin_only')
        @admin_required
        def admin_only():
            return 'Admin only content'
            
        @self.app.route('/')
        def index():
            return 'Index page'
            
        self.client = self.app.test_client()

    def test_admin_endpoint_with_admin(self):
        """Test admin endpoint with admin user."""
        with patch('flask_login.current_user') as mock_user:
            # Configure mock admin user
            mock_user.is_authenticated = True
            mock_user.role = 'Admin'
            
            response = self.client.get('/admin_only')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode(), 'Admin only content')

    def test_admin_endpoint_with_regular_user(self):
        """Test admin endpoint with regular user."""
        with patch('flask_login.current_user') as mock_user:
            # Configure mock regular user
            mock_user.is_authenticated = True
            mock_user.role = 'User'
            
            response = self.client.get('/admin_only')
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(response.data.decode(), 'Admin only content')

    def test_admin_endpoint_unauthenticated(self):
        """Test admin endpoint with unauthenticated user."""
        with patch('flask_login.current_user') as mock_user:
            # Configure mock unauthenticated user
            mock_user.is_authenticated = False
            
            response = self.client.get('/admin_only')
            self.assertEqual(response.status_code, 403)
            self.assertNotEqual(response.data.decode(), 'Admin only content')

class TestUtilsEdgeCases(unittest.TestCase):
    """Test suite for edge cases and error handling."""

    def setUp(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = self.app.test_client()

    def test_admin_required_missing_role(self):
        """Test admin_required with user missing role attribute."""
        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                # Configure mock user without role
                mock_user.is_authenticated = True
                del mock_user.role
                
                @admin_required
                def test_func():
                    return 'Success'
                
                result, status_code = test_func()
                self.assertEqual(status_code, 403)

    def test_admin_required_custom_role(self):
        """Test admin_required with custom role values."""
        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                test_cases = [
                    ('admin', False),      # Lowercase
                    ('ADMIN', False),      # Uppercase
                    ('Admin ', False),     # Extra space
                    (' Admin', False),     # Leading space
                    ('Admin', True),       # Correct case
                    ('SuperAdmin', False)  # Different admin type
                ]
                
                @admin_required
                def test_func():
                    return 'Success'
                
                for role, should_succeed in test_cases:
                    with self.subTest(role=role):
                        mock_user.is_authenticated = True
                        mock_user.role = role
                        
                        result = test_func()
                        if should_succeed:
                            self.assertEqual(result, 'Success')
                        else:
                            self.assertIsInstance(result, tuple)
                            self.assertEqual(result[1], 403)

    def test_admin_required_multiple_decorators(self):
        """Test admin_required with multiple decorators."""
        def other_decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                return f(*args, **kwargs)
            return decorated

        with self.app.test_request_context():
            with patch('flask_login.current_user') as mock_user:
                mock_user.is_authenticated = True
                mock_user.role = 'Admin'
                
                @admin_required
                @other_decorator
                def test_func():
                    return 'Success'
                
                result = test_func()
                self.assertEqual(result, 'Success')

if __name__ == '__main__':
    unittest.main()