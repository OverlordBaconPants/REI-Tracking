"""
Property financial routes module for the REI-Tracker application.

This module provides routes for property financial tracking, equity tracking, cash flow calculations,
and comparison of actual performance to analysis projections.
"""

import logging
from flask import Blueprint, request, jsonify, g

from src.services.property_financial_service import PropertyFinancialService
from src.utils.auth_middleware import login_required, property_access_required

# Set up logger
logger = logging.getLogger(__name__)

# Create blueprint
property_financial_bp = Blueprint('property_financials', __name__, url_prefix='/api/property-financials')

# Create service
property_financial_service = PropertyFinancialService()


@property_financial_bp.route('/update/<property_id>', methods=['POST'])
@login_required
@property_access_required
def update_property_financials(property_id):
    """
    Update property financial data based on transactions.
    
    Args:
        property_id: ID of the property to update
        
    Returns:
        JSON response with updated property
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Update property financials
        updated_property = property_financial_service.update_property_financials(property_id)
        
        # Check if property was updated
        if not updated_property:
            return jsonify({
                'success': False,
                'error': 'Property not found or update failed'
            }), 404
        
        # Convert to dictionary
        property_dict = updated_property.to_dict()
        
        return jsonify({
            'success': True,
            'message': 'Property financials updated successfully',
            'property': property_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating property financials: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error updating property financials: {str(e)}"
        }), 500


@property_financial_bp.route('/summary/<property_id>', methods=['GET'])
@login_required
def get_property_financial_summary(property_id):
    """
    Get financial summary for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with financial summary
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get property financial summary
        summary = property_financial_service.get_property_financial_summary(property_id, user_id)
        
        return jsonify({
            'success': True,
            'summary': summary
        }), 200
        
    except ValueError as e:
        logger.error(f"Value error getting property financial summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting property financial summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting property financial summary: {str(e)}"
        }), 500


@property_financial_bp.route('/all', methods=['GET'])
@login_required
def get_all_property_financials():
    """
    Get financial summaries for all properties accessible to the user.
    
    Returns:
        JSON response with financial summaries
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get all property financials
        summaries = property_financial_service.get_all_property_financials(user_id)
        
        return jsonify({
            'success': True,
            'summaries': summaries
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all property financials: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting all property financials: {str(e)}"
        }), 500


@property_financial_bp.route('/update-all', methods=['POST'])
@login_required
def update_all_property_financials():
    """
    Update financial data for all properties.
    
    Returns:
        JSON response with number of properties updated
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Check if user is admin
        if not g.current_user.is_admin():
            return jsonify({
                'success': False,
                'error': 'Only administrators can update all property financials'
            }), 403
        
        # Update all property financials
        updated_count = property_financial_service.update_all_property_financials()
        
        return jsonify({
            'success': True,
            'message': f'Updated financials for {updated_count} properties',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating all property financials: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error updating all property financials: {str(e)}"
        }), 500


@property_financial_bp.route('/maintenance-capex/<property_id>', methods=['GET'])
@login_required
def get_maintenance_and_capex_records(property_id):
    """
    Get maintenance and capital expenditure records for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with maintenance and capex records
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get maintenance and capex records
        records = property_financial_service.get_maintenance_and_capex_records(property_id, user_id)
        
        return jsonify({
            'success': True,
            'records': records
        }), 200
        
    except ValueError as e:
        logger.error(f"Value error getting maintenance and capex records: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Error getting maintenance and capex records: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error getting maintenance and capex records: {str(e)}"
        }), 500


@property_financial_bp.route('/equity/<property_id>', methods=['GET'])
@login_required
def calculate_property_equity(property_id):
    """
    Calculate current equity for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with equity details
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Calculate property equity
        equity_details = property_financial_service.calculate_property_equity(property_id, user_id)
        
        return jsonify({
            'success': True,
            'equity_details': equity_details
        }), 200
        
    except ValueError as e:
        logger.error(f"Value error calculating property equity: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Error calculating property equity: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error calculating property equity: {str(e)}"
        }), 500


@property_financial_bp.route('/cash-flow/<property_id>', methods=['GET'])
@login_required
def calculate_cash_flow_metrics(property_id):
    """
    Calculate cash flow metrics for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with cash flow metrics
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Calculate cash flow metrics
        metrics = property_financial_service.calculate_cash_flow_metrics(
            property_id, 
            user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except ValueError as e:
        logger.error(f"Value error calculating cash flow metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Error calculating cash flow metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error calculating cash flow metrics: {str(e)}"
        }), 500


@property_financial_bp.route('/compare/<property_id>', methods=['GET'])
@login_required
def compare_actual_to_projected(property_id):
    """
    Compare actual property performance to analysis projections.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with comparison results
    """
    try:
        # Get user ID from session
        user_id = g.current_user.id
        
        # Get query parameters
        analysis_id = request.args.get('analysis_id')
        
        # Compare actual to projected
        comparison = property_financial_service.compare_actual_to_projected(
            property_id, 
            user_id,
            analysis_id=analysis_id
        )
        
        return jsonify({
            'success': True,
            'comparison': comparison
        }), 200
        
    except ValueError as e:
        logger.error(f"Value error comparing actual to projected: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
        
    except Exception as e:
        logger.error(f"Error comparing actual to projected: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error comparing actual to projected: {str(e)}"
        }), 500
