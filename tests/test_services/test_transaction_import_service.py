import unittest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import json
import io
from flask import Flask
from services.transaction_import_service import TransactionImportService

class TestTransactionImportService(unittest.TestCase):
    """Test cases for TransactionImportService"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a test Flask app
        self.app = Flask(__name__)
        self.app.config['CATEGORIES_FILE'] = 'mock_categories.json'
        
        # Mock categories data
        self.categories = {
            "income": ["Rent", "Other Income"],
            "expense": ["Repairs", "Utilities", "Mortgage"]
        }
        
        # Use the app context for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create service instance with mocked categories
        self.service = TransactionImportService()
        self.service.categories = self.categories

    def tearDown(self):
        """Tear down test fixtures"""
        self.app_context.pop()

    @patch('builtins.open', new_callable=mock_open, read_data='{"income": ["Rent"], "expense": ["Repairs"]}')
    def test_load_categories(self, mock_file):
        """Test loading categories from file"""
        service = TransactionImportService()
        self.assertEqual(service.categories["income"], ["Rent"])
        self.assertEqual(service.categories["expense"], ["Repairs"])
        mock_file.assert_called_once_with(self.app.config['CATEGORIES_FILE'], 'r')

    @patch('builtins.open')
    def test_load_categories_error(self, mock_file):
        """Test error handling when loading categories"""
        mock_file.side_effect = Exception("File not found")
        service = TransactionImportService()
        self.assertEqual(service.categories, {"income": [], "expense": []})

    @patch('pandas.read_csv')
    def test_read_csv_file(self, mock_read_csv):
        """Test reading CSV file"""
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        mock_read_csv.return_value = mock_df
        
        result = self.service.read_file('test.csv', 'test.csv')
        
        mock_read_csv.assert_called_once()
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape, (2, 2))

    @patch('pandas.read_excel')
    def test_read_excel_file(self, mock_read_excel):
        """Test reading Excel file"""
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        mock_read_excel.return_value = mock_df
        
        result = self.service.read_file('test.xlsx', 'test.xlsx')
        
        mock_read_excel.assert_called_once_with('test.xlsx')
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape, (2, 2))

    @patch('pandas.read_csv')
    def test_read_csv_with_fallback_encoding(self, mock_read_csv):
        """Test CSV reading with fallback encodings"""
        # First encoding fails, second succeeds
        mock_read_csv.side_effect = [UnicodeDecodeError('utf-8', b'', 0, 1, 'Test error'), 
                                     pd.DataFrame({'col1': [1, 2]})]
        
        result = self.service._read_csv_with_fallback_encoding('test.csv')
        
        # Should have been called twice with different encodings
        self.assertEqual(mock_read_csv.call_count, 2)
        self.assertTrue(isinstance(result, pd.DataFrame))

    @patch('pandas.read_csv')
    def test_read_csv_all_encodings_fail(self, mock_read_csv):
        """Test when all CSV encodings fail"""
        # All encodings fail
        mock_read_csv.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'Test error')
        
        with self.assertRaises(ValueError):
            self.service._read_csv_with_fallback_encoding('test.csv')

    def test_normalize_date(self):
        """Test date normalization"""
        # Test various date formats
        self.assertEqual(self.service.normalize_date('2023-01-15'), '2023-01-15')
        self.assertEqual(self.service.normalize_date('01/15/2023'), '2023-01-15')
        self.assertEqual(self.service.normalize_date('15-Jan-2023'), '2023-01-15')
        
        # Test invalid date
        self.assertIsNone(self.service.normalize_date('not a date'))
        
        # Test None value
        self.assertIsNone(self.service.normalize_date(None))
        self.assertIsNone(self.service.normalize_date(pd.NA))

    def test_create_empty_transaction(self):
        """Test creating empty transaction structure"""
        transaction = self.service.create_empty_transaction()
        
        # Check structure
        self.assertIsNone(transaction['property_id'])
        self.assertIsNone(transaction['type'])
        self.assertIsNone(transaction['category'])
        self.assertIsNone(transaction['amount'])
        self.assertIsNone(transaction['date'])
        
        # Check reimbursement structure
        self.assertIn('reimbursement', transaction)
        self.assertEqual(transaction['reimbursement']['reimbursement_status'], 'completed')

    @patch('pandas.read_csv')
    def test_process_import_file_csv(self, mock_read_csv):
        """Test processing CSV import file"""
        # Create mock DataFrame
        mock_df = pd.DataFrame({
            'Property': ['123 Main St', '456 Oak Ave'],
            'Transaction Type': ['Income', 'Expense'],
            'Category': ['Rent', 'Repairs'],
            'Item Description': ['Monthly Rent', 'Fix Sink'],
            'Amount': ['$1000', '$200'],
            'Date Received or Paid': ['2023-01-15', '2023-01-20'],
            'Paid By': ['Tenant', 'Owner'],
            'Notes': ['On time', 'Emergency repair']
        })
        mock_read_csv.return_value = mock_df
        
        # Define column mapping
        column_mapping = {
            'Property': 'Property',
            'Transaction Type': 'Transaction Type',
            'Category': 'Category',
            'Item Description': 'Item Description',
            'Amount': 'Amount',
            'Date Received or Paid': 'Date Received or Paid',
            'Paid By': 'Paid By',
            'Notes': 'Notes'
        }
        
        # Process file
        result = self.service.process_import_file('test.csv', column_mapping, 'test.csv')
        
        # Check results
        self.assertEqual(result['stats']['total_rows'], 2)
        self.assertEqual(result['stats']['processed_rows'], 2)
        self.assertEqual(len(result['successful_rows']), 2)
        
        # Check first transaction
        first_transaction = result['successful_rows'][0]
        self.assertEqual(first_transaction['property_id'], '123 Main St')
        self.assertEqual(first_transaction['type'], 'income')
        self.assertEqual(first_transaction['category'], 'Rent')
        self.assertEqual(first_transaction['amount'], 1000.0)
        self.assertEqual(first_transaction['date'], '2023-01-15')

    def test_transform_row_valid(self):
        """Test transforming a valid row"""
        # Create a row with all valid data
        row = pd.Series({
            'Property': '123 Main St',
            'Transaction Type': 'Income',
            'Category': 'Rent',
            'Item Description': 'Monthly Rent',
            'Amount': '$1000',
            'Date Received or Paid': '2023-01-15',
            'Paid By': 'Tenant',
            'Notes': 'On time'
        })
        
        column_mapping = {
            'Property': 'Property',
            'Transaction Type': 'Transaction Type',
            'Category': 'Category',
            'Item Description': 'Item Description',
            'Amount': 'Amount',
            'Date Received or Paid': 'Date Received or Paid',
            'Paid By': 'Paid By',
            'Notes': 'Notes'
        }
        
        transaction, modifications = self.service.transform_row(row, 2, column_mapping)
        
        # Check transaction data
        self.assertEqual(transaction['property_id'], '123 Main St')
        self.assertEqual(transaction['type'], 'income')
        self.assertEqual(transaction['category'], 'Rent')
        self.assertEqual(transaction['description'], 'Monthly Rent')
        self.assertEqual(transaction['amount'], 1000.0)
        self.assertEqual(transaction['date'], '2023-01-15')
        self.assertEqual(transaction['collector_payer'], 'Tenant')
        self.assertEqual(transaction['notes'], 'On time')
        
        # No modifications should be needed
        self.assertEqual(modifications, [])

    def test_transform_row_invalid_type(self):
        """Test transforming a row with invalid transaction type"""
        row = pd.Series({
            'Property': '123 Main St',
            'Transaction Type': 'Invalid',
            'Category': 'Rent',
            'Amount': '$1000',
            'Date Received or Paid': '2023-01-15'
        })
        
        column_mapping = {
            'Property': 'Property',
            'Transaction Type': 'Transaction Type',
            'Category': 'Category',
            'Amount': 'Amount',
            'Date Received or Paid': 'Date Received or Paid'
        }
        
        transaction, modifications = self.service.transform_row(row, 2, column_mapping)
        
        # Type should be None
        self.assertIsNone(transaction['type'])
        
        # Should have a modification
        self.assertEqual(len(modifications), 1)
        self.assertEqual(modifications[0]['field'], 'Transaction Type')

    def test_transform_row_invalid_category(self):
        """Test transforming a row with invalid category"""
        row = pd.Series({
            'Property': '123 Main St',
            'Transaction Type': 'Income',
            'Category': 'Invalid Category',
            'Amount': '$1000',
            'Date Received or Paid': '2023-01-15'
        })
        
        column_mapping = {
            'Property': 'Property',
            'Transaction Type': 'Transaction Type',
            'Category': 'Category',
            'Amount': 'Amount',
            'Date Received or Paid': 'Date Received or Paid'
        }
        
        transaction, modifications = self.service.transform_row(row, 2, column_mapping)
        
        # Category should be None
        self.assertIsNone(transaction['category'])
        
        # Should have a modification
        self.assertEqual(len(modifications), 1)
        self.assertEqual(modifications[0]['field'], 'Category')

    def test_transform_row_invalid_amount(self):
        """Test transforming a row with invalid amount"""
        row = pd.Series({
            'Property': '123 Main St',
            'Transaction Type': 'Income',
            'Category': 'Rent',
            'Amount': 'Not a number',
            'Date Received or Paid': '2023-01-15'
        })
        
        column_mapping = {
            'Property': 'Property',
            'Transaction Type': 'Transaction Type',
            'Category': 'Category',
            'Amount': 'Amount',
            'Date Received or Paid': 'Date Received or Paid'
        }
        
        transaction, modifications = self.service.transform_row(row, 2, column_mapping)
        
        # Amount should be None
        self.assertIsNone(transaction['amount'])
        
        # Should have a modification
        self.assertEqual(len(modifications), 1)
        self.assertEqual(modifications[0]['field'], 'Amount')

    def test_transform_row_invalid_date(self):
        """Test transforming a row with invalid date"""
        row = pd.Series({
            'Property': '123 Main St',
            'Transaction Type': 'Income',
            'Category': 'Rent',
            'Amount': '$1000',
            'Date Received or Paid': 'Not a date'
        })
        
        column_mapping = {
            'Property': 'Property',
            'Transaction Type': 'Transaction Type',
            'Category': 'Category',
            'Amount': 'Amount',
            'Date Received or Paid': 'Date Received or Paid'
        }
        
        transaction, modifications = self.service.transform_row(row, 2, column_mapping)
        
        # Date should be None
        self.assertIsNone(transaction['date'])
        
        # Should have a modification
        self.assertEqual(len(modifications), 1)
        self.assertEqual(modifications[0]['field'], 'Date Received or Paid')

    def test_map_property_id(self):
        """Test mapping property ID"""
        transaction = self.service.create_empty_transaction()
        row = pd.Series({'Property': '123 Main St'})
        column_mapping = {'Property': 'Property'}
        modifications = []
        
        self.service._map_property_id(transaction, row, column_mapping, modifications, 1)
        
        self.assertEqual(transaction['property_id'], '123 Main St')
        self.assertEqual(modifications, [])

    def test_map_transaction_type(self):
        """Test mapping transaction type"""
        transaction = self.service.create_empty_transaction()
        
        # Test valid income type
        row = pd.Series({'Transaction Type': 'Income'})
        column_mapping = {'Transaction Type': 'Transaction Type'}
        modifications = []
        
        self.service._map_transaction_type(transaction, row, column_mapping, modifications, 1)
        
        self.assertEqual(transaction['type'], 'income')
        self.assertEqual(modifications, [])
        
        # Test valid expense type
        transaction = self.service.create_empty_transaction()
        row = pd.Series({'Transaction Type': 'Expense'})
        modifications = []
        
        self.service._map_transaction_type(transaction, row, column_mapping, modifications, 1)
        
        self.assertEqual(transaction['type'], 'expense')
        self.assertEqual(modifications, [])
        
        # Test invalid type
        transaction = self.service.create_empty_transaction()
        row = pd.Series({'Transaction Type': 'Invalid'})
        modifications = []
        
        self.service._map_transaction_type(transaction, row, column_mapping, modifications, 1)
        
        self.assertIsNone(transaction['type'])
        self.assertEqual(len(modifications), 1)

    def test_map_category(self):
        """Test mapping category"""
        # Test valid category for income
        transaction = {'type': 'income'}
        row = pd.Series({'Category': 'Rent'})
        column_mapping = {'Category': 'Category'}
        modifications = []
        
        self.service._map_category(transaction, row, column_mapping, modifications, 1)
        
        self.assertEqual(transaction['category'], 'Rent')
        self.assertEqual(modifications, [])
        
        # Test invalid category for income
        transaction = {'type': 'income'}
        row = pd.Series({'Category': 'Invalid'})
        modifications = []
        
        self.service._map_category(transaction, row, column_mapping, modifications, 1)
        
        self.assertIsNone(transaction.get('category'))
        self.assertEqual(len(modifications), 1)

    def test_map_amount(self):
        """Test mapping amount"""
        # Test valid amount
        transaction = self.service.create_empty_transaction()
        row = pd.Series({'Amount': '$1,000.50'})
        column_mapping = {'Amount': 'Amount'}
        modifications = []
        
        self.service._map_amount(transaction, row, column_mapping, modifications, 1)
        
        self.assertEqual(transaction['amount'], 1000.50)
        self.assertEqual(modifications, [])
        
        # Test invalid amount
        transaction = self.service.create_empty_transaction()
        row = pd.Series({'Amount': 'Not a number'})
        modifications = []
        
        self.service._map_amount(transaction, row, column_mapping, modifications, 1)
        
        self.assertIsNone(transaction['amount'])
        self.assertEqual(len(modifications), 1)

    def test_map_date(self):
        """Test mapping date"""
        # Test valid date
        transaction = self.service.create_empty_transaction()
        row = pd.Series({'Date Received or Paid': '2023-01-15'})
        column_mapping = {'Date Received or Paid': 'Date Received or Paid'}
        modifications = []
        
        self.service._map_date(transaction, row, column_mapping, modifications, 1)
        
        self.assertEqual(transaction['date'], '2023-01-15')
        self.assertEqual(modifications, [])
        
        # Test invalid date
        transaction = self.service.create_empty_transaction()
        row = pd.Series({'Date Received or Paid': 'Not a date'})
        modifications = []
        
        self.service._map_date(transaction, row, column_mapping, modifications, 1)
        
        self.assertIsNone(transaction['date'])
        self.assertEqual(len(modifications), 1)

if __name__ == '__main__':
    unittest.main()
