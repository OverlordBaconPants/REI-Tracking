from utils.flash import flash_message
from flask import abort, Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from services.transaction_import_service import TransactionImportService
from services.transaction_service import add_transaction, is_duplicate_transaction, get_properties_for_user, get_transaction_by_id, update_transaction, get_categories, get_partners_for_property
from utils.utils import admin_required
import tempfile
import os
import re
import html
import logging
import json
import traceback
import pandas as pd

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/')
@login_required
def transactions_list():
    return render_template('transactions/transactions_list.html')

def generate_documentation_filename(transaction_id, original_filename):
    """Generate a standardized filename for documentation files"""
    if not original_filename:
        return ''
    
    # Remove any existing prefix
    if original_filename.startswith(('reimb_', 'trans_')):
        original_filename = original_filename.split('_', 1)[1]
    
    # Generate new filename with transaction ID prefix
    return f"trans_{transaction_id}_{secure_filename(original_filename)}"

@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transactions():
    logging.info(f"Add transaction route accessed by user: {current_user.name} (ID: {current_user.id})")

    properties = get_properties_for_user(current_user.id, current_user.name)
    
    if request.method == 'POST':
        logging.info("Processing POST request for add_transaction")
        try:
            # Get and sanitize notes
            notes = sanitize_notes(request.form.get('notes', ''))
            
            # Create transaction data structure
            transaction_data = {
                'property_id': request.form.get('property_id'),
                'type': request.form.get('type'),
                'category': request.form.get('category'),
                'description': request.form.get('description'),
                'amount': float(request.form.get('amount')),
                'date': request.form.get('date'),
                'collector_payer': request.form.get('collector_payer'),
                'notes': notes,
                'documentation_file': '',
                'reimbursement': {
                    'date_shared': request.form.get('date_shared'),
                    'share_description': request.form.get('share_description'),
                    'reimbursement_status': request.form.get('reimbursement_status'),
                    'documentation': None
                }
            }

            # Add the transaction first to get an ID
            add_transaction(transaction_data)
            transaction_id = transaction_data['id']

            # Handle documentation files after we have the transaction ID
            if 'documentation_file' in request.files:
                file = request.files['documentation_file']
                if file and file.filename:
                    if allowed_file(file.filename, file_type='documentation'):
                        filename = generate_documentation_filename(transaction_id, file.filename)
                        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        transaction_data['documentation_file'] = filename
                    else:
                        flash_message('Invalid file type. Allowed types are: ' + 
                                    ', '.join(current_app.config['ALLOWED_DOCUMENTATION_EXTENSIONS']), 'error')
                        return redirect(url_for('transactions.add_transactions'))

            # Handle reimbursement documentation
            if 'reimbursement_documentation' in request.files:
                reimb_file = request.files['reimbursement_documentation']
                if reimb_file and reimb_file.filename:
                    if allowed_file(reimb_file.filename, file_type='documentation'):
                        reimb_filename = generate_documentation_filename(transaction_id, reimb_file.filename)
                        reimb_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], reimb_filename)
                        reimb_file.save(reimb_file_path)
                        transaction_data['reimbursement']['documentation'] = reimb_filename
                    else:
                        flash_message('Invalid reimbursement documentation file type. Allowed types are: ' + 
                                    ', '.join(current_app.config['ALLOWED_DOCUMENTATION_EXTENSIONS']), 'error')
                        return redirect(url_for('transactions.add_transactions'))

            # Update the transaction with file information
            update_transaction(transaction_data)
            
            flash_message('Transaction added successfully!', 'success')
            return redirect(url_for('transactions.add_transactions'))

        except Exception as e:
            logging.error(f"Error adding transaction: {str(e)}")
            flash_message(f"Error adding transaction: {str(e)}", "error")
            return redirect(url_for('transactions.add_transactions'))

    # For GET requests, render the template
    return render_template(
        'transactions/add_transactions.html', 
        properties=properties)

def sanitize_notes(notes):
    """
    Sanitize notes input to prevent XSS and other injection attacks while preserving natural language.
    
    Args:
        notes (str): Raw notes input
        
    Returns:
        str: Sanitized notes string
    """
    if not notes:
        return ""
        
    # Strip any HTML tags
    notes = re.sub(r'<[^>]*?>', '', notes)
    
    # Don't escape special characters, but remove potentially dangerous characters
    notes = re.sub(r'[^\w\s\-_.,!?\'\"@#$%^&*()+=\[\]{};:\/|\\<>]', '', notes)
    
    # Limit to 150 characters
    notes = notes[:150]
    
    return notes.strip()

@transactions_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    logging.info(f"Uploaded file request for: {filename} by user: {current_user.id}")
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@transactions_bp.route('/bulk_import', methods=['GET', 'POST'])
@login_required
def bulk_import():
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({'success': False, 'error': 'No file uploaded'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No selected file'}), 400

            if not allowed_file(file.filename, file_type='import'):
                return jsonify({
                    'success': False,
                    'error': f'Invalid file type. Allowed types are: {", ".join(current_app.config["ALLOWED_IMPORT_EXTENSIONS"])}'
                }), 400

            try:
                column_mapping = json.loads(request.form.get('column_mapping', '{}'))
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    file.save(temp_file)
                    temp_path = temp_file.name

                try:
                    import_service = TransactionImportService()
                    results = import_service.process_import_file(temp_path, column_mapping, file.filename)

                    transactions_saved = 0
                    for transaction in results['successful_rows']:
                        if any(transaction.values()):
                            add_transaction(transaction)
                            transactions_saved += 1

                    return jsonify({
                        'success': True,
                        'redirect': url_for('transactions.view_transactions'),
                        'modifications': results.get('modifications', []),
                        'stats': {
                            'total_processed': results['stats']['processed_rows'],
                            'total_saved': transactions_saved,
                            'total_modified': results['stats'].get('modified_rows', 0)
                        }
                    })

                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            except json.JSONDecodeError as e:
                return jsonify({'success': False, 'error': 'Invalid column mapping format'}), 400

            except Exception as e:
                current_app.logger.error(f"Error processing file: {str(e)}")
                return jsonify({'success': False, 'error': f'Error processing file: {str(e)}'}), 500

        except Exception as e:
            current_app.logger.error(f"Unexpected error in bulk import: {str(e)}")
            return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

    return render_template('transactions/bulk_import.html', body_class='bulk-import-page')

def allowed_file(filename, file_type='documentation'):
    allowed_extensions = (current_app.config['ALLOWED_DOCUMENTATION_EXTENSIONS'] 
                          if file_type == 'documentation' 
                          else current_app.config['ALLOWED_IMPORT_EXTENSIONS'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def flash_import_results(results):
    flash_message('Import summary:', 'info')
    flash_message(f'Total rows in file: {results["total_rows"]}', 'info')
    flash_message(f'Successfully processed: {results["processed_rows"]}', 'info')
    flash_message(f'Successfully imported: {results["imported_count"]}', 'success')
    flash_message(f'Skipped rows: {results["skipped_rows"]}', 'warning')
    flash_message(f'  - Empty dates: {results["empty_dates"]}', 'warning')
    flash_message(f'  - Empty amounts: {results["empty_amounts"]}', 'warning')
    flash_message(f'  - Unmatched properties: {results["unmatched_properties"]}', 'warning')
    flash_message(f'  - Other issues: {results["other_issues"]}', 'warning')

@transactions_bp.route('/get_columns', methods=['POST'])
@login_required
def get_columns():
    if 'file' not in request.files:
        current_app.logger.error("No file part in request")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        current_app.logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename, file_type='import'):
        current_app.logger.error(f"File type not allowed: {file.filename}")
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        # Create temporary file with correct extension
        file_extension = file.filename.lower().split('.')[-1]
        
        with tempfile.NamedTemporaryFile(suffix=f'.{file_extension}', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
            
        try:
            # Use the service to read the file
            import_service = TransactionImportService()
            df = import_service.read_file(temp_path, file.filename)
            
            if df.empty:
                return jsonify({'error': 'No data found in file'}), 400
                
            columns = df.columns.tolist()
            return jsonify({'columns': columns})

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    current_app.logger.warning(f"Failed to remove temporary file {temp_path}: {str(e)}")

    except Exception as e:
        current_app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_transactions(transaction_id):
    try:
        # Get filter state from URL
        filters = request.args.get('filters', '{}')
        
        transaction = get_transaction_by_id(transaction_id)
        if not transaction:
            flash_message('Transaction not found', 'error')
            return redirect(url_for('transactions.view_transactions'))
        
        properties = get_properties_for_user(current_user.id, current_user.name, current_user.role == 'Admin')
        
        if request.method == 'POST':
            try:
                current_app.logger.info(f"Processing POST request to edit transaction ID: {transaction_id}")
                form_data = request.form.to_dict()
                current_app.logger.debug(f"Form data received: {form_data}")
                
                # Sanitize notes
                notes = sanitize_notes(form_data.get('notes', ''))
                
                # Create updated transaction dict
                updated_transaction = {
                    'id': transaction_id,
                    'property_id': form_data.get('property_id'),
                    'type': form_data.get('type'),
                    'category': form_data.get('category'),
                    'description': form_data.get('description'),
                    'amount': float(form_data.get('amount')),
                    'date': form_data.get('date'),
                    'collector_payer': form_data.get('collector_payer'),
                    'notes': notes,  # Add notes field
                    'reimbursement': {
                        'date_shared': form_data.get('date_shared'),
                        'share_description': form_data.get('share_description'),
                        'reimbursement_status': form_data.get('reimbursement_status'),
                        'documentation': None
                    }
                }

                # Check for document removal flags
                remove_transaction_doc = form_data.get('remove_transaction_documentation') == 'true'
                remove_reimbursement_doc = form_data.get('remove_reimbursement_documentation') == 'true'
                
                # Handle document removals and updates
                if remove_transaction_doc:
                    updated_transaction['documentation_file'] = None
                else:
                    updated_transaction['documentation_file'] = transaction.get('documentation_file')

                if remove_reimbursement_doc:
                    updated_transaction['reimbursement']['documentation'] = None
                else:
                    updated_transaction['reimbursement']['documentation'] = (
                        transaction.get('reimbursement', {}).get('documentation')
                    )

                # Handle new file uploads
                if 'documentation_file' in request.files:
                    file = request.files['documentation_file']
                    if file and file.filename:
                        if allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                            file.save(file_path)
                            updated_transaction['documentation_file'] = filename

                if 'reimbursement_documentation' in request.files:
                    file = request.files['reimbursement_documentation']
                    if file and file.filename:
                        if allowed_file(file.filename):
                            filename = f"reimb_{secure_filename(file.filename)}"
                            file_path = os.path.join(current_app.config['REIMBURSEMENTS_DIR'], filename)
                            file.save(file_path)
                            updated_transaction['reimbursement']['documentation'] = filename

                update_transaction(updated_transaction)
                
                return redirect(url_for('transactions.view_transactions') + 
                    f'?filters={filters}&message=Transaction updated successfully&message_type=success')

            except Exception as e:
                current_app.logger.error(f"Error updating transaction: {str(e)}")
                current_app.logger.error(f"Traceback: {traceback.format_exc()}")
                flash_message(f'Error updating transaction: {str(e)}', 'error')
                return redirect(url_for('transactions.edit_transactions', 
                    transaction_id=transaction_id, 
                    filters=filters))

        # GET request: render the edit form
        return render_template(
            'transactions/edit_transactions.html',
            transaction=transaction,
            properties=properties,
            filters=filters
        )

    except Exception as e:
        current_app.logger.error(f"Error in edit_transactions: {str(e)}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        flash_message(f'Error: {str(e)}', 'error')
        return redirect(url_for('transactions.view_transactions'))

@transactions_bp.route('/remove', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_transactions():
    if request.method == 'POST':
        # Handle the form submission for removing a transaction
        # This is where you'd process the request and remove the transaction from the database
        flash_message('Transaction removed successfully', 'success')
    # Render the template for removing transactions
    return render_template('transaction/remove_transactions.html')

@transactions_bp.route('/view/')
@login_required
def view_transactions():
    try:
        user_info = {
            'id': current_user.id,
            'name': current_user.name,
            'role': current_user.role,
            'is_authenticated': current_user.is_authenticated
        }
        current_app.logger.info(f"View transactions accessed by user: {user_info}")
        return render_template('transactions/view_transactions.html', show_bulk_import=True)
    except Exception as e:
        current_app.logger.error(f"Error in view_transactions: {str(e)}")
        flash_message(f"An error occurred while loading the transactions view: {str(e)}", "error")
        return redirect(url_for('main.index'))

@transactions_bp.route('/test')
def test_route():
    return "Transactions blueprint is working!"

@transactions_bp.route('/artifact/<path:filename>')
@login_required
def get_artifact(filename):
    current_app.logger.debug(f"Attempting to serve artifact: {filename}")
    
    try:
        # All files are now in one directory
        artifact_dir = current_app.config['UPLOAD_FOLDER']
        current_app.logger.debug(f"Looking for file in: {artifact_dir}")

        # Log the full path being attempted
        full_path = os.path.join(artifact_dir, filename)
        current_app.logger.debug(f"Attempting to serve file from: {full_path}")
        
        if not os.path.exists(full_path):
            current_app.logger.error(f"File not found: {full_path}")
            abort(404)

        return send_from_directory(
            artifact_dir, 
            filename, 
            as_attachment=False
        )
        
    except Exception as e:
        current_app.logger.error(f"Error serving artifact {filename}: {str(e)}")
        current_app.logger.error(f"Full error traceback: {traceback.format_exc()}")
        abort(404)

@transactions_bp.route('/api/partners')
@login_required
def get_property_partners():
    property_id = request.args.get('property_id')
    partners = get_partners_for_property(property_id)
    return jsonify(partners)

@transactions_bp.route('/debug/api-test')
@login_required
def debug_api_test():
    """Debug endpoint to test API responses"""
    try:
        # Test categories
        income_categories = get_categories('income')
        expense_categories = get_categories('expense')
        
        # Test partners
        properties = get_properties_for_user(current_user.id, current_user.name)
        test_property = properties[0] if properties else None
        partners = get_partners_for_property(test_property['address']) if test_property else []
        
        debug_info = {
            'categories': {
                'income': income_categories,
                'expense': expense_categories
            },
            'test_property': test_property,
            'partners': partners
        }
        
        return jsonify(debug_info)
    except Exception as e:
        current_app.logger.error(f"Debug API test error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transactions_bp.route('/delete/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    try:
        current_app.logger.debug(f"Delete endpoint called for transaction {transaction_id}")
        current_app.logger.debug(f"Current user: {current_user.name} (ID: {current_user.id})")
        
        # Get the transaction
        transaction = get_transaction_by_id(transaction_id)
        if not transaction:
            current_app.logger.error(f"Transaction {transaction_id} not found")
            return jsonify({'success': False, 'message': 'Transaction not found'}), 404
            
        current_app.logger.debug(f"Found transaction: {json.dumps(transaction, indent=2)}")
        
        # Get properties to verify property manager status
        properties = get_properties_for_user(current_user.id, current_user.name, current_user.role == 'Admin')
        
        # Check if user is property manager for this property
        property_data = next(
            (prop for prop in properties if prop['address'] == transaction['property_id']),
            None
        )
        
        if not property_data:
            current_app.logger.error(f"Property not found for transaction {transaction_id}")
            return jsonify({'success': False, 'message': 'Property not found'}), 404
            
        current_app.logger.debug(f"Found property data: {json.dumps(property_data, indent=2)}")
        
        is_property_manager = any(
            partner['name'] == current_user.name and 
            partner.get('is_property_manager', False)
            for partner in property_data.get('partners', [])
        )
        
        current_app.logger.debug(f"Is property manager: {is_property_manager}")
        current_app.logger.debug(f"Is admin: {current_user.role == 'Admin'}")
        
        if not is_property_manager and current_user.role != 'Admin':
            current_app.logger.error("User not authorized to delete transaction")
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        # Delete the transaction from the JSON file
        data_file = os.path.join(current_app.config['DATA_DIR'], 'transactions.json')
        current_app.logger.debug(f"Reading transactions from: {data_file}")
        
        with open(data_file, 'r') as f:
            transactions = json.load(f)
            
        current_app.logger.debug(f"Found {len(transactions)} transactions")
        original_count = len(transactions)
        
        # Filter out the transaction to delete - ensure IDs are compared as integers
        transactions = [t for t in transactions if int(t['id']) != int(transaction_id)]
        
        current_app.logger.debug(f"After filtering: {len(transactions)} transactions")
        if len(transactions) == original_count:
            current_app.logger.error(f"Transaction {transaction_id} was not filtered out")
            return jsonify({'success': False, 'message': 'Transaction not removed'}), 500
            
        # Write back to the file
        with open(data_file, 'w') as f:
            json.dump(transactions, f, indent=2)
            
        current_app.logger.info(f"Successfully deleted transaction {transaction_id}")
        
        # Delete associated files if they exist
        if transaction.get('documentation_file'):
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], transaction['documentation_file'])
            if os.path.exists(file_path):
                os.remove(file_path)
                current_app.logger.debug(f"Deleted documentation file: {file_path}")
                
        if transaction.get('reimbursement', {}).get('documentation'):
            reimb_file_path = os.path.join(
                current_app.config['REIMBURSEMENTS_DIR'], 
                transaction['reimbursement']['documentation']
            )
            if os.path.exists(reimb_file_path):
                os.remove(reimb_file_path)
                current_app.logger.debug(f"Deleted reimbursement file: {reimb_file_path}")
            
        return jsonify({'success': True, 'message': 'Transaction deleted successfully'}), 200
            
    except Exception as e:
        current_app.logger.error(f"Error deleting transaction: {str(e)}")
        current_app.logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Error deleting transaction: {str(e)}'}), 500