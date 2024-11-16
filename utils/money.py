from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Union, Optional
import logging

class Money:
    """
    Handles monetary values and formatting.
    """
    
    def __init__(self, amount: Union[Decimal, str, float, int, 'Money', None]) -> None:
        if amount is None:
            self.amount = Decimal('0')
        elif isinstance(amount, Money):
            self.amount = amount.amount
        elif isinstance(amount, Decimal):
            self.amount = amount
        elif isinstance(amount, (float, int)):
            self.amount = Decimal(str(amount))
        elif isinstance(amount, str):
            # Remove currency symbols, commas, and spaces
            cleaned = amount.replace('$', '').replace(',', '').replace(' ', '').strip()
            try:
                self.amount = Decimal(cleaned if cleaned else '0')
            except (ValueError, Decimal.InvalidOperation) as e:
                logging.error(f"Error converting string to Money: {amount}")
                raise ValueError(f"Invalid monetary value: {amount}")
        else:
            raise ValueError(f"Unsupported type for Money: {type(amount)}")
            
    def __add__(self, other: Union['Money', Decimal, float, int, str]) -> 'Money':
        if isinstance(other, Money):
            return Money(self.amount + other.amount)
        return Money(self.amount + Decimal(str(other)))
        
    def __sub__(self, other: Union['Money', Decimal, float, int, str]) -> 'Money':
        if isinstance(other, Money):
            return Money(self.amount - other.amount)
        return Money(self.amount - Decimal(str(other)))
        
    def __mul__(self, other: Union['Percentage', Decimal, float, int, str]) -> 'Money':
        if isinstance(other, Percentage):
            return Money(self.amount * other.as_decimal())
        return Money(self.amount * Decimal(str(other)))
        
    def __truediv__(self, other: Union['Money', Decimal, float, int, str]) -> Union[Decimal, 'Money']:
        if isinstance(other, Money):
            return self.amount / other.amount
        return Money(self.amount / Decimal(str(other)))
        
    def __eq__(self, other: Union['Money', Decimal, float, int, str]) -> bool:
        if isinstance(other, Money):
            return self.amount == other.amount
        return self.amount == Decimal(str(other))
        
    def __lt__(self, other: Union['Money', Decimal, float, int, str]) -> bool:
        if isinstance(other, Money):
            return self.amount < other.amount
        return self.amount < Decimal(str(other))
        
    def __gt__(self, other: Union['Money', Decimal, float, int, str]) -> bool:
        if isinstance(other, Money):
            return self.amount > other.amount
        return self.amount > Decimal(str(other))
        
    def __le__(self, other: Union['Money', Decimal, float, int, str]) -> bool:
        if isinstance(other, Money):
            return self.amount <= other.amount
        return self.amount <= Decimal(str(other))
        
    def __ge__(self, other: Union['Money', Decimal, float, int, str]) -> bool:
        if isinstance(other, Money):
            return self.amount >= other.amount
        return self.amount >= Decimal(str(other))
        
    @property
    def dollars(self) -> Decimal:
        """Return the raw decimal amount"""
        return self.amount
        
    def format(self, include_cents: bool = True) -> str:
        """Format as currency string"""
        if include_cents:
            return f"${self.amount.quantize(Decimal('0.01'), ROUND_HALF_UP):,.2f}"
        return f"${int(self.amount):,}"
        
    def __str__(self) -> str:
        return self.format()
        
    def __repr__(self) -> str:
        return f"Money('{self.format()}')"

class Percentage:
    """
    Handles percentage values and formatting.
    
    Usage:
        rate = Percentage(5.5)
        tax_rate = Percentage('7.25%')
        print(rate.format())  # '5.50%'
        print(tax_rate.as_decimal())  # Decimal('0.0725')
    """
    
    def __init__(self, value: Union[Decimal, str, float, int, 'Percentage']) -> None:
        if isinstance(value, Percentage):
            self.value = value.value
        elif isinstance(value, Decimal):
            self.value = value
        elif isinstance(value, (float, int)):
            self.value = Decimal(str(value))
        elif isinstance(value, str):
            # Remove % symbol and spaces
            cleaned = value.replace('%', '').strip()
            try:
                self.value = Decimal(cleaned if cleaned else '0')
            except (ValueError, Decimal.InvalidOperation) as e:
                logging.error(f"Error converting string to Percentage: {value}")
                raise ValueError(f"Invalid percentage value: {value}")
        else:
            raise ValueError(f"Unsupported type for Percentage: {type(value)}")
            
    def as_decimal(self) -> Decimal:
        """Convert percentage to decimal for calculations (e.g., 5% -> 0.05)"""
        return self.value / Decimal('100')
        
    def format(self, decimal_places: int = 2) -> str:
        """Format as percentage string with specified decimal places"""
        format_str = f"0.{'0' * decimal_places}"
        return f"{self.value.quantize(Decimal(format_str), ROUND_HALF_UP)}%"
        
    def __mul__(self, other: Union['Money', Decimal, float, int, str]) -> Union['Money', Decimal]:
        if isinstance(other, Money):
            return Money(other.dollars * self.as_decimal())
        return Decimal(str(other)) * self.as_decimal()
        
    def __eq__(self, other: Union['Percentage', Decimal, float, int, str]) -> bool:
        if isinstance(other, Percentage):
            return self.value == other.value
        return self.value == Decimal(str(other))
        
    def __str__(self) -> str:
        return self.format()
        
    def __repr__(self) -> str:
        return f"Percentage('{self.format()}')"

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