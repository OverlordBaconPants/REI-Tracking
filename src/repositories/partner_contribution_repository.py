"""
Partner contribution repository module for the REI-Tracker application.

This module provides the PartnerContributionRepository class for partner contribution
data persistence and retrieval.
"""

from typing import List, Optional, Dict, Any

from src.config import current_config
from src.models.partner_contribution import PartnerContribution
from src.repositories.base_repository import BaseRepository
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class PartnerContributionRepository(BaseRepository[PartnerContribution]):
    """
    Partner contribution repository for partner contribution data persistence and retrieval.
    
    This class provides methods for partner contribution-specific operations, such as
    finding contributions by property and partner.
    """
    
    def __init__(self) -> None:
        """Initialize the partner contribution repository."""
        super().__init__(str(current_config.PARTNER_CONTRIBUTIONS_FILE), PartnerContribution)
    
    def get_by_property(self, property_id: str) -> List[PartnerContribution]:
        """
        Get contributions by property ID.
        
        Args:
            property_id: ID of the property to get contributions for
            
        Returns:
            List of contributions for the property
        """
        try:
            contributions = self.get_all()
            
            return [
                contribution for contribution in contributions
                if contribution.property_id == property_id
            ]
        except Exception as e:
            logger.error(f"Error getting contributions by property: {str(e)}")
            raise
    
    def get_by_partner(self, partner_name: str) -> List[PartnerContribution]:
        """
        Get contributions by partner name.
        
        Args:
            partner_name: Name of the partner to get contributions for
            
        Returns:
            List of contributions for the partner
        """
        try:
            contributions = self.get_all()
            
            return [
                contribution for contribution in contributions
                if contribution.partner_name == partner_name
            ]
        except Exception as e:
            logger.error(f"Error getting contributions by partner: {str(e)}")
            raise
    
    def get_by_property_and_partner(self, property_id: str, partner_name: str) -> List[PartnerContribution]:
        """
        Get contributions by property ID and partner name.
        
        Args:
            property_id: ID of the property to get contributions for
            partner_name: Name of the partner to get contributions for
            
        Returns:
            List of contributions for the property and partner
        """
        try:
            contributions = self.get_all()
            
            return [
                contribution for contribution in contributions
                if contribution.property_id == property_id and contribution.partner_name == partner_name
            ]
        except Exception as e:
            logger.error(f"Error getting contributions by property and partner: {str(e)}")
            raise
    
    def get_total_contributions_by_property(self, property_id: str) -> Dict[str, float]:
        """
        Get total contributions by property ID.
        
        Args:
            property_id: ID of the property to get contributions for
            
        Returns:
            Dictionary mapping partner names to their total contribution amount
        """
        try:
            contributions = self.get_by_property(property_id)
            
            # Initialize result dictionary
            result = {}
            
            # Calculate total contributions for each partner
            for contribution in contributions:
                if contribution.partner_name not in result:
                    result[contribution.partner_name] = 0.0
                
                if contribution.contribution_type == "contribution":
                    result[contribution.partner_name] += float(contribution.amount)
                else:  # distribution
                    result[contribution.partner_name] -= float(contribution.amount)
            
            return result
        except Exception as e:
            logger.error(f"Error getting total contributions by property: {str(e)}")
            raise
