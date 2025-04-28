"""
User model module for the REI-Tracker application.

This module provides the User model for user authentication and management.
"""

from typing import Optional, List, Dict, Any, Set
from pydantic import Field, field_validator, model_validator, ConfigDict

from src.models.base_model import BaseModel
from src.utils.validation_utils import validate_email, validate_phone


class PropertyAccess(BaseModel):
    """
    Property access model for user permissions.
    
    This class represents a user's access to a specific property,
    including access level and permissions.
    """
    
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True
    )
    
    property_id: str
    access_level: str = "viewer"  # "owner", "manager", "editor", "viewer"
    equity_share: Optional[float] = None
    
    @field_validator("access_level")
    @classmethod
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
    
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True
    )
    
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
    
    @field_validator("email")
    @classmethod
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
    
    @field_validator("phone")
    @classmethod
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
    
    @model_validator(mode='after')
    def set_full_name(self) -> 'User':
        """
        Set full name from first and last name if not provided.
        
        Returns:
            The user instance with full name set
        """
        if not self.name:
            if self.first_name and self.last_name:
                self.name = f"{self.first_name} {self.last_name}"
            else:
                self.name = self.first_name or self.last_name or ""
        return self
    
    @field_validator("role")
    @classmethod
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
    
    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary, excluding sensitive fields.
        
        Returns:
            Dictionary representation of the model
        """
        exclude = kwargs.pop("exclude", set())
        exclude.add("password")
        
        return super().model_dump(*args, exclude=exclude, **kwargs)
    
    # Alias for backward compatibility
    def dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Convert model to dictionary, excluding sensitive fields (alias for model_dump).
        
        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(*args, **kwargs)
    
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
