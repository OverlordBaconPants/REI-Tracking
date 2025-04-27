"""
Transaction routes module for the REI-Tracker application.

This module provides routes for transaction management.
"""

import logging
from typing import Dict, Any, List, Optional
from decimal import Decimal
from flask import Blueprint, request, jsonify, g

from src.models.transaction import Transaction
from src.repositories.transaction_repository import TransactionRepository
from src.services.transaction_service import TransactionService
from src.services.property_access_service import PropertyAccessService
from src.utils.auth_middleware import login_required, property_access_required

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# Create repositories and services
transaction_repo = TransactionRepository()
property_access_service = PropertyAccessService()
transaction_service = TransactionService()


@transaction_bp.route('/', methods=['GET'])
@login_required
def get_transactions():
    """
    Get transactions with optional filtering.
    
    Returns:
        JSON response with transactions
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get filter parameters from query string
        filters = _parse_transaction_filters(request.args)
        
        # Get transactions
        transactions = transaction_service.get_transactions(user_id, filters)
        
        # Convert to dictionaries
        transaction_dicts = [t.to_dict() for t in transactions]
        
        return jsonify({
            'success': True,
            'transactions': transaction_dicts
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting transactions: {str(e)}"
        }), 500


@transaction_bp.route('/by-property', methods=['GET'])
@login_required
def get_transactions_by_property():
    """
    Get transactions grouped by property with optional filtering.
    
    Returns:
        JSON response with transactions grouped by property
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get filter parameters from query string
        filters = _parse_transaction_filters(request.args)
        
        # Get transactions grouped by property
        grouped_transactions = transaction_service.get_transactions_by_property(user_id, filters)
        
        # Convert to dictionaries
        result = {}
        for property_id, transactions in grouped_transactions.items():
            result[property_id] = [t.to_dict() for t in transactions]
        
        return jsonify({
            'success': True,
            'grouped_transactions': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions by property: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting transactions by property: {str(e)}"
        }), 500

@transaction_bp.route('/property-summaries', methods=['GET'])
@login_required
def get_property_summaries():
    """
    Get financial summaries for each property based on filtered transactions.
    
    Returns:
        JSON response with property summaries
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get filter parameters from query string
        filters = _parse_transaction_filters(request.args)
        
        # Get property summaries
        summaries = transaction_service.get_property_summaries(user_id, filters)
        
        # Convert to dictionaries
        result = {}
        for property_id, summary in summaries.items():
            result[property_id] = {
                'property': summary['property'].to_dict(),
                'transaction_count': summary['transaction_count'],
                'income_total': str(summary['income_total']),
                'expense_total': str(summary['expense_total']),
                'net_amount': str(summary['net_amount'])
            }
        
        return jsonify({
            'success': True,
            'property_summaries': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting property summaries: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting property summaries: {str(e)}"
        }), 500

@transaction_bp.route('/with-property-info', methods=['GET'])
@login_required
def get_transactions_with_property_info():
    """
    Get transactions with their associated property information.
    
    Returns:
        JSON response with transactions and property info
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get filter parameters from query string
        filters = _parse_transaction_filters(request.args)
        
        # Get transactions with property info
        transaction_property_pairs = transaction_service.get_transactions_with_property_info(user_id, filters)
        
        # Convert to dictionaries
        result = []
        for transaction, property_obj in transaction_property_pairs:
            result.append({
                'transaction': transaction.to_dict(),
                'property': property_obj.to_dict()
            })
        
        return jsonify({
            'success': True,
            'transactions_with_property': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transactions with property info: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting transactions with property info: {str(e)}"
        }), 500

@transaction_bp.route('/<transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    """
    Get a specific transaction.
    
    Args:
        transaction_id: ID of the transaction
        
    Returns:
        JSON response with transaction
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get transaction
        transaction = transaction_service.get_transaction(transaction_id, user_id)
        
        # Check if transaction exists and user has access
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found or access denied'
            }), 404
        
        # Convert to dictionary
        transaction_dict = transaction.to_dict()
        
        return jsonify({
            'success': True,
            'transaction': transaction_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting transaction: {str(e)}"
        }), 500


@transaction_bp.route('/', methods=['POST'])
@login_required
def create_transaction():
    """
    Create a new transaction.
    
    Returns:
        JSON response with created transaction
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get transaction data from request
        transaction_data = request.json
        
        # Check if property ID is provided
        if 'property_id' not in transaction_data:
            return jsonify({
                'success': False,
                'error': 'Property ID is required'
            }), 400
        
        # Check if user has access to the property
        if not property_access_service.can_manage_property(user_id, transaction_data['property_id']):
            return jsonify({
                'success': False,
                'error': 'You do not have permission to create transactions for this property'
            }), 403
        
        # Create transaction
        transaction = transaction_service.create_transaction(transaction_data, user_id)
        
        # Check if transaction was created
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Failed to create transaction'
            }), 500
        
        # Convert to dictionary
        transaction_dict = transaction.to_dict()
        
        return jsonify({
            'success': True,
            'message': 'Transaction created successfully',
            'transaction': transaction_dict
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error creating transaction: {str(e)}"
        }), 500


@transaction_bp.route('/<transaction_id>', methods=['PUT'])
@login_required
def update_transaction(transaction_id):
    """
    Update a specific transaction.
    
    Args:
        transaction_id: ID of the transaction
        
    Returns:
        JSON response with updated transaction
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get transaction data from request
        update_data = request.json
        
        # Update transaction
        transaction = transaction_service.update_transaction(transaction_id, update_data, user_id)
        
        # Check if transaction exists and user has access
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found or access denied'
            }), 404
        
        # Convert to dictionary
        transaction_dict = transaction.to_dict()
        
        return jsonify({
            'success': True,
            'message': 'Transaction updated successfully',
            'transaction': transaction_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error updating transaction: {str(e)}"
        }), 500


@transaction_bp.route('/<transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """
    Delete a specific transaction.
    
    Args:
        transaction_id: ID of the transaction
        
    Returns:
        JSON response with success message
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Delete transaction
        success = transaction_service.delete_transaction(transaction_id, user_id)
        
        # Check if transaction exists and user has access
        if not success:
            return jsonify({
                'success': False,
                'error': 'Transaction not found or access denied'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Transaction deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error deleting transaction: {str(e)}"
        }), 500


def _parse_transaction_filters(args) -> Dict[str, Any]:
    """
    Parse transaction filter parameters from request arguments.
    
    Args:
        args: Request arguments
        
    Returns:
        Dictionary of filter parameters
    """
    filters = {}
    
    # Property filters
    if args.get('property_id'):
        filters['property_id'] = args.get('property_id')
    
    # Multiple property IDs (comma-separated)
    if args.get('property_ids'):
        property_ids = args.get('property_ids').split(',')
        filters['property_ids'] = [pid.strip() for pid in property_ids if pid.strip()]
    
    # Transaction type and category
    if args.get('type'):
        filters['type'] = args.get('type')
    if args.get('category'):
        filters['category'] = args.get('category')
    
    # Date range
    if args.get('start_date'):
        filters['start_date'] = args.get('start_date')
    if args.get('end_date'):
        filters['end_date'] = args.get('end_date')
    
    # Reimbursement status
    if args.get('reimbursement_status'):
        filters['reimbursement_status'] = args.get('reimbursement_status')
    
    # Description search
    if args.get('description'):
        filters['description'] = args.get('description')
    
    return filters

@transaction_bp.route('/reimbursement/<transaction_id>', methods=['PUT'])
@login_required
def update_reimbursement(transaction_id):
    """
    Update reimbursement status for a transaction.
    
    Args:
        transaction_id: ID of the transaction
        
    Returns:
        JSON response with updated transaction
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get reimbursement data from request
        reimbursement_data = request.json
        
        # Update reimbursement
        transaction = transaction_service.update_reimbursement(transaction_id, reimbursement_data, user_id)
        
        # Check if transaction exists and user has access
        if not transaction:
            return jsonify({
                'success': False,
                'error': 'Transaction not found or access denied'
            }), 404
        
        # Convert to dictionary
        transaction_dict = transaction.to_dict()
        
        return jsonify({
            'success': True,
            'message': 'Reimbursement updated successfully',
            'transaction': transaction_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating reimbursement: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error updating reimbursement: {str(e)}"
        }), 500

@transaction_bp.route('/reimbursement/calculate/<transaction_id>', methods=['GET'])
@login_required
def calculate_reimbursement_shares(transaction_id):
    """
    Calculate reimbursement shares for a transaction.
    
    Args:
        transaction_id: ID of the transaction
        
    Returns:
        JSON response with calculated reimbursement shares
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Calculate reimbursement shares
        shares = transaction_service.calculate_reimbursement_shares(transaction_id, user_id)
        
        # Convert Decimal values to strings for JSON serialization
        shares_dict = {partner: str(amount) for partner, amount in shares.items()}
        
        return jsonify({
            'success': True,
            'reimbursement_shares': shares_dict
        }), 200
        
    except ValueError as e:
        logger.error(f"Value error calculating reimbursement shares: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error calculating reimbursement shares: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error calculating reimbursement shares: {str(e)}"
        }), 500

@transaction_bp.route('/reimbursement/pending', methods=['GET'])
@login_required
def get_pending_reimbursements():
    """
    Get pending reimbursements for the current user.
    
    Returns:
        JSON response with pending reimbursements
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get pending reimbursements
        reimbursements = transaction_service.get_pending_reimbursements_for_user(user_id)
        
        # Convert to dictionaries
        result = []
        for transaction, property_obj in reimbursements:
            result.append({
                'transaction': transaction.to_dict(),
                'property': property_obj.to_dict()
            })
        
        return jsonify({
            'success': True,
            'pending_reimbursements': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting pending reimbursements: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting pending reimbursements: {str(e)}"
        }), 500

@transaction_bp.route('/reimbursement/owed', methods=['GET'])
@login_required
def get_reimbursements_owed():
    """
    Get reimbursements that the current user owes to others.
    
    Returns:
        JSON response with reimbursements owed
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get reimbursements owed
        reimbursements = transaction_service.get_reimbursements_owed_by_user(user_id)
        
        # Convert to dictionaries
        result = []
        for transaction, property_obj in reimbursements:
            result.append({
                'transaction': transaction.to_dict(),
                'property': property_obj.to_dict()
            })
        
        return jsonify({
            'success': True,
            'reimbursements_owed': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting reimbursements owed: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting reimbursements owed: {str(e)}"
        }), 500
