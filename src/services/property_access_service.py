"""
Property access service module for the REI-Tracker application.

This module provides the PropertyAccessService class for managing property access
and property manager designation.
"""

from typing import List, Dict, Any, Optional, Set
from decimal import Decimal

from src.models.user import User, PropertyAccess
from src.models.property import Property, Partner
from src.repositories.user_repository import UserRepository
from src.repositories.property_repository import PropertyRepository
from src.utils.logging_utils import get_logger, audit_logger

# Set up logger
logger = get_logger(__name__)


class PropertyAccessService:
    """
    Property access service for managing property access and property manager designation.
    
    This class provides methods for managing property access, including
    granting and revoking access, and designating property managers.
    """
    
    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        property_repository: Optional[PropertyRepository] = None
    ) -> None:
        """
        Initialize the property access service.
        
        Args:
            user_repository: The user repository to use
            property_repository: The property repository to use
        """
        self.user_repository = user_repository or UserRepository()
        self.property_repository = property_repository or PropertyRepository()
    
    def grant_property_access(
        self,
        user_id: str,
        property_id: str,
        access_level: str,
        equity_share: Optional[float] = None,
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Grant property access to a user.
        
        Args:
            user_id: The ID of the user to grant access to
            property_id: The ID of the property to grant access to
            access_level: The access level to grant
            equity_share: The equity share to assign (optional)
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the access was granted successfully
        """
        # Get user and property
        user = self.user_repository.get_by_id(user_id)
        property_obj = self.property_repository.get_by_id(property_id)
        
        if not user or not property_obj:
            logger.warning(f"Failed to grant property access: User or property not found")
            return False
        
        # Check if user already has access to the property
        existing_access = next(
            (access for access in user.property_access if access.property_id == property_id),
            None
        )
        
        if existing_access:
            # Update existing access
            existing_access.access_level = access_level
            if equity_share is not None:
                existing_access.equity_share = equity_share
        else:
            # Create new access
            new_access = PropertyAccess(
                property_id=property_id,
                access_level=access_level,
                equity_share=equity_share
            )
            user.property_access.append(new_access)
        
        # Update user
        success = self.user_repository.update(user)
        
        # Log action
        if success and current_user_id:
            audit_logger.log_user_action(
                user_id=current_user_id,
                action="grant_property_access",
                resource_type="property",
                resource_id=property_id,
                details={
                    "target_user_id": user_id,
                    "access_level": access_level,
                    "equity_share": equity_share
                }
            )
            logger.info(f"Granted {access_level} access to property {property_id} for user {user_id}")
        
        return success
    
    def revoke_property_access(
        self,
        user_id: str,
        property_id: str,
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Revoke property access from a user.
        
        Args:
            user_id: The ID of the user to revoke access from
            property_id: The ID of the property to revoke access to
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the access was revoked successfully
        """
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            logger.warning(f"Failed to revoke property access: User not found")
            return False
        
        # Check if user has access to the property
        initial_access_count = len(user.property_access)
        user.property_access = [
            access for access in user.property_access
            if access.property_id != property_id
        ]
        
        # If no access was removed, return False
        if len(user.property_access) == initial_access_count:
            logger.warning(f"Failed to revoke property access: User does not have access to property")
            return False
        
        # Update user
        success = self.user_repository.update(user)
        
        # Log action
        if success and current_user_id:
            audit_logger.log_user_action(
                user_id=current_user_id,
                action="revoke_property_access",
                resource_type="property",
                resource_id=property_id,
                details={
                    "target_user_id": user_id
                }
            )
            logger.info(f"Revoked access to property {property_id} for user {user_id}")
        
        return success
    
    def designate_property_manager(
        self,
        user_id: str,
        property_id: str,
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Designate a user as a property manager.
        
        Args:
            user_id: The ID of the user to designate as a property manager
            property_id: The ID of the property to manage
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the designation was successful
        """
        # Get user and property
        user = self.user_repository.get_by_id(user_id)
        property_obj = self.property_repository.get_by_id(property_id)
        
        if not user or not property_obj:
            logger.warning(f"Failed to designate property manager: User or property not found")
            return False
        
        # Grant manager access to the user
        success = self.grant_property_access(
            user_id=user_id,
            property_id=property_id,
            access_level="manager",
            current_user_id=current_user_id
        )
        
        if not success:
            logger.warning(f"Failed to designate property manager: Could not grant access")
            return False
        
        # Update property partners
        # Find if user is already a partner
        existing_partner = next(
            (partner for partner in property_obj.partners if partner.name == user.name),
            None
        )
        
        if existing_partner:
            # Update existing partner
            existing_partner.is_property_manager = True
        else:
            # Create new partner with 0% equity
            new_partner = Partner(
                name=user.name,
                equity_share=Decimal("0"),
                is_property_manager=True
            )
            
            # Remove any existing property manager
            for partner in property_obj.partners:
                if partner.is_property_manager:
                    partner.is_property_manager = False
            
            property_obj.partners.append(new_partner)
        
        # Update property
        success = self.property_repository.update(property_obj)
        
        # Log action
        if success and current_user_id:
            audit_logger.log_user_action(
                user_id=current_user_id,
                action="designate_property_manager",
                resource_type="property",
                resource_id=property_id,
                details={
                    "target_user_id": user_id
                }
            )
            logger.info(f"Designated user {user_id} as manager for property {property_id}")
        
        return success
    
    def remove_property_manager(
        self,
        property_id: str,
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Remove the property manager designation.
        
        Args:
            property_id: The ID of the property to remove the manager from
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the removal was successful
        """
        # Get property
        property_obj = self.property_repository.get_by_id(property_id)
        
        if not property_obj:
            logger.warning(f"Failed to remove property manager: Property not found")
            return False
        
        # Find the current property manager
        property_manager = property_obj.get_property_manager()
        
        if not property_manager:
            logger.warning(f"Failed to remove property manager: No property manager found")
            return False
        
        # Remove property manager designation
        property_manager.is_property_manager = False
        
        # Update property
        success = self.property_repository.update(property_obj)
        
        # Find the user with manager access and downgrade to editor
        users = self.user_repository.get_all()
        for user in users:
            for access in user.property_access:
                if access.property_id == property_id and access.access_level == "manager":
                    access.access_level = "editor"
                    self.user_repository.update(user)
                    
                    # Log action
                    if current_user_id:
                        audit_logger.log_user_action(
                            user_id=current_user_id,
                            action="remove_property_manager",
                            resource_type="property",
                            resource_id=property_id,
                            details={
                                "target_user_id": user.id
                            }
                        )
                        logger.info(f"Removed user {user.id} as manager for property {property_id}")
        
        return success
    
    def sync_property_partners(self, property_id: str) -> bool:
        """
        Synchronize property partners with user access.
        
        This method ensures that all property partners have corresponding
        user access entries, and that equity shares are consistent.
        
        Args:
            property_id: The ID of the property to synchronize
            
        Returns:
            Whether the synchronization was successful
        """
        # Get property
        property_obj = self.property_repository.get_by_id(property_id)
        
        if not property_obj:
            logger.warning(f"Failed to sync property partners: Property not found")
            return False
        
        # Get all users
        users = self.user_repository.get_all()
        
        # Map of user names to user objects
        user_map = {user.name: user for user in users}
        
        # Sync partners to users
        for partner in property_obj.partners:
            # Find user by name
            user = user_map.get(partner.name)
            
            if user:
                # Grant appropriate access level
                access_level = "owner"
                if partner.is_property_manager:
                    access_level = "manager"
                
                self.grant_property_access(
                    user_id=user.id,
                    property_id=property_id,
                    access_level=access_level,
                    equity_share=float(partner.equity_share)
                )
        
        logger.info(f"Synchronized partners for property {property_id}")
        return True
    
    def get_users_with_property_access(
        self,
        property_id: str,
        access_level: Optional[str] = None
    ) -> List[User]:
        """
        Get users with access to a property.
        
        Args:
            property_id: The ID of the property to check
            access_level: The minimum required access level (optional)
            
        Returns:
            A list of users with access to the property
        """
        # Get all users
        users = self.user_repository.get_all()
        
        # Filter users with access to the property
        return [
            user for user in users
            if user.has_property_access(property_id, access_level)
        ]
    
    def get_property_manager(self, property_id: str) -> Optional[User]:
        """
        Get the property manager for a property.
        
        Args:
            property_id: The ID of the property to check
            
        Returns:
            The property manager, or None if there isn't one
        """
        # Get users with manager access
        managers = self.get_users_with_property_access(
            property_id=property_id,
            access_level="manager"
        )
        
        # Return the first manager (there should be at most one)
        return managers[0] if managers else None
    
    def get_accessible_properties(self, user_id: str) -> List[Property]:
        """
        Get properties that a user has access to.
        
        Args:
            user_id: The ID of the user to check
            
        Returns:
            A list of properties the user has access to
        """
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            logger.warning(f"Failed to get accessible properties: User not found")
            return []
        
        # Get all properties
        all_properties = self.property_repository.get_all()
        
        # If user is admin, return all properties
        if user.is_admin():
            return all_properties
        
        # Get property IDs the user has access to
        accessible_property_ids = {
            access.property_id for access in user.property_access
        }
        
        # Filter properties by access
        return [
            prop for prop in all_properties
            if prop.id in accessible_property_ids
        ]
    
    def can_access_property(self, user_id: str, property_id: str) -> bool:
        """
        Check if a user can access a property.
        
        Args:
            user_id: The ID of the user to check
            property_id: The ID of the property to check
            
        Returns:
            Whether the user can access the property
        """
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            logger.warning(f"Failed to check property access: User not found")
            return False
        
        # If user is admin, they can access all properties
        if user.is_admin():
            return True
        
        # Check if user has access to the property
        return user.has_property_access(property_id)
    
    def can_manage_property(self, user_id: str, property_id: str) -> bool:
        """
        Check if a user can manage a property.
        
        Args:
            user_id: The ID of the user to check
            property_id: The ID of the property to check
            
        Returns:
            Whether the user can manage the property
        """
        # Get user
        user = self.user_repository.get_by_id(user_id)
        
        if not user:
            logger.warning(f"Failed to check property management: User not found")
            return False
        
        # If user is admin, they can manage all properties
        if user.is_admin():
            return True
        
        # Check if user has manager or owner access to the property
        return user.has_property_access(property_id, "manager")
