import json
import logging
from utils.json_handler import read_json, write_json
from flask import current_app
from datetime import datetime
import pandas as pd
import traceback
from fuzzywuzzy import process
import re

def format_address(address: str, format_type: str = 'full') -> str | tuple[str, str]:
    """
    Multi-purpose address formatter that handles different format requirements.
    
    Args:
        address (str): Full property address
        format_type (str): Type of formatting needed:
            - 'display': Returns just the street address (before first comma)
            - 'base': Returns street address and city (before second comma)
            - 'full': Returns tuple of (display_address, full_address)
            
    Returns:
        Union[str, tuple[str, str]]: Formatted address in requested format
    """
    if not address:
        return ("", "") if format_type == 'full' else ""
        
    parts = [p.strip() for p in address.split(',')]
    
    if format_type == 'display':
        return parts[0]
    elif format_type == 'base':
        return ', '.join(parts[:2]) if len(parts) >= 2 else parts[0]
    else:  # 'full'
        return (parts[0], address)

def get_properties_for_user(user_id, user_name, is_admin=False):
    """Get properties for a user with formatted addresses."""
    logging.debug(f"Getting properties for user: {user_name} (ID: {user_id}), is_admin: {is_admin}")
    
    try:
        properties = read_json(current_app.config['PROPERTIES_FILE'])
        logging.debug(f"Read {len(properties)} properties")
        
        if not is_admin:
            properties = [
                prop for prop in properties
                if any(partner.get('name', '').lower() == user_name.lower() 
                      for partner in prop.get('partners', []))
            ]
            logging.debug(f"Found {len(properties)} properties for user {user_name}")
        else:
            logging.info(f"Admin user, returning all {len(properties)} properties")
        
        # Format addresses consistently for all properties
        for prop in properties:
            if prop.get('address'):
                display_address, full_address = format_address(prop['address'], 'full')
                prop['display_address'] = display_address
                prop['full_address'] = full_address
        
        logging.debug(f"Formatted properties: {properties}")
        return properties
        
    except Exception as e:
        logging.error(f"Error in get_properties_for_user: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def add_transaction(transaction_data):
    """
    Add a new transaction with consistent data structure.
    
    Args:
        transaction_data (dict): The transaction data to add
        
    Returns:
        str: The ID of the newly created transaction
    """
    try:
        # Load existing transactions
        transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
        
        # Find the highest existing ID
        highest_id = 0
        for transaction in transactions:
            try:
                current_id = int(transaction.get('id', 0))
                highest_id = max(highest_id, current_id)
            except (ValueError, TypeError):
                current_app.logger.warning(f"Invalid ID format found: {transaction.get('id')}")
                continue

        # Generate new ID
        new_id = str(highest_id + 1)
        
        # Update transaction data with new ID
        transaction_data['id'] = new_id
        
        # Ensure proper structure for optional fields
        transaction_data.setdefault('notes', '')
        transaction_data.setdefault('documentation_file', '')
        transaction_data.setdefault('reimbursement', {})
        transaction_data['reimbursement'].setdefault('date_shared', '')
        transaction_data['reimbursement'].setdefault('share_description', '')
        transaction_data['reimbursement'].setdefault('reimbursement_status', 'pending')
        transaction_data['reimbursement'].setdefault('documentation', None)

        # Log the final structure before saving
        current_app.logger.debug(f"Final transaction structure: {json.dumps(transaction_data, indent=2)}")

        # Append and save
        transactions.append(transaction_data)
        write_json(current_app.config['TRANSACTIONS_FILE'], transactions)
        
        current_app.logger.info(f"Successfully added transaction with ID: {new_id}")
        return new_id

    except Exception as e:
        current_app.logger.error(f"Error in add_transaction: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise

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

def get_transactions_for_view(user_id, user_name, property_id=None, reimbursement_status=None, 
                            start_date=None, end_date=None, is_admin=False):
    """Get filtered transactions with consistent address handling."""
    current_app.logger.debug(f"get_transactions_for_view called with property_id: {property_id}")
    
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    
    # Filter by user access
    if not is_admin:
        user_properties = [
            prop['address'] for prop in properties
            if any(partner['name'].lower() == user_name.lower() 
                  for partner in prop.get('partners', []))
        ]
        transactions = [t for t in transactions if t.get('property_id') in user_properties]
    
    # Apply property filter using base address matching
    if property_id and property_id != 'all':
        filter_base = format_address(property_id, 'base')
        current_app.logger.debug(f"Filtering with base address: {filter_base}")
        
        transactions = [
            t for t in transactions
            if format_address(t.get('property_id', ''), 'base') == filter_base
        ]
        current_app.logger.debug(f"After property filter: {len(transactions)} transactions")
    
    # Apply remaining filters
    if reimbursement_status and reimbursement_status != 'all':
        transactions = [
            t for t in transactions 
            if t.get('reimbursement', {}).get('reimbursement_status') == reimbursement_status
        ]
    
    # Apply date filters
    if start_date or end_date:
        transactions = filter_by_date_range(transactions, start_date, end_date)
    
    # Flatten and return transactions
    return [flatten_transaction(t) for t in transactions]

def flatten_transaction(transaction: dict) -> dict:
    """Flatten a transaction dictionary for display."""
    flat_t = transaction.copy()
    flat_t.update(transaction.get('reimbursement', {}))
    flat_t['documentation_file'] = transaction.get('documentation_file', '')
    flat_t['reimbursement_documentation'] = (
        transaction.get('reimbursement', {}).get('documentation', '')
    )
    return flat_t

def filter_by_date_range(transactions, start_date=None, end_date=None):
    """Filter transactions by date range."""
    if not transactions:
        return []
        
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        transactions = [
            t for t in transactions 
            if datetime.strptime(t.get('date'), '%Y-%m-%d').date() >= start
        ]
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        transactions = [
            t for t in transactions 
            if datetime.strptime(t.get('date'), '%Y-%m-%d').date() <= end
        ]
    
    return transactions

def get_transaction_by_id(transaction_id):
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    return next((t for t in transactions if t['id'] == str(transaction_id)), None)

def update_transaction(updated_transaction):
    """Update a transaction with detailed logging."""
    current_app.logger.info("=== Starting transaction update ===")
    current_app.logger.debug(f"Received transaction data: {json.dumps(updated_transaction, indent=2)}")
    
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    current_app.logger.debug(f"Loaded {len(transactions)} transactions from file")
    
    for i, transaction in enumerate(transactions):
        if transaction['id'] == str(updated_transaction['id']):
            current_app.logger.info(f"Found transaction to update at index {i}")
            current_app.logger.debug(f"Original transaction data: {json.dumps(transaction, indent=2)}")
            
            # Create base transaction
            updated = {
                "id": str(updated_transaction['id']),
                "property_id": updated_transaction['property_id'],
                "type": updated_transaction['type'],
                "category": updated_transaction['category'],
                "description": updated_transaction['description'],
                "amount": float(updated_transaction['amount']),
                "date": updated_transaction['date'],
                "collector_payer": updated_transaction['collector_payer'],
                "documentation_file": updated_transaction.get('documentation_file', transaction.get('documentation_file')),
                "notes": updated_transaction.get('notes', transaction.get('notes', ''))
            }
            
            # Handle reimbursement
            if updated_transaction.get('reimbursement'):
                current_app.logger.debug(f"Handling reimbursement data: {json.dumps(updated_transaction['reimbursement'], indent=2)}")
                
                # Keep existing documentation if not being updated or removed
                existing_documentation = (
                    transaction.get('reimbursement', {}).get('documentation')
                    if not updated_transaction.get('remove_reimbursement_documentation')
                    else None
                )
                
                updated['reimbursement'] = {
                    "date_shared": updated_transaction['reimbursement'].get('date_shared', ''),
                    "share_description": updated_transaction['reimbursement'].get('share_description', ''),
                    "reimbursement_status": updated_transaction['reimbursement'].get('reimbursement_status', 'pending'),
                    "documentation": (
                        updated_transaction['reimbursement'].get('documentation') or 
                        existing_documentation
                    )
                }
            else:
                # Preserve existing reimbursement data if none provided
                updated['reimbursement'] = transaction.get('reimbursement', {})
            
            current_app.logger.debug(f"Final updated transaction: {json.dumps(updated, indent=2)}")
            transactions[i] = updated
            break
    else:
        error_msg = f"Transaction with id {updated_transaction['id']} not found"
        current_app.logger.error(error_msg)
        raise ValueError(error_msg)
    
    current_app.logger.info("Writing updated transactions to file")
    write_json(current_app.config['TRANSACTIONS_FILE'], transactions)
    current_app.logger.info("=== Transaction update completed ===")

def process_bulk_import(file_path, column_mapping, properties):
    """Process bulk import of transactions from file."""
    df = pd.read_excel(file_path) if file_path.endswith(('.xlsx', '.xls')) else pd.read_csv(file_path)
    
    total_rows = len(df)
    skipped_rows = {'empty_date': 0, 'empty_amount': 0, 'unmatched_property': 0, 'other': 0}
    
    # Use fuzzy matching for property matching instead of separate function
    def find_matching_property(address):
        if pd.isna(address):
            return None
        # Use base address format for matching
        address_base = format_address(str(address), 'base')
        property_bases = {format_address(p['address'], 'base'): p['address'] 
                         for p in properties}
        
        # Use fuzzywuzzy for approximate matching
        matches = process.extractOne(address_base, list(property_bases.keys()))
        if matches and matches[1] >= 80:  # 80% match threshold
            return property_bases[matches[0]]
        return None
    
    df['property_id'] = df[column_mapping['Property']].apply(find_matching_property)
    df['collector_payer'] = df[column_mapping['Paid By']].fillna('')
    
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
            logging.error(f"Error processing row {index}: {str(e)}")
    
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