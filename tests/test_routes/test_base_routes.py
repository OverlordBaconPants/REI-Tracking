"""
Tests for the base routes.

This module provides tests for the base routes, including
health check and static file routes.
"""

import pytest
import json
import os

from src.routes.base_routes import blueprint


def test_health_check(app_client):
    """Test the health check endpoint."""
    response = app_client.get('/health')
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response is JSON
    assert response.content_type == 'application/json'
    
    # Check that the response has the expected data
    data = json.loads(response.data)
    assert 'status' in data
    assert 'version' in data
    assert data['status'] == 'ok'
    assert data['version'] == '1.0.0'


def test_api_version(app_client):
    """Test the API version endpoint."""
    response = app_client.get('/api/version')
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response is JSON
    assert response.content_type == 'application/json'
    
    # Check that the response has the expected data
    data = json.loads(response.data)
    assert 'version' in data
    assert 'name' in data
    assert data['version'] == '1.0.0'
    assert data['name'] == 'REI-Tracker API'


def test_serve_upload(app_client, temp_data_dir):
    """Test the serve upload endpoint."""
    # Create a test file
    test_file_content = b'Test file content'
    test_filename = 'test_file.txt'
    test_file_path = os.path.join(temp_data_dir, 'uploads', test_filename)
    
    with open(test_file_path, 'wb') as f:
        f.write(test_file_content)
    
    # Request the file
    response = app_client.get(f'/uploads/{test_filename}')
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response has the expected data
    assert response.data == test_file_content


def test_serve_upload_not_found(app_client):
    """Test the serve upload endpoint with a non-existent file."""
    response = app_client.get('/uploads/non_existent_file.txt')
    
    # Check that the response is not found
    assert response.status_code == 404


def test_not_found(app_client):
    """Test the 404 error handler."""
    response = app_client.get('/non_existent_endpoint')
    
    # Check that the response is not found
    assert response.status_code == 404
    
    # Check that the response is JSON
    assert response.content_type == 'application/json'
    
    # Check that the response has the expected data
    data = json.loads(response.data)
    assert 'error' in data
    assert 'code' in data['error']
    assert 'message' in data['error']
    assert data['error']['code'] == 404
    assert data['error']['message'] == 'Not Found'
