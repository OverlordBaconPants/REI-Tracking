"""
Property model module for the REI-Tracker application.

This module provides the Property model for real estate property management.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import Field, validator

from src.models.base_model import BaseModel
from src.utils.validation_utils import validate_date, validate_decimal, percentage_validator


class Partner(BaseModel):
    """
    Partner model for property ownership.
    
    This class represents a partner with an equity share in a property.
    """
    
    name: str
    equity_share: Decimal
    is_property_manager: bool = False
    
    @validator("equity_share")
    def validate_equity_share(cls, v: Decimal) -> Decimal:
        """
        Validate equity share.
        
        Args:
            v: The equity share to validate
            
        Returns:
            The validated equity share
            
        Raises:
            ValueError: If the equity share is invalid
        """
        if not validate_decimal(v, 0, 100):
            raise ValueError("Equity share must be between 0 and 100")
        return v


class Utilities(BaseModel):
    """
    Utilities model for property expenses.
    
    This class represents the utility expenses for a property.
    """
    
    water: Decimal = Decimal("0")
    electricity: Decimal = Decimal("0")
    gas: Decimal = Decimal("0")
    trash: Decimal = Decimal("0")
    
    _validate_decimal = percentage_validator()


class MonthlyIncome(BaseModel):
    """
    Monthly income model for property income.
    
    This class represents the monthly income for a property.
    """
    
    rental_income: Decimal = Decimal("0")
    parking_income: Decimal = Decimal("0")
    laundry_income: Decimal = Decimal("0")
    other_income: Decimal = Decimal("0")
    income_notes: Optional[str] = None
    
    _validate_decimal = percentage_validator()
    
    def total(self) -> Decimal:
        """
        Calculate the total monthly income.
        
        Returns:
            The total monthly income
        """
        return (
            self.rental_income +
            self.parking_income +
            self.laundry_income +
            self.other_income
        )


class MonthlyExpenses(BaseModel):
    """
    Monthly expenses model for property expenses.
    
    This class represents the monthly expenses for a property.
    """
    
    property_tax: Decimal = Decimal("0")
    insurance: Decimal = Decimal("0")
    repairs: Decimal = Decimal("0")
    capex: Decimal = Decimal("0")
    property_management: Decimal = Decimal("0")
    hoa_fees: Decimal = Decimal("0")
    utilities: Utilities = Field(default_factory=Utilities)
    other_expenses: Decimal = Decimal("0")
    expense_notes: Optional[str] = None
    
    _validate_decimal = percentage_validator()
    
    def total(self) -> Decimal:
        """
        Calculate the total monthly expenses.
        
        Returns:
            The total monthly expenses
        """
        utilities_total = (
            self.utilities.water +
            self.utilities.electricity +
            self.utilities.gas +
            self.utilities.trash
        )
        
        return (
            self.property_tax +
            self.insurance +
            self.repairs +
            self.capex +
            self.property_management +
            self.hoa_fees +
            utilities_total +
            self.other_expenses
        )


class Loan(BaseModel):
    """
    Loan model for property financing.
    
    This class represents a loan used to finance a property.
    """
    
    name: str
    amount: Decimal
    interest_rate: Decimal
    term: int  # In months
    down_payment: Decimal = Decimal("0")
    closing_costs: Decimal = Decimal("0")
    start_date: Optional[str] = None
    
    @validator("interest_rate")
    def validate_interest_rate(cls, v: Decimal) -> Decimal:
        """
        Validate interest rate.
        
        Args:
            v: The interest rate to validate
            
        Returns:
            The validated interest rate
            
        Raises:
            ValueError: If the interest rate is invalid
        """
        if not validate_decimal(v, 0, 100):
            raise ValueError("Interest rate must be between 0 and 100")
        return v
    
    @validator("term")
    def validate_term(cls, v: int) -> int:
        """
        Validate loan term.
        
        Args:
            v: The loan term to validate
            
        Returns:
            The validated loan term
            
        Raises:
            ValueError: If the loan term is invalid
        """
        if v <= 0:
            raise ValueError("Loan term must be positive")
        return v
    
    @validator("start_date")
    def validate_start_date(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate loan start date.
        
        Args:
            v: The loan start date to validate
            
        Returns:
            The validated loan start date
            
        Raises:
            ValueError: If the loan start date is invalid
        """
        if v is not None and not validate_date(v):
            raise ValueError("Invalid loan start date format (should be YYYY-MM-DD)")
        return v


class Property(BaseModel):
    """
    Property model for real estate property management.
    
    This class represents a real estate property in the system, including
    purchase details, financing, income, expenses, and partnership information.
    """
    
    # Property identification
    address: str
    
    # Purchase details
    purchase_price: Decimal
    purchase_date: str
    down_payment: Decimal = Decimal("0")
    closing_costs: Decimal = Decimal("0")
    renovation_costs: Decimal = Decimal("0")
    marketing_costs: Decimal = Decimal("0")
    holding_costs: Decimal = Decimal("0")
    
    # Financing
    primary_loan: Optional[Loan] = None
    secondary_loan: Optional[Loan] = None
    
    # Income and expenses
    monthly_income: MonthlyIncome = Field(default_factory=MonthlyIncome)
    monthly_expenses: MonthlyExpenses = Field(default_factory=MonthlyExpenses)
    
    # Partnership
    partners: List[Partner] = Field(default_factory=list)
    
    @validator("purchase_date")
    def validate_purchase_date(cls, v: str) -> str:
        """
        Validate purchase date.
        
        Args:
            v: The purchase date to validate
            
        Returns:
            The validated purchase date
            
        Raises:
            ValueError: If the purchase date is invalid
        """
        if not validate_date(v):
            raise ValueError("Invalid purchase date format (should be YYYY-MM-DD)")
        return v
    
    @validator("partners")
    def validate_partners(cls, v: List[Partner]) -> List[Partner]:
        """
        Validate partners.
        
        Args:
            v: The partners to validate
            
        Returns:
            The validated partners
            
        Raises:
            ValueError: If the partners are invalid
        """
        # Ensure total equity is 100%
        total_equity = sum(partner.equity_share for partner in v)
        if total_equity != Decimal("100"):
            raise ValueError(f"Total equity must be 100% (currently {total_equity}%)")
        
        # Ensure at most one property manager
        property_managers = [p for p in v if p.is_property_manager]
        if len(property_managers) > 1:
            raise ValueError("Only one partner can be the property manager")
        
        return v
    
    def calculate_cash_flow(self) -> Decimal:
        """
        Calculate the monthly cash flow.
        
        Returns:
            The monthly cash flow
        """
        return self.monthly_income.total() - self.monthly_expenses.total()
    
    def calculate_cap_rate(self) -> Decimal:
        """
        Calculate the capitalization rate.
        
        Returns:
            The capitalization rate as a percentage
        """
        annual_noi = (self.monthly_income.total() - self.monthly_expenses.total()) * 12
        
        if self.purchase_price == 0:
            return Decimal("0")
        
        return (annual_noi / self.purchase_price) * 100
    
    def calculate_cash_on_cash_return(self) -> Decimal:
        """
        Calculate the cash-on-cash return.
        
        Returns:
            The cash-on-cash return as a percentage
        """
        annual_cash_flow = self.calculate_cash_flow() * 12
        total_investment = (
            self.down_payment +
            self.closing_costs +
            self.renovation_costs +
            self.marketing_costs +
            self.holding_costs
        )
        
        if total_investment == 0:
            return Decimal("0")
        
        return (annual_cash_flow / total_investment) * 100
    
    def get_property_manager(self) -> Optional[Partner]:
        """
        Get the property manager.
        
        Returns:
            The property manager, or None if there isn't one
        """
        property_managers = [p for p in self.partners if p.is_property_manager]
        return property_managers[0] if property_managers else None
