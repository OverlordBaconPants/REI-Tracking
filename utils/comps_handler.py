import requests
from typing import Dict, Optional
from datetime import datetime
import logging
from flask import session, current_app

logger = logging.getLogger(__name__)

class RentcastAPIError(Exception):
    """Custom exception for RentCast API errors"""
    pass

def format_address(address: str) -> str:
    """
    Format address string for RentCast API.
    Converts full street types to abbreviated versions and handles address formatting.
    
    Args:
        address: Full address string
        
    Returns:
        Formatted address string ready for RentCast API
    """
    try:
        # Common street type mappings
        street_types = {
            'STREET': 'ST',
            'AVENUE': 'AVE',
            'BOULEVARD': 'BLVD',
            'DRIVE': 'DR',
            'LANE': 'LN',
            'PLACE': 'PL',
            'ROAD': 'RD',
            'COURT': 'CT',
            'CIRCLE': 'CIR',
            'HIGHWAY': 'HWY',
            'PARKWAY': 'PKWY',
            'WAY': 'WAY',  # Some don't get abbreviated
            'TRAIL': 'TRL',
            'TERRACE': 'TER',
            'SQUARE': 'SQ',
            # Add plural forms
            'STREETS': 'ST',
            'AVENUES': 'AVE',
            'BOULEVARDS': 'BLVD',
            'DRIVES': 'DR',
            'LANES': 'LN',
            'PLACES': 'PL',
            'ROADS': 'RD',
            'COURTS': 'CT',
            'CIRCLES': 'CIR',
            'HIGHWAYS': 'HWY',
            'PARKWAYS': 'PKWY',
            'WAYS': 'WAY',
            'TRAILS': 'TRL',
            'TERRACES': 'TER',
            'SQUARES': 'SQ'
        }
        
        # Split address into parts
        parts = [part.strip() for part in address.split(',')]
        
        # Handle the street part (first component)
        street_parts = parts[0].upper().split()
        
        # Look for street type and abbreviate if found
        for i, word in enumerate(street_parts):
            if word in street_types:
                street_parts[i] = street_types[word]
        
        # Reconstruct street with abbreviated type
        street = ' '.join(word.title() if i == 0 or word not in street_types.values() 
                         else word for i, word in enumerate(street_parts))
        
        # Get city, state, zip
        city = parts[1].strip() if len(parts) > 1 else ''
        state_zip = parts[2].strip() if len(parts) > 2 else ''
        
        # Extract state and zip if present
        state = state_zip.split()[0] if state_zip else ''
        zip_code = state_zip.split()[1] if state_zip and len(state_zip.split()) > 1 else ''
        
        # Build formatted address
        formatted = f"{street}, {city}, {state}"
        if zip_code:
            formatted += f" {zip_code}"
            
        # Remove any "United States" or similar
        formatted = formatted.split('United States')[0].strip().rstrip(',')
        
        # Clean up any double spaces or commas
        formatted = formatted.replace('  ', ' ').replace(', ,', ',')
        
        logger.debug(f"Formatted address from '{address}' to '{formatted}'")
        
        # Return the formatted address without URL encoding
        # Let the requests library handle the URL encoding
        return formatted
        
    except Exception as e:
        logger.error(f"Error formatting address: {str(e)}")
        # If anything goes wrong, return the original address without encoding
        return address

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
        
        # Access config values using dictionary syntax
        api_base_url = app_config['RENTCAST_API_BASE_URL']
        if not api_base_url:
            raise RentcastAPIError("RENTCAST_API_BASE_URL missing from configuration")
            
        api_key = app_config['RENTCAST_API_KEY']
        if not api_key:
            raise RentcastAPIError("RENTCAST_API_KEY missing from configuration")
            
        comp_defaults = app_config['RENTCAST_COMP_DEFAULTS']
        if not comp_defaults:
            raise RentcastAPIError("RENTCAST_COMP_DEFAULTS missing from configuration")

        # Access max runs config using dictionary syntax
        max_runs = app_config['MAX_COMP_RUNS_PER_SESSION']
        if max_runs is None:
            max_runs = 3  # Default value if not configured
            logger.warning("MAX_COMP_RUNS_PER_SESSION not found in config, using default: 3")
        
        # Check run count
        session_key = f'comps_run_count_{address}'
        run_count = session.get(session_key, 0)
        
        if run_count >= max_runs:
            raise RentcastAPIError(
                f"Maximum comp runs ({max_runs}) reached for this session"
            )
        
        # Log configuration (excluding API key)
        logger.debug(f"Using API base URL: {api_base_url}")
        logger.debug(f"API Key present: {'Yes' if api_key else 'No'}")
        logger.debug(f"Using comp defaults: {comp_defaults}")
        logger.debug(f"Max runs per session: {max_runs}")
        
        # Format address for URL
        formatted_address = format_address(address)
        
        # Construct API URL with parameters
        url = f"{api_base_url}/avm/value"
        params = {
            'address': formatted_address,
            'propertyType': property_type,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'squareFootage': square_footage,
            'maxRadius': comp_defaults.get('maxRadius', 1.0),
            'daysOld': comp_defaults.get('daysOld', 180),
            'compCount': comp_defaults.get('compCount', 5),
            'includeActiveSoldPending': 'false',  # Only include sold properties
            'includeSold': 'true'
        }
        
        # Set up headers with API key
        headers = {
            'accept': 'application/json',
            'X-Api-Key': api_key
        }
        
        # Make API request
        logger.debug("Making RentCast API request with parameters: %s", params)
        response = requests.get(url, params=params, headers=headers)
        
        # Check for successful response
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        logger.debug("Successfully received comps data")
        
        # Filter comparables to ensure we only have sold properties
        if 'comparables' in data and isinstance(data['comparables'], list):
            filtered_comps = []
            for comp in data['comparables']:
                # Include only if property has a removedDate (which indicates it was sold)
                # And must have a reasonable price
                if comp.get('removedDate') and comp.get('price', 0) > 0:
                    # Add the sale date for frontend display
                    comp['saleDate'] = comp.get('removedDate')
                    filtered_comps.append(comp)
            
            # Replace the comparables with filtered list
            data['comparables'] = filtered_comps
            logger.debug(f"Filtered {len(data.get('comparables', []))} sold properties")
        
        # Add timestamp for when comps were run
        data['last_run'] = datetime.utcnow().isoformat()
        
        # Increment and store run count
        run_count += 1
        session[session_key] = run_count
        logger.debug(f"Updated run count to {run_count}")
        
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