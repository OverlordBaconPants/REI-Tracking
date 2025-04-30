import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from werkzeug.security import generate_password_hash, check_password_hash
from services.user_service import (
    load_users, save_users, get_user_by_email, create_user,
    hash_password, verify_password, update_user_password
)

class TestUserService(unittest.TestCase):
    """Test suite for user service functions."""

    def setUp(self):
        """Set up test environment."""
        self.test_user = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': generate_password_hash('password123'),
            'phone': '123-456-7890',
            'role': 'User'
        }
        
        self.test_users = {
            'test@example.com': self.test_user
        }

    def test_hash_password(self):
        """Test password hashing."""
        password = 'password123'
        hashed = hash_password(password)
        
        # Verify it's a valid hash
        self.assertTrue(hashed.startswith('pbkdf2:sha256'))
        
        # Verify it's not the original password
        self.assertNotEqual(hashed, password)
        
        # Verify we can verify it
        self.assertTrue(check_password_hash(hashed, password))

    def test_verify_password(self):
        """Test password verification."""
        # Test correct password
        self.assertTrue(
            verify_password(
                self.test_user['password'],
                'password123'
            )
        )
        
        # Test incorrect password
        self.assertFalse(
            verify_password(
                self.test_user['password'],
                'wrongpassword'
            )
        )
        
        # Test empty password
        self.assertFalse(
            verify_password(
                self.test_user['password'],
                ''
            )
        )

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_users(self, mock_json_load, mock_file):
        """Test user loading."""
        # Test successful load
        mock_json_load.return_value = self.test_users
        users = load_users()
        self.assertEqual(users, self.test_users)
        
        # Test file not found
        mock_file.side_effect = FileNotFoundError
        users = load_users()
        self.assertEqual(users, {})
        
        # Test invalid JSON
        mock_file.side_effect = None
        mock_json_load.side_effect = json.JSONDecodeError('Test error', '', 0)
        users = load_users()
        self.assertEqual(users, {})

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_users(self, mock_json_dump, mock_file):
        """Test user saving."""
        save_users(self.test_users)
        mock_json_dump.assert_called_once()
        mock_file.assert_called_once()
        
        # Verify the data being saved
        saved_data = mock_json_dump.call_args[0][0]
        self.assertEqual(saved_data, self.test_users)

    @patch('services.user_service.load_users')
    def test_get_user_by_email(self, mock_load_users):
        """Test user retrieval by email."""
        # Test existing user
        mock_load_users.return_value = self.test_users
        user = get_user_by_email('test@example.com')
        self.assertEqual(user, self.test_user)
        
        # Test non-existent user
        user = get_user_by_email('nonexistent@example.com')
        self.assertIsNone(user)
        
        # Test with empty users
        mock_load_users.return_value = {}
        user = get_user_by_email('test@example.com')
        self.assertIsNone(user)

    @patch('services.user_service.load_users')
    @patch('services.user_service.save_users')
    def test_create_user(self, mock_save_users, mock_load_users):
        """Test user creation."""
        # Test creating new user
        mock_load_users.return_value = {}
        result = create_user(
            'new@example.com',
            'New User',
            'password123',
            '123-456-7890'
        )
        self.assertTrue(result)
        mock_save_users.assert_called_once()
        
        # Test creating existing user
        mock_load_users.return_value = self.test_users
        result = create_user(
            'test@example.com',
            'Test User',
            'password123',
            '123-456-7890'
        )
        self.assertFalse(result)

    @patch('services.user_service.load_users')
    @patch('services.user_service.save_users')
    def test_update_user_password(self, mock_save_users, mock_load_users):
        """Test password updates."""
        # Test updating existing user
        mock_load_users.return_value = self.test_users
        result = update_user_password('test@example.com', 'newpassword123')
        self.assertTrue(result)
        mock_save_users.assert_called_once()
        
        # Test updating non-existent user
        result = update_user_password('nonexistent@example.com', 'newpassword123')
        self.assertFalse(result)

class TestUserServiceEdgeCases(unittest.TestCase):
    """Test suite for edge cases and error handling."""

    def setUp(self):
        self.test_users = {
            'test@example.com': {
                'name': 'Test User',
                'email': 'test@example.com',
                'password': generate_password_hash('password123'),
                'phone': '123-456-7890',
                'role': 'User'
            }
        }

    def test_create_user_invalid_data(self):
        """Test user creation with invalid data."""
        with patch('services.user_service.load_users') as mock_load:
            mock_load.return_value = {}
            
            # Test with empty email
            result = create_user('', 'Test User', 'password123', '123-456-7890')
            self.assertFalse(result)
            
            # Test with empty name
            result = create_user('test@example.com', '', 'password123', '123-456-7890')
            self.assertFalse(result)
            
            # Test with empty password
            result = create_user('test@example.com', 'Test User', '', '123-456-7890')
            self.assertFalse(result)

    def test_password_complexity(self):
        """Test password hashing with various complexities."""
        test_cases = [
            'short',                    # Too short
            'a' * 100,                  # Very long
            '!@#$%^&*()',              # Special characters
            '12345678',                # Numbers only
            'abcdefgh',                # Letters only
            'password123!@#'           # Mixed
        ]
        
        for password in test_cases:
            with self.subTest(password=password):
                hashed = hash_password(password)
                self.assertTrue(verify_password(hashed, password))

    @patch('json.load')
    def test_load_users_corrupted_data(self, mock_json_load):
        """Test handling of corrupted user data."""
        # Test with invalid JSON structure
        mock_json_load.return_value = ['invalid', 'user', 'data']
        users = load_users()
        self.assertEqual(users, {})
        
        # Test with missing required fields
        mock_json_load.return_value = {
            'test@example.com': {'name': 'Test User'}  # Missing required fields
        }
        users = load_users()
        self.assertTrue(isinstance(users, dict))

    def test_password_verification_edge_cases(self):
        """Test password verification with edge cases."""
        # Create a hash of an empty password
        empty_hash = hash_password('')
        
        test_cases = [
            ('', empty_hash),           # Empty password
            (None, empty_hash),         # None password
            ('password123', 'invalid'), # Invalid hash
            ('password123', '')         # Empty hash
        ]
        
        for password, hash_value in test_cases:
            with self.subTest(password=password):
                result = verify_password(hash_value, password)
                self.assertFalse(result)

    @patch('services.user_service.load_users')
    @patch('services.user_service.save_users')
    def test_concurrent_user_updates(self, mock_save, mock_load):
        """Test handling of concurrent user updates."""
        # Simulate concurrent updates by changing data between load and save
        initial_users = self.test_users.copy()
        updated_users = self.test_users.copy()
        updated_users['test@example.com']['name'] = 'Updated Name'
        
        mock_load.side_effect = [initial_users, updated_users]
        
        # Attempt to update password
        result = update_user_password('test@example.com', 'newpassword123')
        self.assertTrue(result)
        
        # Verify the save operation included both changes
        saved_data = mock_save.call_args[0][0]
        self.assertEqual(saved_data['test@example.com']['name'], 'Updated Name')
        self.assertTrue(
            verify_password(
                saved_data['test@example.com']['password'],
                'newpassword123'
            )
        )

if __name__ == '__main__':
    unittest.main()