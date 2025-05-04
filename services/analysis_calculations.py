from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Generic
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment, ensure_money, ensure_percentage
from datetime import datetime
from math import ceil
import logging
import json
import traceback
from utils.error_handling import safe_calculation
from utils.validators import Validator

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler if it doesn't exist
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Constants
MAX_RENOVATION_DURATION = 24
DEFAULT_ANNUAL_INCREASE_RATE = 0.025
MAX_LOAN_TERM = 360  # 30 years
MAX_LOAN_INTEREST_RATE = 30.0  # 30%

# Typical ranges for percentage fields
PERCENTAGE_RANGES = {
    'management_fee_percentage': (0, 15),
    'capex_percentage': (0, 10),
    'vacancy_percentage': (0, 15),
    'repairs_percentage': (0, 15),
}

def format_percentage_or_infinite(value: Union[Percentage, str]) -> str:
    """
    Format a percentage value or the string 'Infinite' for consistent display.
    
    Args:
        value: Either a Percentage object or the string 'Infinite'
        
    Returns:
        Formatted string representation for display
    """
    if value == "Infinite":
        return "Infinite"
    
    if isinstance(value, Percentage):
        # Format with one decimal place
        return f"{value.value:.1f}%"
    
    # Handle unexpected types
    return str(value)

@dataclass
class LoanDetails:
    """Data class to encapsulate loan parameters."""
    amount: Money
    interest_rate: Percentage
    term: int
    is_interest_only: bool = False
    
    def __post_init__(self) -> None:
        """Validate loan details after initialization."""
        Validator.validate_positive_number(self.amount, "Loan amount")
        
        # Validate interest rate is between 0 and MAX_LOAN_INTEREST_RATE
        if self.interest_rate.value < 0:
            raise ValueError(f"Interest rate must be greater than or equal to 0%")
        if self.interest_rate.value > MAX_LOAN_INTEREST_RATE:
            raise ValueError(f"Interest rate must be less than or equal to {MAX_LOAN_INTEREST_RATE}%")
            
        if self.term <= 0 or self.term > MAX_LOAN_TERM:
            raise ValueError(f"Loan term must be between 1 and {MAX_LOAN_TERM} months")

from utils.financial_calculator import FinancialCalculator

class LoanCalculator:
    """Utility class for loan-related calculations."""
    
    @staticmethod
    @safe_calculation(default_value=Money(0))
    def calculate_payment(loan: LoanDetails) -> Money:
        """Calculate monthly payment for a loan."""
        if loan.amount.dollars == 0:
            return Money(0)
            
        if loan.amount.dollars < 0 or loan.term <= 0:
            return Money(0)
        
        # Use the centralized financial calculator
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=loan.amount,
            annual_rate=loan.interest_rate,
            term=loan.term,
            is_interest_only=loan.is_interest_only
        )
        
        logger.debug(f"Calculated payment: {payment.total} for loan amount: {loan.amount}")
        return payment.total

@dataclass
class AnalysisReport:
    """Container for complete analysis report data matching flat schema"""
    # Core metadata
    id: str
    user_id: str
    analysis_name: str
    analysis_type: str
    address: str
    generated_date: str
    
    # Property details
    square_footage: int
    lot_size: int
    year_built: int
    
    # Financial details
    purchase_price: int
    after_repair_value: int
    renovation_costs: int
    renovation_duration: int
    monthly_rent: int
    
    # Operating expenses
    property_taxes: int
    insurance: int
    hoa_coa_coop: int
    management_fee_percentage: float
    capex_percentage: float
    vacancy_percentage: float
    repairs_percentage: float
    
    # Calculated metrics
    metrics: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert report to dictionary format."""
        return {
            # Core metadata
            'id': self.id,
            'user_id': self.user_id,
            'analysis_name': self.analysis_name,
            'analysis_type': self.analysis_type,
            'address': self.address,
            'generated_date': self.generated_date,
            
            # Property details
            'square_footage': self.square_footage,
            'lot_size': self.lot_size,
            'year_built': self.year_built,
            
            # Financial details
            'purchase_price': self.purchase_price,
            'after_repair_value': self.after_repair_value,
            'renovation_costs': self.renovation_costs,
            'renovation_duration': self.renovation_duration,
            'monthly_rent': self.monthly_rent,
            
            # Operating expenses
            'property_taxes': self.property_taxes,
            'insurance': self.insurance,
            'hoa_coa_coop': self.hoa_coa_coop,
            'management_fee_percentage': self.management_fee_percentage,
            'capex_percentage': self.capex_percentage,
            'vacancy_percentage': self.vacancy_percentage,
            'repairs_percentage': self.repairs_percentage,
            
            # Calculated metrics
            'metrics': self.metrics
        }

    @classmethod
    def from_analysis(cls, analysis: 'Analysis') -> 'AnalysisReport':
        """Create report from analysis instance."""
        return cls(
            # Core metadata
            id=analysis.data['id'],
            user_id=analysis.data['user_id'],
            analysis_name=analysis.data['analysis_name'],
            analysis_type=analysis.data['analysis_type'],
            address=analysis.data['address'],
            generated_date=datetime.now().isoformat(),
            
            # Property details
            square_footage=analysis.data.get('square_footage', 0),
            lot_size=analysis.data.get('lot_size', 0),
            year_built=analysis.data.get('year_built', 0),
            
            # Financial details
            purchase_price=analysis.data.get('purchase_price', 0),
            after_repair_value=analysis.data.get('after_repair_value', 0),
            renovation_costs=analysis.data.get('renovation_costs', 0),
            renovation_duration=analysis.data.get('renovation_duration', 0),
            monthly_rent=analysis.data.get('monthly_rent', 0),
            
            # Operating expenses
            property_taxes=analysis.data.get('property_taxes', 0),
            insurance=analysis.data.get('insurance', 0),
            hoa_coa_coop=analysis.data.get('hoa_coa_coop', 0),
            management_fee_percentage=analysis.data.get('management_fee_percentage', 0.0),
            capex_percentage=analysis.data.get('capex_percentage', 0.0),
            vacancy_percentage=analysis.data.get('vacancy_percentage', 0.0),
            repairs_percentage=analysis.data.get('repairs_percentage', 0.0),
            
            # Get calculated metrics
            metrics=analysis.get_report_data()['metrics']
        )

    def get_type_specific_data(self) -> Dict:
        """Get additional data specific to analysis type."""
        if 'BRRRR' in self.analysis_type:
            return {
                'equity_captured': self.metrics.get('equity_captured'),
                'cash_recouped': self.metrics.get('cash_recouped'),
                'total_project_costs': self.metrics.get('total_project_costs'),
                'holding_costs': self.metrics.get('holding_costs')
            }
        if 'PadSplit' in self.analysis_type:
            return {
                'utilities': self.metrics.get('utilities'),
                'internet': self.metrics.get('internet'),
                'cleaning': self.metrics.get('cleaning'),
                'pest_control': self.metrics.get('pest_control'),
                'landscaping': self.metrics.get('landscaping'),
                'platform_fee': self.metrics.get('platform_fee')
            }
        return {}

class Analysis(ABC):
    """Base class for all property investment analysis types."""
    
    def __init__(self, data: Dict):
        """Initialize analysis with flat data structure."""
        self.data = data
        self.calculated_metrics = {}
        self._validate_base_requirements()
        self._validate_type_specific_requirements()

    @abstractmethod
    def _validate_type_specific_requirements(self) -> None:
        """Validate requirements specific to the analysis type."""
        pass

    def _validate_base_requirements(self) -> None:
        """Validate base requirements common to all analysis types."""
        logger.debug(f"Analysis type: {self.data.get('analysis_type')}")
        logger.debug(f"Analysis data: {self.data}")

        try:
            # 1. Validate metadata fields
            required_meta = {
                'id': 'ID',
                'user_id': 'User ID',
                'created_at': 'Created date',
                'updated_at': 'Updated date',
                'analysis_type': 'Analysis type',
                'analysis_name': 'Analysis name',
                'address': 'Property address'
            }
            Validator.validate_required_fields(self.data, required_meta)
            
            # 2. Validate ID is valid UUID
            Validator.validate_uuid(self.data['id'])
            
            # 3. Validate dates are in ISO format
            Validator.validate_date_format(self.data['created_at'], "Created date")
            Validator.validate_date_format(self.data['updated_at'], "Updated date")
            
            # 4. Validate core calculation fields - monthly_rent only for non-Multi-Family
            if self.data.get('analysis_type') != 'Multi-Family':
                value = self.data.get('monthly_rent')
                if not value or not isinstance(value, (int, float)) or value < 0:
                    raise ValueError(f"Invalid monthly_rent: must be a positive number")

            # 5. Validate percentage fields
            for field, (min_val, max_val) in PERCENTAGE_RANGES.items():
                value = self.data.get(field, 0)
                Validator.validate_percentage(value, field, min_val, max_val)

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def _get_money(self, field: str) -> Money:
        """Safely get a money value from data."""
        return Money(self.data.get(field, 0))

    def _get_percentage(self, field: str) -> Percentage:
        """Safely get a percentage value from data."""
        return Percentage(self.data.get(field, 0))

    def _get_loan_details(self, prefix: str) -> Optional[LoanDetails]:
        """Get loan details for a specific loan prefix."""
        amount = self._get_money(f'{prefix}_loan_amount')
        
        # Return None if no loan amount
        if amount.dollars <= 0:
            return None
            
        return LoanDetails(
            amount=amount,
            interest_rate=self._get_percentage(f'{prefix}_loan_interest_rate'),
            term=self.data.get(f'{prefix}_loan_term', 0),
            is_interest_only=self.data.get(f'{prefix}_interest_only', False)
        )

    @safe_calculation(default_value=Money(0))
    def _calculate_single_loan_payment(self, prefix: str) -> Money:
        """Calculate payment for a single loan by prefix."""
        loan_details = self._get_loan_details(prefix)
        if not loan_details:
            return Money(0)
            
        payment = LoanCalculator.calculate_payment(loan_details)
        self.calculated_metrics[f'{prefix}_loan_payment'] = str(payment)
        logger.debug(f"Calculated {prefix} payment: {payment}")
        return payment

    @safe_calculation(default_value=Money(0))
    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow."""
        logger.debug("=== Starting Monthly Cash Flow Calculation ===")
        
        # Get income
        monthly_income = self._get_money('monthly_rent')
        logger.debug(f"Monthly income: {monthly_income}")
        
        # Calculate expenses
        operating_expenses = self._calculate_operating_expenses()
        logger.debug(f"Operating expenses: {operating_expenses}")
        
        # Calculate loan payments
        loan_payments = self._calculate_loan_payments()
        logger.debug(f"Loan payments: {loan_payments}")
        
        # Calculate final cash flow
        cash_flow = monthly_income - operating_expenses - loan_payments
        logger.debug(f"Final monthly cash flow: {cash_flow}")
        
        return cash_flow

    @safe_calculation(default_value=Money(0))
    def _calculate_operating_expenses(self) -> Money:
        """Calculate total monthly operating expenses."""
        # Fixed expenses
        fixed_expenses = sum([
            self._get_money('property_taxes'),
            self._get_money('insurance'),
            self._get_money('hoa_coa_coop')
        ], Money(0))
        
        # Percentage-based expenses
        monthly_rent = self._get_money('monthly_rent')
        rent_based_expenses = sum([
            monthly_rent * self._get_percentage('management_fee_percentage'),
            monthly_rent * self._get_percentage('capex_percentage'),
            monthly_rent * self._get_percentage('vacancy_percentage'),
            monthly_rent * self._get_percentage('repairs_percentage')
        ], Money(0))
        
        # PadSplit-specific expenses if applicable
        padsplit_expenses = Money(0)
        if 'PadSplit' in self.data.get('analysis_type', ''):
            padsplit_expenses = sum([
                self._get_money('utilities'),
                self._get_money('internet'),
                self._get_money('cleaning'),
                self._get_money('pest_control'),
                self._get_money('landscaping'),
                monthly_rent * self._get_percentage('padsplit_platform_percentage')
            ], Money(0))
        
        return fixed_expenses + rent_based_expenses + padsplit_expenses

    @safe_calculation(default_value=Money(0))
    def _calculate_loan_payments(self) -> Money:
        """Calculate total monthly loan payments."""
        # This is the base implementation - each subclass can override as needed
        total_payments = Money(0)
        loan_prefixes = ['loan1', 'loan2', 'loan3']
        
        for prefix in loan_prefixes:
            total_payments += self._calculate_single_loan_payment(prefix)
                
        logger.debug(f"Total monthly loan payments: ${total_payments.dollars:.2f}")
        return total_payments

    @safe_calculation(default_value=Money(0))
    def calculate_total_cash_invested(self) -> Money:
        """
        Calculate total cash invested in the project.
        Only counts actual out-of-pocket expenses, regardless of financing type.
        """
        logger.debug("=== Starting Total Cash Invested Calculation ===")
        
        # Base investment (out of pocket costs)
        total_cash = sum([
            self._get_money('cash_to_seller'),          # Any cash paid directly to seller
            self._get_money('renovation_costs'),        # Renovation costs
            self._get_money('closing_costs'),           # Base closing costs
            self._get_money('assignment_fee'),          # Any assignment fees
            self._get_money('marketing_costs')          # Marketing costs
        ], Money(0))
        
        # Add loan down payments and closing costs for all loans
        for prefix in ['loan1', 'loan2', 'loan3']:
            total_cash += sum([
                self._get_money(f'{prefix}_loan_down_payment'),
                self._get_money(f'{prefix}_loan_closing_costs')
            ], Money(0))

        # Add furnishing costs for PadSplit
        if 'PadSplit' in self.data.get('analysis_type', ''):
            total_cash += self._get_money('furnishing_costs')
            
        return Money(max(0, float(total_cash.dollars)))

    @property
    def annual_cash_flow(self) -> Money:
        """Calculate annual cash flow."""
        return self.calculate_monthly_cash_flow() * 12

    @property
    def cash_on_cash_return(self) -> Union[Percentage, str]:
        """Calculate Cash on Cash return."""
        cash_invested = self.calculate_total_cash_invested()
        annual_cf = self.annual_cash_flow
        
        # Use the centralized financial calculator
        return FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=annual_cf,
            total_investment=cash_invested
        )

    @property
    def roi(self) -> Percentage:
        """Calculate ROI including equity and cash flow."""
        cash_invested = self.calculate_total_cash_invested()
        if cash_invested.dollars <= 0:
            return Percentage(0)
        
        annual_cf = float(self.annual_cash_flow.dollars)
        
        equity_captured = 0
        if 'BRRRR' in self.data.get('analysis_type', ''):
            arv = self._get_money('after_repair_value')
            total_costs = sum([
                self._get_money('purchase_price'),
                self._get_money('renovation_costs')
            ], Money(0))
            equity_captured = float((arv - total_costs).dollars)
        
        total_return = annual_cf + equity_captured
        return Percentage((total_return / float(cash_invested.dollars)) * 100)

    def _calculate_core_metrics(self) -> Dict:
        """Calculate core metrics shared by all analysis types."""
        monthly_cf = self.calculate_monthly_cash_flow()
        return {
            'monthly_cash_flow': str(monthly_cf),
            'annual_cash_flow': str(monthly_cf * 12),
            'total_cash_invested': str(self.calculate_total_cash_invested()),
            'cash_on_cash_return': str(self.cash_on_cash_return),
            'roi': str(self.roi)
        }

    def get_report_data(self) -> Dict:
        """Get analysis report data with calculated metrics."""
        try:
            # Calculate core metrics
            metrics = self._calculate_core_metrics()
            
            # Add any calculated loan payments that have been computed
            metrics.update({
                key: value for key, value in self.calculated_metrics.items()
                if 'loan_payment' in key
            })
            
            # Add type-specific metrics
            type_specific_metrics = self._calculate_type_specific_metrics()
            metrics.update(type_specific_metrics)
            
            return {'metrics': metrics}
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    @abstractmethod
    def _calculate_type_specific_metrics(self) -> Dict:
        """Calculate metrics specific to the analysis type."""
        return {}

class LeaseOptionAnalysis(Analysis):
    """Lease option analysis implementation."""
    
    def __init__(self, data: Dict):
        """Initialize lease option analysis."""
        if data.get('analysis_type') != 'Lease Option':
            raise ValueError("Invalid analysis type for lease option analysis")
            
        super().__init__(data)

    def _validate_type_specific_requirements(self) -> None:
        """Validate fields specific to lease option analysis."""
        try:
            # Validate required numeric fields
            required_fields = {
                'option_consideration_fee': 'Option fee',
                'option_term_months': 'Option term',
                'strike_price': 'Strike price',
                'monthly_rent_credit_percentage': 'Monthly rent credit percentage',
                'rent_credit_cap': 'Rent credit cap'
            }
            
            for field, display_name in required_fields.items():
                if field == 'option_term_months':
                    value = self.data.get(field, 0)
                    Validator.validate_positive_number(value, display_name)
                else:
                    value = self._get_money(field)
                    Validator.validate_positive_number(value, display_name)

            # Validate rent credit percentage is between 0 and 100
            rent_credit_pct = self.data.get('monthly_rent_credit_percentage', 0)
            if rent_credit_pct < 0 or rent_credit_pct > 100:
                raise ValueError("Monthly rent credit percentage must be between 0 and 100%")

            # Validate strike price is greater than purchase price
            if float(self.data.get('strike_price', 0)) <= float(self.data.get('purchase_price', 0)):
                raise ValueError("Strike price must be greater than purchase price")

            # Validate standard rental fields
            rental_fields = {
                'monthly_rent': 'Monthly rent',
                'property_taxes': 'Property taxes',
                'insurance': 'Insurance'
            }
            
            for field, display_name in rental_fields.items():
                value = self._get_money(field)
                Validator.validate_positive_number(value, display_name)

        except Exception as e:
            logger.error(f"Lease option validation error: {str(e)}")
            raise ValueError(f"Lease option validation failed: {str(e)}")
            
    @property
    def total_rent_credits(self) -> Money:
        """Calculate total potential rent credits over option term."""
        monthly_credit = self._get_money('monthly_rent') * self._get_percentage('monthly_rent_credit_percentage')
        total_potential = monthly_credit * self.data.get('option_term_months', 0)
        credit_cap = self._get_money('rent_credit_cap')
        return min(total_potential, credit_cap)

    @property
    def effective_purchase_price(self) -> Money:
        """Calculate effective purchase price after credits."""
        return self._get_money('strike_price') - self.total_rent_credits

    @property
    def option_roi(self) -> Percentage:
        """Calculate ROI on option fee."""
        annual_cf = float(self.annual_cash_flow.dollars)
        option_fee = float(self._get_money('option_consideration_fee').dollars)
        return Percentage((annual_cf / option_fee) * 100) if option_fee > 0 else Percentage(0)

    @safe_calculation(default_value=float('inf'))
    def calculate_breakeven_months(self) -> int:
        """Calculate months to break even on option fee."""
        option_fee = float(self._get_money('option_consideration_fee').dollars)
        monthly_cf = float(self.calculate_monthly_cash_flow().dollars)
        return ceil(option_fee / monthly_cf) if monthly_cf > 0 else float('inf')
    
    def _calculate_type_specific_metrics(self) -> Dict:
        """Calculate metrics specific to lease option analysis."""
        # Calculate NOI
        monthly_income = self._get_money('monthly_rent')
        operating_expenses = self._calculate_operating_expenses()
        monthly_noi = monthly_income - operating_expenses
        
        # Calculate operating expense ratio
        expense_ratio = (float(operating_expenses.dollars) / float(monthly_income.dollars)) * 100 if monthly_income.dollars > 0 else 0.0
        
        # Calculate debt service
        loan_payments = self._calculate_loan_payments()
        
        # Calculate cash flow
        monthly_cash_flow = monthly_noi - loan_payments
        
        return {
            'total_rent_credits': str(self.total_rent_credits),
            'effective_purchase_price': str(self.effective_purchase_price),
            'option_roi': str(self.option_roi),
            'breakeven_months': str(self.calculate_breakeven_months()),
            
            # Core KPIs required for Lease Option
            'noi': str(monthly_noi),
            'monthly_noi': str(monthly_noi),
            'annual_noi': str(monthly_noi * 12),
            'operating_expense_ratio': str(Percentage(expense_ratio)),
            'expense_ratio': str(Percentage(expense_ratio)),
            'monthly_cash_flow': str(monthly_cash_flow),
            'annual_cash_flow': str(monthly_cash_flow * 12)
        }

    @safe_calculation(default_value=Money(0))
    def calculate_total_cash_invested(self) -> Money:
        """
        Calculate total cash invested for Lease Option.
        For lease options, the primary investment is the option consideration fee.
        """
        logger.debug("=== Starting Lease Option Total Cash Invested Calculation ===")
        
        # For Lease Option, the main investment is the option fee
        option_fee = self._get_money('option_consideration_fee')
        logger.debug(f"Option consideration fee: ${float(option_fee.dollars):.2f}")
        
        return option_fee

class LTRAnalysis(Analysis):
    """Long-term rental analysis implementation."""
    
    def __init__(self, data: Dict):
        """Initialize LTR analysis."""
        if data.get('analysis_type') not in ['LTR', 'PadSplit LTR']:
            raise ValueError("Invalid analysis type for LTR analysis")
            
        super().__init__(data)

    def _validate_type_specific_requirements(self) -> None:
        """Validate fields specific to LTR analysis."""
        try:
            # Validate required numeric fields
            ltr_fields = {
                'purchase_price': 'Purchase price',
                'monthly_rent': 'Monthly rent',
                'property_taxes': 'Property taxes',
                'insurance': 'Insurance'
            }
            
            for field, display_name in ltr_fields.items():
                value = self._get_money(field)
                Validator.validate_positive_number(value, display_name)

            # Validate balloon payment fields if present
            if self.data.get('has_balloon_payment'):
                self.validate_balloon_payment()

        except Exception as e:
            logger.error(f"LTR validation error: {str(e)}")
            raise ValueError(f"LTR validation failed: {str(e)}")

    def validate_balloon_payment(self) -> None:
        """Validate balloon payment specific fields."""
        if not self.data.get('has_balloon_payment'):
            return

        try:
            # Validate required balloon fields
            balloon_fields = {
                'balloon_due_date': 'Balloon payment due date',
                'balloon_refinance_ltv_percentage': 'Balloon refinance LTV percentage',
                'balloon_refinance_loan_amount': 'Balloon refinance loan amount',
                'balloon_refinance_loan_interest_rate': 'Balloon refinance interest rate',
                'balloon_refinance_loan_term': 'Balloon refinance term'
            }
            
            Validator.validate_required_fields(self.data, balloon_fields)
            
            # Validate balloon date
            Validator.validate_date_format(self.data['balloon_due_date'], "Balloon due date")
            balloon_date = datetime.fromisoformat(self.data['balloon_due_date'].replace('Z', '+00:00'))
            if balloon_date <= datetime.now():
                raise ValueError("Balloon due date must be in the future")

            # Validate LTV percentage
            ltv = self._get_percentage('balloon_refinance_ltv_percentage')
            Validator.validate_percentage(ltv, "Balloon refinance LTV percentage")

            # Validate refinance loan parameters
            refinance_amount = self._get_money('balloon_refinance_loan_amount')
            Validator.validate_positive_number(refinance_amount, "Balloon refinance loan amount")

            interest_rate = self._get_percentage('balloon_refinance_loan_interest_rate')
            Validator.validate_percentage(interest_rate, "Balloon refinance interest rate", 0, MAX_LOAN_INTEREST_RATE)

            term = self.data.get('balloon_refinance_loan_term', 0)
            if term <= 0 or term > MAX_LOAN_TERM:
                raise ValueError(f"Balloon refinance term must be between 1 and {MAX_LOAN_TERM} months")

        except ValueError as e:
            raise
        except Exception as e:
            raise ValueError(f"Invalid balloon payment parameters: {str(e)}")

    def _calculate_loan_payments(self) -> Money:
        """Calculate total monthly loan payments considering balloon scenarios."""
        try:
            if not self.data.get('has_balloon_payment'):
                return super()._calculate_loan_payments()

            # For balloon scenarios, use original loan payment until balloon date
            now = datetime.now()
            balloon_date = datetime.fromisoformat(self.data['balloon_due_date'].replace('Z', '+00:00'))
            
            if now > balloon_date:
                # Past balloon date, use refinanced terms
                loan_details = LoanDetails(
                    amount=self._get_money('balloon_refinance_loan_amount'),
                    interest_rate=self._get_percentage('balloon_refinance_loan_interest_rate'),
                    term=self.data.get('balloon_refinance_loan_term', 0),
                    is_interest_only=False  # Refinanced balloon typically amortizes
                )
                payment = LoanCalculator.calculate_payment(loan_details)
                self.calculated_metrics['balloon_refinance_payment'] = str(payment)
                return payment
            else:
                # Before balloon date, use original terms
                return super()._calculate_loan_payments()
                
        except Exception as e:
            logger.error(f"Error calculating loan payments: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    @safe_calculation(default_value=Money(0))
    def _calculate_pre_balloon_loan_payments(self) -> Money:
        """Calculate total monthly loan payments before balloon payment."""
        total_payments = Money(0)
        loan_prefixes = ['loan1', 'loan2', 'loan3']
        
        for prefix in loan_prefixes:
            amount = self._get_money(f'{prefix}_loan_amount')
            if amount.dollars > 0:
                payment = self._calculate_single_loan_payment(prefix)
                total_payments += payment
                logger.debug(f"Pre-balloon {prefix} payment: ${payment.dollars:.2f}")
                    
        return total_payments

    @safe_calculation(default_value=Money(0))
    def _calculate_post_balloon_loan_payment(self) -> Money:
        """Calculate monthly loan payment after balloon refinance."""
        if not self.data.get('has_balloon_payment'):
            return Money(0)

        # Calculate refinance payment
        loan_details = LoanDetails(
            amount=self._get_money('balloon_refinance_loan_amount'),
            interest_rate=self._get_percentage('balloon_refinance_loan_interest_rate'),
            term=self.data.get('balloon_refinance_loan_term', 0),
            is_interest_only=False  # Balloon refinances typically amortize
        )
        payment = LoanCalculator.calculate_payment(loan_details)
        
        logger.debug(f"Calculated post-balloon payment: {payment}")
        return payment

    @safe_calculation(default_value=Money(0))
    def calculate_pre_balloon_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow before balloon payment."""
        logger.debug("=== Starting Pre-Balloon Monthly Cash Flow Calculation ===")
        
        # Get income
        monthly_income = self._get_money('monthly_rent')
        logger.debug(f"Monthly income: {monthly_income}")
        
        # Calculate expenses
        operating_expenses = self._calculate_operating_expenses()
        logger.debug(f"Operating expenses: {operating_expenses}")
        
        # Calculate pre-balloon loan payments
        loan_payments = self._calculate_pre_balloon_loan_payments()
        logger.debug(f"Pre-balloon loan payments: {loan_payments}")
        
        # Calculate final cash flow
        cash_flow = monthly_income - operating_expenses - loan_payments
        logger.debug(f"Final pre-balloon monthly cash flow: {cash_flow}")
        
        return cash_flow

    @safe_calculation(default_value=0)
    def _calculate_balloon_years(self) -> float:
        """Calculate the number of years between now and balloon date."""
        balloon_date = datetime.fromisoformat(self.data['balloon_due_date'].replace('Z', '+00:00'))
        today = datetime.now()
        return max(0, (balloon_date.year - today.year) + 
                 (balloon_date.month - today.month) / 12)

    @safe_calculation(default_value=0.0)
    def _apply_annual_increase(self, base_value: float, years: float, 
                             increase_rate: float = DEFAULT_ANNUAL_INCREASE_RATE) -> float:
        """Apply annual percentage increase to a value over specified years."""
        return base_value * (1 + increase_rate) ** years

    @safe_calculation(default_value={})
    def _calculate_post_balloon_values(self) -> Dict:
        """Calculate post-balloon values with annual increases."""
        years = self._calculate_balloon_years()
        
        # Calculate increased values
        post_balloon_rent = self._apply_annual_increase(
            self._get_money('monthly_rent').dollars,
            years
        )
        post_balloon_taxes = self._apply_annual_increase(
            self._get_money('property_taxes').dollars,
            years
        )
        post_balloon_insurance = self._apply_annual_increase(
            self._get_money('insurance').dollars,
            years
        )
        
        # Create Money objects for increased values
        post_balloon_values = {
            'monthly_rent': Money(post_balloon_rent),
            'property_taxes': Money(post_balloon_taxes),
            'insurance': Money(post_balloon_insurance)
        }
        
        # Calculate percentage-based expenses using new rent
        rent_money = post_balloon_values['monthly_rent']
        post_balloon_values.update({
            'management_fee': rent_money * self._get_percentage('management_fee_percentage'),
            'capex': rent_money * self._get_percentage('capex_percentage'),
            'vacancy': rent_money * self._get_percentage('vacancy_percentage'),
            'repairs': rent_money * self._get_percentage('repairs_percentage')
        })
        
        return post_balloon_values

    @safe_calculation(default_value=Money(0))
    def _calculate_post_balloon_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow after balloon refinance with increased values."""
        # Get increased values
        post_balloon_values = self._calculate_post_balloon_values()
        
        # Calculate income
        monthly_income = post_balloon_values.get('monthly_rent', self._get_money('monthly_rent'))
        
        # Calculate operating expenses with increased values
        operating_expenses = sum([
            post_balloon_values.get('property_taxes', self._get_money('property_taxes')),
            post_balloon_values.get('insurance', self._get_money('insurance')),
            self._get_money('hoa_coa_coop'),
            post_balloon_values.get('management_fee', Money(0)),
            post_balloon_values.get('capex', Money(0)),
            post_balloon_values.get('vacancy', Money(0)),
            post_balloon_values.get('repairs', Money(0))
        ], Money(0))
        
        # Get loan payment
        loan_payment = self._calculate_post_balloon_loan_payment()
        
        logger.debug(f"""
            Post-Balloon Cash Flow Calculation (with increases):
            Monthly Income: {monthly_income}
            Operating Expenses: {operating_expenses}
            Loan Payment: {loan_payment}
            Expected Cash Flow: {monthly_income - operating_expenses - loan_payment}
        """)
        
        return monthly_income - operating_expenses - loan_payment

    @safe_calculation(default_value=Money(0))
    def calculate_balloon_refinance_costs(self) -> Money:
        """Calculate total costs associated with balloon payment refinance."""
        if not self.data.get('has_balloon_payment'):
            return Money(0)

        return sum([
            self._get_money('balloon_refinance_loan_down_payment'),
            self._get_money('balloon_refinance_loan_closing_costs')
        ], Money(0))

    def _calculate_type_specific_metrics(self) -> Dict:
        """Calculate metrics specific to LTR analysis."""
        metrics = {}
        
        # Add loan payment metrics
        for prefix in ['loan1', 'loan2', 'loan3']:
            amount = self._get_money(f'{prefix}_loan_amount')
            if amount.dollars > 0:
                self._calculate_single_loan_payment(prefix)

        # Calculate monthly NOI
        monthly_income = self._get_money('monthly_rent')
        operating_expenses = self._calculate_operating_expenses()
        monthly_noi = monthly_income - operating_expenses
        
        # Calculate loan payments for debt service
        total_loan_payment = self._calculate_loan_payments()
        
        # Calculate DSCR using the centralized financial calculator
        dscr = FinancialCalculator.calculate_dscr(
            noi=monthly_noi,
            debt_service=total_loan_payment
        )
        
        # Calculate operating expense ratio
        expense_ratio = (float(operating_expenses.dollars) / float(monthly_income.dollars)) * 100 if monthly_income.dollars > 0 else 0.0
        
        # Calculate cap rate using the centralized financial calculator
        purchase_price = self._get_money('purchase_price')
        annual_noi = monthly_noi * 12
        cap_rate = FinancialCalculator.calculate_cap_rate(
            annual_noi=annual_noi,
            property_value=purchase_price
        )
        
        # Add standard KPI metrics
        metrics.update({
            'noi': str(monthly_noi),
            'monthly_noi': str(monthly_noi),
            'annual_noi': str(monthly_noi * 12),
            'dscr': str(dscr),
            'cap_rate': str(cap_rate),
            'operating_expense_ratio': str(Percentage(expense_ratio)),
            'expense_ratio': str(Percentage(expense_ratio))
        })

        # Only calculate balloon-related metrics if balloon payment is enabled
        if self.data.get('has_balloon_payment'):
            # Calculate pre-balloon metrics
            pre_balloon_monthly_cf = self.calculate_pre_balloon_monthly_cash_flow()
            pre_balloon_payment = self._calculate_pre_balloon_loan_payments()
            
            # Calculate post-balloon metrics
            post_balloon_monthly_cf = self._calculate_post_balloon_monthly_cash_flow()
            post_balloon_payment = self._calculate_post_balloon_loan_payment()
            
            # Calculate payment difference
            payment_difference = post_balloon_payment - pre_balloon_payment
            
            # Add balloon-specific metrics
            metrics.update({
                'pre_balloon_monthly_cash_flow': str(pre_balloon_monthly_cf),
                'pre_balloon_annual_cash_flow': str(pre_balloon_monthly_cf * 12),
                'post_balloon_monthly_cash_flow': str(post_balloon_monthly_cf),
                'post_balloon_annual_cash_flow': str(post_balloon_monthly_cf * 12),
                'pre_balloon_monthly_payment': str(pre_balloon_payment),
                'post_balloon_monthly_payment': str(post_balloon_payment),
                'monthly_payment_difference': str(payment_difference),
                'balloon_refinance_costs': str(self.calculate_balloon_refinance_costs())
            })
            
            # Add post-balloon metrics...
            # Calculate post-balloon values with annual increases
            post_balloon_values = self._calculate_post_balloon_values()

            # Extract key post-balloon values
            post_balloon_rent = post_balloon_values.get('monthly_rent', monthly_income)
            post_balloon_taxes = post_balloon_values.get('property_taxes', self._get_money('property_taxes'))
            post_balloon_insurance = post_balloon_values.get('insurance', self._get_money('insurance'))

            # Calculate years to balloon
            balloon_years = self._calculate_balloon_years()

            # Add post-balloon detail metrics
            metrics.update({
                'post_balloon_monthly_rent': str(post_balloon_rent),
                'post_balloon_property_taxes': str(post_balloon_taxes),
                'post_balloon_insurance': str(post_balloon_insurance),
                'balloon_years_from_now': str(balloon_years),
                'estimated_annual_increase': str(Percentage(DEFAULT_ANNUAL_INCREASE_RATE * 100)),
                'post_balloon_cap_rate': str(Percentage(
                    (float(post_balloon_monthly_cf.dollars) * 12 / float(purchase_price.dollars)) * 100
                    if purchase_price.dollars > 0 else 0.0
                )),
                'refinance_dscr': str(
                    float(post_balloon_monthly_cf.dollars) / float(post_balloon_payment.dollars)
                    if post_balloon_payment.dollars > 0 else 0.0
                )
            })

        return metrics

class BRRRRAnalysis(Analysis):
    """BRRRR strategy analysis implementation."""
    
    def __init__(self, data: Dict):
        """Initialize BRRRR analysis."""
        if data.get('analysis_type') not in ['BRRRR', 'PadSplit BRRRR']:
            raise ValueError("Invalid analysis type for BRRRR analysis")
            
        super().__init__(data)

    def _validate_type_specific_requirements(self) -> None:
        """Validate fields specific to BRRRR analysis."""
        try:
            # Validate required BRRRR fields
            required_fields = {
                'purchase_price': 'Purchase price',
                'after_repair_value': 'After repair value',
                'renovation_costs': 'Renovation costs',
                'renovation_duration': 'Renovation duration',
                'initial_loan_amount': 'Initial loan amount',
                'refinance_loan_amount': 'Refinance loan amount'
            }
            
            for field, display_name in required_fields.items():
                if field == 'renovation_duration':
                    value = self.data.get(field, 0)
                    if value <= 0 or value > MAX_RENOVATION_DURATION:
                        raise ValueError(f"{display_name} must be between 1 and {MAX_RENOVATION_DURATION} months")
                else:
                    value = self._get_money(field)
                    Validator.validate_positive_number(value, display_name)

            # Validate loan parameters
            self._validate_loan_parameters('initial_loan', is_initial=True)
            self._validate_loan_parameters('refinance_loan')

            # Validate ARV is greater than purchase price + renovation costs
            arv = self._get_money('after_repair_value')
            total_cost = self._get_money('purchase_price') + self._get_money('renovation_costs')
            if arv <= total_cost:
                raise ValueError("After repair value must be greater than purchase price plus renovation costs")
            
            # Validate initial_interest_only is boolean if present
            initial_interest_only = self.data.get('initial_interest_only')
            if initial_interest_only is not None and not isinstance(initial_interest_only, bool):
                try:
                    # Convert string values to boolean
                    if isinstance(initial_interest_only, str):
                        self.data['initial_interest_only'] = initial_interest_only.lower() in ('true', '1')
                    else:
                        self.data['initial_interest_only'] = bool(initial_interest_only)
                except (ValueError, TypeError):
                    raise ValueError("initial_interest_only must be a boolean value")

        except Exception as e:
            logger.error(f"BRRRR validation error: {str(e)}")
            raise ValueError(f"BRRRR validation failed: {str(e)}")

    def _validate_loan_parameters(self, loan_prefix: str, is_initial: bool = False) -> None:
        """Validate loan parameters for a given loan type."""
        try:
            # Validate loan amount
            loan_amount = self._get_money(f'{loan_prefix}_amount')
            Validator.validate_positive_number(loan_amount, f"{loan_prefix} amount")

            # Validate interest rate
            interest_rate = self._get_percentage(f'{loan_prefix}_interest_rate')
            Validator.validate_percentage(interest_rate, f"{loan_prefix} interest rate", 0, MAX_LOAN_INTEREST_RATE)

            # Validate loan term
            loan_term = self.data.get(f'{loan_prefix}_term', 0)
            if is_initial:
                if loan_term <= 0 or loan_term > MAX_RENOVATION_DURATION:  # Initial loan typically 3-24 months
                    raise ValueError(f"Initial loan term must be between 1 and {MAX_RENOVATION_DURATION} months")
            else:
                if loan_term <= 0 or loan_term > MAX_LOAN_TERM:  # Long-term loan typically up to 30 years
                    raise ValueError(f"Refinance loan term must be between 1 and {MAX_LOAN_TERM} months")

        except Exception as e:
            logger.error(f"Loan validation error: {str(e)}")
            raise ValueError(f"Loan validation failed: {str(e)}")

    def _calculate_loan_payments(self) -> Money:
        """Calculate total monthly loan payments for BRRRR."""
        try:
            # For BRRRR, we calculate both initial and refinance payments
            # Store initial loan payment
            initial_loan_details = LoanDetails(
                amount=self._get_money('initial_loan_amount'),
                interest_rate=self._get_percentage('initial_loan_interest_rate'),
                term=self.data.get('initial_loan_term', 0),
                is_interest_only=self.data.get('initial_interest_only', False)
            )
            
            initial_payment = LoanCalculator.calculate_payment(initial_loan_details)
            self.calculated_metrics['initial_loan_payment'] = str(initial_payment)
            
            # Store refinance payment
            refinance_loan_details = LoanDetails(
                amount=self._get_money('refinance_loan_amount'),
                interest_rate=self._get_percentage('refinance_loan_interest_rate'),
                term=self.data.get('refinance_loan_term', 0),
                is_interest_only=False  # Refinance loans are always amortizing
            )
            
            refinance_payment = LoanCalculator.calculate_payment(refinance_loan_details)
            self.calculated_metrics['refinance_loan_payment'] = str(refinance_payment)
            
            # Return refinance payment for monthly cash flow calculation
            return refinance_payment
        
        except Exception as e:
            logger.error(f"Error calculating BRRRR loan payments: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    @property
    @safe_calculation(default_value=Money(0))
    def holding_costs(self) -> Money:
        """
        Calculate holding costs during renovation period.
        
        Holding costs include property fixed expenses and loan interest during renovation:
        - Property taxes
        - Insurance
        - HOA/COA fees
        - Interest-only payment on initial loan
        
        These costs are multiplied by the renovation duration to get total holding costs.
        """
        # Calculate monthly fixed expenses
        fixed_expenses = sum([
            self._get_money('property_taxes'),
            self._get_money('insurance'),
            self._get_money('hoa_coa_coop')
        ], Money(0))
        
        # Calculate interest-only payment on initial loan
        initial_loan_amount = self._get_money('initial_loan_amount')
        initial_loan_rate = self._get_percentage('initial_loan_interest_rate')
        
        # Calculate monthly interest (don't use full payment calculation for clarity)
        monthly_interest = Money(0)
        if initial_loan_amount.dollars > 0 and initial_loan_rate.value > 0:
            monthly_interest = initial_loan_amount * (initial_loan_rate / Percentage(1200))  # Convert to monthly rate
            logger.debug(f"Monthly interest on initial loan: ${float(monthly_interest.dollars):.2f}")
        
        # Total monthly holding costs
        monthly_costs = fixed_expenses + monthly_interest
        logger.debug(f"Total monthly holding costs: ${float(monthly_costs.dollars):.2f}")
        
        # Multiply by renovation duration
        renovation_duration = self.data.get('renovation_duration', 0)
        total_holding_costs = monthly_costs * renovation_duration
        logger.debug(f"Total holding costs over {renovation_duration} months: ${float(total_holding_costs.dollars):.2f}")
        
        return total_holding_costs

    @property
    @safe_calculation(default_value=Money(0))
    def total_project_costs(self) -> Money:
        """Calculate total project costs including holding costs."""
        return sum([
            self._get_money('purchase_price'),
            self._get_money('renovation_costs'),
            self.holding_costs,
            self._get_money('initial_loan_closing_costs'),
            self._get_money('refinance_loan_closing_costs')
        ], Money(0))

    @safe_calculation(default_value=Money(0))
    def calculate_total_cash_invested(self) -> Money:
        """
        Calculate total cash invested in BRRRR project accounting for cash-out refinance.
        Returns the true out-of-pocket costs after considering cash recouped in refinance.
        
        Note: This value can be negative if the refinance pulls out more cash than was
        initially invested. A negative value represents cash extracted beyond the
        initial investment - effectively profit while still owning the asset.
        """
        logger.debug("=== Starting BRRRR Total Cash Invested Calculation ===")
        
        # Step 1: Calculate initial investment (before financing)
        initial_investment = sum([
            self._get_money('purchase_price'),        # Purchase price
            self._get_money('renovation_costs'),      # Renovation costs
            self.holding_costs,                       # Holding costs during renovation
            self._get_money('initial_loan_closing_costs'), # Initial loan costs
        ], Money(0))
        
        # Add furnishing costs for PadSplit
        if 'PadSplit' in self.data.get('analysis_type', ''):
            initial_investment += self._get_money('furnishing_costs')
            
        logger.debug(f"Initial gross investment: ${float(initial_investment.dollars):.2f}")
        
        # Step 2: Subtract initial financing to get out-of-pocket
        initial_loan_amount = self._get_money('initial_loan_amount')
        initial_out_of_pocket = initial_investment - initial_loan_amount
        
        # Allow negative values to represent over-leveraged acquisition
        logger.debug(f"Initial out-of-pocket after financing: ${float(initial_out_of_pocket.dollars):.2f}")
        
        # Step 3: Calculate cash recouped from refinance
        refinance_loan_amount = self._get_money('refinance_loan_amount')
        refinance_closing_costs = self._get_money('refinance_loan_closing_costs')
        
        cash_recouped = refinance_loan_amount - initial_loan_amount - refinance_closing_costs
        # Allow negative values to represent refinance shortfall
        logger.debug(f"Cash recouped from refinance: ${float(cash_recouped.dollars):.2f}")
        
        # Step 4: Calculate final out-of-pocket investment
        final_investment = initial_out_of_pocket - cash_recouped
        # Allow negative values to represent cash-out beyond initial investment
        logger.debug(f"Final out-of-pocket investment after refinance: ${float(final_investment.dollars):.2f}")
        if final_investment.dollars < 0:
            logger.debug("Negative cash invested indicates cash extracted beyond initial investment")
        
        return final_investment

    @safe_calculation(default_value=Money(0))
    def calculate_mao(self) -> Money:
        """Calculate Maximum Allowable Offer."""
        arv = self._get_money('after_repair_value')
        renovation_costs = self._get_money('renovation_costs')
        holding_costs = self.holding_costs
        closing_costs = sum([
            self._get_money('initial_loan_closing_costs'),
            self._get_money('refinance_loan_closing_costs')
        ], Money(0))
        
        # Use the centralized financial calculator
        return FinancialCalculator.calculate_mao(
            arv=arv,
            renovation_costs=renovation_costs,
            holding_costs=holding_costs,
            closing_costs=closing_costs,
            ltv_percentage=75,  # Typical BRRRR wants 75% ARV
            max_cash_left=Money(0)  # No cash left in the deal for BRRRR
        )

    @property
    def cash_on_cash_return(self) -> Union[Percentage, str]:
        """
        Calculate Cash on Cash return.
        
        Returns:
            Percentage: The calculated cash on cash return percentage
            str: "Infinite" if the cash invested is zero or negative
        """
        cash_invested = self.calculate_total_cash_invested()
        annual_cf = float(self.annual_cash_flow.dollars)
        
        # Special case: Zero or negative cash invested means infinite return
        if cash_invested.dollars <= 0:
            logger.debug("Cash invested is zero or negative, returning 'Infinite' for cash-on-cash return")
            return "Infinite"
        
        # Normal calculation
        return Percentage((annual_cf / float(cash_invested.dollars)) * 100)

    def _calculate_loan_payments(self) -> Money:
        """
        Calculate total monthly loan payments for BRRRR.
        
        For BRRRR analyses, we always use the refinance loan payment for cash flow calculations,
        as this represents the permanent financing scenario for the property.
        """
        try:
            # For BRRRR, we first calculate and store initial loan payment for reference
            initial_loan_details = LoanDetails(
                amount=self._get_money('initial_loan_amount'),
                interest_rate=self._get_percentage('initial_loan_interest_rate'),
                term=self.data.get('initial_loan_term', 0),
                is_interest_only=self.data.get('initial_interest_only', False)
            )
            
            initial_payment = LoanCalculator.calculate_payment(initial_loan_details)
            self.calculated_metrics['initial_loan_payment'] = str(initial_payment)
            logger.debug(f"Initial loan payment: ${float(initial_payment.dollars):.2f} (for reference only)")
            
            # Calculate and store refinance payment - this is what we use for cash flow
            refinance_loan_details = LoanDetails(
                amount=self._get_money('refinance_loan_amount'),
                interest_rate=self._get_percentage('refinance_loan_interest_rate'),
                term=self.data.get('refinance_loan_term', 0),
                is_interest_only=False  # Refinance loans are always amortizing
            )
            
            refinance_payment = LoanCalculator.calculate_payment(refinance_loan_details)
            self.calculated_metrics['refinance_loan_payment'] = str(refinance_payment)
            logger.debug(f"Refinance loan payment: ${float(refinance_payment.dollars):.2f} (used for cash flow)")
            
            # Always return refinance payment for monthly cash flow calculation
            # This is the post-renovation permanent financing scenario
            return refinance_payment
        
        except Exception as e:
            logger.error(f"Error calculating BRRRR loan payments: {str(e)}")
            logger.error(traceback.format_exc())
            return Money(0)

    def _calculate_type_specific_metrics(self) -> Dict:
        """Calculate metrics specific to BRRRR analysis."""
        # Ensure loan payments are calculated first
        self._calculate_loan_payments()
        
        # Calculate BRRRR-specific metrics
        arv = self._get_money('after_repair_value')
        purchase_price = self._get_money('purchase_price')
        total_costs = sum([
            purchase_price,
            self._get_money('renovation_costs')
        ], Money(0))
        
        # Initial loan amount
        initial_loan = self._get_money('initial_loan_amount')
        
        # Refinance calculation
        refinance_loan = self._get_money('refinance_loan_amount')
        refinance_closing_costs = self._get_money('refinance_loan_closing_costs')
        
        # Calculate cash recouped
        cash_recouped = refinance_loan - initial_loan - refinance_closing_costs
        cash_recouped = Money(max(0, float(cash_recouped.dollars)))  # Ensure non-negative

        # Calculate final cash invested
        final_cash_invested = self.calculate_total_cash_invested()
        
        # Calculate monthly NOI
        monthly_income = self._get_money('monthly_rent')
        operating_expenses = self._calculate_operating_expenses()
        monthly_noi = monthly_income - operating_expenses
        
        # Calculate DSCR
        debt_service = self._calculate_loan_payments()
        dscr = float(monthly_noi.dollars) / float(debt_service.dollars) if debt_service.dollars > 0 else 0.0
        
        # Calculate operating expense ratio
        expense_ratio = (float(operating_expenses.dollars) / float(monthly_income.dollars)) * 100 if monthly_income.dollars > 0 else 0.0
        
        # Calculate cap rate
        cap_rate = (float(monthly_noi.dollars) * 12 / float(arv.dollars)) * 100 if arv.dollars > 0 else 0.0
        
        return {
            # BRRRR-specific metrics
            'equity_captured': str(arv - total_costs),
            'cash_recouped': str(cash_recouped),
            'holding_costs': str(self.holding_costs),
            'total_project_costs': str(self.total_project_costs),
            'final_cash_invested': str(final_cash_invested),
            'maximum_allowable_offer': str(self.calculate_mao()),
            
            # Core KPIs required for all types
            'noi': str(monthly_noi),
            'monthly_noi': str(monthly_noi),  # Add both formats to ensure compatibility
            'annual_noi': str(monthly_noi * 12),
            'cap_rate': str(Percentage(cap_rate)),
            'dscr': str(dscr),
            'operating_expense_ratio': str(Percentage(expense_ratio)),
            'expense_ratio': str(Percentage(expense_ratio))  # Add alias for compatibility
        }

class MultiFamilyAnalysis(Analysis):
    """Multi-Family analysis implementation."""
    
    def __init__(self, data: Dict):
        """Initialize multi-family analysis."""
        if data.get('analysis_type') != 'Multi-Family':
            raise ValueError("Invalid analysis type for multi-family analysis")
            
        super().__init__(data)

    def _validate_type_specific_requirements(self) -> None:
        """Validate fields specific to multi-family analysis."""
        try:
            # Validate required numeric fields that must be greater than 0
            required_positive_fields = {
                'total_units': 'Total units',
                'floors': 'Number of floors',
                'property_taxes': 'Property taxes',
                'insurance': 'Insurance'
            }
            
            # Fields that must be present but can be 0
            required_fields = {
                'elevator_maintenance': 'Elevator maintenance',
                'other_income': 'Other income',
                'hoa_coa_coop': 'HOA/COA/COOP fees'
            }
            
            for field, display_name in required_positive_fields.items():
                if field in ['total_units', 'floors']:
                    value = self.data.get(field, 0)
                    Validator.validate_positive_number(value, display_name)
                else:
                    value = self._get_money(field)
                    Validator.validate_positive_number(value, display_name)

            # Just verify these fields exist (can be 0)
            Validator.validate_required_fields(self.data, required_fields)

            # Validate unit types
            unit_types = json.loads(self.data.get('unit_types', '[]'))
            if not unit_types:
                raise ValueError("At least one unit type must be defined")
            
            total_units = sum(ut.get('count', 0) for ut in unit_types)
            if total_units != self.data.get('total_units', 0):
                raise ValueError("Sum of units must match total units")

            total_occupied = sum(ut.get('occupied', 0) for ut in unit_types)
            if total_occupied != self.data.get('occupied_units', 0):
                raise ValueError("Sum of occupied units must match total occupied units")

            # Validate each unit type has required fields
            for unit_type in unit_types:
                if not all(key in unit_type for key in ['type', 'count', 'occupied', 'square_footage', 'rent']):
                    raise ValueError("Invalid unit type structure")
                if unit_type['rent'] <= 0:
                    raise ValueError("Unit rent must be greater than 0")
                if unit_type['count'] <= 0:
                    raise ValueError("Unit count must be greater than 0")
                if unit_type['occupied'] < 0 or unit_type['occupied'] > unit_type['count']:
                    raise ValueError("Occupied units cannot exceed total units for a type")

        except Exception as e:
            logger.error(f"Multi-family validation error: {str(e)}")
            raise ValueError(f"Multi-family validation failed: {str(e)}")

    @property
    @safe_calculation(default_value=Money(0))
    def gross_potential_rent(self) -> Money:
        """
        Calculate gross potential rent from all units.
        This is the total rent if all units were occupied.
        """
        try:
            unit_types = json.loads(self.data.get('unit_types', '[]'))
            total = sum(ut.get('count', 0) * ut.get('rent', 0) for ut in unit_types)
            logger.debug(f"Calculated gross potential rent: ${total:.2f}")
            return Money(total)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error calculating gross potential rent: {str(e)}")
            return Money(0)

    @property
    @safe_calculation(default_value=Money(0))
    def actual_gross_income(self) -> Money:
        """
        Calculate actual gross income including other income.
        This uses occupied units only plus any other property income.
        """
        try:
            # Get occupied unit rent
            unit_types = json.loads(self.data.get('unit_types', '[]'))
            occupied_rent = sum(ut.get('occupied', 0) * ut.get('rent', 0) for ut in unit_types)
            
            # Add other income
            other_income = self._get_money('other_income')
            
            actual_income = Money(occupied_rent) + other_income
            logger.debug(f"Calculated actual gross income: ${float(actual_income.dollars):.2f}")
            return actual_income
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error calculating actual gross income: {str(e)}")
            return Money(0)

    @property
    @safe_calculation(default_value=Money(0))
    def net_operating_income(self) -> Money:
        """Calculate NOI (before debt service)."""
        # Get effective gross income
        vacancy_loss = self.gross_potential_rent * self._get_percentage('vacancy_percentage')
        effective_gross_income = self.gross_potential_rent - vacancy_loss + self._get_money('other_income')
        
        # Calculate operating expenses
        operating_expenses = self._calculate_operating_expenses()
        
        return effective_gross_income - operating_expenses

    @property
    @safe_calculation(default_value=Percentage(0))
    def cap_rate(self) -> Percentage:
        """Calculate capitalization rate."""
        purchase_price = self._get_money('purchase_price')
        if purchase_price.dollars <= 0:
            return Percentage(0)
        
        return Percentage((float(self.net_operating_income.dollars) * 12 / 
                         float(purchase_price.dollars)) * 100)

    @property
    @safe_calculation(default_value=Percentage(0))
    def occupancy_rate(self) -> Percentage:
        """Calculate current occupancy rate as percentage."""
        total_units = self.data.get('total_units', 0)
        occupied_units = self.data.get('occupied_units', 0)
        
        if total_units <= 0:
            return Percentage(0)
            
        return Percentage((occupied_units / total_units) * 100)

    @property
    @safe_calculation(default_value=Money(0))
    def price_per_unit(self) -> Money:
        """Calculate purchase price per unit."""
        total_units = self.data.get('total_units', 0)
        purchase_price = self._get_money('purchase_price')
        
        if total_units <= 0:
            return Money(0)
            
        return Money(float(purchase_price.dollars) / total_units)

    @property
    @safe_calculation(default_value=0.0)
    def gross_rent_multiplier(self) -> float:
        """Calculate Gross Rent Multiplier."""
        annual_rent = float(self.gross_potential_rent.dollars) * 12
        if annual_rent <= 0:
            return 0
        
        return float(self._get_money('purchase_price').dollars) / annual_rent

    def _calculate_operating_expenses(self) -> Money:
        """
        Calculate total monthly operating expenses for multi-family property.
        Includes fixed expenses, percentage-based expenses, and multi-family specific expenses.
        """
        # Fixed expenses
        fixed_expenses = sum([
            self._get_money('property_taxes'),
            self._get_money('insurance'),
            self._get_money('hoa_coa_coop'),
        ], Money(0))
        
        # Multi-family specific expenses
        multi_family_expenses = sum([
            self._get_money('common_area_maintenance'),
            self._get_money('elevator_maintenance'),
            self._get_money('staff_payroll'),
            self._get_money('trash_removal'),
            self._get_money('common_utilities')
        ], Money(0))
        
        # Percentage-based expenses (based on gross potential rent)
        rent_based_expenses = sum([
            self.gross_potential_rent * self._get_percentage('management_fee_percentage'),
            self.gross_potential_rent * self._get_percentage('capex_percentage'),
            self.gross_potential_rent * self._get_percentage('vacancy_percentage'),
            self.gross_potential_rent * self._get_percentage('repairs_percentage')
        ], Money(0))
        
        total_expenses = fixed_expenses + multi_family_expenses + rent_based_expenses
        logger.debug(f"Total multi-family operating expenses: ${float(total_expenses.dollars):.2f}")
        
        return total_expenses

    def _calculate_operating_expense_ratio(self) -> float:
        """Calculate operating expense ratio as a decimal (not percentage)."""
        operating_expenses = self._calculate_operating_expenses()
        gross_rent = self.gross_potential_rent
        
        if gross_rent.dollars <= 0:
            return 0.0
            
        return float(operating_expenses.dollars) / float(gross_rent.dollars)
    
    def _calculate_type_specific_metrics(self) -> Dict:
        """
        Calculate metrics specific to multi-family analysis.
        Includes both property-level and per-unit metrics.
        """
        # Get basic property data
        total_units = float(self.data.get('total_units', 1))
        
        # Calculate NOI and per-unit metrics
        monthly_noi = self.net_operating_income
        noi_per_unit = monthly_noi.dollars / total_units if total_units > 0 else 0
        
        # Calculate debt service for DSCR
        loan_payments = self._calculate_loan_payments()
        dscr = float(monthly_noi.dollars) / float(loan_payments.dollars) if loan_payments.dollars > 0 else 0.0
        
        # Calculate expense ratio
        expense_ratio = self._calculate_operating_expense_ratio()
        
        # Add multi-family specific metrics
        multi_family_metrics = {
            # Income metrics
            'gross_potential_rent': str(self.gross_potential_rent),
            'actual_gross_income': str(self.actual_gross_income),
            'other_income': str(self._get_money('other_income')),
            
            # NOI metrics
            'net_operating_income': str(monthly_noi),
            'monthly_noi': str(monthly_noi),
            'noi_per_unit': str(Money(noi_per_unit)),  # Per unit for multi-family
            'noi': str(Money(noi_per_unit)),  # Alias for noi_per_unit 
            'annual_noi': str(monthly_noi * 12),
            
            # Return metrics
            'cap_rate': str(self.cap_rate),
            'dscr': str(dscr),
            'gross_rent_multiplier': str(self.gross_rent_multiplier),
            
            # Property metrics
            'price_per_unit': str(self.price_per_unit),
            'occupancy_rate': str(self.occupancy_rate),
            'expense_ratio': str(Percentage(expense_ratio * 100)),
            'operating_expense_ratio': str(Percentage(expense_ratio * 100)),
            'total_units': str(self.data.get('total_units', 0)),
            'occupied_units': str(self.data.get('occupied_units', 0)),
            'vacancy_units': str(self.data.get('total_units', 0) - self.data.get('occupied_units', 0))
        }
        
        # Calculate unit type metrics
        try:
            unit_types = json.loads(self.data.get('unit_types', '[]'))
            unit_metrics = {
                'unit_type_summary': {
                    ut['type']: {
                        'count': ut['count'],
                        'occupied': ut['occupied'],
                        'vacancy': ut['count'] - ut['occupied'],
                        'vacancy_rate': (1 - (ut['occupied'] / ut['count'])) * 100 if ut['count'] > 0 else 0,
                        'avg_sf': ut['square_footage'],
                        'rent': str(Money(ut['rent'])),
                        'rent_per_sf': str(Money(ut['rent'] / ut['square_footage'])) if ut['square_footage'] > 0 else str(Money(0)),
                        'total_potential_rent': str(Money(ut['rent'] * ut['count'])),
                        'actual_rent': str(Money(ut['rent'] * ut['occupied']))
                    } for ut in unit_types
                }
            }
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            logger.error(f"Error processing unit types: {str(e)}")
            unit_metrics = {'unit_type_summary': {}}
        
        return {**multi_family_metrics, **unit_metrics}

def create_analysis(data: Dict) -> Analysis:
    """Factory function to create appropriate analysis instance"""
    analysis_registry = {
        'LTR': LTRAnalysis,
        'BRRRR': BRRRRAnalysis,
        'PadSplit LTR': LTRAnalysis,
        'PadSplit BRRRR': BRRRRAnalysis,
        'Lease Option': LeaseOptionAnalysis,
        'Multi-Family': MultiFamilyAnalysis
    }
    
    analysis_type = data.get('analysis_type')
    analysis_class = analysis_registry.get(analysis_type)
    
    if not analysis_class:
        raise ValueError(f"Invalid analysis type: {analysis_type}")
        
    return analysis_class(data)
