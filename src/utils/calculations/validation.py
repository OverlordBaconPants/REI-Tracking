from typing import Dict, List, Optional, Union, Any, Callable
import logging
from decimal import Decimal
from src.utils.money import Money, Percentage

logger = logging.getLogger(__name__)

class ValidationError:
    """
    Represents a validation error with field name and error message.
    
    Attributes:
        field: The name of the field that failed validation
        message: The error message describing the validation failure
    """
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        
    def __str__(self) -> str:
        return f"{self.field}: {self.message}"
        
    def __repr__(self) -> str:
        return f"ValidationError(field='{self.field}', message='{self.message}')"

class ValidationResult:
    """
    Contains the result of a validation operation.
    
    This class collects and manages validation errors, providing
    methods to check validity and retrieve error messages.
    
    Attributes:
        errors: List of ValidationError objects
    """
    def __init__(self):
        self.errors: List[ValidationError] = []
        
    def add_error(self, field: str, message: str) -> None:
        """Add a validation error."""
        self.errors.append(ValidationError(field, message))
        
    def is_valid(self) -> bool:
        """Check if validation passed with no errors."""
        return len(self.errors) == 0
        
    def get_error_messages(self) -> Dict[str, List[str]]:
        """
        Get error messages grouped by field.
        
        Returns:
            Dict mapping field names to lists of error messages
        """
        error_dict: Dict[str, List[str]] = {}
        
        for error in self.errors:
            if error.field not in error_dict:
                error_dict[error.field] = []
            error_dict[error.field].append(error.message)
            
        return error_dict
        
    def get_all_messages(self) -> List[str]:
        """
        Get all error messages as a flat list.
        
        Returns:
            List of error messages with field names
        """
        return [str(error) for error in self.errors]
        
    def __str__(self) -> str:
        if self.is_valid():
            return "Validation passed"
        return f"Validation failed with {len(self.errors)} errors: {', '.join(self.get_all_messages())}"
        
    def __bool__(self) -> bool:
        """Allow using ValidationResult in boolean context to check validity."""
        return self.is_valid()

class Validator:
    """
    Utility class for validation logic with error collection.
    
    This class provides methods for validating different types of values
    and collecting validation errors.
    """
    
    @staticmethod
    def validate_required(
        result: ValidationResult,
        data: Dict[str, Any],
        field_name: str,
        display_name: Optional[str] = None
    ) -> bool:
        """
        Validate that a required field is present and not None.
        
        Args:
            result: ValidationResult to collect errors
            data: Dictionary containing the field
            field_name: Name of the field to validate
            display_name: Human-readable name for error messages
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        if field_name not in data or data[field_name] is None:
            result.add_error(
                field_name,
                f"Missing required field: {display_name or field_name}"
            )
            return False
        return True
    
    @staticmethod
    def validate_positive_number(
        result: ValidationResult,
        value: Union[int, float, Money],
        field_name: str,
        display_name: Optional[str] = None,
        allow_zero: bool = False
    ) -> bool:
        """
        Validate that a value is positive (or zero if allowed).
        
        Args:
            result: ValidationResult to collect errors
            value: Value to validate
            field_name: Name of the field for error reporting
            display_name: Human-readable name for error messages
            allow_zero: Whether to allow zero values
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        display = display_name or field_name
        
        try:
            if isinstance(value, Money):
                if allow_zero:
                    if value.dollars < 0:
                        result.add_error(field_name, f"{display} must be greater than or equal to 0")
                        return False
                else:
                    if value.dollars <= 0:
                        result.add_error(field_name, f"{display} must be greater than 0")
                        return False
            else:
                num_value = float(value)
                if allow_zero:
                    if num_value < 0:
                        result.add_error(field_name, f"{display} must be greater than or equal to 0")
                        return False
                else:
                    if num_value <= 0:
                        result.add_error(field_name, f"{display} must be greater than 0")
                        return False
        except (ValueError, TypeError):
            result.add_error(field_name, f"{display} must be a valid number")
            return False
            
        return True
    
    @staticmethod
    def validate_percentage(
        result: ValidationResult,
        value: Union[float, Percentage],
        field_name: str,
        display_name: Optional[str] = None,
        min_val: float = 0,
        max_val: float = 100
    ) -> bool:
        """
        Validate that a percentage is within a given range.
        
        Args:
            result: ValidationResult to collect errors
            value: Value to validate
            field_name: Name of the field for error reporting
            display_name: Human-readable name for error messages
            min_val: Minimum allowed percentage value
            max_val: Maximum allowed percentage value
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        display = display_name or field_name
        
        try:
            if isinstance(value, Percentage):
                percentage_value = value.value
            else:
                percentage_value = float(value)
                
            if percentage_value < min_val or percentage_value > max_val:
                result.add_error(
                    field_name,
                    f"{display} must be between {min_val}% and {max_val}%"
                )
                return False
        except (ValueError, TypeError):
            result.add_error(field_name, f"{display} must be a valid percentage")
            return False
            
        return True
    
    @staticmethod
    def validate_range(
        result: ValidationResult,
        value: Union[int, float],
        field_name: str,
        min_val: Union[int, float],
        max_val: Union[int, float],
        display_name: Optional[str] = None
    ) -> bool:
        """
        Validate that a numeric value is within a specified range.
        
        Args:
            result: ValidationResult to collect errors
            value: Value to validate
            field_name: Name of the field for error reporting
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            display_name: Human-readable name for error messages
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        display = display_name or field_name
        
        try:
            num_value = float(value)
            if num_value < min_val or num_value > max_val:
                result.add_error(
                    field_name,
                    f"{display} must be between {min_val} and {max_val}"
                )
                return False
        except (ValueError, TypeError):
            result.add_error(field_name, f"{display} must be a valid number")
            return False
            
        return True
    
    @staticmethod
    def validate_string(
        result: ValidationResult,
        value: str,
        field_name: str,
        display_name: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None
    ) -> bool:
        """
        Validate string values with optional length and pattern constraints.
        
        Args:
            result: ValidationResult to collect errors
            value: String value to validate
            field_name: Name of the field for error reporting
            display_name: Human-readable name for error messages
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            pattern: Regular expression pattern to match
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        display = display_name or field_name
        
        if not isinstance(value, str):
            result.add_error(field_name, f"{display} must be a string")
            return False
            
        if min_length is not None and len(value) < min_length:
            result.add_error(field_name, f"{display} must be at least {min_length} characters")
            return False
            
        if max_length is not None and len(value) > max_length:
            result.add_error(field_name, f"{display} must be at most {max_length} characters")
            return False
            
        if pattern is not None:
            import re
            if not re.match(pattern, value):
                result.add_error(field_name, f"{display} has an invalid format")
                return False
                
        return True
    
    @staticmethod
    def validate_date(
        result: ValidationResult,
        value: str,
        field_name: str,
        display_name: Optional[str] = None,
        format_str: str = "%Y-%m-%d"
    ) -> bool:
        """
        Validate that a string is a valid date in the specified format.
        
        Args:
            result: ValidationResult to collect errors
            value: Date string to validate
            field_name: Name of the field for error reporting
            display_name: Human-readable name for error messages
            format_str: Date format string (default: YYYY-MM-DD)
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        display = display_name or field_name
        
        if not isinstance(value, str):
            result.add_error(field_name, f"{display} must be a string")
            return False
            
        try:
            from datetime import datetime
            datetime.strptime(value, format_str)
            return True
        except ValueError:
            result.add_error(field_name, f"{display} must be a valid date in format {format_str}")
            return False
    
    @staticmethod
    def validate_with_function(
        result: ValidationResult,
        value: Any,
        field_name: str,
        validation_func: Callable[[Any], bool],
        error_message: str
    ) -> bool:
        """
        Validate a value using a custom validation function.
        
        Args:
            result: ValidationResult to collect errors
            value: Value to validate
            field_name: Name of the field for error reporting
            validation_func: Function that returns True if valid, False otherwise
            error_message: Error message to use if validation fails
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        if not validation_func(value):
            result.add_error(field_name, error_message)
            return False
        return True

def safe_calculation(default_value: Any = None) -> Callable:
    """
    Decorator for safely executing calculations with proper error handling.
    
    This decorator catches exceptions in calculation functions and returns
    a default value instead of raising an exception.
    
    Args:
        default_value: Value to return if an exception occurs
        
    Returns:
        Decorated function that handles exceptions
    """
    def decorator(func: Callable) -> Callable:
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return default_value
        return wrapper
    return decorator
