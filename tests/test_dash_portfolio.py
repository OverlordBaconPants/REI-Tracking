import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from dash.testing.composite import DashComposite
from dash_portfolio import (
    safe_float, validate_property_data, calculate_user_equity_share,
    calculate_loan_metrics, calculate_monthly_cashflow, generate_color_scale,
    create_portfolio_dash
)

class TestUtilityFunctions(unittest.TestCase):
    """Test suite for utility functions."""

    def test_safe_float(self):
        """Test safe float conversion."""
        test_cases = [
            ('$1,234.56', 1234.56),
            ('1234.56', 1234.56),
            (1234.56, 1234.56),
            (None, 0.0),
            ('invalid', 0.0),
            ('', 0.0),
            ('$-1,234.56', -1234.56)
        ]
        
        for input_val, expected in test_cases:
            with self.subTest(input_val=input_val):
                result = safe_float(input_val)
                self.assertEqual(result, expected)

    def test_generate_color_scale(self):
        """Test color scale generation."""
        # Test with different numbers of colors
        self.assertEqual(len(generate_color_scale(5)), 5)
        self.assertEqual(generate_color_scale(0), [])
        self.assertEqual(generate_color_scale(1), ['#000080'])
        
        # Test color format
        colors = generate_color_scale(3)
        for color in colors:
            self.assertTrue(color.startswith('#'))
            self.assertEqual(len(color), 7)

class TestPropertyValidation(unittest.TestCase):
    """Test suite for property data validation."""

    def setUp(self):
        """Set up test data."""
        self.valid_property = {
            'address': '123 Test St',
            'loan_amount': 200000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'loan_start_date': '2024-01-01',
            'purchase_price': 250000,
            'monthly_income': {'rental_income': 2000},
            'monthly_expenses': {'property_tax': 200},
            'partners': [{'name': 'Test User', 'equity_share': 100}]
        }

    def test_validate_property_data(self):
        """Test property data validation."""
        # Test valid property
        is_valid, error = validate_property_data(self.valid_property, 'Test User')
        self.assertTrue(is_valid)
        self.assertEqual(error, '')
        
        # Test missing required fields
        invalid_property = self.valid_property.copy()
        del invalid_property['loan_amount']
        is_valid, error = validate_property_data(invalid_property, 'Test User')
        self.assertFalse(is_valid)
        self.assertIn('loan_amount', error)

    def test_calculate_user_equity_share(self):
        """Test equity share calculation."""
        share = calculate_user_equity_share(self.valid_property, 'Test User')
        self.assertEqual(share, 1.0)
        
        # Test non-existent user
        share = calculate_user_equity_share(self.valid_property, 'Non Existent')
        self.assertEqual(share, 0.0)

class TestFinancialCalculations(unittest.TestCase):
    """Test suite for financial calculations."""

    def setUp(self):
        """Set up test data."""
        self.property_data = {
            'address': '123 Test St',
            'loan_amount': 200000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'loan_start_date': '2024-01-01',
            'purchase_price': 250000,
            'monthly_income': {
                'rental_income': 2000,
                'parking_income': 100
            },
            'monthly_expenses': {
                'property_tax': 200,
                'insurance': 100,
                'utilities': {}
            },
            'partners': [{'name': 'Test User', 'equity_share': 100}]
        }

    def test_calculate_loan_metrics(self):
        """Test loan metrics calculation."""
        metrics = calculate_loan_metrics(self.property_data, 'Test User')
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['address'], '123 Test St')
        self.assertEqual(metrics['purchase_price'], 250000)
        self.assertEqual(metrics['loan_amount'], 200000)
        self.assertTrue(metrics['monthly_payment'] > 0)

    def test_calculate_monthly_cashflow(self):
        """Test monthly cash flow calculation."""
        cashflow = calculate_monthly_cashflow(self.property_data, 'Test User')
        
        self.assertIsNotNone(cashflow)
        self.assertEqual(cashflow['address'], '123 Test St')
        self.assertEqual(cashflow['monthly_income'], 2100)  # 2000 + 100
        self.assertTrue(cashflow['net_cashflow'] > 0)

class TestDashboardCreation(unittest.TestCase):
    """Test suite for dashboard creation and callbacks."""

    def setUp(self):
        """Set up test environment."""
        self.app = MagicMock()
        self.app.config = {}
        self.dash_app = create_portfolio_dash(self.app)

    def test_dashboard_initialization(self):
        """Test dashboard initialization."""
        self.assertIsNotNone(self.dash_app.layout)
        self.assertIn('session-store', 
                     [child.id for child in self.dash_app.layout.children if hasattr(child, 'id')])

    @patch('services.transaction_service.get_properties_for_user')
    def test_update_metrics_no_properties(self, mock_get_properties):
        """Test metrics update with no properties."""
        mock_get_properties.return_value = []
        
        @self.dash_app.callback_context
        def test_callback():
            outputs = self.dash_app.callback_map['user-context']['callback'](None)
            self.assertIn('No properties found', str(outputs[12]))  # Error message
            self.assertEqual(outputs[1], '$0.00')  # Portfolio value

    @patch('services.transaction_service.get_properties_for_user')
    def test_update_metrics_with_properties(self, mock_get_properties):
        """Test metrics update with properties."""
        mock_get_properties.return_value = [{
            'address': '123 Test St',
            'loan_amount': 200000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'loan_start_date': '2024-01-01',
            'purchase_price': 250000,
            'monthly_income': {'rental_income': 2000},
            'monthly_expenses': {'property_tax': 200},
            'partners': [{'name': 'Test User', 'equity_share': 100}]
        }]
        
        @self.dash_app.callback_context
        def test_callback():
            outputs = self.dash_app.callback_map['user-context']['callback'](None)
            self.assertEqual(outputs[13]['display'], 'none')  # No error
            self.assertNotEqual(outputs[1], '$0.00')  # Portfolio value not zero

class TestVisualizationGeneration(unittest.TestCase):
    """Test suite for visualization generation."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_portfolio_dash(MagicMock())
        self.test_property = {
            'address': '123 Test St',
            'loan_amount': 200000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'loan_start_date': '2024-01-01',
            'purchase_price': 250000,
            'monthly_income': {'rental_income': 2000},
            'monthly_expenses': {'property_tax': 200},
            'partners': [{'name': 'Test User', 'equity_share': 100}]
        }

    @patch('services.transaction_service.get_properties_for_user')
    def test_chart_generation(self, mock_get_properties):
        """Test chart generation."""
        mock_get_properties.return_value = [self.test_property]
        
        @self.app.callback_context
        def test_callback():
            outputs = self.app.callback_map['user-context']['callback'](None)
            
            # Test equity pie chart
            equity_chart = outputs[7]
            self.assertEqual(equity_chart['data'][0]['type'], 'pie')
            self.assertTrue(len(equity_chart['data'][0]['values']) > 0)
            
            # Test cashflow bar chart
            cashflow_chart = outputs[8]
            self.assertEqual(cashflow_chart['data'][0]['type'], 'bar')
            
            # Test expense pie chart
            expense_chart = outputs[10]
            self.assertEqual(expense_chart['data'][0]['type'], 'pie')

class TestErrorHandling(unittest.TestCase):
    """Test suite for error handling."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_portfolio_dash(MagicMock())

    def test_invalid_property_data(self):
        """Test handling of invalid property data."""
        @self.app.callback_context
        @patch('services.transaction_service.get_properties_for_user')
        def test_callback(mock_get_properties):
            mock_get_properties.return_value = [{'invalid': 'data'}]
            outputs = self.app.callback_map['user-context']['callback'](None)
            self.assertEqual(outputs[13]['display'], 'block')  # Error visible
            self.assertIn('error', outputs[12].lower())  # Error message

    def test_calculation_errors(self):
        """Test handling of calculation errors."""
        @self.app.callback_context
        @patch('services.transaction_service.get_properties_for_user')
        def test_callback(mock_get_properties):
            mock_get_properties.side_effect = ValueError("Test error")
            outputs = self.app.callback_map['user-context']['callback'](None)
            self.assertEqual(outputs[13]['display'], 'block')
            self.assertIn('error', outputs[12].lower())

if __name__ == '__main__':
    unittest.main()