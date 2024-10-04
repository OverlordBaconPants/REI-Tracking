from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from services.transaction_service import add_transaction, get_transactions_for_user, get_unresolved_transactions, resolve_reimbursement, get_properties_for_user
import os
import logging

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    logging.debug("Entering add_transaction route")
    logging.info(f"Add transaction route accessed by user: {current_user.name} (ID: {current_user.id})")
    logging.info(f"User role: {current_user.role}")

    is_admin = current_user.role == 'Admin'
    properties = get_properties_for_user(current_user.id, current_user.name, is_admin)
    logging.info(f"Properties fetched for user: {len(properties)}")

    if request.method == 'POST':
        logging.info("Processing POST request for add_transaction")
        transaction_data = {
            'property_id': request.form['property_id'],
            'type': request.form['type'],
            'category': request.form['category'],
            'description': request.form['description'],
            'amount': float(request.form['amount']),
            'date': request.form['date'],
            'collector_payer': request.form['collector_payer'],
            'reimbursement': {
                'date_shared': request.form.get('date_shared'),
                'description': request.form.get('share_description')
            }
        }
        
        if 'documentation_file' in request.files:
            file = request.files['documentation_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                transaction_data['documentation_file'] = filename

        add_transaction(transaction_data)
        flash('Transaction added successfully', 'success')
        return redirect(url_for('main.transactions'))
    
    else:
        logging.info("Processing GET request for add_transaction")
        return render_template('main/add_transactions.html', properties=properties)
        
@transactions_bp.route('/reimbursements')
@login_required
def reimbursements():
    logging.info(f"Reimbursements route accessed by user: {current_user.id}")
    unresolved_transactions = get_unresolved_transactions()
    logging.info(f"Number of unresolved transactions: {len(unresolved_transactions)}")
    return render_template('transactions/reimbursements.html', transactions=unresolved_transactions)

@transactions_bp.route('/resolve_reimbursement/<transaction_id>', methods=['POST'])
@login_required
def resolve_reimbursement_route(transaction_id):
    logging.info(f"Resolve reimbursement route accessed by user: {current_user.id} for transaction: {transaction_id}")
    comment = request.form.get('comment')
    if resolve_reimbursement(transaction_id, comment):
        flash('Reimbursement resolved successfully', 'success')
    else:
        flash('Failed to resolve reimbursement', 'error')
    return redirect(url_for('transactions.reimbursements'))

@transactions_bp.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    logging.info(f"Uploaded file request for: {filename} by user: {current_user.id}")
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# You might want to add more routes here for other transaction-related functionalities

logging.info("transactions.py blueprint loaded")