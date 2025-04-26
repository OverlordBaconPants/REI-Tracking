"""
Geoapify service module for the REI-Tracker application.

This module provides the GeoapifyService class for address services,
including address validation, geocoding, and autocomplete.
"""

import requests
from typing import Dict, List, Any, Optional
import json

from src.config import current_config
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class GeoapifyService:
    """
    Geoapify service for address services.
    
    This class provides methods for address services, including address
    validation, geocoding, and autocomplete.
    """
    
    def __init__(self) -> None:
        """Initialize the Geoapify service."""
        self.api_key = current_config.GEOAPIFY_API_KEY
        self.base_url = "https://api.geoapify.com/v1"
        
        if not self.api_key:
            logger.warning("Geoapify API key not set")
    
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Geocode an address.
        
        Args:
            address: The address to geocode
            
        Returns:
            The geocoded address data, or None if not found
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        if not self.api_key:
            raise ValueError("Geoapify API key not set")
        
        try:
            url = f"{self.base_url}/geocode/search"
            params = {
                "text": address,
                "format": "json",
                "apiKey": self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("results"):
                return None
            
            return data["results"][0]
        except requests.RequestException as e:
            logger.error(f"Error geocoding address: {str(e)}")
            raise
    
    def validate_address(self, address: str) -> bool:
        """
        Validate an address.
        
        Args:
            address: The address to validate
            
        Returns:
            True if the address is valid, False otherwise
        """
        try:
            result = self.geocode_address(address)
            return result is not None
        except Exception as e:
            logger.error(f"Error validating address: {str(e)}")
            return False
    
    def get_address_components(self, address: str) -> Optional[Dict[str, str]]:
        """
        Get the components of an address.
        
        Args:
            address: The address to get components for
            
        Returns:
            The address components, or None if not found
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        result = self.geocode_address(address)
        
        if not result:
            return None
        
        components = {
            "formatted": result.get("formatted", ""),
            "street": result.get("street", ""),
            "house_number": result.get("housenumber", ""),
            "city": result.get("city", ""),
            "state": result.get("state", ""),
            "country": result.get("country", ""),
            "postal_code": result.get("postcode", ""),
            "latitude": result.get("lat", 0),
            "longitude": result.get("lon", 0)
        }
        
        return components
    
    def get_autocomplete_suggestions(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get autocomplete suggestions for an address.
        
        Args:
            text: The text to get suggestions for
            limit: The maximum number of suggestions to return
            
        Returns:
            The autocomplete suggestions
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        if not self.api_key:
            raise ValueError("Geoapify API key not set")
        
        try:
            url = f"{self.base_url}/geocode/autocomplete"
            params = {
                "text": text,
                "format": "json",
                "limit": limit,
                "apiKey": self.api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get("results"):
                return []
            
            return data["results"]
        except requests.RequestException as e:
            logger.error(f"Error getting autocomplete suggestions: {str(e)}")
            raise
    
    def get_distance_between_addresses(self, address1: str, address2: str) -> Optional[float]:
        """
        Get the distance between two addresses.
        
        Args:
            address1: The first address
            address2: The second address
            
        Returns:
            The distance in kilometers, or None if either address is not found
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        try:
            result1 = self.geocode_address(address1)
            result2 = self.geocode_address(address2)
            
            if not result1 or not result2:
                return None
            
            # Calculate distance using Haversine formula
            from math import radians, sin, cos, sqrt, atan2
            
            lat1 = radians(result1["lat"])
            lon1 = radians(result1["lon"])
            lat2 = radians(result2["lat"])
            lon2 = radians(result2["lon"])
            
            # Radius of the Earth in kilometers
            radius = 6371
            
            # Haversine formula
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = radius * c
            
            return distance
        except Exception as e:
            logger.error(f"Error getting distance between addresses: {str(e)}")
            return None
