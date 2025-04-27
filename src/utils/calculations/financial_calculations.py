"""
Financial calculations module for the REI-Tracker application.

This module provides specialized financial calculations for real estate investments,
including cash flow calculations, balloon payment analysis, lease option calculations,
and refinance impact analysis.
"""

from typing import Dict, Any, Optional, List, Union, Tuple
from decimal import Decimal
import logging
from dataclasses import dataclass, field
from datetime import date

from src.utils.money import Money, Percentage, MonthlyPayment
from src.utils.calculations.validation import ValidationResult, Validator, safe_calculation
from src.utils.calculations.loan_details import LoanDetails
from src.utils.calculations.investment_metrics import InvestmentMetricsCalculator

logger = logging.getLogger(__name__)

@dataclass
class CashFlowBreakdown:
    """
    Detailed breakdown of cash flow components.
    
    This class provides a structured representation of all income and expense
    components that contribute to the monthly cash flow calculation.
    
    Attributes:
        income: Dictionary of income components
        expenses: Dictionary of expense components
        loan_payments: Dictionary of loan payment components
        total_income: Total monthly income
        total_expenses: Total monthly expenses
        total_loan_payments: Total monthly loan payments
        net_cash_flow: Net monthly cash flow
    """
    income: Dict[str, Money] = field(default_factory=dict)
    expenses: Dict[str, Money] = field(default_factory=dict)
    loan_payments: Dict[str, Money] = field(default_factory=dict)
    total_income: Money = field(default_factory=lambda: Money(0))
    total_expenses: Money = field(default_factory=lambda: Money(0))
    total_loan_payments: Money = field(default_factory=lambda: Money(0))
    net_cash_flow: Money = field(default_factory=lambda: Money(0))
    
    def __str__(self) -> str:
        """Format cash flow breakdown as a string."""
        result = "Income:\n"
        for name, amount in self.income.items():
            result += f"  {name}: {amount}\n"
        result += f"Total Income: {self.total_income}\n\n"
        
        result += "Expenses:\n"
        for name, amount in self.expenses.items():
            result += f"  {name}: {amount}\n"
        result += f"Total Expenses: {self.total_expenses}\n\n"
        
        result += "Loan Payments:\n"
        for name, amount in self.loan_payments.items():
            result += f"  {name}: {amount}\n"
        result += f"Total Loan Payments: {self.total_loan_payments}\n\n"
        
        result += f"Net Cash Flow: {self.net_cash_flow}"
        return result

@dataclass
class BalloonAnalysis:
    """
    Analysis of balloon payment impact on cash flow and investment returns.
    
    This class provides detailed analysis of how a balloon payment affects
    cash flow and investment returns, including pre-balloon and post-balloon
    scenarios.
    
    Attributes:
        pre_balloon_cash_flow: Monthly cash flow before balloon payment
        post_balloon_cash_flow: Monthly cash flow after balloon payment
        balloon_amount: Balloon payment amount
        balloon_date: Balloon payment due date
        balloon_term_months: Months until balloon payment is due
        refinance_loan_details: Details of refinance loan after balloon payment
        post_balloon_annual_increases: Annual increases in post-balloon values
    """
    pre_balloon_cash_flow: Money = field(default_factory=lambda: Money(0))
    post_balloon_cash_flow: Money = field(default_factory=lambda: Money(0))
    balloon_amount: Money = field(default_factory=lambda: Money(0))
    balloon_date: Optional[date] = None
    balloon_term_months: int = 0
    refinance_loan_details: Optional[LoanDetails] = None
    post_balloon_annual_increases: Dict[str, Percentage] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Format balloon analysis as a string."""
        result = f"Balloon Payment Analysis:\n"
        result += f"  Balloon Amount: {self.balloon_amount}\n"
        result += f"  Balloon Date: {self.balloon_date}\n"
        result += f"  Balloon Term: {self.balloon_term_months} months\n"
        result += f"  Pre-Balloon Monthly Cash Flow: {self.pre_balloon_cash_flow}\n"
        result += f"  Post-Balloon Monthly Cash Flow: {self.post_balloon_cash_flow}\n"
        
        if self.refinance_loan_details:
            result += f"\nRefinance Loan Details:\n"
            result += f"  Amount: {self.refinance_loan_details.amount}\n"
            result += f"  Interest Rate: {self.refinance_loan_details.interest_rate}\n"
            result += f"  Term: {self.refinance_loan_details.term} months\n"
            result += f"  Monthly Payment: {self.refinance_loan_details.calculate_payment().total}\n"
        
        if self.post_balloon_annual_increases:
            result += f"\nPost-Balloon Annual Increases:\n"
            for name, percentage in self.post_balloon_annual_increases.items():
                result += f"  {name}: {percentage}\n"
        
        return result

@dataclass
class LeaseOptionCalculation:
    """
    Lease option specific calculations.
    
    This class provides detailed calculations for lease option investments,
    including rent credits, effective purchase price, and option consideration.
    
    Attributes:
        monthly_rent: Monthly rent amount
        monthly_rent_credit: Monthly rent credit amount
        option_term_months: Option term in months
        strike_price: Strike price for the option
        option_consideration_fee: Option consideration fee
        total_rent_credits: Total rent credits over the option term
        effective_purchase_price: Effective purchase price after credits
    """
    monthly_rent: Money = field(default_factory=lambda: Money(0))
    monthly_rent_credit: Money = field(default_factory=lambda: Money(0))
    option_term_months: int = 0
    strike_price: Money = field(default_factory=lambda: Money(0))
    option_consideration_fee: Money = field(default_factory=lambda: Money(0))
    total_rent_credits: Money = field(default_factory=lambda: Money(0))
    effective_purchase_price: Money = field(default_factory=lambda: Money(0))
    
    def __str__(self) -> str:
        """Format lease option calculation as a string."""
        result = f"Lease Option Calculation:\n"
        result += f"  Monthly Rent: {self.monthly_rent}\n"
        result += f"  Monthly Rent Credit: {self.monthly_rent_credit}\n"
        result += f"  Option Term: {self.option_term_months} months\n"
        result += f"  Strike Price: {self.strike_price}\n"
        result += f"  Option Consideration Fee: {self.option_consideration_fee}\n"
        result += f"  Total Rent Credits: {self.total_rent_credits}\n"
        result += f"  Effective Purchase Price: {self.effective_purchase_price}\n"
        return result

@dataclass
class RefinanceImpactAnalysis:
    """
    Analysis of refinance impact on cash flow and investment returns.
    
    This class provides detailed analysis of how refinancing affects
    cash flow and investment returns, including before and after scenarios.
    
    Attributes:
        pre_refinance_cash_flow: Monthly cash flow before refinance
        post_refinance_cash_flow: Monthly cash flow after refinance
        monthly_savings: Monthly savings from refinance
        annual_savings: Annual savings from refinance
        closing_costs: Closing costs for refinance
        break_even_months: Months to break even on closing costs
        interest_savings: Total interest savings over loan term
        cash_out_amount: Cash out amount from refinance
        new_loan_details: Details of new loan after refinance
    """
    pre_refinance_cash_flow: Money = field(default_factory=lambda: Money(0))
    post_refinance_cash_flow: Money = field(default_factory=lambda: Money(0))
    monthly_savings: Money = field(default_factory=lambda: Money(0))
    annual_savings: Money = field(default_factory=lambda: Money(0))
    closing_costs: Money = field(default_factory=lambda: Money(0))
    break_even_months: float = 0.0
    interest_savings: Money = field(default_factory=lambda: Money(0))
    cash_out_amount: Money = field(default_factory=lambda: Money(0))
    new_loan_details: Optional[LoanDetails] = None
    
    def __str__(self) -> str:
        """Format refinance impact analysis as a string."""
        result = f"Refinance Impact Analysis:\n"
        result += f"  Pre-Refinance Monthly Cash Flow: {self.pre_refinance_cash_flow}\n"
        result += f"  Post-Refinance Monthly Cash Flow: {self.post_refinance_cash_flow}\n"
        result += f"  Monthly Savings: {self.monthly_savings}\n"
        result += f"  Annual Savings: {self.annual_savings}\n"
        result += f"  Closing Costs: {self.closing_costs}\n"
        result += f"  Break-Even Months: {self.break_even_months:.1f}\n"
        result += f"  Interest Savings: {self.interest_savings}\n"
        result += f"  Cash Out Amount: {self.cash_out_amount}\n"
        
        if self.new_loan_details:
            result += f"\nNew Loan Details:\n"
            result += f"  Amount: {self.new_loan_details.amount}\n"
            result += f"  Interest Rate: {self.new_loan_details.interest_rate}\n"
            result += f"  Term: {self.new_loan_details.term} months\n"
            result += f"  Monthly Payment: {self.new_loan_details.calculate_payment().total}\n"
        
        return result

class FinancialCalculator:
    """
    Calculator for real estate financial calculations.
    
    This class provides methods for calculating various financial metrics
    for real estate investments, including cash flow, balloon payment analysis,
    lease option calculations, and refinance impact analysis.
    """
    
    @staticmethod
    @safe_calculation(None)
    def calculate_detailed_cash_flow(data: Dict[str, Any]) -> CashFlowBreakdown:
        """
        Calculate detailed cash flow breakdown with comprehensive expense categories.
        
        Args:
            data: Dictionary containing property data
            
        Returns:
            CashFlowBreakdown object containing detailed income and expense breakdown
            
        Examples:
            >>> calculator = FinancialCalculator()
            >>> data = {
            ...     'monthly_rent': 2000,
            ...     'property_taxes': 2400,
            ...     'insurance': 1200,
            ...     'utilities': 100,
            ...     'management_fee_percentage': 10,
            ...     'capex_percentage': 5,
            ...     'vacancy_percentage': 5,
            ...     'repairs_percentage': 5,
            ...     'initial_loan_amount': 240000,
            ...     'initial_loan_interest_rate': 4.5,
            ...     'initial_loan_term': 360
            ... }
            >>> cash_flow = calculator.calculate_detailed_cash_flow(data)
            >>> print(cash_flow.net_cash_flow)
        """
        # Initialize cash flow breakdown
        breakdown = CashFlowBreakdown()
        
        # Calculate income components
        monthly_rent = Money(data.get('monthly_rent', 0) or 0)
        breakdown.income['Monthly Rent'] = monthly_rent
        
        # Add other income sources if available
        if 'parking_income' in data and data['parking_income']:
            breakdown.income['Parking Income'] = Money(data['parking_income'])
            
        if 'laundry_income' in data and data['laundry_income']:
            breakdown.income['Laundry Income'] = Money(data['laundry_income'])
            
        if 'storage_income' in data and data['storage_income']:
            breakdown.income['Storage Income'] = Money(data['storage_income'])
            
        if 'other_income' in data and data['other_income']:
            breakdown.income['Other Income'] = Money(data['other_income'])
        
        # Calculate total income
        breakdown.total_income = sum(breakdown.income.values(), Money(0))
        
        # Calculate expense components
        
        # Property taxes (annual to monthly)
        if 'property_taxes' in data and data['property_taxes']:
            breakdown.expenses['Property Taxes'] = Money(data['property_taxes']) / 12
        
        # Insurance (annual to monthly)
        if 'insurance' in data and data['insurance']:
            breakdown.expenses['Insurance'] = Money(data['insurance']) / 12
        
        # HOA/COA/Co-op fees
        if 'hoa_coa_coop' in data and data['hoa_coa_coop']:
            breakdown.expenses['HOA/COA/Co-op Fees'] = Money(data['hoa_coa_coop'])
        
        # Management fee
        if 'management_fee_percentage' in data and data['management_fee_percentage'] and 'monthly_rent' in data:
            management_fee = Money(data['monthly_rent']) * Percentage(data['management_fee_percentage']) / 100
            breakdown.expenses['Management Fee'] = management_fee
        
        # CapEx
        if 'capex_percentage' in data and data['capex_percentage'] and 'monthly_rent' in data:
            capex = Money(data['monthly_rent']) * Percentage(data['capex_percentage']) / 100
            breakdown.expenses['CapEx'] = capex
        
        # Vacancy
        if 'vacancy_percentage' in data and data['vacancy_percentage'] and 'monthly_rent' in data:
            vacancy = Money(data['monthly_rent']) * Percentage(data['vacancy_percentage']) / 100
            breakdown.expenses['Vacancy'] = vacancy
        
        # Repairs
        if 'repairs_percentage' in data and data['repairs_percentage'] and 'monthly_rent' in data:
            repairs = Money(data['monthly_rent']) * Percentage(data['repairs_percentage']) / 100
            breakdown.expenses['Repairs'] = repairs
        
        # Utilities
        if 'utilities' in data and data['utilities']:
            breakdown.expenses['Utilities'] = Money(data['utilities'])
        
        # Internet
        if 'internet' in data and data['internet']:
            breakdown.expenses['Internet'] = Money(data['internet'])
        
        # Cleaning
        if 'cleaning' in data and data['cleaning']:
            breakdown.expenses['Cleaning'] = Money(data['cleaning'])
        
        # Pest control
        if 'pest_control' in data and data['pest_control']:
            breakdown.expenses['Pest Control'] = Money(data['pest_control'])
        
        # Landscaping
        if 'landscaping' in data and data['landscaping']:
            breakdown.expenses['Landscaping'] = Money(data['landscaping'])
        
        # Snow removal
        if 'snow_removal' in data and data['snow_removal']:
            breakdown.expenses['Snow Removal'] = Money(data['snow_removal'])
        
        # Trash removal
        if 'trash_removal' in data and data['trash_removal']:
            breakdown.expenses['Trash Removal'] = Money(data['trash_removal'])
        
        # Multi-family specific expenses
        if data.get('analysis_type') == 'MultiFamily':
            # Common area maintenance
            if 'common_area_maintenance' in data and data['common_area_maintenance']:
                breakdown.expenses['Common Area Maintenance'] = Money(data['common_area_maintenance'])
            
            # Elevator maintenance
            if 'elevator_maintenance' in data and data['elevator_maintenance']:
                breakdown.expenses['Elevator Maintenance'] = Money(data['elevator_maintenance'])
            
            # Staff payroll
            if 'staff_payroll' in data and data['staff_payroll']:
                breakdown.expenses['Staff Payroll'] = Money(data['staff_payroll'])
            
            # Security
            if 'security' in data and data['security']:
                breakdown.expenses['Security'] = Money(data['security'])
        
        # Calculate total expenses
        breakdown.total_expenses = sum(breakdown.expenses.values(), Money(0))
        
        # Calculate loan payments
        
        # Initial loan
        initial_loan = FinancialCalculator._get_loan_details(data, 'initial_loan')
        if initial_loan:
            payment = initial_loan.calculate_payment()
            breakdown.loan_payments['Initial Loan'] = payment.total
        
        # Additional loans
        for i in range(1, 4):  # loans 1-3
            loan = FinancialCalculator._get_loan_details(data, f'loan{i}_loan')
            if loan:
                payment = loan.calculate_payment()
                breakdown.loan_payments[f'Loan {i}'] = payment.total
        
        # Calculate total loan payments
        breakdown.total_loan_payments = sum(breakdown.loan_payments.values(), Money(0))
        
        # Calculate net cash flow
        breakdown.net_cash_flow = breakdown.total_income - breakdown.total_expenses - breakdown.total_loan_payments
        
        return breakdown
    
    @staticmethod
    def _get_loan_details(data: Dict[str, Any], loan_prefix: str) -> Optional[LoanDetails]:
        """
        Get loan details for a specific loan.
        
        Args:
            data: Dictionary containing loan data
            loan_prefix: Prefix for loan fields (e.g., 'initial_loan', 'refinance_loan')
            
        Returns:
            LoanDetails object or None if loan amount is not specified
        """
        amount_field = f"{loan_prefix}_amount"
        
        if amount_field not in data or data[amount_field] is None:
            return None
        
        try:
            return LoanDetails(
                amount=Money(data[amount_field]),
                interest_rate=Percentage(data.get(f"{loan_prefix}_interest_rate", 0) or 0),
                term=int(data.get(f"{loan_prefix}_term", 360) or 360),
                is_interest_only=bool(data.get(f"{loan_prefix}_is_interest_only", False)),
                name=data.get(f"{loan_prefix}_name", loan_prefix.replace('_', ' ').title())
            )
        except Exception as e:
            logger.error(f"Error creating loan details for {loan_prefix}: {str(e)}")
            return None
    
    @staticmethod
    @safe_calculation(None)
    def calculate_balloon_payment_analysis(data: Dict[str, Any]) -> BalloonAnalysis:
        """
        Calculate pre-balloon and post-balloon cash flows and values.
        
        Args:
            data: Dictionary containing property data with balloon payment information
            
        Returns:
            BalloonAnalysis object containing pre-balloon and post-balloon analysis
            
        Examples:
            >>> calculator = FinancialCalculator()
            >>> data = {
            ...     'monthly_rent': 2000,
            ...     'property_taxes': 2400,
            ...     'insurance': 1200,
            ...     'initial_loan_amount': 240000,
            ...     'initial_loan_interest_rate': 4.5,
            ...     'initial_loan_term': 360,
            ...     'has_balloon_payment': True,
            ...     'balloon_term_months': 60,
            ...     'balloon_refinance_ltv_percentage': 75,
            ...     'balloon_refinance_interest_rate': 5.0,
            ...     'balloon_refinance_term': 360,
            ...     'property_value': 300000,
            ...     'appreciation_rate': 3
            ... }
            >>> balloon_analysis = calculator.calculate_balloon_payment_analysis(data)
            >>> print(balloon_analysis.balloon_amount)
        """
        # Check if balloon payment is enabled
        if not data.get('has_balloon_payment', False):
            return None
        
        # Initialize balloon analysis
        balloon_analysis = BalloonAnalysis()
        
        # Get initial loan details
        initial_loan = FinancialCalculator._get_loan_details(data, 'initial_loan')
        if not initial_loan:
            return None
        
        # Get balloon term
        balloon_term_months = int(data.get('balloon_term_months', 0) or 0)
        if balloon_term_months <= 0:
            return None
        
        balloon_analysis.balloon_term_months = balloon_term_months
        
        # Calculate balloon date
        if 'start_date' in data and data['start_date']:
            from datetime import datetime, timedelta
            start_date = datetime.fromisoformat(data['start_date']).date()
            balloon_date = start_date + timedelta(days=balloon_term_months * 30)  # Approximate
            balloon_analysis.balloon_date = balloon_date
        
        # Calculate balloon amount (remaining balance at balloon term)
        balloon_amount = initial_loan.calculate_remaining_balance(balloon_term_months)
        balloon_analysis.balloon_amount = balloon_amount
        
        # Calculate pre-balloon cash flow
        pre_balloon_data = dict(data)
        pre_balloon_cash_flow = FinancialCalculator.calculate_detailed_cash_flow(pre_balloon_data)
        balloon_analysis.pre_balloon_cash_flow = pre_balloon_cash_flow.net_cash_flow
        
        # Calculate post-balloon refinance loan
        property_value = Money(data.get('property_value', 0) or 0)
        if property_value.dollars == 0:
            # Use purchase price if property value is not specified
            property_value = Money(data.get('purchase_price', 0) or 0)
        
        # Apply appreciation to property value
        if 'appreciation_rate' in data and data['appreciation_rate']:
            appreciation_rate = Percentage(data['appreciation_rate'])
            years = balloon_term_months / 12
            for _ in range(int(years)):
                property_value = Money(float(property_value.dollars) * (1 + float(appreciation_rate.as_decimal())))
            
            # Handle partial year
            partial_year = years - int(years)
            if partial_year > 0:
                property_value = Money(float(property_value.dollars) * (1 + float(appreciation_rate.as_decimal()) * partial_year))
        
        # Calculate refinance loan amount
        refinance_ltv = Percentage(data.get('balloon_refinance_ltv_percentage', 75) or 75)
        refinance_amount = property_value * (refinance_ltv.value / 100)
        
        # Create refinance loan details
        refinance_loan = LoanDetails(
            amount=refinance_amount,
            interest_rate=Percentage(data.get('balloon_refinance_interest_rate', 0) or 0),
            term=int(data.get('balloon_refinance_term', 360) or 360),
            is_interest_only=bool(data.get('balloon_refinance_is_interest_only', False)),
            name="Refinance Loan"
        )
        balloon_analysis.refinance_loan_details = refinance_loan
        
        # Calculate post-balloon cash flow
        post_balloon_data = dict(data)
        post_balloon_data['initial_loan_amount'] = refinance_amount.dollars
        post_balloon_data['initial_loan_interest_rate'] = data.get('balloon_refinance_interest_rate', 0)
        post_balloon_data['initial_loan_term'] = data.get('balloon_refinance_term', 360)
        post_balloon_data['initial_loan_is_interest_only'] = data.get('balloon_refinance_is_interest_only', False)
        
        # Apply annual increases to post-balloon values
        post_balloon_annual_increases = {}
        
        # Rent increase
        if 'post_balloon_rent_increase_percentage' in data and data['post_balloon_rent_increase_percentage']:
            rent_increase = Percentage(data['post_balloon_rent_increase_percentage'])
            post_balloon_annual_increases['Rent'] = rent_increase
            
            # Apply rent increase to post-balloon data
            if 'monthly_rent' in post_balloon_data and post_balloon_data['monthly_rent']:
                monthly_rent = Money(post_balloon_data['monthly_rent'])
                post_balloon_data['monthly_rent'] = (monthly_rent * (1 + rent_increase.as_decimal())).dollars
        
        # Expense increase
        if 'post_balloon_expense_increase_percentage' in data and data['post_balloon_expense_increase_percentage']:
            expense_increase = Percentage(data['post_balloon_expense_increase_percentage'])
            post_balloon_annual_increases['Expenses'] = expense_increase
            
            # Apply expense increase to post-balloon data
            for expense_field in ['property_taxes', 'insurance', 'utilities', 'hoa_coa_coop', 'cleaning', 'pest_control', 'landscaping']:
                if expense_field in post_balloon_data and post_balloon_data[expense_field]:
                    expense = Money(post_balloon_data[expense_field])
                    post_balloon_data[expense_field] = (expense * (1 + expense_increase.as_decimal())).dollars
        
        balloon_analysis.post_balloon_annual_increases = post_balloon_annual_increases
        
        # Calculate post-balloon cash flow
        post_balloon_cash_flow = FinancialCalculator.calculate_detailed_cash_flow(post_balloon_data)
        balloon_analysis.post_balloon_cash_flow = post_balloon_cash_flow.net_cash_flow
        
        return balloon_analysis
    
    @staticmethod
    @safe_calculation(None)
    def calculate_lease_option_details(data: Dict[str, Any]) -> LeaseOptionCalculation:
        """
        Calculate lease option specific details.
        
        Args:
            data: Dictionary containing lease option data
            
        Returns:
            LeaseOptionCalculation object containing lease option details
            
        Examples:
            >>> calculator = FinancialCalculator()
            >>> data = {
            ...     'monthly_rent': 2000,
            ...     'monthly_rent_credit': 500,
            ...     'option_term_months': 24,
            ...     'strike_price': 300000,
            ...     'option_consideration_fee': 5000
            ... }
            >>> lease_option = calculator.calculate_lease_option_details(data)
            >>> print(lease_option.effective_purchase_price)
        """
        # Check if this is a lease option analysis
        if data.get('analysis_type') != 'LeaseOption':
            return None
        
        # Initialize lease option calculation
        lease_option = LeaseOptionCalculation()
        
        # Get basic lease option parameters
        lease_option.monthly_rent = Money(data.get('monthly_rent', 0) or 0)
        lease_option.monthly_rent_credit = Money(data.get('monthly_rent_credit', 0) or 0)
        lease_option.option_term_months = int(data.get('option_term_months', 0) or 0)
        lease_option.strike_price = Money(data.get('strike_price', 0) or 0)
        lease_option.option_consideration_fee = Money(data.get('option_consideration_fee', 0) or 0)
        
        # Calculate total rent credits
        lease_option.total_rent_credits = lease_option.monthly_rent_credit * lease_option.option_term_months
        
        # Calculate effective purchase price
        lease_option.effective_purchase_price = lease_option.strike_price - lease_option.total_rent_credits - lease_option.option_consideration_fee
        
        # Ensure effective purchase price is not negative
        lease_option.effective_purchase_price = Money(max(0, lease_option.effective_purchase_price.dollars))
        
        return lease_option
    
    @staticmethod
    @safe_calculation(None)
    def calculate_refinance_impact(data: Dict[str, Any]) -> RefinanceImpactAnalysis:
        """
        Calculate refinance impact on cash flow and investment returns.
        
        Args:
            data: Dictionary containing property data with refinance information
            
        Returns:
            RefinanceImpactAnalysis object containing refinance impact analysis
            
        Examples:
            >>> calculator = FinancialCalculator()
            >>> data = {
            ...     'monthly_rent': 2000,
            ...     'property_taxes': 2400,
            ...     'insurance': 1200,
            ...     'initial_loan_amount': 240000,
            ...     'initial_loan_interest_rate': 4.5,
            ...     'initial_loan_term': 360,
            ...     'refinance_loan_amount': 250000,
            ...     'refinance_loan_interest_rate': 3.75,
            ...     'refinance_loan_term': 360,
            ...     'refinance_closing_costs': 5000
            ... }
            >>> refinance_analysis = calculator.calculate_refinance_impact(data)
            >>> print(refinance_analysis.monthly_savings)
        """
        # Check if refinance data is available
        if 'refinance_loan_amount' not in data or not data['refinance_loan_amount']:
            return None
        
        # Initialize refinance impact analysis
        refinance_analysis = RefinanceImpactAnalysis()
        
        # Get initial loan details
        initial_loan = FinancialCalculator._get_loan_details(data, 'initial_loan')
        if not initial_loan:
            return None
        
        # Get refinance loan details
        refinance_loan = FinancialCalculator._get_loan_details(data, 'refinance_loan')
        if not refinance_loan:
            return None
        
        refinance_analysis.new_loan_details = refinance_loan
        
        # Get closing costs
        refinance_analysis.closing_costs = Money(data.get('refinance_closing_costs', 0) or 0)
        
        # Calculate cash out amount
        refinance_analysis.cash_out_amount = refinance_loan.amount - initial_loan.amount
        
        # Calculate pre-refinance cash flow
        pre_refinance_data = dict(data)
        pre_refinance_cash_flow = FinancialCalculator.calculate_detailed_cash_flow(pre_refinance_data)
        refinance_analysis.pre_refinance_cash_flow = pre_refinance_cash_flow.net_cash_flow
        
        # Calculate post-refinance cash flow
        post_refinance_data = dict(data)
        post_refinance_data['initial_loan_amount'] = refinance_loan.amount.dollars
        post_refinance_data['initial_loan_interest_rate'] = refinance_loan.interest_rate.value
        post_refinance_data['initial_loan_term'] = refinance_loan.term
        post_refinance_data['initial_loan_is_interest_only'] = refinance_loan.is_interest_only
        
        # Remove any additional loans if cash-out refinance
        if refinance_analysis.cash_out_amount.dollars > 0:
            for i in range(1, 4):
                loan_prefix = f'loan{i}_loan'
                if f'{loan_prefix}_amount' in post_refinance_data:
                    post_refinance_data[f'{loan_prefix}_amount'] = 0
        
        post_refinance_cash_flow = FinancialCalculator.calculate_detailed_cash_flow(post_refinance_data)
        refinance_analysis.post_refinance_cash_flow = post_refinance_cash_flow.net_cash_flow
        
        # Calculate monthly savings
        refinance_analysis.monthly_savings = refinance_analysis.post_refinance_cash_flow - refinance_analysis.pre_refinance_cash_flow
        
        # Calculate annual savings
        refinance_analysis.annual_savings = refinance_analysis.monthly_savings * 12
        
        # Calculate break-even months
        if refinance_analysis.monthly_savings.dollars <= 0:
            refinance_analysis.break_even_months = float('inf')
        else:
            refinance_analysis.break_even_months = refinance_analysis.closing_costs.dollars / refinance_analysis.monthly_savings.dollars
        
        # Calculate interest savings
        initial_total_interest = (initial_loan.calculate_payment().total.dollars * initial_loan.term) - initial_loan.amount.dollars
        refinance_total_interest = (refinance_loan.calculate_payment().total.dollars * refinance_loan.term) - refinance_loan.amount.dollars
        
        # Adjust for remaining term
        if 'payments_made' in data and data['payments_made']:
            payments_made = int(data['payments_made'])
            remaining_payments = initial_loan.term - payments_made
            initial_remaining_interest = (initial_loan.calculate_payment().total.dollars * remaining_payments) - initial_loan.calculate_remaining_balance(payments_made).dollars
            refinance_analysis.interest_savings = Money(initial_remaining_interest - refinance_total_interest)
        else:
            refinance_analysis.interest_savings = Money(initial_total_interest - refinance_total_interest)
        
        return refinance_analysis
