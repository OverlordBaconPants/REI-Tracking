import json
import logging
from utils.json_handler import read_json, write_json
from flask import current_app
from datetime import datetime

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
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    transaction_data['id'] = str(len(transactions) + 1)  # Simple ID generation
    transaction_data['date'] = datetime.strptime(transaction_data['date'], '%Y-%m-%d').date().isoformat()
    transactions.append(transaction_data)
    write_json(current_app.config['TRANSACTIONS_FILE'], transactions)

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