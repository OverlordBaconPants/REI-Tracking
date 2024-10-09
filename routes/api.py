from flask import Blueprint, request, jsonify, current_app
from services.transaction_service import get_categories
import requests
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/categories')
def get_categories():
    try:
        with open(current_app.config['CATEGORIES_FILE'], 'r') as f:
            categories = json.load(f)
        return jsonify(categories)
    except Exception as e:
        current_app.logger.error(f"Error loading categories: {str(e)}")
        return jsonify({"error": "Failed to load categories"}), 500
    
@api_bp.route('/autocomplete')
def autocomplete():
    query = request.args.get('query', '')
    api_key = current_app.config.get('GEOAPIFY_API_KEY')
    
    if not api_key:
        current_app.logger.error("GEOAPIFY_API_KEY is not found in the configuration")
        return jsonify({"error": "API key is not configured"}), 500

    url = f'https://api.geoapify.com/v1/geocode/autocomplete?text={query}&format=json&apiKey={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError for bad responses
        data = response.json()
        
        suggestions = [
            {
                'formatted': result['formatted'],
                'lat': result['lat'],
                'lon': result['lon']
            }
            for result in data.get('results', [])
        ]
        return jsonify(suggestions)
    except requests.RequestException as e:
        current_app.logger.error(f"Error calling Geoapify API: {str(e)}")
        return jsonify({"error": "Error fetching autocomplete results"}), 500
    except json.JSONDecodeError as e:
        current_app.logger.error(f"Error decoding JSON from Geoapify API: {str(e)}")
        return jsonify({"error": "Error processing autocomplete results"}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in autocomplete: {str(e)}")
        return jsonify({"error": "Unexpected error occurred"}), 500

@api_bp.route('/test')
def test():
    return jsonify({"message": "API is working"})