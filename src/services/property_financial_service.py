"""
Property financial service module for the REI-Tracker application.

This module provides services for property financial tracking, including
income and expense tracking, utility expense tracking, maintenance/capex recording,
equity tracking, cash flow calculations, and comparison of actual performance to analysis projections.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, date
from collections import defaultdict

from src.models.transaction import Transaction
from src.models.property import Property, MonthlyIncome, MonthlyExpenses, Utilities
from src.models.analysis import Analysis
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.property_repository import PropertyRepository
from src.repositories.analysis_repository import AnalysisRepository
from src.services.property_access_service import PropertyAccessService

# Set up logger
logger = logging.getLogger(__name__)


class PropertyFinancialService:
    """
    Service for property financial tracking.
    
    This class provides methods for tracking property finances, including
    income, expenses, utilities, maintenance/capital expenditures,
    equity tracking, cash flow calculations, and comparison of actual performance to analysis projections.
    """
    
    # Income categories mapping
    INCOME_CATEGORIES = {
        "Rental Income": "rental_income",
        "Parking Income": "parking_income",
        "Laundry Income": "laundry_income",
        "Other Income": "other_income"
    }
    
    # Expense categories mapping
    EXPENSE_CATEGORIES = {
        "Property Tax": "property_tax",
        "Insurance": "insurance",
        "Repairs": "repairs",
        "Capital Expenditures": "capex",
        "Property Management": "property_management",
        "HOA Fees": "hoa_fees",
        "Other Expenses": "other_expenses"
    }
    
    # Utility categories mapping
    UTILITY_CATEGORIES = {
        "Water": "water",
        "Electricity": "electricity",
        "Gas": "gas",
        "Trash": "trash"
    }
    
    # Categories that should NOT be included in operating expenses
    NON_OPERATING_CATEGORIES = {
        'Asset Acquisition',     # One-time acquisition costs
        'Capital Expenditures',  # Major improvements
        'Bank/Financial Fees',   # Financing costs
        'Legal/Professional Fees',# One-time costs
        'Marketing/Advertising', # One-time costs
        'Mortgage'               # Handled separately for DSCR
    }
    
    # Categories that should NOT be included in income calculations
    NON_OPERATING_INCOME = {
        'Security Deposit',  # Not true income
        'Loan Repayment',    # Principal recovery
        'Insurance Refund',  # One-time refunds
        'Escrow Refund'      # One-time refunds
    }
    
    # Constants for data quality checks
    MAX_START_GAP_DAYS = 30  # Allow 30 days gap from purchase
    MAX_END_GAP_DAYS = 45    # Allow 45 days gap to present
    
    def __init__(self):
        """Initialize the property financial service."""
        self.transaction_repo = TransactionRepository()
        self.property_repo = PropertyRepository()
        self.analysis_repo = AnalysisRepository()
        self.property_access_service = PropertyAccessService()
    
    def update_property_financials(self, property_id: str) -> Optional[Property]:
        """
        Update property financial data based on transactions.
        
        Args:
            property_id: ID of the property to update
            
        Returns:
            Updated property if successful, None otherwise
        """
        try:
            # Get property
            property_obj = self.property_repo.get_by_id(property_id)
            if not property_obj:
                logger.error(f"Property not found: {property_id}")
                return None
            
            # Get transactions for the property
            transactions = self.transaction_repo.get_by_property(property_id)
            
            # Update income
            self._update_property_income(property_obj, transactions)
            
            # Update expenses
            self._update_property_expenses(property_obj, transactions)
            
            # Save updated property
            updated_property = self.property_repo.update(property_obj)
            
            return updated_property
            
        except Exception as e:
            logger.error(f"Error updating property financials: {str(e)}")
            raise
    
    def _update_property_income(self, property_obj: Property, transactions: List[Transaction]) -> None:
        """
        Update property income based on transactions.
        
        Args:
            property_obj: Property to update
            transactions: List of transactions for the property
        """
        # Initialize monthly income if not present
        if not property_obj.monthly_income:
            property_obj.monthly_income = MonthlyIncome()
        
        # Filter income transactions
        income_transactions = [t for t in transactions if t.type == "income"]
        
        # Group by category
        income_by_category = defaultdict(Decimal)
        income_notes = []
        
        for transaction in income_transactions:
            category = transaction.category
            
            # Map category to property field
            if category in self.INCOME_CATEGORIES:
                field = self.INCOME_CATEGORIES[category]
                income_by_category[field] += transaction.amount
            
            # Collect notes
            if transaction.description and len(transaction.description) > 0:
                income_notes.append(transaction.description)
        
        # Update property income fields
        for field, amount in income_by_category.items():
            if hasattr(property_obj.monthly_income, field):
                setattr(property_obj.monthly_income, field, amount)
        
        # Update income notes
        if income_notes:
            property_obj.monthly_income.income_notes = "; ".join(income_notes[-5:])  # Keep last 5 notes
    
    def _update_property_expenses(self, property_obj: Property, transactions: List[Transaction]) -> None:
        """
        Update property expenses based on transactions.
        
        Args:
            property_obj: Property to update
            transactions: List of transactions for the property
        """
        # Initialize monthly expenses if not present
        if not property_obj.monthly_expenses:
            property_obj.monthly_expenses = MonthlyExpenses()
        
        # Initialize utilities if not present
        if not property_obj.monthly_expenses.utilities:
            property_obj.monthly_expenses.utilities = Utilities()
        
        # Filter expense transactions
        expense_transactions = [t for t in transactions if t.type == "expense"]
        
        # Group by category
        expense_by_category = defaultdict(Decimal)
        utility_by_category = defaultdict(Decimal)
        expense_notes = []
        
        for transaction in expense_transactions:
            category = transaction.category
            
            # Map category to property field
            if category in self.EXPENSE_CATEGORIES:
                field = self.EXPENSE_CATEGORIES[category]
                expense_by_category[field] += transaction.amount
            elif category in self.UTILITY_CATEGORIES:
                field = self.UTILITY_CATEGORIES[category]
                utility_by_category[field] += transaction.amount
            
            # Collect notes
            if transaction.description and len(transaction.description) > 0:
                expense_notes.append(transaction.description)
        
        # Update property expense fields
        for field, amount in expense_by_category.items():
            if hasattr(property_obj.monthly_expenses, field):
                setattr(property_obj.monthly_expenses, field, amount)
        
        # Update utility fields
        for field, amount in utility_by_category.items():
            if hasattr(property_obj.monthly_expenses.utilities, field):
                setattr(property_obj.monthly_expenses.utilities, field, amount)
        
        # Update expense notes
        if expense_notes:
            property_obj.monthly_expenses.expense_notes = "; ".join(expense_notes[-5:])  # Keep last 5 notes
    
    def get_property_financial_summary(self, property_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get financial summary for a property.
        
        Args:
            property_id: ID of the property
            user_id: ID of the user requesting the summary
            
        Returns:
            Dictionary with financial summary
            
        Raises:
            ValueError: If the property is not found or user doesn't have access
        """
        try:
            # Check if user has access to the property
            if not self.property_access_service.can_access_property(user_id, property_id):
                raise ValueError("User does not have access to this property")
            
            # Get property
            property_obj = self.property_repo.get_by_id(property_id)
            if not property_obj:
                raise ValueError(f"Property not found: {property_id}")
            
            # Get transactions for the property
            transactions = self.transaction_repo.get_by_property(property_id)
            
            # Calculate financial summary
            summary = self._calculate_financial_summary(property_obj, transactions)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting property financial summary: {str(e)}")
            raise
    
    def _calculate_financial_summary(self, property_obj: Property, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Calculate financial summary for a property.
        
        Args:
            property_obj: Property to calculate summary for
            transactions: List of transactions for the property
            
        Returns:
            Dictionary with financial summary
        """
        # Calculate income totals
        income_total = property_obj.monthly_income.total() if property_obj.monthly_income else Decimal("0")
        
        # Calculate expense totals
        expense_total = property_obj.monthly_expenses.total() if property_obj.monthly_expenses else Decimal("0")
        
        # Calculate net cash flow
        net_cash_flow = income_total - expense_total
        
        # Calculate utility totals
        utility_total = Decimal("0")
        if property_obj.monthly_expenses and property_obj.monthly_expenses.utilities:
            utilities = property_obj.monthly_expenses.utilities
            utility_total = utilities.water + utilities.electricity + utilities.gas + utilities.trash
        
        # Calculate maintenance and capex totals
        maintenance_total = property_obj.monthly_expenses.repairs if property_obj.monthly_expenses else Decimal("0")
        capex_total = property_obj.monthly_expenses.capex if property_obj.monthly_expenses else Decimal("0")
        
        # Calculate income breakdown
        income_breakdown = {}
        if property_obj.monthly_income:
            income_breakdown = {
                "rental_income": str(property_obj.monthly_income.rental_income),
                "parking_income": str(property_obj.monthly_income.parking_income),
                "laundry_income": str(property_obj.monthly_income.laundry_income),
                "other_income": str(property_obj.monthly_income.other_income)
            }
        
        # Calculate expense breakdown
        expense_breakdown = {}
        if property_obj.monthly_expenses:
            expense_breakdown = {
                "property_tax": str(property_obj.monthly_expenses.property_tax),
                "insurance": str(property_obj.monthly_expenses.insurance),
                "repairs": str(property_obj.monthly_expenses.repairs),
                "capex": str(property_obj.monthly_expenses.capex),
                "property_management": str(property_obj.monthly_expenses.property_management),
                "hoa_fees": str(property_obj.monthly_expenses.hoa_fees),
                "other_expenses": str(property_obj.monthly_expenses.other_expenses)
            }
        
        # Calculate utility breakdown
        utility_breakdown = {}
        if property_obj.monthly_expenses and property_obj.monthly_expenses.utilities:
            utilities = property_obj.monthly_expenses.utilities
            utility_breakdown = {
                "water": str(utilities.water),
                "electricity": str(utilities.electricity),
                "gas": str(utilities.gas),
                "trash": str(utilities.trash)
            }
        
        # Create summary
        summary = {
            "property_id": property_obj.id,
            "address": property_obj.address,
            "income_total": str(income_total),
            "expense_total": str(expense_total),
            "net_cash_flow": str(net_cash_flow),
            "utility_total": str(utility_total),
            "maintenance_total": str(maintenance_total),
            "capex_total": str(capex_total),
            "income_breakdown": income_breakdown,
            "expense_breakdown": expense_breakdown,
            "utility_breakdown": utility_breakdown,
            "income_notes": property_obj.monthly_income.income_notes if property_obj.monthly_income else None,
            "expense_notes": property_obj.monthly_expenses.expense_notes if property_obj.monthly_expenses else None
        }
        
        return summary
    
    def get_all_property_financials(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get financial summaries for all properties accessible to a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of dictionaries with financial summaries
        """
        try:
            # Get properties accessible to the user
            accessible_properties = self.property_access_service.get_accessible_properties(user_id)
            
            # Calculate financial summaries
            summaries = []
            for property_obj in accessible_properties:
                # Get transactions for the property
                transactions = self.transaction_repo.get_by_property(property_obj.id)
                
                # Calculate financial summary
                summary = self._calculate_financial_summary(property_obj, transactions)
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Error getting all property financials: {str(e)}")
            raise
    
    def update_all_property_financials(self) -> int:
        """
        Update financial data for all properties.
        
        Returns:
            Number of properties updated
        """
        try:
            # Get all properties
            properties = self.property_repo.get_all()
            
            # Update each property
            updated_count = 0
            for property_obj in properties:
                if self.update_property_financials(property_obj.id):
                    updated_count += 1
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating all property financials: {str(e)}")
            raise
    
    def get_maintenance_and_capex_records(self, property_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get maintenance and capital expenditure records for a property.
        
        Args:
            property_id: ID of the property
            user_id: ID of the user requesting the records
            
        Returns:
            List of maintenance and capex transactions
            
        Raises:
            ValueError: If the property is not found or user doesn't have access
        """
        try:
            # Check if user has access to the property
            if not self.property_access_service.can_access_property(user_id, property_id):
                raise ValueError("User does not have access to this property")
            
            # Get property
            property_obj = self.property_repo.get_by_id(property_id)
            if not property_obj:
                raise ValueError(f"Property not found: {property_id}")
            
            # Get transactions for the property
            transactions = self.transaction_repo.get_by_property(property_id)
            
            # Filter maintenance and capex transactions
            maintenance_capex_transactions = [
                t for t in transactions 
                if t.type == "expense" and t.category in ["Repairs", "Capital Expenditures"]
            ]
            
            # Convert to dictionaries
            records = [t.to_dict() for t in maintenance_capex_transactions]
            
            return records
            
        except Exception as e:
            logger.error(f"Error getting maintenance and capex records: {str(e)}")
            raise
    
    def calculate_property_equity(self, property_id: str, user_id: str) -> Dict[str, Any]:
        """
        Calculate current equity for a property based on purchase price, loan balance, and estimated appreciation.
        
        Args:
            property_id: ID of the property
            user_id: ID of the user requesting the equity calculation
            
        Returns:
            Dictionary with equity details
            
        Raises:
            ValueError: If the property is not found or user doesn't have access
        """
        try:
            # Check if user has access to the property
            if not self.property_access_service.can_access_property(user_id, property_id):
                raise ValueError("User does not have access to this property")
            
            # Get property
            property_obj = self.property_repo.get_by_id(property_id)
            if not property_obj:
                raise ValueError(f"Property not found: {property_id}")
            
            # Get purchase details
            purchase_price = property_obj.purchase_price
            purchase_date = datetime.strptime(property_obj.purchase_date, "%Y-%m-%d").date()
            
            # Calculate months since purchase
            today = date.today()
            months_owned = (today.year - purchase_date.year) * 12 + (today.month - purchase_date.month)
            
            # Get loan details
            primary_loan_balance = Decimal("0")
            if property_obj.primary_loan:
                primary_loan_balance = self._calculate_loan_balance(
                    property_obj.primary_loan.amount,
                    property_obj.primary_loan.interest_rate,
                    property_obj.primary_loan.term,
                    months_owned
                )
            
            secondary_loan_balance = Decimal("0")
            if property_obj.secondary_loan:
                secondary_loan_balance = self._calculate_loan_balance(
                    property_obj.secondary_loan.amount,
                    property_obj.secondary_loan.interest_rate,
                    property_obj.secondary_loan.term,
                    months_owned
                )
            
            total_loan_balance = primary_loan_balance + secondary_loan_balance
            
            # Estimate current property value (using 3% annual appreciation as default)
            annual_appreciation_rate = Decimal("0.03")  # 3% annual appreciation
            years_owned = Decimal(str(months_owned)) / Decimal("12")
            estimated_value = purchase_price * (Decimal("1") + annual_appreciation_rate) ** years_owned
            
            # Calculate equity
            initial_equity = purchase_price - (property_obj.primary_loan.amount if property_obj.primary_loan else Decimal("0")) - (property_obj.secondary_loan.amount if property_obj.secondary_loan else Decimal("0"))
            current_equity = estimated_value - total_loan_balance
            equity_gain = current_equity - initial_equity
            
            # Calculate equity from loan paydown
            initial_loan_balance = (property_obj.primary_loan.amount if property_obj.primary_loan else Decimal("0")) + (property_obj.secondary_loan.amount if property_obj.secondary_loan else Decimal("0"))
            equity_from_loan_paydown = initial_loan_balance - total_loan_balance
            
            # Calculate equity from appreciation
            equity_from_appreciation = estimated_value - purchase_price
            
            # Calculate monthly equity gain
            monthly_equity_gain = equity_gain / Decimal(str(max(months_owned, 1)))
            
            # Calculate equity breakdown by partner
            partner_equity = {}
            for partner in property_obj.partners:
                partner_equity[partner.name] = {
                    "equity_share": str(partner.equity_share),
                    "initial_equity": str(initial_equity * partner.equity_share / Decimal("100")),
                    "current_equity": str(current_equity * partner.equity_share / Decimal("100")),
                    "equity_gain": str(equity_gain * partner.equity_share / Decimal("100"))
                }
            
            return {
                "property_id": property_obj.id,
                "address": property_obj.address,
                "purchase_price": str(purchase_price),
                "purchase_date": property_obj.purchase_date,
                "months_owned": months_owned,
                "estimated_current_value": str(estimated_value),
                "total_loan_balance": str(total_loan_balance),
                "initial_equity": str(initial_equity),
                "current_equity": str(current_equity),
                "equity_gain": str(equity_gain),
                "equity_from_loan_paydown": str(equity_from_loan_paydown),
                "equity_from_appreciation": str(equity_from_appreciation),
                "monthly_equity_gain": str(monthly_equity_gain),
                "partner_equity": partner_equity
            }
            
        except Exception as e:
            logger.error(f"Error calculating property equity: {str(e)}")
            raise
    
    def _calculate_loan_balance(self, loan_amount: Decimal, interest_rate: Decimal, loan_term: int, months_elapsed: int) -> Decimal:
        """
        Calculate the remaining balance on a loan after a certain number of months.
        
        Args:
            loan_amount: Original loan amount
            interest_rate: Annual interest rate (as a percentage)
            loan_term: Loan term in months
            months_elapsed: Number of months elapsed since loan origination
            
        Returns:
            Remaining loan balance
        """
        # Handle edge cases
        if months_elapsed >= loan_term:
            return Decimal("0")
        
        if months_elapsed <= 0:
            return loan_amount
        
        if interest_rate == Decimal("0"):
            # Simple division for zero-interest loans
            return loan_amount * (Decimal(str(loan_term - months_elapsed)) / Decimal(str(loan_term)))
        
        # Convert annual interest rate to monthly
        monthly_rate = interest_rate / Decimal("12") / Decimal("100")
        
        # Calculate remaining balance using amortization formula
        remaining_payments = loan_term - months_elapsed
        payment = self._calculate_monthly_payment(loan_amount, interest_rate, loan_term)
        
        balance = (payment / monthly_rate) * (Decimal("1") - (Decimal("1") + monthly_rate) ** (-remaining_payments))
        
        return max(Decimal("0"), balance)
    
    def _calculate_monthly_payment(self, loan_amount: Decimal, interest_rate: Decimal, loan_term: int) -> Decimal:
        """
        Calculate the monthly payment for a loan.
        
        Args:
            loan_amount: Loan amount
            interest_rate: Annual interest rate (as a percentage)
            loan_term: Loan term in months
            
        Returns:
            Monthly payment amount
        """
        # Handle zero interest case
        if interest_rate == Decimal("0"):
            return loan_amount / Decimal(str(loan_term))
        
        # Convert annual interest rate to monthly
        monthly_rate = interest_rate / Decimal("12") / Decimal("100")
        
        # Calculate monthly payment using amortization formula
        payment = loan_amount * (monthly_rate * (Decimal("1") + monthly_rate) ** loan_term) / ((Decimal("1") + monthly_rate) ** loan_term - Decimal("1"))
        
        return payment
    
    def calculate_cash_flow_metrics(self, property_id: str, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate cash flow metrics for a property based on actual transaction data.
        
        Args:
            property_id: ID of the property
            user_id: ID of the user requesting the metrics
            start_date: Optional start date for filtering transactions (YYYY-MM-DD)
            end_date: Optional end date for filtering transactions (YYYY-MM-DD)
            
        Returns:
            Dictionary with cash flow metrics
            
        Raises:
            ValueError: If the property is not found or user doesn't have access
        """
        try:
            # Check if user has access to the property
            if not self.property_access_service.can_access_property(user_id, property_id):
                raise ValueError("User does not have access to this property")
            
            # Get property
            property_obj = self.property_repo.get_by_id(property_id)
            if not property_obj:
                raise ValueError(f"Property not found: {property_id}")
            
            # Get transactions for the property
            transactions = self.transaction_repo.get_by_property(property_id)
            
            # Filter transactions by date if specified
            if start_date or end_date:
                transactions = self._filter_transactions_by_date(transactions, start_date, end_date)
            
            # Calculate monthly metrics
            monthly_metrics = self._calculate_monthly_metrics(transactions)
            
            # Calculate cash flow metrics
            metrics = self._compute_cash_flow_metrics(property_obj, monthly_metrics, transactions)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating cash flow metrics: {str(e)}")
            raise
    
    def _filter_transactions_by_date(self, transactions: List[Transaction], start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Transaction]:
        """
        Filter transactions by date range.
        
        Args:
            transactions: List of transactions to filter
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            
        Returns:
            Filtered list of transactions
        """
        filtered = transactions.copy()
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            filtered = [
                t for t in filtered
                if datetime.strptime(t.date, '%Y-%m-%d').date() >= start
            ]
            
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            filtered = [
                t for t in filtered
                if datetime.strptime(t.date, '%Y-%m-%d').date() <= end
            ]
            
        return filtered
    
    def _calculate_monthly_metrics(self, transactions: List[Transaction]) -> Dict[str, Decimal]:
        """
        Calculate average monthly metrics from transactions.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Dictionary with monthly metrics
        """
        monthly_income = {}
        monthly_expenses = {}
        monthly_mortgage = {}
        
        # Group transactions by month
        for transaction in transactions:
            month = transaction.date[:7]  # YYYY-MM
            amount = transaction.amount
            
            if transaction.type == 'income' and transaction.category not in self.NON_OPERATING_INCOME:
                monthly_income[month] = monthly_income.get(month, Decimal('0')) + amount
                
            elif transaction.type == 'expense':
                if transaction.category == 'Mortgage':
                    monthly_mortgage[month] = monthly_mortgage.get(month, Decimal('0')) + amount
                elif transaction.category not in self.NON_OPERATING_CATEGORIES:
                    monthly_expenses[month] = monthly_expenses.get(month, Decimal('0')) + amount
        
        # Calculate averages
        all_months = set(monthly_income) | set(monthly_expenses) | set(monthly_mortgage)
        num_months = len(all_months)
        
        if num_months == 0:
            return {
                'avg_monthly_income': Decimal('0'),
                'avg_monthly_expenses': Decimal('0'),
                'avg_monthly_mortgage': Decimal('0'),
                'avg_monthly_noi': Decimal('0')
            }
        
        avg_monthly_income = sum(monthly_income.values()) / Decimal(str(num_months))
        avg_monthly_expenses = sum(monthly_expenses.values()) / Decimal(str(num_months))
        avg_monthly_mortgage = sum(monthly_mortgage.values()) / Decimal(str(num_months))
        avg_monthly_noi = avg_monthly_income - avg_monthly_expenses
        
        return {
            'avg_monthly_income': avg_monthly_income,
            'avg_monthly_expenses': avg_monthly_expenses,
            'avg_monthly_mortgage': avg_monthly_mortgage,
            'avg_monthly_noi': avg_monthly_noi
        }
    
    def _compute_cash_flow_metrics(self, property_obj: Property, monthly_metrics: Dict[str, Decimal], transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Compute cash flow metrics from monthly data and property details.
        
        Args:
            property_obj: Property object
            monthly_metrics: Dictionary with monthly metrics
            transactions: List of transactions
            
        Returns:
            Dictionary with cash flow metrics
        """
        # Extract required values
        purchase_price = property_obj.purchase_price
        total_investment = self._calculate_total_investment(property_obj)
        
        # Calculate monthly NOI and cash flow
        avg_monthly_noi = monthly_metrics['avg_monthly_noi']
        avg_monthly_cash_flow = avg_monthly_noi - monthly_metrics['avg_monthly_mortgage']
        
        # Calculate DSCR
        dscr = self._calculate_dscr(avg_monthly_noi, monthly_metrics['avg_monthly_mortgage'])
        
        # Calculate Cap Rate (using annualized NOI)
        annual_noi = avg_monthly_noi * Decimal('12')
        cap_rate = (annual_noi / purchase_price * Decimal('100')) if purchase_price else None
        
        # Calculate Cash on Cash Return
        annual_cash_flow = avg_monthly_cash_flow * Decimal('12')
        cash_on_cash = (annual_cash_flow / total_investment * Decimal('100')) if total_investment else None
        
        # Calculate data quality metrics
        has_complete_history = self._has_complete_history(property_obj, transactions)
        
        return {
            'net_operating_income': {
                'monthly': str(avg_monthly_noi),
                'annual': str(annual_noi)
            },
            'total_income': {
                'monthly': str(monthly_metrics['avg_monthly_income']),
                'annual': str(monthly_metrics['avg_monthly_income'] * Decimal('12'))
            },
            'total_expenses': {
                'monthly': str(monthly_metrics['avg_monthly_expenses']),
                'annual': str(monthly_metrics['avg_monthly_expenses'] * Decimal('12'))
            },
            'cash_flow': {
                'monthly': str(avg_monthly_cash_flow),
                'annual': str(annual_cash_flow)
            },
            'cap_rate': str(cap_rate) if cap_rate is not None else None,
            'cash_on_cash_return': str(cash_on_cash) if cash_on_cash is not None else None,
            'debt_service_coverage_ratio': str(dscr) if dscr is not None else None,
            'cash_invested': str(total_investment),
            'metadata': {
                'has_complete_history': has_complete_history,
                'data_quality': {
                    'confidence_level': 'high' if has_complete_history else 'medium',
                    'refinance_info': self._calculate_refinance_impact(property_obj, transactions)
                }
            }
        }
    
    def _calculate_dscr(self, noi: Decimal, mortgage_payment: Decimal) -> Optional[Decimal]:
        """
        Calculate debt service coverage ratio.
        
        Args:
            noi: Net operating income
            mortgage_payment: Monthly mortgage payment
            
        Returns:
            Debt service coverage ratio or None if mortgage payment is zero
        """
        return noi / mortgage_payment if mortgage_payment > Decimal('0') else None
    
    def _calculate_total_investment(self, property_obj: Property) -> Decimal:
        """
        Calculate total cash invested in the property.
        
        Args:
            property_obj: Property object
            
        Returns:
            Total investment amount
        """
        total_investment = Decimal('0')
        
        # Down payment
        if property_obj.down_payment:
            total_investment += property_obj.down_payment
        
        # Closing costs
        if property_obj.closing_costs:
            total_investment += property_obj.closing_costs
        
        # Renovation costs
        if property_obj.renovation_costs:
            total_investment += property_obj.renovation_costs
        
        # Marketing costs
        if property_obj.marketing_costs:
            total_investment += property_obj.marketing_costs
        
        # Holding costs
        if property_obj.holding_costs:
            total_investment += property_obj.holding_costs
        
        return total_investment
    
    def _has_complete_history(self, property_obj: Property, transactions: List[Transaction]) -> bool:
        """
        Check if we have complete transaction history for meaningful KPI calculation.
        
        Args:
            property_obj: Property object
            transactions: List of transactions
            
        Returns:
            True if history is complete, False otherwise
        """
        if not transactions:
            return False
            
        if not property_obj.purchase_date:
            return False
            
        purchase_date = datetime.strptime(property_obj.purchase_date, '%Y-%m-%d').date()
        today = date.today()
        
        transaction_dates = [
            datetime.strptime(t.date, '%Y-%m-%d').date()
            for t in transactions
        ]
        
        if not transaction_dates:
            return False
            
        earliest_transaction = min(transaction_dates)
        latest_transaction = max(transaction_dates)
        
        has_start_coverage = (earliest_transaction - purchase_date).days <= self.MAX_START_GAP_DAYS
        has_end_coverage = (today - latest_transaction).days <= self.MAX_END_GAP_DAYS
        
        return has_start_coverage and has_end_coverage
    
    def _calculate_refinance_impact(self, property_obj: Property, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Analyze impact of refinancing on debt service.
        
        Args:
            property_obj: Property object
            transactions: List of transactions
            
        Returns:
            Dictionary with refinance impact details
        """
        mortgage_transactions = [t for t in transactions if t.category == 'Mortgage']
        
        if not mortgage_transactions:
            return {
                'has_refinanced': False,
                'original_debt_service': '0',
                'current_debt_service': '0'
            }
            
        # Sort by date and analyze patterns
        mortgage_transactions.sort(key=lambda x: x.date)
        payments = [t.amount for t in mortgage_transactions]
        
        # Look for significant changes in payment amounts
        unique_payments = set(payments)
        has_refinanced = len(unique_payments) > 1
        
        return {
            'has_refinanced': has_refinanced,
            'original_debt_service': str(payments[0]) if payments else '0',
            'current_debt_service': str(payments[-1]) if payments else '0'
        }
    
    def compare_actual_to_projected(self, property_id: str, user_id: str, analysis_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare actual property performance to analysis projections.
        
        Args:
            property_id: ID of the property
            user_id: ID of the user requesting the comparison
            analysis_id: Optional ID of the specific analysis to compare against
            
        Returns:
            Dictionary with comparison results
            
        Raises:
            ValueError: If the property is not found or user doesn't have access
        """
        try:
            # Check if user has access to the property
            if not self.property_access_service.can_access_property(user_id, property_id):
                raise ValueError("User does not have access to this property")
            
            # Get property
            property_obj = self.property_repo.get_by_id(property_id)
            if not property_obj:
                raise ValueError(f"Property not found: {property_id}")
            
            # Get actual performance metrics
            actual_metrics = self.calculate_cash_flow_metrics(property_id, user_id)
            
            # Get analysis for the property
            analyses = self._get_analyses_for_property(property_id, user_id)
            
            if not analyses:
                return {
                    'property_id': property_id,
                    'address': property_obj.address,
                    'actual_metrics': actual_metrics,
                    'projected_metrics': None,
                    'comparison': None,
                    'available_analyses': []
                }
            
            # If analysis_id is provided, use that specific analysis
            # Otherwise, use the most recent analysis
            target_analysis = None
            if analysis_id:
                target_analysis = next((a for a in analyses if a.id == analysis_id), None)
                if not target_analysis:
                    raise ValueError(f"Analysis not found: {analysis_id}")
            else:
                # Sort analyses by created_at date and get the most recent
                analyses.sort(key=lambda a: a.created_at if hasattr(a, 'created_at') else '', reverse=True)
                target_analysis = analyses[0] if analyses else None
            
            if not target_analysis:
                return {
                    'property_id': property_id,
                    'address': property_obj.address,
                    'actual_metrics': actual_metrics,
                    'projected_metrics': None,
                    'comparison': None,
                    'available_analyses': [{'id': a.id, 'name': a.analysis_name} for a in analyses]
                }
            
            # Calculate projected metrics from analysis
            projected_metrics = self._calculate_projected_metrics(target_analysis)
            
            # Compare actual vs projected
            comparison = self._compare_metrics(actual_metrics, projected_metrics)
            
            return {
                'property_id': property_id,
                'address': property_obj.address,
                'actual_metrics': actual_metrics,
                'projected_metrics': projected_metrics,
                'comparison': comparison,
                'analysis_details': {
                    'id': target_analysis.id,
                    'name': target_analysis.analysis_name,
                    'type': target_analysis.analysis_type
                },
                'available_analyses': [{'id': a.id, 'name': a.analysis_name} for a in analyses]
            }
            
        except Exception as e:
            logger.error(f"Error comparing actual to projected: {str(e)}")
            raise
    
    def _get_analyses_for_property(self, property_id: str, user_id: str) -> List[Analysis]:
        """
        Get analyses for a property.
        
        Args:
            property_id: ID of the property
            user_id: ID of the user
            
        Returns:
            List of analyses for the property
        """
        try:
            # Get property to get the address
            property_obj = self.property_repo.get_by_id(property_id)
            if not property_obj:
                return []
            
            # Get all analyses for the user
            all_analyses = self.analysis_repo.get_by_user(user_id)
            
            # Filter analyses by property address
            property_analyses = [
                a for a in all_analyses 
                if a.address == property_obj.address
            ]
            
            return property_analyses
            
        except Exception as e:
            logger.error(f"Error getting analyses for property: {str(e)}")
            return []
    
    def _calculate_projected_metrics(self, analysis: Analysis) -> Dict[str, Any]:
        """
        Calculate projected metrics from an analysis.
        
        Args:
            analysis: Analysis object
            
        Returns:
            Dictionary with projected metrics
        """
        # Calculate monthly cash flow
        monthly_cash_flow = analysis.calculate_monthly_cash_flow()
        annual_cash_flow = monthly_cash_flow * Decimal('12')
        
        # Calculate cap rate
        cap_rate = analysis.calculate_cap_rate()
        
        # Calculate cash on cash return
        cash_on_cash = analysis.calculate_cash_on_cash_return()
        
        # Calculate monthly income
        monthly_income = Decimal(str(analysis.monthly_rent or 0))
        
        # For Multi-Family, calculate income based on unit types if available
        if analysis.analysis_type == "MultiFamily" and analysis.unit_types:
            monthly_income = Decimal("0")
            for unit_type in analysis.unit_types:
                monthly_income += Decimal(str(unit_type.rent)) * Decimal(str(unit_type.count))
        
        # For PadSplit, calculate income based on room count and average rent
        if analysis.analysis_type == "PadSplit" and analysis.room_count and analysis.average_room_rent:
            monthly_income = Decimal(str(analysis.room_count)) * Decimal(str(analysis.average_room_rent))
        
        # Calculate monthly expenses (excluding mortgage)
        monthly_expenses = Decimal("0")
        
        # Property taxes
        if analysis.property_taxes:
            monthly_expenses += Decimal(str(analysis.property_taxes)) / Decimal("12")
        
        # Insurance
        if analysis.insurance:
            monthly_expenses += Decimal(str(analysis.insurance)) / Decimal("12")
        
        # HOA/COA/Co-op fees
        if analysis.hoa_coa_coop:
            monthly_expenses += Decimal(str(analysis.hoa_coa_coop))
        
        # Management fee
        if analysis.management_fee_percentage:
            monthly_expenses += monthly_income * Decimal(str(analysis.management_fee_percentage)) / Decimal("100")
        
        # CapEx
        if analysis.capex_percentage:
            monthly_expenses += monthly_income * Decimal(str(analysis.capex_percentage)) / Decimal("100")
        
        # Vacancy
        if analysis.vacancy_percentage:
            monthly_expenses += monthly_income * Decimal(str(analysis.vacancy_percentage)) / Decimal("100")
        
        # Repairs
        if analysis.repairs_percentage:
            monthly_expenses += monthly_income * Decimal(str(analysis.repairs_percentage)) / Decimal("100")
        
        # Utilities
        if analysis.utilities:
            monthly_expenses += Decimal(str(analysis.utilities))
        
        # Internet
        if analysis.internet:
            monthly_expenses += Decimal(str(analysis.internet))
        
        # Cleaning
        if analysis.cleaning:
            monthly_expenses += Decimal(str(analysis.cleaning))
        
        # Pest control
        if analysis.pest_control:
            monthly_expenses += Decimal(str(analysis.pest_control))
        
        # Landscaping
        if analysis.landscaping:
            monthly_expenses += Decimal(str(analysis.landscaping))
        
        # PadSplit platform fee
        if analysis.analysis_type == "PadSplit" and analysis.padsplit_platform_percentage:
            monthly_expenses += monthly_income * Decimal(str(analysis.padsplit_platform_percentage)) / Decimal("100")
        
        # Calculate monthly NOI
        monthly_noi = monthly_income - monthly_expenses
        
        # Calculate mortgage payment
        monthly_mortgage = Decimal("0")
        initial_loan = analysis.get_initial_loan()
        if initial_loan:
            monthly_mortgage += analysis.calculate_monthly_payment(initial_loan)
        
        # Calculate DSCR
        dscr = monthly_noi / monthly_mortgage if monthly_mortgage > Decimal("0") else None
        
        return {
            'net_operating_income': {
                'monthly': str(monthly_noi),
                'annual': str(monthly_noi * Decimal('12'))
            },
            'total_income': {
                'monthly': str(monthly_income),
                'annual': str(monthly_income * Decimal('12'))
            },
            'total_expenses': {
                'monthly': str(monthly_expenses),
                'annual': str(monthly_expenses * Decimal('12'))
            },
            'cash_flow': {
                'monthly': str(monthly_cash_flow),
                'annual': str(annual_cash_flow)
            },
            'cap_rate': str(cap_rate),
            'cash_on_cash_return': str(cash_on_cash),
            'debt_service_coverage_ratio': str(dscr) if dscr is not None else None
        }
    
    def _compare_metrics(self, actual_metrics: Dict[str, Any], projected_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare actual metrics to projected metrics.
        
        Args:
            actual_metrics: Dictionary with actual metrics
            projected_metrics: Dictionary with projected metrics
            
        Returns:
            Dictionary with comparison results
        """
        comparison = {}
        
        # Compare income
        actual_monthly_income = Decimal(actual_metrics['total_income']['monthly'])
        projected_monthly_income = Decimal(projected_metrics['total_income']['monthly'])
        income_variance = actual_monthly_income - projected_monthly_income
        income_variance_pct = (income_variance / projected_monthly_income * Decimal('100')) if projected_monthly_income else None
        
        comparison['income'] = {
            'monthly_variance': str(income_variance),
            'monthly_variance_percentage': str(income_variance_pct) if income_variance_pct is not None else None,
            'is_better_than_projected': income_variance > Decimal('0')
        }
        
        # Compare expenses
        actual_monthly_expenses = Decimal(actual_metrics['total_expenses']['monthly'])
        projected_monthly_expenses = Decimal(projected_metrics['total_expenses']['monthly'])
        expenses_variance = actual_monthly_expenses - projected_monthly_expenses
        expenses_variance_pct = (expenses_variance / projected_monthly_expenses * Decimal('100')) if projected_monthly_expenses else None
        
        comparison['expenses'] = {
            'monthly_variance': str(expenses_variance),
            'monthly_variance_percentage': str(expenses_variance_pct) if expenses_variance_pct is not None else None,
            'is_better_than_projected': expenses_variance < Decimal('0')  # Lower expenses are better
        }
        
        # Compare NOI
        actual_monthly_noi = Decimal(actual_metrics['net_operating_income']['monthly'])
        projected_monthly_noi = Decimal(projected_metrics['net_operating_income']['monthly'])
        noi_variance = actual_monthly_noi - projected_monthly_noi
        noi_variance_pct = (noi_variance / projected_monthly_noi * Decimal('100')) if projected_monthly_noi else None
        
        comparison['noi'] = {
            'monthly_variance': str(noi_variance),
            'monthly_variance_percentage': str(noi_variance_pct) if noi_variance_pct is not None else None,
            'is_better_than_projected': noi_variance > Decimal('0')
        }
        
        # Compare cash flow
        actual_monthly_cash_flow = Decimal(actual_metrics['cash_flow']['monthly'])
        projected_monthly_cash_flow = Decimal(projected_metrics['cash_flow']['monthly'])
        cash_flow_variance = actual_monthly_cash_flow - projected_monthly_cash_flow
        cash_flow_variance_pct = (cash_flow_variance / projected_monthly_cash_flow * Decimal('100')) if projected_monthly_cash_flow else None
        
        comparison['cash_flow'] = {
            'monthly_variance': str(cash_flow_variance),
            'monthly_variance_percentage': str(cash_flow_variance_pct) if cash_flow_variance_pct is not None else None,
            'is_better_than_projected': cash_flow_variance > Decimal('0')
        }
        
        # Compare cap rate
        if actual_metrics['cap_rate'] and projected_metrics['cap_rate']:
            actual_cap_rate = Decimal(actual_metrics['cap_rate'])
            projected_cap_rate = Decimal(projected_metrics['cap_rate'])
            cap_rate_variance = actual_cap_rate - projected_cap_rate
            cap_rate_variance_pct = (cap_rate_variance / projected_cap_rate * Decimal('100')) if projected_cap_rate else None
            
            comparison['cap_rate'] = {
                'variance': str(cap_rate_variance),
                'variance_percentage': str(cap_rate_variance_pct) if cap_rate_variance_pct is not None else None,
                'is_better_than_projected': cap_rate_variance > Decimal('0')
            }
        
        # Compare cash on cash return
        if actual_metrics['cash_on_cash_return'] and projected_metrics['cash_on_cash_return']:
            actual_coc = Decimal(actual_metrics['cash_on_cash_return'])
            projected_coc = Decimal(projected_metrics['cash_on_cash_return'])
            coc_variance = actual_coc - projected_coc
            coc_variance_pct = (coc_variance / projected_coc * Decimal('100')) if projected_coc else None
            
            comparison['cash_on_cash_return'] = {
                'variance': str(coc_variance),
                'variance_percentage': str(coc_variance_pct) if coc_variance_pct is not None else None,
                'is_better_than_projected': coc_variance > Decimal('0')
            }
        
        # Compare DSCR
        if actual_metrics['debt_service_coverage_ratio'] and projected_metrics['debt_service_coverage_ratio']:
            actual_dscr = Decimal(actual_metrics['debt_service_coverage_ratio'])
            projected_dscr = Decimal(projected_metrics['debt_service_coverage_ratio'])
            dscr_variance = actual_dscr - projected_dscr
            dscr_variance_pct = (dscr_variance / projected_dscr * Decimal('100')) if projected_dscr else None
            
            comparison['debt_service_coverage_ratio'] = {
                'variance': str(dscr_variance),
                'variance_percentage': str(dscr_variance_pct) if dscr_variance_pct is not None else None,
                'is_better_than_projected': dscr_variance > Decimal('0')
            }
        
        # Calculate overall performance score
        better_count = sum(1 for metric in comparison.values() if metric.get('is_better_than_projected', False))
        total_count = len(comparison)
        performance_score = (better_count / total_count * 100) if total_count > 0 else 0
        
        comparison['overall'] = {
            'performance_score': performance_score,
            'metrics_better_than_projected': better_count,
            'total_metrics_compared': total_count,
            'is_better_than_projected': performance_score >= 50
        }
        
        return comparison
