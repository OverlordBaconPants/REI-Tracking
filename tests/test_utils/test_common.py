"""
Unit tests for common utility functions.

This module contains tests for the utility functions in src/utils/common.py.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from src.utils.common import (
    safe_float,
    format_address,
    validate_date_range,
    is_wholly_owned_by_user,
    validate_email,
    validate_phone,
    validate_date,
    is_valid_category
)
from src.utils.money import Money

class TestSafeFloat:
    """Tests for the safe_float function."""
    
    def test_none_value(self):
        """Test with None value."""
        assert safe_float(None) == 0.0
        assert safe_float(None, 1.0) == 1.0
    
    def test_money_object(self):
        """Test with Money object."""
        assert safe_float(Money(123.45)) == 123.45
    
    def test_numeric_values(self):
        """Test with numeric values."""
        assert safe_float(123) == 123.0
        assert safe_float(123.45) == 123.45
        assert safe_float(Decimal('123.45')) == 123.45
    
    def test_string_values(self):
        """Test with string values."""
        assert safe_float('123') == 123.0
        assert safe_float('123.45') == 123.45
        assert safe_float('$123.45') == 123.45
        assert safe_float('123,456.78') == 123456.78
        assert safe_float('123.45%') == 123.45
        assert safe_float('  123.45  ') == 123.45
    
    def test_invalid_values(self):
        """Test with invalid values."""
        assert safe_float('abc') == 0.0
        assert safe_float('abc', 1.0) == 1.0
        assert safe_float({}) == 0.0
        assert safe_float([]) == 0.0

class TestFormatAddress:
    """Tests for the format_address function."""
    
    def test_empty_address(self):
        """Test with empty address."""
        assert format_address('') == 'Unknown'
        assert format_address(None) == 'Unknown'
    
    def test_base_format(self):
        """Test with base format."""
        address = '123 Main St, Anytown, CA 12345'
        assert format_address(address, 'base') == '123 Main St'
    
    def test_display_format(self):
        """Test with display format."""
        address = '123 Main St, Anytown, CA 12345'
        assert format_address(address, 'display') == '123 Main St, Anytown'
    
    def test_full_format(self):
        """Test with full format."""
        address = '123 Main St, Anytown, CA 12345'
        assert format_address(address, 'full') == address
    
    def test_single_part_address(self):
        """Test with single part address."""
        address = '123 Main St'
        assert format_address(address, 'base') == '123 Main St'
        assert format_address(address, 'display') == '123 Main St'
        assert format_address(address, 'full') == '123 Main St'

class TestValidateDateRange:
    """Tests for the validate_date_range function."""
    
    def test_empty_dates(self):
        """Test with empty dates."""
        is_valid, _ = validate_date_range(None, None)
        assert is_valid is True
    
    def test_valid_range(self):
        """Test with valid date range."""
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        is_valid, _ = validate_date_range(start_date, end_date)
        assert is_valid is True
    
    def test_start_date_after_end_date(self):
        """Test with start date after end date."""
        start_date = '2023-12-31'
        end_date = '2023-01-01'
        is_valid, error = validate_date_range(start_date, end_date)
        assert is_valid is False
        assert "Start date cannot be after end date" in error
    
    def test_start_date_before_min_date(self):
        """Test with start date before minimum date."""
        start_date = '1999-01-01'
        end_date = '2023-12-31'
        min_date = '2000-01-01'
        is_valid, error = validate_date_range(start_date, end_date, min_date)
        assert is_valid is False
        assert f"Start date cannot be before {min_date}" in error
    
    def test_end_date_too_far_in_future(self):
        """Test with end date too far in future."""
        start_date = '2023-01-01'
        # Set end date to 31 days in the future
        future_date = (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d')
        is_valid, error = validate_date_range(start_date, future_date, max_future_days=30)
        assert is_valid is False
        assert "End date cannot be more than 30 days in the future" in error
    
    def test_invalid_date_format(self):
        """Test with invalid date format."""
        start_date = '2023/01/01'
        end_date = '2023-12-31'
        is_valid, error = validate_date_range(start_date, end_date)
        assert is_valid is False
        assert "Invalid date format" in error

class TestIsWhollyOwnedByUser:
    """Tests for the is_wholly_owned_by_user function."""
    
    def test_single_owner_100_percent(self):
        """Test with single owner with 100% equity."""
        property_data = {
            'address': '123 Main St',
            'partners': [
                {'name': 'user1', 'equity_share': 100}
            ]
        }
        assert is_wholly_owned_by_user(property_data, 'user1') is True
        assert is_wholly_owned_by_user(property_data, 'user2') is False
    
    def test_single_owner_almost_100_percent(self):
        """Test with single owner with almost 100% equity."""
        property_data = {
            'address': '123 Main St',
            'partners': [
                {'name': 'user1', 'equity_share': 99.99}
            ]
        }
        assert is_wholly_owned_by_user(property_data, 'user1') is True
    
    def test_multiple_owners_user_has_100_percent(self):
        """Test with multiple owners but user has 100% equity."""
        property_data = {
            'address': '123 Main St',
            'partners': [
                {'name': 'user1', 'equity_share': 100},
                {'name': 'user2', 'equity_share': 0}
            ]
        }
        assert is_wholly_owned_by_user(property_data, 'user1') is True
        assert is_wholly_owned_by_user(property_data, 'user2') is False
    
    def test_multiple_owners_split_equity(self):
        """Test with multiple owners with split equity."""
        property_data = {
            'address': '123 Main St',
            'partners': [
                {'name': 'user1', 'equity_share': 50},
                {'name': 'user2', 'equity_share': 50}
            ]
        }
        assert is_wholly_owned_by_user(property_data, 'user1') is False
        assert is_wholly_owned_by_user(property_data, 'user2') is False
    
    def test_no_partners(self):
        """Test with no partners."""
        property_data = {
            'address': '123 Main St',
            'partners': []
        }
        assert is_wholly_owned_by_user(property_data, 'user1') is False
    
    def test_case_insensitive(self):
        """Test case insensitivity."""
        property_data = {
            'address': '123 Main St',
            'partners': [
                {'name': 'User1', 'equity_share': 100}
            ]
        }
        assert is_wholly_owned_by_user(property_data, 'user1') is True

class TestValidateEmail:
    """Tests for the validate_email function."""
    
    def test_valid_emails(self):
        """Test with valid email addresses."""
        assert validate_email('user@example.com') is True
        assert validate_email('user.name@example.com') is True
        assert validate_email('user+tag@example.com') is True
        assert validate_email('user@subdomain.example.com') is True
    
    def test_invalid_emails(self):
        """Test with invalid email addresses."""
        assert validate_email('') is False
        assert validate_email(None) is False
        assert validate_email('user') is False
        assert validate_email('user@') is False
        assert validate_email('@example.com') is False
        assert validate_email('user@example') is False
        assert validate_email('user@.com') is False

class TestValidatePhone:
    """Tests for the validate_phone function."""
    
    def test_valid_phones(self):
        """Test with valid phone numbers."""
        assert validate_phone('1234567890') is True
        assert validate_phone('123-456-7890') is True
        assert validate_phone('(123) 456-7890') is True
        assert validate_phone('+11234567890') is True
        assert validate_phone('+1 123 456 7890') is True
    
    def test_invalid_phones(self):
        """Test with invalid phone numbers."""
        assert validate_phone('') is False
        assert validate_phone(None) is False
        assert validate_phone('123') is False
        assert validate_phone('abcdefghij') is False
        assert validate_phone('123-456-789') is False  # Too short
        assert validate_phone('123456789012345678901') is False  # Too long

class TestValidateDate:
    """Tests for the validate_date function."""
    
    def test_valid_dates(self):
        """Test with valid dates."""
        assert validate_date('2023-01-01') is True
        assert validate_date('2023-12-31') is True
        assert validate_date('2023/01/01', '%Y/%m/%d') is True
    
    def test_invalid_dates(self):
        """Test with invalid dates."""
        assert validate_date('') is False
        assert validate_date(None) is False
        assert validate_date('2023-13-01') is False  # Invalid month
        assert validate_date('2023-01-32') is False  # Invalid day
        assert validate_date('2023/01/01') is False  # Wrong format
        assert validate_date('01/01/2023', '%Y-%m-%d') is False  # Wrong format

class TestIsValidCategory:
    """Tests for the is_valid_category function."""
    
    def test_valid_categories(self):
        """Test with valid categories."""
        categories = {
            'income': ['Rent', 'Parking', 'Laundry'],
            'expense': ['Repairs', 'Utilities', 'Insurance']
        }
        assert is_valid_category('Rent', 'income', categories) is True
        assert is_valid_category('Repairs', 'expense', categories) is True
    
    def test_invalid_categories(self):
        """Test with invalid categories."""
        categories = {
            'income': ['Rent', 'Parking', 'Laundry'],
            'expense': ['Repairs', 'Utilities', 'Insurance']
        }
        assert is_valid_category('', 'income', categories) is False
        assert is_valid_category(None, 'income', categories) is False
        assert is_valid_category('Rent', '', categories) is False
        assert is_valid_category('Rent', None, categories) is False
        assert is_valid_category('Rent', 'expense', categories) is False
        assert is_valid_category('Other', 'income', categories) is False
        assert is_valid_category('Rent', 'other', categories) is False
