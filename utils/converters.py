from typing import Union, Optional, Any
from decimal import Decimal, InvalidOperation
import logging

logger = logging.getLogger(__name__)

def to_int(value: Any, default: Optional[int] = None) -> Optional[int]:
    """
    Convert value to integer, handling various formats.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Converted integer or default value
    """
    if value is None or value == '':
        return default
    try:
        if isinstance(value, str):
            clean_value = value.replace('$', '').replace(',', '').strip()
            return int(float(clean_value))
        return int(float(value))
    except (ValueError, TypeError):
        logger.debug(f"Cannot convert {value} to integer, using default {default}")
        return default

def to_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Convert value to float, handling various formats.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Converted float or default value
    """
    if value is None or value == '':
        return default
    try:
        if isinstance(value, str):
            clean_value = value.replace('$', '').replace('%', '').replace(',', '').strip()
            return float(clean_value)
        return float(value)
    except (ValueError, TypeError):
        logger.debug(f"Cannot convert {value} to float, using default {default}")
        return default

def to_decimal(value: Any, default: Optional[Decimal] = None) -> Optional[Decimal]:
    """
    Convert value to Decimal, handling various formats.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Converted Decimal or default value
    """
    if value is None or value == '':
        return default
    try:
        if isinstance(value, str):
            if value.lower() == 'infinite' or value.lower() == '∞':
                return Decimal('Infinity')
            clean_value = value.replace('$', '').replace('%', '').replace(',', '').strip()
            return Decimal(clean_value)
        return Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        logger.debug(f"Cannot convert {value} to Decimal, using default {default}")
        return default

def to_bool(value: Any, default: bool = False) -> bool:
    """
    Convert value to boolean, handling various formats.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Converted boolean or default value
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes', 'on', 't', 'y')
    if isinstance(value, (int, float)):
        return value != 0
    return default
