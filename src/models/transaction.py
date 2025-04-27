"""
Transaction model module for the REI-Tracker application.

This module provides the Transaction model for financial transaction management.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from pydantic import Field, validator

from src.models.base_model import BaseModel
from src.models.property import Partner
from src.utils.validation_utils import validate_date, validate_decimal


class Reimbursement(BaseModel):
    """
    Reimbursement model for transaction reimbursements.
    
    This class represents the reimbursement status and details for a transaction.
    """
    
    date_shared: Optional[str] = None
    share_description: Optional[str] = None
    reimbursement_status: str = "pending"  # "pending", "in_progress", "completed"
    documentation: Optional[str] = None
    partner_shares: Dict[str, Decimal] = Field(default_factory=dict)
    
    @validator("date_shared")
    def validate_date_shared(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate date shared.
        
        Args:
            v: The date shared to validate
            
        Returns:
            The validated date shared
            
        Raises:
            ValueError: If the date shared is invalid
        """
        if v is not None and v != "" and not validate_date(v):
            raise ValueError("Invalid date shared format (should be YYYY-MM-DD)")
        if v == "":
            return None
        return v
    
    @validator("reimbursement_status")
    def validate_reimbursement_status(cls, v: str) -> str:
        """
        Validate reimbursement status.
        
        Args:
            v: The reimbursement status to validate
            
        Returns:
            The validated reimbursement status
            
        Raises:
            ValueError: If the reimbursement status is invalid
        """
        valid_statuses = ["pending", "in_progress", "completed"]
        if v not in valid_statuses:
            raise ValueError(f"Reimbursement status must be one of: {', '.join(valid_statuses)}")
        return v


class Transaction(BaseModel):
    """
    Transaction model for financial transaction management.
    
    This class represents a financial transaction in the system, including
    property association, categorization, and reimbursement status.
    """
    
    # Transaction details
    property_id: str
    type: str  # "income" or "expense"
    category: str
    description: str
    amount: Decimal
    date: str
    collector_payer: str
    
    # Documentation
    documentation_file: Optional[str] = None
    
    # Reimbursement
    reimbursement: Optional[Reimbursement] = None
    
    @validator("type")
    def validate_type(cls, v: str) -> str:
        """
        Validate transaction type.
        
        Args:
            v: The transaction type to validate
            
        Returns:
            The validated transaction type
            
        Raises:
            ValueError: If the transaction type is invalid
        """
        valid_types = ["income", "expense"]
        if v not in valid_types:
            raise ValueError(f"Transaction type must be one of: {', '.join(valid_types)}")
        return v
    
    @validator("amount")
    def validate_amount(cls, v: Decimal) -> Decimal:
        """
        Validate transaction amount.
        
        Args:
            v: The transaction amount to validate
            
        Returns:
            The validated transaction amount
            
        Raises:
            ValueError: If the transaction amount is invalid
        """
        if not validate_decimal(v, 0):
            raise ValueError("Transaction amount must be positive")
        return v
    
    @validator("date")
    def validate_date(cls, v: str) -> str:
        """
        Validate transaction date.
        
        Args:
            v: The transaction date to validate
            
        Returns:
            The validated transaction date
            
        Raises:
            ValueError: If the transaction date is invalid
        """
        if not validate_date(v):
            raise ValueError("Invalid transaction date format (should be YYYY-MM-DD)")
        return v
    
    def is_reimbursed(self) -> bool:
        """
        Check if the transaction has been reimbursed.
        
        Returns:
            True if the transaction has been reimbursed, False otherwise
        """
        return (
            self.reimbursement is not None and
            self.reimbursement.reimbursement_status == "completed"
        )
    
    def is_pending_reimbursement(self) -> bool:
        """
        Check if the transaction is pending reimbursement.
        
        Returns:
            True if the transaction is pending reimbursement, False otherwise
        """
        return (
            self.reimbursement is not None and
            self.reimbursement.reimbursement_status == "pending"
        )
    
    def is_in_progress_reimbursement(self) -> bool:
        """
        Check if the transaction reimbursement is in progress.
        
        Returns:
            True if the transaction reimbursement is in progress, False otherwise
        """
        return (
            self.reimbursement is not None and
            self.reimbursement.reimbursement_status == "in_progress"
        )
    
    def needs_reimbursement(self) -> bool:
        """
        Check if the transaction needs reimbursement.
        
        Returns:
            True if the transaction needs reimbursement, False otherwise
        """
        return (
            self.type == "expense" and
            (self.reimbursement is None or
             self.reimbursement.reimbursement_status != "completed")
        )
    
    def complete_reimbursement(self, date_shared: str, share_description: str) -> None:
        """
        Mark the transaction as reimbursed.
        
        Args:
            date_shared: The date the reimbursement was shared
            share_description: Description of the reimbursement sharing
        """
        if self.reimbursement is None:
            self.reimbursement = Reimbursement()
        
        self.reimbursement.date_shared = date_shared
        self.reimbursement.share_description = share_description
        self.reimbursement.reimbursement_status = "completed"
    
    def calculate_reimbursement_shares(self, partners: List[Partner]) -> Dict[str, Decimal]:
        """
        Calculate reimbursement amounts based on partner equity shares.
        
        Args:
            partners: List of partners with equity shares
            
        Returns:
            Dictionary mapping partner names to reimbursement amounts
            
        Raises:
            ValueError: If the total equity share is not 100%
        """
        if not partners:
            return {}
            
        # Validate total equity is 100%
        total_equity = sum(partner.equity_share for partner in partners)
        if total_equity != Decimal("100"):
            raise ValueError(f"Total equity must be 100% (currently {total_equity}%)")
            
        # Calculate reimbursement amounts based on equity shares
        reimbursement_shares = {}
        for partner in partners:
            # Skip the partner who paid (collector_payer)
            if partner.name == self.collector_payer:
                continue
                
            # Calculate share based on equity percentage
            share_amount = (self.amount * partner.equity_share) / Decimal("100")
            reimbursement_shares[partner.name] = share_amount
            
        return reimbursement_shares
    
    def is_wholly_owned(self, partners: List[Partner]) -> bool:
        """
        Check if the property is wholly owned by a single partner.
        
        Args:
            partners: List of partners with equity shares
            
        Returns:
            True if the property is wholly owned by a single partner, False otherwise
        """
        return len(partners) == 1 and partners[0].equity_share == Decimal("100")
    
    def is_owned_by_payer(self, partners: List[Partner]) -> bool:
        """
        Check if the property is wholly owned by the transaction payer.
        
        Args:
            partners: List of partners with equity shares
            
        Returns:
            True if the property is wholly owned by the transaction payer, False otherwise
        """
        return (
            self.is_wholly_owned(partners) and 
            partners[0].name == self.collector_payer
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transaction to a dictionary.
        
        Returns:
            Dictionary representation of the transaction
        """
        result = {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "property_id": self.property_id,
            "type": self.type,
            "category": self.category,
            "description": self.description,
            "amount": str(self.amount),  # Convert Decimal to string for JSON serialization
            "date": self.date,
            "collector_payer": self.collector_payer,
            "documentation_file": self.documentation_file
        }
        
        # Add reimbursement if it exists
        if self.reimbursement:
            reimbursement_dict = {
                "date_shared": self.reimbursement.date_shared,
                "share_description": self.reimbursement.share_description,
                "reimbursement_status": self.reimbursement.reimbursement_status,
                "documentation": self.reimbursement.documentation
            }
            
            # Add partner shares if they exist
            if self.reimbursement.partner_shares:
                reimbursement_dict["partner_shares"] = {
                    partner: str(amount)
                    for partner, amount in self.reimbursement.partner_shares.items()
                }
                
            result["reimbursement"] = reimbursement_dict
        
        return result
