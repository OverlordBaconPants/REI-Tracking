"""
Property repository module for the REI-Tracker application.

This module provides the PropertyRepository class for property data persistence
and retrieval.
"""

from typing import List, Optional, Dict, Any

from src.config import current_config
from src.models.property import Property
from src.repositories.base_repository import BaseRepository
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class PropertyRepository(BaseRepository[Property]):
    """
    Property repository for property data persistence and retrieval.
    
    This class provides methods for property-specific operations, such as
    finding properties by address and partner.
    """
    
    def __init__(self) -> None:
        """Initialize the property repository."""
        super().__init__(str(current_config.PROPERTIES_FILE), Property)
    
    def get_by_address(self, address: str) -> Optional[Property]:
        """
        Get a property by address.
        
        Args:
            address: Address of the property to get
            
        Returns:
            The property, or None if not found
        """
        try:
            properties = self.get_all()
            
            for prop in properties:
                if prop.address.lower() == address.lower():
                    return prop
            
            return None
        except Exception as e:
            logger.error(f"Error getting property by address: {str(e)}")
            raise
    
    def get_by_partner(self, partner_name: str) -> List[Property]:
        """
        Get properties by partner name.
        
        Args:
            partner_name: Name of the partner
            
        Returns:
            List of properties with the partner
        """
        try:
            properties = self.get_all()
            
            return [
                prop for prop in properties
                if any(partner.name.lower() == partner_name.lower() for partner in prop.partners)
            ]
        except Exception as e:
            logger.error(f"Error getting properties by partner: {str(e)}")
            raise
    
    def get_by_property_manager(self, manager_name: str) -> List[Property]:
        """
        Get properties by property manager name.
        
        Args:
            manager_name: Name of the property manager
            
        Returns:
            List of properties with the property manager
        """
        try:
            properties = self.get_all()
            
            return [
                prop for prop in properties
                if prop.get_property_manager() and
                prop.get_property_manager().name.lower() == manager_name.lower()
            ]
        except Exception as e:
            logger.error(f"Error getting properties by property manager: {str(e)}")
            raise
    
    def address_exists(self, address: str) -> bool:
        """
        Check if a property with the given address exists.
        
        Args:
            address: Address to check
            
        Returns:
            True if a property with the address exists, False otherwise
        """
        return self.get_by_address(address) is not None
