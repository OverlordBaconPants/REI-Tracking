# utils/flash.py
from flask import flash
from typing import Optional

def flash_message(message: str, category: Optional[str] = 'info') -> None:
    """
    Utility function to standardize flash messages across the application.
    Maps Flask flash categories to toastr notification types.
    """
    if not message:
        return

    # Map Flask categories to toastr types
    category_mapping = {
        'message': 'info',
        'danger': 'error',
        'success': 'success',
        'error': 'error',
        'warning': 'warning',
        'info': 'info'
    }

    # Normalize category to lowercase and get mapped category
    normalized_category = str(category).lower()
    flash_category = category_mapping.get(normalized_category, 'info')

    # Flash the message with the mapped category
    try:
        flash(str(message), flash_category)
    except Exception as e:
        flash(str(e), 'error')

def flash_success(message: str) -> None:
    """Convenience method for success messages"""
    flash_message(message, 'success')

def flash_error(message: str) -> None:
    """Convenience method for error messages"""
    flash_message(message, 'error')

def flash_warning(message: str) -> None:
    """Convenience method for warning messages"""
    flash_message(message, 'warning')

def flash_info(message: str) -> None:
    """Convenience method for info messages"""
    flash_message(message, 'info')