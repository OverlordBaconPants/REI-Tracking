import pytest
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment, ensure_money, ensure_percentage


class TestMoney:
    """Test suite for the Money class."""

    def test_initialization_with_various_types(self):
        """Test Money initialization with different types of input."""
        # Test with integer
        money_int = Money(100)
        assert money_int.dollars == 100.0
        assert str(money_int) == "$100.00"

        # Test with float
        money_float = Money(99.99)
        assert money_float.dollars == 99.99
        assert str(money_float) == "$99.99"

        # Test with string
        money_str = Money("50.50")
        assert money_str.dollars == 50.50
        assert str(money_str) == "$50.50"

        # Test with Decimal
        money_decimal = Money(Decimal("123.45"))
        assert money_decimal.dollars == 123.45
        assert str(money_decimal) == "$123.45"

        # Test with another Money object
        money_from_money = Money(money_int)
        assert money_from_money.dollars == 100.0
        assert str(money_from_money) == "$100.00"

    def test_infinite_money(self):
        """Test handling of infinite values."""
        # Test initialization with 'infinite' string
        inf_money1 = Money("infinite")
        assert inf_money1.is_infinite
        assert str(inf_money1) == "∞"

        # Test initialization with '∞' symbol
        inf_money2 = Money("∞")
        assert inf_money2.is_infinite
        assert str(inf_money2) == "∞"

    def test_arithmetic_operations(self):
        """Test arithmetic operations with Money objects."""
        money1 = Money(100)
        money2 = Money(50)

        # Addition
        result = money1 + money2
        assert isinstance(result, Money)
        assert result.dollars == 150.0

        # Addition with number
        result = money1 + 25
        assert result.dollars == 125.0

        # Subtraction
        result = money1 - money2
        assert result.dollars == 50.0

        # Subtraction with number
        result = money1 - 25
        assert result.dollars == 75.0

        # Multiplication
        result = money1 * money2
        assert result.dollars == 5000.0

        # Multiplication with number
        result = money1 * 2
        assert result.dollars == 200.0

        # Division (Money / Money)
        result = money1 / money2
        assert isinstance(result, Decimal)
        assert float(result) == 2.0

        # Division (Money / number)
        result = money1 / 2
        assert isinstance(result, Money)
        assert result.dollars == 50.0

    def test_comparison_operations(self):
        """Test comparison operations with Money objects."""
        money1 = Money(100)
        money2 = Money(50)
        money3 = Money(100)
        inf_money = Money("infinite")

        # Equality
        assert money1 == money3
        assert money1 != money2
        assert money1 == 100
        assert money1 != "100"  # String comparison should fail
        assert inf_money == "infinite"
        assert inf_money != money1

        # Less than
        assert money2 < money1
        assert money2 < 100
        assert not (money1 < money2)
        assert money1 < inf_money
        assert not (inf_money < money1)
        assert not (inf_money < "infinite")

        # Less than or equal
        assert money2 <= money1
        assert money1 <= money3
        assert money1 <= 100
        assert money1 <= inf_money

        # Greater than
        assert money1 > money2
        assert money1 > 50
        assert not (money2 > money1)
        assert inf_money > money1
        assert not (money1 > inf_money)

        # Greater than or equal
        assert money1 >= money2
        assert money1 >= money3
        assert money1 >= 100
        assert inf_money >= money1

    def test_ensure_money_function(self):
        """Test the ensure_money utility function."""
        # Already a Money object
        money = Money(100)
        result = ensure_money(money)
        assert result is money  # Should return the same object

        # Convert other types
        assert ensure_money(50).dollars == 50.0
        assert ensure_money("75.25").dollars == 75.25
        assert ensure_money(Decimal("123.45")).dollars == 123.45


class TestPercentage:
    """Test suite for the Percentage class."""

    def test_initialization_with_various_types(self):
        """Test Percentage initialization with different types of input."""
        # Test with integer
        pct_int = Percentage(5)
        assert pct_int.value == 5.0
        assert str(pct_int) == "5.000%"

        # Test with float
        pct_float = Percentage(3.75)
        assert pct_float.value == 3.75
        assert str(pct_float) == "3.750%"

        # Test with string
        pct_str = Percentage("2.5")
        assert pct_str.value == 2.5
        assert str(pct_str) == "2.500%"

        # Test with string including % symbol
        pct_str_symbol = Percentage("4.25%")
        assert pct_str_symbol.value == 4.25
        assert str(pct_str_symbol) == "4.250%"

        # Test with another Percentage object
        pct_from_pct = Percentage(pct_int)
        assert pct_from_pct.value == 5.0
        assert str(pct_from_pct) == "5.000%"

    def test_infinite_percentage(self):
        """Test handling of infinite values."""
        # Test initialization with 'infinite' string
        inf_pct1 = Percentage("infinite")
        assert inf_pct1.is_infinite
        assert str(inf_pct1) == "∞"

        # Test initialization with '∞' symbol
        inf_pct2 = Percentage("∞")
        assert inf_pct2.is_infinite
        assert str(inf_pct2) == "∞"

    def test_as_decimal_conversion(self):
        """Test conversion to decimal representation."""
        pct = Percentage(5)
        assert pct.as_decimal() == Decimal("0.05")

        pct = Percentage(100)
        assert pct.as_decimal() == Decimal("1")

        pct = Percentage(0)
        assert pct.as_decimal() == Decimal("0")

        inf_pct = Percentage("infinite")
        assert str(inf_pct.as_decimal()) == "Infinity"

    def test_arithmetic_operations(self):
        """Test arithmetic operations with Percentage objects."""
        pct1 = Percentage(5)
        pct2 = Percentage(2)

        # Addition
        result = pct1 + pct2
        assert isinstance(result, Percentage)
        assert result.value == 7.0

        # Addition with number
        result = pct1 + 3
        assert result.value == 8.0

        # Subtraction
        result = pct1 - pct2
        assert result.value == 3.0

        # Subtraction with number
        result = pct1 - 2
        assert result.value == 3.0

        # Multiplication
        result = pct1 * pct2
        assert result.value == 0.1  # 5% * 2% = 0.05 * 0.02 = 0.001 (0.1%)

        # Multiplication with number
        result = pct1 * 2
        assert result.value == 10.0

        # Division (Percentage / Percentage)
        result = pct1 / pct2
        assert result == 2.5

        # Division (Percentage / number)
        result = pct1 / 2
        assert isinstance(result, Percentage)
        assert result.value == 2.5

    def test_comparison_operations(self):
        """Test comparison operations with Percentage objects."""
        pct1 = Percentage(5)
        pct2 = Percentage(2)
        pct3 = Percentage(5)
        inf_pct = Percentage("infinite")

        # Equality
        assert pct1 == pct3
        assert pct1 != pct2
        assert pct1 == 5
        assert pct1 != "5"  # String comparison should fail
        assert inf_pct == "infinite"
        assert inf_pct != pct1

        # Less than
        assert pct2 < pct1
        assert pct2 < 5
        assert not (pct1 < pct2)
        assert pct1 < inf_pct
        assert not (inf_pct < pct1)
        assert not (inf_pct < "infinite")

        # Less than or equal
        assert pct2 <= pct1
        assert pct1 <= pct3
        assert pct1 <= 5
        assert pct1 <= inf_pct

        # Greater than
        assert pct1 > pct2
        assert pct1 > 2
        assert not (pct2 > pct1)
        assert inf_pct > pct1
        assert not (pct1 > inf_pct)

        # Greater than or equal
        assert pct1 >= pct2
        assert pct1 >= pct3
        assert pct1 >= 5
        assert inf_pct >= pct1

    def test_ensure_percentage_function(self):
        """Test the ensure_percentage utility function."""
        # Already a Percentage object
        pct = Percentage(5)
        result = ensure_percentage(pct)
        assert result is pct  # Should return the same object

        # Convert other types
        assert ensure_percentage(3).value == 3.0
        assert ensure_percentage("4.5").value == 4.5
        assert ensure_percentage("6.75%").value == 6.75
        assert ensure_percentage(Decimal("7.5")).value == 7.5


class TestMonthlyPayment:
    """Test suite for the MonthlyPayment class."""

    def test_initialization(self):
        """Test MonthlyPayment initialization and post-initialization processing."""
        # Test with Money objects
        payment = MonthlyPayment(
            total=Money(1000),
            principal=Money(800),
            interest=Money(200)
        )
        assert isinstance(payment.total, Money)
        assert isinstance(payment.principal, Money)
        assert isinstance(payment.interest, Money)
        assert payment.total.dollars == 1000.0
        assert payment.principal.dollars == 800.0
        assert payment.interest.dollars == 200.0

        # Test with non-Money objects (should be converted)
        payment = MonthlyPayment(
            total=1200,
            principal="900.50",
            interest=Decimal("299.50")
        )
        assert isinstance(payment.total, Money)
        assert isinstance(payment.principal, Money)
        assert isinstance(payment.interest, Money)
        assert payment.total.dollars == 1200.0
        assert payment.principal.dollars == 900.50
        assert payment.interest.dollars == 299.50

    def test_string_representation(self):
        """Test string representation of MonthlyPayment."""
        payment = MonthlyPayment(
            total=Money(1000),
            principal=Money(800),
            interest=Money(200)
        )
        expected_str = (
            "Monthly Payment: $1,000.00\n"
            "Principal: $800.00\n"
            "Interest: $200.00"
        )
        assert str(payment) == expected_str
