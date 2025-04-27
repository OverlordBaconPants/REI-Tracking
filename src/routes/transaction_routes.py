"""
Transaction routes module for the REI-Tracker application.

This module provides routes for transaction management.
"""

import logging
import tempfile
import os
from typing import Dict, Any, List, Optional
from decimal import Decimal
from flask import Blueprint, request, jsonify, g, send_file, render_template
import io

from src.models.transaction import Transaction
from src.repositories.transaction_repository import TransactionRepository
from src.services.transaction_service import TransactionService
from src.services.property_access_service import PropertyAccessService
from src.services.transaction_report_generator import TransactionReportGenerator
from src.utils.auth_middleware import login_required, property_access_required

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
transaction_bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

# Create repositories and services
transaction_repo = TransactionRepository()
property_access_service = PropertyAccessService()
transaction_service = TransactionService()
report_generator = TransactionReportGenerator()


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


@transaction_bp.route('/report', methods=['GET'])
@login_required
def generate_transaction_report():
    """
    Generate a PDF report of transactions with optional filtering.
    
    Returns:
        PDF file download
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get filter parameters from query string
        filters = _parse_transaction_filters(request.args)
        
        # Get transactions
        transactions = transaction_service.get_transactions(user_id, filters)
        
        # Convert to dictionaries for the report generator
        transaction_dicts = [t.to_dict() for t in transactions]
        
        # Create metadata for the report
        metadata = {
            "title": "Transaction Report",
            "generated_by": g.current_user.name,
            "date_range": "All Dates"
        }
        
        # Add date range if specified
        if 'start_date' in filters and 'end_date' in filters:
            metadata["date_range"] = f"{filters['start_date']} to {filters['end_date']}"
        elif 'start_date' in filters:
            metadata["date_range"] = f"From {filters['start_date']}"
        elif 'end_date' in filters:
            metadata["date_range"] = f"Until {filters['end_date']}"
        
        # Add property information if specified
        if 'property_id' in filters:
            metadata["property_name"] = filters['property_id']
            metadata["property"] = filters['property_id']
        else:
            metadata["property_name"] = "All Properties"
            metadata["property"] = "All Properties"
        
        # Create buffer for PDF
        buffer = io.BytesIO()
        
        # Generate report
        report_generator.generate(transaction_dicts, buffer, metadata)
        
        # Reset buffer position
        buffer.seek(0)
        
        # Create filename
        property_part = metadata["property_name"].replace(" ", "_").replace(",", "")
        date_part = metadata["date_range"].replace(" ", "_").replace(",", "")
        filename = f"Transaction_Report_{property_part}_{date_part}.pdf"
        
        # Return PDF file
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating transaction report: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error generating transaction report: {str(e)}"
        }), 500


@transaction_bp.route('/documentation-archive', methods=['GET'])
@login_required
def generate_documentation_archive():
    """
    Generate a ZIP archive of transaction documentation with optional filtering.
    
    Returns:
        ZIP file download
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get filter parameters from query string
        filters = _parse_transaction_filters(request.args)
        
        # Get transactions
        transactions = transaction_service.get_transactions(user_id, filters)
        
        # Convert to dictionaries for the report generator
        transaction_dicts = [t.to_dict() for t in transactions]
        
        # Create buffer for ZIP
        buffer = io.BytesIO()
        
        # Generate ZIP archive
        report_generator.generate_zip_archive(transaction_dicts, buffer)
        
        # Reset buffer position
        buffer.seek(0)
        
        # Create filename
        property_part = "All_Properties"
        if 'property_id' in filters:
            property_part = filters['property_id'].replace(" ", "_").replace(",", "")
        
        date_part = "All_Dates"
        if 'start_date' in filters and 'end_date' in filters:
            date_part = f"{filters['start_date']}_to_{filters['end_date']}".replace(" ", "_")
        elif 'start_date' in filters:
            date_part = f"From_{filters['start_date']}".replace(" ", "_")
        elif 'end_date' in filters:
            date_part = f"Until_{filters['end_date']}".replace(" ", "_")
        
        filename = f"Transaction_Documentation_{property_part}_{date_part}.zip"
        
        # Return ZIP file
        return send_file(
            buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating documentation archive: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error generating documentation archive: {str(e)}"
        }), 500


@transaction_bp.route('/bulk-import', methods=['GET'])
@login_required
def bulk_import_page():
    """
    Render the bulk import page.
    
    Returns:
        Rendered bulk import template
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        return render_template('transactions/bulk_import.html')
        
    except Exception as e:
        logger.error(f"Error rendering bulk import page: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error rendering bulk import page: {str(e)}"
        }), 500


@transaction_bp.route('/bulk-import/get-columns', methods=['POST'])
@login_required
def get_columns():
    """
    Get columns from an uploaded file.
    
    Returns:
        JSON response with columns
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part in request'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No selected file'
            }), 400
        
        # Check file extension
        if not _allowed_file(file.filename, ['csv', 'xls', 'xlsx']):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed types are: csv, xls, xlsx'
            }), 400
        
        # Save file to temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Import service
            from src.services.transaction_import_service import TransactionImportService
            import_service = TransactionImportService()
            
            # Read file
            df = import_service.read_file(temp_path, file.filename)
            
            # Get columns
            columns = df.columns.tolist()
            
            return jsonify({
                'success': True,
                'columns': columns
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Error getting columns: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting columns: {str(e)}"
        }), 500


@transaction_bp.route('/bulk-import', methods=['POST'])
@login_required
def bulk_import():
    """
    Process a bulk import file.
    
    Returns:
        JSON response with import results
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part in request'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No selected file'
            }), 400
        
        # Check file extension
        if not _allowed_file(file.filename, ['csv', 'xls', 'xlsx']):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed types are: csv, xls, xlsx'
            }), 400
        
        # Get column mapping
        try:
            column_mapping = request.form.get('column_mapping', '{}')
            column_mapping = json.loads(column_mapping)
        except Exception as e:
            logger.error(f"Error parsing column mapping: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid column mapping format'
            }), 400
        
        # Save file to temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Import service
            from src.services.transaction_import_service import TransactionImportService
            import_service = TransactionImportService()
            
            # Process import file
            results = import_service.process_import_file(temp_path, column_mapping, file.filename, user_id)
            
            return jsonify({
                'success': True,
                'results': results,
                'redirect': '/api/transactions'
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except Exception as e:
        logger.error(f"Error processing bulk import: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error processing bulk import: {str(e)}"
        }), 500


def _allowed_file(filename, allowed_extensions=None):
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions
        
    Returns:
        True if file has an allowed extension, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = ['csv', 'xls', 'xlsx']
        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
