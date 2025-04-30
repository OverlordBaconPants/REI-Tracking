import unittest
from unittest.mock import patch, MagicMock
from flask import url_for
from app import create_app
from auth import ValidationError, PasswordStrength, AuthValidator
import json

class TestAuthRoutes(unittest.TestCase):
    """Test suite for authentication routes."""

    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Sample test data
        self.valid_user_data = {
            'email': 'test@example.com',
            'password': 'Test123!@#',
            'confirm_password': 'Test123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+1234567890'
        }
        
        self.valid_login_data = {
            'email': 'test@example.com',
            'password': 'Test123!@#',
            'remember': True
        }

    def tearDown(self):
        """Clean up after each test."""
        self.ctx.pop()

    def test_signup_get(self):
        """Test GET signup page."""
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'signup.html', response.data)

    @patch('routes.auth.create_user')
    @patch('routes.auth.get_user_by_email')
    def test_signup_success(self, mock_get_user, mock_create):
        """Test successful user signup."""
        mock_get_user.return_value = None
        mock_create.return_value = True
        
        response = self.client.post('/signup', data=self.valid_user_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    @patch('routes.auth.get_user_by_email')
    def test_signup_existing_user(self, mock_get_user):
        """Test signup with existing email."""
        mock_get_user.return_value = {'email': 'test@example.com'}
        
        response = self.client.post('/signup', data=self.valid_user_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email address already exists', response.data)

    def test_signup_invalid_data(self):
        """Test signup with invalid data."""
        invalid_data = self.valid_user_data.copy()
        invalid_data['email'] = 'invalid_email'
        
        response = self.client.post('/signup', data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email format', response.data)

    def test_login_get(self):
        """Test GET login page."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login.html', response.data)

    @patch('routes.auth.get_user_by_email')
    @patch('routes.auth.verify_password')
    @patch('routes.auth.get_properties_for_user')
    def test_login_success(self, mock_get_properties, mock_verify, mock_get_user):
        """Test successful login."""
        mock_get_user.return_value = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'hashed_password',
            'role': 'User'
        }
        mock_verify.return_value = True
        mock_get_properties.return_value = [{'address': '123 Test St'}]
        
        response = self.client.post('/login', data=self.valid_login_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/main', response.location)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        invalid_data = self.valid_login_data.copy()
        invalid_data['password'] = 'wrong_password'
        
        response = self.client.post('/login', data=invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)

    def test_forgot_password_get(self):
        """Test GET forgot password page."""
        response = self.client.get('/forgot-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'forgot_password.html', response.data)

    @patch('routes.auth.get_user_by_email')
    @patch('routes.auth.update_user_password')
    def test_forgot_password_success(self, mock_update, mock_get_user):
        """Test successful password reset."""
        mock_get_user.return_value = {'email': 'test@example.com'}
        mock_update.return_value = True
        
        reset_data = {
            'email': 'test@example.com',
            'password': 'NewTest123!@#',
            'confirm_password': 'NewTest123!@#'
        }
        
        response = self.client.post('/forgot-password', data=reset_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_logout(self):
        """Test logout functionality."""
        with self.client:
            # First login
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = MagicMock(email='test@example.com')
                
                response = self.client.get('/logout')
                self.assertEqual(response.status_code, 302)
                self.assertIn('/', response.location)

class TestAuthValidator(unittest.TestCase):
    """Test suite for AuthValidator class."""

    def setUp(self):
        """Set up test environment."""
        self.validator = AuthValidator()

    def test_validate_email(self):
        """Test email validation."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+label@domain.com'
        ]
        
        invalid_emails = [
            '',
            'invalid_email',
            '@domain.com',
            'user@',
            'a' * 256 + '@domain.com'
        ]
        
        for email in valid_emails:
            self.assertTrue(self.validator.validate_email(email))
            
        for email in invalid_emails:
            self.validator.errors = []
            self.assertEqual(self.validator.validate_email(email), '')

    def test_validate_password(self):
        """Test password validation."""
        valid_passwords = [
            'Test123!@#',
            'ValidP@ssw0rd',
            'C0mplex!Pass'
        ]
        
        invalid_passwords = [
            '',
            'short',
            'no_numbers',
            'no_uppercase1',
            'NO_LOWERCASE1',
            'NoSpecialChars1'
        ]
        
        for password in valid_passwords:
            self.validator.errors = []
            self.assertTrue(self.validator.validate_password(password))
            
        for password in invalid_passwords:
            self.validator.errors = []
            self.assertEqual(self.validator.validate_password(password), '')

    def test_check_password_strength(self):
        """Test password strength checker."""
        test_cases = [
            ('weak123', PasswordStrength.WEAK),
            ('Better123', PasswordStrength.MEDIUM),
            ('Str0ng!P@ssword', PasswordStrength.STRONG)
        ]
        
        for password, expected_strength in test_cases:
            self.assertEqual(
                self.validator.check_password_strength(password),
                expected_strength
            )

    def test_validate_name(self):
        """Test name validation."""
        valid_names = [
            'John',
            'Mary Jane',
            "O'Connor",
            'Smith-Jones'
        ]
        
        invalid_names = [
            '',
            'A',
            'A' * 51,
            'Invalid123',
            'Invalid@Name'
        ]
        
        for name in valid_names:
            self.validator.errors = []
            self.assertTrue(self.validator.validate_name(name, 'first_name'))
            
        for name in invalid_names:
            self.validator.errors = []
            self.assertEqual(self.validator.validate_name(name, 'first_name'), '')

    def test_validate_phone(self):
        """Test phone number validation."""
        valid_phones = [
            '+1234567890',
            '1234567890',
            '+44123456789'
        ]
        
        invalid_phones = [
            'invalid',
            '123',
            '+abc123456789'
        ]
        
        for phone in valid_phones:
            self.validator.errors = []
            self.assertTrue(self.validator.validate_phone(phone))
            
        for phone in invalid_phones:
            self.validator.errors = []
            self.assertEqual(self.validator.validate_phone(phone), '')

    def test_validate_signup_data(self):
        """Test complete signup data validation."""
        valid_data = {
            'email': 'test@example.com',
            'password': 'Test123!@#',
            'confirm_password': 'Test123!@#',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+1234567890'
        }
        
        result = self.validator.validate_signup_data(valid_data)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        
        # Test with missing fields
        invalid_data = valid_data.copy()
        del invalid_data['email']
        
        result = self.validator.validate_signup_data(invalid_data)
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.errors) > 0)

class TestSecurityHeaders(unittest.TestCase):
    """Test suite for security headers."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def test_security_headers(self):
        """Test security headers are properly set."""
        response = self.client.get('/login')
        headers = response.headers
        
        self.assertIn('X-Content-Type-Options', headers)
        self.assertIn('X-Frame-Options', headers)
        self.assertIn('X-XSS-Protection', headers)
        self.assertIn('Strict-Transport-Security', headers)
        self.assertIn('Content-Security-Policy', headers)
        self.assertIn('Permissions-Policy', headers)
        self.assertIn('Referrer-Policy', headers)

    def test_csp_headers(self):
        """Test Content Security Policy headers."""
        response = self.client.get('/login')
        csp = response.headers.get('Content-Security-Policy')
        
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src", csp)
        self.assertIn("style-src", csp)
        self.assertIn("font-src", csp)
        self.assertIn("img-src", csp)
        self.assertIn("connect-src", csp)

class TestErrorHandlers(unittest.TestCase):
    """Test suite for error handlers."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def test_400_error(self):
        """Test 400 error handler."""
        response = self.client.post('/login', data='invalid-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'400.html', response.data)

    def test_404_error(self):
        """Test 404 error handler."""
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'404.html', response.data)

if __name__ == '__main__':
    unittest.main()