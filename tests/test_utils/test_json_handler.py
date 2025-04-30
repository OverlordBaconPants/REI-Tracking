import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import os
from utils.json_handler import read_json, write_json, validate_analysis_file

class TestJSONHandler(unittest.TestCase):
    """Test suite for JSON handling utilities."""

    def setUp(self):
        """Set up test environment."""
        self.test_data = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR',
            'property_address': '123 Test St'
        }
        self.test_file = 'test.json'

    def test_read_json_success(self):
        """Test successful JSON file reading."""
        mock_content = json.dumps(self.test_data)
        with patch('builtins.open', mock_open(read_data=mock_content)):
            with patch('os.path.exists', return_value=True):
                result = read_json(self.test_file)
                self.assertEqual(result, self.test_data)

    def test_read_json_file_not_found(self):
        """Test reading non-existent JSON file."""
        with patch('os.path.exists', return_value=False):
            result = read_json(self.test_file)
            self.assertEqual(result, [])

    def test_read_json_empty_file(self):
        """Test reading empty JSON file."""
        with patch('builtins.open', mock_open(read_data='')):
            with patch('os.path.exists', return_value=True):
                result = read_json(self.test_file)
                self.assertEqual(result, [])

    def test_read_json_invalid_json(self):
        """Test reading invalid JSON content."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with patch('os.path.exists', return_value=True):
                result = read_json(self.test_file)
                self.assertEqual(result, [])

    def test_write_json_success(self):
        """Test successful JSON file writing."""
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            write_json(self.test_file, self.test_data)
            mock_file.assert_called_once_with(self.test_file, 'w')
            mock_file().write.assert_called()

    def test_write_json_failure(self):
        """Test JSON file writing failure."""
        with patch('builtins.open', side_effect=IOError("Test error")):
            with self.assertRaises(Exception):
                write_json(self.test_file, self.test_data)

    def test_validate_analysis_file_success(self):
        """Test successful analysis file validation."""
        mock_content = json.dumps(self.test_data)
        with patch('builtins.open', mock_open(read_data=mock_content)):
            with patch('os.path.exists', return_value=True):
                data, error = validate_analysis_file(self.test_file)
                self.assertIsNotNone(data)
                self.assertIsNone(error)
                self.assertEqual(data, self.test_data)

    def test_validate_analysis_file_not_found(self):
        """Test validation of non-existent analysis file."""
        with patch('os.path.exists', return_value=False):
            data, error = validate_analysis_file(self.test_file)
            self.assertIsNone(data)
            self.assertEqual(error, "File does not exist")

    def test_validate_analysis_file_empty(self):
        """Test validation of empty analysis file."""
        with patch('builtins.open', mock_open(read_data='')):
            with patch('os.path.exists', return_value=True):
                data, error = validate_analysis_file(self.test_file)
                self.assertIsNone(data)
                self.assertEqual(error, "File is empty")

    def test_validate_analysis_file_invalid_json(self):
        """Test validation of file with invalid JSON."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with patch('os.path.exists', return_value=True):
                data, error = validate_analysis_file(self.test_file)
                self.assertIsNone(data)
                self.assertIn("Invalid JSON format", error)

    def test_validate_analysis_file_missing_fields(self):
        """Test validation of file with missing required fields."""
        invalid_data = {'property_address': '123 Test St'}  # Missing required fields
        mock_content = json.dumps(invalid_data)
        with patch('builtins.open', mock_open(read_data=mock_content)):
            with patch('os.path.exists', return_value=True):
                data, error = validate_analysis_file(self.test_file)
                self.assertIsNone(data)
                self.assertIn("Missing required fields", error)

    def test_validate_analysis_file_invalid_format(self):
        """Test validation of file with invalid data format."""
        invalid_data = ['not', 'a', 'dictionary']
        mock_content = json.dumps(invalid_data)
        with patch('builtins.open', mock_open(read_data=mock_content)):
            with patch('os.path.exists', return_value=True):
                data, error = validate_analysis_file(self.test_file)
                self.assertIsNone(data)
                self.assertEqual(error, "Invalid data format")

class TestJSONHandlerEdgeCases(unittest.TestCase):
    """Test suite for JSON handler edge cases."""

    def test_read_json_special_characters(self):
        """Test reading JSON with special characters."""
        test_data = {
            'name': 'Test \u0041\u0042\u0043',  # Unicode characters
            'path': 'C:\\path\\to\\file'        # Escaped backslashes
        }
        mock_content = json.dumps(test_data)
        with patch('builtins.open', mock_open(read_data=mock_content)):
            with patch('os.path.exists', return_value=True):
                result = read_json('test.json')
                self.assertEqual(result, test_data)

    def test_write_json_special_characters(self):
        """Test writing JSON with special characters."""
        test_data = {
            'name': 'Test \u0041\u0042\u0043',
            'path': 'C:\\path\\to\\file'
        }
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            write_json('test.json', test_data)
            mock_file.assert_called_once_with('test.json', 'w')
            written_data = json.loads(mock_file().write.call_args[0][0])
            self.assertEqual(written_data, test_data)

    def test_read_json_large_file(self):
        """Test reading large JSON file."""
        large_data = {'key' + str(i): 'value' + str(i) for i in range(1000)}
        mock_content = json.dumps(large_data)
        with patch('builtins.open', mock_open(read_data=mock_content)):
            with patch('os.path.exists', return_value=True):
                result = read_json('test.json')
                self.assertEqual(result, large_data)

    def test_write_json_recursive_structure(self):
        """Test writing JSON with recursive data structure."""
        test_data = {
            'name': 'Test',
            'nested': {
                'level1': {
                    'level2': {
                        'level3': 'value'
                    }
                }
            }
        }
        mock_file = mock_open()
        with patch('builtins.open', mock_file):
            write_json('test.json', test_data)
            mock_file.assert_called_once_with('test.json', 'w')
            written_data = json.loads(mock_file().write.call_args[0][0])
            self.assertEqual(written_data, test_data)

    def test_validate_analysis_file_malformed_json(self):
        """Test validation of malformed JSON files."""
        test_cases = [
            '{missing: quote}',
            '{"unclosed": "string}',
            '{"trailing": "comma",}',
            '[1, 2, 3,]'
        ]
        
        for test_case in test_cases:
            with self.subTest(test_case=test_case):
                with patch('builtins.open', mock_open(read_data=test_case)):
                    with patch('os.path.exists', return_value=True):
                        data, error = validate_analysis_file('test.json')
                        self.assertIsNone(data)
                        self.assertIn("Invalid JSON format", error)

if __name__ == '__main__':
    unittest.main()