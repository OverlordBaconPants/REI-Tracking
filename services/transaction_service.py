import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any

import pandas as pd
from flask import current_app
from fuzzywuzzy import process

from utils.json_handler import read_json, write_json


logger = logging.getLogger(__name__)


def format_address(address: str, format_type: str = 'full') -> Union[str, Tuple[str, str]]:
    """
    Multi-purpose address formatter that handles different format requirements.
    
    Args:
        address (str): Full property address
        format_type (str): Type of formatting needed:
            - 'display': Returns just house number and street (e.g., "1714 Miller")
            - 'base': Same as 'display' for consistency
            - 'full': Returns tuple of (display_address, full_address)
            
    Returns:
        Union[str, Tuple[str, str]]: Formatted address in requested format
    """
    if not address:
        return ("", "") if format_type == 'full' else ""
        
    parts = [p.strip() for p in address.split(',')]
    street_address = parts[0].strip()
    
    if format_type in ['display', 'base']:
        return street_address
        
    return (street_address, address)


def get_properties_for_user(user_id: str, user_name: str, is_admin: bool = False) -> List[Dict]:
    """
    Get properties for a user with formatted addresses.
    
    Args:
        user_id (str): ID of the user
        user_name (str): Name of the user
        is_admin (bool): Whether the user is an admin
        
    Returns:
        List[Dict]: List of properties accessible by the user
    """
    logger.debug(f"Getting properties for user: {user_name} (ID: {user_id}), is_admin: {is_admin}")
    
    try:
        properties = read_json(current_app.config['PROPERTIES_FILE'])
        logger.debug(f"Read {len(properties)} properties")
        
        if not is_admin:
            properties = _filter_properties_by_user(properties, user_name)
            logger.debug(f"Found {len(properties)} properties for user {user_name}")
        else:
            logger.info(f"Admin user, returning all {len(properties)} properties")
        
        return _format_property_addresses(properties)
        
    except Exception as e:
        logger.error(f"Error in get_properties_for_user: {str(e)}", exc_info=True)
        raise


def _filter_properties_by_user(properties: List[Dict], user_name: str) -> List[Dict]:
    """Filter properties by user name."""
    return [
        prop for prop in properties
        if any(partner.get('name', '').lower() == user_name.lower() 
              for partner in prop.get('partners', []))
    ]


def _format_property_addresses(properties: List[Dict]) -> List[Dict]:
    """Format addresses for all properties."""
    for prop in properties:
        if prop.get('address'):
            display_address, full_address = format_address(prop['address'], 'full')
            prop['display_address'] = display_address
            prop['full_address'] = full_address
    
    return properties


def add_transaction(transaction_data: Dict) -> str:
    """
    Add a new transaction with consistent data structure.
    
    Args:
        transaction_data (Dict): The transaction data to add
        
    Returns:
        str: The ID of the newly created transaction
    """
    try:
        transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
        
        # Find the highest existing ID
        highest_id = _get_highest_transaction_id(transactions)
        new_id = str(highest_id + 1)
        
        # Prepare transaction with defaults
        transaction_data['id'] = new_id
        complete_transaction = _prepare_transaction_with_defaults(transaction_data)

        # Log and save
        logger.debug(f"Final transaction structure: {json.dumps(complete_transaction, indent=2)}")
        transactions.append(complete_transaction)
        write_json(current_app.config['TRANSACTIONS_FILE'], transactions)
        
        logger.info(f"Successfully added transaction with ID: {new_id}")
        return new_id

    except Exception as e:
        logger.error(f"Error in add_transaction: {str(e)}", exc_info=True)
        raise


def _get_highest_transaction_id(transactions: List[Dict]) -> int:
    """Get the highest transaction ID from the list."""
    highest_id = 0
    for transaction in transactions:
        try:
            current_id = int(transaction.get('id', 0))
            highest_id = max(highest_id, current_id)
        except (ValueError, TypeError):
            logger.warning(f"Invalid ID format found: {transaction.get('id')}")
    return highest_id


def _prepare_transaction_with_defaults(transaction_data: Dict) -> Dict:
    """Prepare a transaction with default values for optional fields."""
    transaction = transaction_data.copy()
    
    # Set defaults for top-level fields
    transaction.setdefault('notes', '')
    transaction.setdefault('documentation_file', '')
    
    # Set defaults for reimbursement sub-dictionary
    transaction.setdefault('reimbursement', {})
    reimbursement = transaction['reimbursement']
    reimbursement.setdefault('date_shared', '')
    reimbursement.setdefault('share_description', '')
    reimbursement.setdefault('reimbursement_status', 'pending')
    reimbursement.setdefault('documentation', None)
    
    return transaction


def get_unresolved_transactions() -> List[Dict]:
    """Get transactions that don't have a corresponding reimbursement."""
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    reimbursements = read_json(current_app.config['REIMBURSEMENTS_FILE'])
    
    resolved_transaction_ids = set(r['transaction_id'] for r in reimbursements)
    return [t for t in transactions if t['id'] not in resolved_transaction_ids]


def get_categories(transaction_type: str) -> List[str]:
    """Get categories for a specific transaction type."""
    categories = read_json(current_app.config['CATEGORIES_FILE'])
    return categories.get(transaction_type, [])


def get_partners_for_property(property_id: str) -> List[Dict]:
    """Get partners for a specific property."""
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    property_data = next((p for p in properties if p['address'] == property_id), None)
    return property_data.get('partners', []) if property_data else []


def get_transactions_for_view(
    user_id: str, 
    user_name: str, 
    property_id: Optional[str] = None, 
    reimbursement_status: Optional[str] = None,
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    is_admin: bool = False
) -> List[Dict]:
    """
    Get filtered transactions with consistent address handling.
    
    Args:
        user_id (str): ID of the user
        user_name (str): Name of the user
        property_id (Optional[str]): Property ID filter
        reimbursement_status (Optional[str]): Reimbursement status filter
        start_date (Optional[str]): Start date for filtering (YYYY-MM-DD)
        end_date (Optional[str]): End date for filtering (YYYY-MM-DD)
        is_admin (bool): Whether the user is an admin
        
    Returns:
        List[Dict]: Filtered and flattened transactions
    """
    logger.debug(
        f"get_transactions_for_view called with property_id: {property_id}, "
        f"reimbursement_status: {reimbursement_status}"
    )
    
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    properties = read_json(current_app.config['PROPERTIES_FILE'])
    
    # Apply filters
    transactions = _filter_transactions_by_user_access(
        transactions, properties, user_name, is_admin
    )
    
    if property_id and property_id != 'all':
        transactions = _filter_transactions_by_property(transactions, property_id)
        
    if reimbursement_status and reimbursement_status != 'all':
        transactions = _filter_transactions_by_reimbursement_status(
            transactions, properties, user_name, reimbursement_status
        )
    
    if start_date or end_date:
        transactions = filter_by_date_range(transactions, start_date, end_date)
    
    # Set status for wholly-owned properties
    transactions = _update_wholly_owned_status(transactions, properties, user_name)
    
    # Flatten for display
    return [flatten_transaction(t) for t in transactions]


def _filter_transactions_by_user_access(
    transactions: List[Dict], 
    properties: List[Dict], 
    user_name: str, 
    is_admin: bool
) -> List[Dict]:
    """Filter transactions based on user access."""
    if is_admin:
        return transactions
        
    user_properties = [
        prop['address'] for prop in properties
        if any(partner['name'].lower() == user_name.lower() 
              for partner in prop.get('partners', []))
    ]
    
    return [t for t in transactions if t.get('property_id') in user_properties]


def _filter_transactions_by_property(transactions: List[Dict], property_id: str) -> List[Dict]:
    """Filter transactions by property ID using base address matching."""
    filter_base = format_address(property_id, 'base')
    logger.debug(f"Filtering with base address: {filter_base}")
    
    filtered = [
        t for t in transactions
        if format_address(t.get('property_id', ''), 'base') == filter_base
    ]
    
    logger.debug(f"After property filter: {len(filtered)} transactions")
    return filtered


def _filter_transactions_by_reimbursement_status(
    transactions: List[Dict], 
    properties: List[Dict], 
    user_name: str, 
    status: str
) -> List[Dict]:
    """Filter transactions by reimbursement status."""
    filtered_transactions = []
    
    for transaction in transactions:
        property_data = next(
            (p for p in properties if p['address'] == transaction.get('property_id')), 
            None
        )
        
        # For wholly-owned properties, set status to 'completed'
        if property_data and is_wholly_owned_property(property_data, user_name):
            if status == 'completed':
                filtered_transactions.append(transaction)
        else:
            # For shared properties, check actual status
            t_status = transaction.get('reimbursement', {}).get('reimbursement_status')
            if t_status == status:
                filtered_transactions.append(transaction)
    
    logger.debug(f"After reimbursement status filter: {len(filtered_transactions)} transactions")
    return filtered_transactions


def _update_wholly_owned_status(
    transactions: List[Dict], 
    properties: List[Dict], 
    user_name: str
) -> List[Dict]:
    """Update reimbursement status for wholly-owned properties."""
    for transaction in transactions:
        property_data = next(
            (p for p in properties if p['address'] == transaction.get('property_id')), 
            None
        )
        
        if property_data and is_wholly_owned_property(property_data, user_name):
            if 'reimbursement' not in transaction:
                transaction['reimbursement'] = {}
            transaction['reimbursement']['reimbursement_status'] = 'completed'
    
    return transactions


def flatten_transaction(transaction: Dict) -> Dict:
    """
    Flatten a transaction dictionary for display.
    
    Args:
        transaction (Dict): Transaction to flatten
        
    Returns:
        Dict: Flattened transaction
    """
    flat_t = transaction.copy()
    
    # Add reimbursement fields at top level
    flat_t.update(transaction.get('reimbursement', {}))
    
    # Ensure documentation fields exist
    flat_t['documentation_file'] = transaction.get('documentation_file', '')
    flat_t['reimbursement_documentation'] = (
        transaction.get('reimbursement', {}).get('documentation', '')
    )
    
    return flat_t


def filter_by_date_range(
    transactions: List[Dict], 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> List[Dict]:
    """
    Filter transactions by date range.
    
    Args:
        transactions (List[Dict]): Transactions to filter
        start_date (Optional[str]): Start date in YYYY-MM-DD format
        end_date (Optional[str]): End date in YYYY-MM-DD format
        
    Returns:
        List[Dict]: Filtered transactions
    """
    if not transactions:
        return []
    
    filtered = transactions.copy()
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        filtered = [
            t for t in filtered 
            if datetime.strptime(t.get('date'), '%Y-%m-%d').date() >= start
        ]
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        filtered = [
            t for t in filtered 
            if datetime.strptime(t.get('date'), '%Y-%m-%d').date() <= end
        ]
    
    return filtered


def get_transaction_by_id(transaction_id: str) -> Optional[Dict]:
    """Get a transaction by its ID."""
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    return next((t for t in transactions if t['id'] == str(transaction_id)), None)


def update_transaction(updated_transaction: Dict) -> None:
    """
    Update a transaction with detailed logging.
    
    Args:
        updated_transaction (Dict): Updated transaction data
    """
    logger.info("=== Starting transaction update ===")
    logger.debug(f"Received transaction data: {json.dumps(updated_transaction, indent=2)}")
    
    transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    logger.debug(f"Loaded {len(transactions)} transactions from file")
    
    transaction_id = str(updated_transaction['id'])
    
    for i, transaction in enumerate(transactions):
        if transaction['id'] == transaction_id:
            logger.info(f"Found transaction to update at index {i}")
            logger.debug(f"Original transaction data: {json.dumps(transaction, indent=2)}")
            
            # Create updated transaction
            updated = _create_updated_transaction(transaction, updated_transaction)
            
            logger.debug(f"Final updated transaction: {json.dumps(updated, indent=2)}")
            transactions[i] = updated
            break
    else:
        error_msg = f"Transaction with id {transaction_id} not found"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Writing updated transactions to file")
    write_json(current_app.config['TRANSACTIONS_FILE'], transactions)
    logger.info("=== Transaction update completed ===")


def _create_updated_transaction(original: Dict, updates: Dict) -> Dict:
    """Create an updated transaction by merging original and updates."""
    # Base transaction fields
    updated = {
        "id": str(updates['id']),
        "property_id": updates['property_id'],
        "type": updates['type'],
        "category": updates['category'],
        "description": updates['description'],
        "amount": float(updates['amount']),
        "date": updates['date'],
        "collector_payer": updates['collector_payer'],
        "documentation_file": updates.get('documentation_file', original.get('documentation_file', '')),
        "notes": updates.get('notes', original.get('notes', ''))
    }
    
    # Handle reimbursement
    if updates.get('reimbursement'):
        logger.debug(f"Handling reimbursement data: {json.dumps(updates['reimbursement'], indent=2)}")
        
        # Keep existing documentation if not being updated or removed
        existing_documentation = (
            original.get('reimbursement', {}).get('documentation')
            if not updates.get('remove_reimbursement_documentation')
            else None
        )
        
        updated['reimbursement'] = {
            "date_shared": updates['reimbursement'].get('date_shared', ''),
            "share_description": updates['reimbursement'].get('share_description', ''),
            "reimbursement_status": updates['reimbursement'].get('reimbursement_status', 'pending'),
            "documentation": (
                updates['reimbursement'].get('documentation') or 
                existing_documentation
            )
        }
    else:
        # Preserve existing reimbursement data if none provided
        updated['reimbursement'] = original.get('reimbursement', {})
        
    return updated


def process_bulk_import(file_path: str, column_mapping: Dict[str, str], properties: List[Dict]) -> Dict:
    """
    Process bulk import of transactions from file.
    
    Args:
        file_path (str): Path to the file to import
        column_mapping (Dict[str, str]): Mapping of file columns to transaction fields
        properties (List[Dict]): List of properties
        
    Returns:
        Dict: Import statistics
    """
    # Read file
    if file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    
    total_rows = len(df)
    skipped_rows = {'empty_date': 0, 'empty_amount': 0, 'unmatched_property': 0, 'other': 0}
    
    # Match properties
    df['property_id'] = df[column_mapping['Property']].apply(
        lambda address: _find_matching_property(address, properties)
    )
    
    # Fill in payer
    df['collector_payer'] = df[column_mapping['Paid By']].fillna('')
    
    # Process rows
    mapped_data = []
    for index, row in df.iterrows():
        try:
            # Process amount and date
            amount, transaction_type = clean_amount(row[column_mapping['Amount']])
            date = parse_date(row[column_mapping['Date Received or Paid']])
            
            # Skip invalid rows
            if date is None:
                skipped_rows['empty_date'] += 1
                continue
            
            if amount is None:
                skipped_rows['empty_amount'] += 1
                continue
            
            if pd.isna(row['property_id']):
                skipped_rows['unmatched_property'] += 1
                continue
            
            # Create transaction
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
            logger.error(f"Error processing row {index}: {str(e)}")
    
    # Import transactions
    imported_count = bulk_import_transactions(mapped_data)
    
    # Return statistics
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


def _find_matching_property(address: Any, properties: List[Dict]) -> Optional[str]:
    """Find a matching property using fuzzy matching."""
    if pd.isna(address):
        return None
        
    # Use base address format for matching
    address_base = format_address(str(address), 'base')
    property_bases = {
        format_address(p['address'], 'base'): p['address'] 
        for p in properties
    }
    
    # Use fuzzywuzzy for approximate matching
    matches = process.extractOne(address_base, list(property_bases.keys()))
    if matches and matches[1] >= 80:  # 80% match threshold
        return property_bases[matches[0]]
        
    return None


def clean_amount(amount_str: Any) -> Tuple[Optional[float], Optional[str]]:
    """
    Clean amount string and determine transaction type.
    
    Args:
        amount_str (Any): Amount string to clean
        
    Returns:
        Tuple[Optional[float], Optional[str]]: (amount, transaction_type)
    """
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


def parse_date(date_str: Any) -> Optional[str]:
    """
    Parse date from string in various formats.
    
    Args:
        date_str (Any): Date string to parse
        
    Returns:
        Optional[str]: Parsed date in YYYY-MM-DD format
    """
    if pd.isna(date_str) or date_str == '':
        return None
        
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'):
        try:
            return datetime.strptime(str(date_str), fmt).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            pass
            
    return None


def bulk_import_transactions(transactions: List[Dict]) -> int:
    """
    Import multiple transactions, avoiding duplicates.
    
    Args:
        transactions (List[Dict]): Transactions to import
        
    Returns:
        int: Number of transactions imported
    """
    existing_transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    
    imported_count = 0
    highest_id = _get_highest_transaction_id(existing_transactions)
    
    for transaction in transactions:
        if not is_duplicate_transaction(transaction, existing_transactions):
            transaction['id'] = str(highest_id + imported_count + 1)
            existing_transactions.append(transaction)
            imported_count += 1
    
    if imported_count > 0:
        write_json(current_app.config['TRANSACTIONS_FILE'], existing_transactions)
    
    return imported_count


def is_wholly_owned_property(property_data: Dict, user_name: str) -> bool:
    """
    Check if a property is wholly owned by a user.
    
    Args:
        property_data (Dict): Property data
        user_name (str): Name of the user
        
    Returns:
        bool: True if the property is wholly owned by the user
    """
    partners = property_data.get('partners', [])
    
    if len(partners) == 1:
        partner = partners[0]
        is_user = partner.get('name', '').lower() == user_name.lower()
        equity = float(partner.get('equity_share', 0))
        return is_user and abs(equity - 100.0) < 0.01
        
    return False


def is_duplicate_transaction(
    new_transaction: Dict, 
    existing_transactions: Optional[List[Dict]] = None
) -> bool:
    """
    Check if a transaction is a duplicate of an existing transaction.
    
    Args:
        new_transaction (Dict): Transaction to check
        existing_transactions (Optional[List[Dict]]): Existing transactions
        
    Returns:
        bool: True if the transaction is a duplicate
    """
    if existing_transactions is None:
        existing_transactions = read_json(current_app.config['TRANSACTIONS_FILE'])
    
    # Convert the new transaction's date to a datetime object
    new_date = datetime.strptime(new_transaction['date'], '%Y-%m-%d').date()
    
    for transaction in existing_transactions:
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
            
            logger.warning(f"Potential duplicate transaction detected:")
            logger.warning(f"Existing: {transaction}")
            logger.warning(f"New: {new_transaction}")
            return True
    
    return False