import pytest
from decimal import Decimal
from unittest.mock import patch
from utils.calculators import AmortizationCalculator
from utils.money import Money, Percentage, MonthlyPayment

class TestAmortizationCalculator:
    """Test suite for the AmortizationCalculator class."""

    def test_calculate_monthly_payment(self):
        """Test calculate_monthly_payment with standard inputs."""
        # Arrange
        loan_amount = Money(200000)
        annual_rate = Percentage(4.5)
        term = 360  # 30 years in months

        # Mock the FinancialCalculator to isolate our test
        expected_payment = MonthlyPayment(
            total=Money(1013.37),
            principal=Money(346.68),
            interest=Money(666.69)
        )
        with patch('utils.financial_calculator.FinancialCalculator.calculate_loan_payment',
                  return_value=expected_payment) as mock_calc:
            
            # Act
            result = AmortizationCalculator.calculate_monthly_payment(
                loan_amount=loan_amount,
                annual_rate=annual_rate,
                term=term
            )
            
            # Assert
            assert result == expected_payment
            mock_calc.assert_called_once_with(
                loan_amount=loan_amount,
                annual_rate=annual_rate,
                term=term,
                is_interest_only=False
            )

    def test_calculate_monthly_payment_with_string_term(self):
        """Test calculate_monthly_payment with string term."""
        # Arrange
        loan_amount = Money(200000)
        annual_rate = Percentage(4.5)
        term = "360"  # 30 years in months as string

        # Mock the FinancialCalculator to isolate our test
        expected_payment = MonthlyPayment(
            total=Money(1013.37),
            principal=Money(346.68),
            interest=Money(666.69)
        )
        with patch('utils.financial_calculator.FinancialCalculator.calculate_loan_payment',
                  return_value=expected_payment) as mock_calc:
            
            # Act
            result = AmortizationCalculator.calculate_monthly_payment(
                loan_amount=loan_amount,
                annual_rate=annual_rate,
                term=term
            )
            
            # Assert
            assert result == expected_payment
            mock_calc.assert_called_once_with(
                loan_amount=loan_amount,
                annual_rate=annual_rate,
                term=term,
                is_interest_only=False
            )

    def test_calculate_monthly_payment_integration(self):
        """Test calculate_monthly_payment with actual calculation (integration test)."""
        # Arrange
        loan_amount = Money(200000)
        annual_rate = Percentage(4.5)
        term = 360  # 30 years in months
        
        # Act
        result = AmortizationCalculator.calculate_monthly_payment(
            loan_amount=loan_amount,
            annual_rate=annual_rate,
            term=term
        )
        
        # Assert
        # We're expecting approximately $1,013.37 for a $200k loan at 4.5% for 30 years
        assert isinstance(result, MonthlyPayment)
        assert abs(float(result.total.amount) - 1013.37) < 1  # Allow for small rounding differences
