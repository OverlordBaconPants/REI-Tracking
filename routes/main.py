# routes/main.py

# Keep routes that are accessible to all authenticated users 
# (Main, Properties, Transactions, Dashboards)

import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
import logging
import requests
from services.transaction_service import get_properties_for_user
from werkzeug.utils import secure_filename
import os
import json
from decimal import Decimal, InvalidOperation

main_bp = Blueprint('main', __name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/autocomplete')
def autocomplete():
    query = request.args.get('query', '')
    api_key = current_app.config['GEOAPIFY_API_KEY']
    url = f'https://api.geoapify.com/v1/geocode/autocomplete?text={query}&format=json&apiKey={api_key}'
    
    response = requests.get(url)
    data = response.json()
    
    suggestions = [
        {
            'formatted': result['formatted'],
            'lat': result['lat'],
            'lon': result['lon']
        }
        for result in data.get('results', [])
    ]
    return jsonify(suggestions)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/main')
@login_required
def main():
    return render_template('main/main.html', name=current_user.name)

@main_bp.route('/properties')
@login_required
def properties():
    return render_template('main/properties.html')

@main_bp.route('/transactions')
@login_required
def transactions():
    return render_template('main/transactions.html')

@main_bp.route('/add_transactions', methods=['GET', 'POST'])
@login_required
def add_transactions():
    if request.method == 'POST':
        try:
            transaction_data = {
                'id': str(uuid.uuid4()),
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

            # Load existing transactions
            transactions_file = current_app.config['TRANSACTIONS_FILE']
            try:
                with open(transactions_file, 'r') as file:
                    content = file.read()
                    transactions = json.loads(content) if content else []
            except json.JSONDecodeError:
                logging.error(f"Error decoding JSON from {transactions_file}. Initializing with empty list.")
                transactions = []
            except FileNotFoundError:
                logging.error(f"Transactions file not found. Creating a new file.")
                transactions = []

            # Add new transaction
            transactions.append(transaction_data)

            # Save updated transactions
            with open(transactions_file, 'w') as file:
                json.dump(transactions, file, indent=2)

            flash('Transaction added successfully', 'success')
            return redirect(url_for('main.transactions'))
        except Exception as e:
            logging.error(f"Error adding transaction: {str(e)}")
            flash(f'Error adding transaction: {str(e)}', 'danger')
    
    return render_template('main/add_transactions.html', properties=properties)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/dashboards')
@login_required
def dashboards():
    return render_template('main/dashboards.html')