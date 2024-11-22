from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment
from utils.calculators import AmortizationCalculator
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Loan:
    """Represents a loan with its terms and payments"""
    def __init__(self, amount, interest_rate, term_months, down_payment, closing_costs, is_interest_only: bool = False, name: Optional[str] = None):
        """
        Initialize loan with given terms.
        
        Args:
            amount: Loan amount
            interest_rate: Annual interest rate (percentage)
            term_months: Loan term in months
            down_payment: Down payment amount
            closing_costs: Closing costs amount
            is_interest_only: Whether this is an interest-only loan
            name: Optional name/description for the loan
        """
        # Set raw values first
        self.amount = amount
        self.interest_rate = interest_rate
        self.term_months = term_months
        self.down_payment = down_payment
        self.closing_costs = closing_costs
        self.is_interest_only = bool(is_interest_only)
        self.name = name
        
        # Then convert types
        self._validate_and_convert_types()

    def _validate_and_convert_types(self):
        """Convert all monetary values to proper types"""
        try:
            self.amount = Money(self.amount)
            self.interest_rate = Percentage(self.interest_rate)
            self.term_months = int(float(str(self.term_months)))
            self.down_payment = Money(self.down_payment)
            self.closing_costs = Money(self.closing_costs)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid loan parameters: {str(e)}")

    def calculate_payment(self) -> MonthlyPayment:
        """Calculate monthly payment based on loan type"""
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
            self.term_months
        )

    @property
    def total_initial_costs(self) -> Money:
        """Calculate total initial costs"""
        return self.down_payment + self.closing_costs

class OperatingExpenses:
    """Base operating expenses calculations"""
    def __init__(self, data: Dict):
        self.monthly_rent = Money(data.get('monthly_rent', 0))
        self.property_taxes = Money(data.get('property_taxes', 0))
        self.insurance = Money(data.get('insurance', 0))
        self.management_percentage = Percentage(data.get('management_percentage', 0))
        self.capex_percentage = Percentage(data.get('capex_percentage', 0))
        self.vacancy_percentage = Percentage(data.get('vacancy_percentage', 0))

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
    def total(self) -> Money:
        return sum([
            self.property_taxes,
            self.insurance,
            self.management_fee,
            self.capex,
            self.vacancy
        ], Money(0))

class LTROperatingExpenses(OperatingExpenses):
    """Long-term rental operating expenses"""
    def __init__(self, data: Dict):
        super().__init__(data)
        # Use .get() with default values
        self.repairs_percentage = Percentage(data.get('repairs_percentage', 0))
        self.hoa_coa_coop = Money(data.get('hoa_coa_coop', 0))

    @property
    def repairs(self) -> Money:
        return self.monthly_rent * self.repairs_percentage

    @property
    def total(self) -> Money:
        return super().total + self.repairs + self.hoa_coa_coop

class PadSplitOperatingExpenses(OperatingExpenses):
    """PadSplit-specific operating expenses"""
    def __init__(self, data: Dict):
        super().__init__(data)
        self.platform_percentage = Percentage(data['padsplit_platform_percentage'])
        self.utilities = Money(data['utilities'])
        self.internet = Money(data['internet'])
        self.cleaning_costs = Money(data['cleaning_costs'])
        self.pest_control = Money(data['pest_control'])
        self.landscaping = Money(data['landscaping'])

    @property
    def platform_fee(self) -> Money:
        return self.monthly_rent * self.platform_percentage

    @property
    def total(self) -> Money:
        return super().total + sum([
            self.platform_fee,
            self.utilities,
            self.internet,
            self.cleaning_costs,
            self.pest_control,
            self.landscaping
        ], Money(0))

class Analysis(ABC):
    """Abstract base class for all analysis types"""
    def __init__(self, data: Dict):
        self.data = data
        self.purchase_price = Money(data['purchase_price'])
        self.monthly_rent = Money(data['monthly_rent'])
        self.after_repair_value = Money(data['after_repair_value'])
        self.renovation_costs = Money(data['renovation_costs'])
        self.operating_expenses = self._create_operating_expenses()

    @abstractmethod
    def _create_operating_expenses(self) -> OperatingExpenses:
        """Create appropriate operating expenses object"""
        pass

    @abstractmethod
    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow"""
        pass

    @property
    def annual_cash_flow(self) -> Money:
        """Calculate annual cash flow"""
        return self.calculate_monthly_cash_flow() * 12

    @abstractmethod
    def calculate_total_cash_invested(self) -> Money:
        """Calculate total cash invested in the deal"""
        pass

    @property
    def roi(self) -> Union[Percentage, str]:
        """Calculate ROI including both cash flow and equity"""
        try:
            cash_invested = self.calculate_total_cash_invested()
            if cash_invested.dollars <= 0:
                return "Infinite"
            return Percentage(
                (self.annual_cash_flow / cash_invested * 100).dollars
            )
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return "Error"

class LTRAnalysis(Analysis):
    """Long-term rental analysis implementation"""
    def __init__(self, data: Dict):
        self.loans = self._create_loans(data.get('loans', []))
        super().__init__(data)

    def _create_operating_expenses(self) -> LTROperatingExpenses:
        return LTROperatingExpenses(self.data)

    def _create_loans(self, loan_data: List[Dict]) -> List[Loan]:
        return [Loan(**loan) for loan in loan_data]

    @property
    def total_loan_payment(self) -> Money:
        return sum((loan.calculate_payment().total for loan in self.loans), Money(0))
    
    @property
    def cash_on_cash_return(self) -> Union[str, Percentage]:
        try:
            cash_invested = self.calculate_total_cash_invested()
            if cash_invested.dollars <= 0:
                return "Infinite"
            # Get raw decimal values and perform calculation
            annual_flow = self.annual_cash_flow.dollars  
            total_invested = cash_invested.dollars
            return_percentage = (annual_flow / total_invested * 100)
            return Percentage(return_percentage)
        except Exception as e:
            logger.error(f"Error calculating cash on cash return: {str(e)}")
            return "Error"
        
    @property
    def roi(self) -> Union[Percentage, str]:
        try:
            cash_invested = self.calculate_total_cash_invested()
            if cash_invested.dollars <= 0:
                return "Infinite"
            annual_flow = self.annual_cash_flow.dollars
            total_invested = cash_invested.dollars
            return_percentage = (annual_flow / total_invested * 100)
            return Percentage(return_percentage)
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return "Error"

    def calculate_monthly_cash_flow(self) -> Money:
        return self.monthly_rent - (
            self.operating_expenses.total + 
            self.total_loan_payment
        )

    def calculate_total_cash_invested(self) -> Money:
        renovation = self.renovation_costs
        loan_costs = sum((loan.total_initial_costs for loan in self.loans), Money(0))
        cash_to_seller = Money(self.data.get('cash_to_seller', 0))
        assignment = Money(self.data.get('assignment_fee', 0))
        marketing = Money(self.data.get('marketing_costs', 0))
        
        total = sum([renovation, loan_costs, cash_to_seller, assignment, marketing], Money(0))
        
        logger.debug(f"""
            Cash invested calculation:
            Renovation: {renovation}
            Loan costs: {loan_costs}
            Cash to seller: {cash_to_seller}
            Assignment: {assignment}
            Marketing: {marketing}
            Total: {total}
        """)
        
        return total

class BRRRRAnalysis(Analysis):
    """BRRRR strategy analysis implementation"""
    def __init__(self, data: Dict):
        self.initial_loan = self._create_initial_loan(data)
        self.refinance_loan = self._create_refinance_loan(data)
        super().__init__(data)
        self.renovation_duration = int(data.get('renovation_duration', 0))

    def _create_operating_expenses(self) -> OperatingExpenses:
        return OperatingExpenses(self.data)

    def _create_initial_loan(self, data: Dict) -> Loan:
        return Loan(
            amount=data['initial_loan_amount'],
            interest_rate=data['initial_interest_rate'],
            term_months=data['initial_loan_term'],
            down_payment=data['initial_down_payment'],
            closing_costs=data['initial_closing_costs'],
            is_interest_only=data.get('initial_interest_only', False),
            name="Initial Purchase Loan"
        )

    def _create_refinance_loan(self, data: Dict) -> Loan:
        return Loan(
            amount=data['refinance_loan_amount'],
            interest_rate=data['refinance_interest_rate'],
            term_months=data['refinance_loan_term'],
            down_payment=data['refinance_down_payment'],
            closing_costs=data['refinance_closing_costs'],
            name="Refinance Loan"
        )

    @property
    def holding_costs(self) -> Money:
        monthly_costs = sum([
            self.operating_expenses.property_taxes,
            self.operating_expenses.insurance,
            self.initial_loan.calculate_payment().total
        ], Money(0))
        return monthly_costs * self.renovation_duration

    def calculate_monthly_cash_flow(self) -> Money:
        return self.monthly_rent - (
            self.operating_expenses.total + 
            self.refinance_loan.calculate_payment().total
        )

    @property
    def total_project_costs(self) -> Money:
        return sum([
            self.purchase_price,
            self.renovation_costs,
            self.holding_costs,
            self.initial_loan.closing_costs,
            self.refinance_loan.closing_costs,
            (self.refinance_loan.amount * -1)
        ], Money(0))

    @property
    def cash_recouped(self) -> Money:
        return self.refinance_loan.amount

    def calculate_total_cash_invested(self) -> Money:
        return self.total_project_costs - self.cash_recouped

    @property
    def equity_captured(self) -> Money:
        return Money(abs(
            self.after_repair_value.dollars - 
            self.total_project_costs.dollars
        ))

    @property
    def total_monthly_expenses(self) -> Money:
        return self.operating_expenses.total + self.refinance_loan.calculate_payment().total

    @property
    def cash_on_cash_return(self) -> Union[str, Percentage]:
        try:
            cash_invested = self.calculate_total_cash_invested()
            if cash_invested.dollars <= 0:
                return "Infinite"
            # Get raw decimal values and perform calculation
            annual_flow = self.annual_cash_flow.dollars  
            total_invested = cash_invested.dollars
            return_percentage = (annual_flow / total_invested * 100)
            return Percentage(return_percentage)
        except Exception as e:
            logger.error(f"Error calculating cash on cash return: {str(e)}")
            return "Error"

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

class ActualPerformanceMetrics:
    """Calculate actual performance metrics from transaction data"""
    
    def __init__(self, property_address: str, transactions: List[Dict]):
        self.property_address = self._normalize_address(property_address)
        self.transactions = self._filter_transactions(transactions)
        self._categorized_expenses = self._categorize_expenses()

    def _normalize_address(self, address: str) -> str:
        """Normalize address format for comparison"""
        # Remove duplicate city/state/zip if present after USA
        base_address = address.split(', United States of America')[0]
        # Split into components
        components = base_address.split(',')
        # Keep street, city, state, zip
        normalized = ','.join(c.strip() for c in components[:4])
        return normalized

    def _filter_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Filter transactions for this property"""
        target = self._normalize_address(self.property_address)
        return [t for t in transactions 
                if self._normalize_address(t['property_id']) == target]

    def _is_same_address(self, addr1: str, addr2: str) -> bool:
        """Compare addresses more flexibly"""
        # Split into components
        components1 = addr1.lower().split(',')
        components2 = addr2.lower().split(',')
        
        # Must match street number and name
        street1 = components1[0].strip()
        street2 = components2[0].strip()
        if street1 != street2:
            return False
            
        # City should be similar (contained)
        city1 = components1[1].strip()
        city2 = components2[1].strip()
        if city1 not in city2 and city2 not in city1:
            return False
            
        # State abbreviation should match
        state1 = components1[2].strip()[:2]
        state2 = components2[2].strip()[:2]
        if state1 != state2:
            return False
            
        return True

    def _categorize_expenses(self) -> Dict[str, List[Dict]]:
        """Group expenses by category"""
        categories = {}
        for t in self.transactions:
            if t['type'] == 'expense':
                cat = t['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(t)
        return categories

    def calculate_actual_monthly_income(self) -> Money:
        """Calculate average monthly rental income"""
        rent_transactions = [t for t in self.transactions if t['type'] == 'income']
        
        if not rent_transactions:
            return Money(0)
        
        dates = [datetime.strptime(t['date'], '%Y-%m-%d') for t in rent_transactions]
        min_date = min(dates)
        max_date = max(dates)
        
        # Calculate actual months between first and last transaction
        months = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month + 1
        
        total_rent = sum(float(t['amount']) for t in rent_transactions)
        return Money(total_rent / max(months, 1))

    def calculate_actual_monthly_expenses(self) -> Dict[str, Money]:
        """Calculate average monthly expenses by category"""
        if not self.transactions:
            return {'total': Money(0)}

        # Get date range for all transactions
        dates = [datetime.strptime(t['date'], '%Y-%m-%d') 
                for t in self.transactions]
        min_date = min(dates)
        max_date = max(dates)
        months = (max_date.year - min_date.year) * 12 + max_date.month - min_date.month + 1
        
        monthly_expenses = {}
        for category, transactions in self._categorized_expenses.items():
            # Skip one-time expenses like Asset Acquisition
            if category in ['Asset Acquisition', 'Capital Expenditures']:
                continue
            total = sum(float(t['amount']) for t in transactions)
            monthly_expenses[category] = Money(total / max(months, 1))
            
        monthly_expenses['total'] = Money(sum(e.dollars for e in monthly_expenses.values()))
        return monthly_expenses

    def get_metrics(self) -> Dict:
        """Get all actual performance metrics"""
        monthly_income = self.calculate_actual_monthly_income()
        monthly_expenses = self.calculate_actual_monthly_expenses()
        monthly_cash_flow = monthly_income - monthly_expenses['total']
        
        return {
            'actual_monthly_income': str(monthly_income),
            'actual_monthly_expenses': {k: str(v) for k, v in monthly_expenses.items()},
            'actual_monthly_cash_flow': str(monthly_cash_flow),
            'actual_annual_cash_flow': str(monthly_cash_flow * 12)
        }