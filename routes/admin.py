# routes/admin.py

# Import necessary modules
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_required, current_user
from functools import wraps
from services.user_service import check_password, get_user_by_email
import logging
import json

# Create a Blueprint for admin routes
# The url_prefix means all routes defined here will start with '/admin'
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Define a custom decorator to require admin privileges
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is authenticated and has the 'Admin' role
        if not current_user.is_authenticated or current_user.role != 'Admin':
            # If not, flash an error message and redirect to the main page
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index')), 403
        # If the user is an admin, allow access to the route
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard route
@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Render the admin dashboard template
    return render_template('main/dashboard.html')

# Properties Management Routes

# Route for adding new properties
@admin_bp.route('/add_properties', methods=['GET', 'POST'])
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
                               'primary_loan_term', 'purchase_date', 'loan_start_date', 'partners']
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
    return render_template('admin/add_properties.html', partners=partners)

# Route for removing properties
@admin_bp.route('/remove_properties', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        logging.info("Processing POST request in remove_properties")
        property_to_remove = request.form.get('property_select')
        confirm_input = request.form.get('confirm_input')

        logging.info(f"Property to remove: {property_to_remove}")
        logging.info(f"Confirmation input: {confirm_input}")

        if not property_to_remove:
            logging.warning("No property selected for removal")
            flash('No property selected for removal.', 'danger')
            return redirect(url_for('admin.remove_properties'))

        expected_confirm_phrase = "I am sure I want to do this."
        if confirm_input != expected_confirm_phrase:
            logging.warning(f"Incorrect confirmation phrase. Expected: {expected_confirm_phrase}, Got: {confirm_input}")
            flash('Incorrect confirmation phrase. Property not removed.', 'danger')
            return redirect(url_for('admin.remove_properties'))

        try:
            properties = [p for p in properties if p['address'] != property_to_remove]
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump(properties, f, indent=2)
            logging.info(f"Property successfully removed: {property_to_remove}")
            flash('Property Successfully Removed!', 'success')
        except Exception as e:
            logging.error(f"Error removing property: {str(e)}")
            flash('Error removing property.', 'danger')

        return redirect(url_for('admin.remove_properties'))

    logging.info(f"Rendering remove_properties template with {len(properties)} properties")
    return render_template('admin/remove_properties.html', properties=properties)

# Route for editing properties
@admin_bp.route('/edit_properties', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_properties():
    logging.info("Entering edit_properties function")
    
    partners = []
    properties = []

    try:
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            partners = sorted(set(partner['name'] for prop in properties for partner in prop.get('partners', [])))
        logging.info(f"Loaded {len(properties)} properties and {len(partners)} unique partners")
    except Exception as e:
        logging.error(f"Error when processing properties file: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        updated_property = request.form.to_dict()
        address = updated_property.pop('property_select')
        
        try:
            existing_property = next((prop for prop in properties if prop['address'] == address), None)
            if not existing_property:
                raise ValueError(f"Property with address '{address}' not found.")

            # Update fields
            for key, value in updated_property.items():
                if key not in ['partners', 'new_partner']:
                    if value.strip():
                        if key in ['purchase_price', 'down_payment', 'primary_loan_term', 'seller_financing_amount', 
                                   'seller_financing_term', 'closing_costs', 'renovation_costs', 'marketing_costs', 'holding_costs']:
                            existing_property[key] = int(value)
                        elif key in ['primary_loan_rate', 'seller_financing_rate']:
                            existing_property[key] = float(value)
                        else:
                            existing_property[key] = value

            # Handle partners
            partners_data = []
            for key, value in request.form.items():
                if key.startswith('partners[') and key.endswith('[name]'):
                    index = ''.join(char for char in key[8:-6] if char.isdigit())
                    partner_name = value
                    equity_share = float(request.form.get(f'partners[{index}][equity_share]', 0))
                    if partner_name == 'new':
                        partner_name = request.form.get(f'partners[{index}][new_name]')
                    if not partner_name or partner_name.strip() == '':
                        raise ValueError(f"Partner name is required for partner {int(index) + 1}")
                    partners_data.append({'name': partner_name.strip(), 'equity_share': equity_share})

            total_equity = sum(partner['equity_share'] for partner in partners_data)
            if abs(total_equity - 100) > 0.01:
                raise ValueError(f"Total equity must equal 100%, current total: {total_equity}%")

            existing_property['partners'] = partners_data

            # Save updated properties
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump(properties, f, indent=2)
            
            logging.info(f"Property updated: {address}")
            flash('Property updated successfully', 'success')
        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            flash(str(ve), 'danger')
        except Exception as e:
            logging.error(f"Error updating property: {str(e)}")
            flash(f'An error occurred while updating the property: {str(e)}', 'danger')
        
        return redirect(url_for('admin.edit_properties'))

    return render_template('admin/edit_properties.html', properties=properties, partners=partners)

@admin_bp.route('/get_property_details', methods=['GET'])
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


# Transactions Management Routes

# Route for removing transactions
@admin_bp.route('/remove_transactions', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_transactions():
    if request.method == 'POST':
        # Handle the form submission for removing a transaction
        # This is where you'd process the request and remove the transaction from the database
        flash('Transaction removed successfully', 'success')
    # Render the template for removing transactions
    return render_template('admin/remove_transactions.html')

# Route for editing transactions
@admin_bp.route('/edit_transactions', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_transactions():
    if request.method == 'POST':
        # Handle the form submission for editing a transaction
        # This is where you'd process the form data and update the transaction in the database
        flash('Transaction updated successfully', 'success')
    # Render the template for editing transactions
    return render_template('admin/edit_transactions.html')

# Note: The route for adding transactions is in main.py as it's accessible to all authenticated users

# You can add more admin routes here as needed, such as user management, reporting, etc.
# Remember to use the @login_required and @admin_required decorators for all admin routes