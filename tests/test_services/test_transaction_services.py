import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from datetime import datetime, date
import pandas as pd
from services.transaction_service import (
    get_properties_for_user, add_transaction, get_transactions_for_user,
    get_categories, get_transaction_by_id, update_transaction,
    process_bulk_import, is_duplicate_transaction, clean_amount,
    parse_date, match_property
)

class TestTransactionService(unittest.TestCase):
    """Test suite for transaction service functions."""

    def setUp(self):
        """Set up test environment."""
        self.test_transaction = {
            'id': '1',
            'property_id': '123 Test St',
            'type': 'income',
            'category': 'RENT',
            'description': 'Monthly Rent',
            'amount': 1000.00,
            'date': '2024-01-01',
            'collector_payer': 'Tenant',
            'documentation_file': 'test.pdf',
            'reimbursement': {
                'date_shared': '2024-01-02',
                'share_description': 'Test share',
                'reimbursement_status': 'pending'
            }
        }
        
        self.test_property = {
            'address': '123 Test St',
            'partners': [
                {'name': 'Test User', 'equity_share': 50},
                {'name': 'Partner User', 'equity_share': 50}
            ]
        }

    @patch('services.transaction_service.read_json')
    def test_get_properties_for_user(self, mock_read):
        """Test property retrieval for users."""
        mock_read.return_value = [self.test_property]
        
        # Test regular user
        properties = get_properties_for_user('user@test.com', 'Test User')
        self.assertEqual(len(properties), 1)
        
        # Test admin user
        properties = get_properties_for_user('admin@test.com', 'Admin', is_admin=True)
        self.assertEqual(len(properties), 1)
        
        # Test user with no properties
        properties = get_properties_for_user('none@test.com', 'No User')
        self.assertEqual(len(properties), 0)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('json.dump')
    def test_add_transaction(self, mock_dump, mock_load, mock_file):
        """Test transaction addition."""
        mock_load.return_value = []
        
        result = add_transaction(self.test_transaction)
        self.assertTrue(result)
        mock_dump.assert_called_once()

    @patch('services.transaction_service.read_json')
    def test_get_transactions_for_user(self, mock_read):
        """Test transaction retrieval for users."""
        mock_read.side_effect = [
            [self.test_transaction],  # transactions
            [self.test_property]      # properties
        ]
        
        transactions = get_transactions_for_user('Test User')
        self.assertEqual(len(transactions), 1)
        
        # Test with property filter
        transactions = get_transactions_for_user('Test User', property_id='123 Test St')
        self.assertEqual(len(transactions), 1)
        
        # Test with date filters
        transactions = get_transactions_for_user(
            'Test User',
            start_date='2024-01-01',
            end_date='2024-12-31'
        )
        self.assertEqual(len(transactions), 1)

    @patch('services.transaction_service.read_json')
    def test_get_categories(self, mock_read):
        """Test category retrieval."""
        mock_read.return_value = {
            'income': ['RENT'],
            'expense': ['REPAIRS']
        }
        
        categories = get_categories('income')
        self.assertEqual(categories, ['RENT'])
        
        categories = get_categories('invalid')
        self.assertEqual(categories, [])

    @patch('services.transaction_service.read_json')
    def test_get_transaction_by_id(self, mock_read):
        """Test transaction retrieval by ID."""
        mock_read.return_value = [self.test_transaction]
        
        transaction = get_transaction_by_id('1')
        self.assertEqual(transaction['id'], '1')
        
        transaction = get_transaction_by_id('999')
        self.assertIsNone(transaction)

    @patch('services.transaction_service.read_json')
    @patch('services.transaction_service.write_json')
    def test_update_transaction(self, mock_write, mock_read):
        """Test transaction update."""
        mock_read.return_value = [self.test_transaction]
        
        updated_transaction = self.test_transaction.copy()
        updated_transaction['amount'] = 1100.00
        
        update_transaction(updated_transaction)
        mock_write.assert_called_once()
        
        # Test non-existent transaction
        invalid_transaction = self.test_transaction.copy()
        invalid_transaction['id'] = '999'
        with self.assertRaises(ValueError):
            update_transaction(invalid_transaction)

    def test_clean_amount(self):
        """Test amount cleaning and type detection."""
        test_cases = [
            ('$1,000.00', (1000.00, 'income')),
            ('-$1,000.00', (1000.00, 'expense')),
            ('1000', (1000.00, 'income')),
            ('-1000', (1000.00, 'expense')),
            ('invalid', (None, None)),
            ('', (None, None))
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = clean_amount(input_value)
                self.assertEqual(result, expected)

    def test_parse_date(self):
        """Test date parsing."""
        test_cases = [
            ('2024-01-01', '2024-01-01'),
            ('01/01/2024', '2024-01-01'),
            ('2024/01/01', '2024-01-01'),
            ('invalid', None),
            ('', None)
        ]
        
        for input_date, expected in test_cases:
            with self.subTest(input_date=input_date):
                result = parse_date(input_date)
                self.assertEqual(result, expected)

    def test_match_property(self):
        """Test property matching."""
        properties = [
            {'address': '123 Main Street'},
            {'address': '456 Oak Avenue'}
        ]
        
        test_cases = [
            ('123 Main St', '123 Main Street'),
            ('456 Oak Ave', '456 Oak Avenue'),
            ('789 Invalid St', None)
        ]
        
        for input_address, expected in test_cases:
            with self.subTest(input_address=input_address):
                result = match_property(input_address, properties)
                self.assertEqual(result, expected)

    @patch('services.transaction_service.read_json')
    def test_is_duplicate_transaction(self, mock_read):
        """Test duplicate transaction detection."""
        mock_read.return_value = [self.test_transaction]
        
        # Test exact duplicate
        self.assertTrue(is_duplicate_transaction(self.test_transaction))
        
        # Test similar but not duplicate
        different_transaction = self.test_transaction.copy()
        different_transaction['amount'] = 2000.00
        self.assertFalse(is_duplicate_transaction(different_transaction))
        
        # Test date threshold
        close_date_transaction = self.test_transaction.copy()
        close_date_transaction['date'] = '2024-01-02'
        self.assertTrue(is_duplicate_transaction(close_date_transaction))

class TestBulkImport(unittest.TestCase):
    """Test suite for bulk import functionality."""

    def setUp(self):
        self.test_data = pd.DataFrame([{
            'Property': '123 Test St',
            'Amount': '$1,000.00',
            'Date Received or Paid': '2024-01-01',
            'Category': 'RENT',
            'Item Description': 'Monthly Rent',
            'Paid By': 'Tenant'
        }])
        
        self.column_mapping = {
            'Property': 'Property',
            'Amount': 'Amount',
            'Date Received or Paid': 'Date Received or Paid',
            'Category': 'Category',
            'Item Description': 'Item Description',
            'Paid By': 'Paid By'
        }
        
        self.properties = [{'address': '123 Test St'}]

    @patch('pandas.read_excel')
    @patch('services.transaction_service.bulk_import_transactions')
    def test_process_bulk_import(self, mock_import, mock_read_excel):
        """Test bulk import processing."""
        mock_read_excel.return_value = self.test_data
        mock_import.return_value = 1
        
        results = process_bulk_import('test.xlsx', self.column_mapping, self.properties)
        
        self.assertEqual(results['total_rows'], 1)
        self.assertEqual(results['imported_count'], 1)
        self.assertEqual(results['skipped_rows'], 0)

    @patch('pandas.read_excel')
    def test_bulk_import_invalid_data(self, mock_read_excel):
        """Test bulk import with invalid data."""
        invalid_data = pd.DataFrame([{
            'Property': 'Invalid Address',
            'Amount': 'invalid',
            'Date Received or Paid': 'invalid',
            'Category': '',
            'Item Description': '',
            'Paid By': ''
        }])
        mock_read_excel.return_value = invalid_data
        
        results = process_bulk_import('test.xlsx', self.column_mapping, self.properties)
        
        self.assertEqual(results['total_rows'], 1)
        self.assertEqual(results['imported_count'], 0)
        self.assertGreater(results['skipped_rows'], 0)

    def test_bulk_import_edge_cases(self):
        """Test bulk import edge cases."""
        # Empty DataFrame
        empty_df = pd.DataFrame()
        with patch('pandas.read_excel', return_value=empty_df):
            results = process_bulk_import('test.xlsx', self.column_mapping, self.properties)
            self.assertEqual(results['total_rows'], 0)
            
        # Missing required columns
        invalid_mapping = {'Property': 'Invalid'}
        with patch('pandas.read_excel', return_value=self.test_data):
            results = process_bulk_import('test.xlsx', invalid_mapping, self.properties)
            self.assertEqual(results['imported_count'], 0)

if __name__ == '__main__':
    unittest.main()