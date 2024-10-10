# routes/admin.py

# Import necessary modules
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from functools import wraps
from utils.utils import admin_required
from services.user_service import get_user_by_email, create_user, update_user_password, hash_password, verify_password
import logging
import json
import requests

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
        flash(f'An error occurred while loading properties: {str(e)}', 'danger')
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
            flash('Property added successfully', 'success')
            return jsonify({'success': True, 'message': 'Property added successfully'})

        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            flash(str(ve), 'danger')
            return jsonify({'success': False, 'message': str(ve)}), 400
        except Exception as e:
            logging.error(f"Error processing form submission: {str(e)}")
            flash(f'An error occurred while adding the property: {str(e)}', 'danger')
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
        flash('Error loading properties.', 'danger')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        logging.info("Processing POST request in remove_properties")
        property_to_remove = request.form.get('property_select')
        confirm_input = request.form.get('confirm_input')

        logging.info(f"Property to remove: {property_to_remove}")
        logging.info(f"Confirmation input: {confirm_input}")

        if not property_to_remove:
            logging.warning("No property selected for removal")
            flash('No property selected for removal.', 'danger')
            return redirect(url_for('properties.remove_properties'))

        expected_confirm_phrase = "I am sure I want to do this."
        if confirm_input != expected_confirm_phrase:
            logging.warning(f"Incorrect confirmation phrase. Expected: {expected_confirm_phrase}, Got: {confirm_input}")
            flash('Incorrect confirmation phrase. Property not removed.', 'danger')
            return redirect(url_for('properties.remove_properties'))

        try:
            properties = [p for p in properties if p['address'] != property_to_remove]
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump(properties, f, indent=2)
            logging.info(f"Property successfully removed: {property_to_remove}")
            flash('Property Successfully Removed!', 'success')
        except Exception as e:
            logging.error(f"Error removing property: {str(e)}")
            flash('Error removing property.', 'danger')

        return redirect(url_for('properties.remove_properties'))

    logging.info(f"Rendering remove_properties template with {len(properties)} properties")
    return render_template('properties/remove_properties.html', properties=properties)

# Route for editing properties
@properties_bp.route('/edit_properties', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_properties():
    properties_file = current_app.config['PROPERTIES_FILE']

    if request.method == 'GET':
        # Read properties from JSON file
        with open(properties_file, 'r') as f:
            properties = json.load(f)
        return render_template('properties/edit_properties.html', properties=properties)
    
    elif request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        address = data.get('address')
        if not address:
            return jsonify({'success': False, 'message': 'No property address provided'}), 400

        try:
            # Read current properties
            with open(properties_file, 'r') as f:
                properties = json.load(f)

            # Find the property to edit
            property_to_edit = next((prop for prop in properties if prop['address'] == address), None)
            if not property_to_edit:
                return jsonify({'success': False, 'message': 'Property not found'}), 404

            # Update property fields
            for key in ['purchase_price', 'down_payment', 'primary_loan_rate', 'primary_loan_term',
                        'purchase_date', 'loan_amount', 'loan_start_date', 'seller_financing_amount',
                        'seller_financing_rate', 'seller_financing_term', 'closing_costs',
                        'renovation_costs', 'marketing_costs', 'holding_costs']:
                if key in data:
                    property_to_edit[key] = data[key]

            # Update partners
            if 'partners' in data:
                property_to_edit['partners'] = data['partners']

            # Write updated properties back to file
            with open(properties_file, 'w') as f:
                json.dump(properties, f, indent=2)

            return jsonify({'success': True, 'message': 'Property updated successfully'})
        except Exception as e:
            current_app.logger.error(f"Error updating property: {str(e)}")
            return jsonify({'success': False, 'message': str(e)}), 500

@properties_bp.route('/get_property_details', methods=['GET'])
@login_required
@admin_required
def get_property_details():
    address = request.args.get('address')
    try:
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            property_details = next((prop for prop in properties if prop['address'] == address), None)
            if property_details:
                return jsonify({'success': True, 'property': property_details})
            else:
                return jsonify({'success': False, 'message': 'Property not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching property details: {str(e)}'}), 500

