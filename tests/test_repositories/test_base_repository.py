"""
Tests for the base repository.

This module provides tests for the base repository, including
CRUD operations and data persistence.
"""

import os
import pytest
import tempfile
import json
from pathlib import Path

from src.models.base_model import BaseModel
from src.repositories.base_repository import BaseRepository


class TestModel(BaseModel):
    """Test model for repository tests."""
    name: str = "Test"
    value: int = 0


class TestRepository(BaseRepository[TestModel]):
    """Test repository for repository tests."""
    
    def __init__(self, file_path: str):
        """Initialize the test repository."""
        super().__init__(file_path, TestModel)


def test_base_repository_initialization():
    """Test base repository initialization."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Check that the repository has the expected attributes
        assert repository.file_path == temp_path
        assert repository.model_class == TestModel
        
        # Check that the file was created
        assert os.path.exists(temp_path)
        
        # Check that the file contains an empty list
        with open(temp_path, 'r') as f:
            data = json.load(f)
            assert data == []
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_base_repository_create():
    """Test base repository create operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Create a model
        model = TestModel(name="Test Model", value=42)
        
        # Create the model in the repository
        created_model = repository.create(model)
        
        # Check that the created model has the expected attributes
        assert created_model.id == model.id
        assert created_model.name == "Test Model"
        assert created_model.value == 42
        
        # Check that the model was saved to the file
        with open(temp_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['id'] == model.id
            assert data[0]['name'] == "Test Model"
            assert data[0]['value'] == 42
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_base_repository_get_all():
    """Test base repository get_all operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Create some models
        model1 = TestModel(name="Model 1", value=1)
        model2 = TestModel(name="Model 2", value=2)
        model3 = TestModel(name="Model 3", value=3)
        
        # Create the models in the repository
        repository.create(model1)
        repository.create(model2)
        repository.create(model3)
        
        # Get all models
        models = repository.get_all()
        
        # Check that the correct number of models was returned
        assert len(models) == 3
        
        # Check that the models have the expected attributes
        assert models[0].id == model1.id
        assert models[0].name == "Model 1"
        assert models[0].value == 1
        
        assert models[1].id == model2.id
        assert models[1].name == "Model 2"
        assert models[1].value == 2
        
        assert models[2].id == model3.id
        assert models[2].name == "Model 3"
        assert models[2].value == 3
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_base_repository_get_by_id():
    """Test base repository get_by_id operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Create some models
        model1 = TestModel(name="Model 1", value=1)
        model2 = TestModel(name="Model 2", value=2)
        model3 = TestModel(name="Model 3", value=3)
        
        # Create the models in the repository
        repository.create(model1)
        repository.create(model2)
        repository.create(model3)
        
        # Get a model by ID
        model = repository.get_by_id(model2.id)
        
        # Check that the model has the expected attributes
        assert model is not None
        assert model.id == model2.id
        assert model.name == "Model 2"
        assert model.value == 2
        
        # Try to get a nonexistent model
        nonexistent_model = repository.get_by_id("nonexistent-id")
        
        # Check that None was returned
        assert nonexistent_model is None
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_base_repository_update():
    """Test base repository update operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Create a model
        model = TestModel(name="Test Model", value=42)
        
        # Create the model in the repository
        repository.create(model)
        
        # Update the model
        model.name = "Updated Model"
        model.value = 99
        
        # Update the model in the repository
        updated_model = repository.update(model)
        
        # Check that the updated model has the expected attributes
        assert updated_model.id == model.id
        assert updated_model.name == "Updated Model"
        assert updated_model.value == 99
        
        # Check that the model was updated in the file
        with open(temp_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['id'] == model.id
            assert data[0]['name'] == "Updated Model"
            assert data[0]['value'] == 99
        
        # Try to update a nonexistent model
        nonexistent_model = TestModel(id="nonexistent-id", name="Nonexistent", value=0)
        
        # Check that an exception is raised
        with pytest.raises(ValueError):
            repository.update(nonexistent_model)
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_base_repository_delete():
    """Test base repository delete operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Create some models
        model1 = TestModel(name="Model 1", value=1)
        model2 = TestModel(name="Model 2", value=2)
        model3 = TestModel(name="Model 3", value=3)
        
        # Create the models in the repository
        repository.create(model1)
        repository.create(model2)
        repository.create(model3)
        
        # Delete a model
        result = repository.delete(model2.id)
        
        # Check that the operation was successful
        assert result is True
        
        # Check that the model was deleted from the file
        with open(temp_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]['id'] == model1.id
            assert data[1]['id'] == model3.id
        
        # Try to delete a nonexistent model
        result = repository.delete("nonexistent-id")
        
        # Check that the operation failed
        assert result is False
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_base_repository_count():
    """Test base repository count operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Check that the count is 0
        assert repository.count() == 0
        
        # Create some models
        model1 = TestModel(name="Model 1", value=1)
        model2 = TestModel(name="Model 2", value=2)
        model3 = TestModel(name="Model 3", value=3)
        
        # Create the models in the repository
        repository.create(model1)
        repository.create(model2)
        repository.create(model3)
        
        # Check that the count is 3
        assert repository.count() == 3
        
        # Delete a model
        repository.delete(model2.id)
        
        # Check that the count is 2
        assert repository.count() == 2
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_base_repository_exists():
    """Test base repository exists operation."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        # Create a repository
        repository = TestRepository(temp_path)
        
        # Create a model
        model = TestModel(name="Test Model", value=42)
        
        # Create the model in the repository
        repository.create(model)
        
        # Check that the model exists
        assert repository.exists(model.id) is True
        
        # Check that a nonexistent model doesn't exist
        assert repository.exists("nonexistent-id") is False
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
