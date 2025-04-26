"""
Tests for the file_utils module.

This module provides tests for the file utilities, including
atomic JSON file operations and file validation.
"""

import os
import pytest
import json
import tempfile
import uuid
from pathlib import Path

from src.utils.file_utils import AtomicJsonFile, validate_file_extension, generate_secure_filename, save_uploaded_file


def test_atomic_json_file_read_write():
    """Test AtomicJsonFile read and write operations."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create an AtomicJsonFile instance
        json_file = AtomicJsonFile[dict](temp_path)
        
        # Write data to the file
        test_data = {'key': 'value', 'number': 42}
        json_file.write(test_data)
        
        # Read data from the file
        read_data = json_file.read()
        
        # Check that the read data matches the written data
        assert read_data == test_data
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_atomic_json_file_read_nonexistent():
    """Test AtomicJsonFile read operation with a nonexistent file."""
    # Generate a path that doesn't exist
    temp_path = f"/tmp/nonexistent-{uuid.uuid4()}.json"
    
    # Create an AtomicJsonFile instance
    json_file = AtomicJsonFile[dict](temp_path)
    
    # Read with default value
    default_value = {'default': True}
    read_data = json_file.read(default=default_value)
    
    # Check that the read data is the default value
    assert read_data == default_value
    
    # Read without default value
    with pytest.raises(FileNotFoundError):
        json_file.read()


def test_atomic_json_file_append():
    """Test AtomicJsonFile append operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create an AtomicJsonFile instance
        json_file = AtomicJsonFile[list](temp_path)
        
        # Write initial data to the file
        initial_data = [1, 2, 3]
        json_file.write(initial_data)
        
        # Append an item
        json_file.append(4)
        
        # Read data from the file
        read_data = json_file.read()
        
        # Check that the read data includes the appended item
        assert read_data == [1, 2, 3, 4]
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_atomic_json_file_append_dict():
    """Test AtomicJsonFile append operation with a dictionary."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create an AtomicJsonFile instance
        json_file = AtomicJsonFile[dict](temp_path)
        
        # Write initial data to the file
        initial_data = {'key1': 'value1'}
        json_file.write(initial_data)
        
        # Append a key-value pair
        json_file.append('value2', key='key2')
        
        # Read data from the file
        read_data = json_file.read()
        
        # Check that the read data includes the appended key-value pair
        assert read_data == {'key1': 'value1', 'key2': 'value2'}
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_validate_file_extension():
    """Test validate_file_extension function."""
    # Test with allowed extensions
    assert validate_file_extension('test.jpg') is True
    assert validate_file_extension('test.jpeg') is True
    assert validate_file_extension('test.png') is True
    assert validate_file_extension('test.pdf') is True
    
    # Test with uppercase extensions
    assert validate_file_extension('test.JPG') is True
    assert validate_file_extension('test.PDF') is True
    
    # Test with disallowed extensions
    assert validate_file_extension('test.exe') is False
    assert validate_file_extension('test.js') is False
    assert validate_file_extension('test.html') is False
    
    # Test with custom allowed extensions
    assert validate_file_extension('test.txt', ['.txt']) is True
    assert validate_file_extension('test.jpg', ['.txt']) is False


def test_generate_secure_filename():
    """Test generate_secure_filename function."""
    # Test with various file extensions
    filename = generate_secure_filename('test.jpg')
    assert filename.endswith('.jpg')
    assert len(filename) > 36  # UUID (36 chars) + extension
    
    filename = generate_secure_filename('test.PDF')
    assert filename.endswith('.pdf')  # Should be lowercase
    
    # Test that the generated filenames are unique
    filename1 = generate_secure_filename('test.jpg')
    filename2 = generate_secure_filename('test.jpg')
    assert filename1 != filename2


def test_save_uploaded_file(temp_data_dir):
    """Test save_uploaded_file function."""
    # Create test file data
    file_data = b'Test file content'
    original_filename = 'test.jpg'
    
    # Save the file
    filename = save_uploaded_file(file_data, original_filename)
    
    # Check that the file exists
    file_path = os.path.join(temp_data_dir, 'uploads', filename)
    assert os.path.exists(file_path)
    
    # Check that the file has the correct content
    with open(file_path, 'rb') as f:
        assert f.read() == file_data
    
    # Check that the file has the correct extension
    assert filename.endswith('.jpg')
    
    # Test with invalid extension
    with pytest.raises(ValueError):
        save_uploaded_file(file_data, 'test.exe')
