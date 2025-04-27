"""
Analysis model module for the REI-Tracker application.

This module provides the Analysis model for property investment analysis.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from decimal import Decimal
from pydantic import Field, validator, root_validator

from src.models.base_model import BaseModel
from src.utils.validation_utils import validate_date, validate_decimal, percentage_validator


class LoanDetails(BaseModel):
    """
    Loan details model for property financing analysis.
    
    This class represents the details of a loan used in an analysis.
    """
    
    loan_name: str
    loan_amount: Decimal
    loan_interest_rate: Decimal
    loan_term: int  # In months
    loan_down_payment: Decimal = Decimal("0")
    loan_closing_costs: Decimal = Decimal("0")
    is_interest_only: bool = False
    
    @validator("loan_interest_rate")
    def validate_loan_interest_rate(cls, v: Decimal) -> Decimal:
        """
        Validate loan interest rate.
        
        Args:
            v: The loan interest rate to validate
            
        Returns:
            The validated loan interest rate
            
        Raises:
            ValueError: If the loan interest rate is invalid
        """
        if not validate_decimal(v, 0, 100):
            raise ValueError("Loan interest rate must be between 0 and 100")
        return v
    
    @validator("loan_term")
    def validate_loan_term(cls, v: int) -> int:
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


class CompsData(BaseModel):
    """
    Comps data model for property comparables.
    
    This class represents the comparable properties data used in an analysis.
    """
    
    last_run: str
    run_count: int
    estimated_value: int
    value_range_low: int
    value_range_high: int
    comparables: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator("last_run")
    def validate_last_run(cls, v: str) -> str:
        """
        Validate last run date.
        
        Args:
            v: The last run date to validate
            
        Returns:
            The validated last run date
            
        Raises:
            ValueError: If the last run date is invalid
        """
        if not validate_date(v, format_str="%Y-%m-%dT%H:%M:%S.%fZ"):
            raise ValueError("Invalid last run date format")
        return v
    
    @validator("run_count")
    def validate_run_count(cls, v: int) -> int:
        """
        Validate run count.
        
        Args:
            v: The run count to validate
            
        Returns:
            The validated run count
            
        Raises:
            ValueError: If the run count is invalid
        """
        if v < 0:
            raise ValueError("Run count must be non-negative")
        return v


class UnitType(BaseModel):
    """
    Unit type model for multi-family properties.
    
    This class represents a type of unit in a multi-family property.
    """
    
    name: str
    count: int
    bedrooms: int
    bathrooms: float
    square_footage: int
    rent: int
    
    @validator("count", "bedrooms", "square_footage", "rent")
    def validate_positive_int(cls, v: int, values: Dict[str, Any], field: str) -> int:
        """
        Validate positive integer fields.
        
        Args:
            v: The value to validate
            values: The values being validated
            field: The field being validated
            
        Returns:
            The validated value
            
        Raises:
            ValueError: If the value is invalid
        """
        if v <= 0:
            raise ValueError(f"{field.title()} must be positive")
        return v
    
    @validator("bathrooms")
    def validate_bathrooms(cls, v: float) -> float:
        """
        Validate bathrooms.
        
        Args:
            v: The bathrooms value to validate
            
        Returns:
            The validated bathrooms value
            
        Raises:
            ValueError: If the bathrooms value is invalid
        """
        if v <= 0:
            raise ValueError("Bathrooms must be positive")
        return v


class Analysis(BaseModel):
    """
    Analysis model for property investment analysis.
    
    This class represents a property investment analysis in the system,
    including property details, financial information, and calculations.
    """
    
    # User association
    user_id: str
    
    # Analysis metadata
    analysis_type: Literal["LTR", "BRRRR", "LeaseOption", "MultiFamily", "PadSplit"]
    analysis_name: str
    
    # Property details
    address: str
    square_footage: Optional[int] = None
    lot_size: Optional[int] = None
    year_built: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    
    # Financial details
    purchase_price: int
    after_repair_value: Optional[int] = None
    renovation_costs: Optional[int] = None
    renovation_duration: Optional[int] = None  # In months
    furnishing_costs: Optional[int] = None
    cash_to_seller: Optional[int] = None
    closing_costs: Optional[int] = None
    assignment_fee: Optional[int] = None
    marketing_costs: Optional[int] = None
    
    # Income details
    monthly_rent: Optional[int] = None
    
    # Expense details
    property_taxes: Optional[int] = None
    insurance: Optional[int] = None
    hoa_coa_coop: Optional[int] = None
    management_fee_percentage: Optional[float] = None
    capex_percentage: Optional[float] = None
    vacancy_percentage: Optional[float] = None
    repairs_percentage: Optional[float] = None
    utilities: Optional[int] = None
    internet: Optional[int] = None
    cleaning: Optional[int] = None
    pest_control: Optional[int] = None
    landscaping: Optional[int] = None
    padsplit_platform_percentage: Optional[float] = None
    
    # Loan details
    initial_loan_name: Optional[str] = None
    initial_loan_amount: Optional[int] = None
    initial_loan_interest_rate: Optional[float] = None
    initial_loan_term: Optional[int] = None
    initial_loan_down_payment: Optional[int] = None
    initial_loan_closing_costs: Optional[int] = None
    initial_loan_is_interest_only: Optional[bool] = False
    
    refinance_loan_name: Optional[str] = None
    refinance_loan_amount: Optional[int] = None
    refinance_loan_interest_rate: Optional[float] = None
    refinance_loan_term: Optional[int] = None
    refinance_loan_down_payment: Optional[int] = None
    refinance_loan_closing_costs: Optional[int] = None
    refinance_loan_is_interest_only: Optional[bool] = False
    
    loan1_loan_name: Optional[str] = None
    loan1_loan_amount: Optional[int] = None
    loan1_loan_interest_rate: Optional[float] = None
    loan1_loan_term: Optional[int] = None
    loan1_loan_down_payment: Optional[int] = None
    loan1_loan_closing_costs: Optional[int] = None
    loan1_loan_is_interest_only: Optional[bool] = False
    
    loan2_loan_name: Optional[str] = None
    loan2_loan_amount: Optional[int] = None
    loan2_loan_interest_rate: Optional[float] = None
    loan2_loan_term: Optional[int] = None
    loan2_loan_down_payment: Optional[int] = None
    loan2_loan_closing_costs: Optional[int] = None
    loan2_loan_is_interest_only: Optional[bool] = False
    
    loan3_loan_name: Optional[str] = None
    loan3_loan_amount: Optional[int] = None
    loan3_loan_interest_rate: Optional[float] = None
    loan3_loan_term: Optional[int] = None
    loan3_loan_down_payment: Optional[int] = None
    loan3_loan_closing_costs: Optional[int] = None
    loan3_loan_is_interest_only: Optional[bool] = False
    
    # Balloon payment details
    has_balloon_payment: Optional[bool] = False
    balloon_due_date: Optional[str] = None
    balloon_refinance_ltv_percentage: Optional[float] = None
    balloon_refinance_loan_amount: Optional[int] = None
    balloon_refinance_loan_interest_rate: Optional[float] = None
    balloon_refinance_loan_term: Optional[int] = None
    balloon_refinance_loan_down_payment: Optional[int] = None
    balloon_refinance_loan_closing_costs: Optional[int] = None
    
    # Lease Option specific fields
    option_consideration_fee: Optional[int] = None
    option_term_months: Optional[int] = None
    strike_price: Optional[int] = None
    monthly_rent_credit_percentage: Optional[float] = None
    rent_credit_cap: Optional[int] = None
    
    # Multi-Family specific fields
    total_units: Optional[int] = None
    occupied_units: Optional[int] = None
    floors: Optional[int] = None
    unit_types: Optional[List[UnitType]] = None
    
    # PadSplit specific fields
    room_count: Optional[int] = None
    average_room_rent: Optional[int] = None
    
    # Comps integration data
    comps_data: Optional[CompsData] = None
    
    # Validation for analysis type-specific fields
    @root_validator
    def validate_analysis_type_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields based on analysis type.
        
        Args:
            values: The values being validated
            
        Returns:
            The validated values
            
        Raises:
            ValueError: If the values are invalid for the analysis type
        """
        analysis_type = values.get("analysis_type")
        
        if analysis_type == "BRRRR":
            # BRRRR requires after_repair_value, renovation_costs, and renovation_duration
            if not values.get("after_repair_value"):
                raise ValueError("After repair value is required for BRRRR analysis")
            if not values.get("renovation_costs"):
                raise ValueError("Renovation costs are required for BRRRR analysis")
            if not values.get("renovation_duration"):
                raise ValueError("Renovation duration is required for BRRRR analysis")
        
        elif analysis_type == "LeaseOption":
            # LeaseOption requires option_consideration_fee, option_term_months, and strike_price
            if not values.get("option_consideration_fee"):
                raise ValueError("Option consideration fee is required for Lease Option analysis")
            if not values.get("option_term_months"):
                raise ValueError("Option term months are required for Lease Option analysis")
            if not values.get("strike_price"):
                raise ValueError("Strike price is required for Lease Option analysis")
            
            # Validate strike price is greater than purchase price
            if values.get("strike_price") and values.get("purchase_price"):
                if values.get("strike_price") <= values.get("purchase_price"):
                    raise ValueError("Strike price must be greater than purchase price")
        
        elif analysis_type == "MultiFamily":
            # MultiFamily requires total_units and occupied_units
            if not values.get("total_units"):
                raise ValueError("Total units are required for Multi-Family analysis")
            if not values.get("occupied_units"):
                raise ValueError("Occupied units are required for Multi-Family analysis")
            
            # Validate occupied_units <= total_units
            if values.get("occupied_units") and values.get("total_units"):
                if values.get("occupied_units") > values.get("total_units"):
                    raise ValueError("Occupied units cannot exceed total units")
        
        elif analysis_type == "PadSplit":
            # PadSplit requires furnishing_costs and padsplit_platform_percentage
            if not values.get("furnishing_costs"):
                raise ValueError("Furnishing costs are required for PadSplit analysis")
            if not values.get("padsplit_platform_percentage"):
                raise ValueError("PadSplit platform percentage is required for PadSplit analysis")
        
        return values
    
    def get_initial_loan(self) -> Optional[LoanDetails]:
        """
        Get the initial loan details.
        
        Returns:
            The initial loan details, or None if not specified
        """
        if self.initial_loan_amount is None:
            return None
        
        return LoanDetails(
            loan_name=self.initial_loan_name or "Initial Loan",
            loan_amount=Decimal(str(self.initial_loan_amount)),
            loan_interest_rate=Decimal(str(self.initial_loan_interest_rate or 0)),
            loan_term=self.initial_loan_term or 360,
            loan_down_payment=Decimal(str(self.initial_loan_down_payment or 0)),
            loan_closing_costs=Decimal(str(self.initial_loan_closing_costs or 0)),
            is_interest_only=self.initial_loan_is_interest_only or False
        )
    
    def get_refinance_loan(self) -> Optional[LoanDetails]:
        """
        Get the refinance loan details.
        
        Returns:
            The refinance loan details, or None if not specified
        """
        if self.refinance_loan_amount is None:
            return None
        
        return LoanDetails(
            loan_name=self.refinance_loan_name or "Refinance Loan",
            loan_amount=Decimal(str(self.refinance_loan_amount)),
            loan_interest_rate=Decimal(str(self.refinance_loan_interest_rate or 0)),
            loan_term=self.refinance_loan_term or 360,
            loan_down_payment=Decimal(str(self.refinance_loan_down_payment or 0)),
            loan_closing_costs=Decimal(str(self.refinance_loan_closing_costs or 0)),
            is_interest_only=self.refinance_loan_is_interest_only or False
        )
    
    def get_balloon_loan(self) -> Optional[LoanDetails]:
        """
        Get the balloon loan details.
        
        Returns:
            The balloon loan details, or None if not specified
        """
        if not self.has_balloon_payment or self.balloon_refinance_loan_amount is None:
            return None
        
        return LoanDetails(
            loan_name="Balloon Refinance Loan",
            loan_amount=Decimal(str(self.balloon_refinance_loan_amount)),
            loan_interest_rate=Decimal(str(self.balloon_refinance_loan_interest_rate or 0)),
            loan_term=self.balloon_refinance_loan_term or 360,
            loan_down_payment=Decimal(str(self.balloon_refinance_loan_down_payment or 0)),
            loan_closing_costs=Decimal(str(self.balloon_refinance_loan_closing_costs or 0)),
            is_interest_only=False
        )
    
    def calculate_monthly_payment(self, loan: LoanDetails) -> Decimal:
        """
        Calculate the monthly payment for a loan.
        
        Args:
            loan: The loan details
            
        Returns:
            The monthly payment
        """
        # If interest-only loan, just calculate interest
        if loan.is_interest_only:
            return loan.loan_amount * (loan.loan_interest_rate / Decimal("12") / Decimal("100"))
        
        # Convert annual interest rate to monthly
        monthly_rate = loan.loan_interest_rate / Decimal("12") / Decimal("100")
        
        # If interest rate is 0, simple division
        if monthly_rate == 0:
            return loan.loan_amount / Decimal(str(loan.loan_term))
        
        # Standard amortization formula
        factor = (monthly_rate * (1 + monthly_rate) ** loan.loan_term) / ((1 + monthly_rate) ** loan.loan_term - 1)
        return loan.loan_amount * factor
    
    def calculate_monthly_cash_flow(self) -> Decimal:
        """
        Calculate the monthly cash flow.
        
        Returns:
            The monthly cash flow
        """
        # Income
        income = Decimal(str(self.monthly_rent or 0))
        
        # For Multi-Family, calculate income based on unit types if available
        if self.analysis_type == "MultiFamily" and self.unit_types:
            income = Decimal("0")
            for unit_type in self.unit_types:
                income += Decimal(str(unit_type.rent)) * Decimal(str(unit_type.count))
        
        # For PadSplit, calculate income based on room count and average rent
        if self.analysis_type == "PadSplit" and self.room_count and self.average_room_rent:
            income = Decimal(str(self.room_count)) * Decimal(str(self.average_room_rent))
        
        # Expenses
        expenses = Decimal("0")
        
        # Property taxes
        if self.property_taxes:
            expenses += Decimal(str(self.property_taxes)) / Decimal("12")
        
        # Insurance
        if self.insurance:
            expenses += Decimal(str(self.insurance)) / Decimal("12")
        
        # HOA/COA/Co-op fees
        if self.hoa_coa_coop:
            expenses += Decimal(str(self.hoa_coa_coop))
        
        # Management fee
        if self.management_fee_percentage:
            expenses += income * Decimal(str(self.management_fee_percentage)) / Decimal("100")
        
        # CapEx
        if self.capex_percentage:
            expenses += income * Decimal(str(self.capex_percentage)) / Decimal("100")
        
        # Vacancy
        if self.vacancy_percentage:
            expenses += income * Decimal(str(self.vacancy_percentage)) / Decimal("100")
        
        # Repairs
        if self.repairs_percentage:
            expenses += income * Decimal(str(self.repairs_percentage)) / Decimal("100")
        
        # Utilities
        if self.utilities:
            expenses += Decimal(str(self.utilities))
        
        # Internet
        if self.internet:
            expenses += Decimal(str(self.internet))
        
        # Cleaning
        if self.cleaning:
            expenses += Decimal(str(self.cleaning))
        
        # Pest control
        if self.pest_control:
            expenses += Decimal(str(self.pest_control))
        
        # Landscaping
        if self.landscaping:
            expenses += Decimal(str(self.landscaping))
        
        # PadSplit platform fee
        if self.analysis_type == "PadSplit" and self.padsplit_platform_percentage:
            expenses += income * Decimal(str(self.padsplit_platform_percentage)) / Decimal("100")
        
        # Loan payments
        initial_loan = self.get_initial_loan()
        if initial_loan:
            expenses += self.calculate_monthly_payment(initial_loan)
        
        # Refinance loan payments (for BRRRR)
        if self.analysis_type == "BRRRR":
            refinance_loan = self.get_refinance_loan()
            if refinance_loan:
                expenses += self.calculate_monthly_payment(refinance_loan)
        
        # Additional loan payments
        for i in range(1, 4):
            loan_prefix = f"loan{i}_loan"
            loan_amount = getattr(self, f"{loan_prefix}_amount", None)
            if loan_amount:
                loan = LoanDetails(
                    loan_name=getattr(self, f"{loan_prefix}_name", f"Loan {i}") or f"Loan {i}",
                    loan_amount=Decimal(str(loan_amount)),
                    loan_interest_rate=Decimal(str(getattr(self, f"{loan_prefix}_interest_rate", 0) or 0)),
                    loan_term=getattr(self, f"{loan_prefix}_term", 360) or 360,
                    loan_down_payment=Decimal(str(getattr(self, f"{loan_prefix}_down_payment", 0) or 0)),
                    loan_closing_costs=Decimal(str(getattr(self, f"{loan_prefix}_closing_costs", 0) or 0)),
                    is_interest_only=getattr(self, f"{loan_prefix}_is_interest_only", False) or False
                )
                expenses += self.calculate_monthly_payment(loan)
        
        # Balloon loan payments
        if self.has_balloon_payment and self.balloon_refinance_loan_amount:
            balloon_loan = self.get_balloon_loan()
            if balloon_loan:
                expenses += self.calculate_monthly_payment(balloon_loan)
        
        # Cash flow
        return income - expenses
    
    def calculate_cash_on_cash_return(self) -> Decimal:
        """
        Calculate the cash-on-cash return.
        
        Returns:
            The cash-on-cash return as a percentage
        """
        # Annual cash flow
        annual_cash_flow = self.calculate_monthly_cash_flow() * Decimal("12")
        
        # Total investment
        total_investment = Decimal("0")
        
        # Down payment
        initial_loan = self.get_initial_loan()
        if initial_loan:
            total_investment += initial_loan.loan_down_payment
        
        # Closing costs
        if self.closing_costs:
            total_investment += Decimal(str(self.closing_costs))
        
        # Renovation costs
        if self.renovation_costs:
            total_investment += Decimal(str(self.renovation_costs))
        
        # Furnishing costs
        if self.furnishing_costs:
            total_investment += Decimal(str(self.furnishing_costs))
        
        # Marketing costs
        if self.marketing_costs:
            total_investment += Decimal(str(self.marketing_costs))
        
        # Cash to seller
        if self.cash_to_seller:
            total_investment += Decimal(str(self.cash_to_seller))
        
        # Assignment fee
        if self.assignment_fee:
            total_investment += Decimal(str(self.assignment_fee))
        
        # Lease Option specific: option consideration fee
        if self.analysis_type == "LeaseOption" and self.option_consideration_fee:
            total_investment += Decimal(str(self.option_consideration_fee))
        
        # Avoid division by zero
        if total_investment == 0:
            return Decimal("0")
        
        # Calculate cash-on-cash return
        return (annual_cash_flow / total_investment) * Decimal("100")
    
    def calculate_cap_rate(self) -> Decimal:
        """
        Calculate the capitalization rate.
        
        Returns:
            The capitalization rate as a percentage
        """
        # Annual net operating income
        annual_noi = self.calculate_monthly_cash_flow() * Decimal("12")
        
        # Add back loan payments
        initial_loan = self.get_initial_loan()
        if initial_loan:
            annual_noi += self.calculate_monthly_payment(initial_loan) * Decimal("12")
        
        # Add back refinance loan payments (for BRRRR)
        if self.analysis_type == "BRRRR":
            refinance_loan = self.get_refinance_loan()
            if refinance_loan:
                annual_noi += self.calculate_monthly_payment(refinance_loan) * Decimal("12")
        
        # Add back additional loan payments
        for i in range(1, 4):
            loan_prefix = f"loan{i}_loan"
            loan_amount = getattr(self, f"{loan_prefix}_amount", None)
            if loan_amount:
                loan = LoanDetails(
                    loan_name=getattr(self, f"{loan_prefix}_name", f"Loan {i}") or f"Loan {i}",
                    loan_amount=Decimal(str(loan_amount)),
                    loan_interest_rate=Decimal(str(getattr(self, f"{loan_prefix}_interest_rate", 0) or 0)),
                    loan_term=getattr(self, f"{loan_prefix}_term", 360) or 360,
                    loan_down_payment=Decimal(str(getattr(self, f"{loan_prefix}_down_payment", 0) or 0)),
                    loan_closing_costs=Decimal(str(getattr(self, f"{loan_prefix}_closing_costs", 0) or 0)),
                    is_interest_only=getattr(self, f"{loan_prefix}_is_interest_only", False) or False
                )
                annual_noi += self.calculate_monthly_payment(loan) * Decimal("12")
        
        # Add back balloon loan payments
        if self.has_balloon_payment and self.balloon_refinance_loan_amount:
            balloon_loan = self.get_balloon_loan()
            if balloon_loan:
                annual_noi += self.calculate_monthly_payment(balloon_loan) * Decimal("12")
        
        # Avoid division by zero
        if self.purchase_price == 0:
            return Decimal("0")
        
        # Calculate cap rate
        return (annual_noi / Decimal(str(self.purchase_price))) * Decimal("100")
    
    def calculate_price_per_unit(self) -> Optional[Decimal]:
        """
        Calculate the price per unit for multi-family properties.
        
        Returns:
            The price per unit, or None if not applicable
        """
        if self.analysis_type != "MultiFamily" or not self.total_units or self.total_units == 0:
            return None
        
        return Decimal(str(self.purchase_price)) / Decimal(str(self.total_units))
    
    def calculate_effective_purchase_price(self) -> Optional[Decimal]:
        """
        Calculate the effective purchase price for lease option properties.
        
        Returns:
            The effective purchase price, or None if not applicable
        """
        if self.analysis_type != "LeaseOption" or not self.strike_price:
            return None
        
        effective_price = Decimal(str(self.strike_price))
        
        # Subtract option consideration fee
        if self.option_consideration_fee:
            effective_price -= Decimal(str(self.option_consideration_fee))
        
        # Subtract rent credits
        if self.monthly_rent and self.monthly_rent_credit_percentage and self.option_term_months:
            monthly_credit = Decimal(str(self.monthly_rent)) * Decimal(str(self.monthly_rent_credit_percentage)) / Decimal("100")
            total_credits = monthly_credit * Decimal(str(self.option_term_months))
            
            # Apply rent credit cap if specified
            if self.rent_credit_cap and total_credits > Decimal(str(self.rent_credit_cap)):
                total_credits = Decimal(str(self.rent_credit_cap))
            
            effective_price -= total_credits
        
        return max(Decimal("0"), effective_price)
