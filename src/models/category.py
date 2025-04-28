"""
Category model module for the REI-Tracker application.

This module provides the Category model for income and expense categorization.
"""

from typing import List, Dict, Any, Optional
from pydantic import Field, validator

from src.models.base_model import BaseModel


class Categories(BaseModel):
    """
    Categories model for income and expense categorization.
    
    This class represents the available categories for income and expense
    transactions in the system.
    """
    
    income: List[str] = Field(default_factory=list)
    expense: List[str] = Field(default_factory=list)
    
    @validator("income", "expense")
    def validate_categories(cls, v: List[str]) -> List[str]:
        """
        Validate categories.
        
        Args:
            v: The categories to validate
            
        Returns:
            The validated categories
            
        Raises:
            ValueError: If any category is invalid
        """
        # Ensure all categories are strings
        if not all(isinstance(category, str) for category in v):
            raise ValueError("All categories must be strings")
        
        # Ensure all categories are unique
        if len(v) != len(set(v)):
            raise ValueError("All categories must be unique")
        
        # Ensure all categories are non-empty
        if any(not category.strip() for category in v):
            raise ValueError("All categories must be non-empty")
        
        return v
    
    def add_income_category(self, category: str) -> None:
        """
        Add an income category.
        
        Args:
            category: The category to add
            
        Raises:
            ValueError: If the category already exists
        """
        if category in self.income:
            raise ValueError(f"Income category '{category}' already exists")
        
        self.income.append(category)
    
    def add_expense_category(self, category: str) -> None:
        """
        Add an expense category.
        
        Args:
            category: The category to add
            
        Raises:
            ValueError: If the category already exists
        """
        if category in self.expense:
            raise ValueError(f"Expense category '{category}' already exists")
        
        self.expense.append(category)
    
    def remove_income_category(self, category: str) -> None:
        """
        Remove an income category.
        
        Args:
            category: The category to remove
            
        Raises:
            ValueError: If the category doesn't exist
        """
        if category not in self.income:
            raise ValueError(f"Income category '{category}' doesn't exist")
        
        self.income.remove(category)
    
    def remove_expense_category(self, category: str) -> None:
        """
        Remove an expense category.
        
        Args:
            category: The category to remove
            
        Raises:
            ValueError: If the category doesn't exist
        """
        if category not in self.expense:
            raise ValueError(f"Expense category '{category}' doesn't exist")
        
        self.expense.remove(category)
    
    def is_valid_income_category(self, category: str) -> bool:
        """
        Check if an income category is valid.
        
        Args:
            category: The category to check
            
        Returns:
            True if the category is valid, False otherwise
        """
        return category in self.income
    
    def is_valid_expense_category(self, category: str) -> bool:
        """
        Check if an expense category is valid.
        
        Args:
            category: The category to check
            
        Returns:
            True if the category is valid, False otherwise
        """
        return category in self.expense
    
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
        from src.utils.common import is_valid_category
        return is_valid_category(self, category, category_type)
