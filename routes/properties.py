# Import necessary modules
from utils.flash import flash_message
from flask import Blueprint, render_template, request, current_app, jsonify
from flask_login import login_required, current_user
from utils.utils import admin_required
from services.transaction_service import get_partners_for_property
import logging
import json
from datetime import datetime

# Create a Blueprint for properties routes
# The url_prefix means all routes defined here will start with '/properties'
properties_bp = Blueprint('properties', __name__, url_prefix='/properties')

# Route for adding new properties
@properties_bp.route('/add_properties', methods=['GET', 'POST'])
@login_required
@admin_required
def add_properties():
    logging.info("Entering add_properties function")
    
    partners = []
    properties = []

    try:
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            logging.info(f"Successfully loaded properties. Number of properties: {len(properties)}")
            partners = sorted(set(partner['name'] for prop in properties for partner in prop.get('partners', [])))
            logging.info(f"Extracted partners: {partners}")
    except Exception as e:
        logging.error(f"Error when processing properties file: {str(e)}")
        flash_message(f'An error occurred while loading properties: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)}), 500

    if request.method == 'POST':
        try:
            new_property = request.get_json()
            logging.info(f"Received property data: {json.dumps(new_property, indent=2)}")

            if not new_property:
                raise ValueError("No data received")

            # Validate the new property data
            required_fields = ['address', 'purchase_price', 'down_payment', 'primary_loan_rate', 
                               'primary_loan_term', 'purchase_date', 'loan_amount', 'loan_start_date', 'partners']
            for field in required_fields:
                if field not in new_property or new_property[field] is None:
                    logging.error(f"Missing or null required field: {field}")
                    raise ValueError(f"{field} is required and cannot be null")

            # Validate address
            if not new_property['address'].strip():
                raise ValueError("Address cannot be empty")

            # Validate partner data
            partners_data = new_property['partners']
            if not partners_data:
                raise ValueError("At least one partner is required")

            for partner in partners_data:
                if 'name' not in partner or not partner['name'].strip():
                    raise ValueError("Partner name is required and cannot be empty")
                if 'equity_share' not in partner or not isinstance(partner['equity_share'], (int, float)):
                    raise ValueError("Valid equity share is required for each partner")

            total_equity = sum(partner['equity_share'] for partner in partners_data)
            if abs(total_equity - 100) > 0.01:  # Allow for small floating-point discrepancies
                raise ValueError(f"Total equity must equal 100%, current total: {total_equity}%")

            # Add the new property
            properties.append(new_property)

            # Save updated properties
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump(properties, f, indent=2)

            logging.info(f"New property added: {new_property['address']}")
            flash_message('Property added successfully', 'success')
            return jsonify({'success': True, 'message': 'Property added successfully'})

        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            flash_message(str(ve), 'error')
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as e:
            logging.error(f"Error processing form submission: {str(e)}")
            flash_message(f'An error occurred while adding the property: {str(e)}', 'error')
            return jsonify({'success': False, 'message': f'An error occurred while adding the property: {str(e)}'}), 500

    # For GET requests, render the template
    logging.info(f"Rendering add_properties template with partners: {partners}")
    return render_template('properties/add_properties.html', partners=partners)

# Route for removing properties
@properties_bp.route('/remove_properties', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_properties():
    logging.info("Entering remove_properties route")
    properties = []
    try:
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
    except Exception as e:
        logging.error(f"Error loading properties: {str(e)}")
        flash_message('Error loading properties.', 'error')
        return jsonify({'success': False, 'message': 'Error loading properties'})

    if request.method == 'POST':
        logging.info("Processing POST request in remove_properties")
        property_to_remove = request.form.get('property_select')
        confirm_input = request.form.get('confirm_input')

        logging.info(f"Property to remove: {property_to_remove}")
        logging.info(f"Confirmation input: {confirm_input}")

        if not property_to_remove:
            logging.warning("No property selected for removal")
            return jsonify({'success': False, 'message': 'No property selected for removal'})

        expected_confirm_phrase = "I am sure I want to do this."
        if confirm_input != expected_confirm_phrase:
            logging.warning(f"Incorrect confirmation phrase. Expected: {expected_confirm_phrase}, Got: {confirm_input}")
            return jsonify({'success': False, 'message': 'Incorrect confirmation phrase. Property not removed'})

        try:
            properties = [p for p in properties if p['address'] != property_to_remove]
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump(properties, f, indent=2)
            logging.info(f"Property successfully removed: {property_to_remove}")
            flash_message('Property Successfully Removed!', 'success')
            return jsonify({'success': True, 'message': 'Property successfully removed'})
        except Exception as e:
            logging.error(f"Error removing property: {str(e)}")
            return jsonify({'success': False, 'message': f'Error removing property: {str(e)}'})

    logging.info(f"Rendering remove_properties template with {len(properties)} properties")
    return render_template('properties/remove_properties.html', properties=properties)

# Route for editing properties
@properties_bp.route('/edit_properties', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_properties():
    logging.info("Entering edit_properties route")
    
    try:
        # Load properties from JSON file
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            logging.info(f"Successfully loaded {len(properties)} properties")
    except Exception as e:
        error_msg = f"Error loading properties file: {str(e)}"
        logging.error(error_msg)
        flash_message(error_msg, 'error')
        return jsonify({'success': False, 'message': error_msg}), 500

    if request.method == 'POST':
        try:
            data = request.get_json()
            logging.info(f"Received edit request data: {json.dumps(data, indent=2)}")

            if not data:
                raise ValueError("No data received")

            if 'address' not in data:
                raise ValueError("Property address is required")

            # Validate partners data
            if 'partners' not in data or not data['partners']:
                raise ValueError("At least one partner is required")

            total_equity = sum(float(partner.get('equity_share', 0)) for partner in data['partners'])
            logging.info(f"Total equity calculated: {total_equity}")
            
            if abs(total_equity - 100) > 0.01:
                raise ValueError(f"Total equity must equal 100%. Current total: {total_equity}%")

            # Find the property to update
            property_index = None
            for i, prop in enumerate(properties):
                if prop['address'] == data['address']:
                    property_index = i
                    break

            if property_index is None:
                raise ValueError(f"Property not found: {data['address']}")

            logging.info(f"Found property at index {property_index}")

            # Update the property
            try:
                properties[property_index].update({
                    'purchase_date': data['purchase_date'],
                    'loan_amount': data['loan_amount'],
                    'loan_start_date': data['loan_start_date'],
                    'purchase_price': data['purchase_price'],
                    'down_payment': data['down_payment'],
                    'primary_loan_rate': data['primary_loan_rate'],
                    'primary_loan_term': data['primary_loan_term'],
                    'seller_financing_amount': data.get('seller_financing_amount', 0),
                    'seller_financing_rate': data.get('seller_financing_rate', 0),
                    'seller_financing_term': data.get('seller_financing_term', 0),
                    'closing_costs': data.get('closing_costs', 0),
                    'renovation_costs': data.get('renovation_costs', 0),
                    'marketing_costs': data.get('marketing_costs', 0),
                    'holding_costs': data.get('holding_costs', 0),
                    'partners': data['partners']
                })

                # Save updated properties back to file
                with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                    json.dump(properties, f, indent=2)

                success_msg = f"Property {data['address']} updated successfully"
                logging.info(success_msg)
                flash_message(success_msg, 'success')
                return jsonify({'success': True, 'message': success_msg})

            except Exception as e:
                error_msg = f"Error updating property data: {str(e)}"
                logging.error(error_msg)
                return jsonify({'success': False, 'message': error_msg}), 500

        except ValueError as ve:
            error_msg = str(ve)
            logging.error(f"Validation error: {error_msg}")
            return jsonify({'success': False, 'message': error_msg}), 400

        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logging.error(error_msg, exc_info=True)
            return jsonify({'success': False, 'message': error_msg}), 500

    # GET request - render template with properties list
    return render_template('properties/edit_properties.html', properties=properties)

@properties_bp.route('/get_property_details', methods=['GET'])
@login_required
def get_property_details():
    """Endpoint to fetch property details for editing"""
    try:
        # Get address from query parameters
        address = request.args.get('address')
        if not address:
            return jsonify({
                'success': False,
                'message': 'No address provided'
            }), 400

        logging.info(f"Fetching details for property: {address}")

        # Load properties file
        try:
            with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
                properties = json.load(f)
        except FileNotFoundError:
            logging.error("Properties file not found")
            return jsonify({
                'success': False,
                'message': 'Properties database not found'
            }), 500
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding properties JSON: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error reading properties database'
            }), 500

        # Find the property
        property_details = next(
            (prop for prop in properties if prop['address'] == address),
            None
        )

        if property_details:
            logging.info(f"Found property details for: {address}")
            return jsonify({
                'success': True,
                'property': property_details
            })
        else:
            logging.warning(f"Property not found: {address}")
            return jsonify({
                'success': False,
                'message': 'Property not found'
            }), 404

    except Exception as e:
        logging.error(f"Unexpected error in get_property_details: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
    
@properties_bp.route('/get_partners_for_property', methods=['GET'])
@login_required
@admin_required
def api_get_partners_for_property():
    property_id = request.args.get('property_id')
    if not property_id:
        return jsonify({'error': 'Property ID is required'}), 400
    
    try:
        partners = get_partners_for_property(property_id)
        return jsonify(partners)
    except Exception as e:
        current_app.logger.error(f"Error fetching partners for property {property_id}: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching partners'}), 500

@properties_bp.route('/test_properties', methods=['GET'])
def test_properties():
    try:
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            return jsonify({
                'success': True,
                'count': len(properties)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
    
@properties_bp.route('/get_available_partners', methods=['GET'])
@login_required
def get_available_partners():
    try:
        current_user_email = current_user.id  # Assuming email is stored as the user ID
        available_partners = set()  # Use set to avoid duplicates
        
        # Add current user
        available_partners.add(current_user.name)
        
        # Load properties
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            
        # Find properties where current user is a partner
        for property in properties:
            user_is_partner = any(
                partner['name'] == current_user.name 
                for partner in property.get('partners', [])
            )
            
            if user_is_partner:
                # Add all partners from these properties
                for partner in property.get('partners', []):
                    available_partners.add(partner['name'])
        
        # Convert set to sorted list
        partners_list = sorted(list(available_partners))
        
        return jsonify({
            'success': True,
            'partners': partners_list
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching available partners: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error fetching partners: {str(e)}'
        }), 500