"""
Analysis model module for the REI-Tracker application.

This module provides the Analysis model for property investment analysis.
"""

from typing import List, Dict, Any, Optional, Union
from decimal import Decimal
from pydantic import Field, validator

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


class Analysis(BaseModel):
    """
    Analysis model for property investment analysis.
    
    This class represents a property investment analysis in the system,
    including property details, financial information, and calculations.
    """
    
    # User association
    user_id: str
    
    # Analysis metadata
    analysis_type: str  # "LTR", "BRRRR", "LeaseOption", "MultiFamily", "PadSplit"
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
    
    refinance_loan_name: Optional[str] = None
    refinance_loan_amount: Optional[int] = None
    refinance_loan_interest_rate: Optional[float] = None
    refinance_loan_term: Optional[int] = None
    refinance_loan_down_payment: Optional[int] = None
    refinance_loan_closing_costs: Optional[int] = None
    
    loan1_loan_name: Optional[str] = None
    loan1_loan_amount: Optional[int] = None
    loan1_loan_interest_rate: Optional[float] = None
    loan1_loan_term: Optional[int] = None
    loan1_loan_down_payment: Optional[int] = None
    loan1_loan_closing_costs: Optional[int] = None
    
    loan2_loan_name: Optional[str] = None
    loan2_loan_amount: Optional[int] = None
    loan2_loan_interest_rate: Optional[float] = None
    loan2_loan_term: Optional[int] = None
    loan2_loan_down_payment: Optional[int] = None
    loan2_loan_closing_costs: Optional[int] = None
    
    loan3_loan_name: Optional[str] = None
    loan3_loan_amount: Optional[int] = None
    loan3_loan_interest_rate: Optional[float] = None
    loan3_loan_term: Optional[int] = None
    loan3_loan_down_payment: Optional[int] = None
    loan3_loan_closing_costs: Optional[int] = None
    
    # Comps integration data
    comps_data: Optional[CompsData] = None
    
    @validator("analysis_type")
    def validate_analysis_type(cls, v: str) -> str:
        """
        Validate analysis type.
        
        Args:
            v: The analysis type to validate
            
        Returns:
            The validated analysis type
            
        Raises:
            ValueError: If the analysis type is invalid
        """
        valid_types = ["LTR", "BRRRR", "LeaseOption", "MultiFamily", "PadSplit"]
        if v not in valid_types:
            raise ValueError(f"Analysis type must be one of: {', '.join(valid_types)}")
        return v
    
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
            loan_closing_costs=Decimal(str(self.initial_loan_closing_costs or 0))
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
            loan_closing_costs=Decimal(str(self.refinance_loan_closing_costs or 0))
        )
    
    def calculate_monthly_payment(self, loan: LoanDetails) -> Decimal:
        """
        Calculate the monthly payment for a loan.
        
        Args:
            loan: The loan details
            
        Returns:
            The monthly payment
        """
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
        if self.management_fee_percentage and self.monthly_rent:
            expenses += Decimal(str(self.monthly_rent)) * Decimal(str(self.management_fee_percentage)) / Decimal("100")
        
        # CapEx
        if self.capex_percentage and self.monthly_rent:
            expenses += Decimal(str(self.monthly_rent)) * Decimal(str(self.capex_percentage)) / Decimal("100")
        
        # Vacancy
        if self.vacancy_percentage and self.monthly_rent:
            expenses += Decimal(str(self.monthly_rent)) * Decimal(str(self.vacancy_percentage)) / Decimal("100")
        
        # Repairs
        if self.repairs_percentage and self.monthly_rent:
            expenses += Decimal(str(self.monthly_rent)) * Decimal(str(self.repairs_percentage)) / Decimal("100")
        
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
        if self.padsplit_platform_percentage and self.monthly_rent:
            expenses += Decimal(str(self.monthly_rent)) * Decimal(str(self.padsplit_platform_percentage)) / Decimal("100")
        
        # Loan payments
        initial_loan = self.get_initial_loan()
        if initial_loan:
            expenses += self.calculate_monthly_payment(initial_loan)
        
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
        
        # Avoid division by zero
        if self.purchase_price == 0:
            return Decimal("0")
        
        # Calculate cap rate
        return (annual_noi / Decimal(str(self.purchase_price))) * Decimal("100")
