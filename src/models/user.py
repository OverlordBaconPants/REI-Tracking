"""
User model module for the REI-Tracker application.

This module provides the User model for user authentication and management.
"""

from typing import Optional, List, Dict, Any
from pydantic import Field, validator

from src.models.base_model import BaseModel
from src.utils.validation_utils import validate_email, validate_phone


class User(BaseModel):
    """
    User model for authentication and user management.
    
    This class represents a user in the system, including authentication
    information and profile details.
    """
    
    # User identification
    email: str
    first_name: str
    last_name: str
    name: Optional[str] = None
    
    # Authentication
    password: str  # Stored as a hash
    
    # Contact information
    phone: Optional[str] = None
    
    # Permissions
    role: str = "User"  # "Admin" or "User"
    
    @validator("email")
    def validate_email(cls, v: str) -> str:
        """
        Validate email format.
        
        Args:
            v: The email to validate
            
        Returns:
            The validated email
            
        Raises:
            ValueError: If the email is invalid
        """
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v.lower()
    
    @validator("phone")
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate phone number format.
        
        Args:
            v: The phone number to validate
            
        Returns:
            The validated phone number
            
        Raises:
            ValueError: If the phone number is invalid
        """
        if v is not None and not validate_phone(v):
            raise ValueError("Invalid phone number format")
        return v
    
    @validator("name", always=True)
    def set_full_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """
        Set full name from first and last name if not provided.
        
        Args:
            v: The current name value
            values: The values being validated
            
        Returns:
            The full name
        """
        if v:
            return v
        
        first_name = values.get("first_name", "")
        last_name = values.get("last_name", "")
        
        if first_name and last_name:
            return f"{first_name} {last_name}"
        
        return first_name or last_name or ""
    
    @validator("role")
    def validate_role(cls, v: str) -> str:
        """
        Validate user role.
        
        Args:
            v: The role to validate
            
        Returns:
            The validated role
            
        Raises:
            ValueError: If the role is invalid
        """
        valid_roles = ["Admin", "User"]
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")
        return v
    
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary, excluding sensitive fields.
        
        Returns:
            Dictionary representation of the model
        """
        exclude = kwargs.pop("exclude", set())
        exclude.add("password")
        
        return super().dict(*args, exclude=exclude, **kwargs)
    
    def is_admin(self) -> bool:
        """
        Check if the user is an admin.
        
        Returns:
            True if the user is an admin, False otherwise
        """
        return self.role == "Admin"
