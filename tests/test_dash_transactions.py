import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
import json
from dash.testing.composite import DashComposite
from dash.exceptions import PreventUpdate
from dash_transactions import (
    validate_date_range, validate_property_id, create_transactions_dash,
    process_summary_data, create_summary_report, create_detailed_report,
    VALID_TRANSACTION_TYPES, VALID_REIMBURSEMENT_STATUS,
    MIN_DATE, MAX_FUTURE_DAYS
)

class TestDateValidation(unittest.TestCase):
    """Test suite for date validation."""

    def test_valid_date_ranges(self):
        """Test valid date range combinations."""
        test_cases = [
            (None, None),  # Open range
            ('2024-01-01', None),  # Open end date
            (None, '2024-12-31'),  # Open start date
            ('2024-01-01', '2024-12-31')  # Specific range
        ]
        
        for start_date, end_date in test_cases:
            with self.subTest(start_date=start_date, end_date=end_date):
                is_valid, error = validate_date_range(start_date, end_date)
                self.assertTrue(is_valid)
                self.assertEqual(error, "")

    def test_invalid_date_ranges(self):
        """Test invalid date range combinations."""
        future_date = (datetime.now() + timedelta(days=MAX_FUTURE_DAYS + 1)).strftime('%Y-%m-%d')
        test_cases = [
            ('1999-01-01', '2024-01-01', "Start date cannot be before"),  # Before min date
            ('2024-01-01', future_date, "End date cannot be more than"),  # Too far in future
            ('2024-12-31', '2024-01-01', "Start date cannot be after end date"),  # Invalid range
            ('invalid', '2024-01-01', "Invalid date format"),  # Invalid format
        ]
        
        for start_date, end_date, expected_error in test_cases:
            with self.subTest(start_date=start_date, end_date=end_date):
                is_valid, error = validate_date_range(start_date, end_date)
                self.assertFalse(is_valid)
                self.assertIn(expected_error, error)

class TestPropertyValidation(unittest.TestCase):
    """Test suite for property validation."""

    def setUp(self):
        """Set up test data."""
        self.test_properties = [
            {'address': '123 Test St'},
            {'address': '456 Example Rd'}
        ]

    def test_property_validation(self):
        """Test property ID validation."""
        # Test valid cases
        self.assertTrue(validate_property_id(None, self.test_properties))
        self.assertTrue(validate_property_id('all', self.test_properties))
        self.assertTrue(validate_property_id('123 Test St', self.test_properties))
        
        # Test invalid cases
        self.assertFalse(validate_property_id('invalid', self.test_properties))
        self.assertFalse(validate_property_id('', self.test_properties))

class TestDashboardCreation(unittest.TestCase):
    """Test suite for dashboard creation and callbacks."""

    def setUp(self):
        """Set up test environment."""
        self.app = MagicMock()
        self.app.config = {}
        self.dash_app = create_transactions_dash(self.app)

    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        self.assertIsNotNone(self.dash_app.layout)
        self.assertIn('transactions-table', 
                     [child.id for child in self.dash_app.layout.children if hasattr(child, 'id')])
        self.assertIn('filter-options', 
                     [child.id for child in self.dash_app.layout.children if hasattr(child, 'id')])

    @patch('services.transaction_service.get_properties_for_user')
    @patch('services.transaction_service.get_transactions_for_view')
    def test_update_table_callback(self, mock_get_transactions, mock_get_properties):
        """Test table update callback."""
        mock_get_properties.return_value = [{'address': '123 Test St'}]
        mock_get_transactions.return_value = [{
            'id': '1',
            'type': 'income',
            'category': 'RENT',
            'amount': 1000,
            'date': '2024-01-01',
            'description': 'Test'
        }]
        
        @self.dash_app.callback_context
        def test_callback():
            outputs = self.dash_app.callback_map['transactions-table']['callback'](
                None, '123 Test St', 'income', 'all', '2024-01-01', '2024-12-31'
            )
            
            self.assertIsInstance(outputs[0], list)  # table data
            self.assertIsInstance(outputs[1], str)   # header
            self.assertIsInstance(outputs[2], list)  # property options
            self.assertIsInstance(outputs[3], list)  # columns

    def test_filter_options_callback(self):
        """Test filter options update callback."""
        @self.dash_app.callback_context
        def test_callback():
            filter_data = self.dash_app.callback_map['filter-options']['callback'](
                '123 Test St', 'income', 'all', '2024-01-01', '2024-12-31'
            )
            
            self.assertEqual(filter_data['property_id'], '123 Test St')
            self.assertEqual(filter_data['transaction_type'], 'income')
            self.assertEqual(filter_data['reimbursement_status'], 'all')

class TestReportGeneration(unittest.TestCase):
    """Test suite for report generation."""

    def setUp(self):
        """Set up test data."""
        self.test_transactions = [
            {
                'type': 'income',
                'category': 'RENT',
                'amount': 1000,
                'date': '2024-01-01',
                'description': 'Test Rent'
            },
            {
                'type': 'expense',
                'category': 'REPAIRS',
                'amount': 500,
                'date': '2024-01-15',
                'description': 'Test Repair'
            }
        ]

    def test_process_summary_data(self):
        """Test summary data processing."""
        summary = process_summary_data(self.test_transactions)
        
        self.assertIn('income', summary)
        self.assertIn('expense', summary)
        self.assertEqual(summary['income'].loc['RENT', 'count'], 1)
        self.assertEqual(summary['expense'].loc['REPAIRS', 'count'], 1)

    def test_create_summary_report(self):
        """Test summary report creation."""
        summary = process_summary_data(self.test_transactions)
        elements = create_summary_report(summary, getSampleStyleSheet())
        
        self.assertGreater(len(elements), 0)
        self.assertIsInstance(elements[0], Paragraph)

    def test_create_detailed_report(self):
        """Test detailed report creation."""
        elements = create_detailed_report(self.test_transactions, getSampleStyleSheet())
        
        self.assertGreater(len(elements), 0)
        self.assertIsInstance(elements[0], Table)

class TestErrorHandling(unittest.TestCase):
    """Test suite for error handling."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_transactions_dash(MagicMock())

    @patch('services.transaction_service.get_properties_for_user')
    def test_invalid_transaction_type(self, mock_get_properties):
        """Test handling of invalid transaction type."""
        @self.app.callback_context
        def test_callback():
            outputs = self.app.callback_map['transactions-table']['callback'](
                None, '123 Test St', 'invalid_type', 'all', '2024-01-01', '2024-12-31'
            )
            self.assertEqual(outputs[1], "Invalid transaction type")

    @patch('services.transaction_service.get_properties_for_user')
    def test_invalid_reimbursement_status(self, mock_get_properties):
        """Test handling of invalid reimbursement status."""
        @self.app.callback_context
        def test_callback():
            outputs = self.app.callback_map['transactions-table']['callback'](
                None, '123 Test St', 'income', 'invalid_status', '2024-01-01', '2024-12-31'
            )
            self.assertEqual(outputs[1], "Invalid reimbursement status")

    @patch('services.transaction_service.get_properties_for_user')
    def test_service_error_handling(self, mock_get_properties):
        """Test handling of service errors."""
        mock_get_properties.side_effect = Exception("Test error")
        
        @self.app.callback_context
        def test_callback():
            outputs = self.app.callback_map['transactions-table']['callback'](
                None, '123 Test St', 'income', 'all', '2024-01-01', '2024-12-31'
            )
            self.assertEqual(outputs[1], "Error loading properties")

if __name__ == '__main__':
    unittest.main()