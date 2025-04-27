"""
Reimbursement service module for the REI-Tracker application.

This module provides services for managing transaction reimbursements.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime

from src.models.transaction import Transaction, Reimbursement
from src.models.property import Property, Partner
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.property_repository import PropertyRepository
from src.services.property_access_service import PropertyAccessService

# Set up logger
logger = logging.getLogger(__name__)


class ReimbursementService:
    """
    Service for managing transaction reimbursements.
    
    This class provides methods for reimbursement operations, such as
    calculating reimbursement amounts, updating reimbursement status,
    and handling automatic reimbursements for wholly-owned properties.
    """
    
    def __init__(
        self,
        transaction_repository: Optional[TransactionRepository] = None,
        property_repository: Optional[PropertyRepository] = None,
        property_access_service: Optional[PropertyAccessService] = None
    ):
        """
        Initialize the reimbursement service.
        
        Args:
            transaction_repository: Transaction repository instance
            property_repository: Property repository instance
            property_access_service: Property access service instance
        """
        self.transaction_repo = transaction_repository or TransactionRepository()
        self.property_repo = property_repository or PropertyRepository()
        self.property_access_service = property_access_service or PropertyAccessService()
    
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
        # Get transaction
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        # Check if user has access to the property
        if not self.property_access_service.can_access_property(user_id, transaction.property_id):
            raise ValueError("Access denied to this transaction")
        
        # Get property
        property_obj = self.property_repo.get_by_id(transaction.property_id)
        if not property_obj:
            raise ValueError(f"Property {transaction.property_id} not found")
        
        # Calculate reimbursement shares
        return transaction.calculate_reimbursement_shares(property_obj.partners)
    
    def update_reimbursement(
        self,
        transaction_id: str,
        reimbursement_data: Dict[str, Any],
        user_id: str
    ) -> Optional[Transaction]:
        """
        Update reimbursement information for a transaction.
        
        Args:
            transaction_id: ID of the transaction
            reimbursement_data: Reimbursement data to update
            user_id: ID of the user making the update
            
        Returns:
            Updated transaction if successful, None otherwise
        """
        # Get transaction
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            logger.warning(f"Transaction {transaction_id} not found")
            return None
        
        # Check if user has access to the property
        if not self.property_access_service.can_manage_property(user_id, transaction.property_id):
            logger.warning(f"User {user_id} does not have permission to update transaction {transaction_id}")
            return None
        
        # Create reimbursement if it doesn't exist
        if transaction.reimbursement is None:
            transaction.reimbursement = Reimbursement()
        
        # Update reimbursement fields
        if "date_shared" in reimbursement_data:
            transaction.reimbursement.date_shared = reimbursement_data["date_shared"]
        
        if "share_description" in reimbursement_data:
            transaction.reimbursement.share_description = reimbursement_data["share_description"]
        
        if "reimbursement_status" in reimbursement_data:
            transaction.reimbursement.reimbursement_status = reimbursement_data["reimbursement_status"]
        
        if "documentation" in reimbursement_data:
            transaction.reimbursement.documentation = reimbursement_data["documentation"]
        
        # Update partner shares if provided
        if "partner_shares" in reimbursement_data:
            partner_shares = {}
            for partner, amount in reimbursement_data["partner_shares"].items():
                partner_shares[partner] = Decimal(str(amount))
            transaction.reimbursement.partner_shares = partner_shares
        
        # Save updated transaction
        return self.transaction_repo.update(transaction)
    
    def process_new_transaction(
        self,
        transaction: Transaction
    ) -> Transaction:
        """
        Process a new transaction for reimbursement.
        
        This method handles automatic reimbursement completion for
        wholly-owned properties.
        
        Args:
            transaction: The new transaction to process
            
        Returns:
            The processed transaction
        """
        # Only process expense transactions
        if transaction.type != "expense":
            return transaction
        
        # Get property
        property_obj = self.property_repo.get_by_id(transaction.property_id)
        if not property_obj:
            logger.warning(f"Property {transaction.property_id} not found")
            return transaction
        
        # Check if property is wholly owned by the payer
        if transaction.is_owned_by_payer(property_obj.partners):
            # Auto-complete reimbursement for wholly-owned properties
            if transaction.reimbursement is None:
                transaction.reimbursement = Reimbursement()
            
            transaction.reimbursement.reimbursement_status = "completed"
            transaction.reimbursement.date_shared = datetime.now().strftime("%Y-%m-%d")
            transaction.reimbursement.share_description = "Auto-completed (wholly owned property)"
            
            # Save updated transaction
            return self.transaction_repo.update(transaction)
        
        # For shared properties, calculate and store reimbursement shares
        if property_obj.partners and len(property_obj.partners) > 1:
            try:
                # Calculate shares
                shares = transaction.calculate_reimbursement_shares(property_obj.partners)
                
                # Create reimbursement if it doesn't exist
                if transaction.reimbursement is None:
                    transaction.reimbursement = Reimbursement()
                
                # Store shares
                transaction.reimbursement.partner_shares = shares
                
                # Save updated transaction
                return self.transaction_repo.update(transaction)
            except Exception as e:
                logger.error(f"Error calculating reimbursement shares: {str(e)}")
        
        return transaction
    
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
        # Get user
        user = self.property_access_service.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return []
        
        # Get accessible properties
        accessible_properties = self.property_access_service.get_accessible_properties(user_id)
        property_map = {prop.id: prop for prop in accessible_properties}
        
        # Get pending reimbursements
        pending_reimbursements = self.transaction_repo.get_pending_reimbursements()
        
        # Filter by user's properties and where user is not the payer
        result = []
        for transaction in pending_reimbursements:
            if transaction.property_id in property_map:
                property_obj = property_map[transaction.property_id]
                
                # Skip if user is the payer
                if transaction.collector_payer == user.name:
                    continue
                
                # Check if user is a partner in the property
                is_partner = any(partner.name == user.name for partner in property_obj.partners)
                
                if is_partner:
                    result.append((transaction, property_obj))
        
        return result
    
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
        # Get user
        user = self.property_access_service.user_repository.get_by_id(user_id)
        if not user:
            logger.warning(f"User {user_id} not found")
            return []
        
        # Get accessible properties
        accessible_properties = self.property_access_service.get_accessible_properties(user_id)
        property_map = {prop.id: prop for prop in accessible_properties}
        
        # Get pending and in-progress reimbursements
        pending_reimbursements = self.transaction_repo.get_pending_reimbursements()
        in_progress_reimbursements = self.transaction_repo.get_in_progress_reimbursements()
        reimbursements = pending_reimbursements + in_progress_reimbursements
        
        # Filter by user's properties and where user is a partner but not the payer
        result = []
        for transaction in reimbursements:
            if transaction.property_id in property_map:
                property_obj = property_map[transaction.property_id]
                
                # Only include if user is a partner and not the payer
                is_partner = any(partner.name == user.name for partner in property_obj.partners)
                
                if is_partner and transaction.collector_payer != user.name:
                    result.append((transaction, property_obj))
        
        return result
