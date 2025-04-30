# transaction_import_service.py
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import logging
from datetime import datetime
import json
from flask import current_app  # Added missing import

logger = logging.getLogger(__name__)

class TransactionImportService:
    """Service for importing and processing transaction data from CSV or Excel files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.categories = {"income": [], "expense": []}
        self.load_categories()
        
    def load_categories(self) -> None:
        """Load transaction categories from configuration file."""
        try:
            with open(current_app.config['CATEGORIES_FILE'], 'r') as f:
                self.categories = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading categories: {str(e)}")
            self.categories = {"income": [], "expense": []}

    def read_file(self, file_path: str, original_filename: str) -> pd.DataFrame:
        """
        Read CSV or Excel file into DataFrame with appropriate encoding.
        
        Args:
            file_path: Path to temporary file
            original_filename: Original filename to determine type
            
        Returns:
            pd.DataFrame: DataFrame containing file contents
        """
        try:
            if original_filename.lower().endswith('.csv'):
                return self._read_csv_with_fallback_encoding(file_path)
            else:
                # Handle Excel files
                df = pd.read_excel(file_path)
                df.columns = df.columns.str.strip()
                return df
                
        except Exception as e:
            self.logger.error(f"Error reading file: {str(e)}")
            raise
    
    def _read_csv_with_fallback_encoding(self, file_path: str) -> pd.DataFrame:
        """
        Try reading CSV with different encodings.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            pd.DataFrame: DataFrame with CSV contents
            
        Raises:
            Exception: If file cannot be read with any encoding
        """
        encodings = ['utf-8', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                df.columns = df.columns.str.strip()
                return df
            except UnicodeDecodeError:
                continue
            except Exception as e:
                self.logger.error(f"Error reading CSV with {encoding}: {str(e)}")
                
        # If we get here, no encoding worked
        raise ValueError(f"Unable to read CSV file with any supported encoding")

    def normalize_date(self, date_value: Any) -> Optional[str]:
        """
        Normalize date to YYYY-MM-DD format.
        
        Args:
            date_value: Input date in any format
            
        Returns:
            str: Normalized date string or None if conversion fails
        """
        if pd.isna(date_value):
            return None
            
        try:
            # Convert to pandas timestamp
            ts = pd.to_datetime(date_value)
            return ts.strftime('%Y-%m-%d')
        except Exception:
            return None
    
    def create_empty_transaction(self) -> Dict[str, Any]:
        """
        Create an empty transaction with the correct schema structure.
        
        Returns:
            Dict: Empty transaction with null values
        """
        return {
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
        
    def process_import_file(self, file_path: str, column_mapping: Dict[str, str], 
                           original_filename: str) -> Dict[str, Any]:
        """
        Process imported file and validate/transform data.
        
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
                row_number = idx + 2  # Account for header row and 0-based index
                transformed_row, modifications = self.transform_row(row, row_number, column_mapping)
                
                # Add row if it has required fields
                if (transformed_row['property_id'] and 
                    transformed_row['type'] and 
                    (transformed_row['amount'] is not None or transformed_row['date'])):
                    
                    if modifications:
                        results['modifications'].extend(modifications)
                        results['stats']['modified_rows'] += 1
                        
                    results['successful_rows'].append(transformed_row)
                    results['stats']['processed_rows'] += 1
                else:
                    results['modifications'].append({
                        'row': row_number,
                        'message': 'Missing required fields (property, type, and either amount or date)'
                    })

            return results

        except Exception as e:
            self.logger.error(f"Error processing import file: {str(e)}")
            raise

    def transform_row(self, row: pd.Series, row_number: int, 
                     column_mapping: Dict[str, str]) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
        """
        Transform a row from the import file into a transaction.
        
        Args:
            row: Pandas Series containing row data
            row_number: Row number for error reporting
            column_mapping: Dictionary mapping file columns to schema fields
            
        Returns:
            Tuple containing (transformed_row, list_of_modifications)
        """
        modifications = []
        transaction = self.create_empty_transaction()
        
        try:
            # Map fields using column mapping
            self._map_property_id(transaction, row, column_mapping, modifications, row_number)
            self._map_transaction_type(transaction, row, column_mapping, modifications, row_number)
            self._map_category(transaction, row, column_mapping, modifications, row_number)
            self._map_description(transaction, row, column_mapping)
            self._map_amount(transaction, row, column_mapping, modifications, row_number)
            self._map_date(transaction, row, column_mapping, modifications, row_number)
            self._map_collector_payer(transaction, row, column_mapping)
            self._map_notes(transaction, row, column_mapping)
            
            return transaction, modifications
            
        except Exception as e:
            self.logger.error(f"Error transforming row {row_number}: {str(e)}")
            modifications.append({
                'row': row_number,
                'message': f'Error processing row: {str(e)}'
            })
            return transaction, modifications
    
    def _map_property_id(self, transaction: Dict[str, Any], row: pd.Series, 
                        column_mapping: Dict[str, str], modifications: List[Dict[str, str]], 
                        row_number: int) -> None:
        """Map Property ID field from import to transaction."""
        if 'Property' in column_mapping:
            val = row.get(column_mapping['Property'])
            if pd.notna(val):
                transaction['property_id'] = str(val).strip()
    
    def _map_transaction_type(self, transaction: Dict[str, Any], row: pd.Series, 
                             column_mapping: Dict[str, str], modifications: List[Dict[str, str]], 
                             row_number: int) -> None:
        """Map Transaction Type field from import to transaction."""
        if 'Transaction Type' in column_mapping:
            val = row.get(column_mapping['Transaction Type'])
            if pd.notna(val):
                trans_type = str(val).strip().lower()
                if trans_type in ['income', 'expense']:
                    transaction['type'] = trans_type
                else:
                    modifications.append({
                        'row': row_number,
                        'field': 'Transaction Type',
                        'message': f"Invalid transaction type '{val}' was removed"
                    })
    
    def _map_category(self, transaction: Dict[str, Any], row: pd.Series, 
                     column_mapping: Dict[str, str], modifications: List[Dict[str, str]], 
                     row_number: int) -> None:
        """Map Category field from import to transaction."""
        if 'Category' in column_mapping:
            val = row.get(column_mapping['Category'])
            if pd.notna(val):
                category = str(val).strip()
                # Only validate if we have a transaction type
                if transaction['type']:
                    valid_categories = self.categories.get(transaction['type'], [])
                    if category not in valid_categories:
                        modifications.append({
                            'row': row_number,
                            'field': 'Category',
                            'message': f"Invalid Category '{category}' was removed"
                        })
                    else:
                        transaction['category'] = category
                else:
                    # Store category without validation if no transaction type
                    transaction['category'] = category
    
    def _map_description(self, transaction: Dict[str, Any], row: pd.Series, 
                        column_mapping: Dict[str, str]) -> None:
        """Map Description field from import to transaction."""
        if 'Item Description' in column_mapping:
            val = row.get(column_mapping['Item Description'])
            if pd.notna(val):
                transaction['description'] = str(val).strip()
    
    def _map_amount(self, transaction: Dict[str, Any], row: pd.Series, 
                   column_mapping: Dict[str, str], modifications: List[Dict[str, str]], 
                   row_number: int) -> None:
        """Map Amount field from import to transaction."""
        if 'Amount' in column_mapping:
            val = row.get(column_mapping['Amount'])
            if pd.notna(val):
                try:
                    cleaned_amount = str(val).replace('$', '').replace(',', '')
                    transaction['amount'] = float(cleaned_amount)
                except ValueError:
                    modifications.append({
                        'row': row_number,
                        'field': 'Amount',
                        'message': f"Invalid amount '{val}' was removed"
                    })
    
    def _map_date(self, transaction: Dict[str, Any], row: pd.Series, 
                 column_mapping: Dict[str, str], modifications: List[Dict[str, str]], 
                 row_number: int) -> None:
        """Map Date field from import to transaction."""
        if 'Date Received or Paid' in column_mapping:
            val = row.get(column_mapping['Date Received or Paid'])
            if pd.notna(val):
                normalized_date = self.normalize_date(val)
                if normalized_date:
                    transaction['date'] = normalized_date
                else:
                    modifications.append({
                        'row': row_number,
                        'field': 'Date Received or Paid',
                        'message': f"Invalid date '{val}' - could not parse into standard format"
                    })
    
    def _map_collector_payer(self, transaction: Dict[str, Any], row: pd.Series, 
                            column_mapping: Dict[str, str]) -> None:
        """Map Collector/Payer field from import to transaction."""
        if 'Paid By' in column_mapping:
            val = row.get(column_mapping['Paid By'])
            if pd.notna(val):
                transaction['collector_payer'] = str(val).strip()
    
    def _map_notes(self, transaction: Dict[str, Any], row: pd.Series, 
                  column_mapping: Dict[str, str]) -> None:
        """Map Notes field from import to transaction."""
        if 'Notes' in column_mapping:
            val = row.get(column_mapping['Notes'])
            if pd.notna(val):
                transaction['notes'] = str(val).strip()