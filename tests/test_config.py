"""
Tests for the config module.

This module provides tests for the config module, including
environment-specific configuration and validation.
"""

import os
import pytest
from pathlib import Path

from src.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig, get_config


def test_base_config():
    """Test the base configuration."""
    config = Config()
    
    # Check that the base configuration has the expected attributes
    assert hasattr(config, 'SECRET_KEY')
    assert hasattr(config, 'DEBUG')
    assert hasattr(config, 'TESTING')
    assert hasattr(config, 'MAX_CONTENT_LENGTH')
    assert hasattr(config, 'UPLOAD_EXTENSIONS')
    assert hasattr(config, 'GEOAPIFY_API_KEY')
    assert hasattr(config, 'RENTCAST_API_KEY')
    assert hasattr(config, 'USERS_FILE')
    assert hasattr(config, 'PROPERTIES_FILE')
    assert hasattr(config, 'TRANSACTIONS_FILE')
    assert hasattr(config, 'CATEGORIES_FILE')
    assert hasattr(config, 'LOG_LEVEL')
    assert hasattr(config, 'LOG_FORMAT')
    assert hasattr(config, 'LOG_FILE')
    
    # Check that the base configuration has the expected values
    assert config.DEBUG is False
    assert config.TESTING is False
    assert config.MAX_CONTENT_LENGTH == 5 * 1024 * 1024  # 5MB
    assert config.UPLOAD_EXTENSIONS == ['.jpg', '.jpeg', '.png', '.pdf']
    assert config.LOG_LEVEL == 'INFO'
    assert config.LOG_FORMAT == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def test_development_config():
    """Test the development configuration."""
    config = DevelopmentConfig()
    
    # Check that the development configuration has the expected values
    assert config.DEBUG is True
    assert config.TESTING is False
    assert config.LOG_LEVEL == 'DEBUG'


def test_testing_config():
    """Test the testing configuration."""
    config = TestingConfig()
    
    # Check that the testing configuration has the expected values
    assert config.DEBUG is True
    assert config.TESTING is True
    
    # Check that the testing configuration uses test data files
    assert config.USERS_FILE.name == 'test_users.json'
    assert config.PROPERTIES_FILE.name == 'test_properties.json'
    assert config.TRANSACTIONS_FILE.name == 'test_transactions.json'
    assert config.CATEGORIES_FILE.name == 'test_categories.json'


def test_production_config():
    """Test the production configuration."""
    config = ProductionConfig()
    
    # Check that the production configuration has the expected values
    assert config.DEBUG is False
    assert config.TESTING is False
    
    # Test validation with missing API key
    with pytest.raises(ValueError):
        # Set SECRET_KEY to a non-default value to isolate the API key validation
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['GEOAPIFY_API_KEY'] = ''
        config.validate()
    
    # Test validation with default SECRET_KEY
    with pytest.raises(ValueError):
        os.environ['SECRET_KEY'] = 'dev-key-change-in-production'
        os.environ['GEOAPIFY_API_KEY'] = 'test-api-key'
        config.validate()


def test_get_config():
    """Test the get_config function."""
    # Test with development environment
    os.environ['FLASK_ENV'] = 'development'
    config = get_config()
    assert config == DevelopmentConfig
    
    # Test with testing environment
    os.environ['FLASK_ENV'] = 'testing'
    config = get_config()
    assert config == TestingConfig
    
    # Test with production environment
    os.environ['FLASK_ENV'] = 'production'
    config = get_config()
    assert config == ProductionConfig
    
    # Test with unknown environment
    os.environ['FLASK_ENV'] = 'unknown'
    config = get_config()
    assert config == DevelopmentConfig
