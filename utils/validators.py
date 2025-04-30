from typing import Union, Optional, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime
import logging
from utils.money import Money, Percentage, ensure_money, ensure_percentage

logger = logging.getLogger(__name__)

class Validator:
    """Centralized validator for all data types."""
    
    @staticmethod
    def validate_money(value: Union[str, float, int, Money, Decimal],
                      min_value: float = 0,
                      max_value: float = 1e9,
                      field_name: str = "Amount",
                      raise_exception: bool = False) -> Optional[str]:
        """
        Validate monetary value.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            field_name: Name of the field for error messages
            raise_exception: Whether to raise an exception on validation failure
            
        Returns:
            None if valid, error message string if invalid and not raising exception
            
        Raises:
            ValueError: If validation fails and raise_exception is True
        """
        try:
            amount = ensure_money(value)
            if amount.dollars < min_value or amount.dollars > max_value:
                error_msg = f"{field_name} must be between {Money(min_value)} and {Money(max_value)}"
                if raise_exception:
                    raise ValueError(error_msg)
                return error_msg
            return None
        except (ValueError, TypeError) as e:
            error_msg = f"Invalid monetary value for {field_name}: {str(e)}"
            logger.error(error_msg)
            if raise_exception:
                raise ValueError(error_msg)
            return error_msg
        
    @staticmethod
    def validate_percentage(value: Union[str, float, int, Percentage, Decimal],
                           min_value: float = 0,
                           max_value: float = 100,
                           field_name: str = "Percentage",
                           raise_exception: bool = False) -> Optional[str]:
        """
        Validate percentage value.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed percentage
            max_value: Maximum allowed percentage
            field_name: Name of the field for error messages
            raise_exception: Whether to raise an exception on validation failure
            
        Returns:
            None if valid, error message string if invalid and not raising exception
            
        Raises:
            ValueError: If validation fails and raise_exception is True
        """
        try:
            percentage = ensure_percentage(value)
            if percentage.value < min_value or percentage.value > max_value:
                error_msg = f"{field_name} must be between {min_value}% and {max_value}%"
                if raise_exception:
                    raise ValueError(error_msg)
                return error_msg
            return None
        except (ValueError, TypeError) as e:
            error_msg = f"Invalid percentage value for {field_name}: {str(e)}"
            logger.error(error_msg)
            if raise_exception:
                raise ValueError(error_msg)
            return error_msg
        
    @staticmethod
    def validate_positive_number(value: Union[int, float, Money, Decimal],
                               field_name: str,
                               raise_exception: bool = True) -> Optional[str]:
        """
        Validate that a value is positive.
        
        Args:
            value: Value to validate
            field_name: Name of the field for error messages
            raise_exception: Whether to raise an exception on validation failure
            
        Returns:
            None if valid, error message string if invalid and not raising exception
            
        Raises:
            ValueError: If validation fails and raise_exception is True
        """
        try:
            if isinstance(value, Money):
                money_value = value
            else:
                money_value = ensure_money(value)
                
            if money_value.dollars <= 0:
                error_msg = f"{field_name} must be greater than 0"
                if raise_exception:
                    raise ValueError(error_msg)
                return error_msg
            return None
        except (ValueError, TypeError) as e:
            error_msg = f"Invalid value for {field_name}: {str(e)}"
            logger.error(error_msg)
            if raise_exception:
                raise ValueError(error_msg)
            return error_msg
        
    @staticmethod
    def validate_uuid(uuid_str: str,
                     field_name: str = "ID",
                     raise_exception: bool = True) -> Optional[str]:
        """
        Validate that a string is a valid UUID.
        
        Args:
            uuid_str: String to validate as UUID
            field_name: Name of the field for error messages
            raise_exception: Whether to raise an exception on validation failure
            
        Returns:
            None if valid, error message string if invalid and not raising exception
            
        Raises:
            ValueError: If validation fails and raise_exception is True
        """
        try:
            uuid.UUID(str(uuid_str))
            return None
        except (ValueError, AttributeError, TypeError) as e:
            error_msg = f"{field_name} must be a valid UUID"
            logger.error(f"UUID validation error: {str(e)}")
            if raise_exception:
                raise ValueError(error_msg)
            return error_msg
        
    @staticmethod
    def validate_date_format(date_str: str,
                           field_name: str,
                           format_str: str = "%Y-%m-%d",
                           raise_exception: bool = True) -> Optional[str]:
        """
        Validate that a string is in the specified date format.
        
        Args:
            date_str: String to validate as date
            field_name: Name of the field for error messages
            format_str: Expected date format string
            raise_exception: Whether to raise an exception on validation failure
            
        Returns:
            None if valid, error message string if invalid and not raising exception
            
        Raises:
            ValueError: If validation fails and raise_exception is True
        """
        try:
            if format_str == "ISO":
                # Handle ISO format with timezone
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Handle specific format string
                datetime.strptime(date_str, format_str)
            return None
        except (ValueError, AttributeError, TypeError) as e:
            format_display = "ISO format" if format_str == "ISO" else format_str
            error_msg = f"{field_name} must be in {format_display} date format"
            logger.error(f"Date validation error: {str(e)}")
            if raise_exception:
                raise ValueError(error_msg)
            return error_msg
        
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: Dict[str, str], 
                               raise_exception: bool = True) -> Optional[str]:
        """
        Validate that required fields are present and valid.
        
        Args:
            data: Data dictionary to validate
            required_fields: Dictionary mapping field names to display names
            raise_exception: Whether to raise an exception on validation failure
            
        Returns:
            None if valid, error message string if invalid and not raising exception
            
        Raises:
            ValueError: If validation fails and raise_exception is True
        """
        for field, display_name in required_fields.items():
            if field not in data or data[field] is None:
                error_msg = f"Missing required field: {display_name}"
                if raise_exception:
                    raise ValueError(error_msg)
                return error_msg
        return None
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float, Decimal],
                             min_value: float,
                             max_value: float,
                             field_name: str,
                             raise_exception: bool = True) -> Optional[str]:
        """
        Validate that a numeric value is within a specified range.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            field_name: Name of the field for error messages
            raise_exception: Whether to raise an exception on validation failure
            
        Returns:
            None if valid, error message string if invalid and not raising exception
            
        Raises:
            ValueError: If validation fails and raise_exception is True
        """
        try:
            numeric_value = float(value)
            if numeric_value < min_value or numeric_value > max_value:
                error_msg = f"{field_name} must be between {min_value} and {max_value}"
                if raise_exception:
                    raise ValueError(error_msg)
                return error_msg
            return None
        except (ValueError, TypeError) as e:
            error_msg = f"Invalid numeric value for {field_name}: {str(e)}"
            logger.error(error_msg)
            if raise_exception:
                raise ValueError(error_msg)
            return error_msg
