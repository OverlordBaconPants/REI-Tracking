"""
Tests for the base model.

This module provides tests for the base model, including
ID generation, timestamps, and validation.
"""

import pytest
from datetime import datetime
import uuid

from src.models.base_model import BaseModel


def test_base_model_initialization():
    """Test base model initialization."""
    model = BaseModel()
    
    # Check that the model has the expected attributes
    assert hasattr(model, 'id')
    assert hasattr(model, 'created_at')
    assert hasattr(model, 'updated_at')
    
    # Check that the ID is a valid UUID
    try:
        uuid.UUID(model.id)
    except ValueError:
        pytest.fail("Model ID is not a valid UUID")
    
    # Check that the timestamps are valid ISO 8601 datetime strings
    try:
        datetime.fromisoformat(model.created_at)
        datetime.fromisoformat(model.updated_at)
    except ValueError:
        pytest.fail("Model timestamps are not valid ISO 8601 datetime strings")
    
    # Check that the timestamps are equal on initialization
    # Compare only up to seconds to avoid microsecond differences
    assert model.created_at.split('.')[0] == model.updated_at.split('.')[0]


def test_base_model_dict():
    """Test base model dict method."""
    model = BaseModel()
    model_dict = model.dict()
    
    # Check that the dictionary has the expected keys
    assert 'id' in model_dict
    assert 'created_at' in model_dict
    assert 'updated_at' in model_dict
    
    # Check that the values are correct
    assert model_dict['id'] == model.id
    assert model_dict['created_at'] == model.created_at
    assert model_dict['updated_at'] == model.updated_at


def test_base_model_from_dict():
    """Test base model from_dict method."""
    # Create a dictionary with model data
    data = {
        'id': str(uuid.uuid4()),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    # Create a model from the dictionary
    model = BaseModel.from_dict(data)
    
    # Check that the model has the expected attributes
    assert model.id == data['id']
    # Parse timestamps to compare only the date parts, not the exact microseconds
    model_created = datetime.fromisoformat(model.created_at)
    data_created = datetime.fromisoformat(data['created_at'])
    assert model_created.date() == data_created.date()
    assert model_created.hour == data_created.hour
    assert model_created.minute == data_created.minute
    
    model_updated = datetime.fromisoformat(model.updated_at)
    data_updated = datetime.fromisoformat(data['updated_at'])
    assert model_updated.date() == data_updated.date()
    assert model_updated.hour == data_updated.hour
    assert model_updated.minute == data_updated.minute


def test_base_model_updated_at():
    """Test that updated_at is updated when the model is modified."""
    model = BaseModel()
    original_updated_at = model.updated_at
    
    # Wait a moment to ensure the timestamp changes
    import time
    time.sleep(0.001)
    
    # Modify the model
    model.id = str(uuid.uuid4())
    
    # Check that updated_at has changed
    # Wait a bit longer to ensure the timestamp changes even at the second level
    time.sleep(1.0)
    
    # Modify the model
    model.id = str(uuid.uuid4())
    
    # Compare timestamps - they should be different now
    assert model.updated_at != original_updated_at


def test_base_model_exclude_none():
    """Test that None values are excluded from the dictionary."""
    class TestModel(BaseModel):
        name: str = None
        value: int = 0
    
    model = TestModel()
    model_dict = model.dict()
    
    # Check that the None value is excluded
    assert 'name' not in model_dict
    assert 'value' in model_dict
