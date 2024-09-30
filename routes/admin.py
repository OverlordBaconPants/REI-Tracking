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
    
    # Initialize partners and properties
    partners = []
    properties = []

    # Get existing partners for the dropdown
    try:
        logging.info(f"Attempting to read properties file: {current_app.config['PROPERTIES_FILE']}")
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
            logging.info(f"Successfully loaded properties. Number of properties: {len(properties)}")
            partners = sorted(set(prop['partner'] for prop in properties if prop.get('partner')))
            logging.info(f"Extracted partners: {partners}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error when reading properties file: {str(e)}")
        flash(f'Error reading properties file: {str(e)}', 'danger')
    except IOError as e:
        logging.error(f"IO error when accessing properties file: {str(e)}")
        flash(f'Error accessing properties file: {str(e)}', 'danger')
    except Exception as e:
        logging.error(f"Unexpected error when processing properties file: {str(e)}")
        flash(f'An unexpected error occurred: {str(e)}', 'danger')

    if request.method == 'POST':
        try:
            # Handle partner selection or new partner addition
            selected_partner = request.form['partner']
            if selected_partner == 'new':
                new_partner = request.form.get('new_partner')
                if new_partner:
                    selected_partner = new_partner
                else:
                    raise ValueError("New partner name is required when 'Add new partner' is selected.")

            new_property = {
                'address': request.form['property_address'],
                'purchase_price': int(request.form['purchase_price']),
                'down_payment': int(request.form['down_payment']),
                'primary_loan_rate': float(request.form['primary_loan_rate']),
                'primary_loan_term': int(request.form['primary_loan_term']),
                'purchase_date': request.form['purchase_date'],
                'loan_start_date': request.form['loan_start_date'],
                'seller_financing_amount': int(request.form.get('seller_financing_amount') or 0),
                'seller_financing_rate': float(request.form.get('seller_financing_rate') or 0),
                'seller_financing_term': float(request.form.get('seller_financing_term') or 0),
                'closing_costs': int(request.form['closing_costs']),
                'renovation_costs': int(request.form['renovation_costs']),
                'marketing_costs': int(request.form['marketing_costs']),
                'holding_costs': int(request.form['holding_costs']),
                'partner': selected_partner,
                'equity_share': float(request.form['equity_share'])
            }
            
            # Logic to save the new_property to the properties file
            properties.append(new_property)
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump(properties, f, indent=2)
            
            logging.info(f"New property added: {new_property['address']} with partner: {selected_partner}")
            flash('Property added successfully', 'success')
            return redirect(url_for('admin.add_properties'))
        except ValueError as ve:
            logging.error(f"Validation error: {str(ve)}")
            flash(str(ve), 'danger')
        except Exception as e:
            logging.error(f"Error processing form submission: {str(e)}")
            flash(f'An error occurred while adding the property: {str(e)}', 'danger')

    # If it's a GET request or if there was an error in POST, render the template
    logging.info(f"Final list of partners to be passed to template: {partners}")
    return render_template('admin/add_properties.html', partners=partners)

# Route for removing properties
@admin_bp.route('/remove_properties', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_properties():
    properties = []
    try:
        with open(current_app.config['PROPERTIES_FILE'], 'r') as f:
            properties = json.load(f)
    except Exception as e:
        logging.error(f"Error loading properties: {str(e)}")
        return jsonify({'success': False, 'message': 'Error loading properties.'}), 500

    if request.method == 'POST':
        property_to_remove = request.form.get('property_select')

        if not property_to_remove:
            return jsonify({'success': False, 'message': 'No property selected for removal.'}), 400

        try:
            properties = [p for p in properties if p['address'] != property_to_remove]
            with open(current_app.config['PROPERTIES_FILE'], 'w') as f:
                json.dump(properties, f, indent=2)
            return jsonify({'success': True, 'message': 'Property Successfully Removed!'})
        except Exception as e:
            logging.error(f"Error removing property: {str(e)}")
            return jsonify({'success': False, 'message': 'Error removing property.'}), 500

    return render_template('admin/remove_properties.html', properties=properties)


# Route for editing properties
@admin_bp.route('/edit_properties', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_properties():
    if request.method == 'POST':
        # Handle the form submission for editing a property
        # This is where you'd process the form data and update the property in the database
        flash('Property updated successfully', 'success')
    # Render the template for editing properties
    return render_template('admin/edit_properties.html')

# Loans Management Routes

# Route for viewing all loans
@admin_bp.route('/loans')
@login_required
@admin_required
def loans():
    # Fetch loans data from the database
    loans = []  # Replace this with actual data fetching logic
    # Render the template for viewing loans, passing the loans data
    return render_template('admin/loans.html', loans=loans)

# Route for adding new loans
@admin_bp.route('/add_loans', methods=['GET', 'POST'])
@login_required
@admin_required
def add_loans():
    if request.method == 'POST':
        # Handle the form submission for adding a new loan
        # This is where you'd process the form data and add it to the database
        flash('Loan added successfully', 'success')
    # Render the template for adding loans
    return render_template('admin/add_loans.html')

# Route for removing loans
@admin_bp.route('/remove_loans', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_loans():
    if request.method == 'POST':
        # Handle the form submission for removing a loan
        # This is where you'd process the request and remove the loan from the database
        flash('Loan removed successfully', 'success')
    # Render the template for removing loans
    return render_template('admin/remove_loans.html')

# Route for editing loans
@admin_bp.route('/edit_loans', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_loans():
    if request.method == 'POST':
        # Handle the form submission for editing a loan
        # This is where you'd process the form data and update the loan in the database
        flash('Loan updated successfully', 'success')
    # Render the template for editing loans
    return render_template('admin/edit_loans.html')

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