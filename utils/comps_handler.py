import requests
from typing import Dict, Optional
from datetime import datetime
import logging
from flask import session, current_app
from utils.mao_calculator import calculate_mao

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
    square_footage: float,
    analysis_data: Optional[Dict] = None  # New parameter
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
        
        logger.debug(f"About to calculate MAO with analysis data: {bool(analysis_data)} and price: {'price' in data}")

        # Calculate MAO if analysis data is provided and we have an estimated value
        if analysis_data and 'price' in data:
            try:
                arv = data['price']
                mao_data = calculate_mao(arv, analysis_data)
                data['mao'] = mao_data
                logger.debug(f"Calculated MAO: ${mao_data['value']:.2f} for ARV: ${arv:.2f}")
            except Exception as e:
                logger.error(f"Error calculating MAO: {str(e)}")
                # Don't fail the entire operation if MAO calculation fails
        
        # After MAO calculation:
        if 'mao' in data:
            logger.debug(f"MAO calculation successful: {data['mao']['value']}")
        else:
            logger.debug("MAO calculation not included in response")

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

def fetch_rental_comps(
    app_config,
    address: str,
    bedrooms: float,
    bathrooms: float,
    square_footage: float,
    property_type: str = 'single_family'
) -> Optional[Dict]:
    """
    Fetch rental comps data from RentCast API
    
    Args:
        app_config: Application configuration
        address: Property address string
        bedrooms: Number of bedrooms
        bathrooms: Number of bathrooms
        square_footage: Property square footage
        property_type: Type of property (default: single_family)
        
    Returns:
        Dictionary with rental comps data
        
    Raises:
        RentcastAPIError: If the API call fails
    """
    try:
        logger.debug(f"Fetching rental comps for address: {address}")
        
        # Access config values
        api_base_url = app_config['RENTCAST_API_BASE_URL']
        if not api_base_url:
            raise RentcastAPIError("RENTCAST_API_BASE_URL missing from configuration")
            
        api_key = app_config['RENTCAST_API_KEY']
        if not api_key:
            raise RentcastAPIError("RENTCAST_API_KEY missing from configuration")
            
        comp_defaults = app_config['RENTCAST_COMP_DEFAULTS']
        if not comp_defaults:
            raise RentcastAPIError("RENTCAST_COMP_DEFAULTS missing from configuration")
        
        # Format address for URL
        formatted_address = format_address(address)
        
        # Construct API URL with parameters
        url = f"{api_base_url}/avm/rent/long-term"
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
        
        # Set up headers with API key
        headers = {
            'accept': 'application/json',
            'X-Api-Key': api_key
        }
        
        # Make API request
        logger.debug("Making RentCast Rental API request with parameters: %s", params)
        response = requests.get(url, params=params, headers=headers)
        
        # Check for successful response
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        logger.debug("Successfully received rental comps data")
        
        # Filter rental comps to ensure valid entries
        if 'comparables' in data and isinstance(data['comparables'], list):
            filtered_comps = []
            for comp in data['comparables']:
                # Ensure the rental has a valid price
                if comp.get('price', 0) > 0:
                    filtered_comps.append(comp)
            
            # Replace the comparables with filtered list
            data['comparables'] = filtered_comps
            logger.debug(f"Filtered {len(data.get('comparables', []))} rental properties")
        
        # Add timestamp for when comps were run
        data['last_run'] = datetime.utcnow().isoformat()
        
        # Reformat the data for consistency with our existing structure
        rental_comps = {
            'last_run': data['last_run'],
            'estimated_rent': data.get('rent', 0),
            'rent_range_low': data.get('rentRangeLow', 0),
            'rent_range_high': data.get('rentRangeHigh', 0),
            'comparable_rentals': data.get('comparables', []),
            'confidence_score': data.get('confidenceScore', 0)
        }
        
        return rental_comps
        
    except requests.exceptions.RequestException as e:
        logger.error(f"RentCast Rental API request failed: {str(e)}")
        raise RentcastAPIError(f"Failed to fetch rental comps: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing RentCast Rental API response: {str(e)}")
        raise RentcastAPIError(f"Error processing rental comps data: {str(e)}")

def calculate_mao_from_analysis(arv: float, analysis_data: Dict) -> Dict:
    """
    Calculate Maximum Allowable Offer using analysis data and ARV.
    Returns dictionary with MAO value and calculation parameters.
    """
    try:
        # Extract values from analysis data
        renovation_costs = float(analysis_data.get('renovation_costs', 0))
        renovation_duration = float(analysis_data.get('renovation_duration', 0))
        closing_costs = float(analysis_data.get('closing_costs', 0))
        
        # Get expected LTV (conservative default of 75% if not specified)
        expected_ltv = 75.0
        
        # Handle different analysis types
        if 'BRRRR' in analysis_data.get('analysis_type', ''):
            # Use refinance LTV for BRRRR
            refinance_ltv = float(analysis_data.get('refinance_loan_interest_rate', 75.0))
            expected_ltv = refinance_ltv
        elif analysis_data.get('has_balloon_payment'):
            # Use balloon refinance LTV if balloon payment is enabled
            balloon_ltv = float(analysis_data.get('balloon_refinance_ltv_percentage', 75.0))
            expected_ltv = balloon_ltv
        
        # Calculate monthly holding costs
        monthly_holding_costs = calculate_monthly_holding_costs(analysis_data)
        total_holding_costs = monthly_holding_costs * renovation_duration
        
        # Calculate loan amount based on LTV
        loan_amount = arv * (expected_ltv / 100)
        
        # Default max cash left in deal
        max_cash_left = 10000  # $10k default
        
        # Calculate MAO
        mao = loan_amount - renovation_costs - closing_costs - total_holding_costs + max_cash_left
        mao = max(0, mao)  # Ensure non-negative
        
        return {
            'value': mao,
            'arv': arv,
            'ltv_percentage': expected_ltv,
            'renovation_costs': renovation_costs,
            'closing_costs': closing_costs,
            'monthly_holding_costs': monthly_holding_costs,
            'total_holding_costs': total_holding_costs,
            'holding_months': renovation_duration,
            'max_cash_left': max_cash_left
        }
    except Exception as e:
        # Log error but don't crash
        logger.error(f"Error calculating MAO: {str(e)}")
        return {'value': 0, 'error': str(e)}

def calculate_monthly_holding_costs(analysis_data: Dict) -> float:
    """Calculate monthly holding costs during renovation phase."""
    # Get basic fixed costs
    property_taxes = float(analysis_data.get('property_taxes', 0))
    insurance = float(analysis_data.get('insurance', 0))
    utilities = float(analysis_data.get('utilities', 0))
    hoa_coa = float(analysis_data.get('hoa_coa_coop', 0))
    
    # Calculate loan interest payments for initial/hard money loan
    loan_amount = 0
    interest_rate = 0
    
    if 'BRRRR' in analysis_data.get('analysis_type', ''):
        loan_amount = float(analysis_data.get('initial_loan_amount', 0))
        interest_rate = float(analysis_data.get('initial_loan_interest_rate', 0))
    else:
        # Try to get the first loan data
        loan_amount = float(analysis_data.get('loan1_loan_amount', 0))
        interest_rate = float(analysis_data.get('loan1_loan_interest_rate', 0))
    
    # Calculate monthly interest
    monthly_interest = loan_amount * (interest_rate / 100 / 12) if loan_amount > 0 and interest_rate > 0 else 0
    
    # Sum all monthly holding costs
    return property_taxes + insurance + utilities + hoa_coa + monthly_interest

def update_analysis_comps(analysis: Dict, comps_data: Dict, rental_comps: Dict = None, run_count: int = 1) -> Dict:
    """
    Update analysis with new comps data
    
    Args:
        analysis: Current analysis dictionary
        comps_data: Comps data from RentCast API
        rental_comps: Rental comps data from RentCast API (optional)
        run_count: Current session run count
        
    Returns:
        Updated analysis dictionary
    """
    # Initialize comps_data if it doesn't exist
    if 'comps_data' not in analysis:
        analysis['comps_data'] = {}
    
    # Update property comps data
    analysis['comps_data'].update({
        'last_run': comps_data['last_run'],
        'run_count': run_count,
        'estimated_value': comps_data['price'],
        'value_range_low': comps_data['priceRangeLow'],
        'value_range_high': comps_data['priceRangeHigh'],
        'comparables': comps_data['comparables']
    })
    
    # Add MAO data if available
    if 'mao' in comps_data:
        analysis['comps_data']['mao'] = comps_data['mao']
    
    # Add rental comps data if available
    if rental_comps:
        # Calculate cap rate if we have both estimated value and rent
        if comps_data.get('price', 0) > 0 and rental_comps.get('estimated_rent', 0) > 0:
            annual_rent = rental_comps['estimated_rent'] * 12
            property_value = comps_data['price']
            cap_rate = (annual_rent / property_value) * 100
            rental_comps['cap_rate'] = round(cap_rate, 2)  # Store as percentage
        
        # Add rental comps to the analysis
        analysis['comps_data']['rental_comps'] = rental_comps
    
    return analysis