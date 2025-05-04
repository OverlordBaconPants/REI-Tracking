import pytest
import os
import json
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from utils.json_handler import read_json, write_json, validate_analysis_file

class TestJsonHandler:
    """Test suite for the json_handler module."""
    
    def test_read_json_file_not_found(self):
        """Test read_json when file is not found."""
        with patch('os.path.exists', return_value=False), \
             patch('logging.warning') as mock_log:
            
            result = read_json('nonexistent_file.json')
            
            # Assert empty list is returned
            assert result == []
            
            # Assert warning is logged
            mock_log.assert_called_once()
            assert 'File not found' in mock_log.call_args[0][0]
    
    def test_read_json_empty_file(self):
        """Test read_json with an empty file."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="")), \
             patch('logging.warning') as mock_log:
            
            result = read_json('empty_file.json')
            
            # Assert empty list is returned
            assert result == []
            
            # Assert warning is logged
            mock_log.assert_called_once()
            assert 'Empty file' in mock_log.call_args[0][0]
    
    def test_read_json_valid_file(self):
        """Test read_json with a valid JSON file."""
        test_data = [{"key": "value"}, {"another_key": 123}]
        json_content = json.dumps(test_data)
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json_content)):
            
            result = read_json('valid_file.json')
            
            # Assert correct data is returned
            assert result == test_data
    
    def test_read_json_invalid_json(self):
        """Test read_json with invalid JSON content."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="{ invalid json }")), \
             patch('logging.error') as mock_log:
            
            result = read_json('invalid_file.json')
            
            # Assert empty list is returned
            assert result == []
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'Error decoding JSON' in mock_log.call_args[0][0]
    
    def test_write_json_success(self):
        """Test write_json with successful write."""
        test_data = {"key": "value"}
        mock_file = mock_open()
        
        with patch('builtins.open', mock_file):
            write_json('output_file.json', test_data)
            
            # Assert file was opened for writing
            mock_file.assert_called_once_with('output_file.json', 'w')
            
            # Assert json.dump was called with correct data
            handle = mock_file()
            handle.write.assert_called()  # json.dump calls write
    
    def test_write_json_error(self):
        """Test write_json with an error during writing."""
        test_data = {"key": "value"}
        
        with patch('builtins.open', side_effect=IOError("Test IO Error")), \
             patch('logging.error') as mock_log, \
             pytest.raises(IOError):
            
            write_json('error_file.json', test_data)
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'Error writing JSON' in mock_log.call_args[0][0]
    
    def test_validate_analysis_file_not_found(self):
        """Test validate_analysis_file when file is not found."""
        with patch('os.path.exists', return_value=False), \
             patch('logging.error') as mock_log:
            
            data, error = validate_analysis_file('nonexistent_file.json')
            
            # Assert correct return values
            assert data is None
            assert error == "File does not exist"
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'File not found' in mock_log.call_args[0][0]
    
    def test_validate_analysis_file_empty(self):
        """Test validate_analysis_file with an empty file."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="")), \
             patch('logging.error') as mock_log:
            
            data, error = validate_analysis_file('empty_file.json')
            
            # Assert correct return values
            assert data is None
            assert error == "File is empty"
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'Empty file' in mock_log.call_args[0][0]
    
    def test_validate_analysis_file_invalid_json(self):
        """Test validate_analysis_file with invalid JSON content."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="{ invalid json }")), \
             patch('logging.error') as mock_log:
            
            data, error = validate_analysis_file('invalid_file.json')
            
            # Assert correct return values
            assert data is None
            assert "Invalid JSON format" in error
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'Error decoding JSON' in mock_log.call_args[0][0]
    
    def test_validate_analysis_file_not_dict(self):
        """Test validate_analysis_file with JSON that's not a dictionary."""
        test_data = ["item1", "item2"]  # List, not a dict
        json_content = json.dumps(test_data)
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json_content)), \
             patch('logging.error') as mock_log:
            
            data, error = validate_analysis_file('list_file.json')
            
            # Assert correct return values
            assert data is None
            assert error == "Invalid data format"
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'Invalid data format' in mock_log.call_args[0][0]
    
    def test_validate_analysis_file_missing_fields(self):
        """Test validate_analysis_file with missing required fields."""
        test_data = {"some_field": "value"}  # Missing required fields
        json_content = json.dumps(test_data)
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json_content)), \
             patch('logging.error') as mock_log:
            
            data, error = validate_analysis_file('missing_fields.json')
            
            # Assert correct return values
            assert data is None
            assert "Missing required fields" in error
            assert "analysis_name" in error
            assert "analysis_type" in error
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'Missing required fields' in mock_log.call_args[0][0]
    
    def test_validate_analysis_file_valid(self):
        """Test validate_analysis_file with valid analysis data."""
        test_data = {
            "analysis_name": "Test Analysis",
            "analysis_type": "rental"
        }
        json_content = json.dumps(test_data)
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json_content)):
            
            data, error = validate_analysis_file('valid_analysis.json')
            
            # Assert correct return values
            assert data == test_data
            assert error is None
    
    def test_validate_analysis_file_io_error(self):
        """Test validate_analysis_file with an IO error."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=IOError("Test IO Error")), \
             patch('logging.error') as mock_log:
            
            data, error = validate_analysis_file('error_file.json')
            
            # Assert correct return values
            assert data is None
            assert "File read error" in error
            
            # Assert error is logged
            mock_log.assert_called_once()
            assert 'Error reading file' in mock_log.call_args[0][0]
    
    def test_validate_analysis_file_unexpected_error(self):
        """Test validate_analysis_file with an unexpected error."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=Exception("Unexpected test error")), \
             patch('logging.error') as mock_log:
            
            data, error = validate_analysis_file('error_file.json')
            
            # Assert correct return values
            assert data is None
            assert "Unexpected error" in error
            
            # Assert error is logged
            mock_log.assert_called_once()
