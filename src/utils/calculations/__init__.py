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

from src.utils.calculations.analysis import (
    BaseAnalysis,
    LTRAnalysis,
    BRRRRAnalysis,
    LeaseOptionAnalysis,
    MultiFamilyAnalysis,
    PadSplitAnalysis,
    AnalysisResult,
    create_analysis
)

from src.utils.calculations.investment_metrics import (
    InvestmentMetricsCalculator,
    EquityProjection,
    YearlyProjection
)

__all__ = [
    'ValidationError',
    'ValidationResult',
    'Validator',
    'safe_calculation',
    'LoanDetails',
    'BaseAnalysis',
    'LTRAnalysis',
    'BRRRRAnalysis',
    'LeaseOptionAnalysis',
    'MultiFamilyAnalysis',
    'PadSplitAnalysis',
    'AnalysisResult',
    'create_analysis',
    'InvestmentMetricsCalculator',
    'EquityProjection',
    'YearlyProjection',
]
