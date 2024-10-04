from flask import Blueprint, request, jsonify
from services.transaction_service import get_categories

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/categories')
def api_categories():
    try:
        transaction_type = request.args.get('type')
        categories = get_categories(transaction_type)
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500