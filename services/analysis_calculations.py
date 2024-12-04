from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment
from utils.calculators import AmortizationCalculator
import logging

logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

@dataclass
class Loan:
    """Represents a loan with its terms and payments"""
    def __init__(self, amount, interest_rate, term, down_payment, closing_costs, 
                 is_interest_only: bool = False, name: Optional[str] = None,
                 monthly_payment: Optional[str] = None):
        self.amount = Money(amount)
        self.interest_rate = Percentage(interest_rate)
        self.term = int(float(str(term))) if term else 0
        self.down_payment = Money(down_payment)
        self.closing_costs = Money(closing_costs)
        self.is_interest_only = bool(is_interest_only)
        self.name = name
        self._monthly_payment = Money(monthly_payment) if monthly_payment else None

    def _validate_and_convert_types(self):
        try:
            self.amount = Money(self.amount)
            self.interest_rate = Percentage(self.interest_rate)
            self.term = int(float(str(self.term)))
            self.down_payment = Money(self.down_payment)
            self.closing_costs = Money(self.closing_costs)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid loan parameters: {str(e)}")

    def calculate_payment(self) -> MonthlyPayment:
        if self._monthly_payment:
            return MonthlyPayment(
                total=self._monthly_payment,
                principal=Money(0),  # We don't have this breakdown for stored payments
                interest=Money(0)    # We don't have this breakdown for stored payments
            )
            
        if self.is_interest_only:
            monthly_interest = self.amount * (self.interest_rate.as_decimal() / Decimal('12'))
            return MonthlyPayment(
                total=monthly_interest,
                principal=Money(0),
                interest=monthly_interest
            )
        return AmortizationCalculator.calculate_monthly_payment(
            self.amount, 
            self.interest_rate, 
            self.term
        )

    @property
    def total_initial_costs(self) -> Money:
        return self.down_payment + self.closing_costs

@dataclass
class PropertyDetails:
    """Represents property details"""
    def __init__(self, data: Dict):
        self.address = data.get('property_address')
        self.square_footage = int(data.get('home_square_footage', 0))
        self.lot_size = int(data.get('lot_square_footage', 0))
        self.year_built = int(data.get('year_built', 0))

@dataclass
class PurchaseDetails:
    """Purchase and renovation details"""
    def __init__(self, data: Dict):
        self.purchase_price = Money(data.get('purchase_price', 0))
        self.after_repair_value = Money(data.get('after_repair_value', 0))
        self.renovation_costs = Money(data.get('renovation_costs', 0))
        self.renovation_duration = int(data.get('renovation_duration', 0))
        self.cash_to_seller = Money(data.get('cash_to_seller', 0))
        self.closing_costs = Money(data.get('closing_costs', 0))
        self.assignment_fee = Money(data.get('assignment_fee', 0))
        self.marketing_costs = Money(data.get('marketing_costs', 0))

class OperatingExpenses:
    """Base operating expenses calculations"""
    def __init__(self, data: Dict):
        self.monthly_rent = Money(data.get('monthly_rent', 0))
        self.property_taxes = Money(data.get('property_taxes', 0))
        self.insurance = Money(data.get('insurance', 0))
        self.hoa_coa_coop = Money(data.get('hoa_coa_coop', 0))
        self.management_percentage = Percentage(data.get('management_percentage', 0))
        self.capex_percentage = Percentage(data.get('capex_percentage', 0))
        self.vacancy_percentage = Percentage(data.get('vacancy_percentage', 0))
        self.repairs_percentage = Percentage(data.get('repairs_percentage', 0))

        # Store the total if provided, otherwise calculate it
        self._total = Money(data.get('total_operating_expenses', 0))

    @property
    def management_fee(self) -> Money:
        return self.monthly_rent * self.management_percentage

    @property
    def capex(self) -> Money:
        return self.monthly_rent * self.capex_percentage

    @property
    def vacancy(self) -> Money:
        return self.monthly_rent * self.vacancy_percentage

    @property
    def repairs(self) -> Money:
        return self.monthly_rent * self.repairs_percentage

    @property
    def total(self) -> Money:
        if self._total.dollars > 0:
            return self._total
        return sum([
            self.property_taxes,
            self.insurance,
            self.hoa_coa_coop,
            self.management_fee,
            self.capex,
            self.vacancy,
            self.repairs
        ], Money(0))

class PadSplitOperatingExpenses(OperatingExpenses):
    """PadSplit-specific operating expenses"""
    def __init__(self, data: Dict):
        super().__init__(data)
        self.platform_percentage = Percentage(data.get('padsplit_platform_percentage', 0))
        self.utilities = Money(data.get('utilities', 0))
        self.internet = Money(data.get('internet', 0))
        self.cleaning = Money(data.get('cleaning_costs', 0))  # Note: JSON uses cleaning_costs
        self.pest_control = Money(data.get('pest_control', 0))
        self.landscaping = Money(data.get('landscaping', 0))

    @property
    def platform_fee(self) -> Money:
        return self.monthly_rent * self.platform_percentage

    @property
    def total(self) -> Money:
        if self._total.dollars > 0:
            logger.debug(f"Using stored total operating expenses: {self._total}")
            return self._total
            
        base_expenses = super().total
        logger.debug(f"Base operating expenses: {base_expenses}")
        
        padsplit_expenses = sum([
            self.platform_fee,
            self.utilities,
            self.internet,
            self.cleaning,
            self.pest_control,
            self.landscaping
        ], Money(0))
        logger.debug(f"PadSplit specific expenses: {padsplit_expenses}")
        
        total = base_expenses + padsplit_expenses
        logger.debug(f"Total operating expenses: {total}")
        return total

class LoanCollection:
    """Manages all loans for an analysis"""
    def __init__(self, data: Dict):
        # Initialize BRRRR loans if present
        self.initial_loan = None
        self.refinance_loan = None
        if data.get('initial_loan_amount'):
            self.initial_loan = Loan(
                amount=data.get('initial_loan_amount', 0),
                interest_rate=data.get('initial_interest_rate', 0),
                term=data.get('initial_loan_term', 0),
                down_payment=data.get('initial_down_payment', 0),
                closing_costs=data.get('initial_closing_costs', 0),
                is_interest_only=data.get('initial_interest_only', False),
                name="Initial Purchase Loan",
                monthly_payment=data.get('initial_monthly_payment')
            )
            self.refinance_loan = Loan(
                amount=data.get('refinance_loan_amount', 0),
                interest_rate=data.get('refinance_interest_rate', 0),
                term=data.get('refinance_loan_term', 0),
                down_payment=data.get('refinance_down_payment', 0),
                closing_costs=data.get('refinance_closing_costs', 0),
                name="Refinance Loan",
                monthly_payment=data.get('refinance_monthly_payment')
            )

        # Initialize additional loans if present
        self.additional_loans = []
        if isinstance(data.get('loans'), list):
            for loan_data in data.get('loans', []):
                self.additional_loans.append(Loan(
                    amount=loan_data.get('amount', 0),
                    interest_rate=loan_data.get('interest_rate', 0),
                    term=loan_data.get('term', 0), 
                    down_payment=loan_data.get('down_payment', 0),
                    closing_costs=loan_data.get('closing_costs', 0),
                    name=loan_data.get('name')
                ))

    @property
    def all_loans(self) -> List[Loan]:
        loans = []
        if self.initial_loan and self.initial_loan.amount.dollars > 0:
            loans.append(self.initial_loan)
        if self.refinance_loan and self.refinance_loan.amount.dollars > 0:
            loans.append(self.refinance_loan)
        loans.extend([loan for loan in self.additional_loans if loan.amount.dollars > 0])
        return loans

    """Manages all loans for an analysis"""
    @property
    def total_monthly_payment(self) -> Money:
        total = sum((loan.calculate_payment().total for loan in self.all_loans), Money(0))
        logger.debug(f"Total monthly loan payment: {total}")
        return total

    @property
    def total_initial_costs(self) -> Money:
        return sum((loan.total_initial_costs for loan in self.all_loans), Money(0))

class Analysis(ABC):
    """Abstract base class for all analysis types"""
    def __init__(self, data: Dict):
        self.data = data
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.analysis_type = data.get('analysis_type')
        self.analysis_name = data.get('analysis_name')
        self.monthly_rent = Money(data.get('monthly_rent', 0))  # Add this line
        
        self.property_details = PropertyDetails(data.get('property_details', {}))
        self.purchase_details = PurchaseDetails(data.get('purchase_details', {}))
        self.loans = LoanCollection(data.get('loans', {}))
        self.operating_expenses = self._create_operating_expenses()

    @abstractmethod
    def _create_operating_expenses(self) -> OperatingExpenses:
        pass

    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow with detailed logging"""
        try:
            # Log input values
            logger.debug(f"Calculating monthly cash flow:")
            logger.debug(f"Monthly rent: {self.monthly_rent}")
            logger.debug(f"Operating expenses total: {self.operating_expenses.total}")
            
            # Get loan payments
            monthly_loan_payment = self.loans.total_monthly_payment
            logger.debug(f"Monthly loan payment: {monthly_loan_payment}")
            
            # Convert to floats for calculation
            monthly_rent = float(str(self.monthly_rent).replace('$', '').replace(',', ''))
            operating_expenses = float(str(self.operating_expenses.total).replace('$', '').replace(',', ''))
            loan_payment = float(str(monthly_loan_payment).replace('$', '').replace(',', ''))
            
            # Calculate and log cash flow
            cash_flow = monthly_rent - operating_expenses - loan_payment
            logger.debug(f"Calculated cash flow: {cash_flow}")
            
            return Money(cash_flow)
        except Exception as e:
            logger.error(f"Error calculating monthly cash flow: {str(e)}\n{traceback.format_exc()}")
            return Money(0)

    @property
    def annual_cash_flow(self) -> Money:
        monthly = self.calculate_monthly_cash_flow()
        annual = Money(float(monthly.dollars) * 12)
        logger.debug(f"Annual cash flow: {annual}")
        return annual

    def calculate_total_cash_invested(self) -> Money:
        """Calculate total cash invested"""
        total = sum([
            self.purchase_details.renovation_costs,
            self.loans.total_initial_costs,
            self.purchase_details.cash_to_seller,
            self.purchase_details.assignment_fee,
            self.purchase_details.marketing_costs
        ], Money(0))
        
        logger.debug(f"Total Cash Invested: {total}")
        return total

    @property
    def roi(self) -> Union[str, Percentage]:
        """Calculate ROI"""
        cash_invested = float(self.calculate_total_cash_invested().dollars)
        if cash_invested <= 0:
            return Percentage(0)
        annual_cf = float(self.annual_cash_flow.dollars)
        return Percentage((annual_cf / cash_invested) * 100 if cash_invested > 0 else 0)

    @property
    def cash_on_cash_return(self) -> Union[str, Percentage]:
        try:
            cash_invested = float(self.calculate_total_cash_invested().dollars)
            logger.debug(f"Total cash invested: {cash_invested}")
            
            if cash_invested <= 0:
                logger.debug("Cash invested is zero or negative, returning 0%")
                return Percentage(0)
                
            annual_cf = float(self.annual_cash_flow.dollars)
            logger.debug(f"Annual cash flow for CoC calculation: {annual_cf}")
            
            coc = Percentage((annual_cf / cash_invested) * 100)
            logger.debug(f"Calculated Cash on Cash return: {coc}")
            return coc
        except Exception as e:
            logger.error(f"Error calculating cash on cash return: {str(e)}\n{traceback.format_exc()}")
            return Percentage(0)

class LTRAnalysis(Analysis):
    """Long-term rental analysis implementation"""
    def _create_operating_expenses(self) -> OperatingExpenses:
        return OperatingExpenses(self.data)

class BRRRRAnalysis(Analysis):
    """BRRRR strategy analysis implementation"""
    def _create_operating_expenses(self) -> OperatingExpenses:
        return OperatingExpenses(self.data)

    @property
    def holding_costs(self) -> Money:
        monthly_costs = sum([
            self.operating_expenses.property_taxes,
            self.operating_expenses.insurance,
            self.loans.initial_loan.calculate_payment().total if self.loans.initial_loan else Money(0)
        ], Money(0))
        return monthly_costs * self.purchase_details.renovation_duration

    @property
    def total_project_costs(self) -> Money:
        return sum([
            self.purchase_details.purchase_price,
            self.purchase_details.renovation_costs,
            self.holding_costs,
            self.loans.initial_loan.closing_costs if self.loans.initial_loan else Money(0),
            self.loans.refinance_loan.closing_costs if self.loans.refinance_loan else Money(0),
            (self.loans.refinance_loan.amount * -1) if self.loans.refinance_loan else Money(0)
        ], Money(0))

    @property
    def cash_recouped(self) -> Money:
        return self.loans.refinance_loan.amount if self.loans.refinance_loan else Money(0)

    def calculate_total_cash_invested(self) -> Money:
        return self.total_project_costs - self.cash_recouped

    @property
    def equity_captured(self) -> Money:
        return Money(abs(
            self.purchase_details.after_repair_value.dollars - 
            self.total_project_costs.dollars
        ))

class PadSplitLTRAnalysis(LTRAnalysis):
    """PadSplit long-term rental analysis"""
    def _create_operating_expenses(self) -> PadSplitOperatingExpenses:
        return PadSplitOperatingExpenses(self.data)

class PadSplitBRRRRAnalysis(BRRRRAnalysis):
    """PadSplit BRRRR analysis"""
    def _create_operating_expenses(self) -> PadSplitOperatingExpenses:
        return PadSplitOperatingExpenses(self.data)

def create_analysis(data: Dict) -> Analysis:
    """Factory function to create appropriate analysis type"""
    analysis_types = {
        'BRRRR': BRRRRAnalysis,
        'PadSplit BRRRR': PadSplitBRRRRAnalysis,
        'PadSplit LTR': PadSplitLTRAnalysis,
        'LTR': LTRAnalysis
    }
    
    analysis_type = data.get('analysis_type')
    analysis_class = analysis_types.get(analysis_type)
    
    if not analysis_class:
        raise ValueError(f"Unknown analysis type: {analysis_type}")
        
    return analysis_class(data)