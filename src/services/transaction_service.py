"""
Transaction service module for the REI-Tracker application.

This module provides services for transaction management.
"""

import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from decimal import Decimal
from collections import defaultdict

from src.models.transaction import Transaction, Reimbursement
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.property_repository import PropertyRepository
from src.services.property_access_service import PropertyAccessService
from src.services.reimbursement_service import ReimbursementService
from src.models.property import Property

# Set up logger
logger = logging.getLogger(__name__)


class TransactionService:
    """
    Service for transaction management.
    
    This class provides methods for transaction operations, such as
    creating, updating, and deleting transactions.
    """
    
    def __init__(self):
        """Initialize the transaction service."""
        self.transaction_repo = TransactionRepository()
        self.property_repo = PropertyRepository()
        self.property_access_service = PropertyAccessService()
        self.reimbursement_service = ReimbursementService(
            self.transaction_repo,
            self.property_repo,
            self.property_access_service
        )
    
    def get_transactions(self, user_id: str, filters: Dict[str, Any] = None) -> List[Transaction]:
        """
        Get transactions with optional filtering.
        
        Args:
            user_id: ID of the user
            filters: Optional filters to apply
            
        Returns:
            List of transactions
        """
        try:
            # Get all transactions
            all_transactions = self.transaction_repo.get_all()
            
            # Filter by user access (unless user is admin)
            user = self.property_access_service.user_repository.get_by_id(user_id)
            if user and not user.is_admin():
                accessible_properties = self.property_access_service.get_accessible_properties(user_id)
                all_transactions = [
                    t for t in all_transactions 
                    if t.property_id in [p.id for p in accessible_properties]
                ]
            
            # Apply filters if provided
            if filters:
                # Filter by property ID
                if 'property_id' in filters and filters['property_id']:
                    if filters['property_id'] != 'all':  # Skip filtering if 'all' is specified
                        all_transactions = [t for t in all_transactions if t.property_id == filters['property_id']]
                
                # Filter by multiple property IDs
                elif 'property_ids' in filters and filters['property_ids']:
                    property_ids = set(filters['property_ids'])
                    all_transactions = [t for t in all_transactions if t.property_id in property_ids]
                
                # Filter by transaction type
                if 'type' in filters and filters['type']:
                    all_transactions = [t for t in all_transactions if t.type == filters['type']]
                
                # Filter by category
                if 'category' in filters and filters['category']:
                    all_transactions = [t for t in all_transactions if t.category == filters['category']]
                
                # Filter by date range
                if 'start_date' in filters or 'end_date' in filters:
                    all_transactions = self._filter_by_date_range(
                        all_transactions, 
                        filters.get('start_date'), 
                        filters.get('end_date')
                    )
                
                # Filter by reimbursement status
                if 'reimbursement_status' in filters and filters['reimbursement_status']:
                    all_transactions = self._filter_by_reimbursement_status(
                        all_transactions, 
                        filters['reimbursement_status']
                    )
                    
                # Filter by description search
                if 'description' in filters and filters['description']:
                    search_term = filters['description'].lower()
                    all_transactions = [
                        t for t in all_transactions 
                        if search_term in t.description.lower()
                    ]
            
            return all_transactions
            
        except Exception as e:
            logger.error(f"Error getting transactions: {str(e)}")
            raise
    
    def get_transaction(self, transaction_id: str, user_id: str) -> Optional[Transaction]:
        """
        Get a specific transaction by ID.
        
        Args:
            transaction_id: ID of the transaction
            user_id: ID of the user
            
        Returns:
            Transaction if found and accessible, None otherwise
        """
        try:
            # Get transaction
            transaction = self.transaction_repo.get_by_id(transaction_id)
            if not transaction:
                return None
            
            # Check if user has access to the property
            if not self.property_access_service.can_access_property(user_id, transaction.property_id):
                return None
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error getting transaction: {str(e)}")
            raise
    
    def create_transaction(self, transaction_data: Dict[str, Any], user_id: str) -> Optional[Transaction]:
        """
        Create a new transaction.
        
        Args:
            transaction_data: Transaction data
            user_id: ID of the user
            
        Returns:
            Created transaction if successful, None otherwise
        """
        try:
            # Check if user has access to the property
            if not self.property_access_service.can_manage_property(user_id, transaction_data["property_id"]):
                return None
            
            # Create transaction object
            transaction = Transaction(**transaction_data)
            
            # Save transaction
            created_transaction = self.transaction_repo.create(transaction)
            
            # Process for reimbursement (auto-complete for wholly-owned properties)
            if created_transaction:
                processed_transaction = self.reimbursement_service.process_new_transaction(created_transaction)
                return processed_transaction
            
            return created_transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            raise
    
    def update_transaction(self, transaction_id: str, update_data: Dict[str, Any], user_id: str) -> Optional[Transaction]:
        """
        Update a specific transaction.
        
        Args:
            transaction_id: ID of the transaction
            update_data: Data to update
            user_id: ID of the user
            
        Returns:
            Updated transaction if successful, None otherwise
        """
        try:
            # Get transaction
            transaction = self.transaction_repo.get_by_id(transaction_id)
            if not transaction:
                return None
            
            # Check if user has access to the property
            if not self.property_access_service.can_manage_property(user_id, transaction.property_id):
                return None
            
            # Update transaction fields
            for key, value in update_data.items():
                if key != "id" and hasattr(transaction, key):
                    setattr(transaction, key, value)
            
            # Handle reimbursement data if provided
            if "reimbursement" in update_data:
                reimbursement_data = update_data["reimbursement"]
                if transaction.reimbursement is None:
                    transaction.reimbursement = Reimbursement(**reimbursement_data)
                else:
                    for key, value in reimbursement_data.items():
                        setattr(transaction.reimbursement, key, value)
            
            # Save updated transaction
            return self.transaction_repo.update(transaction)
            
        except Exception as e:
            logger.error(f"Error updating transaction: {str(e)}")
            raise
    
    def delete_transaction(self, transaction_id: str, user_id: str) -> bool:
        """
        Delete a specific transaction.
        
        Args:
            transaction_id: ID of the transaction
            user_id: ID of the user
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get transaction
            transaction = self.transaction_repo.get_by_id(transaction_id)
            if not transaction:
                return False
            
            # Check if user has access to the property
            if not self.property_access_service.can_manage_property(user_id, transaction.property_id):
                return False
            
            # Delete transaction
            self.transaction_repo.delete(transaction_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting transaction: {str(e)}")
            raise
    
    def update_reimbursement(self, transaction_id: str, reimbursement_data: Dict[str, Any], user_id: str) -> Optional[Transaction]:
        """
        Update reimbursement status for a transaction.
        
        Args:
            transaction_id: ID of the transaction
            reimbursement_data: Reimbursement data
            user_id: ID of the user
            
        Returns:
            Updated transaction if successful, None otherwise
        """
        try:
            # Use the reimbursement service to update the reimbursement
            return self.reimbursement_service.update_reimbursement(
                transaction_id, 
                reimbursement_data, 
                user_id
            )
            
        except Exception as e:
            logger.error(f"Error updating reimbursement: {str(e)}")
            raise
    
    def get_transactions_by_property(
        self, 
        user_id: str, 
        filters: Dict[str, Any] = None
    ) -> Dict[str, List[Transaction]]:
        """
        Get transactions grouped by property with optional filtering.
        
        Args:
            user_id: ID of the user
            filters: Optional filters to apply
            
        Returns:
            Dictionary mapping property IDs to lists of transactions
        """
        try:
            # Get filtered transactions
            transactions = self.get_transactions(user_id, filters)
            
            # Group by property
            grouped_transactions = defaultdict(list)
            for transaction in transactions:
                grouped_transactions[transaction.property_id].append(transaction)
                
            return dict(grouped_transactions)
            
        except Exception as e:
            logger.error(f"Error getting transactions by property: {str(e)}")
            raise
            
    def get_transactions_with_property_info(
        self, 
        user_id: str, 
        filters: Dict[str, Any] = None
    ) -> List[Tuple[Transaction, Property]]:
        """
        Get transactions with their associated property information.
        
        Args:
            user_id: ID of the user
            filters: Optional filters to apply
            
        Returns:
            List of tuples containing (transaction, property)
        """
        try:
            # Get filtered transactions
            transactions = self.get_transactions(user_id, filters)
            
            # Get all properties
            properties = self.property_access_service.get_accessible_properties(user_id)
            property_map = {prop.id: prop for prop in properties}
            
            # Pair transactions with properties
            result = []
            for transaction in transactions:
                if transaction.property_id in property_map:
                    result.append((transaction, property_map[transaction.property_id]))
                else:
                    logger.warning(f"Property {transaction.property_id} not found for transaction {transaction.id}")
                    
            return result
            
        except Exception as e:
            logger.error(f"Error getting transactions with property info: {str(e)}")
            raise
            
    def get_property_summaries(
        self, 
        user_id: str, 
        filters: Dict[str, Any] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get financial summaries for each property based on filtered transactions.
        
        Args:
            user_id: ID of the user
            filters: Optional filters to apply
            
        Returns:
            Dictionary mapping property IDs to summary dictionaries
        """
        try:
            # Get transactions grouped by property
            grouped_transactions = self.get_transactions_by_property(user_id, filters)
            
            # Get all properties
            properties = self.property_access_service.get_accessible_properties(user_id)
            property_map = {prop.id: prop for prop in properties}
            
            # Calculate summaries
            summaries = {}
            for property_id, transactions in grouped_transactions.items():
                property_obj = property_map.get(property_id)
                
                if not property_obj:
                    logger.warning(f"Property {property_id} not found for summary calculation")
                    continue
                
                # Calculate income and expense totals
                income_total = sum(t.amount for t in transactions if t.type == "income")
                expense_total = sum(t.amount for t in transactions if t.type == "expense")
                net_amount = income_total - expense_total
                
                # Create summary
                summaries[property_id] = {
                    "property": property_obj,
                    "transaction_count": len(transactions),
                    "income_total": income_total,
                    "expense_total": expense_total,
                    "net_amount": net_amount
                }
                
            return summaries
            
        except Exception as e:
            logger.error(f"Error calculating property summaries: {str(e)}")
            raise
    
    def _filter_by_date_range(
        self, 
        transactions: List[Transaction], 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> List[Transaction]:
        """
        Filter transactions by date range.
        
        Args:
            transactions: List of transactions
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Filtered transactions
        """
        filtered = transactions
        
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            filtered = [
                t for t in filtered 
                if datetime.strptime(t.date, "%Y-%m-%d").date() >= start
            ]
        
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            filtered = [
                t for t in filtered 
                if datetime.strptime(t.date, "%Y-%m-%d").date() <= end
            ]
        
        return filtered
    
    def _filter_by_reimbursement_status(
        self, 
        transactions: List[Transaction],
        status: str
    ) -> List[Transaction]:
        """
        Filter transactions by reimbursement status.
        
        Args:
            transactions: List of transactions
            status: Reimbursement status
            
        Returns:
            Filtered transactions
        """
        if status == "all":
            return transactions
        
        if status == "pending":
            return [t for t in transactions if t.is_pending_reimbursement()]
        
        if status == "in_progress":
            return [t for t in transactions if t.is_in_progress_reimbursement()]
        
        if status == "completed":
            return [t for t in transactions if t.is_reimbursed()]
        
        return transactions
    
    def calculate_reimbursement_shares(
        self,
        transaction_id: str,
        user_id: str
    ) -> Dict[str, Decimal]:
        """
        Calculate reimbursement shares for a transaction.
        
        Args:
            transaction_id: ID of the transaction
            user_id: ID of the user requesting the calculation
            
        Returns:
            Dictionary mapping partner names to reimbursement amounts
            
        Raises:
            ValueError: If the transaction is not found or user doesn't have access
        """
        return self.reimbursement_service.calculate_reimbursement_shares(transaction_id, user_id)
    
    def get_pending_reimbursements_for_user(
        self,
        user_id: str
    ) -> List[Tuple[Transaction, Property]]:
        """
        Get pending reimbursements for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of tuples containing (transaction, property)
        """
        return self.reimbursement_service.get_pending_reimbursements_for_user(user_id)
    
    def get_reimbursements_owed_by_user(
        self,
        user_id: str
    ) -> List[Tuple[Transaction, Property]]:
        """
        Get reimbursements that a user owes to others.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of tuples containing (transaction, property)
        """
        return self.reimbursement_service.get_reimbursements_owed_by_user(user_id)
