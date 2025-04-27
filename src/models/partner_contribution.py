"""
Partner contribution model module for the REI-Tracker application.

This module provides the PartnerContribution model for tracking partner contributions
and distributions.
"""

from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import Field, validator

from src.models.base_model import BaseModel
from src.utils.validation_utils import validate_date


class PartnerContribution(BaseModel):
    """
    Partner contribution model for tracking partner contributions and distributions.
    
    This class represents a contribution or distribution made by a partner for a property.
    """
    
    property_id: str
    partner_name: str
    amount: Decimal
    contribution_type: str  # "contribution" or "distribution"
    date: str
    notes: Optional[str] = None
    
    @validator("contribution_type")
    def validate_contribution_type(cls, v: str) -> str:
        """
        Validate contribution type.
        
        Args:
            v: The contribution type to validate
            
        Returns:
            The validated contribution type
            
        Raises:
            ValueError: If the contribution type is invalid
        """
        valid_types = ["contribution", "distribution"]
        if v not in valid_types:
            raise ValueError(f"Contribution type must be one of: {', '.join(valid_types)}")
        return v
    
    @validator("date")
    def validate_date(cls, v: str) -> str:
        """
        Validate date.
        
        Args:
            v: The date to validate
            
        Returns:
            The validated date
            
        Raises:
            ValueError: If the date is invalid
        """
        if not validate_date(v):
            raise ValueError("Invalid date format (should be YYYY-MM-DD)")
        return v
