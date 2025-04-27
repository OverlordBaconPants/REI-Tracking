"""
Partner equity service module for the REI-Tracker application.

This module provides the PartnerEquityService class for managing partner equity,
contributions, and distributions.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal

from src.models.property import Property, Partner
from src.models.partner_contribution import PartnerContribution
from src.repositories.property_repository import PropertyRepository
from src.repositories.partner_contribution_repository import PartnerContributionRepository
from src.utils.logging_utils import get_logger, audit_logger

# Set up logger
logger = get_logger(__name__)


class PartnerEquityService:
    """
    Partner equity service for managing partner equity, contributions, and distributions.
    
    This class provides methods for managing partner equity, including
    adding and removing partners, updating equity shares, and tracking
    contributions and distributions.
    """
    
    def __init__(
        self,
        property_repository: Optional[PropertyRepository] = None,
        partner_contribution_repository: Optional[PartnerContributionRepository] = None
    ) -> None:
        """
        Initialize the partner equity service.
        
        Args:
            property_repository: The property repository to use
            partner_contribution_repository: The partner contribution repository to use
        """
        self.property_repository = property_repository or PropertyRepository()
        self.partner_contribution_repository = partner_contribution_repository or PartnerContributionRepository()
    
    def add_partner(
        self,
        property_id: str,
        partner_name: str,
        equity_share: Decimal,
        is_property_manager: bool = False,
        visibility_settings: Optional[Dict[str, bool]] = None,
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Add a partner to a property.
        
        Args:
            property_id: The ID of the property to add the partner to
            partner_name: The name of the partner to add
            equity_share: The equity share to assign to the partner
            is_property_manager: Whether the partner is the property manager
            visibility_settings: The visibility settings for the partner
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the partner was added successfully
        """
        try:
            # Get property
            property_obj = self.property_repository.get_by_id(property_id)
            
            if not property_obj:
                logger.warning(f"Failed to add partner: Property not found")
                return False
            
            # Check if partner already exists
            existing_partner = next(
                (p for p in property_obj.partners if p.name == partner_name),
                None
            )
            
            if existing_partner:
                logger.warning(f"Failed to add partner: Partner already exists")
                return False
            
            # Create new partner
            new_partner = Partner(
                name=partner_name,
                equity_share=equity_share,
                is_property_manager=is_property_manager,
                visibility_settings=visibility_settings or {}
            )
            
            # If this partner is the property manager, remove any existing property manager
            if is_property_manager:
                for partner in property_obj.partners:
                    if partner.is_property_manager:
                        partner.is_property_manager = False
            
            # Add partner to property
            property_obj.partners.append(new_partner)
            
            # Validate property (this will check total equity = 100% and only one property manager)
            try:
                property_obj.dict()
            except Exception as e:
                logger.warning(f"Failed to add partner: {str(e)}")
                return False
            
            # Update property
            success = self.property_repository.update(property_obj)
            
            # Log action
            if success and current_user_id:
                audit_logger.log_user_action(
                    user_id=current_user_id,
                    action="add_partner",
                    resource_type="property",
                    resource_id=property_id,
                    details={
                        "partner_name": partner_name,
                        "equity_share": float(equity_share),
                        "is_property_manager": is_property_manager
                    }
                )
                logger.info(f"Added partner {partner_name} to property {property_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error adding partner: {str(e)}")
            return False
    
    def remove_partner(
        self,
        property_id: str,
        partner_name: str,
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Remove a partner from a property.
        
        Args:
            property_id: The ID of the property to remove the partner from
            partner_name: The name of the partner to remove
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the partner was removed successfully
        """
        try:
            # Get property
            property_obj = self.property_repository.get_by_id(property_id)
            
            if not property_obj:
                logger.warning(f"Failed to remove partner: Property not found")
                return False
            
            # Check if partner exists
            existing_partner = next(
                (p for p in property_obj.partners if p.name == partner_name),
                None
            )
            
            if not existing_partner:
                logger.warning(f"Failed to remove partner: Partner not found")
                return False
            
            # Remove partner from property
            property_obj.partners = [
                p for p in property_obj.partners if p.name != partner_name
            ]
            
            # Validate property (this will check total equity = 100% and only one property manager)
            try:
                property_obj.dict()
            except Exception as e:
                logger.warning(f"Failed to remove partner: {str(e)}")
                return False
            
            # Update property
            success = self.property_repository.update(property_obj)
            
            # Log action
            if success and current_user_id:
                audit_logger.log_user_action(
                    user_id=current_user_id,
                    action="remove_partner",
                    resource_type="property",
                    resource_id=property_id,
                    details={
                        "partner_name": partner_name
                    }
                )
                logger.info(f"Removed partner {partner_name} from property {property_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error removing partner: {str(e)}")
            return False
    
    def update_partner_equity(
        self,
        property_id: str,
        partner_name: str,
        equity_share: Decimal,
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Update a partner's equity share.
        
        Args:
            property_id: The ID of the property to update the partner for
            partner_name: The name of the partner to update
            equity_share: The new equity share to assign to the partner
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the partner's equity share was updated successfully
        """
        try:
            # Get property
            property_obj = self.property_repository.get_by_id(property_id)
            
            if not property_obj:
                logger.warning(f"Failed to update partner equity: Property not found")
                return False
            
            # Check if partner exists
            existing_partner = next(
                (p for p in property_obj.partners if p.name == partner_name),
                None
            )
            
            if not existing_partner:
                logger.warning(f"Failed to update partner equity: Partner not found")
                return False
            
            # Update partner's equity share
            existing_partner.equity_share = equity_share
            
            # Validate property (this will check total equity = 100% and only one property manager)
            try:
                property_obj.dict()
            except Exception as e:
                logger.warning(f"Failed to update partner equity: {str(e)}")
                return False
            
            # Update property
            success = self.property_repository.update(property_obj)
            
            # Log action
            if success and current_user_id:
                audit_logger.log_user_action(
                    user_id=current_user_id,
                    action="update_partner_equity",
                    resource_type="property",
                    resource_id=property_id,
                    details={
                        "partner_name": partner_name,
                        "equity_share": float(equity_share)
                    }
                )
                logger.info(f"Updated equity share for partner {partner_name} on property {property_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error updating partner equity: {str(e)}")
            return False
    
    def update_partner_visibility_settings(
        self,
        property_id: str,
        partner_name: str,
        visibility_settings: Dict[str, bool],
        current_user_id: Optional[str] = None
    ) -> bool:
        """
        Update a partner's visibility settings.
        
        Args:
            property_id: The ID of the property to update the partner for
            partner_name: The name of the partner to update
            visibility_settings: The new visibility settings for the partner
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            Whether the partner's visibility settings were updated successfully
        """
        try:
            # Get property
            property_obj = self.property_repository.get_by_id(property_id)
            
            if not property_obj:
                logger.warning(f"Failed to update partner visibility settings: Property not found")
                return False
            
            # Check if partner exists
            existing_partner = next(
                (p for p in property_obj.partners if p.name == partner_name),
                None
            )
            
            if not existing_partner:
                logger.warning(f"Failed to update partner visibility settings: Partner not found")
                return False
            
            # Update partner's visibility settings
            existing_partner.visibility_settings = visibility_settings
            
            # Validate property
            try:
                property_obj.dict()
            except Exception as e:
                logger.warning(f"Failed to update partner visibility settings: {str(e)}")
                return False
            
            # Update property
            success = self.property_repository.update(property_obj)
            
            # Log action
            if success and current_user_id:
                audit_logger.log_user_action(
                    user_id=current_user_id,
                    action="update_partner_visibility_settings",
                    resource_type="property",
                    resource_id=property_id,
                    details={
                        "partner_name": partner_name,
                        "visibility_settings": visibility_settings
                    }
                )
                logger.info(f"Updated visibility settings for partner {partner_name} on property {property_id}")
            
            return success
        except Exception as e:
            logger.error(f"Error updating partner visibility settings: {str(e)}")
            return False
    
    def add_contribution(
        self,
        property_id: str,
        partner_name: str,
        amount: Decimal,
        contribution_type: str,
        date: str,
        notes: Optional[str] = None,
        current_user_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Add a contribution or distribution for a partner.
        
        Args:
            property_id: The ID of the property the contribution is for
            partner_name: The name of the partner making the contribution
            amount: The amount of the contribution
            contribution_type: The type of contribution ("contribution" or "distribution")
            date: The date of the contribution
            notes: Optional notes about the contribution
            current_user_id: The ID of the user performing the action (for audit logging)
            
        Returns:
            The ID of the created contribution, or None if the contribution was not created
        """
        try:
            # Get property
            property_obj = self.property_repository.get_by_id(property_id)
            
            if not property_obj:
                logger.warning(f"Failed to add contribution: Property not found")
                return None
            
            # Check if partner exists
            existing_partner = next(
                (p for p in property_obj.partners if p.name == partner_name),
                None
            )
            
            if not existing_partner:
                logger.warning(f"Failed to add contribution: Partner not found")
                return None
            
            # Create contribution
            contribution = PartnerContribution(
                property_id=property_id,
                partner_name=partner_name,
                amount=amount,
                contribution_type=contribution_type,
                date=date,
                notes=notes
            )
            
            # Save contribution
            created_contribution = self.partner_contribution_repository.create(contribution)
            
            if not created_contribution:
                logger.warning(f"Failed to add contribution: Could not create contribution")
                return None
            
            # Log action
            if current_user_id:
                audit_logger.log_user_action(
                    user_id=current_user_id,
                    action=f"add_{contribution_type}",
                    resource_type="property",
                    resource_id=property_id,
                    details={
                        "partner_name": partner_name,
                        "amount": float(amount),
                        "date": date,
                        "notes": notes
                    }
                )
                logger.info(f"Added {contribution_type} for partner {partner_name} on property {property_id}")
            
            return created_contribution.id
        except Exception as e:
            logger.error(f"Error adding contribution: {str(e)}")
            return None
    
    def get_contributions_by_property(self, property_id: str) -> List[PartnerContribution]:
        """
        Get all contributions for a property.
        
        Args:
            property_id: The ID of the property to get contributions for
            
        Returns:
            List of contributions for the property
        """
        try:
            return self.partner_contribution_repository.get_by_property(property_id)
        except Exception as e:
            logger.error(f"Error getting contributions by property: {str(e)}")
            return []
    
    def get_contributions_by_partner(self, partner_name: str) -> List[PartnerContribution]:
        """
        Get all contributions for a partner.
        
        Args:
            partner_name: The name of the partner to get contributions for
            
        Returns:
            List of contributions for the partner
        """
        try:
            return self.partner_contribution_repository.get_by_partner(partner_name)
        except Exception as e:
            logger.error(f"Error getting contributions by partner: {str(e)}")
            return []
    
    def get_contributions_by_property_and_partner(
        self,
        property_id: str,
        partner_name: str
    ) -> List[PartnerContribution]:
        """
        Get all contributions for a property and partner.
        
        Args:
            property_id: The ID of the property to get contributions for
            partner_name: The name of the partner to get contributions for
            
        Returns:
            List of contributions for the property and partner
        """
        try:
            return self.partner_contribution_repository.get_by_property_and_partner(
                property_id, partner_name
            )
        except Exception as e:
            logger.error(f"Error getting contributions by property and partner: {str(e)}")
            return []
    
    def get_total_contributions_by_property(self, property_id: str) -> Dict[str, float]:
        """
        Get total contributions by property ID.
        
        Args:
            property_id: The ID of the property to get contributions for
            
        Returns:
            Dictionary mapping partner names to their total contribution amount
        """
        try:
            return self.partner_contribution_repository.get_total_contributions_by_property(property_id)
        except Exception as e:
            logger.error(f"Error getting total contributions by property: {str(e)}")
            return {}
