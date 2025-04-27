"""
Analysis calculation module for the REI-Tracker application.

This module provides classes for different types of property investment analyses,
including base functionality and specialized analysis types.
"""

from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
import logging
from dataclasses import dataclass, field

from src.utils.money import Money, Percentage, MonthlyPayment
from src.utils.calculations.validation import ValidationResult, Validator, safe_calculation
from src.utils.calculations.loan_details import LoanDetails
from src.utils.calculations.investment_metrics import InvestmentMetricsCalculator, EquityProjection, YearlyProjection

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """
    Result of an analysis calculation.
    
    This class represents the calculated results of a property investment analysis,
    including cash flow, returns, and other metrics.
    
    Attributes:
        monthly_cash_flow: Monthly cash flow amount
        annual_cash_flow: Annual cash flow amount
        cash_on_cash_return: Cash-on-cash return as a percentage
        cap_rate: Capitalization rate as a percentage
        roi: Return on investment as a percentage
        total_investment: Total investment amount
        monthly_income: Monthly income amount
        monthly_expenses: Monthly expenses amount
        debt_service_coverage_ratio: DSCR value
        expense_ratio: Expense ratio as a percentage
        gross_rent_multiplier: GRM value
        price_per_unit: Price per unit (for multi-family)
        breakeven_occupancy: Breakeven occupancy rate as a percentage
        mao: Maximum Allowable Offer amount
        equity_projection: Equity projection over time
        yearly_projections: Year-by-year equity projections
    """
    monthly_cash_flow: Money = field(default_factory=lambda: Money(0))
    annual_cash_flow: Money = field(default_factory=lambda: Money(0))
    cash_on_cash_return: Percentage = field(default_factory=lambda: Percentage(0))
    cap_rate: Percentage = field(default_factory=lambda: Percentage(0))
    roi: Percentage = field(default_factory=lambda: Percentage(0))
    total_investment: Money = field(default_factory=lambda: Money(0))
    monthly_income: Money = field(default_factory=lambda: Money(0))
    monthly_expenses: Money = field(default_factory=lambda: Money(0))
    debt_service_coverage_ratio: float = 0.0
    expense_ratio: Percentage = field(default_factory=lambda: Percentage(0))
    gross_rent_multiplier: float = 0.0
    price_per_unit: Money = field(default_factory=lambda: Money(0))
    breakeven_occupancy: Percentage = field(default_factory=lambda: Percentage(0))
    mao: Money = field(default_factory=lambda: Money(0))
    equity_projection: Optional[EquityProjection] = None
    yearly_projections: List[YearlyProjection] = field(default_factory=list)
    
    def __str__(self) -> str:
        """Format analysis results as a string."""
        result = (
            f"Monthly Cash Flow: {self.monthly_cash_flow}\n"
            f"Annual Cash Flow: {self.annual_cash_flow}\n"
            f"Cash-on-Cash Return: {self.cash_on_cash_return}\n"
            f"Cap Rate: {self.cap_rate}\n"
            f"ROI: {self.roi}\n"
            f"Total Investment: {self.total_investment}\n"
            f"Monthly Income: {self.monthly_income}\n"
            f"Monthly Expenses: {self.monthly_expenses}\n"
            f"DSCR: {self.debt_service_coverage_ratio:.2f}\n"
            f"Expense Ratio: {self.expense_ratio}\n"
            f"Gross Rent Multiplier: {self.gross_rent_multiplier:.2f}\n"
            f"Price Per Unit: {self.price_per_unit}\n"
            f"Breakeven Occupancy: {self.breakeven_occupancy}\n"
            f"Maximum Allowable Offer: {self.mao}"
        )
        
        if self.equity_projection:
            result += f"\n\nEquity Projection (over {self.equity_projection.projection_years} years):\n"
            result += f"  Initial Equity: {self.equity_projection.initial_equity}\n"
            result += f"  Final Property Value: {self.equity_projection.property_value}\n"
            result += f"  Final Equity: {self.equity_projection.current_equity}\n"
            result += f"  Equity from Appreciation: {self.equity_projection.equity_from_appreciation}\n"
            result += f"  Equity from Principal Paydown: {self.equity_projection.equity_from_principal}\n"
            result += f"  Total Equity Gain: {self.equity_projection.total_equity_gain}"
        
        return result

class BaseAnalysis:
    """
    Base class for property investment analyses.
    
    This class provides common functionality for all analysis types,
    including validation and basic calculations.
    
    Attributes:
        data: Dictionary containing analysis data
    """
    
    def __init__(self, data: Dict[str, Any]):
        """
        Initialize the analysis with data.
        
        Args:
            data: Dictionary containing analysis data
        """
        self.data = data
        self.validation_result = ValidationResult()
    
    def validate(self) -> ValidationResult:
        """
        Validate the analysis data.
        
        Returns:
            ValidationResult object containing validation errors
        """
        # Reset validation result
        self.validation_result = ValidationResult()
        
        # Validate required fields
        self._validate_required_fields()
        
        # Validate numeric fields
        self._validate_numeric_fields()
        
        # Validate percentage fields
        self._validate_percentage_fields()
        
        return self.validation_result
    
    def _validate_required_fields(self) -> None:
        """Validate required fields for the analysis."""
        # Common required fields for all analysis types
        required_fields = [
            ('analysis_name', 'Analysis Name'),
            ('address', 'Property Address'),
            ('purchase_price', 'Purchase Price'),
            ('monthly_rent', 'Monthly Rent')
        ]
        
        for field_name, display_name in required_fields:
            Validator.validate_required(
                self.validation_result,
                self.data,
                field_name,
                display_name
            )
    
    def _validate_numeric_fields(self) -> None:
        """Validate numeric fields for the analysis."""
        # Common numeric fields for all analysis types
        numeric_fields = [
            ('purchase_price', 'Purchase Price'),
            ('monthly_rent', 'Monthly Rent'),
            ('property_taxes', 'Property Taxes'),
            ('insurance', 'Insurance'),
            ('closing_costs', 'Closing Costs')
        ]
        
        for field_name, display_name in numeric_fields:
            if field_name in self.data and self.data[field_name] is not None:
                Validator.validate_positive_number(
                    self.validation_result,
                    self.data[field_name],
                    field_name,
                    display_name,
                    allow_zero=True
                )
    
    def _validate_percentage_fields(self) -> None:
        """Validate percentage fields for the analysis."""
        # Common percentage fields for all analysis types
        percentage_fields = [
            ('management_fee_percentage', 'Management Fee Percentage'),
            ('capex_percentage', 'CapEx Percentage'),
            ('vacancy_percentage', 'Vacancy Percentage'),
            ('repairs_percentage', 'Repairs Percentage')
        ]
        
        for field_name, display_name in percentage_fields:
            if field_name in self.data and self.data[field_name] is not None:
                Validator.validate_percentage(
                    self.validation_result,
                    self.data[field_name],
                    field_name,
                    display_name
                )
    
    def get_loan_details(self, loan_prefix: str) -> Optional[LoanDetails]:
        """
        Get loan details for a specific loan.
        
        Args:
            loan_prefix: Prefix for loan fields (e.g., 'initial_loan', 'refinance_loan')
            
        Returns:
            LoanDetails object or None if loan amount is not specified
        """
        amount_field = f"{loan_prefix}_amount"
        
        if amount_field not in self.data or self.data[amount_field] is None:
            return None
        
        try:
            return LoanDetails(
                amount=Money(self.data[amount_field]),
                interest_rate=Percentage(self.data.get(f"{loan_prefix}_interest_rate", 0) or 0),
                term=int(self.data.get(f"{loan_prefix}_term", 360) or 360),
                is_interest_only=bool(self.data.get(f"{loan_prefix}_is_interest_only", False)),
                name=self.data.get(f"{loan_prefix}_name", loan_prefix.replace('_', ' ').title())
            )
        except Exception as e:
            logger.error(f"Error creating loan details for {loan_prefix}: {str(e)}")
            return None
    
    @safe_calculation(Money(0))
    def calculate_monthly_income(self) -> Money:
        """
        Calculate monthly income.
        
        Returns:
            Monthly income as Money object
        """
        return Money(self.data.get('monthly_rent', 0) or 0)
    
    @safe_calculation(Money(0))
    def calculate_monthly_expenses(self) -> Money:
        """
        Calculate monthly expenses.
        
        Returns:
            Monthly expenses as Money object
        """
        expenses = Money(0)
        
        # Property taxes (annual to monthly)
        if 'property_taxes' in self.data and self.data['property_taxes']:
            expenses += Money(self.data['property_taxes']) / 12
        
        # Insurance (annual to monthly)
        if 'insurance' in self.data and self.data['insurance']:
            expenses += Money(self.data['insurance']) / 12
        
        # HOA/COA/Co-op fees
        if 'hoa_coa_coop' in self.data and self.data['hoa_coa_coop']:
            expenses += Money(self.data['hoa_coa_coop'])
        
        # Management fee
        if 'management_fee_percentage' in self.data and self.data['management_fee_percentage'] and 'monthly_rent' in self.data:
            management_fee = Money(self.data['monthly_rent']) * Percentage(self.data['management_fee_percentage'])
            expenses += management_fee
        
        # CapEx
        if 'capex_percentage' in self.data and self.data['capex_percentage'] and 'monthly_rent' in self.data:
            capex = Money(self.data['monthly_rent']) * Percentage(self.data['capex_percentage'])
            expenses += capex
        
        # Vacancy
        if 'vacancy_percentage' in self.data and self.data['vacancy_percentage'] and 'monthly_rent' in self.data:
            vacancy = Money(self.data['monthly_rent']) * Percentage(self.data['vacancy_percentage'])
            expenses += vacancy
        
        # Repairs
        if 'repairs_percentage' in self.data and self.data['repairs_percentage'] and 'monthly_rent' in self.data:
            repairs = Money(self.data['monthly_rent']) * Percentage(self.data['repairs_percentage'])
            expenses += repairs
        
        # Utilities
        if 'utilities' in self.data and self.data['utilities']:
            expenses += Money(self.data['utilities'])
        
        # Internet
        if 'internet' in self.data and self.data['internet']:
            expenses += Money(self.data['internet'])
        
        # Cleaning
        if 'cleaning' in self.data and self.data['cleaning']:
            expenses += Money(self.data['cleaning'])
        
        # Pest control
        if 'pest_control' in self.data and self.data['pest_control']:
            expenses += Money(self.data['pest_control'])
        
        # Landscaping
        if 'landscaping' in self.data and self.data['landscaping']:
            expenses += Money(self.data['landscaping'])
        
        return expenses
    
    @safe_calculation(Money(0))
    def calculate_loan_payments(self) -> Money:
        """
        Calculate total monthly loan payments.
        
        Returns:
            Total monthly loan payments as Money object
        """
        total_payment = Money(0)
        
        # Check for initial loan
        initial_loan = self.get_loan_details('initial_loan')
        if initial_loan:
            payment = initial_loan.calculate_payment()
            total_payment += payment.total
        
        # Check for additional loans
        for i in range(1, 4):  # loans 1-3
            loan = self.get_loan_details(f'loan{i}_loan')
            if loan:
                payment = loan.calculate_payment()
                total_payment += payment.total
        
        return total_payment
    
    @safe_calculation(Money(0))
    def calculate_monthly_cash_flow(self) -> Money:
        """
        Calculate monthly cash flow.
        
        Returns:
            Monthly cash flow as Money object
        """
        income = self.calculate_monthly_income()
        expenses = self.calculate_monthly_expenses()
        loan_payments = self.calculate_loan_payments()
        
        return income - expenses - loan_payments
    
    @safe_calculation(Money(0))
    def calculate_total_investment(self) -> Money:
        """
        Calculate total investment amount.
        
        Returns:
            Total investment as Money object
        """
        total_investment = Money(0)
        
        # Down payment for initial loan
        initial_loan = self.get_loan_details('initial_loan')
        if initial_loan:
            down_payment_field = 'initial_loan_down_payment'
            if down_payment_field in self.data and self.data[down_payment_field]:
                total_investment += Money(self.data[down_payment_field])
        
        # Closing costs
        if 'closing_costs' in self.data and self.data['closing_costs']:
            total_investment += Money(self.data['closing_costs'])
        
        # Renovation costs
        if 'renovation_costs' in self.data and self.data['renovation_costs']:
            total_investment += Money(self.data['renovation_costs'])
        
        # Furnishing costs
        if 'furnishing_costs' in self.data and self.data['furnishing_costs']:
            total_investment += Money(self.data['furnishing_costs'])
        
        # Marketing costs
        if 'marketing_costs' in self.data and self.data['marketing_costs']:
            total_investment += Money(self.data['marketing_costs'])
        
        # Cash to seller
        if 'cash_to_seller' in self.data and self.data['cash_to_seller']:
            total_investment += Money(self.data['cash_to_seller'])
        
        # Assignment fee
        if 'assignment_fee' in self.data and self.data['assignment_fee']:
            total_investment += Money(self.data['assignment_fee'])
        
        return total_investment
    
    @safe_calculation(Percentage(0))
    def calculate_cash_on_cash_return(self) -> Percentage:
        """
        Calculate cash-on-cash return.
        
        Returns:
            Cash-on-cash return as Percentage object
        """
        annual_cash_flow = self.calculate_monthly_cash_flow() * 12
        total_investment = self.calculate_total_investment()
        
        return InvestmentMetricsCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=annual_cash_flow,
            total_investment=total_investment
        )
    
    @safe_calculation(Percentage(0))
    def calculate_cap_rate(self) -> Percentage:
        """
        Calculate capitalization rate.
        
        Returns:
            Cap rate as Percentage object
        """
        # Calculate NOI (income - expenses, excluding debt service)
        income = self.calculate_monthly_income()
        expenses = self.calculate_monthly_expenses()
        annual_noi = (income - expenses) * 12  # Annual NOI
        
        purchase_price = Money(self.data.get('purchase_price', 0) or 0)
        
        return InvestmentMetricsCalculator.calculate_cap_rate(
            annual_noi=annual_noi,
            property_value=purchase_price
        )
    
    @safe_calculation(0.0)
    def calculate_debt_service_coverage_ratio(self) -> float:
        """
        Calculate debt service coverage ratio.
        
        Returns:
            DSCR as a float
        """
        # Calculate NOI (income - expenses, excluding debt service)
        income = self.calculate_monthly_income()
        expenses = self.calculate_monthly_expenses()
        monthly_noi = income - expenses
        annual_noi = monthly_noi * 12
        
        loan_payments = self.calculate_loan_payments()
        annual_debt_service = loan_payments * 12
        
        return InvestmentMetricsCalculator.calculate_debt_service_coverage_ratio(
            annual_noi=annual_noi,
            annual_debt_service=annual_debt_service
        )
    
    @safe_calculation(Percentage(0))
    def calculate_expense_ratio(self) -> Percentage:
        """
        Calculate expense ratio.
        
        Returns:
            Expense ratio as Percentage object
        """
        expenses = self.calculate_monthly_expenses()
        income = self.calculate_monthly_income()
        
        annual_expenses = expenses * 12
        annual_income = income * 12
        
        return InvestmentMetricsCalculator.calculate_expense_ratio(
            annual_expenses=annual_expenses,
            annual_income=annual_income
        )
    
    @safe_calculation(0.0)
    def calculate_gross_rent_multiplier(self) -> float:
        """
        Calculate gross rent multiplier.
        
        Returns:
            GRM as a float
        """
        purchase_price = Money(self.data.get('purchase_price', 0) or 0)
        annual_rent = self.calculate_monthly_income() * 12
        
        return InvestmentMetricsCalculator.calculate_gross_rent_multiplier(
            purchase_price=purchase_price,
            annual_rent=annual_rent
        )
    
    @safe_calculation(Percentage(0))
    def calculate_breakeven_occupancy(self) -> Percentage:
        """
        Calculate breakeven occupancy rate.
        
        Returns:
            Breakeven occupancy as Percentage object
        """
        expenses = self.calculate_monthly_expenses()
        loan_payments = self.calculate_loan_payments()
        potential_income = self.calculate_monthly_income()
        
        annual_expenses = expenses * 12
        annual_debt_service = loan_payments * 12
        annual_potential_income = potential_income * 12
        
        return InvestmentMetricsCalculator.calculate_breakeven_occupancy(
            annual_expenses=annual_expenses,
            annual_debt_service=annual_debt_service,
            annual_potential_income=annual_potential_income
        )
    
    @safe_calculation(Money(0))
    def calculate_holding_costs(self) -> Money:
        """
        Calculate total holding costs during renovation.
        
        Returns:
            Total holding costs as Money object
        """
        monthly_holding_costs = self.calculate_monthly_holding_costs()
        renovation_duration = int(self.data.get('renovation_duration', 0) or 0)
        
        return monthly_holding_costs * renovation_duration
    
    @safe_calculation(Money(0))
    def calculate_monthly_holding_costs(self) -> Money:
        """
        Calculate monthly holding costs during renovation.
        
        Returns:
            Monthly holding costs as Money object
        """
        holding_costs = Money(0)
        
        # Property taxes (annual to monthly)
        if 'property_taxes' in self.data and self.data['property_taxes']:
            holding_costs += Money(self.data['property_taxes']) / 12
        
        # Insurance (annual to monthly)
        if 'insurance' in self.data and self.data['insurance']:
            holding_costs += Money(self.data['insurance']) / 12
        
        # HOA/COA/Co-op fees
        if 'hoa_coa_coop' in self.data and self.data['hoa_coa_coop']:
            holding_costs += Money(self.data['hoa_coa_coop'])
        
        # Utilities
        if 'utilities' in self.data and self.data['utilities']:
            holding_costs += Money(self.data['utilities'])
        
        # Calculate loan interest - handle different analysis types
        initial_loan = self.get_loan_details('initial_loan')
        if initial_loan:
            # During renovation, assume interest-only payments
            monthly_interest = Money(initial_loan.amount.dollars * (initial_loan.interest_rate.value / 100 / 12))
            holding_costs += monthly_interest
        
        return holding_costs
    
    @safe_calculation(Money(0))
    def calculate_mao(self) -> Money:
        """
        Calculate Maximum Allowable Offer.
        
        Returns:
            MAO as Money object
        """
        # Default implementation - override in specialized classes
        return Money(0)
    
    @safe_calculation(Percentage(0))
    def calculate_roi(self) -> Percentage:
        """
        Calculate Return on Investment (ROI).
        
        This calculation considers both cash flow and equity appreciation
        for a more comprehensive ROI calculation.
        
        Returns:
            ROI as Percentage object
        """
        # Get annual cash flow
        annual_cash_flow = self.calculate_monthly_cash_flow() * 12
        
        # Get total investment
        total_investment = self.calculate_total_investment()
        
        # Get equity projection for 5 years
        equity_projection = self.calculate_equity_projection(5)
        
        if equity_projection:
            # Calculate total return (cash flow + equity gain)
            total_return = (annual_cash_flow * 5) + equity_projection.total_equity_gain
            
            # Calculate ROI using the investment metrics calculator
            return InvestmentMetricsCalculator.calculate_roi(
                initial_investment=total_investment,
                total_return=total_return,
                time_period_years=5.0
            )
        else:
            # Fall back to cash-on-cash return if equity projection fails
            return self.calculate_cash_on_cash_return()
    
    @safe_calculation(None)
    def calculate_equity_projection(self, projection_years: int = 30) -> Optional[EquityProjection]:
        """
        Calculate equity projection over time.
        
        Args:
            projection_years: Number of years to project
            
        Returns:
            EquityProjection object or None if calculation fails
        """
        # Get purchase price
        purchase_price = Money(self.data.get('purchase_price', 0) or 0)
        
        # Get current value (use purchase price if not specified)
        current_value = Money(self.data.get('current_value', 0) or purchase_price.dollars)
        
        # Get appreciation rate (default to 3%)
        appreciation_rate = Percentage(self.data.get('appreciation_rate', 3) or 3)
        
        # Get loan details
        loan_details = self.get_loan_details('initial_loan')
        
        # Get payments made
        payments_made = int(self.data.get('payments_made', 0) or 0)
        
        # Calculate equity projection
        return InvestmentMetricsCalculator.project_equity(
            purchase_price=purchase_price,
            current_value=current_value,
            loan_details=loan_details,
            annual_appreciation_rate=appreciation_rate,
            projection_years=projection_years,
            payments_made=payments_made
        )
    
    @safe_calculation([])
    def calculate_yearly_equity_projections(self, projection_years: int = 30) -> List[YearlyProjection]:
        """
        Calculate year-by-year equity projections.
        
        Args:
            projection_years: Number of years to project
            
        Returns:
            List of YearlyProjection objects
        """
        # Get purchase price
        purchase_price = Money(self.data.get('purchase_price', 0) or 0)
        
        # Get current value (use purchase price if not specified)
        current_value = Money(self.data.get('current_value', 0) or purchase_price.dollars)
        
        # Get appreciation rate (default to 3%)
        appreciation_rate = Percentage(self.data.get('appreciation_rate', 3) or 3)
        
        # Get loan details
        loan_details = self.get_loan_details('initial_loan')
        
        # Get payments made
        payments_made = int(self.data.get('payments_made', 0) or 0)
        
        # Calculate yearly projections
        return InvestmentMetricsCalculator.generate_yearly_equity_projections(
            purchase_price=purchase_price,
            current_value=current_value,
            loan_details=loan_details,
            annual_appreciation_rate=appreciation_rate,
            projection_years=projection_years,
            payments_made=payments_made
        )
    
    def analyze(self) -> AnalysisResult:
        """
        Perform the analysis and return results.
        
        Returns:
            AnalysisResult object containing calculated metrics
        """
        # Validate data first
        validation_result = self.validate()
        if not validation_result.is_valid():
            logger.warning(f"Analysis validation failed: {validation_result}")
        
        # Calculate metrics
        monthly_cash_flow = self.calculate_monthly_cash_flow()
        annual_cash_flow = monthly_cash_flow * 12
        cash_on_cash_return = self.calculate_cash_on_cash_return()
        cap_rate = self.calculate_cap_rate()
        roi = self.calculate_roi()
        total_investment = self.calculate_total_investment()
        monthly_income = self.calculate_monthly_income()
        monthly_expenses = self.calculate_monthly_expenses()
        dscr = self.calculate_debt_service_coverage_ratio()
        expense_ratio = self.calculate_expense_ratio()
        grm = self.calculate_gross_rent_multiplier()
        breakeven_occupancy = self.calculate_breakeven_occupancy()
        mao = self.calculate_mao()
        
        # Calculate equity projections
        equity_projection = self.calculate_equity_projection()
        yearly_projections = self.calculate_yearly_equity_projections()
        
        # Create and return result object
        return AnalysisResult(
            monthly_cash_flow=monthly_cash_flow,
            annual_cash_flow=annual_cash_flow,
            cash_on_cash_return=cash_on_cash_return,
            cap_rate=cap_rate,
            roi=roi,
            total_investment=total_investment,
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            debt_service_coverage_ratio=dscr,
            expense_ratio=expense_ratio,
            gross_rent_multiplier=grm,
            price_per_unit=Money(0),  # Will be calculated in MultiFamily
            breakeven_occupancy=breakeven_occupancy,
            mao=mao,
            equity_projection=equity_projection,
            yearly_projections=yearly_projections
        )


class LTRAnalysis(BaseAnalysis):
    """
    Long-Term Rental analysis class.
    
    This class provides calculations specific to long-term rental properties.
    """
    
    def _validate_required_fields(self) -> None:
        """Validate required fields for LTR analysis."""
        # Call parent method first
        super()._validate_required_fields()
        
        # LTR-specific required fields
        required_fields = [
            ('property_taxes', 'Property Taxes'),
            ('insurance', 'Insurance')
        ]
        
        for field_name, display_name in required_fields:
            Validator.validate_required(
                self.validation_result,
                self.data,
                field_name,
                display_name
            )
    
    @safe_calculation(Money(0))
    def calculate_mao(self) -> Money:
        """
        Calculate Maximum Allowable Offer for LTR.
        
        Returns:
            MAO as Money object
        """
        # For LTR, MAO is based on desired cash flow and cap rate
        target_monthly_cash_flow = Money(200)  # $200/month minimum
        target_cap_rate = Percentage(8)  # 8% minimum
        
        # Calculate based on cap rate
        monthly_income = self.calculate_monthly_income()
        monthly_expenses = self.calculate_monthly_expenses()
        monthly_noi = monthly_income - monthly_expenses
        annual_noi = monthly_noi * 12
        
        cap_rate_mao = Money(annual_noi.dollars / (target_cap_rate.value / 100))
        
        # Calculate based on cash flow
        loan_payment_per_100k = Money(500)  # Approximate monthly payment per $100k at current rates
        
        # How much loan can the property support with target cash flow?
        supportable_payment = monthly_noi - target_monthly_cash_flow
        supportable_loan = supportable_payment / loan_payment_per_100k * 100000
        
        # Assume 80% LTV
        cash_flow_mao = supportable_loan / Decimal('0.8')
        
        # Take the lower of the two MAOs
        mao = min(cap_rate_mao, cash_flow_mao)
        
        return Money(max(0, mao.dollars))


class BRRRRAnalysis(BaseAnalysis):
    """
    Buy, Rehab, Rent, Refinance, Repeat analysis class.
    
    This class provides calculations specific to BRRRR strategy properties.
    """
    
    def _validate_required_fields(self) -> None:
        """Validate required fields for BRRRR analysis."""
        # Call parent method first
        super()._validate_required_fields()
        
        # BRRRR-specific required fields
        required_fields = [
            ('property_taxes', 'Property Taxes'),
            ('insurance', 'Insurance'),
            ('after_repair_value', 'After Repair Value'),
            ('renovation_costs', 'Renovation Costs'),
            ('renovation_duration', 'Renovation Duration')
        ]
        
        for field_name, display_name in required_fields:
            Validator.validate_required(
                self.validation_result,
                self.data,
                field_name,
                display_name
            )
    
    @safe_calculation(Money(0))
    def calculate_mao(self) -> Money:
        """
        Calculate Maximum Allowable Offer for BRRRR.
        
        Returns:
            MAO as Money object
        """
        # Get ARV
        arv = Money(self.data.get('after_repair_value', 0) or 0)
        
        # Get renovation costs
        renovation_costs = Money(self.data.get('renovation_costs', 0) or 0)
        
        # Get holding costs
        holding_costs = self.calculate_holding_costs()
        
        # Get closing costs
        closing_costs = Money(self.data.get('closing_costs', 0) or 0)
        
        # Refinance parameters - typically 75% LTV
        refinance_ltv = Percentage(self.data.get('refinance_ltv_percentage', 75) or 75)
        
        # Calculate loan amount based on ARV and LTV
        loan_amount = arv * (refinance_ltv.value / 100)
        
        # Set max cash left in deal - could be configurable
        max_cash_left = Money(10000)  # $10k default
        
        # Calculate MAO using the formula
        mao = loan_amount - renovation_costs - closing_costs - holding_costs + max_cash_left
        
        return Money(max(0, mao.dollars))
    
    @safe_calculation(Money(0))
    def calculate_total_investment(self) -> Money:
        """
        Calculate total investment amount for BRRRR.
        
        Returns:
            Total investment as Money object
        """
        # Start with standard calculation
        initial_investment = super().calculate_total_investment()
        
        # For BRRRR, consider refinance
        refinance_loan = self.get_loan_details('refinance_loan')
        initial_loan = self.get_loan_details('initial_loan')
        
        if refinance_loan and initial_loan:
            # Calculate cash out from refinance
            cash_out = refinance_loan.amount - initial_loan.amount
            
            # Subtract cash out from initial investment
            if cash_out.dollars > 0:
                return initial_investment - cash_out
        
        return initial_investment


class LeaseOptionAnalysis(BaseAnalysis):
    """
    Lease Option analysis class.
    
    This class provides calculations specific to lease option properties.
    """
    
    def _validate_required_fields(self) -> None:
        """Validate required fields for Lease Option analysis."""
        # Call parent method first
        super()._validate_required_fields()
        
        # Lease Option-specific required fields
        required_fields = [
            ('property_taxes', 'Property Taxes'),
            ('insurance', 'Insurance'),
            ('option_consideration_fee', 'Option Consideration Fee'),
            ('option_term_months', 'Option Term Months'),
            ('strike_price', 'Strike Price')
        ]
        
        for field_name, display_name in required_fields:
            Validator.validate_required(
                self.validation_result,
                self.data,
                field_name,
                display_name
            )
    
    @safe_calculation(Money(0))
    def calculate_monthly_income(self) -> Money:
        """
        Calculate monthly income for Lease Option.
        
        Returns:
            Monthly income as Money object
        """
        # Standard rent
        monthly_income = super().calculate_monthly_income()
        
        # Add monthly rent credit if applicable
        if 'monthly_rent_credit' in self.data and self.data['monthly_rent_credit']:
            monthly_income += Money(self.data['monthly_rent_credit'])
        
        return monthly_income
    
    @safe_calculation(Money(0))
    def calculate_total_investment(self) -> Money:
        """
        Calculate total investment for Lease Option.
        
        Returns:
            Total investment as Money object
        """
        total_investment = Money(0)
        
        # Option consideration fee
        if 'option_consideration_fee' in self.data and self.data['option_consideration_fee']:
            total_investment += Money(self.data['option_consideration_fee'])
        
        # Closing costs
        if 'closing_costs' in self.data and self.data['closing_costs']:
            total_investment += Money(self.data['closing_costs'])
        
        return total_investment
    
    @safe_calculation(Money(0))
    def calculate_effective_purchase_price(self) -> Money:
        """
        Calculate effective purchase price for Lease Option.
        
        Returns:
            Effective purchase price as Money object
        """
        strike_price = Money(self.data.get('strike_price', 0) or 0)
        
        # Subtract total rent credits
        if 'monthly_rent_credit' in self.data and self.data['monthly_rent_credit'] and 'option_term_months' in self.data:
            total_rent_credits = Money(self.data['monthly_rent_credit']) * int(self.data['option_term_months'])
            strike_price -= total_rent_credits
        
        # Subtract option consideration fee
        if 'option_consideration_fee' in self.data and self.data['option_consideration_fee']:
            strike_price -= Money(self.data['option_consideration_fee'])
        
        return Money(max(0, strike_price.dollars))
    
    @safe_calculation(Money(0))
    def calculate_total_rent_credits(self) -> Money:
        """
        Calculate total rent credits over the option term.
        
        Returns:
            Total rent credits as Money object
        """
        if 'monthly_rent_credit' in self.data and self.data['monthly_rent_credit'] and 'option_term_months' in self.data:
            monthly_rent_credit = Money(self.data['monthly_rent_credit'])
            option_term_months = int(self.data['option_term_months'])
            return monthly_rent_credit * option_term_months
        
        return Money(0)
    
    @safe_calculation(Percentage(0))
    def calculate_rent_credit_percentage(self) -> Percentage:
        """
        Calculate rent credit as a percentage of monthly rent.
        
        Returns:
            Rent credit percentage as Percentage object
        """
        if 'monthly_rent_credit' in self.data and self.data['monthly_rent_credit'] and 'monthly_rent' in self.data:
            monthly_rent_credit = Money(self.data['monthly_rent_credit'])
            monthly_rent = Money(self.data['monthly_rent'])
            
            if monthly_rent.dollars == 0:
                return Percentage(0)
            
            return Percentage((monthly_rent_credit.dollars / monthly_rent.dollars) * 100)
        
        return Percentage(0)
    
    @safe_calculation(Money(0))
    def calculate_option_equity(self) -> Money:
        """
        Calculate equity built through option (difference between strike price and current value).
        
        Returns:
            Option equity as Money object
        """
        strike_price = Money(self.data.get('strike_price', 0) or 0)
        current_value = Money(self.data.get('current_value', 0) or 0)
        
        if current_value.dollars == 0:
            # Use purchase price if current value is not specified
            current_value = Money(self.data.get('purchase_price', 0) or 0)
        
        # Apply appreciation if specified
        if 'appreciation_rate' in self.data and self.data['appreciation_rate'] and 'option_term_months' in self.data:
            appreciation_rate = Percentage(self.data['appreciation_rate'])
            option_term_years = int(self.data['option_term_months']) / 12
            
            for _ in range(int(option_term_years)):
                current_value = Money(current_value.dollars * (1 + appreciation_rate.as_decimal()))
            
            # Handle partial year
            partial_year = option_term_years - int(option_term_years)
            if partial_year > 0:
                current_value = Money(current_value.dollars * (1 + appreciation_rate.as_decimal() * partial_year))
        
        # Calculate equity (current value - strike price)
        if current_value.dollars > strike_price.dollars:
            return current_value - strike_price
        
        return Money(0)
    
    def analyze(self) -> AnalysisResult:
        """
        Perform the analysis and return results.
        
        Returns:
            AnalysisResult object containing calculated metrics
        """
        # Get base analysis results
        result = super().analyze()
        
        # Add Lease Option specific calculations to the result
        # These could be added to the AnalysisResult class if needed
        
        return result


class MultiFamilyAnalysis(BaseAnalysis):
    """
    Multi-Family property analysis class.
    
    This class provides calculations specific to multi-family properties.
    """
    
    def _validate_required_fields(self) -> None:
        """Validate required fields for Multi-Family analysis."""
        # Call parent method first
        super()._validate_required_fields()
        
        # Multi-Family-specific required fields
        required_fields = [
            ('property_taxes', 'Property Taxes'),
            ('insurance', 'Insurance'),
            ('total_units', 'Total Units'),
            ('occupied_units', 'Occupied Units')
        ]
        
        for field_name, display_name in required_fields:
            Validator.validate_required(
                self.validation_result,
                self.data,
                field_name,
                display_name
            )
    
    @safe_calculation(Money(0))
    def calculate_monthly_income(self) -> Money:
        """
        Calculate monthly income for Multi-Family.
        
        Returns:
            Monthly income as Money object
        """
        # Get rent per unit
        rent_per_unit = Money(self.data.get('monthly_rent', 0) or 0)
        
        # Get number of occupied units
        occupied_units = int(self.data.get('occupied_units', 0) or 0)
        
        # Calculate base rental income
        monthly_income = rent_per_unit * occupied_units
        
        # Add other income sources if available
        if 'parking_income' in self.data and self.data['parking_income']:
            monthly_income += Money(self.data['parking_income'])
            
        if 'laundry_income' in self.data and self.data['laundry_income']:
            monthly_income += Money(self.data['laundry_income'])
            
        if 'storage_income' in self.data and self.data['storage_income']:
            monthly_income += Money(self.data['storage_income'])
            
        if 'other_income' in self.data and self.data['other_income']:
            monthly_income += Money(self.data['other_income'])
        
        return monthly_income
    
    @safe_calculation(Money(0))
    def calculate_monthly_expenses(self) -> Money:
        """
        Calculate monthly expenses for Multi-Family.
        
        Returns:
            Monthly expenses as Money object
        """
        # Get base expenses
        expenses = super().calculate_monthly_expenses()
        
        # Add Multi-Family specific expenses
        
        # Common area maintenance
        if 'common_area_maintenance' in self.data and self.data['common_area_maintenance']:
            expenses += Money(self.data['common_area_maintenance'])
        
        # Elevator maintenance
        if 'elevator_maintenance' in self.data and self.data['elevator_maintenance']:
            expenses += Money(self.data['elevator_maintenance'])
        
        # Staff payroll
        if 'staff_payroll' in self.data and self.data['staff_payroll']:
            expenses += Money(self.data['staff_payroll'])
        
        # Security
        if 'security' in self.data and self.data['security']:
            expenses += Money(self.data['security'])
        
        return expenses
    
    @safe_calculation(Money(0))
    def calculate_price_per_unit(self) -> Money:
        """
        Calculate price per unit for Multi-Family.
        
        Returns:
            Price per unit as Money object
        """
        purchase_price = Money(self.data.get('purchase_price', 0) or 0)
        total_units = int(self.data.get('total_units', 0) or 0)
        
        return InvestmentMetricsCalculator.calculate_price_per_unit(
            purchase_price=purchase_price,
            unit_count=total_units
        )
    
    @safe_calculation(Percentage(0))
    def calculate_occupancy_rate(self) -> Percentage:
        """
        Calculate occupancy rate for Multi-Family.
        
        Returns:
            Occupancy rate as Percentage object
        """
        total_units = int(self.data.get('total_units', 0) or 0)
        occupied_units = int(self.data.get('occupied_units', 0) or 0)
        
        if total_units == 0:
            return Percentage(0)
        
        return Percentage((occupied_units / total_units) * 100)
    
    def analyze(self) -> AnalysisResult:
        """
        Perform the analysis and return results.
        
        Returns:
            AnalysisResult object containing calculated metrics
        """
        # Get base analysis results
        result = super().analyze()
        
        # Add Multi-Family specific calculations
        result.price_per_unit = self.calculate_price_per_unit()
        
        return result


class PadSplitAnalysis(BaseAnalysis):
    """
    PadSplit property analysis class.
    
    This class provides calculations specific to PadSplit properties,
    which involve renting individual rooms in a property.
    """
    
    def _validate_required_fields(self) -> None:
        """Validate required fields for PadSplit analysis."""
        # Call parent method first
        super()._validate_required_fields()
        
        # PadSplit-specific required fields
        required_fields = [
            ('property_taxes', 'Property Taxes'),
            ('insurance', 'Insurance'),
            ('furnishing_costs', 'Furnishing Costs'),
            ('padsplit_platform_percentage', 'PadSplit Platform Percentage')
        ]
        
        for field_name, display_name in required_fields:
            Validator.validate_required(
                self.validation_result,
                self.data,
                field_name,
                display_name
            )
    
    @safe_calculation(Money(0))
    def calculate_monthly_expenses(self) -> Money:
        """
        Calculate monthly expenses for PadSplit.
        
        Returns:
            Monthly expenses as Money object
        """
        # Get base expenses
        expenses = super().calculate_monthly_expenses()
        
        # Add PadSplit platform fee
        if 'padsplit_platform_percentage' in self.data and self.data['padsplit_platform_percentage'] and 'monthly_rent' in self.data:
            platform_fee = Money(self.data['monthly_rent']) * Percentage(self.data['padsplit_platform_percentage'])
            expenses += platform_fee
        
        return expenses
    
    @safe_calculation(Money(0))
    def calculate_total_investment(self) -> Money:
        """
        Calculate total investment for PadSplit.
        
        Returns:
            Total investment as Money object
        """
        # Get base investment
        total_investment = super().calculate_total_investment()
        
        # Ensure furnishing costs are included
        if 'furnishing_costs' in self.data and self.data['furnishing_costs']:
            # Check if it's already included in the base calculation
            if 'furnishing_costs' not in self.data:
                total_investment += Money(self.data['furnishing_costs'])
        
        return total_investment


def create_analysis(data: Dict[str, Any]) -> BaseAnalysis:
    """
    Factory function to create the appropriate analysis object based on analysis type.
    
    Args:
        data: Dictionary containing analysis data
        
    Returns:
        Appropriate analysis object for the specified type
        
    Raises:
        ValueError: If the analysis type is invalid
    """
    analysis_type = data.get('analysis_type')
    
    if not analysis_type:
        raise ValueError("Analysis type is required")
    
    if analysis_type == "LTR":
        return LTRAnalysis(data)
    elif analysis_type == "BRRRR":
        return BRRRRAnalysis(data)
    elif analysis_type == "LeaseOption":
        return LeaseOptionAnalysis(data)
    elif analysis_type == "MultiFamily":
        return MultiFamilyAnalysis(data)
    elif analysis_type == "PadSplit":
        return PadSplitAnalysis(data)
    else:
        raise ValueError(f"Invalid analysis type: {analysis_type}")
