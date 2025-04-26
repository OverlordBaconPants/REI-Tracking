import pytest
from src.utils.calculations.validation import (
    ValidationError,
    ValidationResult,
    Validator,
    safe_calculation
)
from src.utils.money import Money, Percentage

class TestValidationError:
    def test_initialization(self):
        """Test initialization of ValidationError."""
        error = ValidationError("amount", "Amount must be positive")
        assert error.field == "amount"
        assert error.message == "Amount must be positive"
    
    def test_string_representation(self):
        """Test string representation of ValidationError."""
        error = ValidationError("amount", "Amount must be positive")
        assert str(error) == "amount: Amount must be positive"
        
    def test_repr(self):
        """Test repr of ValidationError."""
        error = ValidationError("amount", "Amount must be positive")
        assert repr(error) == "ValidationError(field='amount', message='Amount must be positive')"

class TestValidationResult:
    def test_initialization(self):
        """Test initialization of ValidationResult."""
        result = ValidationResult()
        assert result.errors == []
        assert result.is_valid()
        
    def test_add_error(self):
        """Test adding errors to ValidationResult."""
        result = ValidationResult()
        result.add_error("amount", "Amount must be positive")
        
        assert len(result.errors) == 1
        assert result.errors[0].field == "amount"
        assert result.errors[0].message == "Amount must be positive"
        assert not result.is_valid()
        
        # Add another error
        result.add_error("term", "Term must be greater than 0")
        assert len(result.errors) == 2
        
    def test_get_error_messages(self):
        """Test getting error messages grouped by field."""
        result = ValidationResult()
        result.add_error("amount", "Amount must be positive")
        result.add_error("amount", "Amount must be less than $1,000,000")
        result.add_error("term", "Term must be greater than 0")
        
        error_dict = result.get_error_messages()
        assert len(error_dict) == 2
        assert "amount" in error_dict
        assert "term" in error_dict
        assert len(error_dict["amount"]) == 2
        assert "Amount must be positive" in error_dict["amount"]
        assert "Amount must be less than $1,000,000" in error_dict["amount"]
        assert len(error_dict["term"]) == 1
        assert "Term must be greater than 0" in error_dict["term"]
        
    def test_get_all_messages(self):
        """Test getting all error messages as a flat list."""
        result = ValidationResult()
        result.add_error("amount", "Amount must be positive")
        result.add_error("term", "Term must be greater than 0")
        
        messages = result.get_all_messages()
        assert len(messages) == 2
        assert "amount: Amount must be positive" in messages
        assert "term: Term must be greater than 0" in messages
        
    def test_string_representation(self):
        """Test string representation of ValidationResult."""
        # Valid result
        result = ValidationResult()
        assert str(result) == "Validation passed"
        
        # Invalid result
        result.add_error("amount", "Amount must be positive")
        assert str(result) == "Validation failed with 1 errors: amount: Amount must be positive"
        
        # Multiple errors
        result.add_error("term", "Term must be greater than 0")
        assert "Validation failed with 2 errors" in str(result)
        assert "amount: Amount must be positive" in str(result)
        assert "term: Term must be greater than 0" in str(result)
        
    def test_boolean_conversion(self):
        """Test boolean conversion of ValidationResult."""
        result = ValidationResult()
        assert bool(result) is True
        
        result.add_error("amount", "Amount must be positive")
        assert bool(result) is False

class TestValidator:
    def test_validate_required(self):
        """Test validation of required fields."""
        result = ValidationResult()
        data = {"name": "Test", "amount": 100}
        
        # Field exists
        assert Validator.validate_required(result, data, "name") is True
        assert result.is_valid()
        
        # Field doesn't exist
        assert Validator.validate_required(result, data, "description") is False
        assert not result.is_valid()
        assert "Missing required field: description" in result.get_all_messages()[0]
        
        # Field exists but is None
        data["price"] = None
        assert Validator.validate_required(result, data, "price") is False
        
        # With custom display name
        assert Validator.validate_required(result, data, "category", "Product Category") is False
        assert "Missing required field: Product Category" in result.get_all_messages()[2]
    
    def test_validate_positive_number(self):
        """Test validation of positive numbers."""
        result = ValidationResult()
        
        # Valid positive number
        assert Validator.validate_positive_number(result, 100, "amount") is True
        assert result.is_valid()
        
        # Valid positive Money
        assert Validator.validate_positive_number(result, Money(50), "price") is True
        assert result.is_valid()
        
        # Zero (not allowed by default)
        assert Validator.validate_positive_number(result, 0, "quantity") is False
        assert not result.is_valid()
        assert "quantity must be greater than 0" in result.get_all_messages()[0]
        
        # Zero (allowed)
        result = ValidationResult()
        assert Validator.validate_positive_number(result, 0, "quantity", allow_zero=True) is True
        assert result.is_valid()
        
        # Negative number
        assert Validator.validate_positive_number(result, -10, "discount", allow_zero=True) is False
        assert not result.is_valid()
        assert "discount must be greater than or equal to 0" in result.get_all_messages()[0]
        
        # Invalid type
        assert Validator.validate_positive_number(result, "abc", "code") is False
        assert "code must be a valid number" in result.get_all_messages()[1]
        
        # With custom display name
        assert Validator.validate_positive_number(result, -5, "tax", "Sales Tax", allow_zero=True) is False
        assert "Sales Tax must be greater than or equal to 0" in result.get_all_messages()[2]
    
    def test_validate_percentage(self):
        """Test validation of percentage values."""
        result = ValidationResult()
        
        # Valid percentage
        assert Validator.validate_percentage(result, 10, "rate") is True
        assert result.is_valid()
        
        # Valid Percentage object
        assert Validator.validate_percentage(result, Percentage(5.5), "interest") is True
        assert result.is_valid()
        
        # Zero
        assert Validator.validate_percentage(result, 0, "discount") is True
        assert result.is_valid()
        
        # Out of range (default 0-100)
        assert Validator.validate_percentage(result, 150, "markup") is False
        assert not result.is_valid()
        assert "markup must be between 0% and 100%" in result.get_all_messages()[0]
        
        # Custom range
        result = ValidationResult()
        assert Validator.validate_percentage(result, 3, "interest_rate", min_val=3.5, max_val=18) is False
        assert not result.is_valid()
        assert "interest_rate must be between 3.5% and 18%" in result.get_all_messages()[0]
        
        # Invalid type
        assert Validator.validate_percentage(result, "abc", "rate") is False
        assert "rate must be a valid percentage" in result.get_all_messages()[1]
        
        # With custom display name
        assert Validator.validate_percentage(result, 200, "tax", "Sales Tax") is False
        assert "Sales Tax must be between 0% and 100%" in result.get_all_messages()[2]
    
    def test_validate_range(self):
        """Test validation of numeric ranges."""
        result = ValidationResult()
        
        # Valid in range
        assert Validator.validate_range(result, 5, "rating", 1, 10) is True
        assert result.is_valid()
        
        # At min boundary
        assert Validator.validate_range(result, 1, "min_rating", 1, 10) is True
        assert result.is_valid()
        
        # At max boundary
        assert Validator.validate_range(result, 10, "max_rating", 1, 10) is True
        assert result.is_valid()
        
        # Below min
        assert Validator.validate_range(result, 0, "below_min", 1, 10) is False
        assert not result.is_valid()
        assert "below_min must be between 1 and 10" in result.get_all_messages()[0]
        
        # Above max
        assert Validator.validate_range(result, 11, "above_max", 1, 10) is False
        assert "above_max must be between 1 and 10" in result.get_all_messages()[1]
        
        # Invalid type
        assert Validator.validate_range(result, "abc", "invalid", 1, 10) is False
        assert "invalid must be a valid number" in result.get_all_messages()[2]
        
        # With custom display name
        assert Validator.validate_range(result, 15, "age", 18, 65, "Customer Age") is False
        assert "Customer Age must be between 18 and 65" in result.get_all_messages()[3]
    
    def test_validate_string(self):
        """Test validation of strings."""
        result = ValidationResult()
        
        # Valid string
        assert Validator.validate_string(result, "test", "name") is True
        assert result.is_valid()
        
        # Not a string
        assert Validator.validate_string(result, 123, "code") is False
        assert not result.is_valid()
        assert "code must be a string" in result.get_all_messages()[0]
        
        # Min length
        assert Validator.validate_string(result, "a", "password", min_length=8) is False
        assert "password must be at least 8 characters" in result.get_all_messages()[1]
        
        # Max length
        assert Validator.validate_string(result, "this is too long", "username", max_length=10) is False
        assert "username must be at most 10 characters" in result.get_all_messages()[2]
        
        # Pattern matching
        import re
        assert Validator.validate_string(result, "abc123", "alphanumeric", pattern=r'^[a-zA-Z0-9]+$') is True
        assert Validator.validate_string(result, "abc-123", "invalid_pattern", pattern=r'^[a-zA-Z0-9]+$') is False
        assert "invalid_pattern has an invalid format" in result.get_all_messages()[3]
        
        # With custom display name
        assert Validator.validate_string(result, 123, "email", "Email Address") is False
        assert "Email Address must be a string" in result.get_all_messages()[4]
    
    def test_validate_date(self):
        """Test validation of date strings."""
        result = ValidationResult()
        
        # Valid date
        assert Validator.validate_date(result, "2025-04-26", "date") is True
        assert result.is_valid()
        
        # Invalid date
        assert Validator.validate_date(result, "2025-13-26", "invalid_date") is False
        assert not result.is_valid()
        assert "invalid_date must be a valid date in format %Y-%m-%d" in result.get_all_messages()[0]
        
        # Not a string
        assert Validator.validate_date(result, 20250426, "not_string") is False
        assert "not_string must be a string" in result.get_all_messages()[1]
        
        # Custom format
        assert Validator.validate_date(result, "04/26/2025", "custom_format", format_str="%m/%d/%Y") is True
        assert Validator.validate_date(result, "2025-04-26", "wrong_format", format_str="%m/%d/%Y") is False
        assert "wrong_format must be a valid date in format %m/%d/%Y" in result.get_all_messages()[2]
        
        # With custom display name
        assert Validator.validate_date(result, "invalid", "dob", "Date of Birth") is False
        assert "Date of Birth must be a valid date in format %Y-%m-%d" in result.get_all_messages()[3]
    
    def test_validate_with_function(self):
        """Test validation with custom function."""
        result = ValidationResult()
        
        # Custom validation function
        def is_even(value):
            return value % 2 == 0
            
        assert Validator.validate_with_function(
            result, 4, "even_number", is_even, "Number must be even"
        ) is True
        assert result.is_valid()
        
        assert Validator.validate_with_function(
            result, 5, "odd_number", is_even, "Number must be even"
        ) is False
        assert not result.is_valid()
        assert "Number must be even" in result.get_all_messages()[0]
        
        # More complex validation
        def is_valid_email(value):
            import re
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return isinstance(value, str) and bool(re.match(pattern, value))
            
        assert Validator.validate_with_function(
            result, "test@example.com", "email", is_valid_email, "Invalid email format"
        ) is True
        
        assert Validator.validate_with_function(
            result, "invalid-email", "invalid_email", is_valid_email, "Invalid email format"
        ) is False
        assert "Invalid email format" in result.get_all_messages()[1]

class TestSafeCalculation:
    def test_safe_calculation_success(self):
        """Test safe_calculation decorator with successful calculation."""
        @safe_calculation(default_value=0)
        def add(a, b):
            return a + b
            
        assert add(2, 3) == 5
    
    def test_safe_calculation_error(self):
        """Test safe_calculation decorator with error."""
        @safe_calculation(default_value=0)
        def divide(a, b):
            return a / b
            
        # Should return default value instead of raising exception
        assert divide(10, 0) == 0
    
    def test_safe_calculation_custom_default(self):
        """Test safe_calculation decorator with custom default value."""
        @safe_calculation(default_value="Error")
        def process(value):
            if value < 0:
                raise ValueError("Value must be positive")
            return f"Processed: {value}"
            
        assert process(5) == "Processed: 5"
        assert process(-5) == "Error"
    
    def test_safe_calculation_none_default(self):
        """Test safe_calculation decorator with None default value."""
        @safe_calculation()  # Default is None
        def risky_operation(value):
            if value == "trigger_error":
                raise RuntimeError("Triggered error")
            return value.upper()
            
        assert risky_operation("hello") == "HELLO"
        assert risky_operation("trigger_error") is None
