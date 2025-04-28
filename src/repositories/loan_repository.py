import json
import os
from typing import List, Dict, Optional, Any
from datetime import date
from src.models.loan import Loan, LoanType, LoanStatus
from src.repositories.base_repository import BaseRepository
from src.utils.money import Money

class LoanRepository(BaseRepository):
    """
    Repository for managing loan data.
    
    This class provides methods for creating, retrieving, updating, and deleting
    loan records, as well as specialized queries for loan management.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the loan repository.
        
        Args:
            data_dir: Directory where data files are stored
        """
        from src.config import current_config
        
        if data_dir is None:
            data_dir = current_config.DATA_DIR
            
        file_path = os.path.join(data_dir, "loans.json")
        super().__init__(file_path, Loan)
        
    def get_loans_by_property(self, property_id: str) -> List[Loan]:
        """
        Get all loans associated with a specific property.
        
        Args:
            property_id: ID of the property
            
        Returns:
            List[Loan]: List of loans for the property
        """
        loans = self.get_all()
        return [loan for loan in loans if loan.property_id == property_id]
    
    def get_active_loans_by_property(self, property_id: str) -> List[Loan]:
        """
        Get all active loans associated with a specific property.
        
        Args:
            property_id: ID of the property
            
        Returns:
            List[Loan]: List of active loans for the property
        """
        loans = self.get_loans_by_property(property_id)
        return [loan for loan in loans if loan.status == LoanStatus.ACTIVE]
    
    def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        """
        Get a loan by its ID.
        
        Args:
            loan_id: ID of the loan
            
        Returns:
            Optional[Loan]: The loan if found, None otherwise
        """
        return self.get_by_id(loan_id)
    
    def create_loan(self, loan_data: Dict[str, Any]) -> Loan:
        """
        Create a new loan.
        
        Args:
            loan_data: Dictionary containing loan data
            
        Returns:
            Loan: The created loan
        """
        loan = Loan.from_dict(loan_data)
        return self.create(loan)
    
    def update_loan(self, loan_id: str, loan_data: Dict[str, Any]) -> Optional[Loan]:
        """
        Update an existing loan.
        
        Args:
            loan_id: ID of the loan to update
            loan_data: Dictionary containing updated loan data
            
        Returns:
            Optional[Loan]: The updated loan if found, None otherwise
        """
        existing_loan = self.get_by_id(loan_id)
        if not existing_loan:
            return None
            
        # Update the loan with new data
        updated_data = existing_loan.to_dict()
        updated_data.update(loan_data)
        
        # Preserve the ID
        updated_data['id'] = loan_id
        
        # Update the updated_at timestamp
        updated_data['updated_at'] = date.today().isoformat()
        
        # Create a new loan instance with the updated data
        updated_loan = Loan.from_dict(updated_data)
        
        # Save the updated loan
        return self.update(updated_loan)
    
    def delete_loan(self, loan_id: str) -> bool:
        """
        Delete a loan.
        
        Args:
            loan_id: ID of the loan to delete
            
        Returns:
            bool: True if the loan was deleted, False otherwise
        """
        return self.delete(loan_id)
    
    def refinance_loan(self, old_loan_id: str, new_loan_data: Dict[str, Any]) -> Optional[Loan]:
        """
        Refinance an existing loan by creating a new loan and marking the old one as refinanced.
        
        Args:
            old_loan_id: ID of the loan being refinanced
            new_loan_data: Dictionary containing data for the new loan
            
        Returns:
            Optional[Loan]: The new loan if successful, None otherwise
        """
        old_loan = self.get_by_id(old_loan_id)
        if not old_loan:
            return None
            
        # Set the loan type to refinance and link to the old loan
        new_loan_data['loan_type'] = LoanType.REFINANCE.value
        new_loan_data['refinanced_from_id'] = old_loan_id
        
        # Create the new loan
        new_loan = self.create_loan(new_loan_data)
        
        # Mark the old loan as refinanced
        self.update_loan(old_loan_id, {'status': LoanStatus.REFINANCED.value})
        
        return new_loan
    
    def pay_off_loan(self, loan_id: str, payoff_date: Optional[date] = None) -> Optional[Loan]:
        """
        Mark a loan as paid off.
        
        Args:
            loan_id: ID of the loan to pay off
            payoff_date: Date when the loan was paid off (defaults to today)
            
        Returns:
            Optional[Loan]: The updated loan if found, None otherwise
        """
        if payoff_date is None:
            payoff_date = date.today()
            
        return self.update_loan(loan_id, {
            'status': LoanStatus.PAID_OFF.value,
            'last_updated': payoff_date.isoformat(),
            'current_balance': str(Money(0))
        })
    
    def update_loan_balance(self, loan_id: str, as_of_date: Optional[date] = None) -> Optional[Loan]:
        """
        Update the current balance of a loan based on the amortization schedule.
        
        Args:
            loan_id: ID of the loan to update
            as_of_date: Date to calculate the balance for (defaults to today)
            
        Returns:
            Optional[Loan]: The updated loan if found, None otherwise
        """
        loan = self.get_by_id(loan_id)
        if not loan:
            return None
            
        if as_of_date is None:
            as_of_date = date.today()
            
        # Calculate the current balance
        current_balance = loan.calculate_remaining_balance(as_of_date)
        
        # Update the loan
        return self.update_loan(loan_id, {
            'current_balance': str(current_balance),
            'last_updated': as_of_date.isoformat()
        })
    
    def get_total_debt_for_property(self, property_id: str, as_of_date: Optional[date] = None) -> Money:
        """
        Calculate the total debt for a property across all active loans.
        
        Args:
            property_id: ID of the property
            as_of_date: Date to calculate the balance for (defaults to today)
            
        Returns:
            Money: The total debt amount
        """
        if as_of_date is None:
            as_of_date = date.today()
            
        active_loans = self.get_active_loans_by_property(property_id)
        
        total_debt = Money(0)
        for loan in active_loans:
            total_debt = Money(total_debt.dollars + loan.calculate_remaining_balance(as_of_date).dollars)
            
        return total_debt
    
    def get_total_monthly_payment_for_property(self, property_id: str) -> Money:
        """
        Calculate the total monthly payment for a property across all active loans.
        
        Args:
            property_id: ID of the property
            
        Returns:
            Money: The total monthly payment amount
        """
        active_loans = self.get_active_loans_by_property(property_id)
        
        total_payment = Money(0)
        for loan in active_loans:
            if loan.monthly_payment:
                total_payment = Money(total_payment.dollars + loan.monthly_payment.dollars)
            else:
                # Calculate the payment if not stored
                loan_details = loan.to_loan_details()
                payment = loan_details.calculate_payment().total
                total_payment = Money(total_payment.dollars + payment.dollars)
                
        return total_payment
    
    def _load_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load loan data from the JSON file.
        
        Returns:
            Dict: Dictionary of loan data indexed by ID
        """
        data = super()._load_data()
        
        # If the file doesn't exist or is empty, initialize with an empty dictionary
        if not data:
            return {}
            
        return data
    
    def _save_data(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Save loan data to the JSON file.
        
        Args:
            data: Dictionary of loan data indexed by ID
        """
        super()._save_data(data)
    
    def _entity_to_dict(self, entity: Loan) -> Dict[str, Any]:
        """
        Convert a Loan object to a dictionary for storage.
        
        Args:
            entity: The Loan object to convert
            
        Returns:
            Dict: Dictionary representation of the loan
        """
        return entity.to_dict()
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> Loan:
        """
        Convert a dictionary to a Loan object.
        
        Args:
            data: Dictionary containing loan data
            
        Returns:
            Loan: A Loan object created from the dictionary
        """
        return Loan.from_dict(data)
