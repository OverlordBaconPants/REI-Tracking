"""
Loan model module for the REI-Tracker application.

This module provides the Loan model class for representing loans associated with properties,
including loan types, statuses, and balloon payment details.
"""

import uuid
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Union, ClassVar
from enum import Enum
from pydantic import Field, field_validator, model_validator, ConfigDict, BeforeValidator
from typing_extensions import Annotated
from functools import wraps

from src.models.base_model import BaseModel
from src.utils.money import Money, Percentage
from src.utils.calculations.loan_details import LoanDetails

class LoanType(str, Enum):
    """Enum representing different types of loans."""
    INITIAL = "initial"
    REFINANCE = "refinance"
    ADDITIONAL = "additional"
    HELOC = "heloc"
    SELLER_FINANCING = "seller_financing"
    PRIVATE = "private"

class LoanStatus(str, Enum):
    """Enum representing the status of a loan."""
    ACTIVE = "active"
    PAID_OFF = "paid_off"
    REFINANCED = "refinanced"
    DEFAULTED = "defaulted"

# Custom type validators for Money and Percentage
def validate_money(v: Any) -> Money:
    """Convert various types to Money objects."""
    if isinstance(v, Money):
        return v
    return Money(v)

def validate_percentage(v: Any) -> Percentage:
    """Convert various types to Percentage objects."""
    if isinstance(v, Percentage):
        return v
    return Percentage(v)

# Type aliases with validators
MoneyField = Annotated[Money, BeforeValidator(validate_money)]
PercentageField = Annotated[Percentage, BeforeValidator(validate_percentage)]

# Custom date validator
def validate_date(v: Any) -> date:
    """Convert string to date object if needed."""
    if isinstance(v, date):
        return v
    if isinstance(v, str):
        return date.fromisoformat(v)
    raise ValueError(f"Cannot convert {type(v)} to date")

# Date field with validator
DateField = Annotated[date, BeforeValidator(validate_date)]

class BalloonPayment(BaseModel):
    """
    Represents a balloon payment for a loan.
    
    A balloon payment is a large payment due at the end of a loan term,
    typically after a series of smaller payments.
    
    Args:
        due_date: The date when the balloon payment is due
        amount: The amount of the balloon payment (if known)
        term_months: The number of months until the balloon payment is due
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="ignore"
    )
    
    due_date: Optional[DateField] = None
    amount: Optional[MoneyField] = None
    term_months: Optional[int] = None

class LoanData(BaseModel):
    """
    Data model for loan storage.
    
    This class represents the core data structure for storing loan information,
    without the validation and calculation logic of the full Loan model.
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="ignore"
    )
    
    # Required fields
    property_id: str
    loan_type: LoanType
    amount: MoneyField
    interest_rate: PercentageField
    term_months: int
    start_date: DateField
    
    # Optional fields
    is_interest_only: bool = False
    balloon_payment: Optional[BalloonPayment] = None
    lender: Optional[str] = None
    loan_number: Optional[str] = None
    status: LoanStatus = LoanStatus.ACTIVE
    refinanced_from_id: Optional[str] = None
    notes: Optional[str] = None
    name: Optional[str] = None
    
    # Additional fields for tracking
    monthly_payment: Optional[MoneyField] = None
    current_balance: Optional[MoneyField] = None
    last_updated: Optional[DateField] = None
    
    # Metadata
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Loan(BaseModel):
    """
    Model representing a loan associated with a property.
    
    This class extends the functionality of LoanDetails with additional
    properties specific to property loans, including loan type, status,
    balloon payment details, and refinance information.
    
    Args:
        property_id: ID of the property this loan is associated with
        loan_type: Type of loan (initial, refinance, additional, etc.)
        amount: The loan amount
        interest_rate: The annual interest rate as a percentage
        term_months: The loan term in months
        start_date: The date when the loan started
        is_interest_only: Whether the loan is interest-only
        balloon_payment: Optional balloon payment details
        lender: Name of the lender
        loan_number: Loan identification number from the lender
        status: Current status of the loan
        refinanced_from_id: ID of the loan this refinanced (if applicable)
        notes: Additional notes about the loan
        name: Optional name for the loan
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra="ignore"
    )
    
    # Required fields
    property_id: str
    loan_type: LoanType
    amount: MoneyField
    interest_rate: PercentageField
    term_months: int
    start_date: DateField
    
    # Optional fields
    is_interest_only: bool = False
    balloon_payment: Optional[BalloonPayment] = None
    lender: Optional[str] = None
    loan_number: Optional[str] = None
    status: LoanStatus = LoanStatus.ACTIVE
    refinanced_from_id: Optional[str] = None
    notes: Optional[str] = None
    name: Optional[str] = None
    
    # Additional fields for tracking
    monthly_payment: Optional[MoneyField] = None
    current_balance: Optional[MoneyField] = None
    last_updated: Optional[DateField] = None
    
    # Metadata
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    @model_validator(mode='after')
    def calculate_monthly_payment(self) -> 'Loan':
        """Calculate monthly payment if not provided."""
        if self.monthly_payment is None:
            loan_details = self.to_loan_details()
            self.monthly_payment = loan_details.calculate_payment().total
        return self
    
    def to_loan_details(self) -> LoanDetails:
        """
        Convert this loan to a LoanDetails object for calculations.
        
        Returns:
            LoanDetails: A LoanDetails object with this loan's parameters
        """
        return LoanDetails(
            amount=self.amount,
            interest_rate=self.interest_rate,
            term=self.term_months,
            is_interest_only=self.is_interest_only,
            name=self.name or f"{self.loan_type.value.capitalize()} Loan"
        )
    
    def calculate_remaining_balance(self, as_of_date: Optional[date] = None) -> Money:
        """
        Calculate the remaining balance of the loan as of a specific date.
        
        Args:
            as_of_date: The date to calculate the balance for (defaults to today)
            
        Returns:
            Money: The remaining balance
        """
        if as_of_date is None:
            as_of_date = date.today()
            
        # If the loan hasn't started yet, return the full amount
        if as_of_date < self.start_date:
            return self.amount
            
        # If the loan is paid off or refinanced, return zero
        if self.status in (LoanStatus.PAID_OFF, LoanStatus.REFINANCED):
            return Money(0)
            
        # Calculate months elapsed
        months_elapsed = (
            (as_of_date.year - self.start_date.year) * 12 + 
            as_of_date.month - self.start_date.month
        )
        
        # Adjust for partial months
        if as_of_date.day < self.start_date.day:
            months_elapsed -= 1
            
        # Ensure we don't calculate negative elapsed time
        months_elapsed = max(0, months_elapsed)
        
        # If we've passed the term, return zero unless it's interest-only
        if months_elapsed >= self.term_months and not self.is_interest_only:
            return Money(0)
            
        # Use LoanDetails to calculate the remaining balance
        loan_details = self.to_loan_details()
        return loan_details.calculate_remaining_balance(months_elapsed)
    
    def generate_amortization_schedule(self, max_periods: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate an amortization schedule for this loan.
        
        Args:
            max_periods: Maximum number of periods to generate (defaults to full term)
            
        Returns:
            List[Dict]: A list of dictionaries containing payment details for each period
        """
        loan_details = self.to_loan_details()
        schedule = loan_details.generate_amortization_schedule(max_periods)
        
        # Add dates to the schedule
        for i, period in enumerate(schedule):
            # Calculate the payment date (start_date + i months)
            payment_year = self.start_date.year + (self.start_date.month + i - 1) // 12
            payment_month = (self.start_date.month + i - 1) % 12 + 1
            payment_day = min(self.start_date.day, 28)  # Avoid invalid dates
            
            period['date'] = date(payment_year, payment_month, payment_day).isoformat()
            
        return schedule
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the loan to a dictionary for serialization.
        
        Returns:
            Dict: A dictionary representation of the loan
        """
        result = self.model_dump(exclude_none=True)
        
        # Convert enum values to strings
        result['loan_type'] = self.loan_type.value
        result['status'] = self.status.value
        
        # Convert Money objects to strings
        result['amount'] = str(self.amount)
        result['interest_rate'] = str(self.interest_rate)
        
        if self.monthly_payment:
            result['monthly_payment'] = str(self.monthly_payment)
            
        if self.current_balance:
            result['current_balance'] = str(self.current_balance)
            
        # Convert dates to ISO format strings
        result['start_date'] = self.start_date.isoformat()
        # created_at and updated_at are already ISO format strings
        result['created_at'] = self.created_at
        result['updated_at'] = self.updated_at
        
        if self.last_updated:
            result['last_updated'] = self.last_updated.isoformat()
            
        # Convert balloon payment to dict if present
        if self.balloon_payment:
            result['balloon_payment'] = {
                'term_months': self.balloon_payment.term_months,
                'amount': str(self.balloon_payment.amount) if self.balloon_payment.amount else None,
                'due_date': self.balloon_payment.due_date.isoformat() if self.balloon_payment.due_date else None
            }
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Loan':
        """
        Create a Loan instance from a dictionary.
        
        Args:
            data: Dictionary containing loan data
            
        Returns:
            Loan: A new Loan instance
        """
        # Make a copy to avoid modifying the original
        loan_data = data.copy()
        
        # Handle balloon payment if present
        if 'balloon_payment' in loan_data and loan_data['balloon_payment']:
            balloon_data = loan_data['balloon_payment']
            loan_data['balloon_payment'] = BalloonPayment(
                term_months=balloon_data.get('term_months'),
                amount=balloon_data.get('amount'),
                due_date=balloon_data.get('due_date')
            )
            
        return cls(**loan_data)
    
    def to_data_model(self) -> LoanData:
        """
        Convert this loan to a data model for storage.
        
        Returns:
            LoanData: A data model representation of this loan
        """
        return LoanData(**self.model_dump())
    
    @classmethod
    def from_data_model(cls, data_model: LoanData) -> 'Loan':
        """
        Create a Loan instance from a data model.
        
        Args:
            data_model: LoanData instance
            
        Returns:
            Loan: A new Loan instance
        """
        return cls(**data_model.model_dump())
