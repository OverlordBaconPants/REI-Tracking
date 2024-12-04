from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment
from datetime import datetime
import logging
import traceback

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

@dataclass
class ReportSection:
    """Represents a section of the analysis report with formatted data"""
    title: str
    data: List[tuple[str, str]]  # List of (label, formatted_value) pairs

@dataclass
class AnalysisReportData:
    """Container for all data needed to generate an analysis report"""
    analysis_name: str
    analysis_type: str
    property_address: str
    generated_date: str
    sections: List[ReportSection]

class ReportDataProvider(ABC):
    """Base interface for providing formatted report data"""
    
    @abstractmethod
    def get_report_data(self) -> AnalysisReportData:
        """Get fully formatted data for report generation"""
        pass

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
        """Calculate monthly payment with proper handling of interest-only"""
        if not self.term or not self.amount:
            return MonthlyPayment(total=Money(0), principal=Money(0), interest=Money(0))
            
        if self.is_interest_only:
            monthly_interest = float(self.amount.dollars) * float(self.interest_rate.as_decimal()) / 12
            return MonthlyPayment(total=Money(monthly_interest), principal=Money(0), interest=Money(monthly_interest))
            
        # Amortization calculation
        monthly_rate = Decimal(str(self.interest_rate.as_decimal())) / Decimal('12')
        principal_amount = Decimal(str(self.amount.dollars))
        
        if monthly_rate == 0:
            monthly_payment = principal_amount / Decimal(str(self.term))
        else:
            factor = (1 + monthly_rate) ** Decimal(str(self.term))
            monthly_payment = principal_amount * monthly_rate * factor / (factor - 1)
        
        return MonthlyPayment(total=Money(float(monthly_payment)), principal=Money(0), interest=Money(0))

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
        self.cleaning = Money(data.get('cleaning_costs', 0))
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
        logger.debug("=== Initializing LoanCollection ===")
        logger.debug(f"Received data: {data}")
        
        # Initialize BRRRR loans if present
        self.initial_loan = None
        self.refinance_loan = None
        
        if data.get('initial_loan_amount'):
            logger.debug(f"Creating initial loan with amount: {data.get('initial_loan_amount')}")
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
            logger.debug(f"Created initial loan: {self.initial_loan.__dict__}")

        if data.get('refinance_loan_amount'):
            logger.debug(f"Creating refinance loan with amount: {data.get('refinance_loan_amount')}")
            self.refinance_loan = Loan(
                amount=data.get('refinance_loan_amount', 0),
                interest_rate=data.get('refinance_interest_rate', 0),
                term=data.get('refinance_loan_term', 0),
                down_payment=data.get('refinance_down_payment', 0),
                closing_costs=data.get('refinance_closing_costs', 0),
                name="Refinance Loan",
                monthly_payment=data.get('refinance_monthly_payment')
            )
            logger.debug(f"Created refinance loan: {self.refinance_loan.__dict__}")

        logger.debug("=== Completed LoanCollection Initialization ===")

    @property
    def all_loans(self) -> List[Loan]:
        loans = []
        if self.initial_loan and self.initial_loan.amount.dollars > 0:
            loans.append(self.initial_loan)
        if self.refinance_loan and self.refinance_loan.amount.dollars > 0:
            loans.append(self.refinance_loan)
        loans.extend([loan for loan in self.additional_loans if loan.amount.dollars > 0])
        return loans

    @property
    def total_monthly_payment(self) -> Money:
        total = sum((loan.calculate_payment().total for loan in self.all_loans), Money(0))
        logger.debug(f"Total monthly loan payment: {total}")
        return total

    @property
    def total_initial_costs(self) -> Money:
        return sum((loan.total_initial_costs for loan in self.all_loans), Money(0))

class Analysis(ReportDataProvider, ABC): 
    """Abstract base class for all analysis types"""
    def __init__(self, data: Dict):
        logger.debug("=== Initializing Base Analysis ===")
        logger.debug(f"Analysis type: {data.get('analysis_type')}")
        logger.debug(f"Initial loan data: {data.get('initial_loan_amount')}")
        logger.debug(f"Refinance loan data: {data.get('refinance_loan_amount')}")
        logger.debug(f"Additional loans: {data.get('loans')}")
        
        self.data = data
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.analysis_type = data.get('analysis_type')
        self.analysis_name = data.get('analysis_name')
        self.monthly_rent = Money(data.get('monthly_rent', 0))
        
        # Convert loans list to dictionary if it isn't already
        if isinstance(data.get('loans'), list):
            loans_data = {
                'loans': data.get('loans', []),
                **{k: v for k, v in data.items() if k != 'loans'}
            }
            logger.debug(f"Converted loan data: {loans_data}")
        else:
            loans_data = data
            
        self.property_details = PropertyDetails(data)
        self.purchase_details = PurchaseDetails(data)
        self.loans = LoanCollection(loans_data)
        self.operating_expenses = self._create_operating_expenses()
        
        logger.debug("=== Completed Base Analysis Initialization ===")

    def get_report_data(self) -> AnalysisReportData:
        """Base implementation of report data generation"""
        logger.debug("=== Generating Base Report Data ===")
        logger.debug(f"Analysis type: {self.analysis_type}")
        logger.debug(f"Loan data: {[loan.__dict__ for loan in self.loans.all_loans]}")
        
        sections = [
            ReportSection(
                title="Purchase Details",
                data=[
                    ("Purchase Price", str(self.purchase_details.purchase_price)),
                    ("After Repair Value", str(self.purchase_details.after_repair_value)),
                    ("Renovation Costs", str(self.purchase_details.renovation_costs)),
                    ("Renovation Duration", f"{self.purchase_details.renovation_duration} months")
                ]
            ),
            ReportSection(
                title="Income & Returns",
                data=[
                    ("Monthly Rent", str(self.monthly_rent)),
                    ("Monthly Cash Flow", str(self.calculate_monthly_cash_flow())),
                    ("Annual Cash Flow", str(self.annual_cash_flow)),
                    ("Cash on Cash Return", str(self.cash_on_cash_return)),
                    ("ROI", str(self.roi))
                ]
            ),
            ReportSection(
                title="Operating Expenses",
                data=[
                    ("Property Taxes", str(self.operating_expenses.property_taxes)),
                    ("Insurance", str(self.operating_expenses.insurance)),
                    ("HOA/COA/COOP", str(self.operating_expenses.hoa_coa_coop)),
                    ("Management Fee", str(self.operating_expenses.management_fee)),
                    ("CapEx", str(self.operating_expenses.capex)),
                    ("Vacancy", str(self.operating_expenses.vacancy)),
                    ("Repairs", str(self.operating_expenses.repairs)),
                    ("Total Monthly Expenses", str(self.operating_expenses.total))
                ]
            )
        ]

        logger.debug("=== Completed Base Report Data ===")
        return AnalysisReportData(
            analysis_name=self.analysis_name,
            analysis_type=self.analysis_type,
            property_address=self.property_details.address,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sections=sections
        )

    @abstractmethod
    def _create_operating_expenses(self) -> OperatingExpenses:
        pass

    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow with detailed logging"""
        try:
            logger.debug("=== Starting Monthly Cash Flow Calculation ===")
            logger.debug(f"Monthly rent: {self.monthly_rent.dollars}")
            logger.debug(f"Operating expenses total: {self.operating_expenses.total.dollars}")
            logger.debug(f"Monthly loan payment: {self.loans.total_monthly_payment.dollars}")
            
            cash_flow = (
                self.monthly_rent.dollars -
                self.operating_expenses.total.dollars -
                self.loans.total_monthly_payment.dollars
            )
            
            logger.debug(f"Calculated cash flow: {cash_flow}")
            
            logger.debug("=== Cash Flow Components ===")
            logger.debug(f"Monthly Rent: +{self.monthly_rent.dollars}")
            logger.debug(f"Operating Expenses: -{self.operating_expenses.total.dollars}")
            logger.debug(f"Loan Payments: -{self.loans.total_monthly_payment.dollars}")
            logger.debug(f"Final Cash Flow: {cash_flow}")
            logger.debug("================================")
            
            return Money(cash_flow)
        except Exception as e:
            logger.error("Error calculating monthly cash flow:")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            logger.error(f"Input values:")
            logger.error(f"- Monthly rent: {getattr(self, 'monthly_rent', 'N/A')}")
            logger.error(f"- Operating expenses: {getattr(self.operating_expenses, 'total', 'N/A')}")
            logger.error(f"- Loan payments: {getattr(self.loans, 'total_monthly_payment', 'N/A')}")
            raise

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
            return "Infinite"
        annual_cf = float(self.annual_cash_flow.dollars)
        return Percentage((annual_cf / cash_invested) * 100 if cash_invested > 0 else 0)

    @property
    def cash_on_cash_return(self) -> Union[str, Percentage]:
        try:
            cash_invested = float(self.calculate_total_cash_invested().dollars)
            logger.debug(f"Total cash invested: {cash_invested}")
            
            if cash_invested <= 0:
                logger.debug("Cash invested is zero or negative, returning 'Infinite'")
                return "Infinite"
                
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

    def get_report_data(self) -> AnalysisReportData:
        """LTR-specific report data implementation"""
        logger.debug("=== Generating LTR Report Data ===")
        logger.debug(f"Number of loans: {len(self.loans.all_loans)}")
        
        base_data = super().get_report_data()
        
        # Add loan sections if they exist
        for i, loan in enumerate(self.loans.all_loans, 1):
            logger.debug(f"Processing loan {i}: {loan.__dict__}")
            base_data.sections.append(ReportSection(
                title=f"Loan {i} Details",
                data=[
                    ("Loan Amount", str(loan.amount)),
                    ("Interest Rate", str(loan.interest_rate)),
                    ("Monthly Payment", str(loan.calculate_payment().total)),
                    ("Term", f"{loan.term} months"),
                    ("Down Payment", str(loan.down_payment)),
                    ("Closing Costs", str(loan.closing_costs))
                ]
            ))
        
        logger.debug("=== Completed LTR Report Data ===")
        return base_data

class BRRRRAnalysis(Analysis):
    """BRRRR strategy analysis implementation"""
    def _create_operating_expenses(self) -> OperatingExpenses:
        return OperatingExpenses(self.data)

    def get_report_data(self) -> AnalysisReportData:
        """BRRRR-specific report data implementation"""
        logger.debug("=== Generating BRRRR Report Data ===")
        logger.debug(f"Initial loan amount: {self.loans.initial_loan.amount if self.loans.initial_loan else 'No initial loan'}")
        logger.debug(f"Refinance loan amount: {self.loans.refinance_loan.amount if self.loans.refinance_loan else 'No refinance loan'}")
        
        base_data = super().get_report_data()
        
        # Add BRRRR-specific sections
        investment_summary = ReportSection(
            title="Investment Summary",
            data=[
                ("Total Project Costs", str(self.total_project_costs)),
                ("Total Cash Invested", str(self.total_cash_invested)),
                ("Cash Recouped", str(self.cash_recouped)),
                ("Equity Captured", str(self.equity_captured))
            ]
        )
        base_data.sections.append(investment_summary)
        
        # Add financing details if loans exist
        if self.loans.initial_loan:
            logger.debug("Adding initial loan section")
            base_data.sections.append(ReportSection(
                title="Initial Financing",
                data=[
                    ("Loan Amount", str(self.loans.initial_loan.amount)),
                    ("Interest Rate", str(self.loans.initial_loan.interest_rate)),
                    ("Monthly Payment", str(self.loans.initial_loan.calculate_payment().total)),
                    ("Term", f"{self.loans.initial_loan.term} months"),
                    ("Down Payment", str(self.loans.initial_loan.down_payment)),
                    ("Closing Costs", str(self.loans.initial_loan.closing_costs)),
                    ("Interest Only", str(self.loans.initial_loan.is_interest_only))
                ]
            ))
        
        if self.loans.refinance_loan:
            logger.debug("Adding refinance loan section")
            base_data.sections.append(ReportSection(
                title="Refinance Details",
                data=[
                    ("Loan Amount", str(self.loans.refinance_loan.amount)),
                    ("Interest Rate", str(self.loans.refinance_loan.interest_rate)),
                    ("Monthly Payment", str(self.loans.refinance_loan.calculate_payment().total)),
                    ("Term", f"{self.loans.refinance_loan.term} months"),
                    ("Down Payment", str(self.loans.refinance_loan.down_payment)),
                    ("Closing Costs", str(self.loans.refinance_loan.closing_costs))
                ]
            ))
        
        logger.debug("=== Completed BRRRR Report Data ===")
        return base_data

    def calculate_monthly_cash_flow(self) -> Money:
        """Only consider refinance loan payment for cash flow"""
        refinance_payment = self.loans.refinance_loan.calculate_payment().total if self.loans.refinance_loan else Money(0)
        cash_flow = (
            self.monthly_rent -
            self.operating_expenses.total -
            refinance_payment
        )
        return cash_flow

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
        monthly_holding = sum([
            self.operating_expenses.property_taxes,
            self.operating_expenses.insurance,
            self.loans.initial_loan.calculate_payment().total if self.loans.initial_loan else Money(0)
        ], Money(0))
        
        total_holding_costs = monthly_holding * self.purchase_details.renovation_duration
        
        return sum([
            self.purchase_details.purchase_price,
            self.purchase_details.renovation_costs,
            total_holding_costs,
            self.loans.initial_loan.closing_costs if self.loans.initial_loan else Money(0),
            self.loans.refinance_loan.closing_costs if self.loans.refinance_loan else Money(0)
        ], Money(0))

    @property
    def total_cash_invested(self) -> Money:
        """Return calculated value or 0 if negative"""
        calculated = self.total_project_costs - self.cash_recouped
        return Money(max(0, float(calculated.dollars)))

    @property
    def cash_recouped(self) -> Money:
        return self.loans.refinance_loan.amount if self.loans.refinance_loan else Money(0)

    @property
    def equity_captured(self) -> Money:
        """Down payment minus cash left in deal"""
        down_payment = self.loans.refinance_loan.down_payment if self.loans.refinance_loan else Money(0)
        max_cash_left = Money(self.data.get('max_cash_left', 0))
        return down_payment - max_cash_left

class PadSplitAnalysisMixin:
    """Mixin to add PadSplit-specific report data"""
    
    def get_report_data(self) -> AnalysisReportData:
        """Add PadSplit section to report data"""
        logger.debug("=== Generating PadSplit Report Data ===")
        base_data = super().get_report_data()
        
        padsplit_section = ReportSection(
            title="PadSplit Expenses",
            data=[
                ("Platform Fee", str(self.operating_expenses.platform_fee)),
                ("Utilities", str(self.operating_expenses.utilities)),
                ("Internet", str(self.operating_expenses.internet)),
                ("Cleaning", str(self.operating_expenses.cleaning)),
                ("Pest Control", str(self.operating_expenses.pest_control)),
                ("Landscaping", str(self.operating_expenses.landscaping))
            ]
        )
        base_data.sections.append(padsplit_section)
        
        logger.debug("=== Completed PadSplit Report Data ===")
        return base_data

class PadSplitLTRAnalysis(PadSplitAnalysisMixin, LTRAnalysis):
    """PadSplit LTR implementation"""
    def _create_operating_expenses(self) -> PadSplitOperatingExpenses:
        return PadSplitOperatingExpenses(self.data)

class PadSplitBRRRRAnalysis(PadSplitAnalysisMixin, BRRRRAnalysis):
    """PadSplit BRRRR implementation"""
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