"""
Base model module for the REI-Tracker application.

This module provides the base model class that all other models inherit from,
including common functionality and validation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, TypeVar, Generic, Type

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, validator

T = TypeVar('T', bound='BaseModel')


class BaseModel(PydanticBaseModel):
    """
    Base model class for all application models.
    
    This class provides common fields and functionality for all models,
    including ID generation, timestamps, and validation.
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        """Pydantic configuration."""
        
        # Allow extra fields when parsing
        extra = "ignore"
        
        # Allow field population by name or alias
        populat_by_name_by_field_name = True
        
        # Validate assignment
        validate_assignment = True
    
    @validator("updated_at", pre=True, always=True)
    def set_updated_at(cls, v: Any, values: Dict[str, Any]) -> str:
        """
        Set updated_at to current time on every update.
        
        Args:
            v: The current value
            values: The values being validated
            
        Returns:
            The updated timestamp
        """
        return datetime.now().isoformat()
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary, excluding None values.
        
        Returns:
            Dictionary representation of the model
        """
        kwargs.setdefault("exclude_none", True)
        return super().dict(*args, **kwargs)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            Model instance
        """
        return cls.parse_obj(data)
