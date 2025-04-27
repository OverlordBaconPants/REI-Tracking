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
    
    def calculate_correlation_score(self, subject_property: Dict[str, Any], comparable: Dict[str, Any]) -> float:
        """
        Calculate correlation score between subject property and comparable property.
        
        The correlation score is a measure of how similar the comparable property is to the subject property.
        Factors considered include:
        - Distance (closer is better)
        - Bedrooms (exact match is better)
        - Bathrooms (exact match is better)
        - Square footage (closer is better)
        - Year built (closer is better)
        
        Args:
            subject_property: The subject property data
            comparable: The comparable property data
            
        Returns:
            The correlation score (0-100, higher is better)
        """
        try:
            # Initialize score at 100 (perfect match)
            score = 100.0
            
            # Distance factor (up to 30 point reduction)
            distance = comparable.get("distance", 0)
            if distance > 0:
                # Exponential penalty for distance
                distance_penalty = min(30, 30 * (distance / 2))  # Max penalty at 2 miles
                score -= distance_penalty
            
            # Bedrooms factor (up to 15 point reduction)
            subject_bedrooms = subject_property.get("bedrooms", 0)
            comp_bedrooms = comparable.get("bedrooms", 0)
            if subject_bedrooms > 0 and comp_bedrooms > 0:
                bedroom_diff = abs(subject_bedrooms - comp_bedrooms)
                bedroom_penalty = min(15, 15 * bedroom_diff / 2)  # Max penalty at 2 bedroom difference
                score -= bedroom_penalty
            
            # Bathrooms factor (up to 15 point reduction)
            subject_bathrooms = subject_property.get("bathrooms", 0)
            comp_bathrooms = comparable.get("bathrooms", 0)
            if subject_bathrooms > 0 and comp_bathrooms > 0:
                bathroom_diff = abs(subject_bathrooms - comp_bathrooms)
                bathroom_penalty = min(15, 15 * bathroom_diff / 2)  # Max penalty at 2 bathroom difference
                score -= bathroom_penalty
            
            # Square footage factor (up to 20 point reduction)
            subject_sqft = subject_property.get("squareFootage", 0)
            comp_sqft = comparable.get("squareFootage", 0)
            if subject_sqft > 0 and comp_sqft > 0:
                sqft_diff_pct = abs(subject_sqft - comp_sqft) / subject_sqft if subject_sqft > 0 else 0
                sqft_penalty = min(20, 20 * sqft_diff_pct * 2)  # Max penalty at 50% difference
                score -= sqft_penalty
            
            # Year built factor (up to 10 point reduction)
            subject_year = subject_property.get("yearBuilt", 0)
            comp_year = comparable.get("yearBuilt", 0)
            if subject_year > 0 and comp_year > 0:
                year_diff = abs(subject_year - comp_year)
                year_penalty = min(10, 10 * year_diff / 20)  # Max penalty at 20 year difference
                score -= year_penalty
            
            # Ensure score is between 0 and 100
            score = max(0, min(100, score))
            
            return round(score, 1)
        except Exception as e:
            logger.error(f"Error calculating correlation score: {str(e)}")
            return 0.0
    
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
            
            # Extract subject property details
            subject_property = {
                "bedrooms": comparables_data.get("bedrooms", 0),
                "bathrooms": comparables_data.get("bathrooms", 0),
                "squareFootage": comparables_data.get("squareFootage", 0),
                "yearBuilt": comparables_data.get("yearBuilt", 0)
            }
            
            # Extract comparables
            comparables = []
            for comp in comparables_data.get("comparables", []):
                # Calculate correlation score if not already present
                correlation = comp.get("correlation", 0)
                if correlation == 0:
                    correlation = self.calculate_correlation_score(subject_property, comp)
                
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
                    "correlation": correlation
                }
                comparables.append(comparable)
            
            # Sort comparables by correlation score (highest first)
            comparables.sort(key=lambda x: x.get("correlation", 0), reverse=True)
            
            # Calculate estimated value using weighted average based on correlation scores
            if comparables:
                total_weight = sum(comp.get("correlation", 0) for comp in comparables)
                if total_weight > 0:
                    weighted_sum = sum(comp.get("price", 0) * comp.get("correlation", 0) for comp in comparables)
                    estimated_value = int(weighted_sum / total_weight)
                else:
                    # Fallback to simple average if correlation scores are all zero
                    prices = [comp.get("price", 0) for comp in comparables]
                    estimated_value = sum(prices) // len(prices)
                
                # Calculate value range (wider range for lower correlation scores)
                avg_correlation = total_weight / len(comparables) if total_weight > 0 else 50
                range_factor = 0.05 + (0.15 * (100 - avg_correlation) / 100)  # 5% to 20% range
                value_range_low = int(estimated_value * (1 - range_factor))
                value_range_high = int(estimated_value * (1 + range_factor))
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
                "comparables": comparables,
                "average_correlation": round(avg_correlation, 1) if comparables else 0
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
