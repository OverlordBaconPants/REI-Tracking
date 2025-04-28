"""
Common utility functions for the REI-Tracker application.

This module provides general utility functions that are used across
multiple parts of the application to reduce code duplication.
"""

from typing import Dict, List, Optional, Tuple, Union, Any, Set
from decimal import Decimal
import re
import logging
from datetime import datetime, date

from src.utils.logging_utils import get_logger

# Set up module-level logger
logger = get_logger(__name__)

def safe_float(value: Union[str, int, float, Decimal, None], default: float = 0.0) -> float:
    """
    Safely convert a value to float, handling various input types and formats.
    
    Args:
        value: The value to convert (can be string, int, float, Decimal, or None)
        default: Default value to return if conversion fails
        
    Returns:
        float: Converted value or default
    """
    try:
        if value is None:
            return default
            
        # Handle Money objects (imported conditionally to avoid circular imports)
        if hasattr(value, 'amount'):
            if isinstance(value.amount, (int, float, Decimal)):
                return float(value.amount)
            elif callable(getattr(value, 'amount', None)):
                return float(value.amount())
            
        if isinstance(value, (int, float)):
            return float(value)
            
        if isinstance(value, Decimal):
            return float(value)
            
        if isinstance(value, str):
            # Remove currency symbols, commas, percentages, and spaces
            cleaned = value.replace('$', '').replace(',', '').replace('%', '').replace(' ', '').strip()
            return float(cleaned) if cleaned else default
            
        return default
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Error converting value to float: {value}, using default {default}. Error: {str(e)}")
        return default

def format_address(address: str, format_type: str = 'display') -> str:
    """
    Format an address for consistent display.
    
    Args:
        address: Full address string
        format_type: Type of formatting ('display', 'base', 'full')
        
    Returns:
        Formatted address string
    """
    if not address:
        return "Unknown"
        
    parts = address.split(',')
    
    if format_type == 'base':
        # Return just the first part (street address)
        return parts[0].strip()
    elif format_type == 'display':
        # Return first two parts (street address, city)
        if len(parts) >= 2:
            return f"{parts[0].strip()}, {parts[1].strip()}"
        return parts[0].strip()
    else:
        # Return full address
        return address

def validate_date_range(start_date: Optional[str], end_date: Optional[str], 
                       min_date: str = '2000-01-01', 
                       max_future_days: int = 30) -> tuple[bool, str]:
    """
    Validates the date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        min_date: Minimum allowed date in YYYY-MM-DD format
        max_future_days: Maximum number of days in the future allowed
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not start_date and not end_date:
            return True, ""

        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            min_date_obj = datetime.strptime(min_date, '%Y-%m-%d')
            if start < min_date_obj:
                return False, f"Start date cannot be before {min_date}"

        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            from datetime import timedelta
            max_date = datetime.now() + timedelta(days=max_future_days)
            if end > max_date:
                return False, f"End date cannot be more than {max_future_days} days in the future"

        if start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            if start > end:
                return False, "Start date cannot be after end date"

        return True, ""
    except ValueError as e:
        return False, f"Invalid date format: {str(e)}"

def is_wholly_owned_by_user(property_data: dict, user_name: str) -> bool:
    """
    Checks if a property is wholly owned by the user.
    
    Args:
        property_data: Dictionary containing property information
        user_name: Name of the user to check
        
    Returns:
        True if the property is wholly owned by the user, False otherwise
    """
    logger.debug(f"Checking ownership for property: {property_data.get('address')} and user: {user_name}")
    
    # Use a small epsilon value for floating point comparison
    EPSILON = 0.1  # Allow for 0.1% difference from 100%
    
    partners = property_data.get('partners', [])
    if len(partners) == 1:
        partner = partners[0]
        is_user = partner.get('name', '').lower() == user_name.lower()
        equity = float(partner.get('equity_share', 0))
        return is_user and abs(equity - 100.0) < EPSILON
    
    user_equity = sum(
        float(partner.get('equity_share', 0))
        for partner in partners
        if partner.get('name', '').lower() == user_name.lower()
    )
    
    return abs(user_equity - 100.0) < EPSILON

def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
        
    # Simple regex for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone number is valid, False otherwise
    """
    if not phone:
        return False
        
    # Remove common separators and spaces
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)
    
    # Check if it's a valid phone number (10-15 digits)
    return bool(re.match(r'^\+?[0-9]{10,15}$', cleaned))

def validate_date(date_str: str, format_str: str = '%Y-%m-%d') -> bool:
    """
    Validate date string format.
    
    Args:
        date_str: Date string to validate
        format_str: Expected date format
        
    Returns:
        True if date is valid, False otherwise
    """
    if not date_str:
        return False
        
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False

def is_valid_category(category: str, category_type: str, categories: Dict[str, List[str]]) -> bool:
    """
    Check if a category is valid for the given type.
    
    Args:
        category: Category name to check
        category_type: Type of category ('income' or 'expense')
        categories: Dictionary of categories by type
        
    Returns:
        True if category is valid, False otherwise
    """
    if not category or not category_type:
        return False
        
    if category_type not in categories:
        return False
        
    return category in categories.get(category_type, [])
