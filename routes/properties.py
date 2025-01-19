import os
import json
import logging
import traceback
from flask import Blueprint, render_template, request, current_app, jsonify
from flask_login import login_required, current_user
from utils.utils import admin_required
from services.transaction_service import get_partners_for_property, get_properties_for_user
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from decimal import Decimal

# Configure logger
logger = logging.getLogger(__name__)

# Create a Blueprint for properties routes
properties_bp = Blueprint('properties', __name__, url_prefix='/properties')

class PropertyValidationError(Exception):
    """Custom exception for property validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_property_data(property_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate property data before saving or updating
    
    Args:
        property_data: Dictionary containing property information
        
    Returns:
        Tuple of (is_valid: bool, error_messages: List[str])
    """
    errors = []
    
    # Required fields with their types
    required_fields = {
        'address': str,
        'purchase_price': (int, float),
        'down_payment': (int, float),
        'primary_loan_rate': (int, float),
        'primary_loan_term': (int, float),
        'purchase_date': str,
        'loan_amount': (int, float),
        'loan_start_date': str,
        'partners': list
    }
    
    # Check required fields
    for field, expected_type in required_fields.items():
        if field not in property_data:
            errors.append(f"Missing required field: {field}")
            continue
            
        if property_data[field] is None:
            errors.append(f"Field cannot be null: {field}")
            continue
            
        if not isinstance(property_data[field], expected_type):
            errors.append(f"Invalid type for {field}: expected {expected_type}, got {type(property_data[field])}")

    # Validate numeric fields are positive
    numeric_fields = ['purchase_price', 'down_payment', 'primary_loan_rate', 
                     'primary_loan_term', 'loan_amount']
    for field in numeric_fields:
        if field in property_data and property_data[field] is not None:
            try:
                value = float(property_data[field])
                if value < 0:
                    errors.append(f"{field} cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid numeric value for {field}")

    # Validate dates
    date_fields = ['purchase_date', 'loan_start_date']
    for field in date_fields:
        if field in property_data and property_data[field]:
            try:
                datetime.strptime(property_data[field], '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format for {field}. Expected YYYY-MM-DD")

    # Validate address
    if 'address' in property_data and property_data['address']:
        if not property_data['address'].strip():
            errors.append("Address cannot be empty")

    # Validate partners
    if 'partners' in property_data and property_data['partners']:
        partners_errors = validate_partners_data(property_data['partners'])
        errors.extend(partners_errors)
    
    return len(errors) == 0, errors

def validate_partners_data(partners_data: List[Dict[str, Any]]) -> List[str]:
    """
    Validate partners data structure and equity shares
    """
    errors = []
    
    if not partners_data:
        errors.append("At least one partner is required")
        return errors
        
    total_equity = Decimal('0')
    property_manager_count = 0
    
    for partner in partners_data:
        # Validate partner structure
        if not isinstance(partner, dict):
            errors.append("Invalid partner data format")
            continue
            
        # Check required fields
        if 'name' not in partner or not partner['name'].strip():
            errors.append("Partner name is required and cannot be empty")
            
        if 'equity_share' not in partner:
            errors.append(f"Equity share is required for partner {partner.get('name', 'Unknown')}")
            continue
            
        # Validate equity share
        try:
            equity_share = Decimal(str(partner['equity_share']))
            if equity_share <= 0:
                errors.append(f"Equity share must be positive for partner {partner['name']}")
            total_equity += equity_share
        except (ValueError, TypeError, decimal.InvalidOperation):
            errors.append(f"Invalid equity share value for partner {partner.get('name', 'Unknown')}")

        # Validate Property Manager designation
        if partner.get('is_property_manager', False):
            property_manager_count += 1

    # Validate total equity
    if total_equity != Decimal('100'):
        errors.append(f"Total equity must equal 100%, current total: {float(total_equity)}%")

    # Validate Property Manager count
    if property_manager_count == 0:
        errors.append("One partner must be designated as Property Manager")
    elif property_manager_count > 1:
        errors.append("Only one partner can be designated as Property Manager")
        
    return errors

def sanitize_property_data(property_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and normalize property data
    
    Args:
        property_data: Raw property data dictionary
        
    Returns:
        Sanitized property data with all required fields and proper types
    """
    try:
        sanitized = {
            'address': str(property_data['address']).strip(),
            'purchase_price': float(property_data['purchase_price']),
            'down_payment': float(property_data['down_payment']),
            'primary_loan_rate': float(property_data['primary_loan_rate']),
            'primary_loan_term': float(property_data['primary_loan_term']),
            'purchase_date': str(property_data['purchase_date']),
            'loan_amount': float(property_data['loan_amount']),
            'loan_start_date': str(property_data['loan_start_date']),
            'seller_financing_amount': float(property_data.get('seller_financing_amount', 0)),
            'seller_financing_rate': float(property_data.get('seller_financing_rate', 0)),
            'seller_financing_term': float(property_data.get('seller_financing_term', 0)),
            'closing_costs': float(property_data.get('closing_costs', 0)),
            'renovation_costs': float(property_data.get('renovation_costs', 0)),
            'marketing_costs': float(property_data.get('marketing_costs', 0)),
            'holding_costs': float(property_data.get('holding_costs', 0)),
            'monthly_income': {
                'rental_income': float(property_data.get('monthly_income', {}).get('rental_income', 0)),
                'parking_income': float(property_data.get('monthly_income', {}).get('parking_income', 0)),
                'laundry_income': float(property_data.get('monthly_income', {}).get('laundry_income', 0)),
                'other_income': float(property_data.get('monthly_income', {}).get('other_income', 0)),
                'income_notes': str(property_data.get('monthly_income', {}).get('income_notes', '')).strip()
            },
            'monthly_expenses': {
                'property_tax': float(property_data.get('monthly_expenses', {}).get('property_tax', 0)),
                'insurance': float(property_data.get('monthly_expenses', {}).get('insurance', 0)),
                'repairs': float(property_data.get('monthly_expenses', {}).get('repairs', 0)),
                'capex': float(property_data.get('monthly_expenses', {}).get('capex', 0)),
                'property_management': float(property_data.get('monthly_expenses', {}).get('property_management', 0)),
                'hoa_fees': float(property_data.get('monthly_expenses', {}).get('hoa_fees', 0)),
                'utilities': {
                    'water': float(property_data.get('monthly_expenses', {}).get('utilities', {}).get('water', 0)),
                    'electricity': float(property_data.get('monthly_expenses', {}).get('utilities', {}).get('electricity', 0)),
                    'gas': float(property_data.get('monthly_expenses', {}).get('utilities', {}).get('gas', 0)),
                    'trash': float(property_data.get('monthly_expenses', {}).get('utilities', {}).get('trash', 0))
                },
                'other_expenses': float(property_data.get('monthly_expenses', {}).get('other_expenses', 0)),
                'expense_notes': str(property_data.get('monthly_expenses', {}).get('expense_notes', '')).strip()
            },
            'partners': []
        }
        
        # Process partners data
        for partner in property_data['partners']:
            sanitized_partner = {
                'name': str(partner['name']).strip(),
                'equity_share': float(partner['equity_share']),
                'is_property_manager': bool(partner.get('is_property_manager', False))
            }
            sanitized['partners'].append(sanitized_partner)
        
        # Round all numeric values to 2 decimal places
        def round_nested_dict(d: Dict) -> Dict:
            for k, v in d.items():
                if isinstance(v, dict):
                    d[k] = round_nested_dict(v)
                elif isinstance(v, (int, float)) and k != 'primary_loan_term':
                    d[k] = round(float(v), 2)
            return d
            
        return round_nested_dict(sanitized)
        
    except Exception as e:
        logger.error(f"Error sanitizing property data: {str(e)}")
        raise ValueError(f"Error sanitizing property data: {str(e)}")

@properties_bp.route('/get_manageable_properties')
@login_required
def get_manageable_properties():
    """Get properties where the current user is a property manager."""
    try:
        properties = get_properties_for_user(current_user.id, current_user.name)
        
        return jsonify({
            'success': True,
            'properties': properties
        })
        
    except Exception as e:
        logging.error(f"Error getting manageable properties: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': 'Error loading properties'
        }), 500

def is_property_manager(user_email, property_data):
    """Check if user is a property manager for given property."""
    try:
        logging.debug(f"Checking property manager status for user {user_email}")
        logging.debug(f"Property data: {property_data}")
        
        from flask_login import current_user  # Add this import if not already present
        
        is_manager = any(
            partner.get('name') == current_user.name and 
            partner.get('is_property_manager', False)
            for partner in property_data.get('partners', [])
        )
        
        logging.debug(f"Is property manager result: {is_manager}")
        return is_manager

    except Exception as e:
        logging.error(f"Error checking property manager status: {str(e)}")
        return False
    
@properties_bp.route('/add_properties', methods=['GET', 'POST'])
@login_required
def add_properties():
    """Handle adding new properties"""
    logger.info(f"Add properties route accessed by user: {current_user.email}")
    
    try:
        # Load existing properties
        properties = []
        try:
            with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
                properties = json.load(f)
                logger.debug(f"Successfully loaded {len(properties)} existing properties")
        except FileNotFoundError:
            logger.warning(f"Properties file not found, will create new file")
            # Create an empty properties file
            os.makedirs(os.path.dirname(current_app.config['PROPERTIES_FILE']), exist_ok=True)
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump([], f)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in properties file: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Invalid properties database format',
                'errors': [str(e)]
            }), 500
            
        if request.method == 'POST':
            logger.debug("Processing POST request for add_properties")
            try:
                # Get and validate incoming data
                new_property = request.get_json()
                if not new_property:
                    logger.warning("No property data received in POST request")
                    return jsonify({
                        'success': False,
                        'message': 'No property data received',
                        'errors': ['No property data received']
                    }), 400

                logger.debug(f"Received new property data: {json.dumps(new_property, indent=2)}")

                # Check for duplicate address
                if any(p['address'] == new_property['address'] for p in properties):
                    logger.warning(f"Attempt to add duplicate property address: {new_property['address']}")
                    return jsonify({
                        'success': False,
                        'message': 'A property with this address already exists',
                        'errors': ['A property with this address already exists']
                    }), 400

                # Validate property data
                is_valid, validation_errors = validate_property_data(new_property)
                if not is_valid:
                    logger.warning(f"Property validation failed: {validation_errors}")
                    return jsonify({
                        'success': False,
                        'message': 'Validation failed',
                        'errors': validation_errors
                    }), 400

                # Sanitize and normalize the data
                try:
                    complete_property = sanitize_property_data(new_property)
                    logger.debug("Property data sanitized successfully")
                except ValueError as ve:
                    logger.error(f"Error sanitizing property data: {str(ve)}")
                    return jsonify({
                        'success': False,
                        'message': f'Error processing property data',
                        'errors': [str(ve)]
                    }), 400

                # Add the new property
                properties.append(complete_property)
                
                # Save updated properties with atomic write
                temp_file = current_app.config['PROPERTIES_FILE'] + '.tmp'
                try:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(temp_file), exist_ok=True)
                    
                    with open(temp_file, 'w') as f:
                        json.dump(properties, f, indent=2)
                    os.replace(temp_file, current_app.config['PROPERTIES_FILE'])
                    logger.info(f"New property successfully added: {complete_property['address']}")
                except Exception as e:
                    logger.error(f"Error saving properties file: {str(e)}")
                    if os.path.exists(temp_file):
                        try:
                            os.remove(temp_file)
                        except Exception as e2:
                            logger.error(f"Error removing temporary file: {str(e2)}")
                    return jsonify({
                        'success': False,
                        'message': 'Error saving property data',
                        'errors': [str(e)]
                    }), 500

                return jsonify({
                    'success': True,
                    'message': 'Property added successfully'
                })

            except Exception as e:
                logger.error(f"Unexpected error in add_properties POST handler: {str(e)}", exc_info=True)
                return jsonify({
                    'success': False,
                    'message': 'An unexpected error occurred',
                    'errors': [str(e)]
                }), 500

        # For GET requests, render the template
        partners = sorted(set(
            partner['name'] 
            for prop in properties 
            for partner in prop.get('partners', [])
        ))
        logger.debug(f"Rendering add_properties template with {len(partners)} partners")
        return render_template('properties/add_properties.html', partners=partners)

    except Exception as e:
        logger.error(f"Unexpected error in add_properties: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred',
            'errors': [str(e)]
        }), 500
        
@properties_bp.route('/remove_properties', methods=['GET', 'POST'])
@login_required
def remove_properties():
    """Handle property removal for property managers."""
    logging.info(f"Remove properties route accessed by user: {current_user.name} (ID: {current_user.id})")
    
    try:
        # Get user's properties
        properties = get_properties_for_user(current_user.id, current_user.name)
        logging.debug(f"Retrieved {len(properties)} properties for user")

        if request.method == 'GET':
            return render_template(
                'properties/remove_properties.html', 
                properties=properties
            )

        # Handle POST request
        if request.method == 'POST':
            property_address = request.form.get('property_select')
            confirmation = request.form.get('confirm_input')
            
            logging.debug(f"Processing removal request for property: {property_address}")
            logging.debug(f"Current user: {current_user.name} (ID: {current_user.id})")
            
            if not property_address:
                return jsonify({
                    'success': False,
                    'message': 'Please select a property'
                }), 400

            # Find selected property data
            property_data = next(
                (prop for prop in properties if prop['address'] == property_address),
                None
            )

            if not property_data:
                return jsonify({
                    'success': False,
                    'message': 'Selected property not found'
                }), 404

            # Verify property manager status with debug logging
            logging.debug(f"Checking property manager status...")
            logging.debug(f"Property data: {property_data}")
            if not is_property_manager(current_user.id, property_data):
                logging.error(f"User {current_user.name} (ID: {current_user.id}) " +
                            f"is not a property manager for {property_address}")
                return jsonify({
                    'success': False,
                    'message': 'You must be a property manager to remove properties'
                }), 403

            try:
                # Load properties data
                properties_file = os.path.join(current_app.config['DATA_DIR'], 'properties.json')
                with open(properties_file, 'r') as f:
                    all_properties = json.load(f)

                # Remove the property
                all_properties = [p for p in all_properties if p['address'] != property_address]

                # Save updated properties
                with open(properties_file, 'w') as f:
                    json.dump(all_properties, f, indent=2)

                logging.info(f"Successfully removed property: {property_address}")
                return jsonify({
                    'success': True,
                    'message': 'Property successfully removed'
                })

            except Exception as e:
                logging.error(f"Error removing property: {str(e)}")
                logging.error(traceback.format_exc())
                return jsonify({
                    'success': False,
                    'message': 'Error removing property from database'
                }), 500

    except Exception as e:
        logging.error(f"Error in remove_properties route: {str(e)}")
        logging.error(traceback.format_exc())
        
        if request.method == 'GET':
            return render_template(
                'properties/remove_properties.html',
                properties=[],
                error_message="Unable to load properties. Please try again later."
            )
        
        return jsonify({
            'success': False,
            'message': 'Error loading properties database'
        }), 500

    # This line should never be reached but included for completeness
    return render_template(
        'properties/remove_properties.html',
        properties=properties
    )

@properties_bp.route('/edit_properties', methods=['GET', 'POST'])
@login_required
def edit_properties():
    """Handle property editing"""
    try:
        logger.info(f"Edit properties route accessed by user: {current_user.email}")
        
        # Validate and get properties file path from config
        if 'PROPERTIES_FILE' not in current_app.config:
            logger.error("PROPERTIES_FILE not found in application config")
            raise ValueError("Properties file path not configured")
            
        properties_file = current_app.config.get('PROPERTIES_FILE')
        if not properties_file:
            logger.error("PROPERTIES_FILE is None or empty")
            raise ValueError("Properties file path not configured")
            
        logger.debug(f"Properties file path: {properties_file}")
        properties_dir = os.path.dirname(properties_file)
        
        # Debug logging
        logger.debug(f"Properties directory path: {properties_dir}")
        logger.debug(f"Directory exists: {os.path.exists(properties_dir)}")
        logger.debug(f"File exists: {os.path.exists(properties_file)}")
        logger.debug(f"Current working directory: {os.getcwd()}")

        # Ensure the directory exists
        if not os.path.exists(properties_dir):
            os.makedirs(properties_dir, exist_ok=True)
            logger.debug(f"Created directory: {properties_dir}")

        # Load properties from JSON file
        try:
            with open(properties_file, 'r') as f:
                properties = json.load(f)
                logger.debug(f"Successfully loaded {len(properties)} properties for editing")

            # If user is not admin, filter properties to only show those they're a partner in
            if not current_user.role.lower() == 'admin':
                original_count = len(properties)
                properties = [
                    prop for prop in properties
                    if any(partner['name'] == current_user.name for partner in prop.get('partners', []))
                ]
                logger.debug(f"Filtered properties for non-admin user. Original: {original_count}, Filtered: {len(properties)}")

        except FileNotFoundError:
            logger.warning(f"Properties file not found at {properties_file}, creating new file")
            properties = []
            with open(properties_file, 'w') as f:
                json.dump(properties, f, indent=2)
        except json.JSONDecodeError as e:
            error_msg = f"Error decoding properties JSON: {str(e)}"
            logger.error(error_msg)
            return jsonify({'success': False, 'message': error_msg}), 500

        if request.method == 'POST':
            logger.debug("Processing POST request for edit_properties")
            try:
                # Get and validate incoming data
                data = request.get_json()
                if not data:
                    raise ValueError("No data received")

                logger.debug(f"Received edit request data for property: {data.get('address', 'Unknown')}")

                # Validate property data
                is_valid, validation_errors = validate_property_data(data)
                if not is_valid:
                    logger.warning(f"Property validation failed during edit: {validation_errors}")
                    return jsonify({
                        'success': False,
                        'message': 'Validation failed',
                        'errors': validation_errors
                    }), 400

                # Find the property to update
                property_index = None
                for i, prop in enumerate(properties):
                    if prop['address'] == data['address']:
                        # Check if user has permission to edit
                        if not current_user.role.lower() == 'admin':
                            if not any(partner['name'] == current_user.name 
                                     for partner in prop.get('partners', [])):
                                logger.warning(f"User {current_user.email} attempted to edit property without permission: {data['address']}")
                                return jsonify({
                                    'success': False,
                                    'message': 'You do not have permission to edit this property'
                                }), 403
                        property_index = i
                        logger.debug(f"Found property at index {property_index}")
                        break

                if property_index is None:
                    logger.warning(f"Property not found for editing: {data['address']}")
                    raise ValueError(f"Property not found: {data['address']}")

                # Sanitize and update the property
                try:
                    sanitized_data = sanitize_property_data(data)
                    properties[property_index] = sanitized_data
                    logger.debug(f"Property data sanitized and updated: {data['address']}")

                    # Save updated properties with safer file handling
                    temp_file = os.path.join(properties_dir, 'properties.json.tmp')
                    backup_file = os.path.join(properties_dir, 'properties.json.bak')
                    logger.debug(f"Temp file path: {temp_file}")
                    logger.debug(f"Backup file path: {backup_file}")

                    # Write to temporary file
                    with open(temp_file, 'w') as f:
                        json.dump(properties, f, indent=2)
                        logger.debug("Written data to temporary file")

                    # Create backup of current file if it exists
                    if os.path.exists(properties_file):
                        import shutil
                        shutil.copy2(properties_file, backup_file)
                        logger.debug("Created backup file")

                    # Rename temporary file to actual file
                    os.replace(temp_file, properties_file)
                    logger.debug("Replaced original file with updated version")

                    # Remove backup file if everything succeeded
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                        logger.debug("Removed backup file")

                    logger.info(f"Property successfully updated: {data['address']}")
                    return jsonify({
                        'success': True,
                        'message': f"Property {data['address']} updated successfully"
                    })

                except Exception as e:
                    logger.error(f"Error saving property updates: {str(e)}")
                    # Attempt to restore from backup if it exists
                    if os.path.exists(backup_file):
                        try:
                            os.replace(backup_file, properties_file)
                            logger.info("Successfully restored from backup file")
                        except Exception as restore_error:
                            logger.error(f"Error restoring from backup: {str(restore_error)}")
                    raise

            except ValueError as ve:
                error_msg = str(ve)
                logger.warning(f"Validation error in edit_properties: {error_msg}")
                return jsonify({'success': False, 'message': error_msg}), 400

            except Exception as e:
                error_msg = f"Error updating property data: {str(e)}"
                logger.error(error_msg)
                return jsonify({'success': False, 'message': error_msg}), 500

        # For GET requests, render template with properties list
        logger.debug(f"Rendering edit_properties template with {len(properties)} properties")
        return render_template('properties/edit_properties.html', properties=properties)

    except Exception as e:
        error_msg = f"Unexpected error in edit_properties: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({'success': False, 'message': error_msg}), 500

@properties_bp.route('/get_property_details', methods=['GET'])
@login_required
def get_property_details():
    """Fetch property details for editing"""
    logger.debug(f"Property details request from user: {current_user.email}")
    
    try:
        # Validate address parameter
        address = request.args.get('address')
        if not address:
            logger.warning("Property details requested without address")
            return jsonify({
                'success': False,
                'message': 'No address provided'
            }), 400

        logger.debug(f"Fetching details for property: {address}")

        # Load properties file
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)

        # Find the requested property
        property_details = next(
            (prop for prop in properties if prop['address'] == address),
            None
        )

        if not property_details:
            logger.warning(f"Property not found: {address}")
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404

        # Check user permission - must be either Project Manager or a partner
        is_partner = any(partner['name'] == current_user.name 
                        for partner in property_details.get('partners', []))
        is_pm = any(partner['name'] == current_user.name and 
                partner.get('is_property_manager', False)  # Changed from user_is_project_manager
                for partner in property_details.get('partners', []))
        
        if not (is_partner or is_pm):
            logger.warning(f"User {current_user.email} attempted to access unauthorized property details: {address}")
            return jsonify({
                'success': False,
                'message': 'You do not have permission to view this property'
            }), 403

        # Add flag to indicate if user is Project Manager
        property_details['is_property_manager'] = is_pm

        logger.info(f"Successfully retrieved property details for: {address}")
        return jsonify({
            'success': True,
            'property': property_details
        })

    except Exception as e:
        error_msg = f"Unexpected error in get_property_details: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
    
@properties_bp.route('/get_partners_for_property', methods=['GET'])
@login_required
def api_get_partners_for_property():
    """Get partners associated with a specific property"""
    logger.debug(f"Partners request for property from user: {current_user.email}")
    
    # Validate property_id parameter
    property_id = request.args.get('property_id')
    if not property_id:
        logger.warning("Partner request received without property_id")
        return jsonify({
            'success': False,
            'message': 'Property ID is required'
        }), 400
    
    try:
        logger.debug(f"Fetching partners for property: {property_id}")
        partners = get_partners_for_property(property_id)
        
        # Validate user has permission to view partners
        if not current_user.role.lower() == 'admin':
            user_is_partner = any(
                partner['name'] == current_user.name 
                for partner in partners
            )
            if not user_is_partner:
                logger.warning(f"Unauthorized partner list request from {current_user.email} for property {property_id}")
                return jsonify({
                    'success': False,
                    'message': 'You do not have permission to view this property\'s partners'
                }), 403

        logger.debug(f"Found {len(partners)} partners for property {property_id}")
        return jsonify({
            'success': True,
            'partners': partners
        })
        
    except FileNotFoundError:
        logger.error("Properties database not found while fetching partners")
        return jsonify({
            'success': False,
            'message': 'Properties database not found'
        }), 500
    except Exception as e:
        logger.error(f"Error fetching partners for property {property_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching partners: {str(e)}'
        }), 500

@properties_bp.route('/test_properties', methods=['GET'])
@login_required
def test_properties():
    """Test endpoint to verify properties database access"""
    logger.debug(f"Test properties endpoint accessed by user: {current_user.email}")
    
    try:
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            logger.info(f"Successfully tested properties access. Found {len(properties)} properties.")
            return jsonify({
                'success': True,
                'count': len(properties)
            })
    except FileNotFoundError:
        logger.error("Properties database not found during test")
        return jsonify({
            'success': False,
            'error': 'Properties database not found'
        }), 500
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error during properties test: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Invalid properties database format'
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error during properties test: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@properties_bp.route('/get_available_partners', methods=['GET'])
@login_required
def get_available_partners():
    """Get list of available partners for the current user"""
    logger.debug(f"Available partners request from user: {current_user.email}")
    
    try:
        # Initialize set for unique partners
        available_partners: Set[str] = set()
        available_partners.add(current_user.name)
        
        # Load properties
        try:
            with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
                properties = json.load(f)
                logger.debug(f"Loaded {len(properties)} properties to check for partners")
        except FileNotFoundError:
            logger.error("Properties database not found while fetching available partners")
            return jsonify({
                'success': False,
                'message': 'Properties database not found'
            }), 500
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding properties JSON: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error reading properties database'
            }), 500
            
        # Find properties where current user is a partner
        user_properties = []
        for property in properties:
            try:
                user_is_partner = any(
                    partner['name'] == current_user.name 
                    for partner in property.get('partners', [])
                )
                
                if user_is_partner:
                    user_properties.append(property)
                    # Add all partners from this property
                    for partner in property.get('partners', []):
                        if partner.get('name'):
                            available_partners.add(partner['name'])
                            
            except Exception as e:
                logger.warning(f"Error processing property partners: {str(e)}")
                continue
        
        logger.debug(f"Found {len(user_properties)} properties for user {current_user.name}")
        logger.debug(f"Found {len(available_partners)} unique partners")
        
        # Convert set to sorted list
        partners_list = sorted(list(available_partners))
        
        return jsonify({
            'success': True,
            'partners': partners_list
        })
        
    except Exception as e:
        logger.error(f"Error fetching available partners: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error fetching partners: {str(e)}'
        }), 500

# Error handlers
@properties_bp.errorhandler(400)
def bad_request_error(error):
    """Handle bad request errors"""
    logger.warning(f"Bad request error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Bad Request: ' + str(error)
    }), 400

@properties_bp.errorhandler(403)
def forbidden_error(error):
    """Handle forbidden errors"""
    logger.warning(f"Forbidden error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Forbidden: ' + str(error)
    }), 403

@properties_bp.errorhandler(404)
def not_found_error(error):
    """Handle not found errors"""
    logger.warning(f"Not found error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Not Found: ' + str(error)
    }), 404

@properties_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({
        'success': False,
        'message': 'Internal Server Error'
    }), 500

# After request handler
@properties_bp.after_request
def after_request(response):
    """Log all responses"""
    logger.debug(f"Response status: {response.status}")
    return response