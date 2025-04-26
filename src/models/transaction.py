"""
Transaction model module for the REI-Tracker application.

This module provides the Transaction model for financial transaction management.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from pydantic import Field, validator

from src.models.base_model import BaseModel
from src.utils.validation_utils import validate_date, validate_decimal


class Reimbursement(BaseModel):
    """
    Reimbursement model for transaction reimbursements.
    
    This class represents the reimbursement status and details for a transaction.
    """
    
    date_shared: Optional[str] = None
    share_description: Optional[str] = None
    reimbursement_status: str = "pending"  # "pending", "in_progress", "completed"
    
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
        if v is not None and not validate_date(v):
            raise ValueError("Invalid date shared format (should be YYYY-MM-DD)")
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
