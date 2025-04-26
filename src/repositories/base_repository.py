"""
Base repository module for the REI-Tracker application.

This module provides the base repository class that all other repositories
inherit from, including common CRUD operations and data persistence.
"""

import os
from typing import List, Dict, Any, Optional, TypeVar, Generic, Type

from src.models.base_model import BaseModel
from src.utils.file_utils import AtomicJsonFile
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Type variable for generic repository
T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Base repository class for all application repositories.
    
    This class provides common CRUD operations and data persistence for
    all repositories, using JSON files as the storage backend.
    """
    
    def __init__(self, file_path: str, model_class: Type[T]) -> None:
        """
        Initialize the repository with a file path and model class.
        
        Args:
            file_path: Path to the JSON file
            model_class: Model class for the repository
        """
        self.file_path = file_path
        self.model_class = model_class
        self.json_file = AtomicJsonFile[List[Dict[str, Any]]](file_path)
        
        # Ensure the file exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            self.json_file.write([])
    
    def get_all(self) -> List[T]:
        """
        Get all items from the repository.
        
        Returns:
            List of all items
        """
        try:
            data = self.json_file.read(default=[])
            return [self.model_class.from_dict(item) for item in data]
        except Exception as e:
            logger.error(f"Error getting all items: {str(e)}")
            raise
    
    def get_by_id(self, item_id: str) -> Optional[T]:
        """
        Get an item by ID.
        
        Args:
            item_id: ID of the item to get
            
        Returns:
            The item, or None if not found
        """
        try:
            data = self.json_file.read(default=[])
            for item in data:
                if item.get("id") == item_id:
                    return self.model_class.from_dict(item)
            return None
        except Exception as e:
            logger.error(f"Error getting item by ID: {str(e)}")
            raise
    
    def create(self, item: T) -> T:
        """
        Create a new item.
        
        Args:
            item: Item to create
            
        Returns:
            The created item
        """
        try:
            data = self.json_file.read(default=[])
            
            # Check for duplicate ID
            for existing_item in data:
                if existing_item.get("id") == item.id:
                    raise ValueError(f"Item with ID {item.id} already exists")
            
            # Add the new item
            data.append(item.dict())
            self.json_file.write(data)
            
            return item
        except Exception as e:
            logger.error(f"Error creating item: {str(e)}")
            raise
    
    def update(self, item: T) -> T:
        """
        Update an existing item.
        
        Args:
            item: Item to update
            
        Returns:
            The updated item
            
        Raises:
            ValueError: If the item doesn't exist
        """
        try:
            data = self.json_file.read(default=[])
            
            # Find the item to update
            for i, existing_item in enumerate(data):
                if existing_item.get("id") == item.id:
                    data[i] = item.dict()
                    self.json_file.write(data)
                    return item
            
            raise ValueError(f"Item with ID {item.id} not found")
        except Exception as e:
            logger.error(f"Error updating item: {str(e)}")
            raise
    
    def delete(self, item_id: str) -> bool:
        """
        Delete an item by ID.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if the item was deleted, False if not found
        """
        try:
            data = self.json_file.read(default=[])
            
            # Find the item to delete
            for i, item in enumerate(data):
                if item.get("id") == item_id:
                    del data[i]
                    self.json_file.write(data)
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            raise
    
    def count(self) -> int:
        """
        Count the number of items in the repository.
        
        Returns:
            The number of items
        """
        try:
            data = self.json_file.read(default=[])
            return len(data)
        except Exception as e:
            logger.error(f"Error counting items: {str(e)}")
            raise
    
    def exists(self, item_id: str) -> bool:
        """
        Check if an item exists by ID.
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            True if the item exists, False otherwise
        """
        try:
            data = self.json_file.read(default=[])
            return any(item.get("id") == item_id for item in data)
        except Exception as e:
            logger.error(f"Error checking if item exists: {str(e)}")
            raise
