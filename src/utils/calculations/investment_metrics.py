"""
Investment metric calculators for the REI-Tracker application.

This module provides specialized calculators for real estate investment metrics,
including ROI, equity tracking with appreciation projections, and other
investment-specific calculations.
"""

from typing import Dict, Any, Optional, List, Union
from decimal import Decimal
import logging
from dataclasses import dataclass, field

from src.utils.money import Money, Percentage, MonthlyPayment
from src.utils.calculations.validation import ValidationResult, Validator, safe_calculation
from src.utils.calculations.loan_details import LoanDetails

logger = logging.getLogger(__name__)

@dataclass
class EquityProjection:
    """
    Represents equity projection for a property over time.
    
    This class tracks equity growth through loan principal paydown
    and property appreciation over a specified time period.
    
    Attributes:
        initial_equity: Initial equity in the property
        property_value: Current property value
        loan_balance: Current loan balance
        current_equity: Current equity (property_value - loan_balance)
        equity_from_appreciation: Equity gained from property appreciation
        equity_from_principal: Equity gained from loan principal paydown
        total_equity_gain: Total equity gain (appreciation + principal)
        projection_years: Number of years in the projection
        annual_appreciation_rate: Annual appreciation rate as a percentage
    """
    initial_equity: Money = field(default_factory=lambda: Money(0))
    property_value: Money = field(default_factory=lambda: Money(0))
    loan_balance: Money = field(default_factory=lambda: Money(0))
    current_equity: Money = field(default_factory=lambda: Money(0))
    equity_from_appreciation: Money = field(default_factory=lambda: Money(0))
    equity_from_principal: Money = field(default_factory=lambda: Money(0))
    total_equity_gain: Money = field(default_factory=lambda: Money(0))
    projection_years: int = 0
    annual_appreciation_rate: Percentage = field(default_factory=lambda: Percentage(0))
    
    def __str__(self) -> str:
        """Format equity projection as a string."""
        return (
            f"Initial Equity: {self.initial_equity}\n"
            f"Current Property Value: {self.property_value}\n"
            f"Current Loan Balance: {self.loan_balance}\n"
            f"Current Equity: {self.current_equity}\n"
            f"Equity from Appreciation: {self.equity_from_appreciation}\n"
            f"Equity from Principal Paydown: {self.equity_from_principal}\n"
            f"Total Equity Gain: {self.total_equity_gain}\n"
            f"Projection Years: {self.projection_years}\n"
            f"Annual Appreciation Rate: {self.annual_appreciation_rate}"
        )

@dataclass
class YearlyProjection:
    """
    Represents a single year in an equity projection.
    
    This class contains the details for a specific year in the
    equity projection timeline.
    
    Attributes:
        year: Year number (1-based)
        property_value: Property value at the end of this year
        loan_balance: Loan balance at the end of this year
        equity: Total equity at the end of this year
        equity_from_appreciation: Cumulative equity from appreciation
        equity_from_principal: Cumulative equity from principal paydown
        annual_appreciation: Appreciation amount for this year
        annual_principal_paydown: Principal paid down this year
    """
    year: int = 0
    property_value: Money = field(default_factory=lambda: Money(0))
    loan_balance: Money = field(default_factory=lambda: Money(0))
    equity: Money = field(default_factory=lambda: Money(0))
    equity_from_appreciation: Money = field(default_factory=lambda: Money(0))
    equity_from_principal: Money = field(default_factory=lambda: Money(0))
    annual_appreciation: Money = field(default_factory=lambda: Money(0))
    annual_principal_paydown: Money = field(default_factory=lambda: Money(0))

class InvestmentMetricsCalculator:
    """
    Calculator for real estate investment metrics.
    
    This class provides methods for calculating various investment metrics
    including ROI, equity projections, and other investment-specific calculations.
    """
    
    @staticmethod
    @safe_calculation(Percentage(0))
    def calculate_roi(
        initial_investment: Money,
        total_return: Money,
        time_period_years: float = 1.0
    ) -> Percentage:
        """
        Calculate Return on Investment (ROI).
        
        ROI measures the total return on an investment relative to its cost,
        annualized over the specified time period.
        
        Args:
            initial_investment: Initial investment amount
            total_return: Total return amount (profit)
            time_period_years: Time period in years
            
        Returns:
            ROI as a Percentage object
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> roi = calculator.calculate_roi(Money(100000), Money(20000), 2.0)
            >>> print(roi)  # "10.000%"
        """
        if initial_investment.dollars == 0:
            return Percentage('∞')  # Infinite return if no investment
        
        # Calculate simple ROI
        simple_roi = (total_return.dollars / initial_investment.dollars) * 100
        
        # Annualize if time period is not 1 year
        if time_period_years != 1.0:
            # Use the annualized ROI formula: (1 + ROI)^(1/n) - 1
            annualized_roi = (((1 + (simple_roi / 100)) ** (1 / time_period_years)) - 1) * 100
            return Percentage(annualized_roi)
        
        return Percentage(simple_roi)
    
    @staticmethod
    @safe_calculation(None)
    def project_equity(
        purchase_price: Money,
        current_value: Optional[Money] = None,
        loan_details: Optional[LoanDetails] = None,
        down_payment: Optional[Money] = None,
        annual_appreciation_rate: Percentage = Percentage(3),
        projection_years: int = 30,
        payments_made: int = 0
    ) -> EquityProjection:
        """
        Project equity growth over time based on appreciation and loan paydown.
        
        This method calculates how equity grows through property appreciation
        and mortgage principal paydown over a specified time period.
        
        Args:
            purchase_price: Original purchase price of the property
            current_value: Current property value (defaults to purchase_price if None)
            loan_details: Loan details object
            down_payment: Down payment amount (used if loan_details is None)
            annual_appreciation_rate: Annual appreciation rate as a percentage
            projection_years: Number of years to project
            payments_made: Number of payments already made
            
        Returns:
            EquityProjection object containing equity projection details
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> loan = LoanDetails(
            ...     amount=Money(240000),
            ...     interest_rate=Percentage(4.5),
            ...     term=360,
            ...     is_interest_only=False
            ... )
            >>> projection = calculator.project_equity(
            ...     purchase_price=Money(300000),
            ...     loan_details=loan,
            ...     annual_appreciation_rate=Percentage(3),
            ...     projection_years=30
            ... )
            >>> print(projection.total_equity_gain)
        """
        # Use purchase price as current value if not provided
        if current_value is None:
            current_value = purchase_price
        
        # Calculate initial equity
        initial_equity = Money(0)
        loan_balance = Money(0)
        
        if loan_details is not None:
            # Calculate initial equity based on loan details
            loan_balance = loan_details.calculate_remaining_balance(payments_made)
            initial_equity = current_value - loan_balance
        elif down_payment is not None:
            # Calculate initial equity based on down payment
            initial_equity = down_payment
            loan_balance = purchase_price - down_payment
        else:
            # Assume property is owned free and clear
            initial_equity = current_value
        
        # Initialize projection
        projection = EquityProjection(
            initial_equity=initial_equity,
            property_value=current_value,
            loan_balance=loan_balance,
            current_equity=initial_equity,
            projection_years=projection_years,
            annual_appreciation_rate=annual_appreciation_rate
        )
        
        # Calculate equity growth over time
        final_property_value = current_value
        final_loan_balance = loan_balance
        
        # Calculate final property value with appreciation
        for year in range(1, projection_years + 1):
            appreciation_factor = Decimal(1) + annual_appreciation_rate.as_decimal()
            final_property_value = Money(Decimal(str(final_property_value.dollars)) * appreciation_factor)
        
        # Calculate final loan balance
        if loan_details is not None:
            # Calculate remaining payments
            remaining_payments = loan_details.term - payments_made
            
            # If projection years is less than remaining loan term
            if projection_years * 12 < remaining_payments:
                final_loan_balance = loan_details.calculate_remaining_balance(
                    payments_made + (projection_years * 12)
                )
            else:
                # Loan will be paid off
                final_loan_balance = Money(0)
        
        # Calculate equity components
        equity_from_appreciation = final_property_value - current_value
        equity_from_principal = loan_balance - final_loan_balance
        total_equity_gain = equity_from_appreciation + equity_from_principal
        final_equity = final_property_value - final_loan_balance
        
        # Update projection
        projection.property_value = final_property_value
        projection.loan_balance = final_loan_balance
        projection.current_equity = final_equity
        projection.equity_from_appreciation = equity_from_appreciation
        projection.equity_from_principal = equity_from_principal
        projection.total_equity_gain = total_equity_gain
        
        return projection
    
    @staticmethod
    @safe_calculation([])
    def generate_yearly_equity_projections(
        purchase_price: Money,
        current_value: Optional[Money] = None,
        loan_details: Optional[LoanDetails] = None,
        down_payment: Optional[Money] = None,
        annual_appreciation_rate: Percentage = Percentage(3),
        projection_years: int = 30,
        payments_made: int = 0
    ) -> List[YearlyProjection]:
        """
        Generate year-by-year equity projections.
        
        This method provides a detailed breakdown of equity growth
        for each year in the projection period.
        
        Args:
            purchase_price: Original purchase price of the property
            current_value: Current property value (defaults to purchase_price if None)
            loan_details: Loan details object
            down_payment: Down payment amount (used if loan_details is None)
            annual_appreciation_rate: Annual appreciation rate as a percentage
            projection_years: Number of years to project
            payments_made: Number of payments already made
            
        Returns:
            List of YearlyProjection objects, one for each year
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> loan = LoanDetails(
            ...     amount=Money(240000),
            ...     interest_rate=Percentage(4.5),
            ...     term=360,
            ...     is_interest_only=False
            ... )
            >>> projections = calculator.generate_yearly_equity_projections(
            ...     purchase_price=Money(300000),
            ...     loan_details=loan,
            ...     annual_appreciation_rate=Percentage(3),
            ...     projection_years=5
            ... )
            >>> for year in projections:
            ...     print(f"Year {year.year}: Equity ${year.equity.dollars:.2f}")
        """
        # Use purchase price as current value if not provided
        if current_value is None:
            current_value = purchase_price
        
        # Calculate initial values
        property_value = current_value
        loan_balance = Money(0)
        
        if loan_details is not None:
            # Calculate initial loan balance based on loan details
            loan_balance = loan_details.calculate_remaining_balance(payments_made)
        elif down_payment is not None:
            # Calculate initial loan balance based on down payment
            loan_balance = purchase_price - down_payment
        
        # Initial equity
        initial_equity = property_value - loan_balance
        
        # Initialize projections list
        projections = []
        
        # Track cumulative values
        cumulative_appreciation = Money(0)
        cumulative_principal = Money(0)
        previous_loan_balance = loan_balance
        
        # Generate projection for each year
        for year in range(1, projection_years + 1):
            # Calculate property appreciation for this year
            appreciation_factor = Decimal(1) + annual_appreciation_rate.as_decimal()
            new_property_value = Money(Decimal(str(property_value.dollars)) * appreciation_factor)
            annual_appreciation = new_property_value - property_value
            
            # Update cumulative appreciation
            cumulative_appreciation += annual_appreciation
            
            # Calculate loan balance at the end of this year
            new_loan_balance = Money(0)
            annual_principal_paydown = Money(0)
            
            if loan_details is not None:
                # Calculate remaining payments
                current_payment = payments_made + (year * 12)
                
                if current_payment < loan_details.term:
                    new_loan_balance = loan_details.calculate_remaining_balance(current_payment)
                    annual_principal_paydown = previous_loan_balance - new_loan_balance
                else:
                    # Loan is paid off
                    annual_principal_paydown = previous_loan_balance
            
            # Update cumulative principal paydown
            cumulative_principal += annual_principal_paydown
            
            # Calculate equity at the end of this year
            equity = new_property_value - new_loan_balance
            
            # Create yearly projection
            yearly_projection = YearlyProjection(
                year=year,
                property_value=new_property_value,
                loan_balance=new_loan_balance,
                equity=equity,
                equity_from_appreciation=cumulative_appreciation,
                equity_from_principal=cumulative_principal,
                annual_appreciation=annual_appreciation,
                annual_principal_paydown=annual_principal_paydown
            )
            
            # Add to projections list
            projections.append(yearly_projection)
            
            # Update values for next iteration
            property_value = new_property_value
            previous_loan_balance = new_loan_balance
        
        return projections
    
    @staticmethod
    @safe_calculation(0.0)
    def calculate_gross_rent_multiplier(purchase_price: Money, annual_rent: Money) -> float:
        """
        Calculate Gross Rent Multiplier (GRM).
        
        GRM is the ratio of a property's purchase price to its annual rental income.
        It's a simple metric used to compare different rental properties.
        
        Args:
            purchase_price: Property purchase price
            annual_rent: Annual rental income
            
        Returns:
            GRM as a float
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> grm = calculator.calculate_gross_rent_multiplier(
            ...     Money(300000),
            ...     Money(30000)
            ... )
            >>> print(f"GRM: {grm:.2f}")  # "GRM: 10.00"
        """
        if annual_rent.dollars == 0:
            return 0.0
        
        return purchase_price.dollars / annual_rent.dollars
    
    @staticmethod
    @safe_calculation(Money(0))
    def calculate_price_per_unit(purchase_price: Money, unit_count: int) -> Money:
        """
        Calculate price per unit for multi-family properties.
        
        This metric helps compare different multi-family properties
        by normalizing the price based on the number of units.
        
        Args:
            purchase_price: Property purchase price
            unit_count: Number of units in the property
            
        Returns:
            Price per unit as a Money object
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> price_per_unit = calculator.calculate_price_per_unit(
            ...     Money(1000000),
            ...     4
            ... )
            >>> print(price_per_unit)  # "$250,000.00"
        """
        if unit_count <= 0:
            return Money(0)
        
        return Money(purchase_price.dollars / unit_count)
    
    @staticmethod
    @safe_calculation(Percentage(0))
    def calculate_cash_on_cash_return(annual_cash_flow: Money, total_investment: Money) -> Percentage:
        """
        Calculate Cash-on-Cash Return.
        
        Cash-on-Cash Return measures the annual pre-tax cash flow relative to
        the total cash invested in a property.
        
        Args:
            annual_cash_flow: Annual pre-tax cash flow
            total_investment: Total cash invested
            
        Returns:
            Cash-on-Cash Return as a Percentage object
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> coc = calculator.calculate_cash_on_cash_return(
            ...     Money(12000),
            ...     Money(100000)
            ... )
            >>> print(coc)  # "12.000%"
        """
        if total_investment.dollars == 0:
            return Percentage('∞')  # Infinite return if no investment
        
        return Percentage((annual_cash_flow.dollars / total_investment.dollars) * 100)
    
    @staticmethod
    @safe_calculation(Percentage(0))
    def calculate_cap_rate(annual_noi: Money, property_value: Money) -> Percentage:
        """
        Calculate Capitalization Rate (Cap Rate).
        
        Cap Rate measures the rate of return on a real estate investment property
        based on the expected income the property will generate.
        
        Args:
            annual_noi: Annual Net Operating Income
            property_value: Current property value
            
        Returns:
            Cap Rate as a Percentage object
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> cap_rate = calculator.calculate_cap_rate(
            ...     Money(24000),
            ...     Money(300000)
            ... )
            >>> print(cap_rate)  # "8.000%"
        """
        if property_value.dollars == 0:
            return Percentage(0)
        
        return Percentage((annual_noi.dollars / property_value.dollars) * 100)
    
    @staticmethod
    @safe_calculation(0.0)
    def calculate_debt_service_coverage_ratio(annual_noi: Money, annual_debt_service: Money) -> float:
        """
        Calculate Debt Service Coverage Ratio (DSCR).
        
        DSCR measures the property's ability to cover its debt obligations
        with its net operating income.
        
        Args:
            annual_noi: Annual Net Operating Income
            annual_debt_service: Annual debt service (loan payments)
            
        Returns:
            DSCR as a float
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> dscr = calculator.calculate_debt_service_coverage_ratio(
            ...     Money(24000),
            ...     Money(18000)
            ... )
            >>> print(f"DSCR: {dscr:.2f}")  # "DSCR: 1.33"
        """
        if annual_debt_service.dollars == 0:
            return float('inf')  # Infinite DSCR if no debt service
        
        return annual_noi.dollars / annual_debt_service.dollars
    
    @staticmethod
    @safe_calculation(Percentage(0))
    def calculate_expense_ratio(annual_expenses: Money, annual_income: Money) -> Percentage:
        """
        Calculate Expense Ratio.
        
        Expense Ratio measures the percentage of gross income that goes toward
        operating expenses.
        
        Args:
            annual_expenses: Annual operating expenses
            annual_income: Annual gross income
            
        Returns:
            Expense Ratio as a Percentage object
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> expense_ratio = calculator.calculate_expense_ratio(
            ...     Money(12000),
            ...     Money(30000)
            ... )
            >>> print(expense_ratio)  # "40.000%"
        """
        if annual_income.dollars == 0:
            return Percentage(0)
        
        return Percentage((annual_expenses.dollars / annual_income.dollars) * 100)
    
    @staticmethod
    @safe_calculation(Percentage(0))
    def calculate_breakeven_occupancy(annual_expenses: Money, annual_debt_service: Money, annual_potential_income: Money) -> Percentage:
        """
        Calculate Breakeven Occupancy Rate.
        
        Breakeven Occupancy Rate is the occupancy rate at which a property's
        income equals its expenses and debt service.
        
        Args:
            annual_expenses: Annual operating expenses
            annual_debt_service: Annual debt service (loan payments)
            annual_potential_income: Annual potential gross income at 100% occupancy
            
        Returns:
            Breakeven Occupancy Rate as a Percentage object
            
        Examples:
            >>> calculator = InvestmentMetricsCalculator()
            >>> breakeven = calculator.calculate_breakeven_occupancy(
            ...     Money(12000),
            ...     Money(18000),
            ...     Money(36000)
            ... )
            >>> print(breakeven)  # "83.333%"
        """
        if annual_potential_income.dollars == 0:
            return Percentage(100)  # 100% occupancy needed if no income
        
        total_expenses = annual_expenses.dollars + annual_debt_service.dollars
        breakeven = (total_expenses / annual_potential_income.dollars) * 100
        
        # Cap at 100%
        if breakeven > 100:
            return Percentage(100)
        return Percentage(breakeven)
