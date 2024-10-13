from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from services.transaction_service import add_transaction, is_duplicate_transaction, get_properties_for_user, get_transaction_by_id, update_transaction, get_categories, get_partners_for_property
from utils.utils import admin_required
import os
import logging
import json
import traceback

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
@login_required
def transactions_list():
    return render_template('transactions/transactions_list.html')

@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transactions():
    logging.info(f"Add transaction route accessed by user: {current_user.name} (ID: {current_user.id})")

    properties = get_properties_for_user(current_user.id, current_user.name)
    
    if request.method == 'POST':
        logging.info("Processing POST request for add_transaction")
        try:
            # Check if a file is present in the request
            if 'documentation_file' not in request.files:
                flash('No file provided. Please attach supporting documentation.', 'error')
                return redirect(url_for('transactions.add_transactions'))
            
            file = request.files['documentation_file']
            if file.filename == '':
                flash('No file selected. Please attach supporting documentation.', 'error')
                return redirect(url_for('transactions.add_transactions'))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
            else:
                flash('Invalid file type. Allowed types are: ' + ', '.join(current_app.config['ALLOWED_EXTENSIONS']), 'error')
                return redirect(url_for('transactions.add_transactions'))

            # Get form data
            transaction_data = {
                'property_id': request.form.get('property_id'),
                'type': request.form.get('type'),
                'category': request.form.get('category'),
                'description': request.form.get('description'),
                'amount': float(request.form.get('amount')),
                'date': request.form.get('date'),
                'collector_payer': request.form.get('collector_payer'),
                'documentation_file': filename,
                'reimbursement': {
                    'date_shared': request.form.get('date_shared'),
                    'share_description': request.form.get('share_description'),
                    'reimbursement_status': request.form.get('reimbursement_status')
                }
            }

            # Check for duplicate transaction
            if is_duplicate_transaction(transaction_data):
                flash("This transaction appears to be a duplicate and was not added.", "warning")
                return redirect(url_for('transactions.add_transactions'))

            # Process the transaction data
            add_transaction(transaction_data)
            
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('transactions.add_transactions'))
        except Exception as e:
            logging.error(f"Error adding transaction: {str(e)}")
            flash(f"Error adding transaction: {str(e)}", "error")
            return redirect(url_for('transactions.add_transactions'))

    # For GET requests, render the template
    return render_template('transactions/add_transactions.html', properties=properties)

@transactions_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    logging.info(f"Uploaded file request for: {filename} by user: {current_user.id}")
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    logging.info("transactions.py blueprint loaded")

@transactions_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_transactions(transaction_id):
    try:
        current_app.logger.info(f"Edit transactions route accessed for transaction ID: {transaction_id}")
        transaction = get_transaction_by_id(transaction_id)
        
        if not transaction:
            current_app.logger.warning(f"Transaction not found for ID: {transaction_id}")
            return jsonify({'success': False, 'message': 'Transaction not found.'}), 404

        if request.method == 'POST':
            try:
                current_app.logger.info(f"Processing POST request to edit transaction ID: {transaction_id}")
                form_data = request.form.to_dict()
                current_app.logger.debug(f"Received form data: {form_data}")

                updated_transaction = {
                    'id': transaction_id,
                    'property_id': form_data.get('property_id'),
                    'type': form_data.get('type'),
                    'category': form_data.get('category'),
                    'description': form_data.get('description'),
                    'amount': float(form_data.get('amount')),
                    'date': form_data.get('date'),
                    'collector_payer': form_data.get('collector_payer'),
                    'reimbursement': {
                        'date_shared': form_data.get('date_shared'),
                        'share_description': form_data.get('share_description'),
                        'reimbursement_status': form_data.get('reimbursement_status')
                    }
                }
                
                # Handle file upload if a new file is provided
                if 'documentation_file' in request.files:
                    file = request.files['documentation_file']
                    if file.filename != '':
                        if allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                            file.save(file_path)
                            updated_transaction['documentation_file'] = filename
                        else:
                            return jsonify({'success': False, 'message': 'Invalid file type.'}), 400

                update_transaction(updated_transaction)
                current_app.logger.info(f"Transaction ID: {transaction_id} updated successfully")
                return jsonify({'success': True, 'message': 'Transaction updated successfully.'})

            except Exception as e:
                current_app.logger.error(f"Error updating transaction: {str(e)}")
                current_app.logger.error(traceback.format_exc())
                return jsonify({'success': False, 'message': f'An error occurred while updating the transaction: {str(e)}'}), 500
        
        current_app.logger.info(f"Rendering edit form for transaction ID: {transaction_id}")
        properties = get_properties_for_user(current_user.id, current_user.name)
        return render_template('transactions/edit_transactions.html', transaction=transaction, properties=properties)

    except Exception as e:
        current_app.logger.error(f"Unexpected error in edit_transactions route: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'success': False, 'message': 'An unexpected error occurred. Please try again later.'}), 500

@transactions_bp.route('/remove', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_transactions():
    if request.method == 'POST':
        # Handle the form submission for removing a transaction
        # This is where you'd process the request and remove the transaction from the database
        flash('Transaction removed successfully', 'success')
    # Render the template for removing transactions
    return render_template('transaction/remove_transactions.html')

@transactions_bp.route('/view/')
@login_required
def view_transactions():
    try:
        current_app.logger.info(f"View transactions accessed by user: {current_user.id}")
        return render_template('transactions/view_transactions.html')
    except Exception as e:
        current_app.logger.error(f"Error in view_transactions: {str(e)}")
        flash(f"An error occurred while loading the transactions view: {str(e)}", "error")
        return redirect(url_for('main.index'))

@transactions_bp.route('/test')
def test_route():
    return "Transactions blueprint is working!"

@transactions_bp.route('/artifact/<path:filename>')
@login_required
def get_artifact(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@transactions_bp.route('/api/categories')
@login_required
def get_transaction_categories():
    transaction_type = request.args.get('type')
    categories = get_categories(transaction_type)
    return jsonify(categories)

@transactions_bp.route('/api/partners')
@login_required
def get_property_partners():
    property_id = request.args.get('property_id')
    partners = get_partners_for_property(property_id)
    return jsonify(partners)