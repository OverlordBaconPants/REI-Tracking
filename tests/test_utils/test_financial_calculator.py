import unittest
import sys
import os
from decimal import Decimal

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.financial_calculator import FinancialCalculator
from utils.money import Money, Percentage, MonthlyPayment

class TestFinancialCalculator(unittest.TestCase):
    """Test cases for the FinancialCalculator class."""

    def test_calculate_loan_payment_standard(self):
        """Test standard loan payment calculation."""
        # Test case for a standard 30-year mortgage
        loan_amount = Money(176250)
        annual_rate = Percentage(7.125)
        term = 360  # 30 years
        is_interest_only = False

        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=loan_amount,
            annual_rate=annual_rate,
            term=term,
            is_interest_only=is_interest_only
        )

        # Expected payment for $176,250 at 7.125% for 30 years is $1,187.43
        self.assertAlmostEqual(payment.total.dollars, 1187.43, delta=0.01)
        self.assertGreater(payment.principal.dollars, 0)
        self.assertGreater(payment.interest.dollars, 0)

    def test_calculate_loan_payment_interest_only(self):
        """Test interest-only loan payment calculation."""
        # Test case for an interest-only loan
        loan_amount = Money(140000)
        annual_rate = Percentage(12)
        term = 12  # 1 year
        is_interest_only = True

        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=loan_amount,
            annual_rate=annual_rate,
            term=term,
            is_interest_only=is_interest_only
        )

        # Expected payment for $140,000 at 12% interest-only is $1,400
        self.assertAlmostEqual(payment.total.dollars, 1400.00, delta=0.01)
        self.assertEqual(payment.principal.dollars, 0)
        self.assertAlmostEqual(payment.interest.dollars, 1400.00, delta=0.01)

    def test_calculate_loan_payment_zero_interest(self):
        """Test loan payment calculation with zero interest."""
        # Test case for a zero-interest loan
        loan_amount = Money(12000)
        annual_rate = Percentage(0)
        term = 12  # 1 year
        is_interest_only = False

        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=loan_amount,
            annual_rate=annual_rate,
            term=term,
            is_interest_only=is_interest_only
        )

        # Expected payment for $12,000 at 0% for 12 months is $1,000
        self.assertAlmostEqual(payment.total.dollars, 1000.00, delta=0.01)
        self.assertAlmostEqual(payment.principal.dollars, 1000.00, delta=0.01)
        self.assertEqual(payment.interest.dollars, 0)

    def test_calculate_loan_payment_edge_cases(self):
        """Test loan payment calculation with edge cases."""
        # Test case for zero loan amount
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(0),
            annual_rate=Percentage(5),
            term=360,
            is_interest_only=False
        )
        self.assertEqual(payment.total.dollars, 0)

        # Test case for zero term
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(100000),
            annual_rate=Percentage(5),
            term=0,
            is_interest_only=False
        )
        self.assertEqual(payment.total.dollars, 0)

    def test_calculate_loan_payment_type_handling(self):
        """Test loan payment calculation with different input types."""
        # Test with Decimal inputs
        payment1 = FinancialCalculator.calculate_loan_payment(
            loan_amount=Decimal('176250'),
            annual_rate=Decimal('7.125'),
            term=360,
            is_interest_only=False
        )
        
        # Test with float inputs
        payment2 = FinancialCalculator.calculate_loan_payment(
            loan_amount=176250.0,
            annual_rate=7.125,
            term=360,
            is_interest_only=False
        )
        
        # Test with string inputs
        payment3 = FinancialCalculator.calculate_loan_payment(
            loan_amount="176250",
            annual_rate="7.125",
            term="360",
            is_interest_only=False
        )
        
        # All should give the same result
        self.assertAlmostEqual(payment1.total.dollars, 1187.43, delta=0.01)
        self.assertAlmostEqual(payment2.total.dollars, 1187.43, delta=0.01)
        self.assertAlmostEqual(payment3.total.dollars, 1187.43, delta=0.01)

if __name__ == '__main__':
    unittest.main()
