import json
import pandas as pd
from datetime import datetime
from flask import current_app
import logging
from typing import Dict, List, Tuple, Any

class TransactionImportService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.load_categories()
        
    def load_categories(self) -> None:
        try:
            with open(current_app.config['CATEGORIES_FILE'], 'r') as f:
                self.categories = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading categories: {str(e)}")
            self.categories = {"income": [], "expense": []}

    def validate_and_transform_row(self, row: Dict[str, Any], row_number: int) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
        """
        Validate and transform a single row of import data, replacing invalid values with None.
        """
        modifications = []
        transformed_row = {}
        
        # Transaction Type validation and transformation
        trans_type = str(row.get('Transaction Type', '')).strip().lower()
        if trans_type:
            if trans_type not in ['income', 'expense']:
                modifications.append({
                    'row': row_number,
                    'field': 'Transaction Type',
                    'original': trans_type,
                    'message': f"Invalid Transaction Type '{trans_type}' was removed"
                })
                trans_type = None
            transformed_row['type'] = trans_type.capitalize() if trans_type else None
        
        # Category validation
        category = str(row.get('Category', '')).strip()
        if category:
            valid_categories = self.categories.get(trans_type, []) if trans_type else []
            if category not in valid_categories:
                modifications.append({
                    'row': row_number,
                    'field': 'Category',
                    'original': category,
                    'message': f"Invalid Category '{category}' was removed. Valid categories are: {', '.join(valid_categories)}"
                })
                category = None
            transformed_row['category'] = category
        
        # Amount validation and transformation
        amount = row.get('Amount', '')
        if amount:
            try:
                cleaned_amount = str(amount).replace('$', '').replace(',', '')
                transformed_row['amount'] = float(cleaned_amount)
            except ValueError:
                modifications.append({
                    'row': row_number,
                    'field': 'Amount',
                    'original': amount,
                    'message': f"Invalid Amount '{amount}' was removed"
                })
                transformed_row['amount'] = None
        
        # Date validation and transformation
        date_str = row.get('Date Received or Paid', '')
        if date_str:
            try:
                date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
                date_parsed = False
                for date_format in date_formats:
                    try:
                        date_obj = datetime.strptime(str(date_str), date_format)
                        transformed_row['date'] = date_obj.strftime('%Y-%m-%d')
                        date_parsed = True
                        break
                    except ValueError:
                        continue
                if not date_parsed:
                    modifications.append({
                        'row': row_number,
                        'field': 'Date',
                        'original': date_str,
                        'message': f"Invalid date format '{date_str}' was removed"
                    })
                    transformed_row['date'] = None
            except Exception as e:
                modifications.append({
                    'row': row_number,
                    'field': 'Date',
                    'original': date_str,
                    'message': f"Invalid date '{date_str}' was removed"
                })
                transformed_row['date'] = None
        
        # Copy other fields directly
        for field in ['Property', 'Item Description', 'Paid By']:
            value = row.get(field, '')
            if value:
                transformed_row[field.lower().replace(' ', '_')] = str(value).strip()
        
        return transformed_row, modifications

    def process_import_file(self, file_path: str, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Process the import file and return transformed data with modification details"""
        try:
            self.logger.debug(f"Processing import file: {file_path}")
            self.logger.debug(f"Column mapping: {column_mapping}")

            # Initialize results dictionary with all required keys
            results = {
                'successful_rows': [],
                'modifications': [],
                'stats': {
                    'total_rows': 0,
                    'processed_rows': 0,
                    'modified_rows': 0
                }
            }

            # Read the file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Update total rows stat
            results['stats']['total_rows'] = len(df)
            
            # Rename columns according to mapping
            reverse_mapping = {v: k for k, v in column_mapping.items() if v}
            df = df.rename(columns=reverse_mapping)
            
            # Process each row
            for index, row in df.iterrows():
                row_number = index + 2  # Add 2 to account for 1-based indexing and header row
                transformed_row, modifications = self.validate_and_transform_row(row, row_number)
                
                if modifications:
                    results['modifications'].extend(modifications)
                    results['stats']['modified_rows'] += 1
                
                results['successful_rows'].append(transformed_row)
                results['stats']['processed_rows'] += 1

            self.logger.debug(f"Import processing completed. Results: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing import file: {str(e)}")
            self.logger.exception("Full traceback:")
            raise