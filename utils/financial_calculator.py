from decimal import Decimal
from typing import Union, Optional, Dict, Any
import logging
from utils.money import Money, Percentage, MonthlyPayment, ensure_money, ensure_percentage
from utils.error_handling import safe_calculation

logger = logging.getLogger(__name__)


class FinancialCalculator:
    """Centralized calculator for all real estate financial metrics."""
    
    @staticmethod
    @safe_calculation(default_value=MonthlyPayment(Money(0), Money(0), Money(0)))
    def calculate_loan_payment(loan_amount: Union[Money, Decimal, float], 
                              annual_rate: Union[Percentage, Decimal, float], 
                              term: Union[int, str],
                              is_interest_only: bool = False) -> MonthlyPayment:
        """
        Calculate monthly payment for a loan.
        
        Args:
            loan_amount: Principal loan amount
            annual_rate: Annual interest rate as a percentage
            term: Loan term in months
            is_interest_only: Whether the loan is interest-only
            
        Returns:
            MonthlyPayment object containing payment details
        """
        # Ensure inputs are proper types
        loan_amount = ensure_money(loan_amount)
        annual_rate = ensure_percentage(annual_rate)
            
        # Convert term to integer
        try:
            term = int(float(str(term)))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid loan term: {term}")

        if term <= 0 or loan_amount.dollars <= 0:
            return MonthlyPayment(
                total=Money(0),
                principal=Money(0),
                interest=Money(0)
            )

        # Convert annual rate to monthly decimal
        monthly_rate = annual_rate.as_decimal() / Decimal('12')
        
        # Handle zero interest rate
        if monthly_rate == 0:
            # Convert term to float before dividing
            monthly_payment = loan_amount.dollars / float(term)
            return MonthlyPayment(
                total=Money(monthly_payment),
                interest=Money(0)
            )
        
        # Handle interest-only loans
        if is_interest_only:
            # Convert monthly_rate to float before multiplying with dollars
            monthly_interest = loan_amount.dollars * float(monthly_rate)
            return MonthlyPayment(
                total=Money(monthly_interest),
                principal=Money(0),
                interest=Money(monthly_interest)
            )

        # Standard mortgage payment formula for amortizing loans
        payment_factor = (
            monthly_rate * (1 + monthly_rate) ** term
        ) / (
            (1 + monthly_rate) ** term - 1
        )

        # Convert payment_factor to float before multiplying with dollars
        monthly_payment = loan_amount.dollars * float(payment_factor)

        # Calculate first month's principal and interest
        # Convert monthly_rate to float before multiplying with dollars
        monthly_interest = loan_amount.dollars * float(monthly_rate)
        monthly_principal = monthly_payment - monthly_interest
        
        return MonthlyPayment(
            total=Money(monthly_payment),
            principal=Money(monthly_principal),
            interest=Money(monthly_interest)
        )
        
    @staticmethod
    @safe_calculation(default_value=Percentage(0))
    def calculate_cash_on_cash_return(annual_cash_flow: Union[Money, Decimal, float], 
                                     total_investment: Union[Money, Decimal, float]) -> Union[Percentage, str]:
        """
        Calculate cash-on-cash return.
        
        Args:
            annual_cash_flow: Annual cash flow
            total_investment: Total cash invested
            
        Returns:
            Percentage: The calculated cash on cash return percentage
            str: "Infinite" if the cash invested is zero or negative
        """
        # Ensure inputs are proper types
        annual_cash_flow = ensure_money(annual_cash_flow)
        total_investment = ensure_money(total_investment)
        
        # Special case: Zero or negative cash invested means infinite return
        if total_investment.dollars <= 0:
            logger.debug("Cash invested is zero or negative, returning 'Infinite' for cash-on-cash return")
            return "Infinite"
        
        # Normal calculation
        return Percentage((float(annual_cash_flow.dollars) / float(total_investment.dollars)) * 100)
        
    @staticmethod
    @safe_calculation(default_value=Percentage(0))
    def calculate_cap_rate(annual_noi: Union[Money, Decimal, float],
                          property_value: Union[Money, Decimal, float]) -> Percentage:
        """
        Calculate capitalization rate.
        
        Args:
            annual_noi: Annual Net Operating Income
            property_value: Property value or purchase price
            
        Returns:
            Percentage: The calculated cap rate
        """
        # Ensure inputs are proper types
        annual_noi = ensure_money(annual_noi)
        property_value = ensure_money(property_value)
            
        if property_value.dollars <= 0:
            return Percentage(0)
            
        return Percentage((float(annual_noi.dollars) / float(property_value.dollars)) * 100)
        
    @staticmethod
    @safe_calculation(default_value=Money(0))
    def calculate_noi(income: Union[Money, Decimal, float],
                     expenses: Union[Money, Decimal, float]) -> Money:
        """
        Calculate Net Operating Income.
        
        Args:
            income: Total income
            expenses: Operating expenses (excluding debt service)
            
        Returns:
            Money: The calculated NOI
        """
        # Ensure inputs are proper types
        income = ensure_money(income)
        expenses = ensure_money(expenses)
            
        return income - expenses
        
    @staticmethod
    @safe_calculation(default_value=0)
    def calculate_dscr(noi: Union[Money, Decimal, float],
                      debt_service: Union[Money, Decimal, float]) -> float:
        """
        Calculate Debt Service Coverage Ratio.
        
        Args:
            noi: Net Operating Income
            debt_service: Total debt service (loan payments)
            
        Returns:
            float: The calculated DSCR
        """
        # Ensure inputs are proper types
        noi = ensure_money(noi)
        debt_service = ensure_money(debt_service)
            
        if debt_service.dollars <= 0:
            return 0
            
        return float(noi.dollars) / float(debt_service.dollars)
        
    @staticmethod
    @safe_calculation(default_value=Money(0))
    def calculate_mao(arv: Union[Money, Decimal, float],
                     renovation_costs: Union[Money, Decimal, float],
                     closing_costs: Union[Money, Decimal, float] = 0,
                     holding_costs: Union[Money, Decimal, float] = 0,
                     ltv_percentage: Union[Percentage, Decimal, float] = 75,
                     max_cash_left: Union[Money, Decimal, float] = 10000) -> Money:
        """
        Calculate Maximum Allowable Offer.
        
        Args:
            arv: After Repair Value
            renovation_costs: Estimated renovation costs
            closing_costs: Closing costs
            holding_costs: Holding costs during renovation
            ltv_percentage: Loan-to-Value percentage for refinance
            max_cash_left: Maximum cash left in the deal
            
        Returns:
            Money: The calculated Maximum Allowable Offer
        """
        # Ensure inputs are proper types
        arv = ensure_money(arv)
        renovation_costs = ensure_money(renovation_costs)
        closing_costs = ensure_money(closing_costs)
        holding_costs = ensure_money(holding_costs)
        ltv_percentage = ensure_percentage(ltv_percentage)
        max_cash_left = ensure_money(max_cash_left)
            
        # Calculate target loan amount based on ARV and LTV
        target_loan = arv * ltv_percentage
        
        # Calculate MAO
        mao = target_loan - (renovation_costs + holding_costs + closing_costs + max_cash_left)
        
        return Money(max(0, float(mao.dollars)))
        
    @staticmethod
    @safe_calculation(default_value=Percentage(0))
    def calculate_expense_ratio(expenses: Union[Money, Decimal, float],
                              income: Union[Money, Decimal, float]) -> Percentage:
        """
        Calculate expense ratio.
        
        Args:
            expenses: Operating expenses
            income: Total income
            
        Returns:
            Percentage: The calculated expense ratio
        """
        # Ensure inputs are proper types
        expenses = ensure_money(expenses)
        income = ensure_money(income)
            
        if income.dollars <= 0:
            return Percentage(0)
            
        return Percentage((float(expenses.dollars) / float(income.dollars)) * 100)
        
    @staticmethod
    @safe_calculation(default_value=0)
    def calculate_gross_rent_multiplier(purchase_price: Union[Money, Decimal, float],
                                      annual_rent: Union[Money, Decimal, float]) -> float:
        """
        Calculate Gross Rent Multiplier.
        
        Args:
            purchase_price: Property purchase price
            annual_rent: Annual gross rent
            
        Returns:
            float: The calculated GRM
        """
        # Ensure inputs are proper types
        purchase_price = ensure_money(purchase_price)
        annual_rent = ensure_money(annual_rent)
            
        if annual_rent.dollars <= 0:
            return 0
            
        return float(purchase_price.dollars) / float(annual_rent.dollars)
