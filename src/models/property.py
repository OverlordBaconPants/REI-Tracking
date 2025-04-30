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
    visibility_settings: Dict[str, bool] = Field(default_factory=lambda: {
        "financial_details": True,
        "transaction_history": True,
        "partner_contributions": True,
        "property_documents": True
    })
    
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
    
    @validator("visibility_settings")
    def validate_visibility_settings(cls, v: Dict[str, bool]) -> Dict[str, bool]:
        """
        Validate visibility settings.
        
        Args:
            v: The visibility settings to validate
            
        Returns:
            The validated visibility settings
            
        Raises:
            ValueError: If the visibility settings are invalid
        """
        required_settings = [
            "financial_details",
            "transaction_history",
            "partner_contributions",
            "property_documents"
        ]
        
        for setting in required_settings:
            if setting not in v:
                v[setting] = True
        
        return v


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
    
    # Income and expenses - flat structure as per documentation
    monthly_income: Dict[str, Any] = Field(default_factory=lambda: {
        "rental_income": Decimal("0"),
        "parking_income": Decimal("0"),
        "laundry_income": Decimal("0"),
        "other_income": Decimal("0"),
        "income_notes": ""
    })
    
    monthly_expenses: Dict[str, Any] = Field(default_factory=lambda: {
        "property_taxes": Decimal("0"),
        "insurance": Decimal("0"),
        "repairs": Decimal("0"),
        "capex": Decimal("0"),
        "property_management": Decimal("0"),
        "hoa_fees": Decimal("0"),
        "utilities": {
            "water": Decimal("0"),
            "electricity": Decimal("0"),
            "gas": Decimal("0"),
            "trash": Decimal("0")
        },
        "other_expenses": Decimal("0"),
        "expense_notes": ""
    })
    
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
    
    @validator("monthly_income")
    def validate_monthly_income(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate monthly income.
        
        Args:
            v: The monthly income to validate
            
        Returns:
            The validated monthly income
            
        Raises:
            ValueError: If the monthly income is invalid
        """
        required_fields = ["rental_income", "parking_income", "laundry_income", "other_income"]
        
        # Ensure all required fields exist
        for field in required_fields:
            if field not in v:
                v[field] = Decimal("0")
            elif not isinstance(v[field], Decimal):
                try:
                    v[field] = Decimal(str(v[field]))
                except:
                    v[field] = Decimal("0")
            
            # Validate decimal fields
            if not validate_decimal(v[field], 0):
                raise ValueError(f"{field} must be a positive decimal")
        
        # Ensure income_notes exists
        if "income_notes" not in v:
            v["income_notes"] = ""
        
        return v
    
    @validator("monthly_expenses")
    def validate_monthly_expenses(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate monthly expenses.
        
        Args:
            v: The monthly expenses to validate
            
        Returns:
            The validated monthly expenses
            
        Raises:
            ValueError: If the monthly expenses are invalid
        """
        required_fields = ["property_taxes", "insurance", "repairs", "capex",
                          "property_management", "hoa_fees", "other_expenses"]
        
        # Ensure all required fields exist
        for field in required_fields:
            if field not in v:
                v[field] = Decimal("0")
            elif not isinstance(v[field], Decimal):
                try:
                    v[field] = Decimal(str(v[field]))
                except:
                    v[field] = Decimal("0")
            
            # Validate decimal fields
            if not validate_decimal(v[field], 0):
                raise ValueError(f"{field} must be a positive decimal")
        
        # Ensure utilities exists and is properly structured
        if "utilities" not in v:
            v["utilities"] = {
                "water": Decimal("0"),
                "electricity": Decimal("0"),
                "gas": Decimal("0"),
                "trash": Decimal("0")
            }
        else:
            utility_fields = ["water", "electricity", "gas", "trash"]
            for field in utility_fields:
                if field not in v["utilities"]:
                    v["utilities"][field] = Decimal("0")
                elif not isinstance(v["utilities"][field], Decimal):
                    try:
                        v["utilities"][field] = Decimal(str(v["utilities"][field]))
                    except:
                        v["utilities"][field] = Decimal("0")
                
                # Validate decimal fields
                if not validate_decimal(v["utilities"][field], 0):
                    raise ValueError(f"utilities.{field} must be a positive decimal")
        
        # Ensure expense_notes exists
        if "expense_notes" not in v:
            v["expense_notes"] = ""
        
        return v
    
    def calculate_cash_flow(self) -> Decimal:
        """
        Calculate the monthly cash flow.
        
        Returns:
            The monthly cash flow
        """
        return self.calculate_total_income() - self.calculate_total_expenses()
    
    def calculate_total_income(self) -> Decimal:
        """
        Calculate the total monthly income.
        
        Returns:
            The total monthly income
        """
        return (
            self.monthly_income["rental_income"] +
            self.monthly_income["parking_income"] +
            self.monthly_income["laundry_income"] +
            self.monthly_income["other_income"]
        )
    
    def calculate_total_expenses(self) -> Decimal:
        """
        Calculate the total monthly expenses.
        
        Returns:
            The total monthly expenses
        """
        utilities_total = (
            self.monthly_expenses["utilities"]["water"] +
            self.monthly_expenses["utilities"]["electricity"] +
            self.monthly_expenses["utilities"]["gas"] +
            self.monthly_expenses["utilities"]["trash"]
        )
        
        return (
            self.monthly_expenses["property_taxes"] +
            self.monthly_expenses["insurance"] +
            self.monthly_expenses["repairs"] +
            self.monthly_expenses["capex"] +
            self.monthly_expenses["property_management"] +
            self.monthly_expenses["hoa_fees"] +
            utilities_total +
            self.monthly_expenses["other_expenses"]
        )
    
    def calculate_cap_rate(self) -> Decimal:
        """
        Calculate the capitalization rate.
        
        Returns:
            The capitalization rate as a percentage
        """
        from src.utils.financial_helpers import calculate_cap_rate
        from src.utils.money import Money
        
        annual_noi = (self.calculate_total_income() - self.calculate_total_expenses()) * 12
        
        if self.purchase_price == 0:
            return Decimal("0")
        
        # Use the centralized utility function
        result = calculate_cap_rate(Money(annual_noi), Money(self.purchase_price))
        return Decimal(str(result.value))
    
    def calculate_cash_on_cash_return(self) -> Decimal:
        """
        Calculate the cash-on-cash return.
        
        Returns:
            The cash-on-cash return as a percentage
        """
        from src.utils.financial_helpers import calculate_cash_on_cash_return
        from src.utils.money import Money
        
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
        
        # Use the centralized utility function
        result = calculate_cash_on_cash_return(Money(annual_cash_flow), Money(total_investment))
        return Decimal(str(result.value))
    
    def get_property_manager(self) -> Optional[Partner]:
        """
        Get the property manager.
        
        Returns:
            The property manager, or None if there isn't one
        """
        property_managers = [p for p in self.partners if p.is_property_manager]
        return property_managers[0] if property_managers else None
