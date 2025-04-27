from typing import List, Dict, Optional, Any, Tuple
from datetime import date, timedelta
import logging
from src.models.loan import Loan, LoanType, LoanStatus, BalloonPayment
from src.repositories.loan_repository import LoanRepository
from src.utils.money import Money, Percentage, MonthlyPayment
from src.utils.calculations.loan_details import LoanDetails

logger = logging.getLogger(__name__)

class LoanService:
    """
    Service for managing loans and loan-related operations.
    
    This class provides methods for creating, updating, and analyzing loans,
    as well as generating amortization schedules and comparing loan options.
    """
    
    def __init__(self, loan_repository: Optional[LoanRepository] = None):
        """
        Initialize the loan service.
        
        Args:
            loan_repository: Repository for loan data access (creates one if not provided)
        """
        self.loan_repository = loan_repository or LoanRepository()
    
    def get_loans_by_property(self, property_id: str) -> List[Loan]:
        """
        Get all loans associated with a property.
        
        Args:
            property_id: ID of the property
            
        Returns:
            List[Loan]: List of loans for the property
        """
        return self.loan_repository.get_loans_by_property(property_id)
    
    def get_active_loans_by_property(self, property_id: str) -> List[Loan]:
        """
        Get all active loans associated with a property.
        
        Args:
            property_id: ID of the property
            
        Returns:
            List[Loan]: List of active loans for the property
        """
        return self.loan_repository.get_active_loans_by_property(property_id)
    
    def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        """
        Get a loan by its ID.
        
        Args:
            loan_id: ID of the loan
            
        Returns:
            Optional[Loan]: The loan if found, None otherwise
        """
        return self.loan_repository.get_loan_by_id(loan_id)
    
    def create_loan(self, loan_data: Dict[str, Any]) -> Loan:
        """
        Create a new loan.
        
        Args:
            loan_data: Dictionary containing loan data
            
        Returns:
            Loan: The created loan
        """
        # Validate the loan data before creating
        self._validate_loan_data(loan_data)
        
        # Create the loan
        return self.loan_repository.create_loan(loan_data)
    
    def update_loan(self, loan_id: str, loan_data: Dict[str, Any]) -> Optional[Loan]:
        """
        Update an existing loan.
        
        Args:
            loan_id: ID of the loan to update
            loan_data: Dictionary containing updated loan data
            
        Returns:
            Optional[Loan]: The updated loan if found, None otherwise
        """
        # Validate the loan data before updating
        self._validate_loan_data(loan_data, partial=True)
        
        # Update the loan
        return self.loan_repository.update_loan(loan_id, loan_data)
    
    def delete_loan(self, loan_id: str) -> bool:
        """
        Delete a loan.
        
        Args:
            loan_id: ID of the loan to delete
            
        Returns:
            bool: True if the loan was deleted, False otherwise
        """
        return self.loan_repository.delete_loan(loan_id)
    
    def refinance_loan(self, old_loan_id: str, new_loan_data: Dict[str, Any]) -> Optional[Loan]:
        """
        Refinance an existing loan.
        
        Args:
            old_loan_id: ID of the loan being refinanced
            new_loan_data: Dictionary containing data for the new loan
            
        Returns:
            Optional[Loan]: The new loan if successful, None otherwise
        """
        # Validate the new loan data
        self._validate_loan_data(new_loan_data)
        
        # Perform the refinance
        return self.loan_repository.refinance_loan(old_loan_id, new_loan_data)
    
    def pay_off_loan(self, loan_id: str, payoff_date: Optional[date] = None) -> Optional[Loan]:
        """
        Mark a loan as paid off.
        
        Args:
            loan_id: ID of the loan to pay off
            payoff_date: Date when the loan was paid off (defaults to today)
            
        Returns:
            Optional[Loan]: The updated loan if found, None otherwise
        """
        return self.loan_repository.pay_off_loan(loan_id, payoff_date)
    
    def update_loan_balance(self, loan_id: str, as_of_date: Optional[date] = None) -> Optional[Loan]:
        """
        Update the current balance of a loan.
        
        Args:
            loan_id: ID of the loan to update
            as_of_date: Date to calculate the balance for (defaults to today)
            
        Returns:
            Optional[Loan]: The updated loan if found, None otherwise
        """
        return self.loan_repository.update_loan_balance(loan_id, as_of_date)
    
    def get_total_debt_for_property(self, property_id: str, as_of_date: Optional[date] = None) -> Money:
        """
        Calculate the total debt for a property across all active loans.
        
        Args:
            property_id: ID of the property
            as_of_date: Date to calculate the balance for (defaults to today)
            
        Returns:
            Money: The total debt amount
        """
        return self.loan_repository.get_total_debt_for_property(property_id, as_of_date)
    
    def get_total_monthly_payment_for_property(self, property_id: str) -> Money:
        """
        Calculate the total monthly payment for a property across all active loans.
        
        Args:
            property_id: ID of the property
            
        Returns:
            Money: The total monthly payment amount
        """
        return self.loan_repository.get_total_monthly_payment_for_property(property_id)
    
    def generate_amortization_schedule(self, loan_id: str, max_periods: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate an amortization schedule for a loan.
        
        Args:
            loan_id: ID of the loan
            max_periods: Maximum number of periods to generate (defaults to full term)
            
        Returns:
            List[Dict]: A list of dictionaries containing payment details for each period
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return []
            
        return loan.generate_amortization_schedule(max_periods)
    
    def compare_loans(self, loan_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple loan options and provide analysis.
        
        Args:
            loan_options: List of dictionaries containing loan data for comparison
            
        Returns:
            Dict: Comparison results with metrics for each loan option
        """
        if not loan_options:
            return {}
            
        comparison = {
            'loans': [],
            'summary': {}
        }
        
        # Create temporary loan objects for each option
        loans = []
        for option_data in loan_options:
            try:
                # Create a loan object without saving to the repository
                loan = Loan.from_dict(option_data)
                loan_details = loan.to_loan_details()
                
                # Calculate key metrics
                monthly_payment = loan_details.calculate_payment().total
                total_payments = monthly_payment.dollars * loan.term_months
                total_interest = total_payments - loan.amount.dollars
                
                # Add to comparison
                loans.append(loan)
                comparison['loans'].append({
                    'name': loan.name or f"Option {len(loans)}",
                    'amount': str(loan.amount),
                    'interest_rate': str(loan.interest_rate),
                    'term_months': loan.term_months,
                    'is_interest_only': loan.is_interest_only,
                    'monthly_payment': str(monthly_payment),
                    'total_payments': f"${total_payments:,.2f}",
                    'total_interest': f"${total_interest:,.2f}",
                    'has_balloon': loan.balloon_payment is not None
                })
            except Exception as e:
                logger.error(f"Error processing loan option: {str(e)}")
                continue
                
        # Calculate summary metrics
        if loans:
            # Find the loan with the lowest monthly payment
            lowest_payment_idx = 0
            lowest_payment = float('inf')
            
            # Find the loan with the lowest total interest
            lowest_interest_idx = 0
            lowest_interest = float('inf')
            
            for i, loan in enumerate(loans):
                loan_details = loan.to_loan_details()
                monthly_payment = loan_details.calculate_payment().total.dollars
                total_payments = monthly_payment * loan.term_months
                total_interest = total_payments - loan.amount.dollars
                
                if monthly_payment < lowest_payment:
                    lowest_payment = monthly_payment
                    lowest_payment_idx = i
                    
                if total_interest < lowest_interest:
                    lowest_interest = total_interest
                    lowest_interest_idx = i
                    
            comparison['summary'] = {
                'lowest_payment': {
                    'loan_name': comparison['loans'][lowest_payment_idx]['name'],
                    'amount': comparison['loans'][lowest_payment_idx]['monthly_payment']
                },
                'lowest_interest': {
                    'loan_name': comparison['loans'][lowest_interest_idx]['name'],
                    'amount': comparison['loans'][lowest_interest_idx]['total_interest']
                }
            }
            
        return comparison
    
    def calculate_balloon_payment(self, loan_id: str, balloon_term_months: int) -> Dict[str, Any]:
        """
        Calculate balloon payment details for a loan.
        
        Args:
            loan_id: ID of the loan
            balloon_term_months: Number of months until the balloon payment
            
        Returns:
            Dict: Balloon payment details
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return {}
            
        # Create a loan details object
        loan_details = loan.to_loan_details()
        
        # Calculate the remaining balance after the balloon term
        remaining_balance = loan_details.calculate_remaining_balance(balloon_term_months)
        
        # Calculate the monthly payment
        monthly_payment = loan_details.calculate_payment().total
        
        # Calculate the balloon date
        balloon_date = loan.start_date
        years_to_add = balloon_term_months // 12
        months_to_add = balloon_term_months % 12
        
        balloon_year = balloon_date.year + years_to_add
        balloon_month = balloon_date.month + months_to_add
        
        if balloon_month > 12:
            balloon_year += 1
            balloon_month -= 12
            
        balloon_day = min(balloon_date.day, 28)  # Avoid invalid dates
        balloon_date = date(balloon_year, balloon_month, balloon_day)
        
        return {
            'balloon_amount': str(remaining_balance),
            'balloon_date': balloon_date.isoformat(),
            'monthly_payment': str(monthly_payment),
            'total_payments_before_balloon': f"${monthly_payment.dollars * balloon_term_months:,.2f}"
        }
    
    def update_balloon_payment(self, loan_id: str, balloon_term_months: int) -> Optional[Loan]:
        """
        Update a loan with balloon payment details.
        
        Args:
            loan_id: ID of the loan
            balloon_term_months: Number of months until the balloon payment
            
        Returns:
            Optional[Loan]: The updated loan if found, None otherwise
        """
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return None
            
        # Calculate balloon payment details
        balloon_details = self.calculate_balloon_payment(loan_id, balloon_term_months)
        
        # Create a balloon payment object
        balloon_payment = BalloonPayment(
            term_months=balloon_term_months,
            amount=Money(balloon_details['balloon_amount']),
            due_date=date.fromisoformat(balloon_details['balloon_date'])
        )
        
        # Update the loan
        return self.update_loan(loan_id, {
            'balloon_payment': {
                'term_months': balloon_payment.term_months,
                'amount': str(balloon_payment.amount),
                'due_date': balloon_payment.due_date.isoformat()
            }
        })
    
    def _validate_loan_data(self, loan_data: Dict[str, Any], partial: bool = False) -> None:
        """
        Validate loan data before creating or updating a loan.
        
        Args:
            loan_data: Dictionary containing loan data
            partial: Whether this is a partial update (not all fields required)
            
        Raises:
            ValueError: If the loan data is invalid
        """
        required_fields = ['property_id', 'loan_type', 'amount', 'interest_rate', 'term_months', 'start_date']
        
        # Check required fields
        if not partial:
            for field in required_fields:
                if field not in loan_data:
                    raise ValueError(f"Missing required field: {field}")
                    
        # Validate loan type
        if 'loan_type' in loan_data:
            try:
                if not isinstance(loan_data['loan_type'], LoanType):
                    LoanType(loan_data['loan_type'])
            except ValueError:
                valid_types = [t.value for t in LoanType]
                raise ValueError(f"Invalid loan type. Must be one of: {', '.join(valid_types)}")
                
        # Validate loan status
        if 'status' in loan_data:
            try:
                if not isinstance(loan_data['status'], LoanStatus):
                    LoanStatus(loan_data['status'])
            except ValueError:
                valid_statuses = [s.value for s in LoanStatus]
                raise ValueError(f"Invalid loan status. Must be one of: {', '.join(valid_statuses)}")
                
        # Validate amount
        if 'amount' in loan_data:
            try:
                amount = Money(loan_data['amount'])
                if amount.dollars <= 0:
                    raise ValueError("Loan amount must be greater than 0")
            except Exception as e:
                raise ValueError(f"Invalid loan amount: {str(e)}")
                
        # Validate interest rate
        if 'interest_rate' in loan_data:
            try:
                rate = Percentage(loan_data['interest_rate'])
                if rate.value < 0 or rate.value > 30:
                    raise ValueError("Interest rate must be between 0% and 30%")
            except Exception as e:
                raise ValueError(f"Invalid interest rate: {str(e)}")
                
        # Validate term
        if 'term_months' in loan_data:
            try:
                term = int(loan_data['term_months'])
                if term <= 0 or term > 360:
                    raise ValueError("Loan term must be between 1 and 360 months")
            except Exception as e:
                raise ValueError(f"Invalid loan term: {str(e)}")
                
        # Validate start date
        if 'start_date' in loan_data:
            try:
                if isinstance(loan_data['start_date'], str):
                    date.fromisoformat(loan_data['start_date'])
            except Exception as e:
                raise ValueError(f"Invalid start date: {str(e)}")
                
        # Validate balloon payment
        if 'balloon_payment' in loan_data and loan_data['balloon_payment']:
            balloon = loan_data['balloon_payment']
            
            if 'term_months' in balloon:
                try:
                    term = int(balloon['term_months'])
                    if term <= 0:
                        raise ValueError("Balloon term must be greater than 0")
                    if 'term_months' in loan_data and term >= int(loan_data['term_months']):
                        raise ValueError("Balloon term must be less than the loan term")
                except Exception as e:
                    raise ValueError(f"Invalid balloon term: {str(e)}")
                    
            if 'amount' in balloon and balloon['amount']:
                try:
                    Money(balloon['amount'])
                except Exception as e:
                    raise ValueError(f"Invalid balloon amount: {str(e)}")
                    
            if 'due_date' in balloon and balloon['due_date']:
                try:
                    if isinstance(balloon['due_date'], str):
                        date.fromisoformat(balloon['due_date'])
                except Exception as e:
                    raise ValueError(f"Invalid balloon due date: {str(e)}")
