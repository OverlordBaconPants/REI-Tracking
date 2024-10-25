import json
import logging
from utils.json_handler import read_json, write_json
from flask import current_app
from datetime import datetime
import pandas as pd
from fuzzywuzzy import process
import re

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

def get_categories(transaction_type):
    categories = read_json(current_app.config['CATEGORIES_FILE'])
    return categories.get(transaction_type, [])

def get_partners_for_property(property_id):
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    property_data = next((p for p in properties if p['address'] == property_id), None)
    if property_data:
        return property_data.get('partners', [])
    return []

def get_transactions_for_view(user_id, user_name, property_id=None, reimbursement_status=None, start_date=None, end_date=None, is_admin=False):
    current_app.logger.debug(f"get_transactions_for_view called with: user_id={user_id}, user_name={user_name}, property_id={property_id}, reimbursement_status={reimbursement_status}, start_date={start_date}, end_date={end_date}, is_admin={is_admin}")
    
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    
    current_app.logger.debug(f"All transactions: {transactions}")
    
    if is_admin:
        user_transactions = transactions
    else:
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
        # Ensure both documentation fields are included
        flat_t['documentation_file'] = t.get('documentation_file', '')
        flat_t['reimbursement_documentation'] = t.get('reimbursement', {}).get('documentation', '')
        flattened_transactions.append(flat_t)
    
    return flattened_transactions

def get_transaction_by_id(transaction_id):
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    return next((t for t in transactions if t['id'] == str(transaction_id)), None)

def update_transaction(updated_transaction):
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    for i, transaction in enumerate(transactions):
        if transaction['id'] == str(updated_transaction['id']):
            # Preserve the structure of the original transaction
            updated = {
                "property_id": updated_transaction['property_id'],
                "type": updated_transaction['type'],
                "category": updated_transaction['category'],
                "description": updated_transaction['description'],
                "amount": float(updated_transaction['amount']),
                "date": updated_transaction['date'],
                "collector_payer": updated_transaction['collector_payer'],
                "documentation_file": updated_transaction.get('documentation_file', transaction.get('documentation_file')),
                "id": str(updated_transaction['id']),
                "reimbursement": {
                    "date_shared": updated_transaction['reimbursement']['date_shared'],
                    "share_description": updated_transaction['reimbursement']['share_description'],
                    "reimbursement_status": updated_transaction['reimbursement']['reimbursement_status'],
                    "documentation": updated_transaction['reimbursement'].get('documentation', 
                                   transaction.get('reimbursement', {}).get('documentation'))
                }
            }
            transactions[i] = updated
            break
    else:
        raise ValueError(f"Transaction with id {updated_transaction['id']} not found")
    
    write_json(current_app.config['TRANSACTIONS_FILE'], transactions)

def process_bulk_import(file_path, column_mapping, properties):
    df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
    
    total_rows = len(df)
    skipped_rows = {'empty_date': 0, 'empty_amount': 0, 'unmatched_property': 0, 'other': 0}
    
    df['property_id'] = df[column_mapping['Property']].apply(lambda x: match_property(x, properties))
    df['collector_payer'] = df[column_mapping['Paid By']].apply(match_collector_payer)
    
    mapped_data = []
    for index, row in df.iterrows():
        try:
            amount, transaction_type = clean_amount(row[column_mapping['Amount']])
            date = parse_date(row[column_mapping['Date Received or Paid']])
            
            if date is None:
                skipped_rows['empty_date'] += 1
                continue
            
            if amount is None:
                skipped_rows['empty_amount'] += 1
                continue
            
            if pd.isna(row['property_id']):
                skipped_rows['unmatched_property'] += 1
                continue
            
            transaction = {
                'property_id': row['property_id'],
                'type': transaction_type,
                'category': row[column_mapping['Category']],
                'description': row[column_mapping['Item Description']],
                'amount': amount,
                'date': date,
                'collector_payer': row['collector_payer'],
                'documentation_file': '',
                'reimbursement': {
                    'date_shared': '',
                    'share_description': '',
                    'reimbursement_status': 'pending'
                }
            }
            
            mapped_data.append(transaction)
        
        except Exception as e:
            skipped_rows['other'] += 1
    
    imported_count = bulk_import_transactions(mapped_data)
    
    return {
        'total_rows': total_rows,
        'processed_rows': len(mapped_data),
        'imported_count': imported_count,
        'skipped_rows': sum(skipped_rows.values()),
        'empty_dates': skipped_rows['empty_date'],
        'empty_amounts': skipped_rows['empty_amount'],
        'unmatched_properties': skipped_rows['unmatched_property'],
        'other_issues': skipped_rows['other']
    }

def match_property(address, properties):
    if pd.isna(address):
        return None
    matches = process.extractOne(address, [p['address'] for p in properties])
    return matches[0] if matches and matches[1] >= 80 else None

def match_collector_payer(name):
    if pd.isna(name):
        return None
    # You might want to implement a more sophisticated matching here
    return name

def clean_amount(amount_str):
    if pd.isna(amount_str) or amount_str == '':
        return None, None
    cleaned = re.sub(r'[^\d.-]', '', str(amount_str))
    if not cleaned:
        return None, None
    try:
        amount = float(cleaned)
        transaction_type = 'expense' if amount < 0 else 'income'
        return abs(amount), transaction_type
    except ValueError:
        return None, None

def parse_date(date_str):
    if pd.isna(date_str) or date_str == '':
        return None
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None

def bulk_import_transactions(transactions):
    existing_transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    
    imported_count = 0
    for transaction in transactions:
        if not is_duplicate_transaction(transaction):
            transaction['id'] = str(len(existing_transactions) + 1)
            existing_transactions.append(transaction)
            imported_count += 1
    
    if imported_count > 0:
        write_json(current_app.config['TRANSACTIONS_FILE'], existing_transactions)
    
    return imported_count

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