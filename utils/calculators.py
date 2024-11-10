from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment

class AmortizationCalculator:
    """Calculator for loan amortization and payments"""
    
    @staticmethod
    def calculate_monthly_payment(loan_amount: Money, annual_rate: Percentage, term_months: int) -> MonthlyPayment:
        """
        Calculate monthly payment for a loan.
        
        Args:
            loan_amount: Principal loan amount
            annual_rate: Annual interest rate as a percentage
            term_months: Loan term in months
            
        Returns:
            MonthlyPayment object containing payment details
        """
        if term_months <= 0 or loan_amount.dollars <= 0:
            return MonthlyPayment(
                total=Money(0),
                principal=Money(0),
                interest=Money(0)
            )

        # Convert annual rate to monthly decimal
        monthly_rate = annual_rate.as_decimal() / Decimal('12')
        
        if monthly_rate == 0:
            monthly_payment = loan_amount.dollars / Decimal(term_months)
            return MonthlyPayment(
                total=Money(monthly_payment),
                principal=Money(monthly_payment),
                interest=Money(0)
            )
            
        # Standard mortgage payment formula
        payment_factor = (
            monthly_rate * (1 + monthly_rate) ** term_months
        ) / (
            (1 + monthly_rate) ** term_months - 1
        )
        
        monthly_payment = loan_amount.dollars * payment_factor

        # Calculate first month's principal and interest
        monthly_interest = loan_amount.dollars * monthly_rate
        monthly_principal = monthly_payment - monthly_interest
        
        return MonthlyPayment(
            total=Money(monthly_payment),
            principal=Money(monthly_principal),
            interest=Money(monthly_interest)
        )