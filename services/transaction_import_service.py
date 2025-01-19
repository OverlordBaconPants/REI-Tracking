# transaction_import_service.py
from typing import Dict, List, Tuple, Any
import pandas as pd
import logging
from datetime import datetime
import tempfile
import os
import json

logger = logging.getLogger(__name__)

class TransactionImportService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def read_file(self, file_path: str, original_filename: str) -> pd.DataFrame:
        """
        Read CSV or Excel file into DataFrame
        
        Args:
            file_path: Path to temporary file
            original_filename: Original filename to determine type
            
        Returns:
            pd.DataFrame: DataFrame containing file contents
        """
        try:
            if original_filename.lower().endswith('.csv'):
                # Try different encodings for CSV
                encodings = ['utf-8', 'latin1', 'cp1252']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        self.logger.error(f"Error reading CSV with {encoding}: {str(e)}")
                        raise
            else:
                # Handle Excel files
                df = pd.read_excel(file_path)
                
            # Clean up column names
            df.columns = df.columns.str.strip()
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error reading file: {str(e)}")
            raise

    def normalize_date(self, date_value: Any) -> str:
        """
        Normalize date to YYYY-MM-DD format
        
        Args:
            date_value: Input date in any format
            
        Returns:
            str: Normalized date string or None
        """
        if pd.isna(date_value):
            return None
            
        try:
            # Convert to pandas timestamp
            ts = pd.to_datetime(date_value)
            return ts.strftime('%Y-%m-%d')
        except:
            return None
        
    def load_categories(self) -> None:
        try:
            with open(current_app.config['CATEGORIES_FILE'], 'r') as f:
                self.categories = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading categories: {str(e)}")
            self.categories = {"income": [], "expense": []}

    def validate_and_transform_row(self, row: Dict[str, Any], row_number: int) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
        modifications = []
        
        # Initialize with schema structure and null values
        transformed_row = {
            "property_id": None,
            "type": None,
            "category": None,
            "description": None,
            "amount": None,
            "date": None,
            "collector_payer": None,
            "notes": None,
            "documentation_file": None,
            "reimbursement": {
                "date_shared": None,
                "share_description": "Auto-completed - Single owner property",
                "reimbursement_status": "completed",
                "documentation": None
            }
        }
        
        # Property ID
        if 'Property' in row and row['Property']:
            transformed_row['property_id'] = str(row['Property']).strip()
        
        # Transaction Type
        trans_type = str(row.get('Transaction Type', '')).strip().lower()
        if trans_type:
            if trans_type not in ['income', 'expense']:
                modifications.append({
                    'row': row_number,
                    'field': 'Transaction Type',
                    'message': f"Invalid Transaction Type '{trans_type}' was removed"
                })
            else:
                transformed_row['type'] = trans_type
        
        # Category
        category = str(row.get('Category', '')).strip()
        if category:
            valid_categories = self.categories.get(trans_type, []) if trans_type else []
            if category not in valid_categories:
                modifications.append({
                    'row': row_number,
                    'message': f"Invalid Category '{category}' was removed"
                })
            else:
                transformed_row['category'] = category

        # Description/Item Description
        if 'Item Description' in row and row['Item Description']:
            transformed_row['description'] = str(row['Item Description']).strip()

        # Amount
        amount = row.get('Amount', '')
        if amount:
            try:
                cleaned_amount = str(amount).replace('$', '').replace(',', '')
                transformed_row['amount'] = float(cleaned_amount)
            except ValueError:
                modifications.append({
                    'row': row_number,
                    'message': f"Invalid Amount '{amount}' was removed"
                })

        # Date
        date_str = row.get('Date Received or Paid', '')
        if date_str:
            try:
                if isinstance(date_str, str):
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                else:  # Handle Excel date objects
                    date_obj = pd.to_datetime(date_str)
                transformed_row['date'] = date_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                modifications.append({
                    'row': row_number,
                    'message': f"Invalid date '{date_str}' was removed"
                })

        # Collector/Payer
        if 'Paid By' in row and row['Paid By']:
            transformed_row['collector_payer'] = str(row['Paid By']).strip()

        # Notes (if present in import)
        if 'Notes' in row and row['Notes']:
            transformed_row['notes'] = str(row['Notes']).strip()
            
        # Date handling
        date_str = row.get('Date Received or Paid', '')
        if date_str:
            normalized_date = normalize_date(date_str)
            if normalized_date:
                transformed_row['date'] = normalized_date
            else:
                modifications.append({
                    'row': row_number,
                    'field': 'Date Received or Paid',
                    'message': f"Invalid date '{date_str}' - could not parse into standard format"
                })
        
        return transformed_row, modifications

    def process_import_file(self, file_path: str, column_mapping: Dict[str, str], original_filename: str) -> Dict[str, Any]:
        """
        Process imported file and validate/transform data
        
        Args:
            file_path: Path to temporary file
            column_mapping: Dictionary mapping file columns to schema fields
            original_filename: Original filename
            
        Returns:
            Dict containing processed results
        """
        try:
            # Read file
            df = self.read_file(file_path, original_filename)
            
            # Initialize results
            results = {
                'successful_rows': [],
                'modifications': [],
                'stats': {
                    'total_rows': len(df),
                    'processed_rows': 0,
                    'modified_rows': 0
                }
            }

            # Process each row
            for idx, row in df.iterrows():
                try:
                    # Create transaction with schema structure
                    transaction = {
                        'property_id': None,
                        'type': None,
                        'category': None,
                        'description': None,
                        'amount': None,
                        'date': None,
                        'collector_payer': None,
                        'notes': None,
                        'documentation_file': None,
                        'reimbursement': {
                            'date_shared': None,
                            'share_description': 'Auto-completed - Single owner property',
                            'reimbursement_status': 'completed',
                            'documentation': None
                        }
                    }

                    # Map and transform fields
                    modifications = []
                    
                    # Property ID
                    if 'Property' in column_mapping:
                        val = row[column_mapping['Property']]
                        if pd.notna(val):
                            transaction['property_id'] = str(val).strip()

                    # Transaction Type
                    if 'Transaction Type' in column_mapping:
                        val = row[column_mapping['Transaction Type']]
                        if pd.notna(val):
                            trans_type = str(val).strip().lower()
                            if trans_type in ['income', 'expense']:
                                transaction['type'] = trans_type
                            else:
                                modifications.append(f"Invalid transaction type '{val}'")

                    # Category
                    if 'Category' in column_mapping:
                        val = row[column_mapping['Category']]
                        if pd.notna(val):
                            transaction['category'] = str(val).strip()

                    # Description
                    if 'Item Description' in column_mapping:
                        val = row[column_mapping['Item Description']]
                        if pd.notna(val):
                            transaction['description'] = str(val).strip()

                    # Amount
                    if 'Amount' in column_mapping:
                        val = row[column_mapping['Amount']]
                        if pd.notna(val):
                            try:
                                amount = float(str(val).replace('$', '').replace(',', ''))
                                transaction['amount'] = amount
                            except ValueError:
                                modifications.append(f"Invalid amount '{val}'")

                    # Date
                    if 'Date Received or Paid' in column_mapping:
                        val = row[column_mapping['Date Received or Paid']]
                        if pd.notna(val):
                            normalized_date = self.normalize_date(val)
                            if normalized_date:
                                transaction['date'] = normalized_date
                            else:
                                modifications.append(f"Invalid date '{val}'")

                    # Collector/Payer
                    if 'Paid By' in column_mapping:
                        val = row[column_mapping['Paid By']]
                        if pd.notna(val):
                            transaction['collector_payer'] = str(val).strip()

                    # Add row if it has required fields
                    if (transaction['property_id'] and 
                        transaction['type'] and 
                        (transaction['amount'] is not None or transaction['date'])):
                        
                        if modifications:
                            results['modifications'].extend([{
                                'row': idx + 2,  # Account for header row and 0-based index
                                'message': msg
                            } for msg in modifications])
                            results['stats']['modified_rows'] += 1
                            
                        results['successful_rows'].append(transaction)
                        results['stats']['processed_rows'] += 1
                    else:
                        results['modifications'].append({
                            'row': idx + 2,
                            'message': 'Missing required fields (property, type, and either amount or date)'
                        })

                except Exception as e:
                    self.logger.error(f"Error processing row {idx + 2}: {str(e)}")
                    results['modifications'].append({
                        'row': idx + 2,
                        'message': f'Error processing row: {str(e)}'
                    })

            return results

        except Exception as e:
            self.logger.error(f"Error processing import file: {str(e)}")
            raise