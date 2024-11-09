from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment
import logging

@dataclass
class Loan:
    """Represents a loan with its terms and payments"""
    amount: Money
    interest_rate: Percentage
    term_months: int
    down_payment: Money
    closing_costs: Money
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
        """Calculate monthly payment with amortization details"""
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
    def __init__(self, data: Dict):
        super().__init__(data)
        self.initial_loan = self._create_initial_loan()
        self.refinance_loan = self._create_refinance_loan()
        self.holding_costs = self._calculate_holding_costs()
        
    def _init_operating_expenses(self) -> OperatingExpenses:
        return OperatingExpenses(
            property_taxes=self.data['property_taxes'],
            insurance=self.data['insurance'],
            monthly_rent=self.data['monthly_rent'],
            management_percentage=self.data['management_percentage'],
            capex_percentage=self.data['capex_percentage'],
            vacancy_percentage=self.data['vacancy_percentage']
        )
        
    def _create_initial_loan(self) -> Loan:
        return Loan(
            amount=self.data['initial_loan_amount'],
            interest_rate=self.data['initial_interest_rate'],
            term_months=int(self.data['initial_loan_term']),
            down_payment=self.data['initial_down_payment'],
            closing_costs=self.data['initial_closing_costs'],
            name="Initial Purchase Loan"
        )
        
    def _create_refinance_loan(self) -> Loan:
        return Loan(
            amount=self.data['refinance_loan_amount'],
            interest_rate=self.data['refinance_interest_rate'],
            term_months=int(self.data['refinance_loan_term']),
            down_payment=self.data['refinance_down_payment'],
            closing_costs=self.data['refinance_closing_costs'],
            name="Refinance Loan"
        )
        
    def _calculate_holding_costs(self) -> Money:
        """Calculate holding costs during renovation period"""
        renovation_months = int(self.data['renovation_duration'])
        monthly_costs = sum([
            Money(self.data['property_taxes']),
            Money(self.data['insurance']),
            self.initial_loan.calculate_payment().total
        ], Money(0))
        return monthly_costs * renovation_months
        
    def calculate_monthly_cash_flow(self) -> Money:
        """Calculate monthly cash flow using refinance loan payment"""
        return self.monthly_rent - (
            self.operating_expenses.calculate_total() + 
            self.refinance_loan.calculate_payment().total
        )
        
    def calculate_cash_recouped(self) -> Money:
        """Calculate cash recouped through refinance"""
        return self.refinance_loan.amount - self.initial_loan.amount
        
    def calculate_total_project_costs(self) -> Money:
        """Calculate total project costs including all expenses"""
        return sum([
            self.purchase_price,
            self.renovation_costs,
            self.holding_costs,
            self.initial_loan.closing_costs,
            self.refinance_loan.closing_costs
        ], Money(0))
        
    def calculate_total_cash_invested(self) -> Money:
        """
        Calculate actual cash left in deal after refinance
        This is the total project costs minus the cash recouped through refinance
        """
        total_costs = self.calculate_total_project_costs()
        cash_recouped = self.calculate_cash_recouped()
        return total_costs - cash_recouped
        
    def calculate_equity_captured(self) -> Money:
        """Calculate equity captured (ARV minus total project costs)"""
        return self.after_repair_value - self.calculate_total_project_costs()
        
    def calculate_max_allowable_offer(self) -> Money:
        """Calculate maximum allowable offer based on refinance strategy"""
        refinance_ltv = Percentage(self.data.get('refinance_ltv_percentage', 75))
        max_cash_left = Money(self.data.get('max_cash_left', 10000))
        
        # Maximum loan based on ARV and LTV
        max_loan = self.after_repair_value * refinance_ltv
        
        # Working backwards from the maximum cash left in deal:
        # max_cash_left = total_costs - refinance_loan
        # total_costs = purchase + renovation + holding + closing costs
        estimated_holding_months = int(self.data['renovation_duration'])
        estimated_monthly_holding = Money(self.data['property_taxes']) + Money(self.data['insurance'])
        estimated_holding_costs = estimated_monthly_holding * estimated_monthly_holding
        
        # Solve for purchase price:
        # max_cash_left = (purchase + renovation + holding + closing) - max_loan
        # purchase = max_loan + max_cash_left - (renovation + holding + closing)
        mao = max_loan + max_cash_left - (
            self.renovation_costs +
            estimated_holding_costs +
            self.initial_loan.closing_costs +
            self.refinance_loan.closing_costs
        )
        
        return max(mao, Money(0))

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
    analysis_type = data.get('analysis_type')
    
    if analysis_type == 'BRRRR':
        return BRRRRAnalysis(data)
    elif analysis_type == 'PadSplit BRRRR':
        return PadSplitBRRRRAnalysis(data)
    elif analysis_type == 'PadSplit LTR':
        loans = _create_loans_from_data(data)
        return PadSplitLTRAnalysis(data, loans)
    elif analysis_type == 'Long-Term Rental':
        loans = _create_loans_from_data(data)
        return LongTermRentalAnalysis(data, loans)
    else:
        raise ValueError(f"Unknown analysis type: {analysis_type}")

def _create_loans_from_data(data: Dict) -> List[Loan]:
    """Create loan objects from raw data"""
    loans = []
    for i in range(1, 4):  # Support up to 3 loans
        loan_data = data.get('loans', {}).get(str(i))
        if loan_data:
            loans.append(Loan(
                amount=loan_data['amount'],
                interest_rate=loan_data['interest_rate'],
                term_months=int(loan_data['term']),
                down_payment=loan_data['down_payment'],
                closing_costs=loan_data['closing_costs'],
                name=loan_data.get('name', f'Loan {i}')
            ))
    return loans