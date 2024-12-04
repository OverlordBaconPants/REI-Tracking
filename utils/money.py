from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Union, Optional
import logging

class Money:
    """
    Handles monetary values and formatting.
    """
    
    def __init__(self, amount):
        if isinstance(amount, str):
            cleaned = amount.replace('$', '').replace(',', '').strip()
            self.amount = float(cleaned if cleaned else '0')
        else:
            self.amount = float(amount or 0)

    @property
    def dollars(self):
        return self.amount

    def __str__(self):
        return str(self.amount)

    def __repr__(self):
        return f"Money({self.amount})"

class Percentage:
    """
    Handles percentage values and formatting.
    
    Usage:
        rate = Percentage(5.5)
        tax_rate = Percentage('7.25%')
        print(rate.format())  # '5.50%'
        print(tax_rate.as_decimal())  # Decimal('0.0725')
    """
    
    def __init__(self, value):
       if isinstance(value, str):
           cleaned = value.replace('%', '').strip()
           self.value = float(cleaned if cleaned else '0')
       else:
           self.value = float(value or 0)

    def as_decimal(self):
       return self.value / 100.0

    def __str__(self):
       return str(self.value)

    def __repr__(self):
       return f"Percentage({self.value})"

@dataclass
class MonthlyPayment:
    """
    Represents a monthly payment with principal and interest breakdown.
    
    Usage:
        payment = MonthlyPayment(
            total=Money(1000),
            principal=Money(800),
            interest=Money(200)
        )
        print(payment.format())
    """
    total: Money
    principal: Money
    interest: Money
    
    def __post_init__(self):
        # Ensure all values are Money objects
        if not isinstance(self.total, Money):
            self.total = Money(self.total)
        if not isinstance(self.principal, Money):
            self.principal = Money(self.principal)
        if not isinstance(self.interest, Money):
            self.interest = Money(self.interest)
    
    def format(self) -> str:
        """Format payment details as a string"""
        return (
            f"Monthly Payment: {self.total.format()}\n"
            f"Principal: {self.principal.format()}\n"
            f"Interest: {self.interest.format()}"
        )

def validate_money(value: Union[str, float, int, Money, Decimal],
                  min_value: float = 0,
                  max_value: float = 1e9) -> Optional[str]:
    """
    Validate monetary value and return error message if invalid.
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        None if valid, error message string if invalid
    """
    try:
        amount = Money(value)
        if amount.dollars < Decimal(str(min_value)) or amount.dollars > Decimal(str(max_value)):
            return f"Amount must be between {Money(min_value).format()} and {Money(max_value).format()}"
        return None
    except (ValueError, Decimal.InvalidOperation):
        return "Invalid monetary value"

def validate_percentage(value: Union[str, float, int, Percentage, Decimal],
                       min_value: float = 0,
                       max_value: float = 100) -> Optional[str]:
    """
    Validate percentage value and return error message if invalid.
    
    Args:
        value: Value to validate
        min_value: Minimum allowed percentage
        max_value: Maximum allowed percentage
        
    Returns:
        None if valid, error message string if invalid
    """
    try:
        percentage = Percentage(value)
        if percentage.value < Decimal(str(min_value)) or percentage.value > Decimal(str(max_value)):
            return f"Percentage must be between {min_value}% and {max_value}%"
        return None
    except (ValueError, Decimal.InvalidOperation):
        return "Invalid percentage value"