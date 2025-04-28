"""
Validation utilities for the REI-Tracker application.

This module provides utility functions and classes for data validation,
including custom validators and error handling.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Generic, Callable

from pydantic import BaseModel, Field, ValidationError, validator

from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Type variable for generic validation
T = TypeVar('T')


class ValidationResult(Generic[T]):
    """
    Class representing the result of a validation operation.
    
    This class provides a standardized way to handle validation results,
    including success/failure status and error messages.
    """
    
    def __init__(
        self, 
        is_valid: bool, 
        data: Optional[T] = None, 
        errors: Optional[Dict[str, List[str]]] = None
    ) -> None:
        """
        Initialize a validation result.
        
        Args:
            is_valid: Whether the validation was successful
            data: The validated data (if successful)
            errors: Dictionary of field-specific error messages
        """
        self.is_valid = is_valid
        self.data = data
        self.errors = errors or {}
    
    @classmethod
    def success(cls, data: T) -> 'ValidationResult[T]':
        """
        Create a successful validation result.
        
        Args:
            data: The validated data
            
        Returns:
            A successful validation result
        """
        return cls(True, data)
    
    @classmethod
    def failure(cls, errors: Dict[str, List[str]]) -> 'ValidationResult[T]':
        """
        Create a failed validation result.
        
        Args:
            errors: Dictionary of field-specific error messages
            
        Returns:
            A failed validation result
        """
        return cls(False, None, errors)
    
    def add_error(self, field: str, message: str) -> None:
        """
        Add an error message for a specific field.
        
        Args:
            field: The field name
            message: The error message
        """
        if field not in self.errors:
            self.errors[field] = []
        
        self.errors[field].append(message)
        self.is_valid = False
    
    def merge(self, other: 'ValidationResult') -> None:
        """
        Merge another validation result into this one.
        
        Args:
            other: The validation result to merge
        """
        if not other.is_valid:
            self.is_valid = False
            
            for field, messages in other.errors.items():
                for message in messages:
                    self.add_error(field, message)


class Validator(Generic[T]):
    """
    Base class for validators.
    
    This class provides a common interface for validators, including
    validation methods and error handling.
    """
    
    def validate(self, data: Any) -> ValidationResult[T]:
        """
        Validate the provided data.
        
        Args:
            data: The data to validate
            
        Returns:
            A validation result
        """
        raise NotImplementedError("Subclasses must implement validate method")


class ModelValidator(Validator[T]):
    """
    Validator using Pydantic models.
    
    This class provides validation using Pydantic models, with standardized
    error handling and formatting.
    """
    
    def __init__(self, model_class: Type[BaseModel]) -> None:
        """
        Initialize with a Pydantic model class.
        
        Args:
            model_class: The Pydantic model class to use for validation
        """
        self.model_class = model_class
    
    def validate(self, data: Any) -> ValidationResult[T]:
        """
        Validate the provided data using the Pydantic model.
        
        Args:
            data: The data to validate
            
        Returns:
            A validation result
        """
        try:
            validated_data = self.model_class.parse_obj(data)
            return ValidationResult.success(validated_data)
        except ValidationError as e:
            # Convert Pydantic validation errors to our format
            errors: Dict[str, List[str]] = {}
            
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                message = error['msg']
                
                if field not in errors:
                    errors[field] = []
                
                errors[field].append(message)
            
            return ValidationResult.failure(errors)


class FunctionValidator(Validator[T]):
    """
    Validator using a custom validation function.
    
    This class provides validation using a custom function, with standardized
    error handling and formatting.
    """
    
    def __init__(self, validation_func: Callable[[Any], ValidationResult[T]]) -> None:
        """
        Initialize with a validation function.
        
        Args:
            validation_func: The function to use for validation
        """
        self.validation_func = validation_func
    
    def validate(self, data: Any) -> ValidationResult[T]:
        """
        Validate the provided data using the validation function.
        
        Args:
            data: The data to validate
            
        Returns:
            A validation result
        """
        return self.validation_func(data)


# Common validation functions
from src.utils.common import validate_email, validate_phone, validate_date


def validate_decimal(value: Union[str, float, int, Decimal], min_value: Optional[float] = None, 
                    max_value: Optional[float] = None) -> bool:
    """
    Validate a decimal value.
    
    Args:
        value: The value to validate
        min_value: The minimum allowed value
        max_value: The maximum allowed value
        
    Returns:
        True if the value is valid, False otherwise
    """
    try:
        # Convert to Decimal
        if isinstance(value, str):
            decimal_value = Decimal(value)
        elif isinstance(value, (float, int)):
            decimal_value = Decimal(str(value))
        else:
            decimal_value = value
        
        # Check range
        if min_value is not None and decimal_value < Decimal(str(min_value)):
            return False
        
        if max_value is not None and decimal_value > Decimal(str(max_value)):
            return False
        
        return True
    except (ValueError, TypeError, ArithmeticError):
        return False


def validate_percentage(value: Union[str, float, int, Decimal]) -> bool:
    """
    Validate a percentage value (0-100).
    
    Args:
        value: The value to validate
        
    Returns:
        True if the value is a valid percentage, False otherwise
    """
    return validate_decimal(value, 0, 100)


# Common Pydantic validators

def decimal_validator(min_value: Optional[float] = None, max_value: Optional[float] = None) -> Callable:
    """
    Create a Pydantic validator for decimal values.
    
    Args:
        min_value: The minimum allowed value
        max_value: The maximum allowed value
        
    Returns:
        A Pydantic validator function
    """
    def validate_decimal_field(cls, value: Any) -> Decimal:
        if not validate_decimal(value, min_value, max_value):
            min_str = f">= {min_value}" if min_value is not None else ""
            max_str = f"<= {max_value}" if max_value is not None else ""
            range_str = f" ({min_str} {max_str})".strip() if min_str or max_str else ""
            
            raise ValueError(f"Invalid decimal value{range_str}: {value}")
        
        # Convert to Decimal
        if isinstance(value, str):
            return Decimal(value)
        elif isinstance(value, (float, int)):
            return Decimal(str(value))
        
        return value
    
    return validator('*', allow_reuse=True)(validate_decimal_field)


def percentage_validator() -> Callable:
    """
    Create a Pydantic validator for percentage values.
    
    Returns:
        A Pydantic validator function
    """
    return decimal_validator(0, 100)
