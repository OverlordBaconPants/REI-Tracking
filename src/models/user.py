"""
User model module for the REI-Tracker application.

This module provides the User model for user authentication and management.
"""

from typing import Optional, List, Dict, Any, Set
from pydantic import Field, validator

from src.models.base_model import BaseModel
from src.utils.validation_utils import validate_email, validate_phone


class PropertyAccess(BaseModel):
    """
    Property access model for user permissions.
    
    This class represents a user's access to a specific property,
    including access level and permissions.
    """
    
    property_id: str
    access_level: str = "viewer"  # "owner", "manager", "editor", "viewer"
    equity_share: Optional[float] = None
    
    @validator("access_level")
    def validate_access_level(cls, v: str) -> str:
        """
        Validate access level.
        
        Args:
            v: The access level to validate
            
        Returns:
            The validated access level
            
        Raises:
            ValueError: If the access level is invalid
        """
        valid_levels = ["owner", "manager", "editor", "viewer"]
        if v not in valid_levels:
            raise ValueError(f"Access level must be one of: {', '.join(valid_levels)}")
        return v


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
    property_access: List[PropertyAccess] = Field(default_factory=list)
    
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
    
    def has_property_access(self, property_id: str, required_level: Optional[str] = None) -> bool:
        """
        Check if the user has access to a property.
        
        Args:
            property_id: The property ID to check
            required_level: The minimum required access level (optional)
            
        Returns:
            True if the user has access to the property, False otherwise
        """
        # Admins have access to all properties
        if self.is_admin():
            return True
        
        # Check if user has access to the property
        for access in self.property_access:
            if access.property_id == property_id:
                # If no specific level is required, any access is sufficient
                if required_level is None:
                    return True
                
                # Check if user has the required access level
                access_levels = {
                    "viewer": 1,
                    "editor": 2,
                    "manager": 3,
                    "owner": 4
                }
                
                user_level = access_levels.get(access.access_level, 0)
                required_level_value = access_levels.get(required_level, 0)
                
                return user_level >= required_level_value
        
        return False
    
    def is_property_manager(self, property_id: str) -> bool:
        """
        Check if the user is a manager for a property.
        
        Args:
            property_id: The property ID to check
            
        Returns:
            True if the user is a manager for the property, False otherwise
        """
        return self.has_property_access(property_id, "manager")
    
    def is_property_owner(self, property_id: str) -> bool:
        """
        Check if the user is an owner of a property.
        
        Args:
            property_id: The property ID to check
            
        Returns:
            True if the user is an owner of the property, False otherwise
        """
        return self.has_property_access(property_id, "owner")
    
    def get_accessible_properties(self, required_level: Optional[str] = None) -> Set[str]:
        """
        Get the IDs of properties the user has access to.
        
        Args:
            required_level: The minimum required access level (optional)
            
        Returns:
            A set of property IDs the user has access to
        """
        # Admins have access to all properties, but we can't determine all property IDs here
        if self.is_admin():
            return set()
        
        if required_level is None:
            # Return all properties the user has access to
            return {access.property_id for access in self.property_access}
        
        # Return properties with the required access level
        access_levels = {
            "viewer": 1,
            "editor": 2,
            "manager": 3,
            "owner": 4
        }
        required_level_value = access_levels.get(required_level, 0)
        
        return {
            access.property_id for access in self.property_access
            if access_levels.get(access.access_level, 0) >= required_level_value
        }
