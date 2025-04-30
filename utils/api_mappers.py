"""
API Mapper classes for standardizing external API responses to match our data structures.

This module provides mapper classes that transform external API responses into
standardized formats that match our internal data structures as defined in DATA_STRUCTURES.md.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union


class RentcastApiMapper:
    """
    Maps RentCast API responses to our standardized data structure format.
    
    This class provides static methods to transform the raw API responses from
    RentCast into our standardized data structures, ensuring consistent field
    naming throughout the application.
    """
    
    @staticmethod
    def map_property_comps(api_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Map property comps API response to our standardized format.
        
        Args:
            api_response: Raw API response from RentCast
            
        Returns:
            Standardized comps data structure or None if input is invalid
        """
        if not api_response:
            return None
            
        # Create standardized structure with proper field names
        mapped_data = {
            "last_run": datetime.utcnow().isoformat(),
            "run_count": 1,  # This would be managed by the calling code
            "estimated_value": api_response.get("price", 0),
            "value_range_low": api_response.get("priceRangeLow", 0),
            "value_range_high": api_response.get("priceRangeHigh", 0),
            "comparables": []
        }
        
        # Map each comparable property
        for comp in api_response.get("comparables", []):
            mapped_comp = {
                "id": comp.get("id", ""),
                "formattedAddress": comp.get("formattedAddress", ""),
                "city": comp.get("city", ""),
                "state": comp.get("state", ""),
                "zipCode": comp.get("zipCode", ""),
                "propertyType": comp.get("propertyType", ""),
                "bedrooms": comp.get("bedrooms", 0),
                "bathrooms": comp.get("bathrooms", 0),
                "squareFootage": comp.get("squareFootage", 0),
                "yearBuilt": comp.get("yearBuilt", 0),
                "price": comp.get("price", 0),
                "listingType": comp.get("listingType", ""),
                "listedDate": comp.get("listedDate", ""),
                "removedDate": comp.get("removedDate", ""),
                "daysOnMarket": comp.get("daysOnMarket", 0),
                "distance": comp.get("distance", 0),
                "correlation": comp.get("correlation", 0)
            }
            mapped_data["comparables"].append(mapped_comp)
            
        return mapped_data
        
    @staticmethod
    def map_rental_comps(api_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Map rental comps API response to our standardized format.
        
        Args:
            api_response: Raw API response from RentCast
            
        Returns:
            Standardized rental comps data structure or None if input is invalid
        """
        if not api_response:
            return None
            
        return {
            "last_run": datetime.utcnow().isoformat(),
            "estimated_rent": api_response.get("rent", 0),
            "rent_range_low": api_response.get("rentRangeLow", 0),
            "rent_range_high": api_response.get("rentRangeHigh", 0),
            "comparable_rentals": api_response.get("comparables", []),
            "confidence_score": api_response.get("confidenceScore", 0)
        }


class ApiMapperFactory:
    """
    Factory class for getting the appropriate API mapper.
    
    This class provides a centralized way to get the appropriate mapper
    for different external APIs, making it easy to add new mappers in the future.
    """
    
    @staticmethod
    def get_mapper(api_name: str) -> Any:
        """
        Get the appropriate mapper for the specified API.
        
        Args:
            api_name: Name of the API to get a mapper for
            
        Returns:
            Mapper class for the specified API
            
        Raises:
            ValueError: If no mapper is available for the specified API
        """
        mappers = {
            "rentcast": RentcastApiMapper
        }
        
        mapper = mappers.get(api_name.lower())
        if not mapper:
            raise ValueError(f"No mapper available for API: {api_name}")
            
        return mapper
