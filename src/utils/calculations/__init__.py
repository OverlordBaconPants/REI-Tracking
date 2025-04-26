"""
Financial calculation utilities for the REI Tracker application.

This package provides core calculation components for financial analysis,
including loan calculations, validation, and specialized financial metrics.
"""

from src.utils.calculations.validation import (
    ValidationError,
    ValidationResult,
    Validator,
    safe_calculation
)

from src.utils.calculations.loan_details import LoanDetails

__all__ = [
    'ValidationError',
    'ValidationResult',
    'Validator',
    'safe_calculation',
    'LoanDetails',
]
