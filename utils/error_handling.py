import logging
import functools
from typing import TypeVar, Callable, Any, Optional, Union
import traceback

# Generic type for default values in safe_calculation decorator
T = TypeVar('T')

def safe_calculation(default_value: T = None, 
                    log_level: int = logging.ERROR,
                    error_message: Optional[str] = None) -> Callable:
    """
    Decorator for safely executing calculations with proper error handling.
    
    Args:
        default_value: Value to return if calculation fails
        log_level: Logging level for errors
        error_message: Custom error message prefix
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Union[Any, T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = logging.getLogger(func.__module__)
                msg = f"{error_message or 'Error in'} {func.__name__}: {str(e)}"
                logger.log(log_level, msg)
                if log_level >= logging.ERROR:
                    logger.error(traceback.format_exc())
                return default_value
        return wrapper
    return decorator
