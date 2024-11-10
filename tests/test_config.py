import unittest
from unittest.mock import patch
import os
import tempfile
from config import Config

class TestConfig(unittest.TestCase):
    """Test suite for application configuration."""

    def setUp(self):
        """Set up test environment."""
        self.base_dir = os.path.abspath(os.path.dirname(Config.__file__))
        self.original_env = dict(os.environ)

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_secret_key(self):
        """Test SECRET_KEY configuration."""
        # Test with environment variable
        with patch.dict('os.environ', {'SECRET_KEY': 'test-secret-key'}):
            self.assertEqual(Config.SECRET_KEY, 'test-secret-key')
        
        # Test default value
        with patch.dict('os.environ', clear=True):
            self.assertEqual(Config.SECRET_KEY, 'you-will-never-guess')

    def test_directory_paths(self):
        """Test directory path configurations."""
        # Test BASE_DIR
        self.assertTrue(os.path.exists(Config.BASE_DIR))
        self.assertTrue(os.path.isabs(Config.BASE_DIR))
        
        # Test DATA_DIR
        self.assertEqual(Config.DATA_DIR, os.path.join(Config.BASE_DIR, 'data'))
        
        # Test UPLOAD_FOLDER
        self.assertEqual(Config.UPLOAD_FOLDER, os.path.join(Config.BASE_DIR, 'uploads'))

    def test_file_extensions(self):
        """Test allowed file extensions."""
        # Test ALLOWED_EXTENSIONS
        self.assertIsInstance(Config.ALLOWED_EXTENSIONS, set)
        self.assertEqual(
            Config.ALLOWED_EXTENSIONS,
            {'png', 'svg', 'pdf', 'jpg', 'csv', 'xls', 'xlsx'}
        )
        
        # Test ALLOWED_DOCUMENTATION_EXTENSIONS
        self.assertIsInstance(Config.ALLOWED_DOCUMENTATION_EXTENSIONS, set)
        self.assertEqual(
            Config.ALLOWED_DOCUMENTATION_EXTENSIONS,
            {'png', 'svg', 'pdf', 'jpg'}
        )
        
        # Test ALLOWED_IMPORT_EXTENSIONS
        self.assertIsInstance(Config.ALLOWED_IMPORT_EXTENSIONS, set)
        self.assertEqual(
            Config.ALLOWED_IMPORT_EXTENSIONS,
            {'csv', 'xls', 'xlsx'}
        )
        
        # Verify extension sets are distinct
        self.assertNotEqual(
            Config.ALLOWED_DOCUMENTATION_EXTENSIONS,
            Config.ALLOWED_IMPORT_EXTENSIONS
        )

    def test_file_paths(self):
        """Test JSON file path configurations."""
        # Test USERS_FILE
        self.assertTrue(os.path.join('data', 'users.json') in Config.USERS_FILE)
        
        # Test PROPERTIES_FILE
        self.assertTrue(os.path.join('data', 'properties.json') in Config.PROPERTIES_FILE)
        
        # Test TRANSACTIONS_FILE
        self.assertTrue(os.path.join('data', 'transactions.json') in Config.TRANSACTIONS_FILE)
        
        # Test CATEGORIES_FILE
        self.assertTrue(os.path.join('data', 'categories.json') in Config.CATEGORIES_FILE)
        
        # Test REIMBURSEMENTS_FILE
        self.assertTrue(os.path.join('data', 'reimbursements.json') in Config.REIMBURSEMENTS_FILE)

    def test_max_content_length(self):
        """Test maximum content length configuration."""
        # Test MAX_CONTENT_LENGTH is 5MB
        self.assertEqual(Config.MAX_CONTENT_LENGTH, 5 * 1024 * 1024)
        
        # Verify it's a positive integer
        self.assertIsInstance(Config.MAX_CONTENT_LENGTH, int)
        self.assertGreater(Config.MAX_CONTENT_LENGTH, 0)

    def test_api_key(self):
        """Test API key configuration."""
        self.assertIsInstance(Config.GEOAPIFY_API_KEY, str)
        self.assertTrue(len(Config.GEOAPIFY_API_KEY) > 0)

class TestConfigValidation(unittest.TestCase):
    """Test suite for configuration validation."""

    def test_directory_existence(self):
        """Test directory existence and permissions."""
        directories = [
            Config.BASE_DIR,
            Config.DATA_DIR,
            Config.UPLOAD_FOLDER
        ]
        
        for directory in directories:
            with self.subTest(directory=directory):
                # Test directory exists or can be created
                if not os.path.exists(directory):
                    os.makedirs(directory)
                self.assertTrue(os.path.exists(directory))
                
                # Test directory is writable
                test_file = os.path.join(directory, 'test_write')
                try:
                    with open(test_file, 'w') as f:
                        f.write('test')
                    self.assertTrue(os.path.exists(test_file))
                finally:
                    if os.path.exists(test_file):
                        os.remove(test_file)

    def test_file_permissions(self):
        """Test file permissions for JSON files."""
        json_files = [
            Config.USERS_FILE,
            Config.PROPERTIES_FILE,
            Config.TRANSACTIONS_FILE,
            Config.CATEGORIES_FILE,
            Config.REIMBURSEMENTS_FILE
        ]
        
        for file_path in json_files:
            with self.subTest(file_path=file_path):
                # Ensure directory exists
                directory = os.path.dirname(file_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)
                
                # Test file can be created and written to
                try:
                    with open(file_path, 'w') as f:
                        f.write('{}')
                    self.assertTrue(os.path.exists(file_path))
                    
                    # Test file can be read
                    with open(file_path, 'r') as f:
                        content = f.read()
                    self.assertEqual(content, '{}')
                finally:
                    if os.path.exists(file_path):
                        os.remove(file_path)

class TestConfigEdgeCases(unittest.TestCase):
    """Test suite for configuration edge cases."""

    def test_path_normalization(self):
        """Test path normalization."""
        # Test with different path separators
        self.assertEqual(
            os.path.normpath(Config.DATA_DIR),
            os.path.normpath(os.path.join(Config.BASE_DIR, 'data'))
        )

    def test_empty_environment_variables(self):
        """Test behavior with empty environment variables."""
        with patch.dict('os.environ', {'SECRET_KEY': ''}):
            self.assertEqual(Config.SECRET_KEY, 'you-will-never-guess')

    def test_special_characters_in_paths(self):
        """Test handling of special characters in paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            special_path = os.path.join(temp_dir, 'special!@#$%^&*()')
            os.makedirs(special_path)
            
            # Test absolute path resolution
            resolved_path = os.path.abspath(special_path)
            self.assertTrue(os.path.exists(resolved_path))

    def test_file_extension_case_sensitivity(self):
        """Test file extension case handling."""
        extensions = Config.ALLOWED_EXTENSIONS
        test_cases = [
            'test.PNG',
            'test.pdf',
            'test.JPG',
            'test.CSV'
        ]
        
        for filename in test_cases:
            with self.subTest(filename=filename):
                self.assertTrue(
                    any(filename.lower().endswith(ext) for ext in extensions)
                )

    def test_max_content_length_boundaries(self):
        """Test MAX_CONTENT_LENGTH boundaries."""
        max_length = Config.MAX_CONTENT_LENGTH
        
        # Test maximum file size is reasonable
        self.assertLess(max_length, 1024 * 1024 * 100)  # Less than 100MB
        self.assertGreater(max_length, 1024 * 1024)     # Greater than 1MB

if __name__ == '__main__':
    unittest.main()