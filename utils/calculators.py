from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment, Union
from utils.financial_calculator import FinancialCalculator

class AmortizationCalculator:
    """Calculator for loan amortization and payments"""
    
    @staticmethod
    def calculate_monthly_payment(loan_amount: Money, annual_rate: Percentage, term: Union[int, str]) -> MonthlyPayment:
        """
        Calculate monthly payment for a loan.
        
        Args:
            loan_amount: Principal loan amount
            annual_rate: Annual interest rate as a percentage
            term: Loan term in months
            
        Returns:
            MonthlyPayment object containing payment details
        """
        # Use the centralized financial calculator
        return FinancialCalculator.calculate_loan_payment(
            loan_amount=loan_amount,
            annual_rate=annual_rate,
            term=term,
            is_interest_only=False
        )
