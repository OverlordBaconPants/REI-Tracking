import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dash.testing.application_runners import import_app
from dash.testing.composite import DashComposite
from dash_amortization import (
    validate_loan_data, amortize, create_amortization_dash,
    create_error_response
)

class TestLoanValidation(unittest.TestCase):
    """Test suite for loan data validation."""

    def test_valid_loan_data(self):
        """Test validation with valid loan data."""
        test_cases = [
            (100000, 0.05, 30),  # Standard 30-year loan
            (500000, 0.03, 15),  # 15-year loan
            (1000, 0.10, 5),     # Short-term high-interest loan
            (999999, 0.001, 40)  # Long-term low-interest loan
        ]
        
        for amount, rate, years in test_cases:
            with self.subTest(amount=amount, rate=rate, years=years):
                is_valid, error = validate_loan_data(amount, rate, years)
                self.assertTrue(is_valid)
                self.assertEqual(error, "")

    def test_invalid_loan_data(self):
        """Test validation with invalid loan data."""
        test_cases = [
            (0, 0.05, 30, "Loan amount must be greater than 0"),
            (-1000, 0.05, 30, "Loan amount must be greater than 0"),
            (100000, 0, 30, "Interest rate must be greater than 0"),
            (100000, -0.05, 30, "Interest rate must be greater than 0"),
            (100000, 0.05, 0, "Loan term must be greater than 0"),
            (100000, 0.05, -10, "Loan term must be greater than 0"),
            (None, 0.05, 30, "Loan amount must be greater than 0"),
            (100000, None, 30, "Interest rate must be greater than 0"),
            (100000, 0.05, None, "Loan term must be greater than 0")
        ]
        
        for amount, rate, years, expected_error in test_cases:
            with self.subTest(amount=amount, rate=rate, years=years):
                is_valid, error = validate_loan_data(amount, rate, years)
                self.assertFalse(is_valid)
                self.assertEqual(error, expected_error)

class TestAmortizationCalculation(unittest.TestCase):
    """Test suite for amortization calculations."""

    def test_amortization_calculation(self):
        """Test basic amortization calculation."""
        # Calculate amortization schedule
        schedule = list(amortize(100000, 0.05, 30))
        
        # Verify schedule length
        self.assertEqual(len(schedule), 360)  # 30 years * 12 months
        
        # Verify first payment
        first = schedule[0]
        self.assertEqual(first['month'], 1)
        self.assertGreater(first['payment'], 0)
        self.assertGreater(first['principal'], 0)
        self.assertGreater(first['interest'], 0)
        self.assertLess(first['balance'], 100000)
        
        # Verify last payment
        last = schedule[-1]
        self.assertAlmostEqual(last['balance'], 0, places=2)
        self.assertGreater(last['cumulative_interest'], 0)
        self.assertAlmostEqual(
            last['cumulative_principal'],
            100000,
            places=2
        )

    def test_amortization_accuracy(self):
        """Test accuracy of amortization calculations."""
        schedule = list(amortize(200000, 0.045, 30))
        
        # Verify payment consistency
        payments = [round(row['payment'], 2) for row in schedule]
        self.assertEqual(len(set(payments)), 1)  # All payments should be equal
        
        # Verify total paid equals principal plus interest
        last = schedule[-1]
        total_paid = last['cumulative_principal'] + last['cumulative_interest']
        total_payments = last['payment'] * len(schedule)
        self.assertAlmostEqual(total_paid, total_payments, places=2)

    def test_invalid_inputs(self):
        """Test amortization with invalid inputs."""
        invalid_cases = [
            (0, 0.05, 30),
            (100000, 0, 30),
            (100000, 0.05, 0),
            (-100000, 0.05, 30),
            (100000, -0.05, 30),
            (100000, 0.05, -30)
        ]
        
        for amount, rate, years in invalid_cases:
            with self.subTest(amount=amount, rate=rate, years=years):
                with self.assertRaises(ValueError):
                    list(amortize(amount, rate, years))

class TestDashboardCreation(unittest.TestCase):
    """Test suite for dashboard creation and callbacks."""

    def setUp(self):
        """Set up test environment."""
        self.app = MagicMock()
        self.app.config = {}
        self.dash_app = create_amortization_dash(self.app)
        self.test_property = {
            'address': '123 Test St',
            'loan_amount': 200000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'loan_start_date': '2024-01-01'
        }

    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        self.assertIsNotNone(self.dash_app.layout)
        self.assertIn('property-selector', self.dash_app.layout.children[1].children[0].children[1].id)
        self.assertIn('amortization-graph', 
                     [child.id for child in self.dash_app.layout.children if hasattr(child, 'id')])
        self.assertIn('amortization-table', 
                     [child.id for child in self.dash_app.layout.children if hasattr(child, 'id')])

    @patch('services.transaction_service.get_properties_for_user')
    def test_property_dropdown_population(self, mock_get_properties):
        """Test property dropdown population."""
        mock_get_properties.return_value = [
            {'address': '123 Test St, City, State'},
            {'address': '456 Other St, City, State'}
        ]
        
        @self.dash_app.callback_context
        def test_callback():
            options = self.dash_app.callback_map['property-selector']['callback']()
            self.assertEqual(len(options), 2)
            self.assertEqual(options[0]['label'], '123 Test St')
            self.assertEqual(options[1]['label'], '456 Other St')

    @patch('services.transaction_service.get_properties_for_user')
    def test_amortization_update(self, mock_get_properties):
        """Test amortization update callback."""
        mock_get_properties.return_value = [self.test_property]
        
        @self.dash_app.callback_context
        def test_callback():
            results = self.dash_app.callback_map['loan-info']['callback']('123 Test St')
            
            self.assertIsNotNone(results[0])  # loan info
            self.assertIsNotNone(results[1])  # figure
            self.assertIsNotNone(results[2])  # table data
            self.assertIsNotNone(results[3])  # columns
            self.assertEqual(results[5], "")   # no error
            self.assertEqual(results[6]['display'], 'none')  # error hidden

class TestErrorHandling(unittest.TestCase):
    """Test suite for error handling."""

    def test_error_response_creation(self):
        """Test error response creation."""
        error_msg = "Test error"
        response = create_error_response(error_msg)
        
        self.assertEqual(len(response), 7)  # Should return 7 elements
        self.assertIn(error_msg, response[5])  # Error message
        self.assertEqual(response[6]['display'], 'block')  # Error visible

    def test_invalid_property_selection(self):
        """Test handling of invalid property selection."""
        app = create_amortization_dash(MagicMock())
        
        @app.callback_context
        def test_callback():
            results = app.callback_map['loan-info']['callback'](None)
            self.assertIn("No property selected", str(results[0]))

    def test_missing_loan_data(self):
        """Test handling of missing loan data."""
        app = create_amortization_dash(MagicMock())
        invalid_property = {
            'address': '123 Test St'
            # Missing loan data
        }
        
        @app.callback_context
        @patch('services.transaction_service.get_properties_for_user')
        def test_callback(mock_get_properties):
            mock_get_properties.return_value = [invalid_property]
            results = app.callback_map['loan-info']['callback']('123 Test St')
            self.assertIn("Missing required loan information", str(results[5]))

if __name__ == '__main__':
    unittest.main()