import unittest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
from datetime import datetime
import json
from services.transaction_import_service import TransactionImportService

class TestTransactionImportService(unittest.TestCase):
    """Test suite for TransactionImportService."""

    def setUp(self):
        """Set up test environment."""
        self.service = TransactionImportService()
        self.service.categories = {
            "income": ["RENT", "LAUNDRY", "PARKING"],
            "expense": ["MORTGAGE", "INSURANCE", "REPAIRS"]
        }
        
        # Sample valid row data
        self.valid_row = {
            'Transaction Type': 'income',
            'Category': 'RENT',
            'Amount': '$1,000.00',
            'Date Received or Paid': '2024-01-01',
            'Property': '123 Test St',
            'Item Description': 'Monthly Rent',
            'Paid By': 'Tenant'
        }

    def test_load_categories(self):
        """Test category loading."""
        with patch('builtins.open', mock_open(read_data=json.dumps({
            "income": ["TEST"],
            "expense": ["TEST"]
        }))):
            service = TransactionImportService()
            self.assertIn("income", service.categories)
            self.assertIn("expense", service.categories)

    def test_load_categories_error(self):
        """Test category loading with error."""
        with patch('builtins.open', side_effect=Exception("Test error")):
            service = TransactionImportService()
            self.assertEqual(service.categories, {"income": [], "expense": []})

    def test_validate_and_transform_valid_row(self):
        """Test row validation with valid data."""
        transformed, modifications = self.service.validate_and_transform_row(
            self.valid_row, 1
        )
        
        self.assertEqual(transformed['type'], 'Income')
        self.assertEqual(transformed['category'], 'RENT')
        self.assertEqual(transformed['amount'], 1000.00)
        self.assertEqual(transformed['date'], '2024-01-01')
        self.assertEqual(len(modifications), 0)

    def test_validate_amount_formats(self):
        """Test various amount format validations."""
        test_cases = [
            ('$1,000.00', 1000.00),
            ('1000.00', 1000.00),
            ('1000', 1000.00),
            ('invalid', None),
            ('', None)
        ]
        
        for amount, expected in test_cases:
            with self.subTest(amount=amount):
                row = self.valid_row.copy()
                row['Amount'] = amount
                transformed, mods = self.service.validate_and_transform_row(row, 1)
                self.assertEqual(transformed.get('amount'), expected)

    def test_validate_date_formats(self):
        """Test various date format validations."""
        test_cases = [
            ('2024-01-01', '2024-01-01'),
            ('01/01/2024', '2024-01-01'),
            ('2024/01/01', '2024-01-01'),
            ('invalid', None),
            ('', None)
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                row = self.valid_row.copy()
                row['Date Received or Paid'] = date_str
                transformed, mods = self.service.validate_and_transform_row(row, 1)
                self.assertEqual(transformed.get('date'), expected)

    def test_validate_transaction_type(self):
        """Test transaction type validation."""
        test_cases = [
            ('income', 'Income'),
            ('INCOME', 'Income'),
            ('expense', 'Expense'),
            ('EXPENSE', 'Expense'),
            ('invalid', None),
            ('', None)
        ]
        
        for type_str, expected in test_cases:
            with self.subTest(type_str=type_str):
                row = self.valid_row.copy()
                row['Transaction Type'] = type_str
                transformed, mods = self.service.validate_and_transform_row(row, 1)
                self.assertEqual(transformed.get('type'), expected)

    def test_validate_category(self):
        """Test category validation."""
        test_cases = [
            ('RENT', 'RENT'),
            ('INVALID', None),
            ('', None)
        ]
        
        for category, expected in test_cases:
            with self.subTest(category=category):
                row = self.valid_row.copy()
                row['Category'] = category
                transformed, mods = self.service.validate_and_transform_row(row, 1)
                self.assertEqual(transformed.get('category'), expected)

    @patch('pandas.read_csv')
    def test_process_csv_file(self, mock_read_csv):
        """Test CSV file processing."""
        mock_df = pd.DataFrame([self.valid_row])
        mock_read_csv.return_value = mock_df
        
        column_mapping = {
            'transaction_type': 'Transaction Type',
            'category': 'Category',
            'amount': 'Amount',
            'date': 'Date Received or Paid'
        }
        
        results = self.service.process_import_file('test.csv', column_mapping)
        
        self.assertEqual(results['stats']['total_rows'], 1)
        self.assertEqual(results['stats']['processed_rows'], 1)
        self.assertEqual(results['stats']['modified_rows'], 0)

    @patch('pandas.read_excel')
    def test_process_excel_file(self, mock_read_excel):
        """Test Excel file processing."""
        mock_df = pd.DataFrame([self.valid_row])
        mock_read_excel.return_value = mock_df
        
        column_mapping = {
            'transaction_type': 'Transaction Type',
            'category': 'Category',
            'amount': 'Amount',
            'date': 'Date Received or Paid'
        }
        
        results = self.service.process_import_file('test.xlsx', column_mapping)
        
        self.assertEqual(results['stats']['total_rows'], 1)
        self.assertEqual(results['stats']['processed_rows'], 1)
        self.assertEqual(results['stats']['modified_rows'], 0)

class TestTransactionImportEdgeCases(unittest.TestCase):
    """Test suite for edge cases and error handling."""

    def setUp(self):
        self.service = TransactionImportService()
        self.service.categories = {
            "income": ["RENT"],
            "expense": ["REPAIRS"]
        }

    def test_empty_row(self):
        """Test processing empty row."""
        empty_row = {
            'Transaction Type': '',
            'Category': '',
            'Amount': '',
            'Date Received or Paid': ''
        }
        
        transformed, modifications = self.service.validate_and_transform_row(empty_row, 1)
        self.assertEqual(len(transformed), 0)

    def test_partial_row(self):
        """Test processing partially filled row."""
        partial_row = {
            'Transaction Type': 'income',
            'Category': 'RENT'
            # Missing Amount and Date
        }
        
        transformed, modifications = self.service.validate_and_transform_row(partial_row, 1)
        self.assertEqual(transformed['type'], 'Income')
        self.assertEqual(transformed['category'], 'RENT')
        self.assertNotIn('amount', transformed)
        self.assertNotIn('date', transformed)

    def test_invalid_file_type(self):
        """Test processing invalid file type."""
        with self.assertRaises(Exception):
            self.service.process_import_file('test.txt', {})

    @patch('pandas.read_csv')
    def test_empty_file(self, mock_read_csv):
        """Test processing empty file."""
        mock_read_csv.return_value = pd.DataFrame()
        
        results = self.service.process_import_file('test.csv', {})
        self.assertEqual(results['stats']['total_rows'], 0)
        self.assertEqual(results['stats']['processed_rows'], 0)

    def test_malformed_amount(self):
        """Test processing malformed amount values."""
        test_cases = [
            '$1,000.00.00',  # Double decimal
            '1,000,000',     # Multiple commas
            '1.000,00',      # European format
            '1000-',         # Negative sign at end
            '10.00.00'       # Multiple decimals
        ]
        
        for amount in test_cases:
            with self.subTest(amount=amount):
                row = {'Amount': amount}
                transformed, modifications = self.service.validate_and_transform_row(row, 1)
                self.assertIsNone(transformed.get('amount'))
                self.assertEqual(len(modifications), 1)

    def test_malformed_dates(self):
        """Test processing malformed date values."""
        test_cases = [
            '2024-13-01',    # Invalid month
            '2024-01-32',    # Invalid day
            '01-01-2024',    # Ambiguous format
            '2024.01.01',    # Invalid separator
            '24-01-01'       # Two-digit year
        ]
        
        for date_str in test_cases:
            with self.subTest(date_str=date_str):
                row = {'Date Received or Paid': date_str}
                transformed, modifications = self.service.validate_and_transform_row(row, 1)
                self.assertIsNone(transformed.get('date'))
                self.assertEqual(len(modifications), 1)

class TestTransactionImportBulk(unittest.TestCase):
    """Test suite for bulk import processing."""

    def setUp(self):
        self.service = TransactionImportService()
        self.service.categories = {
            "income": ["RENT"],
            "expense": ["REPAIRS"]
        }

    @patch('pandas.read_csv')
    def test_bulk_import_mixed_valid_invalid(self, mock_read_csv):
        """Test processing mix of valid and invalid rows."""
        mock_data = [
            {
                'Transaction Type': 'income',
                'Category': 'RENT',
                'Amount': '1000',
                'Date Received or Paid': '2024-01-01'
            },
            {
                'Transaction Type': 'invalid',
                'Category': 'invalid',
                'Amount': 'invalid',
                'Date Received or Paid': 'invalid'
            }
        ]
        mock_read_csv.return_value = pd.DataFrame(mock_data)
        
        results = self.service.process_import_file('test.csv', {})
        self.assertEqual(results['stats']['total_rows'], 2)
        self.assertEqual(results['stats']['modified_rows'], 1)

    @patch('pandas.read_csv')
    def test_bulk_import_column_mapping(self, mock_read_csv):
        """Test processing with different column mappings."""
        mock_data = [{
            'Type': 'income',
            'Trans Category': 'RENT',
            'Payment Amount': '1000',
            'Payment Date': '2024-01-01'
        }]
        mock_read_csv.return_value = pd.DataFrame(mock_data)
        
        column_mapping = {
            'transaction_type': 'Type',
            'category': 'Trans Category',
            'amount': 'Payment Amount',
            'date': 'Payment Date'
        }
        
        results = self.service.process_import_file('test.csv', column_mapping)
        self.assertEqual(results['stats']['processed_rows'], 1)
        self.assertEqual(results['stats']['modified_rows'], 0)

if __name__ == '__main__':
    unittest.main()