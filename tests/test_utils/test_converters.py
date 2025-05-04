import pytest
from decimal import Decimal, InvalidOperation
from utils.converters import to_int, to_float, to_decimal, to_bool

class TestToInt:
    def test_valid_int(self):
        """Test conversion of valid integers."""
        assert to_int(5) == 5
        assert to_int(0) == 0
        assert to_int(-10) == -10
    
    def test_valid_float(self):
        """Test conversion of valid floats to integers."""
        assert to_int(5.7) == 5
        assert to_int(5.2) == 5
        assert to_int(-10.8) == -10
    
    def test_valid_string_int(self):
        """Test conversion of valid string integers."""
        assert to_int("5") == 5
        assert to_int("0") == 0
        assert to_int("-10") == -10
    
    def test_valid_string_float(self):
        """Test conversion of valid string floats to integers."""
        assert to_int("5.7") == 5
        assert to_int("5.2") == 5
        assert to_int("-10.8") == -10
    
    def test_formatted_string(self):
        """Test conversion of formatted strings (currency, commas)."""
        assert to_int("$5") == 5
        assert to_int("$5.75") == 5
        assert to_int("1,000") == 1000
        assert to_int("$1,000.50") == 1000
    
    def test_none_value(self):
        """Test handling of None value."""
        assert to_int(None) is None
        assert to_int(None, default=0) == 0
    
    def test_empty_string(self):
        """Test handling of empty string."""
        assert to_int("") is None
        assert to_int("", default=0) == 0
    
    def test_invalid_input(self):
        """Test handling of invalid inputs."""
        assert to_int("abc") is None
        assert to_int("abc", default=0) == 0
        assert to_int([1, 2, 3], default=0) == 0
        assert to_int({"key": "value"}, default=0) == 0

class TestToFloat:
    def test_valid_float(self):
        """Test conversion of valid floats."""
        assert to_float(5.7) == 5.7
        assert to_float(0.0) == 0.0
        assert to_float(-10.8) == -10.8
    
    def test_valid_int(self):
        """Test conversion of valid integers to floats."""
        assert to_float(5) == 5.0
        assert to_float(0) == 0.0
        assert to_float(-10) == -10.0
    
    def test_valid_string_float(self):
        """Test conversion of valid string floats."""
        assert to_float("5.7") == 5.7
        assert to_float("0.0") == 0.0
        assert to_float("-10.8") == -10.8
    
    def test_valid_string_int(self):
        """Test conversion of valid string integers to floats."""
        assert to_float("5") == 5.0
        assert to_float("0") == 0.0
        assert to_float("-10") == -10.0
    
    def test_formatted_string(self):
        """Test conversion of formatted strings (currency, percentage, commas)."""
        assert to_float("$5.75") == 5.75
        assert to_float("5%") == 5.0
        assert to_float("1,000.50") == 1000.50
        assert to_float("$1,000.50") == 1000.50
    
    def test_none_value(self):
        """Test handling of None value."""
        assert to_float(None) is None
        assert to_float(None, default=0.0) == 0.0
    
    def test_empty_string(self):
        """Test handling of empty string."""
        assert to_float("") is None
        assert to_float("", default=0.0) == 0.0
    
    def test_invalid_input(self):
        """Test handling of invalid inputs."""
        assert to_float("abc") is None
        assert to_float("abc", default=0.0) == 0.0
        assert to_float([1, 2, 3], default=0.0) == 0.0
        assert to_float({"key": "value"}, default=0.0) == 0.0

class TestToDecimal:
    def test_valid_decimal(self):
        """Test conversion of valid decimal values."""
        assert to_decimal(Decimal('5.7')) == Decimal('5.7')
        assert to_decimal(Decimal('0.0')) == Decimal('0.0')
        assert to_decimal(Decimal('-10.8')) == Decimal('-10.8')
    
    def test_valid_float(self):
        """Test conversion of valid floats to Decimal."""
        assert to_decimal(5.7) == Decimal('5.7')
        assert to_decimal(0.0) == Decimal('0.0')
        assert to_decimal(-10.8) == Decimal('-10.8')
    
    def test_valid_int(self):
        """Test conversion of valid integers to Decimal."""
        assert to_decimal(5) == Decimal('5')
        assert to_decimal(0) == Decimal('0')
        assert to_decimal(-10) == Decimal('-10')
    
    def test_valid_string_decimal(self):
        """Test conversion of valid string decimals."""
        assert to_decimal("5.7") == Decimal('5.7')
        assert to_decimal("0.0") == Decimal('0.0')
        assert to_decimal("-10.8") == Decimal('-10.8')
    
    def test_formatted_string(self):
        """Test conversion of formatted strings (currency, percentage, commas)."""
        assert to_decimal("$5.75") == Decimal('5.75')
        assert to_decimal("5%") == Decimal('5')
        assert to_decimal("1,000.50") == Decimal('1000.50')
        assert to_decimal("$1,000.50") == Decimal('1000.50')
    
    def test_special_values(self):
        """Test conversion of special string values."""
        assert to_decimal("infinite") == Decimal('Infinity')
        assert to_decimal("∞") == Decimal('Infinity')
        assert to_decimal("INFINITE") == Decimal('Infinity')
    
    def test_none_value(self):
        """Test handling of None value."""
        assert to_decimal(None) is None
        assert to_decimal(None, default=Decimal('0.0')) == Decimal('0.0')
    
    def test_empty_string(self):
        """Test handling of empty string."""
        assert to_decimal("") is None
        assert to_decimal("", default=Decimal('0.0')) == Decimal('0.0')
    
    def test_invalid_input(self):
        """Test handling of invalid inputs."""
        assert to_decimal("abc") is None
        assert to_decimal("abc", default=Decimal('0.0')) == Decimal('0.0')
        assert to_decimal([1, 2, 3], default=Decimal('0.0')) == Decimal('0.0')
        assert to_decimal({"key": "value"}, default=Decimal('0.0')) == Decimal('0.0')

class TestToBool:
    def test_bool_values(self):
        """Test conversion of boolean values."""
        assert to_bool(True) is True
        assert to_bool(False) is False
    
    def test_truthy_strings(self):
        """Test conversion of truthy string values."""
        assert to_bool("true") is True
        assert to_bool("True") is True
        assert to_bool("TRUE") is True
        assert to_bool("t") is True
        assert to_bool("T") is True
        assert to_bool("yes") is True
        assert to_bool("Yes") is True
        assert to_bool("YES") is True
        assert to_bool("y") is True
        assert to_bool("Y") is True
        assert to_bool("1") is True
        assert to_bool("on") is True
        assert to_bool("On") is True
        assert to_bool("ON") is True
    
    def test_falsy_strings(self):
        """Test conversion of falsy string values."""
        assert to_bool("false") is False
        assert to_bool("False") is False
        assert to_bool("FALSE") is False
        assert to_bool("f") is False
        assert to_bool("F") is False
        assert to_bool("no") is False
        assert to_bool("No") is False
        assert to_bool("NO") is False
        assert to_bool("n") is False
        assert to_bool("N") is False
        assert to_bool("0") is False
        assert to_bool("off") is False
        assert to_bool("Off") is False
        assert to_bool("OFF") is False
    
    def test_numeric_values(self):
        """Test conversion of numeric values."""
        assert to_bool(1) is True
        assert to_bool(100) is True
        assert to_bool(0) is False
        assert to_bool(1.0) is True
        assert to_bool(0.0) is False
    
    def test_none_value(self):
        """Test handling of None value."""
        assert to_bool(None) is False
        assert to_bool(None, default=True) is True
    
    def test_empty_string(self):
        """Test handling of empty string."""
        assert to_bool("") is False
        # Empty string is treated as a falsy value, not using default
        assert to_bool("", default=True) is False
    
    def test_other_values(self):
        """Test conversion of other values."""
        # Non-boolean, non-string, non-numeric values use the default
        assert to_bool([]) is False
        assert to_bool([1, 2, 3]) is False  # Lists are not specially handled
        assert to_bool({}) is False
        assert to_bool({"key": "value"}) is False  # Dicts are not specially handled
        assert to_bool("random string") is False
