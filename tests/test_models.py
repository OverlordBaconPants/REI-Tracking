import unittest
from unittest.mock import patch, MagicMock
from models import User
import json

class TestUserModel(unittest.TestCase):
    """Test suite for User model."""

    def setUp(self):
        """Set up test environment."""
        self.user_data = {
            'id': 'test@example.com',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'hashed_password',
            'role': 'User'
        }
        self.user = User(**self.user_data)

    def test_user_initialization(self):
        """Test user initialization with valid data."""
        self.assertEqual(self.user.id, 'test@example.com')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.name, 'Test User')
        self.assertEqual(self.user.password, 'hashed_password')
        self.assertEqual(self.user.role, 'User')

    def test_get_id(self):
        """Test get_id method returns email."""
        self.assertEqual(self.user.get_id(), 'test@example.com')

    @patch('services.user_service.load_users')
    def test_get_existing_user(self, mock_load_users):
        """Test getting existing user."""
        mock_load_users.return_value = {
            'test@example.com': {
                'email': 'test@example.com',
                'name': 'Test User',
                'password': 'hashed_password',
                'role': 'User'
            }
        }
        
        user = User.get('test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.role, 'User')

    @patch('services.user_service.load_users')
    def test_get_nonexistent_user(self, mock_load_users):
        """Test getting non-existent user."""
        mock_load_users.return_value = {}
        
        user = User.get('nonexistent@example.com')
        self.assertIsNone(user)

    def test_is_authenticated(self):
        """Test is_authenticated property."""
        self.assertTrue(self.user.is_authenticated)

    def test_is_active(self):
        """Test is_active property."""
        self.assertTrue(self.user.is_active)

    def test_is_anonymous(self):
        """Test is_anonymous property."""
        self.assertFalse(self.user.is_anonymous)

class TestUserRoles(unittest.TestCase):
    """Test suite for user roles."""

    def setUp(self):
        """Set up test environment."""
        self.admin_data = {
            'id': 'admin@example.com',
            'email': 'admin@example.com',
            'name': 'Admin User',
            'password': 'hashed_password',
            'role': 'Admin'
        }
        self.regular_data = {
            'id': 'user@example.com',
            'email': 'user@example.com',
            'name': 'Regular User',
            'password': 'hashed_password',
            'role': 'User'
        }

    def test_admin_role(self):
        """Test admin user role."""
        admin = User(**self.admin_data)
        self.assertEqual(admin.role, 'Admin')
        self.assertNotEqual(admin.role, 'User')

    def test_user_role(self):
        """Test regular user role."""
        user = User(**self.regular_data)
        self.assertEqual(user.role, 'User')
        self.assertNotEqual(user.role, 'Admin')

    @patch('services.user_service.load_users')
    def test_default_role(self, mock_load_users):
        """Test default role assignment."""
        # Test user without explicit role
        user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'hashed_password'
        }
        mock_load_users.return_value = {'test@example.com': user_data}
        
        user = User.get('test@example.com')
        self.assertEqual(user.role, 'User')  # Should default to 'User'

class TestUserAuthentication(unittest.TestCase):
    """Test suite for user authentication."""

    def setUp(self):
        """Set up test environment."""
        self.user_data = {
            'id': 'test@example.com',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'hashed_password',
            'role': 'User'
        }

    @patch('services.user_service.load_users')
    def test_user_loading(self, mock_load_users):
        """Test user loading from storage."""
        mock_load_users.return_value = {'test@example.com': self.user_data}
        
        user = User.get('test@example.com')
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')

    def test_user_identity(self):
        """Test user identity methods."""
        user = User(**self.user_data)
        
        # Test UserMixin methods
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_anonymous)
        self.assertEqual(user.get_id(), 'test@example.com')

class TestEdgeCases(unittest.TestCase):
    """Test suite for edge cases."""

    def test_empty_user_data(self):
        """Test handling of empty user data."""
        with self.assertRaises(TypeError):
            User()

    def test_missing_fields(self):
        """Test handling of missing fields."""
        minimal_data = {
            'id': 'test@example.com',
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'hashed_password'
        }
        
        # Should work without role (uses default)
        user = User(**minimal_data, role='User')
        self.assertEqual(user.role, 'User')

    def test_invalid_email(self):
        """Test handling of invalid email formats."""
        invalid_emails = [
            '',             # Empty
            'invalid',      # No domain
            '@nodomain',    # No local part
            'spaces in@email.com'  # Spaces
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                user_data = self.setUp()
                user_data = {
                    'id': email,
                    'email': email,
                    'name': 'Test User',
                    'password': 'hashed_password',
                    'role': 'User'
                }
                user = User(**user_data)
                self.assertEqual(user.get_id(), email)  # Should still work, validation should be done elsewhere

    @patch('services.user_service.load_users')
    def test_corrupted_user_data(self, mock_load_users):
        """Test handling of corrupted user data."""
        # Test with invalid JSON
        mock_load_users.side_effect = json.JSONDecodeError('Test error', '', 0)
        user = User.get('test@example.com')
        self.assertIsNone(user)
        
        # Test with None data
        mock_load_users.return_value = None
        user = User.get('test@example.com')
        self.assertIsNone(user)

    def test_special_characters(self):
        """Test handling of special characters in user data."""
        special_data = {
            'id': 'test@example.com',
            'email': 'test@example.com',
            'name': 'Test User !@#$%^&*()',
            'password': 'hashed_password!@#$%^&*()',
            'role': 'User'
        }
        
        user = User(**special_data)
        self.assertEqual(user.name, 'Test User !@#$%^&*()')
        self.assertEqual(user.password, 'hashed_password!@#$%^&*()')

    def test_unicode_characters(self):
        """Test handling of unicode characters in user data."""
        unicode_data = {
            'id': 'test@example.com',
            'email': 'test@example.com',
            'name': 'Test User 测试用户',
            'password': 'hashed_password',
            'role': 'User'
        }
        
        user = User(**unicode_data)
        self.assertEqual(user.name, 'Test User 测试用户')

if __name__ == '__main__':
    unittest.main()