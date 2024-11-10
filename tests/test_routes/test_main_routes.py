import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import pandas as pd
from flask import url_for
from app import create_app
import json

class TestMainRoutes(unittest.TestCase):
    """Test suite for main routes."""

    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Sample test data
        self.test_property = {
            'address': '123 Test St',
            'loan_amount': 200000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'loan_start_date': '2024-01-01',
            'purchase_price': 250000
        }
        
        self.test_user = {
            'email': 'test@example.com',
            'name': 'Test User',
            'id': 'test@example.com'
        }

    def tearDown(self):
        """Clean up after each test."""
        self.ctx.pop()

    def login(self, email='test@example.com'):
        """Helper method to simulate user login."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = email
            sess['_fresh'] = True

    def test_index_unauthenticated(self):
        """Test index page for unauthenticated users."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'landing.html', response.data)

    @patch('routes.main.get_properties_for_user')
    @patch('routes.main.get_user_by_email')
    def test_index_authenticated_with_properties(self, mock_get_user, mock_get_properties):
        """Test index page for authenticated users with properties."""
        self.login()
        mock_get_user.return_value = self.test_user
        mock_get_properties.return_value = [self.test_property]
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/main', response.location)

    @patch('routes.main.get_properties_for_user')
    @patch('routes.main.get_user_by_email')
    def test_index_authenticated_no_properties(self, mock_get_user, mock_get_properties):
        """Test index page for authenticated users without properties."""
        self.login()
        mock_get_user.return_value = self.test_user
        mock_get_properties.return_value = []
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'new_user_welcome.html', response.data)

    def test_validate_loan_data(self):
        """Test loan data validation."""
        # Valid cases
        self.assertTrue(validate_loan_data(200000, 4.5, 30))
        
        # Invalid cases
        invalid_cases = [
            (0, 4.5, 30),           # Zero loan amount
            (200000, 0, 30),        # Zero interest rate
            (200000, 4.5, 0),       # Zero years
            (200000, 101, 30),      # Interest rate > 100
            (200000, 4.5, 101),     # Years > 100
            ('invalid', 4.5, 30),   # Invalid type
            (200000, 4.5, 'invalid')  # Invalid type
        ]
        
        for amount, rate, years in invalid_cases:
            with self.subTest(amount=amount, rate=rate, years=years):
                self.assertFalse(validate_loan_data(amount, rate, years))

    def test_amortize(self):
        """Test amortization calculation."""
        # Test valid calculation
        schedule = list(amortize(200000, 0.045, 30))
        self.assertTrue(len(schedule) > 0)
        self.assertEqual(len(schedule), 360)  # 30 years * 12 months
        
        # Verify first payment
        first_payment = schedule[0]
        self.assertIn('month', first_payment)
        self.assertIn('payment', first_payment)
        self.assertIn('principal', first_payment)
        self.assertIn('interest', first_payment)
        self.assertIn('balance', first_payment)
        
        # Test invalid inputs
        with self.assertRaises(ValueError):
            list(amortize(0, 0.045, 30))
        
        with self.assertRaises(ValueError):
            list(amortize(200000, 0, 30))

    def test_calculate_equity(self):
        """Test equity calculation."""
        with patch('routes.main.get_properties_for_user') as mock_get_properties:
            mock_get_properties.return_value = [self.test_property]
            
            equity = calculate_equity('123 Test St')
            self.assertIsInstance(equity, dict)
            self.assertIn('last_month_equity', equity)
            self.assertIn('equity_gained_since_acquisition', equity)
            
            # Test nonexistent property
            equity = calculate_equity('456 Fake St')
            self.assertEqual(equity['last_month_equity'], 0)
            self.assertEqual(equity['equity_gained_since_acquisition'], 0)

    def test_calculate_cumulative_amortization(self):
        """Test cumulative amortization calculation."""
        test_properties = [self.test_property]
        result = calculate_cumulative_amortization(test_properties)
        
        self.assertIsInstance(result, list)
        if result:  # If properties were valid
            self.assertIn('Portfolio Loan Balance', result[0])
            self.assertIn('Portfolio Interest', result[0])
            self.assertIn('Portfolio Principal', result[0])
        
        # Test with empty properties
        self.assertEqual(calculate_cumulative_amortization([]), [])
        
        # Test with invalid property data
        invalid_property = self.test_property.copy()
        del invalid_property['loan_amount']
        self.assertEqual(calculate_cumulative_amortization([invalid_property]), [])

    @patch('routes.main.get_user_by_email')
    @patch('routes.main.get_properties_for_user')
    @patch('routes.main.get_transactions_for_view')
    def test_main_dashboard(self, mock_transactions, mock_properties, mock_user):
        """Test main dashboard view."""
        self.login()
        mock_user.return_value = self.test_user
        mock_properties.return_value = [self.test_property]
        mock_transactions.return_value = []
        
        response = self.client.get('/main')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'main.html', response.data)

    @patch('routes.main.get_user_by_email')
    def test_main_dashboard_user_not_found(self, mock_user):
        """Test main dashboard when user is not found."""
        self.login()
        mock_user.return_value = None
        
        response = self.client.get('/main')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.location)

    def test_main_dashboard_unauthenticated(self):
        """Test main dashboard access without authentication."""
        response = self.client.get('/main')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_properties_view(self):
        """Test properties view."""
        self.login()
        response = self.client.get('/properties')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'properties.html', response.data)

    def test_test_flash(self):
        """Test flash message functionality."""
        response = self.client.get('/test-flash', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        data = response.get_data(as_text=True)
        
        self.assertIn('success message', data)
        self.assertIn('error message', data)
        self.assertIn('warning message', data)
        self.assertIn('info message', data)

class TestCalculations(unittest.TestCase):
    """Test suite for calculation functions."""

    def test_amortization_edge_cases(self):
        """Test amortization calculation edge cases."""
        test_cases = [
            (100000, 0.001, 30),  # Very low interest rate
            (1000000, 0.10, 5),   # Short term, high rate
            (50000, 0.05, 15)     # Mid-range values
        ]
        
        for principal, rate, years in test_cases:
            with self.subTest(principal=principal, rate=rate, years=years):
                schedule = list(amortize(principal, rate, years))
                self.assertEqual(len(schedule), int(years * 12))
                self.assertGreater(schedule[0]['balance'], schedule[-1]['balance'])

    def test_equity_calculation_edge_cases(self):
        """Test equity calculation edge cases."""
        test_properties = [
            {
                'address': 'Test St',
                'loan_amount': '200000',
                'primary_loan_rate': '4.5',
                'primary_loan_term': '360',
                'loan_start_date': (date.today() + relativedelta(months=1)).strftime('%Y-%m-%d')  # Future start
            },
            {
                'address': 'Test Ave',
                'loan_amount': '200000',
                'primary_loan_rate': '4.5',
                'primary_loan_term': '360',
                'loan_start_date': (date.today() - relativedelta(years=5)).strftime('%Y-%m-%d')  # Past start
            }
        ]
        
        with patch('routes.main.get_properties_for_user') as mock_get_properties:
            for prop in test_properties:
                mock_get_properties.return_value = [prop]
                equity = calculate_equity(prop['address'])
                self.assertIsInstance(equity['last_month_equity'], float)
                self.assertIsInstance(equity['equity_gained_since_acquisition'], float)

    def test_cumulative_amortization_edge_cases(self):
        """Test cumulative amortization calculation edge cases."""
        # Test with multiple properties starting at different times
        test_properties = [
            {
                'address': '123 Test St',
                'loan_amount': 200000,
                'primary_loan_rate': 4.5,
                'primary_loan_term': 360,
                'loan_start_date': '2024-01-01'
            },
            {
                'address': '456 Test Ave',
                'loan_amount': 150000,
                'primary_loan_rate': 5.0,
                'primary_loan_term': 180,
                'loan_start_date': '2024-06-01'
            }
        ]
        
        result = calculate_cumulative_amortization(test_properties)
        self.assertTrue(len(result) > 0)
        
        # Verify cumulative calculations
        if result:
            self.assertTrue(result[-1]['Portfolio Principal'] > result[0]['Portfolio Principal'])
            self.assertTrue(result[0]['Portfolio Loan Balance'] > result[-1]['Portfolio Loan Balance'])

if __name__ == '__main__':
    unittest.main()