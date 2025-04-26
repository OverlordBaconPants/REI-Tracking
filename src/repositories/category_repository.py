"""
Category repository module for the REI-Tracker application.

This module provides the CategoryRepository class for category data persistence
and retrieval.
"""

from typing import List, Optional, Dict, Any

from src.config import current_config
from src.models.category import Categories
from src.repositories.base_repository import BaseRepository
from src.utils.file_utils import AtomicJsonFile
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class CategoryRepository:
    """
    Category repository for category data persistence and retrieval.
    
    This class provides methods for category-specific operations, such as
    adding and removing categories.
    """
    
    def __init__(self) -> None:
        """Initialize the category repository."""
        self.file_path = str(current_config.CATEGORIES_FILE)
        self.json_file = AtomicJsonFile(self.file_path)
    
    def get_categories(self) -> Categories:
        """
        Get all categories.
        
        Returns:
            The categories
        """
        try:
            data = self.json_file.read(default={"income": [], "expense": []})
            return Categories.from_dict(data)
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            raise
    
    def save_categories(self, categories: Categories) -> None:
        """
        Save categories.
        
        Args:
            categories: The categories to save
        """
        try:
            self.json_file.write(categories.dict())
        except Exception as e:
            logger.error(f"Error saving categories: {str(e)}")
            raise
    
    def add_income_category(self, category: str) -> None:
        """
        Add an income category.
        
        Args:
            category: The category to add
            
        Raises:
            ValueError: If the category already exists
        """
        try:
            categories = self.get_categories()
            categories.add_income_category(category)
            self.save_categories(categories)
        except Exception as e:
            logger.error(f"Error adding income category: {str(e)}")
            raise
    
    def add_expense_category(self, category: str) -> None:
        """
        Add an expense category.
        
        Args:
            category: The category to add
            
        Raises:
            ValueError: If the category already exists
        """
        try:
            categories = self.get_categories()
            categories.add_expense_category(category)
            self.save_categories(categories)
        except Exception as e:
            logger.error(f"Error adding expense category: {str(e)}")
            raise
    
    def remove_income_category(self, category: str) -> None:
        """
        Remove an income category.
        
        Args:
            category: The category to remove
            
        Raises:
            ValueError: If the category doesn't exist
        """
        try:
            categories = self.get_categories()
            categories.remove_income_category(category)
            self.save_categories(categories)
        except Exception as e:
            logger.error(f"Error removing income category: {str(e)}")
            raise
    
    def remove_expense_category(self, category: str) -> None:
        """
        Remove an expense category.
        
        Args:
            category: The category to remove
            
        Raises:
            ValueError: If the category doesn't exist
        """
        try:
            categories = self.get_categories()
            categories.remove_expense_category(category)
            self.save_categories(categories)
        except Exception as e:
            logger.error(f"Error removing expense category: {str(e)}")
            raise
    
    def is_valid_category(self, category: str, category_type: str) -> bool:
        """
        Check if a category is valid for the specified type.
        
        Args:
            category: The category to check
            category_type: The category type ("income" or "expense")
            
        Returns:
            True if the category is valid, False otherwise
            
        Raises:
            ValueError: If the category type is invalid
        """
        try:
            categories = self.get_categories()
            return categories.is_valid_category(category, category_type)
        except Exception as e:
            logger.error(f"Error checking if category is valid: {str(e)}")
            raise
