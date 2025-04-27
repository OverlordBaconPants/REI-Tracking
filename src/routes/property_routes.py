"""
Property routes module for the REI-Tracker application.

This module provides routes for property management operations, including
adding, editing, and removing properties, as well as property listing with
filtering and sorting.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, List, Optional

from src.models.property import Property, Partner
from src.repositories.property_repository import PropertyRepository
from src.services.property_access_service import PropertyAccessService
from src.services.geoapify_service import GeoapifyService
from src.utils.auth_middleware import login_required, property_access_required, property_manager_required
from src.utils.logging_utils import get_logger

# Set up logger
logger = get_logger(__name__)

# Create Blueprint
property_bp = Blueprint('property', __name__, url_prefix='/api/properties')

# Initialize repositories and services
property_repository = PropertyRepository()
property_access_service = PropertyAccessService()
geoapify_service = GeoapifyService()


@property_bp.route('/', methods=['GET'])
@login_required
def get_properties():
    """
    Get properties for the current user.
    
    Returns:
        JSON response with properties
    """
    try:
        user_id = request.user_id
        
        # Get properties accessible to the user
        properties = property_access_service.get_accessible_properties(user_id)
        
        # Apply filters if provided
        filters = _parse_property_filters(request.args)
        if filters:
            properties = _filter_properties(properties, filters)
        
        # Apply sorting if provided
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        if sort_by:
            properties = _sort_properties(properties, sort_by, sort_order)
        
        # Convert to dict for response
        properties_dict = [prop.dict() for prop in properties]
        
        return jsonify({
            'success': True,
            'properties': properties_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting properties: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting properties: {str(e)}"
        }), 500


@property_bp.route('/<property_id>', methods=['GET'])
@property_access_required()
def get_property(property_id: str):
    """
    Get a specific property by ID.
    
    Args:
        property_id: ID of the property to get
        
    Returns:
        JSON response with property details
    """
    try:
        # Get property
        property_obj = property_repository.get_by_id(property_id)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Get property manager
        property_manager = property_access_service.get_property_manager(property_id)
        
        # Convert to dict for response
        property_dict = property_obj.dict()
        
        # Add property manager info
        property_dict['property_manager'] = property_manager.dict() if property_manager else None
        
        return jsonify({
            'success': True,
            'property': property_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting property: {str(e)}"
        }), 500


@property_bp.route('/', methods=['POST'])
@login_required
def create_property():
    """
    Create a new property.
    
    Returns:
        JSON response with created property
    """
    try:
        user_id = request.user_id
        
        # Get property data from request
        property_data = request.json
        if not property_data:
            return jsonify({
                'success': False,
                'message': 'No property data provided'
            }), 400
        
        # Validate address
        if not property_data.get('address'):
            return jsonify({
                'success': False,
                'message': 'Property address is required'
            }), 400
        
        # Check if address already exists
        if property_repository.address_exists(property_data['address']):
            return jsonify({
                'success': False,
                'message': 'A property with this address already exists'
            }), 400
        
        # Standardize address using Geoapify if available
        try:
            standardized_address = geoapify_service.standardize_address(property_data['address'])
            if standardized_address:
                property_data['address'] = standardized_address
        except Exception as e:
            logger.warning(f"Could not standardize address: {str(e)}")
            # Continue with the original address
        
        # Validate partners
        partners = property_data.get('partners', [])
        if not partners:
            return jsonify({
                'success': False,
                'message': 'At least one partner is required'
            }), 400
        
        # Ensure current user is included as a partner
        user_included = False
        for partner in partners:
            if partner.get('name') == request.user_name:
                user_included = True
                break
        
        if not user_included:
            return jsonify({
                'success': False,
                'message': 'Current user must be included as a partner'
            }), 400
        
        # Create property object
        try:
            property_obj = Property.from_dict(property_data)
        except Exception as e:
            logger.error(f"Error creating property object: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"Invalid property data: {str(e)}"
            }), 400
        
        # Save property
        created_property = property_repository.create(property_obj)
        
        # Sync property partners with user access
        property_access_service.sync_property_partners(created_property.id)
        
        return jsonify({
            'success': True,
            'message': 'Property created successfully',
            'property': created_property.dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating property: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error creating property: {str(e)}"
        }), 500


@property_bp.route('/<property_id>', methods=['PUT'])
@property_manager_required
def update_property(property_id: str):
    """
    Update an existing property.
    
    Args:
        property_id: ID of the property to update
        
    Returns:
        JSON response with updated property
    """
    try:
        # Get property data from request
        property_data = request.json
        if not property_data:
            return jsonify({
                'success': False,
                'message': 'No property data provided'
            }), 400
        
        # Get existing property
        existing_property = property_repository.get_by_id(property_id)
        if not existing_property:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Check if address is being changed and if it already exists
        if 'address' in property_data and property_data['address'] != existing_property.address:
            if property_repository.address_exists(property_data['address']):
                return jsonify({
                    'success': False,
                    'message': 'A property with this address already exists'
                }), 400
            
            # Standardize new address using Geoapify if available
            try:
                standardized_address = geoapify_service.standardize_address(property_data['address'])
                if standardized_address:
                    property_data['address'] = standardized_address
            except Exception as e:
                logger.warning(f"Could not standardize address: {str(e)}")
                # Continue with the original address
        
        # Update property object
        try:
            # Preserve ID and timestamps
            property_data['id'] = existing_property.id
            property_data['created_at'] = existing_property.created_at
            
            # Create updated property object
            updated_property = Property.from_dict(property_data)
        except Exception as e:
            logger.error(f"Error updating property object: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"Invalid property data: {str(e)}"
            }), 400
        
        # Save updated property
        property_repository.update(updated_property)
        
        # Sync property partners with user access
        property_access_service.sync_property_partners(property_id)
        
        return jsonify({
            'success': True,
            'message': 'Property updated successfully',
            'property': updated_property.dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error updating property: {str(e)}"
        }), 500


@property_bp.route('/<property_id>', methods=['DELETE'])
@property_manager_required
def delete_property(property_id: str):
    """
    Delete a property.
    
    Args:
        property_id: ID of the property to delete
        
    Returns:
        JSON response with result
    """
    try:
        # Check if property exists
        property_obj = property_repository.get_by_id(property_id)
        if not property_obj:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Delete property
        success = property_repository.delete(property_id)
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to delete property'
            }), 500
        
        # Get users with access to the property
        users_with_access = property_access_service.get_users_with_property_access(property_id)
        
        # Revoke access for all users
        for user in users_with_access:
            property_access_service.revoke_property_access(user.id, property_id)
        
        return jsonify({
            'success': True,
            'message': 'Property deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error deleting property: {str(e)}"
        }), 500


@property_bp.route('/<property_id>/partners', methods=['GET'])
@property_access_required()
def get_property_partners(property_id: str):
    """
    Get partners for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with partners
    """
    try:
        # Get property
        property_obj = property_repository.get_by_id(property_id)
        
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


@property_bp.route('/<property_id>/partners', methods=['PUT'])
@property_manager_required
def update_property_partners(property_id: str):
    """
    Update partners for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with updated partners
    """
    try:
        # Get partners data from request
        partners_data = request.json
        if not partners_data or not isinstance(partners_data, list):
            return jsonify({
                'success': False,
                'message': 'Invalid partners data'
            }), 400
        
        # Get property
        property_obj = property_repository.get_by_id(property_id)
        if not property_obj:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Update partners
        try:
            # Create Partner objects
            partners = []
            for partner_data in partners_data:
                partner = Partner(
                    name=partner_data.get('name'),
                    equity_share=partner_data.get('equity_share'),
                    is_property_manager=partner_data.get('is_property_manager', False)
                )
                partners.append(partner)
            
            # Update property partners
            property_obj.partners = partners
            
            # Validate property (this will check total equity = 100% and only one property manager)
            property_obj.dict()  # This triggers validation
            
        except Exception as e:
            logger.error(f"Error updating partners: {str(e)}")
            return jsonify({
                'success': False,
                'message': f"Invalid partners data: {str(e)}"
            }), 400
        
        # Save updated property
        property_repository.update(property_obj)
        
        # Sync property partners with user access
        property_access_service.sync_property_partners(property_id)
        
        return jsonify({
            'success': True,
            'message': 'Partners updated successfully',
            'partners': [partner.dict() for partner in property_obj.partners]
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating partners for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error updating partners: {str(e)}"
        }), 500


@property_bp.route('/<property_id>/manager', methods=['PUT'])
@property_access_required()
def set_property_manager(property_id: str):
    """
    Set the property manager for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with result
    """
    try:
        # Get user ID from request
        data = request.json
        if not data or 'user_id' not in data:
            return jsonify({
                'success': False,
                'message': 'User ID is required'
            }), 400
        
        user_id = data['user_id']
        
        # Designate property manager
        success = property_access_service.designate_property_manager(
            user_id=user_id,
            property_id=property_id,
            current_user_id=request.user_id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to set property manager'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Property manager set successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error setting property manager for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error setting property manager: {str(e)}"
        }), 500


@property_bp.route('/<property_id>/manager', methods=['DELETE'])
@property_access_required()
def remove_property_manager(property_id: str):
    """
    Remove the property manager for a property.
    
    Args:
        property_id: ID of the property
        
    Returns:
        JSON response with result
    """
    try:
        # Remove property manager
        success = property_access_service.remove_property_manager(
            property_id=property_id,
            current_user_id=request.user_id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to remove property manager'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Property manager removed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing property manager for property {property_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error removing property manager: {str(e)}"
        }), 500


@property_bp.route('/by-address', methods=['GET'])
@login_required
def get_property_by_address():
    """
    Get a property by address.
    
    Returns:
        JSON response with property
    """
    try:
        # Get address from query parameters
        address = request.args.get('address')
        if not address:
            return jsonify({
                'success': False,
                'message': 'Address is required'
            }), 400
        
        # Get property by address
        property_obj = property_repository.get_by_address(address)
        
        if not property_obj:
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404
        
        # Check if user has access to the property
        if not property_access_service.can_access_property(request.user_id, property_obj.id):
            return jsonify({
                'success': False,
                'message': 'You do not have access to this property'
            }), 403
        
        return jsonify({
            'success': True,
            'property': property_obj.dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting property by address: {str(e)}")
        return jsonify({
            'success': False,
            'message': f"Error getting property: {str(e)}"
        }), 500


def _parse_property_filters(args) -> Dict[str, Any]:
    """
    Parse property filters from request arguments.
    
    Args:
        args: Request arguments
        
    Returns:
        Dictionary of filters
    """
    filters = {}
    
    # Address filter (partial match)
    if args.get('address'):
        filters['address'] = args.get('address')
    
    # Partner filter
    if args.get('partner'):
        filters['partner'] = args.get('partner')
    
    # Property manager filter
    if args.get('manager'):
        filters['manager'] = args.get('manager')
    
    # Purchase date range
    if args.get('purchase_date_from'):
        filters['purchase_date_from'] = args.get('purchase_date_from')
    if args.get('purchase_date_to'):
        filters['purchase_date_to'] = args.get('purchase_date_to')
    
    # Price range
    if args.get('price_min'):
        filters['price_min'] = float(args.get('price_min'))
    if args.get('price_max'):
        filters['price_max'] = float(args.get('price_max'))
    
    return filters


def _filter_properties(properties: List[Property], filters: Dict[str, Any]) -> List[Property]:
    """
    Filter properties based on provided filters.
    
    Args:
        properties: List of properties to filter
        filters: Dictionary of filters
        
    Returns:
        Filtered list of properties
    """
    filtered_properties = properties
    
    # Address filter (partial match)
    if 'address' in filters:
        filtered_properties = [
            prop for prop in filtered_properties
            if filters['address'].lower() in prop.address.lower()
        ]
    
    # Partner filter
    if 'partner' in filters:
        filtered_properties = [
            prop for prop in filtered_properties
            if any(partner.name.lower() == filters['partner'].lower() for partner in prop.partners)
        ]
    
    # Property manager filter
    if 'manager' in filters:
        filtered_properties = [
            prop for prop in filtered_properties
            if prop.get_property_manager() and 
            prop.get_property_manager().name.lower() == filters['manager'].lower()
        ]
    
    # Purchase date range
    if 'purchase_date_from' in filters:
        filtered_properties = [
            prop for prop in filtered_properties
            if prop.purchase_date >= filters['purchase_date_from']
        ]
    if 'purchase_date_to' in filters:
        filtered_properties = [
            prop for prop in filtered_properties
            if prop.purchase_date <= filters['purchase_date_to']
        ]
    
    # Price range
    if 'price_min' in filters:
        filtered_properties = [
            prop for prop in filtered_properties
            if prop.purchase_price >= filters['price_min']
        ]
    if 'price_max' in filters:
        filtered_properties = [
            prop for prop in filtered_properties
            if prop.purchase_price <= filters['price_max']
        ]
    
    return filtered_properties


def _sort_properties(properties: List[Property], sort_by: str, sort_order: str = 'asc') -> List[Property]:
    """
    Sort properties based on provided criteria.
    
    Args:
        properties: List of properties to sort
        sort_by: Field to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        Sorted list of properties
    """
    reverse = sort_order.lower() == 'desc'
    
    if sort_by == 'address':
        return sorted(properties, key=lambda p: p.address, reverse=reverse)
    elif sort_by == 'purchase_date':
        return sorted(properties, key=lambda p: p.purchase_date, reverse=reverse)
    elif sort_by == 'purchase_price':
        return sorted(properties, key=lambda p: p.purchase_price, reverse=reverse)
    elif sort_by == 'cash_flow':
        return sorted(properties, key=lambda p: p.calculate_cash_flow(), reverse=reverse)
    elif sort_by == 'cap_rate':
        return sorted(properties, key=lambda p: p.calculate_cap_rate(), reverse=reverse)
    elif sort_by == 'cash_on_cash_return':
        return sorted(properties, key=lambda p: p.calculate_cash_on_cash_return(), reverse=reverse)
    
    # Default to sorting by address
    return sorted(properties, key=lambda p: p.address, reverse=reverse)
