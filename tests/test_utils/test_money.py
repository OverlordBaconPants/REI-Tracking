import unittest
from decimal import Decimal, ROUND_HALF_UP
from utils.money import Money, Percentage, MonthlyPayment, validate_money, validate_percentage

class TestMoney(unittest.TestCase):
    """Test suite for Money class."""

    def test_money_initialization(self):
        """Test Money initialization with different types."""
        test_cases = [
            (100, Decimal('100')),
            ('100.50', Decimal('100.50')),
            (100.50, Decimal('100.50')),
            ('$1,234.56', Decimal('1234.56')),
            (Money(100), Decimal('100')),
            (Decimal('100.50'), Decimal('100.50'))
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                money = Money(input_value)
                self.assertEqual(money.dollars, expected)

    def test_money_invalid_initialization(self):
        """Test Money initialization with invalid values."""
        invalid_values = [
            'invalid',
            '',
            None,
            [100],
            {'amount': 100}
        ]
        
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Money(value)

    def test_money_arithmetic(self):
        """Test Money arithmetic operations."""
        m1 = Money(100)
        m2 = Money(50)
        
        # Addition
        self.assertEqual((m1 + m2).dollars, Decimal('150'))
        self.assertEqual((m1 + 50).dollars, Decimal('150'))
        
        # Subtraction
        self.assertEqual((m1 - m2).dollars, Decimal('50'))
        self.assertEqual((m1 - 50).dollars, Decimal('50'))
        
        # Multiplication
        self.assertEqual((m1 * 2).dollars, Decimal('200'))
        self.assertEqual((m1 * Percentage(50)).dollars, Decimal('50'))
        
        # Division
        self.assertEqual(m1 / m2, Decimal('2'))
        self.assertEqual((m1 / 2).dollars, Decimal('50'))

    def test_money_comparisons(self):
        """Test Money comparison operations."""
        m1 = Money(100)
        m2 = Money(50)
        m3 = Money(100)
        
        # Equality
        self.assertEqual(m1, m3)
        self.assertNotEqual(m1, m2)
        
        # Less than
        self.assertTrue(m2 < m1)
        self.assertFalse(m1 < m2)
        
        # Greater than
        self.assertTrue(m1 > m2)
        self.assertFalse(m2 > m1)
        
        # Less than or equal
        self.assertTrue(m2 <= m1)
        self.assertTrue(m1 <= m3)
        
        # Greater than or equal
        self.assertTrue(m1 >= m2)
        self.assertTrue(m1 >= m3)

    def test_money_formatting(self):
        """Test Money formatting."""
        test_cases = [
            (Money(1234.56), True, '$1,234.56'),
            (Money(1234.56), False, '$1,234'),
            (Money(1000000), True, '$1,000,000.00'),
            (Money(-1234.56), True, '-$1,234.56')
        ]
        
        for money, include_cents, expected in test_cases:
            with self.subTest(money=money, include_cents=include_cents):
                self.assertEqual(money.format(include_cents=include_cents), expected)

class TestPercentage(unittest.TestCase):
    """Test suite for Percentage class."""

    def test_percentage_initialization(self):
        """Test Percentage initialization with different types."""
        test_cases = [
            (5.5, Decimal('5.5')),
            ('5.5%', Decimal('5.5')),
            (Decimal('5.5'), Decimal('5.5')),
            (Percentage(5.5), Decimal('5.5'))
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                percentage = Percentage(input_value)
                self.assertEqual(percentage.value, expected)

    def test_percentage_invalid_initialization(self):
        """Test Percentage initialization with invalid values."""
        invalid_values = [
            'invalid',
            '',
            None,
            [5.5],
            {'value': 5.5}
        ]
        
        for value in invalid_values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    Percentage(value)

    def test_percentage_conversions(self):
        """Test Percentage conversions and formatting."""
        p = Percentage(5.5)
        
        # Test decimal conversion
        self.assertEqual(p.as_decimal(), Decimal('0.055'))
        
        # Test formatting
        self.assertEqual(p.format(), '5.50%')
        self.assertEqual(p.format(decimal_places=3), '5.500%')

    def test_percentage_multiplication(self):
        """Test Percentage multiplication."""
        p = Percentage(10)
        m = Money(100)
        
        # Test multiplication with Money
        self.assertEqual((p * m).dollars, Decimal('10'))
        
        # Test multiplication with numbers
        self.assertEqual(p * 100, Decimal('10'))

class TestMonthlyPayment(unittest.TestCase):
    """Test suite for MonthlyPayment class."""

    def test_monthly_payment_initialization(self):
        """Test MonthlyPayment initialization."""
        payment = MonthlyPayment(
            total=1000,
            principal=800,
            interest=200
        )
        
        self.assertIsInstance(payment.total, Money)
        self.assertIsInstance(payment.principal, Money)
        self.assertIsInstance(payment.interest, Money)
        
        self.assertEqual(payment.total.dollars, Decimal('1000'))
        self.assertEqual(payment.principal.dollars, Decimal('800'))
        self.assertEqual(payment.interest.dollars, Decimal('200'))

    def test_monthly_payment_formatting(self):
        """Test MonthlyPayment formatting."""
        payment = MonthlyPayment(
            total=1000,
            principal=800,
            interest=200
        )
        
        formatted = payment.format()
        self.assertIn('$1,000.00', formatted)
        self.assertIn('$800.00', formatted)
        self.assertIn('$200.00', formatted)

class TestValidation(unittest.TestCase):
    """Test suite for validation functions."""

    def test_validate_money(self):
        """Test money validation."""
        test_cases = [
            (100, 0, 1000, None),
            (-100, -1000, 1000, None),
            (100, 200, 1000, "Amount must be between"),
            ('invalid', 0, 1000, "Invalid monetary value"),
            (1e10, 0, 1e9, "Amount must be between")
        ]
        
        for value, min_val, max_val, expected_error in test_cases:
            with self.subTest(value=value):
                result = validate_money(value, min_val, max_val)
                if expected_error:
                    self.assertIsNotNone(result)
                    self.assertIn(expected_error, result)
                else:
                    self.assertIsNone(result)

    def test_validate_percentage(self):
        """Test percentage validation."""
        test_cases = [
            (5.5, 0, 100, None),
            (-5.5, -10, 100, None),
            (150, 0, 100, "Percentage must be between"),
            ('invalid', 0, 100, "Invalid percentage value")
        ]
        
        for value, min_val, max_val, expected_error in test_cases:
            with self.subTest(value=value):
                result = validate_percentage(value, min_val, max_val)
                if expected_error:
                    self.assertIsNotNone(result)
                    self.assertIn(expected_error, result)
                else:
                    self.assertIsNone(result)

class TestEdgeCases(unittest.TestCase):
    """Test suite for edge cases."""

    def test_money_precision(self):
        """Test Money precision handling."""
        # Test rounding
        money = Money('100.125')
        self.assertEqual(money.format(), '$100.13')  # Should round up
        
        money = Money('100.124')
        self.assertEqual(money.format(), '$100.12')  # Should round down
        
        # Test many decimal places
        money = Money('100.1234567890')
        self.assertEqual(money.format(), '$100.12')

    def test_percentage_precision(self):
        """Test Percentage precision handling."""
        # Test rounding
        percentage = Percentage('5.125')
        self.assertEqual(percentage.format(), '5.13%')  # Should round up
        
        percentage = Percentage('5.124')
        self.assertEqual(percentage.format(), '5.12%')  # Should round down

    def test_zero_values(self):
        """Test handling of zero values."""
        # Money
        zero_money = Money(0)
        self.assertEqual(zero_money.format(), '$0.00')
        
        # Percentage
        zero_percentage = Percentage(0)
        self.assertEqual(zero_percentage.format(), '0.00%')
        
        # Division by zero
        with self.assertRaises(decimal.DivisionByZero):
            Money(100) / Money(0)

    def test_large_values(self):
        """Test handling of large values."""
        large_money = Money(1e9)
        self.assertEqual(large_money.format(), '$1,000,000,000.00')
        
        large_percentage = Percentage(1000)
        self.assertEqual(large_percentage.format(), '1000.00%')

if __name__ == '__main__':
    unittest.main()