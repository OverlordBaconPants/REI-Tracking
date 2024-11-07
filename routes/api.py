from flask import Blueprint, request, jsonify, current_app
from services.transaction_service import get_categories
import requests
import json
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import quote_plus
import re
import logging
from dataclasses import dataclass
from enum import Enum

api_bp = Blueprint('api', __name__)
   
class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

@dataclass
class GeoapifyResult:
    """Data class for validated Geoapify API results"""
    formatted: str
    lat: float
    lon: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeoapifyResult':
        """Create a validated GeoapifyResult from dictionary data"""
        if not isinstance(data, dict):
            raise ValidationError("Invalid result format")
            
        # Validate formatted address
        formatted = str(data.get('formatted', '')).strip()
        if not formatted:
            raise ValidationError("Missing formatted address")
            
        # Validate latitude
        try:
            lat = float(data.get('lat', 0))
            if not -90 <= lat <= 90:
                raise ValidationError("Invalid latitude value")
        except (TypeError, ValueError):
            raise ValidationError("Invalid latitude format")
            
        # Validate longitude
        try:
            lon = float(data.get('lon', 0))
            if not -180 <= lon <= 180:
                raise ValidationError("Invalid longitude value")
        except (TypeError, ValueError):
            raise ValidationError("Invalid longitude format")
            
        return cls(formatted=formatted, lat=lat, lon=lon)

class APIValidator:
    """Base validator class for API endpoints"""
    
    @staticmethod
    def validate_api_key(api_key: Optional[str]) -> str:
        """Validate API key existence and format"""
        if not api_key:
            raise ValidationError(
                "API key is not configured",
                status_code=500
            )
        
        if not isinstance(api_key, str) or len(api_key) < 10:
            raise ValidationError(
                "Invalid API key format",
                status_code=500
            )
            
        return api_key

    @staticmethod
    def validate_query_param(
        param: str,
        name: str,
        min_length: int = 1,
        max_length: int = 100,
        pattern: Optional[str] = None
    ) -> str:
        """Validate query parameter"""
        if not param:
            raise ValidationError(
                f"Missing required parameter: {name}",
                status_code=400
            )
            
        param = str(param).strip()
        
        if len(param) < min_length:
            raise ValidationError(
                f"{name} must be at least {min_length} characters long",
                status_code=400
            )
            
        if len(param) > max_length:
            raise ValidationError(
                f"{name} must be no more than {max_length} characters long",
                status_code=400
            )
            
        if pattern and not re.match(pattern, param):
            raise ValidationError(
                f"Invalid {name} format",
                status_code=400
            )
            
        return param

    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitize string input"""
        # Remove any control characters and normalize whitespace
        sanitized = ' '.join(re.sub(r'[\x00-\x1F\x7F]', '', value).split())
        return quote_plus(sanitized)

class CategoriesValidator(APIValidator):
    """Validator for categories endpoint"""
    
    @staticmethod
    def validate_categories_file(filepath: str) -> str:
        """Validate categories file path and existence"""
        if not filepath:
            raise ValidationError(
                "Categories file path not configured",
                status_code=500
            )
            
        if not isinstance(filepath, str):
            raise ValidationError(
                "Invalid categories file path",
                status_code=500
            )
            
        return filepath

    @staticmethod
    def validate_categories_data(data: Any) -> List[Dict[str, Any]]:
        """Validate categories data structure"""
        if not isinstance(data, (list, dict)):
            raise ValidationError(
                "Invalid categories data format",
                status_code=500
            )
            
        return data

class AutocompleteValidator(APIValidator):
    """Validator for autocomplete endpoint"""
    
    @staticmethod
    def validate_geoapify_response(response: requests.Response) -> Dict[str, Any]:
        """Validate Geoapify API response"""
        try:
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValidationError(
                f"Geoapify API error: {str(e)}",
                status_code=response.status_code
            )
            
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise ValidationError(
                f"Invalid JSON response: {str(e)}",
                status_code=500
            )
            
        if not isinstance(data, dict):
            raise ValidationError(
                "Invalid response format",
                status_code=500
            )
            
        return data

def error_response(error: Exception) -> Tuple[Dict[str, Any], int]:
    """Generate standardized error response"""
    if isinstance(error, ValidationError):
        status_code = error.status_code
    else:
        status_code = 500
        
    return {
        "error": str(error),
        "status": "error",
        "code": status_code
    }, status_code

@api_bp.route('/categories')
def get_categories():
    """Get categories with validation"""
    try:
        # Get transaction type from query parameters
        transaction_type = request.args.get('type')
        
        # Validate categories file configuration
        categories_validator = CategoriesValidator()
        filepath = categories_validator.validate_categories_file(
            current_app.config.get('CATEGORIES_FILE')
        )
        
        # Read and validate categories data
        try:
            with open(filepath, 'r') as f:
                categories_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise ValidationError(f"Failed to load categories: {str(e)}", 500)
            
        categories = categories_validator.validate_categories_data(categories_data)
        
        # If transaction type is specified, return only those categories
        if transaction_type and transaction_type in categories:
            return jsonify(categories[transaction_type])
        
        return jsonify(categories)
        
    except Exception as e:
        current_app.logger.error(f"Error in get_categories: {str(e)}")
        return jsonify(error_response(e))

@api_bp.route('/autocomplete')
def autocomplete():
    """Autocomplete endpoint with validation"""
    try:
        # Initialize validator
        validator = AutocompleteValidator()
        
        # Validate and sanitize query parameter
        query = validator.validate_query_param(
            request.args.get('query', ''),
            'query',
            min_length=2,
            max_length=100
            # Removed the pattern restriction to allow more characters
        )
        sanitized_query = validator.sanitize_string(query)
        
        # Validate API key
        api_key = validator.validate_api_key(
            current_app.config.get('GEOAPIFY_API_KEY')
        )
        
        # Construct and validate URL
        url = f'https://api.geoapify.com/v1/geocode/autocomplete'
        params = {
            'text': sanitized_query,
            'format': 'json',
            'apiKey': api_key
        }
        
        # Make API request
        try:
            response = requests.get(url, params=params, timeout=10)
        except requests.RequestException as e:
            raise ValidationError(f"Failed to connect to Geoapify: {str(e)}", 503)
            
        # Validate response
        data = validator.validate_geoapify_response(response)
        
        # Process and validate results
        results = []
        for result in data.get('results', []):
            try:
                validated_result = GeoapifyResult.from_dict(result)
                results.append({
                    'formatted': validated_result.formatted,
                    'lat': validated_result.lat,
                    'lon': validated_result.lon
                })
            except ValidationError as e:
                current_app.logger.warning(f"Skipping invalid result: {str(e)}")
                continue
                
        return jsonify({
            "status": "success",
            "data": results
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in autocomplete: {str(e)}")
        return jsonify(error_response(e))

@api_bp.route('/test')
def test():
    """Simple test endpoint"""
    try:
        return jsonify({
            "status": "success",
            "message": "API is working",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error in test endpoint: {str(e)}")
        return jsonify(error_response(e))