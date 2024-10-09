import json
import logging
from utils.json_handler import read_json, write_json
from flask import current_app
from datetime import datetime, timedelta

def get_properties_for_user(user_id, user_name, is_admin=False):
    logging.debug(f"Getting properties for user: {user_name} (ID: {user_id}), is_admin: {is_admin}")
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    
    if is_admin:
        logging.info(f"Admin user, returning all {len(properties)} properties")
        return properties
    
    user_properties = [
        prop for prop in properties
        if any(partner.get('name').lower() == user_name.lower() for partner in prop.get('partners', []))
    ]
    
    logging.info(f"Found {len(user_properties)} properties for user {user_name}")
    return user_properties

def add_transaction(transaction_data):
    try:
        # Load existing transactions
        with open(current_app.config['TRANSACTIONS_FILE'], 'r') as f:
            transactions = json.load(f)
    except FileNotFoundError:
        transactions = []

    # Add a unique ID to the transaction
    transaction_data['id'] = str(len(transactions) + 1)

    # Append the new transaction
    transactions.append(transaction_data)

    # Save the updated transactions
    with open(current_app.config['TRANSACTIONS_FILE'], 'w') as f:
        json.dump(transactions, f, indent=2)

    return True

def is_duplicate_transaction(new_transaction):
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    
    # Convert the new transaction's date to a datetime object
    new_date = datetime.strptime(new_transaction['date'], '%Y-%m-%d').date()
    
    for transaction in transactions:
        # Check if the transaction is within 1 day of the new transaction
        transaction_date = datetime.strptime(transaction['date'], '%Y-%m-%d').date()
        date_difference = abs((new_date - transaction_date).days)
        
        # Add a small tolerance for amount comparison
        amount_difference = abs(float(transaction['amount']) - float(new_transaction['amount']))
        
        if (transaction['property_id'] == new_transaction['property_id'] and
            transaction['type'] == new_transaction['type'] and
            transaction['category'] == new_transaction['category'] and
            amount_difference < 0.01 and
            date_difference <= 1):
            
            logging.warning(f"Potential duplicate transaction detected:")
            logging.warning(f"Existing: {transaction}")
            logging.warning(f"New: {new_transaction}")
            return True
    
    return False

def get_transactions_for_user(user_id, property_id=None, start_date=None, end_date=None):
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    
    user_properties = [prop for prop in properties if any(partner['name'] == user_id for partner in prop.get('partners', []))]
    user_property_ids = [prop['address'] for prop in user_properties]
    
    filtered_transactions = [
        t for t in transactions
        if t['property_id'] in user_property_ids
        and (property_id is None or t['property_id'] == property_id)
        and (start_date is None or t['date'] >= start_date)
        and (end_date is None or t['date'] <= end_date)
    ]
    
    return filtered_transactions

def get_unresolved_transactions():
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    reimbursements = read_json(current_app.config['REIMBURSEMENTS_FILE'])
    
    resolved_transaction_ids = set(r['transaction_id'] for r in reimbursements)
    unresolved_transactions = [t for t in transactions if t['id'] not in resolved_transaction_ids]
    
    return unresolved_transactions

def resolve_reimbursement(transaction_id, comment):
    reimbursements = read_json(current_app.config['REIMBURSEMENTS_FILE'])
    reimbursement = {
        'transaction_id': transaction_id,
        'date_resolved': datetime.now().isoformat(),
        'comment': comment
    }
    reimbursements.append(reimbursement)
    write_json(current_app.config['REIMBURSEMENTS_FILE'], reimbursements)
    return True

def get_categories(transaction_type):
    categories = read_json(current_app.config['CATEGORIES_FILE'])
    return categories.get(transaction_type, [])

def get_partners_for_property(property_id):
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    property_data = next((p for p in properties if p['address'] == property_id), None)
    if property_data:
        return property_data.get('partners', [])
    return []

def get_transactions_for_view(user_id, user_name, property_id=None, reimbursement_status=None, start_date=None, end_date=None):
    current_app.logger.debug(f"get_transactions_for_view called with: user_id={user_id}, user_name={user_name}, property_id={property_id}, reimbursement_status={reimbursement_status}, start_date={start_date}, end_date={end_date}")
    
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    
    current_app.logger.debug(f"All transactions: {transactions}")
    
    # Get properties where the user is a partner
    user_properties = [
        prop['address'] for prop in properties
        if any(partner['name'].lower() == user_name.lower() for partner in prop.get('partners', []))
    ]
    
    current_app.logger.debug(f"User properties: {user_properties}")
    
    # Filter transactions based on user's properties
    user_transactions = [t for t in transactions if t.get('property_id') in user_properties]
    
    current_app.logger.debug(f"User transactions: {user_transactions}")
    
    # Apply additional filters
    if property_id and property_id != 'all':
        user_transactions = [t for t in user_transactions if t.get('property_id') == property_id]
    
    if reimbursement_status and reimbursement_status != 'all':
        user_transactions = [t for t in user_transactions if t.get('reimbursement', {}).get('reimbursement_status') == reimbursement_status]
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        user_transactions = [t for t in user_transactions if datetime.strptime(t.get('date'), '%Y-%m-%d').date() >= start_date]
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        user_transactions = [t for t in user_transactions if datetime.strptime(t.get('date'), '%Y-%m-%d').date() <= end_date]
    
    current_app.logger.debug(f"Filtered transactions: {user_transactions}")
    
    # Flatten the structure for easier handling in the DataFrame
    flattened_transactions = []
    for t in user_transactions:
        flat_t = t.copy()
        flat_t.update(t.get('reimbursement', {}))
        flattened_transactions.append(flat_t)
    
    return flattened_transactions