from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)

class Money:
    """
    Handles monetary values and formatting.
    """
    
    def __init__(self, amount):
        if isinstance(amount, Money):
            self.amount = amount.amount
        elif isinstance(amount, str):
            if amount.lower() == 'infinite' or amount.lower() == '∞':
                self.amount = float('inf')
            else:
                cleaned = amount.replace('$', '').replace(',', '').strip()
                self.amount = Decimal(cleaned if cleaned else '0')
        else:
            self.amount = Decimal(str(amount or 0))

    @property
    def dollars(self) -> float:
        """Get the monetary value as a float."""
        return float('inf') if self.is_infinite else float(self.amount)
    
    @property
    def is_infinite(self) -> bool:
        """Check if the amount is infinite."""
        return isinstance(self.amount, float) and self.amount == float('inf')

    def __str__(self) -> str:
        """Format as currency with proper precision."""
        if self.is_infinite:
            return "∞"
        return f"${self.amount:,.2f}"

    def __repr__(self) -> str:
        return f"Money({self.amount})"
    
    def __add__(self, other):
        if isinstance(other, Money):
            return Money(self.amount + other.amount)
        if hasattr(other, 'as_decimal'):  # Handle Percentage objects
            return Money(self.amount * other.as_decimal())
        return Money(self.amount + Decimal(str(other)))

    def __sub__(self, other):
        if isinstance(other, Money):
            return Money(self.amount - other.amount)
        if hasattr(other, 'as_decimal'):  # Handle Percentage objects
            return Money(self.amount * (Decimal('1') - other.as_decimal()))
        return Money(self.amount - Decimal(str(other)))

    def __mul__(self, other):
        if isinstance(other, Money):
            return Money(self.amount * other.amount)
        if hasattr(other, 'as_decimal'):  # Handle Percentage objects
            return Money(self.amount * other.as_decimal())
        return Money(self.amount * Decimal(str(other)))

    def __truediv__(self, other):
        if isinstance(other, Money):
            if other.amount == 0:
                raise ValueError("Division by zero")
            return Decimal(self.amount / other.amount)
        if hasattr(other, 'as_decimal'):  # Handle Percentage objects
            if other.as_decimal() == 0:
                raise ValueError("Division by zero")
            return Money(self.amount / other.as_decimal())
        other_decimal = Decimal(str(other))
        if other_decimal == 0:
            raise ValueError("Division by zero")
        return Money(self.amount / other_decimal)

    def __eq__(self, other):
        """Equal comparison handling infinite values."""
        if isinstance(other, str):
            if other.lower() == 'infinite':
                return self.is_infinite
            return False
        if isinstance(other, Money):
            if self.is_infinite and other.is_infinite:
                return True
            if self.is_infinite or other.is_infinite:
                return False
            return self.amount == other.amount
        try:
            return self.amount == Decimal(str(other))
        except (ValueError, TypeError):
            return False

    def __lt__(self, other):
        """Less than comparison handling infinite values."""
        if isinstance(other, str) and other.lower() == 'infinite':
            return not self.is_infinite
        if isinstance(other, Money):
            if self.is_infinite:
                return False
            if other.is_infinite:
                return True
            return self.amount < other.amount
        try:
            return self.amount < Decimal(str(other))
        except (ValueError, TypeError):
            return False

    def __le__(self, other):
        """Less than or equal comparison handling infinite values."""
        return self < other or self == other

    def __gt__(self, other):
        """Greater than comparison handling infinite values."""
        if isinstance(other, str) and other.lower() == 'infinite':
            return False
        if isinstance(other, Money):
            if self.is_infinite:
                return not other.is_infinite
            if other.is_infinite:
                return False
            return self.amount > other.amount
        try:
            return self.amount > Decimal(str(other))
        except (ValueError, TypeError):
            return False

    def __ge__(self, other):
        """Greater than or equal comparison handling infinite values."""
        return self > other or self == other
    
class Percentage:
    """
    Handles percentage values and formatting.
    
    Usage:
        rate = Percentage(5.5)
        tax_rate = Percentage('7.25%')
        print(rate)  # '5.500%'
        print(tax_rate.as_decimal())  # Decimal('0.0725')
    """
    
    def __init__(self, value):
        if isinstance(value, Percentage):
            self.value = value.value
        elif isinstance(value, str):
            if value.lower() == 'infinite' or value.lower() == '∞':
                self.value = float('inf')
            else:
                cleaned = value.replace('%', '').strip()
                self.value = float(cleaned if cleaned else '0')
        else:
            self.value = float(value or 0)

    @property
    def is_infinite(self) -> bool:
        """Check if the value is infinite."""
        return self.value == float('inf')

    def as_decimal(self) -> Decimal:
        """Convert percentage to decimal representation."""
        if self.is_infinite:
            return Decimal('Infinity')
        return Decimal(str(self.value / 100.0))

    def __str__(self) -> str:
        """Format as percentage with three decimal places for interest rates."""
        if self.is_infinite:
            return "∞"
        return f"{self.value:.3f}%"

    def __repr__(self) -> str:
        return f"Percentage({self.value})"

    def __eq__(self, other):
        """Equal comparison handling infinite values."""
        if isinstance(other, str):
            if other.lower() == 'infinite':
                return self.is_infinite
            return False
        if isinstance(other, Percentage):
            if self.is_infinite and other.is_infinite:
                return True
            if self.is_infinite or other.is_infinite:
                return False
            return self.value == other.value
        try:
            return self.value == float(other)
        except (ValueError, TypeError):
            return False
        
    def __lt__(self, other):
        """Less than comparison handling infinite values."""
        if isinstance(other, str) and other.lower() == 'infinite':
            return not self.is_infinite
        if isinstance(other, Percentage):
            if self.is_infinite:
                return False
            if other.is_infinite:
                return True
            return self.value < other.value
        try:
            return self.value < float(other)
        except (ValueError, TypeError):
            return False
    
    def __le__(self, other):
        """Less than or equal comparison handling infinite values."""
        return self < other or self == other

    def __gt__(self, other):
        """Greater than comparison handling infinite values."""
        if isinstance(other, str) and other.lower() == 'infinite':
            return False
        if isinstance(other, Percentage):
            if self.is_infinite:
                return not other.is_infinite
            if other.is_infinite:
                return False
            return self.value > other.value
        try:
            return self.value > float(other)
        except (ValueError, TypeError):
            return False

    def __ge__(self, other):
        """Greater than or equal comparison handling infinite values."""
        return self > other or self == other

    def __add__(self, other):
        if isinstance(other, Percentage):
            return Percentage(self.value + other.value)
        return Percentage(self.value + float(other))

    def __sub__(self, other):
        if isinstance(other, Percentage):
            return Percentage(self.value - other.value)
        return Percentage(self.value - float(other))

    def __mul__(self, other):
        if isinstance(other, Percentage):
            return Percentage(self.value * other.value / 100.0)  # Adjust for percentage multiplication
        return Percentage(self.value * float(other))

    def __truediv__(self, other):
        if isinstance(other, Percentage):
            if other.value == 0:
                raise ValueError("Division by zero")
            return self.value / other.value
        if float(other) == 0:
            raise ValueError("Division by zero")
        return Percentage(self.value / float(other))

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
        print(payment.total)  # "$1,000.00"
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
    
    def __str__(self) -> str:
        """Format payment details as a string."""
        return (
            f"Monthly Payment: {self.total}\n"
            f"Principal: {self.principal}\n"
            f"Interest: {self.interest}"
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
        if amount.dollars < min_value or amount.dollars > max_value:
            return f"Amount must be between {Money(min_value)} and {Money(max_value)}"
        return None
    except (ValueError, TypeError) as e:
        logger.error(f"Money validation error: {str(e)}")
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
        if percentage.value < min_value or percentage.value > max_value:
            return f"Percentage must be between {min_value}% and {max_value}%"
        return None
    except (ValueError, TypeError) as e:
        logger.error(f"Percentage validation error: {str(e)}")
        return "Invalid percentage value"