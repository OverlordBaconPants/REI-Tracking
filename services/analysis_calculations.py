from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment
from utils.calculators import AmortizationCalculator
import logging
import traceback

@dataclass
class Loan:
    """Represents a loan with its terms and payments"""
    amount: Money
    interest_rate: Percentage
    term_months: int
    down_payment: Money
    closing_costs: Money
    is_interest_only: bool = False
    name: Optional[str] = None

    def __post_init__(self):
        # Convert any raw values to Money/Percentage objects
        if not isinstance(self.amount, Money):
            self.amount = Money(self.amount)
        if not isinstance(self.interest_rate, Percentage):
            self.interest_rate = Percentage(self.interest_rate)
        if not isinstance(self.down_payment, Money):
            self.down_payment = Money(self.down_payment)
        if not isinstance(self.closing_costs, Money):
            self.closing_costs = Money(self.closing_costs)

    def calculate_payment(self) -> MonthlyPayment:
        """Calculate monthly payment based on loan type"""
        if self.is_interest_only:
            # For interest-only loans, calculate just the monthly interest
            monthly_interest_rate = self.interest_rate.as_decimal() / Decimal('12')
            monthly_interest = self.amount.dollars * monthly_interest_rate
            return MonthlyPayment(
                total=Money(monthly_interest),
                principal=Money(0),
                interest=Money(monthly_interest)
            )
        else:
            # For conventional loans, use standard amortization
            return AmortizationCalculator.calculate_monthly_payment(
                self.amount, self.interest_rate, self.term_months
            )

    def total_initial_costs(self) -> Money:
        """Calculate total initial costs (down payment + closing costs)"""
        return self.down_payment + self.closing_costs

@dataclass
class OperatingExpenses:
    """Base operating expenses calculations"""
    property_taxes: Money
    insurance: Money
    monthly_rent: Money
    management_percentage: Percentage
    capex_percentage: Percentage
    vacancy_percentage: Percentage
    
    def __post_init__(self):
        # Convert any raw values to Money/Percentage objects
        if not isinstance(self.property_taxes, Money):
            self.property_taxes = Money(self.property_taxes)
        if not isinstance(self.insurance, Money):
            self.insurance = Money(self.insurance)
        if not isinstance(self.monthly_rent, Money):
            self.monthly_rent = Money(self.monthly_rent)
        if not isinstance(self.management_percentage, Percentage):
            self.management_percentage = Percentage(self.management_percentage)
        if not isinstance(self.capex_percentage, Percentage):
            self.capex_percentage = Percentage(self.capex_percentage)
        if not isinstance(self.vacancy_percentage, Percentage):
            self.vacancy_percentage = Percentage(self.vacancy_percentage)
    
    def calculate_management_fee(self) -> Money:
        return self.monthly_rent * self.management_percentage
        
    def calculate_capex(self) -> Money:
        return self.monthly_rent * self.capex_percentage
        
    def calculate_vacancy(self) -> Money:
        return self.monthly_rent * self.vacancy_percentage
        
    def calculate_total(self) -> Money:
        return sum([
            self.property_taxes,
            self.insurance,
            self.calculate_management_fee(),
            self.calculate_capex(),
            self.calculate_vacancy()
        ], Money(0))

@dataclass
class LTROperatingExpenses(OperatingExpenses):
    """Long-term rental operating expenses"""
    repairs_percentage: Percentage
    hoa_coa_coop: Money
    
    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.repairs_percentage, Percentage):
            self.repairs_percentage = Percentage(self.repairs_percentage)
        if not isinstance(self.hoa_coa_coop, Money):
            self.hoa_coa_coop = Money(self.hoa_coa_coop)
    
    def calculate_repairs(self) -> Money:
        return self.monthly_rent * self.repairs_percentage
        
    def calculate_total(self) -> Money:
        return super().calculate_total() + self.calculate_repairs() + self.hoa_coa_coop

@dataclass 
class PadSplitOperatingExpenses(OperatingExpenses):
    """PadSplit-specific operating expenses"""
    platform_percentage: Percentage
    utilities: Money
    internet: Money
    cleaning_costs: Money
    pest_control: Money
    landscaping: Money
    
    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.platform_percentage, Percentage):
            self.platform_percentage = Percentage(self.platform_percentage)
        if not isinstance(self.utilities, Money):
            self.utilities = Money(self.utilities)
        if not isinstance(self.internet, Money):
            self.internet = Money(self.internet)
        if not isinstance(self.cleaning_costs, Money):
            self.cleaning_costs = Money(self.cleaning_costs)
        if not isinstance(self.pest_control, Money):
            self.pest_control = Money(self.pest_control)
        if not isinstance(self.landscaping, Money):
            self.landscaping = Money(self.landscaping)
    
    def calculate_platform_fee(self) -> Money:
        return self.monthly_rent * self.platform_percentage
        
    def calculate_total(self) -> Money:
        return super().calculate_total() + sum([
            self.calculate_platform_fee(),
            self.utilities,
            self.internet,
            self.cleaning_costs,
            self.pest_control,
            self.landscaping
        ], Money(0))

class BaseAnalysis(ABC):
    """Abstract base class for property analysis"""
    
    def __init__(self, data: Dict):
        self.data = data
        self.operating_expenses = self._init_operating_expenses()
        self.monthly_rent = Money(data['monthly_rent'])
        self.purchase_price = Money(data['purchase_price'])
        self.renovation_costs = Money(data['renovation_costs'])
        self.after_repair_value = Money(data['after_repair_value'])
        
    @abstractmethod
    def _init_operating_expenses(self) -> OperatingExpenses:
        """Initialize operating expenses"""
        pass
        
    @abstractmethod
    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow"""
        pass
        
    def calculate_annual_cash_flow(self) -> Money:
        """Calculate annual cash flow"""
        return self.calculate_monthly_cash_flow() * 12
        
    def calculate_roi(self, total_cash_invested: Money, equity_captured: Money) -> Percentage:
        """Calculate ROI including both cash flow and equity"""
        if total_cash_invested.dollars <= 0:
            return Percentage(0)
            
        total_return = self.calculate_annual_cash_flow() + equity_captured
        return Percentage((total_return / total_cash_invested * 100).dollars)

class LongTermRentalAnalysis(BaseAnalysis):
    def __init__(self, data: Dict, loans: List[Loan]):
        super().__init__(data)
        self.loans = loans
        
    def _init_operating_expenses(self) -> LTROperatingExpenses:
        return LTROperatingExpenses(
            property_taxes=self.data['property_taxes'],
            insurance=self.data['insurance'],
            monthly_rent=self.data['monthly_rent'],
            management_percentage=self.data['management_percentage'],
            capex_percentage=self.data['capex_percentage'],
            vacancy_percentage=self.data['vacancy_percentage'],
            repairs_percentage=self.data['repairs_percentage'],
            hoa_coa_coop=self.data['hoa_coa_coop']
        )
        
    def calculate_total_loan_payment(self) -> Money:
        """Calculate total monthly loan payments across all loans"""
        return sum(
            (loan.calculate_payment().total for loan in self.loans),
            Money(0)
        )
        
    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow"""
        return self.monthly_rent - (
            self.operating_expenses.calculate_total() + 
            self.calculate_total_loan_payment()
        )
        
    def calculate_total_cash_invested(self) -> Money:
        """Calculate total cash invested"""
        return sum([
            self.renovation_costs,
            sum((loan.total_initial_costs() for loan in self.loans), Money(0)),
            Money(self.data.get('cash_to_seller', 0)),
            Money(self.data.get('assignment_fee', 0)),
            Money(self.data.get('marketing_costs', 0))
        ], Money(0))

class BRRRRAnalysis(BaseAnalysis):
    """BRRRR strategy analysis implementation"""
    
    def __init__(self, data: Dict):
        self.data = data  # Store data before super().__init__
        super().__init__(data)  # Create base properties first
        self.initial_loan = self._create_initial_loan()
        self.refinance_loan = self._create_refinance_loan()
        self.holding_costs = self._calculate_holding_costs()

    def _init_operating_expenses(self) -> OperatingExpenses:
        """Initialize operating expenses"""
        try:
            return OperatingExpenses(
                property_taxes=Money(self.data.get('property_taxes', 0)),
                insurance=Money(self.data.get('insurance', 0)),
                monthly_rent=Money(self.data.get('monthly_rent', 0)),
                management_percentage=Percentage(self.data.get('management_percentage', 0)),
                capex_percentage=Percentage(self.data.get('capex_percentage', 0)),
                vacancy_percentage=Percentage(self.data.get('vacancy_percentage', 0))
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error initializing operating expenses: {str(e)}")
            raise ValueError(f"Invalid operating expense data: {str(e)}")

    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow"""
        try:
            total_expenses = (
                self.operating_expenses.calculate_total() + 
                self.refinance_loan.calculate_payment().total
            )
            return Money(self.monthly_rent.dollars - total_expenses.dollars)
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating monthly cash flow: {str(e)}")
            raise ValueError(f"Error in cash flow calculation: {str(e)}")
        
    def _create_initial_loan(self) -> Loan:
        """Create the initial purchase loan"""
        try:
            return Loan(
                amount=Money(self.data['initial_loan_amount']),
                interest_rate=Percentage(self.data['initial_interest_rate']),
                term_months=int(self.data['initial_loan_term']),
                down_payment=Money(self.data['initial_down_payment']),
                closing_costs=Money(self.data['initial_closing_costs']),
                is_interest_only=bool(self.data.get('initial_interest_only', False)),
                name="Initial Purchase Loan"
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error creating initial loan: {str(e)}")
            raise ValueError(f"Invalid initial loan data: {str(e)}")
        
    def _create_refinance_loan(self) -> Loan:
        """Create the refinance loan"""
        try:
            return Loan(
                amount=Money(self.data.get('refinance_loan_amount', 0)),
                interest_rate=Percentage(self.data.get('refinance_interest_rate', 0)),
                term_months=int(self.data.get('refinance_loan_term', 0)),
                down_payment=Money(self.data.get('refinance_down_payment', 0)),
                closing_costs=Money(self.data.get('refinance_closing_costs', 0)),
                name="Refinance Loan"
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error creating refinance loan: {str(e)}")
            raise ValueError(f"Invalid refinance loan data: {str(e)}")
        
    def _calculate_holding_costs(self) -> Money:
        """Calculate holding costs during renovation period"""
        try:
            renovation_months = int(self.data.get('renovation_duration', 0))
            monthly_costs = sum([
                Money(self.data.get('property_taxes', 0)),
                Money(self.data.get('insurance', 0)),
                self.initial_loan.calculate_payment().total
            ], Money(0))
            return Money(monthly_costs.dollars * renovation_months)
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating holding costs: {str(e)}")
            raise ValueError(f"Error in holding costs calculation: {str(e)}")

    def calculate_total_project_costs(self) -> Money:
        """
        Calculate total project costs including all costs and subtracting refinance amount
        Total = Purchase Price + Renovation + Initial Closing + Refinance Closing + 
               Holding Costs - Refinance Loan Amount
        """
        try:
            # First sum up all costs
            total_costs = Money(sum([
                self.purchase_price.dollars,
                self.renovation_costs.dollars,
                self.holding_costs.dollars,
                self.initial_loan.closing_costs.dollars,
                self.refinance_loan.closing_costs.dollars
            ]))
            
            # Subtract refinance loan amount (cash we get back)
            final_costs = Money(total_costs.dollars - self.refinance_loan.amount.dollars)
            
            return final_costs
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating total project costs: {str(e)}")
            raise ValueError(f"Error in project costs calculation: {str(e)}")

    def calculate_cash_recouped(self) -> Money:
        """Calculate cash recouped through refinance"""
        return self.refinance_loan.amount

    def calculate_total_cash_invested(self) -> Money:
        """Calculate actual cash left in deal after refinance"""
        try:
            total_costs = self.calculate_total_project_costs()
            cash_recouped = self.calculate_cash_recouped()
            return Money(total_costs.dollars - cash_recouped.dollars)
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating total cash invested: {str(e)}")
            raise ValueError(f"Error in cash invested calculation: {str(e)}")

    def calculate_equity_captured(self) -> Money:
        """Calculate equity captured"""
        try:
            equity = self.after_repair_value.dollars - self.calculate_total_project_costs().dollars
            return Money(abs(equity))
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating equity captured: {str(e)}")
            raise ValueError(f"Error in equity calculation: {str(e)}")

    def calculate_total_monthly_expenses(self) -> Money:
        """Calculate total monthly expenses"""
        try:
            return Money(sum([
                self.operating_expenses.calculate_total().dollars,
                self.refinance_loan.calculate_payment().total.dollars
            ]))
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating total monthly expenses: {str(e)}")
            raise ValueError(f"Error in monthly expenses calculation: {str(e)}")

    def calculate_cash_on_cash_return(self) -> str:
        """
        Calculate cash-on-cash return
        Returns "Infinite" if no cash left in deal, percentage otherwise
        """
        try:
            total_cash_invested = self.calculate_total_cash_invested()
            
            # If no cash left in deal (or negative cash, meaning we pulled out more than we put in)
            if total_cash_invested.dollars <= 0:
                return "Infinite"
                
            annual_cash_flow = self.calculate_annual_cash_flow()
            return str(Percentage((annual_cash_flow.dollars / total_cash_invested.dollars * 100)))
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.error(f"Error calculating cash on cash return: {str(e)}")
            return "Infinite"  # Return infinite if there's any calculation error
    
    def calculate_roi(self) -> str:
        """
        Calculate total ROI including both cash flow and equity
        Returns "Infinite" if no cash left in deal, percentage otherwise
        """
        try:
            total_cash_invested = self.calculate_total_cash_invested()
            
            # If no cash left in deal (or negative cash, meaning we pulled out more than we put in)
            if total_cash_invested.dollars <= 0:
                return "Infinite"
            
            annual_cash_flow = self.calculate_annual_cash_flow()
            equity_captured = self.calculate_equity_captured()
            total_return = annual_cash_flow.dollars + equity_captured.dollars
            
            return str(Percentage((total_return / total_cash_invested.dollars * 100)))
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return "Infinite"  # Return infinite if there's any calculation error

class PadSplitAnalysisMixin:
    """Mixin class for PadSplit-specific calculations"""
    
    def _init_padsplit_expenses(self, data: Dict) -> PadSplitOperatingExpenses:
        return PadSplitOperatingExpenses(
            property_taxes=data['property_taxes'],
            insurance=data['insurance'],
            monthly_rent=data['monthly_rent'],
            management_percentage=data['management_percentage'],
            capex_percentage=data['capex_percentage'],
            vacancy_percentage=data['vacancy_percentage'],
            platform_percentage=data['padsplit_platform_percentage'],
            utilities=data['utilities'],
            internet=data['internet'],
            cleaning_costs=data['cleaning_costs'],
            pest_control=data['pest_control'],
            landscaping=data['landscaping']
        )

class PadSplitLTRAnalysis(LongTermRentalAnalysis, PadSplitAnalysisMixin):
    def _init_operating_expenses(self) -> PadSplitOperatingExpenses:
        return self._init_padsplit_expenses(self.data)

class PadSplitBRRRRAnalysis(BRRRRAnalysis, PadSplitAnalysisMixin):
    def _init_operating_expenses(self) -> PadSplitOperatingExpenses:
        return self._init_padsplit_expenses(self.data)

# Factory function to create the appropriate analysis object
def create_analysis(data: Dict) -> BaseAnalysis:
    """Create the appropriate analysis object based on analysis type"""
    try:
        analysis_type = data.get('analysis_type')
        if not analysis_type:
            raise ValueError("Analysis type is required")
            
        logger = logging.getLogger(__name__)
        logger.debug(f"Creating analysis of type: {analysis_type}")
        
        # Normalize analysis type to match class names
        analysis_type = analysis_type.replace(' ', '')  # Remove spaces
        
        # Map frontend analysis types to classes
        analysis_map = {
            'BRRRR': BRRRRAnalysis,
            'PadSplitBRRRR': PadSplitBRRRRAnalysis,
            'PadSplitLTR': PadSplitLTRAnalysis,
            'Long-TermRental': LongTermRentalAnalysis
        }
        
        analysis_class = analysis_map.get(analysis_type)
        if not analysis_class:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
            
        logger.debug(f"Using analysis class: {analysis_class.__name__}")
        
        # Handle different constructor requirements
        if analysis_class in (LongTermRentalAnalysis, PadSplitLTRAnalysis):
            loans = _create_loans_from_data(data)
            return analysis_class(data, loans)
        else:
            return analysis_class(data)
            
    except Exception as e:
        logger.error(f"Error creating analysis: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def _create_loans_from_data(data: Dict) -> List[Loan]:
    """Create loan objects from raw data"""
    try:
        loans = []
        raw_loans = data.get('loans', [])
        
        # Handle loans whether they come as a list or dict
        if isinstance(raw_loans, dict):
            raw_loans = [loan for _, loan in raw_loans.items() if loan]
        
        for i, loan_data in enumerate(raw_loans, 1):
            if not loan_data:
                continue
                
            try:
                loans.append(Loan(
                    amount=Money(loan_data['amount']),
                    interest_rate=Percentage(loan_data['interest_rate']),
                    term_months=int(loan_data['term']),
                    down_payment=Money(loan_data['down_payment']),
                    closing_costs=Money(loan_data['closing_costs']),
                    name=loan_data.get('name', f'Loan {i}')
                ))
            except KeyError as ke:
                logger.error(f"Missing required loan field: {ke}")
                raise ValueError(f"Loan {i} is missing required field: {ke}")
            except ValueError as ve:
                logger.error(f"Invalid loan data: {ve}")
                raise ValueError(f"Invalid data for loan {i}: {ve}")
                
        return loans
        
    except Exception as e:
        logger.error(f"Error creating loans: {str(e)}")
        logger.error(traceback.format_exc())
        raise