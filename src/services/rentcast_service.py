"""
Rentcast service module for the REI-Tracker application.

This module provides the RentcastService class for property valuation services,
including rental estimates and property comparables.
"""

import requests
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from src.config import current_config
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)


class RentcastService:
    """
    Rentcast service for property valuation services.
    
    This class provides methods for property valuation services, including
    rental estimates and property comparables.
    """
    
    def __init__(self) -> None:
        """Initialize the Rentcast service."""
        self.api_key = current_config.RENTCAST_API_KEY
        self.base_url = "https://api.rentcast.io/v1"
        
        if not self.api_key:
            logger.warning("Rentcast API key not set")
    
    def get_rental_estimate(self, address: str, bedrooms: int, bathrooms: float, 
                           square_feet: int) -> Optional[Dict[str, Any]]:
        """
        Get a rental estimate for a property.
        
        Args:
            address: The property address
            bedrooms: The number of bedrooms
            bathrooms: The number of bathrooms
            square_feet: The square footage
            
        Returns:
            The rental estimate data, or None if not found
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        if not self.api_key:
            raise ValueError("Rentcast API key not set")
        
        try:
            url = f"{self.base_url}/rental-estimate"
            headers = {
                "X-Api-Key": self.api_key
            }
            params = {
                "address": address,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "propertyType": "Single Family",
                "squareFootage": square_feet
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return data
        except requests.RequestException as e:
            logger.error(f"Error getting rental estimate: {str(e)}")
            raise
    
    def get_property_comparables(self, address: str, bedrooms: int, bathrooms: float, 
                               square_feet: int, radius_miles: float = 1.0, 
                               limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get property comparables.
        
        Args:
            address: The property address
            bedrooms: The number of bedrooms
            bathrooms: The number of bathrooms
            square_feet: The square footage
            radius_miles: The search radius in miles
            limit: The maximum number of comparables to return
            
        Returns:
            The property comparables data, or None if not found
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        if not self.api_key:
            raise ValueError("Rentcast API key not set")
        
        try:
            url = f"{self.base_url}/comparables"
            headers = {
                "X-Api-Key": self.api_key
            }
            params = {
                "address": address,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "propertyType": "Single Family",
                "squareFootage": square_feet,
                "radius": radius_miles,
                "limit": limit
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return data
        except requests.RequestException as e:
            logger.error(f"Error getting property comparables: {str(e)}")
            raise
    
    def get_property_value_estimate(self, address: str, bedrooms: int, bathrooms: float, 
                                  square_feet: int, year_built: int) -> Optional[Dict[str, Any]]:
        """
        Get a property value estimate.
        
        Args:
            address: The property address
            bedrooms: The number of bedrooms
            bathrooms: The number of bathrooms
            square_feet: The square footage
            year_built: The year the property was built
            
        Returns:
            The property value estimate data, or None if not found
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        if not self.api_key:
            raise ValueError("Rentcast API key not set")
        
        try:
            url = f"{self.base_url}/value-estimate"
            headers = {
                "X-Api-Key": self.api_key
            }
            params = {
                "address": address,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "propertyType": "Single Family",
                "squareFootage": square_feet,
                "yearBuilt": year_built
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return data
        except requests.RequestException as e:
            logger.error(f"Error getting property value estimate: {str(e)}")
            raise
    
    def get_market_statistics(self, city: str, state: str) -> Optional[Dict[str, Any]]:
        """
        Get market statistics for a city.
        
        Args:
            city: The city
            state: The state
            
        Returns:
            The market statistics data, or None if not found
            
        Raises:
            ValueError: If the API key is not set
            requests.RequestException: If the API request fails
        """
        if not self.api_key:
            raise ValueError("Rentcast API key not set")
        
        try:
            url = f"{self.base_url}/market-stats"
            headers = {
                "X-Api-Key": self.api_key
            }
            params = {
                "city": city,
                "state": state
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return data
        except requests.RequestException as e:
            logger.error(f"Error getting market statistics: {str(e)}")
            raise
    
    def format_comparables_for_analysis(self, comparables_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format property comparables data for analysis.
        
        Args:
            comparables_data: The property comparables data
            
        Returns:
            The formatted comparables data
        """
        try:
            if not comparables_data or "comparables" not in comparables_data:
                return {
                    "last_run": datetime.now().isoformat(),
                    "run_count": 1,
                    "estimated_value": 0,
                    "value_range_low": 0,
                    "value_range_high": 0,
                    "comparables": []
                }
            
            # Extract comparables
            comparables = []
            for comp in comparables_data.get("comparables", []):
                comparable = {
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
                    "removedDate": comp.get("removedDate", None),
                    "daysOnMarket": comp.get("daysOnMarket", 0),
                    "distance": comp.get("distance", 0),
                    "correlation": comp.get("correlation", 0)
                }
                comparables.append(comparable)
            
            # Calculate estimated value
            prices = [comp.get("price", 0) for comp in comparables]
            if prices:
                estimated_value = sum(prices) // len(prices)
                value_range_low = int(estimated_value * 0.95)
                value_range_high = int(estimated_value * 1.05)
            else:
                estimated_value = 0
                value_range_low = 0
                value_range_high = 0
            
            # Format result
            result = {
                "last_run": datetime.now().isoformat(),
                "run_count": 1,
                "estimated_value": estimated_value,
                "value_range_low": value_range_low,
                "value_range_high": value_range_high,
                "comparables": comparables
            }
            
            return result
        except Exception as e:
            logger.error(f"Error formatting comparables data: {str(e)}")
            return {
                "last_run": datetime.now().isoformat(),
                "run_count": 1,
                "estimated_value": 0,
                "value_range_low": 0,
                "value_range_high": 0,
                "comparables": []
            }
