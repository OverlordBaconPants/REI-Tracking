"""
Partner equity routes module for the REI-Tracker application.

This module provides routes for partner equity management operations, including
adding, editing, and removing partners, as well as tracking contributions and
distributions.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, List, Optional
from decimal import Decimal

from src.models.property import Partner
from src.models.partner_contribution import PartnerContribution
from src.services.partner_equity_service import PartnerEquityService
from src.services.property_access_service import PropertyAccessService
from src.utils.auth_middleware import login_required, property_access_required, property_manager_required
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Create Blueprint
partner_equity_bp = Blueprint('partner_equity', __name__, url_prefix='/api/partner-equity')

# Initialize services
partner_equity_service = PartnerEquityService()
property_access_service = PropertyAccessService()


@partner_equity_bp.route('/partners/<property_id>', methods=['GET'])
@property_access_required()
def get_partners(property_id: str):
    """
    Get partners for a property.
    
    Args:
        property_id: ID of the property to get partners for
        
    Returns:
        JSON response with partners
    """
    try:
        # Get property
        property_obj = property_access_service.property_repository.get_by_id(property_id)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Convert partners to dict for response
        partners = [partner.dict() for partner in property_obj.partners]
        
        return jsonify({
            'success': True,
            'partners': partners
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting partners for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting partners: {str(e)}"
        }), 500


@partner_equity_bp.route('/partners/<property_id>', methods=['POST'])
@property_manager_required
def add_partner(property_id: str):
    """
    Add a partner to a property.
    
    Args:
        property_id: ID of the property to add the partner to
        
    Returns:
        JSON response with result
    """
    try:
        # Get partner data from request
        partner_data = request.json
        if not partner_data:
            return jsonify({
                'success': False,
                'message': 'No partner data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['name', 'equity_share']
        for field in required_fields:
            if field not in partner_data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Add partner
        success = partner_equity_service.add_partner(
            property_id=property_id,
            partner_name=partner_data['name'],
            equity_share=Decimal(str(partner_data['equity_share'])),
            is_property_manager=partner_data.get('is_property_manager', False),
            visibility_settings=partner_data.get('visibility_settings'),
            current_user_id=request.user_id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to add partner'
            }), 500
        
        # Sync property partners with user access
        property_access_service.sync_property_partners(property_id)
        
        return jsonify({
            'success': True,
            'message': 'Partner added successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding partner to property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error adding partner: {str(e)}"
        }), 500


@partner_equity_bp.route('/partners/<property_id>/<partner_name>', methods=['PUT'])
@property_manager_required
def update_partner(property_id: str, partner_name: str):
    """
    Update a partner for a property.
    
    Args:
        property_id: ID of the property to update the partner for
        partner_name: Name of the partner to update
        
    Returns:
        JSON response with result
    """
    try:
        # Get partner data from request
        partner_data = request.json
        if not partner_data:
            return jsonify({
                'success': False,
                'message': 'No partner data provided'
            }), 400
        
        # Update equity share if provided
        if 'equity_share' in partner_data:
            success = partner_equity_service.update_partner_equity(
                property_id=property_id,
                partner_name=partner_name,
                equity_share=Decimal(str(partner_data['equity_share'])),
                current_user_id=request.user_id
            )
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update partner equity share'
                }), 500
        
        # Update visibility settings if provided
        if 'visibility_settings' in partner_data:
            success = partner_equity_service.update_partner_visibility_settings(
                property_id=property_id,
                partner_name=partner_name,
                visibility_settings=partner_data['visibility_settings'],
                current_user_id=request.user_id
            )
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': 'Failed to update partner visibility settings'
                }), 500
        
        # Sync property partners with user access
        property_access_service.sync_property_partners(property_id)
        
        return jsonify({
            'success': True,
            'message': 'Partner updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating partner {partner_name} for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error updating partner: {str(e)}"
        }), 500


@partner_equity_bp.route('/partners/<property_id>/<partner_name>', methods=['DELETE'])
@property_manager_required
def remove_partner(property_id: str, partner_name: str):
    """
    Remove a partner from a property.
    
    Args:
        property_id: ID of the property to remove the partner from
        partner_name: Name of the partner to remove
        
    Returns:
        JSON response with result
    """
    try:
        # Remove partner
        success = partner_equity_service.remove_partner(
            property_id=property_id,
            partner_name=partner_name,
            current_user_id=request.user_id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to remove partner'
            }), 500
        
        # Sync property partners with user access
        property_access_service.sync_property_partners(property_id)
        
        return jsonify({
            'success': True,
            'message': 'Partner removed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing partner {partner_name} from property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error removing partner: {str(e)}"
        }), 500


@partner_equity_bp.route('/contributions/<property_id>', methods=['GET'])
@property_access_required()
def get_contributions(property_id: str):
    """
    Get contributions for a property.
    
    Args:
        property_id: ID of the property to get contributions for
        
    Returns:
        JSON response with contributions
    """
    try:
        # Get partner name from query parameters (optional)
        partner_name = request.args.get('partner_name')
        
        # Get contributions
        if partner_name:
            contributions = partner_equity_service.get_contributions_by_property_and_partner(
                property_id, partner_name
            )
        else:
            contributions = partner_equity_service.get_contributions_by_property(property_id)
        
        # Convert contributions to dict for response
        contributions_dict = [contribution.dict() for contribution in contributions]
        
        return jsonify({
            'success': True,
            'contributions': contributions_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting contributions for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting contributions: {str(e)}"
        }), 500


@partner_equity_bp.route('/contributions/<property_id>', methods=['POST'])
@property_manager_required
def add_contribution(property_id: str):
    """
    Add a contribution or distribution for a partner.
    
    Args:
        property_id: ID of the property to add the contribution for
        
    Returns:
        JSON response with result
    """
    try:
        # Get contribution data from request
        contribution_data = request.json
        if not contribution_data:
            return jsonify({
                'success': False,
                'message': 'No contribution data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['partner_name', 'amount', 'contribution_type', 'date']
        for field in required_fields:
            if field not in contribution_data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Add contribution
        contribution_id = partner_equity_service.add_contribution(
            property_id=property_id,
            partner_name=contribution_data['partner_name'],
            amount=Decimal(str(contribution_data['amount'])),
            contribution_type=contribution_data['contribution_type'],
            date=contribution_data['date'],
            notes=contribution_data.get('notes'),
            current_user_id=request.user_id
        )
        
        if not contribution_id:
            return jsonify({
                'success': False,
                'message': 'Failed to add contribution'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Contribution added successfully',
            'contribution_id': contribution_id
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding contribution to property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error adding contribution: {str(e)}"
        }), 500


@partner_equity_bp.route('/contributions/totals/<property_id>', methods=['GET'])
@property_access_required()
def get_contribution_totals(property_id: str):
    """
    Get total contributions for a property.
    
    Args:
        property_id: ID of the property to get contribution totals for
        
    Returns:
        JSON response with contribution totals
    """
    try:
        # Get total contributions
        totals = partner_equity_service.get_total_contributions_by_property(property_id)
        
        return jsonify({
            'success': True,
            'totals': totals
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting contribution totals for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting contribution totals: {str(e)}"
        }), 500


@partner_equity_bp.route('/visibility/<property_id>/<partner_name>', methods=['GET'])
@property_access_required()
def get_partner_visibility(property_id: str, partner_name: str):
    """
    Get visibility settings for a partner.
    
    Args:
        property_id: ID of the property to get visibility settings for
        partner_name: Name of the partner to get visibility settings for
        
    Returns:
        JSON response with visibility settings
    """
    try:
        # Get property
        property_obj = property_access_service.property_repository.get_by_id(property_id)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Find partner
        partner = next(
            (p for p in property_obj.partners if p.name == partner_name),
            None
        )
        
        if not partner:
            return jsonify({
                'success': False,
                'message': 'Partner not found'
            }), 404
        
        return jsonify({
            'success': True,
            'visibility_settings': partner.visibility_settings
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting visibility settings for partner {partner_name} on property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting visibility settings: {str(e)}"
        }), 500


@partner_equity_bp.route('/visibility/<property_id>/<partner_name>', methods=['PUT'])
@property_manager_required
def update_partner_visibility(property_id: str, partner_name: str):
    """
    Update visibility settings for a partner.
    
    Args:
        property_id: ID of the property to update visibility settings for
        partner_name: Name of the partner to update visibility settings for
        
    Returns:
        JSON response with result
    """
    try:
        # Get visibility settings from request
        visibility_data = request.json
        if not visibility_data:
            return jsonify({
                'success': False,
                'message': 'No visibility settings provided'
            }), 400
        
        # Update visibility settings
        success = partner_equity_service.update_partner_visibility_settings(
            property_id=property_id,
            partner_name=partner_name,
            visibility_settings=visibility_data,
            current_user_id=request.user_id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to update visibility settings'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Visibility settings updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating visibility settings for partner {partner_name} on property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error updating visibility settings: {str(e)}"
        }), 500
