import pytest
from services.analysis_calculations import format_percentage_or_infinite
from utils.money import Money
from utils.validators import Percentage

class TestFormatPercentageOrInfiniteExtra:
    def test_format_percentage_or_infinite_with_none(self):
        """Test formatting None value."""
        result = format_percentage_or_infinite(None)
        assert result == "None"
    
    def test_format_percentage_or_infinite_with_string(self):
        """Test formatting string value."""
        result = format_percentage_or_infinite("test")
        assert result == "test"
    
    def test_format_percentage_or_infinite_with_money(self):
        """Test formatting Money object."""
        result = format_percentage_or_infinite(Money(100))
        assert result == "$100.00"
