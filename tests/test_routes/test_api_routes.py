import unittest
from unittest.mock import patch, mock_open, MagicMock
from flask import Flask, current_app
import json
import requests
from datetime import datetime
from api import api_bp, ValidationError, GeoapifyResult

class TestAPIRoutes(unittest.TestCase):
    """Test suite for API routes."""

    def setUp(self):
        """Set up test environment before each test."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['CATEGORIES_FILE'] = 'test_categories.json'
        self.app.config['GEOAPIFY_API_KEY'] = 'test_api_key'
        self.app.register_blueprint(api_bp, url_prefix='/api')
        self.client = self.app.test_client()
        
        # Sample test data
        self.test_categories = {
            "INCOME": ["Rent", "Laundry", "Parking"],
            "EXPENSE": ["Mortgage", "Insurance", "Taxes"]
        }
        
        self.test_geoapify_response = {
            "results": [
                {
                    "formatted": "123 Test St, Test City, TC 12345",
                    "lat": 40.7128,
                    "lon": -74.0060
                }
            ]
        }

    def test_get_categories_success(self):
        """Test successful retrieval of categories."""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_categories))):
            response = self.client.get('/api/categories')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data, self.test_categories)

    def test_get_categories_with_type(self):
        """Test getting categories filtered by type."""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_categories))):
            response = self.client.get('/api/categories?type=INCOME')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data, self.test_categories['INCOME'])

    def test_get_categories_file_error(self):
        """Test error handling when categories file cannot be read."""
        with patch('builtins.open', side_effect=IOError('File not found')):
            response = self.client.get('/api/categories')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 500)
            self.assertIn('error', data)
            self.assertIn('File not found', data['error'])

    def test_get_categories_invalid_json(self):
        """Test error handling with invalid JSON in categories file."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            response = self.client.get('/api/categories')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 500)
            self.assertIn('error', data)
            self.assertIn('Failed to load categories', data['error'])

    @patch('requests.get')
    def test_autocomplete_success(self, mock_get):
        """Test successful address autocomplete."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = self.test_geoapify_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = self.client.get('/api/autocomplete?query=123+Test+St')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(isinstance(data['data'], list))
        self.assertEqual(len(data['data']), 1)
        
        # Verify result structure
        result = data['data'][0]
        self.assertIn('formatted', result)
        self.assertIn('lat', result)
        self.assertIn('lon', result)

    def test_autocomplete_missing_query(self):
        """Test autocomplete with missing query parameter."""
        response = self.client.get('/api/autocomplete')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('Missing required parameter', data['error'])

    def test_autocomplete_short_query(self):
        """Test autocomplete with too short query."""
        response = self.client.get('/api/autocomplete?query=a')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('must be at least', data['error'])

    @patch('requests.get')
    def test_autocomplete_api_error(self, mock_get):
        """Test handling of Geoapify API errors."""
        mock_get.side_effect = requests.RequestException('API Connection Error')
        
        response = self.client.get('/api/autocomplete?query=123+Test+St')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 503)
        self.assertIn('error', data)
        self.assertIn('Failed to connect to Geoapify', data['error'])

    def test_autocomplete_missing_api_key(self):
        """Test handling of missing API key."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(api_bp, url_prefix='/api')
        client = app.test_client()
        
        response = client.get('/api/autocomplete?query=123+Test+St')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', data)
        self.assertIn('API key is not configured', data['error'])

    def test_test_endpoint(self):
        """Test the test endpoint."""
        response = self.client.get('/api/test')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'API is working')
        self.assertTrue('timestamp' in data)
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(data['timestamp'])
        except ValueError:
            self.fail('Invalid timestamp format')

class TestGeoapifyResult(unittest.TestCase):
    """Test suite for GeoapifyResult data class."""

    def test_valid_result(self):
        """Test creating GeoapifyResult with valid data."""
        data = {
            'formatted': '123 Test St',
            'lat': 40.7128,
            'lon': -74.0060
        }
        result = GeoapifyResult.from_dict(data)
        
        self.assertEqual(result.formatted, '123 Test St')
        self.assertEqual(result.lat, 40.7128)
        self.assertEqual(result.lon, -74.0060)

    def test_invalid_result_format(self):
        """Test handling of invalid result format."""
        invalid_data = ['not', 'a', 'dict']
        
        with self.assertRaises(ValidationError) as context:
            GeoapifyResult.from_dict(invalid_data)
        self.assertIn('Invalid result format', str(context.exception))

    def test_missing_formatted_address(self):
        """Test handling of missing formatted address."""
        data = {
            'lat': 40.7128,
            'lon': -74.0060
        }
        
        with self.assertRaises(ValidationError) as context:
            GeoapifyResult.from_dict(data)
        self.assertIn('Missing formatted address', str(context.exception))

    def test_invalid_latitude(self):
        """Test handling of invalid latitude values."""
        test_cases = [
            {'formatted': '123 Test St', 'lat': 91, 'lon': 0},  # Too high
            {'formatted': '123 Test St', 'lat': -91, 'lon': 0},  # Too low
            {'formatted': '123 Test St', 'lat': 'invalid', 'lon': 0},  # Wrong type
        ]
        
        for data in test_cases:
            with self.subTest(data=data):
                with self.assertRaises(ValidationError) as context:
                    GeoapifyResult.from_dict(data)
                self.assertIn('Invalid latitude', str(context.exception))

    def test_invalid_longitude(self):
        """Test handling of invalid longitude values."""
        test_cases = [
            {'formatted': '123 Test St', 'lat': 0, 'lon': 181},  # Too high
            {'formatted': '123 Test St', 'lat': 0, 'lon': -181},  # Too low
            {'formatted': '123 Test St', 'lat': 0, 'lon': 'invalid'},  # Wrong type
        ]
        
        for data in test_cases:
            with self.subTest(data=data):
                with self.assertRaises(ValidationError) as context:
                    GeoapifyResult.from_dict(data)
                self.assertIn('Invalid longitude', str(context.exception))

class TestAPIValidator(unittest.TestCase):
    """Test suite for API validation classes."""

    def test_validate_api_key(self):
        """Test API key validation."""
        validator = APIValidator()
        
        # Valid key
        self.assertEqual(validator.validate_api_key('valid_api_key_12345'), 'valid_api_key_12345')
        
        # Invalid cases
        invalid_cases = [
            None,  # Missing key
            '',   # Empty key
            '123',  # Too short
            123,  # Wrong type
        ]
        
        for invalid_key in invalid_cases:
            with self.subTest(invalid_key=invalid_key):
                with self.assertRaises(ValidationError) as context:
                    validator.validate_api_key(invalid_key)
                self.assertIn('API key', str(context.exception))

    def test_validate_query_param(self):
        """Test query parameter validation."""
        validator = APIValidator()
        
        # Valid cases
        self.assertEqual(validator.validate_query_param('test', 'test'), 'test')
        self.assertEqual(validator.validate_query_param(' test ', 'test'), 'test')
        
        # Invalid cases
        invalid_cases = [
            ('', 'empty'),  # Empty string
            ('a', 'short', 2),  # Too short
            ('a' * 101, 'long', 1, 100),  # Too long
            ('123', 'pattern', 1, 100, r'^[a-zA-Z]+$'),  # Doesn't match pattern
        ]
        
        for value, name, *args in invalid_cases:
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    validator.validate_query_param(value, name, *args)

    def test_sanitize_string(self):
        """Test string sanitization."""
        validator = APIValidator()
        
        test_cases = [
            ('test', 'test'),
            ('test test', 'test+test'),
            ('test\x00test', 'test+test'),  # Control character
            ('  test  test  ', 'test+test'),  # Extra whitespace
            ('test@#$%^&*test', 'test%40%23%24%25%5E%26%2A+test'),  # Special characters
        ]
        
        for input_str, expected in test_cases:
            with self.subTest(input_str=input_str):
                self.assertEqual(validator.sanitize_string(input_str), expected)

if __name__ == '__main__':
    unittest.main()