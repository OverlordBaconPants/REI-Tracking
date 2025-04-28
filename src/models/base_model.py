"""
Base model module for the REI-Tracker application.

This module provides the base model class that all other models inherit from,
including common functionality and validation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional, TypeVar, Generic, Type, ClassVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_validator, ConfigDict, model_validator

T = TypeVar('T', bound='BaseModel')


class BaseModel(PydanticBaseModel):
    """
    Base model class for all application models.
    
    This class provides common fields and functionality for all models,
    including ID generation, timestamps, and validation.
    """
    
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = None
    updated_at: str = None
    
    # Flag to prevent recursion in __setattr__
    _skip_updated_at: bool = False
    
    def __init__(self, **data):
        """Initialize the model with timestamps."""
        # Set timestamps if not provided
        if 'created_at' not in data:
            now = datetime.now().isoformat()
            data['created_at'] = now
            data['updated_at'] = now
        elif 'updated_at' not in data:
            data['updated_at'] = data['created_at']
            
        super().__init__(**data)
    
    def __setattr__(self, name, value):
        """Set attribute and update the updated_at timestamp."""
        # Update timestamp when any field is modified (except timestamps themselves)
        if (name not in ('created_at', 'updated_at', '_skip_updated_at') and 
            hasattr(self, name) and 
            not getattr(self, '_skip_updated_at', False)):
            
            # Set the flag to prevent recursion
            object.__setattr__(self, '_skip_updated_at', True)
            try:
                # Update the timestamp
                super().__setattr__('updated_at', datetime.now().isoformat())
            finally:
                # Reset the flag
                object.__setattr__(self, '_skip_updated_at', False)
                
        # Set the attribute
        super().__setattr__(name, value)
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary, excluding None values.
        
        Returns:
            Dictionary representation of the model
        """
        kwargs.setdefault("exclude_none", True)
        return super().model_dump(*args, **kwargs)
    
    # Alias for backward compatibility
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary, excluding None values (alias for model_dump).
        
        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(*args, **kwargs)
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create a model instance from a dictionary.
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            Model instance
        """
        return cls.model_validate(data)
