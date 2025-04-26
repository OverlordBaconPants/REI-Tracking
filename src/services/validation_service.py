"""
Validation service module for the REI-Tracker application.

This module provides the ValidationService class for data validation,
including input validation and error handling.
"""

from typing import Dict, List, Any, Optional, Type, TypeVar, Generic, Union
from decimal import Decimal

from pydantic import BaseModel, ValidationError

from src.utils.validation_utils import ValidationResult, ModelValidator, FunctionValidator
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Type variable for generic validation
T = TypeVar('T')


class ValidationService:
    """
    Validation service for data validation.
    
    This class provides methods for data validation, including input validation
    and error handling.
    """
    
    @staticmethod
    def validate_model(data: Dict[str, Any], model_class: Type[BaseModel]) -> ValidationResult[BaseModel]:
        """
        Validate data against a Pydantic model.
        
        Args:
            data: The data to validate
            model_class: The Pydantic model class
            
        Returns:
            A validation result
        """
        try:
            validator = ModelValidator(model_class)
            return validator.validate(data)
        except Exception as e:
            logger.error(f"Error validating model: {str(e)}")
            return ValidationResult.failure({"_error": [str(e)]})
    
    @staticmethod
    def validate_email(email: str) -> ValidationResult[str]:
        """
        Validate an email address.
        
        Args:
            email: The email address to validate
            
        Returns:
            A validation result
        """
        from src.utils.validation_utils import validate_email
        
        result = ValidationResult[str](True, email)
        
        if not validate_email(email):
            result.add_error("email", "Invalid email format")
        
        return result
    
    @staticmethod
    def validate_phone(phone: str) -> ValidationResult[str]:
        """
        Validate a phone number.
        
        Args:
            phone: The phone number to validate
            
        Returns:
            A validation result
        """
        from src.utils.validation_utils import validate_phone
        
        result = ValidationResult[str](True, phone)
        
        if not validate_phone(phone):
            result.add_error("phone", "Invalid phone number format")
        
        return result
    
    @staticmethod
    def validate_date(date_str: str, format_str: str = '%Y-%m-%d') -> ValidationResult[str]:
        """
        Validate a date string.
        
        Args:
            date_str: The date string to validate
            format_str: The expected date format
            
        Returns:
            A validation result
        """
        from src.utils.validation_utils import validate_date
        
        result = ValidationResult[str](True, date_str)
        
        if not validate_date(date_str, format_str):
            result.add_error("date", f"Invalid date format (expected {format_str})")
        
        return result
    
    @staticmethod
    def validate_decimal(value: Union[str, float, int, Decimal], min_value: Optional[float] = None, 
                        max_value: Optional[float] = None) -> ValidationResult[Decimal]:
        """
        Validate a decimal value.
        
        Args:
            value: The value to validate
            min_value: The minimum allowed value
            max_value: The maximum allowed value
            
        Returns:
            A validation result
        """
        from src.utils.validation_utils import validate_decimal
        
        try:
            # Convert to Decimal
            if isinstance(value, str):
                decimal_value = Decimal(value)
            elif isinstance(value, (float, int)):
                decimal_value = Decimal(str(value))
            else:
                decimal_value = value
            
            result = ValidationResult[Decimal](True, decimal_value)
            
            if not validate_decimal(decimal_value, min_value, max_value):
                min_str = f">= {min_value}" if min_value is not None else ""
                max_str = f"<= {max_value}" if max_value is not None else ""
                range_str = f" ({min_str} {max_str})".strip() if min_str or max_str else ""
                
                result.add_error("value", f"Invalid decimal value{range_str}: {value}")
            
            return result
        except (ValueError, TypeError, ArithmeticError) as e:
            return ValidationResult.failure({"value": [f"Invalid decimal value: {str(e)}"]})
    
    @staticmethod
    def validate_percentage(value: Union[str, float, int, Decimal]) -> ValidationResult[Decimal]:
        """
        Validate a percentage value (0-100).
        
        Args:
            value: The value to validate
            
        Returns:
            A validation result
        """
        return ValidationService.validate_decimal(value, 0, 100)
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> ValidationResult[Any]:
        """
        Validate that a value is not None or empty.
        
        Args:
            value: The value to validate
            field_name: The name of the field
            
        Returns:
            A validation result
        """
        result = ValidationResult[Any](True, value)
        
        if value is None:
            result.add_error(field_name, "This field is required")
        elif isinstance(value, str) and not value.strip():
            result.add_error(field_name, "This field is required")
        elif isinstance(value, (list, dict)) and not value:
            result.add_error(field_name, "This field is required")
        
        return result
    
    @staticmethod
    def validate_min_length(value: str, min_length: int, field_name: str) -> ValidationResult[str]:
        """
        Validate that a string has a minimum length.
        
        Args:
            value: The value to validate
            min_length: The minimum length
            field_name: The name of the field
            
        Returns:
            A validation result
        """
        result = ValidationResult[str](True, value)
        
        if len(value) < min_length:
            result.add_error(field_name, f"Must be at least {min_length} characters")
        
        return result
    
    @staticmethod
    def validate_max_length(value: str, max_length: int, field_name: str) -> ValidationResult[str]:
        """
        Validate that a string has a maximum length.
        
        Args:
            value: The value to validate
            max_length: The maximum length
            field_name: The name of the field
            
        Returns:
            A validation result
        """
        result = ValidationResult[str](True, value)
        
        if len(value) > max_length:
            result.add_error(field_name, f"Must be at most {max_length} characters")
        
        return result
    
    @staticmethod
    def validate_min_value(value: Union[int, float, Decimal], min_value: Union[int, float, Decimal], 
                          field_name: str) -> ValidationResult[Union[int, float, Decimal]]:
        """
        Validate that a value is at least a minimum value.
        
        Args:
            value: The value to validate
            min_value: The minimum value
            field_name: The name of the field
            
        Returns:
            A validation result
        """
        result = ValidationResult[Union[int, float, Decimal]](True, value)
        
        if value < min_value:
            result.add_error(field_name, f"Must be at least {min_value}")
        
        return result
    
    @staticmethod
    def validate_max_value(value: Union[int, float, Decimal], max_value: Union[int, float, Decimal], 
                          field_name: str) -> ValidationResult[Union[int, float, Decimal]]:
        """
        Validate that a value is at most a maximum value.
        
        Args:
            value: The value to validate
            max_value: The maximum value
            field_name: The name of the field
            
        Returns:
            A validation result
        """
        result = ValidationResult[Union[int, float, Decimal]](True, value)
        
        if value > max_value:
            result.add_error(field_name, f"Must be at most {max_value}")
        
        return result
    
    @staticmethod
    def validate_in_list(value: Any, valid_values: List[Any], field_name: str) -> ValidationResult[Any]:
        """
        Validate that a value is in a list of valid values.
        
        Args:
            value: The value to validate
            valid_values: The list of valid values
            field_name: The name of the field
            
        Returns:
            A validation result
        """
        result = ValidationResult[Any](True, value)
        
        if value not in valid_values:
            result.add_error(field_name, f"Must be one of: {', '.join(str(v) for v in valid_values)}")
        
        return result
