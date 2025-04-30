from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment, Union

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
        # Convert term to integer
        try:
            term = int(float(str(term)))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid loan term: {term}")

        if term <= 0 or loan_amount.dollars <= 0:
            return MonthlyPayment(
                total=Money(0),
                principal=Money(0),
                interest=Money(0)
            )

        # Convert annual rate to monthly decimal
        monthly_rate = annual_rate.as_decimal() / Decimal('12')
        
        if monthly_rate == 0:
            monthly_payment = loan_amount.dollars / Decimal(term)
            return MonthlyPayment(
                total=Money(monthly_payment),
                principal=Money(monthly_payment),
                interest=Money(0)
            )
            
        # Standard mortgage payment formula
        payment_factor = (
            monthly_rate * (1 + monthly_rate) ** term
        ) / (
            (1 + monthly_rate) ** term - 1
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