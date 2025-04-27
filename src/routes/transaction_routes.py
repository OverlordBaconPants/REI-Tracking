"""
Transaction routes module for the REI-Tracker application.

This module provides routes for transaction management.
"""

import logging
from typing import Dict, Any
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
        filters = {}
        if request.args.get('property_id'):
            filters['property_id'] = request.args.get('property_id')
        if request.args.get('type'):
            filters['type'] = request.args.get('type')
        if request.args.get('category'):
            filters['category'] = request.args.get('category')
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        if request.args.get('reimbursement_status'):
            filters['reimbursement_status'] = request.args.get('reimbursement_status')
        
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
