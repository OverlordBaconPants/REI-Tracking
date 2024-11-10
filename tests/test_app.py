import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, current_app
from app import app
from __init__ import create_app

class TestApp(unittest.TestCase):
    """Test suite for Flask application."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after tests."""
        self.app_context.pop()

    def test_app_exists(self):
        """Test that the app exists."""
        self.assertIsNotNone(current_app)
        self.assertIsInstance(current_app, Flask)

    def test_app_is_testing(self):
        """Test that the app is in testing mode."""
        self.assertTrue(current_app.config['TESTING'])

    def test_app_configuration(self):
        """Test app configuration settings."""
        self.assertIsNotNone(current_app.config['SECRET_KEY'])
        self.assertIsNotNone(current_app.config['USERS_FILE'])
        self.assertIsNotNone(current_app.config['PROPERTIES_FILE'])
        self.assertIsNotNone(current_app.config['TRANSACTIONS_FILE'])
        self.assertIsNotNone(current_app.config['CATEGORIES_FILE'])
        self.assertIsNotNone(current_app.config['UPLOAD_FOLDER'])

    def test_app_debug_mode(self):
        """Test app debug mode settings."""
        # Test production config
        prod_app = create_app('production')
        self.assertFalse(prod_app.debug)
        
        # Test development config
        dev_app = create_app('development')
        self.assertTrue(dev_app.debug)
        
        # Test testing config
        test_app = create_app('testing')
        self.assertFalse(test_app.debug)

    def test_app_extensions(self):
        """Test Flask extensions are properly initialized."""
        self.assertIsNotNone(current_app.login_manager)
        self.assertIsNotNone(current_app.session_interface)

    def test_blueprints_registered(self):
        """Test that all blueprints are registered."""
        blueprints = [
            'main',
            'auth',
            'analyses',
            'properties',
            'transactions',
            'dashboards',
            'api'
        ]
        
        for blueprint in blueprints:
            self.assertIn(blueprint, current_app.blueprints)

    def test_error_handlers(self):
        """Test error handlers are registered."""
        self.assertIn(404, current_app.error_handler_spec[None])
        self.assertIn(500, current_app.error_handler_spec[None])

    def test_static_folders(self):
        """Test static folder configuration."""
        self.assertTrue(current_app.static_folder.endswith('static'))
        self.assertEqual(current_app.static_url_path, '/static')

    def test_template_folders(self):
        """Test template folder configuration."""
        self.assertTrue(current_app.template_folder.endswith('templates'))

class TestAppConfiguration(unittest.TestCase):
    """Test suite for different app configurations."""

    def test_development_config(self):
        """Test development configuration."""
        app = create_app('development')
        self.assertTrue(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['TEMPLATES_AUTO_RELOAD'])

    def test_testing_config(self):
        """Test testing configuration."""
        app = create_app('testing')
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])

    def test_production_config(self):
        """Test production configuration."""
        app = create_app('production')
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])
        self.assertTrue(app.config['SESSION_COOKIE_SECURE'])
        self.assertTrue(app.config['REMEMBER_COOKIE_SECURE'])

    def test_invalid_config(self):
        """Test invalid configuration handling."""
        with self.assertRaises(ValueError):
            create_app('invalid_config')

class TestAppSecurity(unittest.TestCase):
    """Test suite for application security settings."""

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def test_security_headers(self):
        """Test security headers are set."""
        response = self.client.get('/')
        headers = response.headers
        
        self.assertIn('X-Content-Type-Options', headers)
        self.assertIn('X-Frame-Options', headers)
        self.assertIn('X-XSS-Protection', headers)
        self.assertIn('Content-Security-Policy', headers)

    def test_csrf_protection(self):
        """Test CSRF protection is enabled."""
        with self.app.test_request_context():
            self.assertTrue(current_app.config['WTF_CSRF_ENABLED'])

    def test_session_configuration(self):
        """Test session security configuration."""
        self.assertTrue(self.app.config['SESSION_COOKIE_HTTPONLY'])
        self.assertTrue(self.app.config['SESSION_COOKIE_SAMESITE'])

class TestAppIntegration(unittest.TestCase):
    """Test suite for application integration."""

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_home_page(self):
        """Test home page access."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        """Test login page access."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_static_files(self):
        """Test static file serving."""
        response = self.client.get('/static/css/styles.css')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/css', response.content_type)

    def test_404_handling(self):
        """Test 404 error handling."""
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)

    def test_500_handling(self):
        """Test 500 error handling."""
        @self.app.route('/trigger-error')
        def trigger_error():
            raise Exception('Test error')
            
        response = self.client.get('/trigger-error')
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()