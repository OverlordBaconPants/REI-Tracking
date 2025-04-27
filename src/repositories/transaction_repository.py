"""
Transaction repository module for the REI-Tracker application.

This module provides the TransactionRepository class for transaction data
persistence and retrieval.
"""

from typing import List, Optional, Dict, Any, Set
from datetime import datetime

from src.config import current_config
from src.models.transaction import Transaction
from src.repositories.base_repository import BaseRepository
from src.utils.logging_utils import get_logger
from src.utils.validation_utils import validate_date

# Set up logger
logger = get_logger(__name__)


class TransactionRepository(BaseRepository[Transaction]):
    """
    Transaction repository for transaction data persistence and retrieval.
    
    This class provides methods for transaction-specific operations, such as
    finding transactions by property, date range, and category.
    """
    
    def __init__(self) -> None:
        """Initialize the transaction repository."""
        super().__init__(str(current_config.TRANSACTIONS_FILE), Transaction)
    
    def get_by_property(self, property_id: str) -> List[Transaction]:
        """
        Get transactions by property ID.
        
        Args:
            property_id: ID of the property
            
        Returns:
            List of transactions for the property
        """
        try:
            transactions = self.get_all()
            return [t for t in transactions if t.property_id == property_id]
        except Exception as e:
            logger.error(f"Error getting transactions by property: {str(e)}")
            raise
    
    def get_by_date_range(self, start_date: str, end_date: str) -> List[Transaction]:
        """
        Get transactions by date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of transactions in the date range
            
        Raises:
            ValueError: If the date format is invalid
        """
        try:
            # Validate date format
            if not validate_date(start_date) or not validate_date(end_date):
                raise ValueError("Invalid date format (should be YYYY-MM-DD)")
            
            # Parse dates
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Get transactions
            transactions = self.get_all()
            
            # Filter by date range
            return [
                t for t in transactions
                if start <= datetime.strptime(t.date, "%Y-%m-%d") <= end
            ]
        except Exception as e:
            logger.error(f"Error getting transactions by date range: {str(e)}")
            raise
    
    def get_by_category(self, category: str, transaction_type: str = None) -> List[Transaction]:
        """
        Get transactions by category.
        
        Args:
            category: Transaction category
            transaction_type: Transaction type ("income" or "expense")
            
        Returns:
            List of transactions with the category
        """
        try:
            transactions = self.get_all()
            
            # Filter by category
            result = [t for t in transactions if t.category.lower() == category.lower()]
            
            # Filter by type if specified
            if transaction_type:
                result = [t for t in result if t.type == transaction_type]
            
            return result
        except Exception as e:
            logger.error(f"Error getting transactions by category: {str(e)}")
            raise
            
    def get_by_description_search(self, search_term: str) -> List[Transaction]:
        """
        Get transactions by description search.
        
        Args:
            search_term: Search term to look for in descriptions
            
        Returns:
            List of transactions with matching descriptions
        """
        try:
            transactions = self.get_all()
            
            # Case-insensitive search in description
            if search_term:
                search_term = search_term.lower()
                return [t for t in transactions if search_term in t.description.lower()]
            
            return transactions
        except Exception as e:
            logger.error(f"Error searching transactions by description: {str(e)}")
            raise
            
    def get_by_properties(self, property_ids: Set[str]) -> List[Transaction]:
        """
        Get transactions for multiple properties.
        
        Args:
            property_ids: Set of property IDs to filter by
            
        Returns:
            List of transactions for the specified properties
        """
        try:
            transactions = self.get_all()
            
            # Filter by property IDs
            if property_ids:
                return [t for t in transactions if t.property_id in property_ids]
            
            return transactions
        except Exception as e:
            logger.error(f"Error getting transactions by properties: {str(e)}")
            raise
    
    def get_by_collector_payer(self, collector_payer: str) -> List[Transaction]:
        """
        Get transactions by collector/payer.
        
        Args:
            collector_payer: Name of the collector/payer
            
        Returns:
            List of transactions with the collector/payer
        """
        try:
            transactions = self.get_all()
            
            return [
                t for t in transactions
                if t.collector_payer.lower() == collector_payer.lower()
            ]
        except Exception as e:
            logger.error(f"Error getting transactions by collector/payer: {str(e)}")
            raise
    
    def get_pending_reimbursements(self) -> List[Transaction]:
        """
        Get transactions with pending reimbursements.
        
        Returns:
            List of transactions with pending reimbursements
        """
        try:
            transactions = self.get_all()
            return [t for t in transactions if t.is_pending_reimbursement()]
        except Exception as e:
            logger.error(f"Error getting pending reimbursements: {str(e)}")
            raise
    
    def get_in_progress_reimbursements(self) -> List[Transaction]:
        """
        Get transactions with in-progress reimbursements.
        
        Returns:
            List of transactions with in-progress reimbursements
        """
        try:
            transactions = self.get_all()
            return [t for t in transactions if t.is_in_progress_reimbursement()]
        except Exception as e:
            logger.error(f"Error getting in-progress reimbursements: {str(e)}")
            raise
    
    def get_completed_reimbursements(self) -> List[Transaction]:
        """
        Get transactions with completed reimbursements.
        
        Returns:
            List of transactions with completed reimbursements
        """
        try:
            transactions = self.get_all()
            return [t for t in transactions if t.is_reimbursed()]
        except Exception as e:
            logger.error(f"Error getting completed reimbursements: {str(e)}")
            raise
