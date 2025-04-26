import pytest
from decimal import Decimal
from src.utils.money import Money, Percentage, MonthlyPayment

class TestMoney:
    def test_initialization(self):
        """Test different ways to initialize Money objects."""
        # Initialize with integer
        m1 = Money(100)
        assert m1.dollars == 100.0
        assert str(m1) == "$100.00"
        
        # Initialize with float
        m2 = Money(99.99)
        assert m2.dollars == 99.99
        assert str(m2) == "$99.99"
        
        # Initialize with string
        m3 = Money("50.50")
        assert m3.dollars == 50.50
        assert str(m3) == "$50.50"
        
        # Initialize with formatted string
        m4 = Money("$1,234.56")
        assert m4.dollars == 1234.56
        assert str(m4) == "$1,234.56"
        
        # Initialize with another Money object
        m5 = Money(m4)
        assert m5.dollars == 1234.56
        assert str(m5) == "$1,234.56"
        
        # Initialize with None or empty string
        m6 = Money(None)
        assert m6.dollars == 0
        assert str(m6) == "$0.00"
        
        m7 = Money("")
        assert m7.dollars == 0
        assert str(m7) == "$0.00"
        
        # Initialize with infinite value
        m8 = Money("infinite")
        assert m8.is_infinite
        assert str(m8) == "∞"
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations with Money objects."""
        m1 = Money(100)
        m2 = Money(50)
        
        # Addition
        result = m1 + m2
        assert isinstance(result, Money)
        assert result.dollars == 150
        
        # Subtraction
        result = m1 - m2
        assert isinstance(result, Money)
        assert result.dollars == 50
        
        # Multiplication
        result = m1 * 2
        assert isinstance(result, Money)
        assert result.dollars == 200
        
        # Division
        result = m1 / 2
        assert isinstance(result, Money)
        assert result.dollars == 50
        
        # Division by Money
        result = m1 / m2
        assert isinstance(result, Decimal)
        assert float(result) == 2.0
    
    def test_comparison_operations(self):
        """Test comparison operations with Money objects."""
        m1 = Money(100)
        m2 = Money(50)
        m3 = Money(100)
        
        # Equality
        assert m1 == m3
        assert m1 != m2
        
        # Greater than
        assert m1 > m2
        assert not m2 > m1
        
        # Less than
        assert m2 < m1
        assert not m1 < m2
        
        # Greater than or equal
        assert m1 >= m3
        assert m1 >= m2
        
        # Less than or equal
        assert m1 <= m3
        assert m2 <= m1
        
        # Comparison with numbers
        assert m1 == 100
        assert m1 > 50
        assert m1 < 200
    
    def test_infinite_handling(self):
        """Test handling of infinite values."""
        inf_money = Money("infinite")
        regular_money = Money(100)
        
        # Equality
        assert inf_money == "infinite"
        assert inf_money != regular_money
        
        # Comparison
        assert inf_money > regular_money
        assert regular_money < inf_money
        assert not inf_money < regular_money
        
        # Two infinite values are equal
        assert inf_money == Money("∞")
    
    def test_percentage_interaction(self):
        """Test interaction with Percentage objects."""
        m = Money(100)
        p = Percentage(10)  # 10%
        
        # Money * Percentage
        result = m * p
        assert isinstance(result, Money)
        assert result.dollars == 10
        
        # Money + Percentage (adds percentage of the money)
        result = m + p
        assert isinstance(result, Money)
        assert result.dollars == 110
        
        # Money - Percentage (subtracts percentage of the money)
        result = m - p
        assert isinstance(result, Money)
        assert result.dollars == 90

class TestPercentage:
    def test_initialization(self):
        """Test different ways to initialize Percentage objects."""
        # Initialize with integer
        p1 = Percentage(10)
        assert p1.value == 10.0
        assert str(p1) == "10.000%"
        
        # Initialize with float
        p2 = Percentage(5.5)
        assert p2.value == 5.5
        assert str(p2) == "5.500%"
        
        # Initialize with string
        p3 = Percentage("7.25")
        assert p3.value == 7.25
        assert str(p3) == "7.250%"
        
        # Initialize with formatted string
        p4 = Percentage("12.5%")
        assert p4.value == 12.5
        assert str(p4) == "12.500%"
        
        # Initialize with another Percentage object
        p5 = Percentage(p4)
        assert p5.value == 12.5
        assert str(p5) == "12.500%"
        
        # Initialize with None or empty string
        p6 = Percentage(None)
        assert p6.value == 0
        assert str(p6) == "0.000%"
        
        p7 = Percentage("")
        assert p7.value == 0
        assert str(p7) == "0.000%"
        
        # Initialize with infinite value
        p8 = Percentage("infinite")
        assert p8.is_infinite
        assert str(p8) == "∞"
    
    def test_as_decimal(self):
        """Test conversion to decimal representation."""
        p = Percentage(5)
        assert p.as_decimal() == Decimal('0.05')
        
        p = Percentage(12.5)
        assert p.as_decimal() == Decimal('0.125')
        
        p = Percentage(0)
        assert p.as_decimal() == Decimal('0')
        
        p = Percentage("infinite")
        assert str(p.as_decimal()) == "Infinity"
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations with Percentage objects."""
        p1 = Percentage(10)
        p2 = Percentage(5)
        
        # Addition
        result = p1 + p2
        assert isinstance(result, Percentage)
        assert result.value == 15
        
        # Subtraction
        result = p1 - p2
        assert isinstance(result, Percentage)
        assert result.value == 5
        
        # Multiplication
        result = p1 * 2
        assert isinstance(result, Percentage)
        assert result.value == 20
        
        # Multiplication with another percentage
        result = p1 * p2
        assert isinstance(result, Percentage)
        assert result.value == 0.5  # 10% * 5% = 0.5%
        
        # Division
        result = p1 / 2
        assert isinstance(result, Percentage)
        assert result.value == 5
        
        # Division by Percentage
        result = p1 / p2
        assert result == 2.0
    
    def test_comparison_operations(self):
        """Test comparison operations with Percentage objects."""
        p1 = Percentage(10)
        p2 = Percentage(5)
        p3 = Percentage(10)
        
        # Equality
        assert p1 == p3
        assert p1 != p2
        
        # Greater than
        assert p1 > p2
        assert not p2 > p1
        
        # Less than
        assert p2 < p1
        assert not p1 < p2
        
        # Greater than or equal
        assert p1 >= p3
        assert p1 >= p2
        
        # Less than or equal
        assert p1 <= p3
        assert p2 <= p1
        
        # Comparison with numbers
        assert p1 == 10
        assert p1 > 5
        assert p1 < 20
    
    def test_infinite_handling(self):
        """Test handling of infinite values."""
        inf_percentage = Percentage("infinite")
        regular_percentage = Percentage(10)
        
        # Equality
        assert inf_percentage == "infinite"
        assert inf_percentage != regular_percentage
        
        # Comparison
        assert inf_percentage > regular_percentage
        assert regular_percentage < inf_percentage
        assert not inf_percentage < regular_percentage
        
        # Two infinite values are equal
        assert inf_percentage == Percentage("∞")

class TestMonthlyPayment:
    def test_initialization(self):
        """Test initialization of MonthlyPayment objects."""
        # Initialize with Money objects
        payment = MonthlyPayment(
            total=Money(1000),
            principal=Money(800),
            interest=Money(200)
        )
        assert payment.total.dollars == 1000
        assert payment.principal.dollars == 800
        assert payment.interest.dollars == 200
        
        # Initialize with numbers
        payment = MonthlyPayment(
            total=1500,
            principal=1200,
            interest=300
        )
        assert payment.total.dollars == 1500
        assert payment.principal.dollars == 1200
        assert payment.interest.dollars == 300
        
        # Initialize with strings
        payment = MonthlyPayment(
            total="2000",
            principal="1600",
            interest="400"
        )
        assert payment.total.dollars == 2000
        assert payment.principal.dollars == 1600
        assert payment.interest.dollars == 400
    
    def test_string_representation(self):
        """Test string representation of MonthlyPayment."""
        payment = MonthlyPayment(
            total=Money(1000),
            principal=Money(800),
            interest=Money(200)
        )
        
        expected = (
            "Monthly Payment: $1,000.00\n"
            "Principal: $800.00\n"
            "Interest: $200.00"
        )
        
        assert str(payment) == expected
