import requests
from typing import Dict, Optional
from datetime import datetime
import logging
from urllib.parse import quote

logger = logging.getLogger(__name__)

class RentcastAPIError(Exception):
    """Custom exception for RentCast API errors"""
    pass

def format_address(address: str) -> str:
    """
    Format address string for RentCast API.
    RentCast expects: Street, City, State, Zip
    """
    try:
        # Split address into parts
        parts = [part.strip() for part in address.split(',')]
        
        # Extract the components we need
        street = parts[0]  # First part is always street
        city = parts[1] if len(parts) > 1 else ''
        state = parts[2].strip().split()[0] if len(parts) > 2 else ''  # Get just the state code
        zip_code = parts[2].strip().split()[1] if len(parts) > 2 else ''  # Get just the zip code
        
        # Combine into RentCast format
        formatted = f"{street}, {city}, {state} {zip_code}"
        
        # Remove any "United States" or similar
        formatted = formatted.split('United States')[0].strip().rstrip(',')
        
        # Clean up any double spaces or commas
        formatted = formatted.replace('  ', ' ').replace(', ,', ',')
        
        logger.debug(f"Formatted address from '{address}' to '{formatted}'")
        
        return quote(formatted)
        
    except Exception as e:
        logger.error(f"Error formatting address: {str(e)}")
        # If anything goes wrong, return the original address quoted
        return quote(address)

def fetch_property_comps(
    app_config,
    address: str,
    property_type: str,
    bedrooms: float,
    bathrooms: float,
    square_footage: float
) -> Optional[Dict]:
    try:
        logger.debug(f"Fetching comps for address: {address}")
        
        # Format address
        formatted_address = format_address(address)
        logger.debug(f"Formatted address: {formatted_address}")
        
        # Verify config
        api_base_url = app_config.get('RENTCAST_API_BASE_URL')
        api_key = app_config.get('RENTCAST_API_KEY')
        comp_defaults = app_config.get('RENTCAST_COMP_DEFAULTS')
        
        if not all([api_base_url, api_key, comp_defaults]):
            raise RentcastAPIError("Missing required RentCast configuration")
        
        # Construct request
        url = f"{api_base_url}/avm/value"
        params = {
            'address': formatted_address,
            'propertyType': property_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'squareFootage': square_footage,
            'maxRadius': comp_defaults.get('maxRadius', 1.0),
            'daysOld': comp_defaults.get('daysOld', 180),
            'compCount': comp_defaults.get('compCount', 5)
        }
        
        # Log request details (excluding API key)
        logger.debug(f"Request URL: {url}")
        logger.debug(f"Request params: {params}")
        
        headers = {
            'accept': 'application/json',
            'X-Api-Key': api_key
        }
        
        # Make request
        response = requests.get(url, params=params, headers=headers)
        
        # Handle non-200 responses
        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_details = response.json()
                error_msg += f": {error_details.get('message', '')}"
            except:
                error_msg += f": {response.text}"
            raise RentcastAPIError(error_msg)
            
        # Parse response
        data = response.json()
        logger.debug("Successfully received comps data")
        
        data['last_run'] = datetime.utcnow().isoformat()
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"RentCast API request failed: {str(e)}")
        raise RentcastAPIError(f"Failed to fetch property comps: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing RentCast API response: {str(e)}")
        raise RentcastAPIError(f"Error processing comps data: {str(e)}")

def update_analysis_comps(analysis: Dict, comps_data: Dict, run_count: int) -> Dict:
    """
    Update analysis with new comps data
    
    Args:
        analysis: Current analysis dictionary
        comps_data: Comps data from RentCast API
        run_count: Current session run count
        
    Returns:
        Updated analysis dictionary
    """
    analysis['comps_data'] = {
        'last_run': comps_data['last_run'],
        'run_count': run_count,
        'estimated_value': comps_data['price'],
        'value_range_low': comps_data['priceRangeLow'],
        'value_range_high': comps_data['priceRangeHigh'],
        'comparables': comps_data['comparables']
    }
    
    return analysis