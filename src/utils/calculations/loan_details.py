from dataclasses import dataclass
from typing import Optional
import logging
from decimal import Decimal
from src.utils.money import Money, Percentage, MonthlyPayment

logger = logging.getLogger(__name__)

# Constants
MAX_LOAN_TERM = 360  # 30 years
MAX_LOAN_INTEREST_RATE = 30.0  # 30%

@dataclass
class LoanDetails:
    """
    Data class to encapsulate loan parameters.
    
    This class provides a structured way to represent loan details,
    with validation and calculation capabilities.
    
    Args:
        amount: The loan amount
        interest_rate: The annual interest rate as a percentage
        term: The loan term in months
        is_interest_only: Whether the loan is interest-only
        name: Optional name for the loan
        
    Examples:
        >>> loan = LoanDetails(
        ...     amount=Money(200000),
        ...     interest_rate=Percentage(4.5),
        ...     term=360,
        ...     is_interest_only=False,
        ...     name="Primary Mortgage"
        ... )
        >>> payment = loan.calculate_payment()
        >>> print(payment.total)
    """
    amount: Money
    interest_rate: Percentage
    term: int
    is_interest_only: bool = False
    name: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate loan details after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate loan parameters."""
        # Validate amount is positive
        if not isinstance(self.amount, Money):
            self.amount = Money(self.amount)
        
        if self.amount.dollars <= 0:
            raise ValueError("Loan amount must be greater than 0")
        
        # Validate interest rate
        if not isinstance(self.interest_rate, Percentage):
            self.interest_rate = Percentage(self.interest_rate)
            
        if self.interest_rate.value < 0 or self.interest_rate.value > MAX_LOAN_INTEREST_RATE:
            raise ValueError(f"Interest rate must be between 0% and {MAX_LOAN_INTEREST_RATE}%")
        
        # Validate term
        if self.term <= 0 or self.term > MAX_LOAN_TERM:
            raise ValueError(f"Loan term must be between 1 and {MAX_LOAN_TERM} months")
        
        # Validate is_interest_only is boolean
        if not isinstance(self.is_interest_only, bool):
            raise ValueError("is_interest_only must be a boolean value")
    
    def calculate_payment(self) -> MonthlyPayment:
        """
        Calculate monthly payment for the loan.
        
        Returns:
            MonthlyPayment: Object containing total payment, principal, and interest
        
        Raises:
            ValueError: If loan parameters are invalid
        """
        try:
            # Convert to decimal for precise calculation
            loan_amount = Decimal(str(self.amount.dollars))
            annual_rate = Decimal(str(self.interest_rate.as_decimal()))
            monthly_rate = annual_rate / Decimal('12')
            term_months = Decimal(str(self.term))
            
            # Handle zero interest rate
            if annual_rate == 0:
                # For 0% loans, always divide principal by term (whether interest-only or not)
                principal_payment = float(loan_amount / term_months)
                logger.debug(f"Calculated principal-only payment: ${principal_payment:.2f} for 0% loan amount: ${self.amount.dollars:.2f}")
                return MonthlyPayment(
                    total=Money(principal_payment),
                    principal=Money(principal_payment),
                    interest=Money(0)
                )
                    
            # Handle interest-only loans
            if self.is_interest_only:
                # For interest-only, calculate the monthly interest
                interest_payment = float(loan_amount * monthly_rate)
                logger.debug(f"Calculated interest-only payment: ${interest_payment:.2f} for loan amount: ${self.amount.dollars:.2f}")
                return MonthlyPayment(
                    total=Money(interest_payment),
                    principal=Money(0),
                    interest=Money(interest_payment)
                )
                    
            # For regular amortizing loans
            factor = (1 + monthly_rate) ** term_months
            total_payment = float(loan_amount * (monthly_rate * factor / (factor - 1)))
            
            # Calculate interest portion
            interest_payment = float(loan_amount * monthly_rate)
            
            # Calculate principal portion
            principal_payment = total_payment - interest_payment
            
            logger.debug(f"Calculated amortized payment: ${total_payment:.2f} for loan amount: ${self.amount.dollars:.2f}")
            
            return MonthlyPayment(
                total=Money(total_payment),
                principal=Money(principal_payment),
                interest=Money(interest_payment)
            )
            
        except Exception as e:
            logger.error(f"Error calculating loan payment: {str(e)}")
            raise ValueError(f"Failed to calculate loan payment: {str(e)}")
    
    def calculate_remaining_balance(self, payments_made: int) -> Money:
        """
        Calculate remaining loan balance after a number of payments.
        
        Args:
            payments_made: Number of payments already made
            
        Returns:
            Money: Remaining loan balance
            
        Raises:
            ValueError: If payments_made is negative or exceeds the term
        """
        if payments_made < 0:
            raise ValueError("Payments made cannot be negative")
            
        if payments_made >= self.term:
            return Money(0)  # Loan is paid off
            
        if payments_made == 0:
            return self.amount  # No payments made yet
            
        if self.is_interest_only:
            # For interest-only loans, principal doesn't change until final payment
            return self.amount
            
        try:
            # Convert to decimal for precise calculation
            loan_amount = Decimal(str(self.amount.dollars))
            annual_rate = Decimal(str(self.interest_rate.as_decimal()))
            monthly_rate = annual_rate / Decimal('12')
            term_months = Decimal(str(self.term))
            
            # Handle zero interest rate
            if annual_rate == 0:
                # Simple linear reduction
                payment_amount = loan_amount / term_months
                remaining = loan_amount - (payment_amount * Decimal(str(payments_made)))
                return Money(max(0, float(remaining)))
                
            # Calculate payment first
            factor = (1 + monthly_rate) ** term_months
            payment = loan_amount * (monthly_rate * factor / (factor - 1))
            
            # Calculate remaining balance using the formula for remaining balance
            # B = P * [(1 + r)^n - (1 + r)^p] / [(1 + r)^n - 1]
            # where B = balance, P = original loan amount, r = monthly rate, n = term, p = payments made
            remaining_factor = (1 + monthly_rate) ** (term_months - Decimal(str(payments_made)))
            original_factor = (1 + monthly_rate) ** term_months
            remaining_balance = loan_amount * (original_factor - remaining_factor) / (original_factor - 1)
            
            return Money(max(0, float(remaining_balance)))
            
        except Exception as e:
            logger.error(f"Error calculating remaining balance: {str(e)}")
            raise ValueError(f"Failed to calculate remaining balance: {str(e)}")
    
    def generate_amortization_schedule(self, max_periods: Optional[int] = None) -> list[dict]:
        """
        Generate amortization schedule for the loan.
        
        Args:
            max_periods: Maximum number of periods to generate (defaults to full term)
            
        Returns:
            list: List of dictionaries containing payment details for each period
        """
        if max_periods is None:
            max_periods = self.term
            
        if max_periods <= 0:
            return []
            
        schedule = []
        remaining_balance = self.amount.dollars
        
        # Handle interest-only loans
        if self.is_interest_only:
            interest_payment = self.amount.dollars * (self.interest_rate.value / 100 / 12)
            
            # Generate schedule for all periods except the last
            for period in range(1, max_periods):
                schedule.append({
                    'period': period,
                    'payment': Money(interest_payment),
                    'principal': Money(0),
                    'interest': Money(interest_payment),
                    'remaining_balance': Money(remaining_balance)
                })
                
            # Last payment includes principal
            if max_periods == self.term:
                schedule.append({
                    'period': self.term,
                    'payment': Money(remaining_balance + interest_payment),
                    'principal': Money(remaining_balance),
                    'interest': Money(interest_payment),
                    'remaining_balance': Money(0)
                })
            else:
                # If not generating the full schedule, just add another interest-only payment
                schedule.append({
                    'period': max_periods,
                    'payment': Money(interest_payment),
                    'principal': Money(0),
                    'interest': Money(interest_payment),
                    'remaining_balance': Money(remaining_balance)
                })
                
            return schedule
            
        # Handle zero interest rate
        if self.interest_rate.value == 0:
            payment = remaining_balance / self.term
            
            for period in range(1, min(self.term + 1, max_periods + 1)):
                schedule.append({
                    'period': period,
                    'payment': Money(payment),
                    'principal': Money(payment),
                    'interest': Money(0),
                    'remaining_balance': Money(remaining_balance - payment)
                })
                remaining_balance -= payment
                
            return schedule
            
        # Regular amortizing loan
        payment = self.calculate_payment().total.dollars
        
        for period in range(1, min(self.term + 1, max_periods + 1)):
            # Calculate interest for this period
            interest = remaining_balance * (self.interest_rate.value / 100 / 12)
            
            # Calculate principal for this period
            principal = payment - interest
            
            # Handle final payment rounding issues
            if period == self.term or period == max_periods:
                principal = remaining_balance
                payment = principal + interest
                
            # Update remaining balance
            remaining_balance -= principal
            
            # Ensure we don't have negative balance due to rounding
            if remaining_balance < 0:
                remaining_balance = 0
                
            schedule.append({
                'period': period,
                'payment': Money(payment),
                'principal': Money(principal),
                'interest': Money(interest),
                'remaining_balance': Money(remaining_balance)
            })
            
        return schedule
