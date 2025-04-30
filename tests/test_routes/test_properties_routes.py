import unittest
from unittest.mock import patch, mock_open, MagicMock
from flask import json
from decimal import Decimal
from datetime import datetime
import os
from app import create_app
from routes.properties import validate_property_data, validate_partners_data, sanitize_property_data

class TestPropertiesRoutes(unittest.TestCase):
    """Test suite for property routes."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Sample valid property data
        self.valid_property = {
            'address': '123 Test St',
            'purchase_price': 200000,
            'down_payment': 40000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'purchase_date': '2024-01-01',
            'loan_amount': 160000,
            'loan_start_date': '2024-01-01',
            'partners': [
                {'name': 'Test User', 'equity_share': 100}
            ]
        }
        
        # Create test user session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test@example.com'
            sess['_fresh'] = True

    def tearDown(self):
        """Clean up after tests."""
        self.ctx.pop()

    def login_as_admin(self):
        """Helper to simulate admin login."""
        with patch('flask_login.current_user') as mock_user:
            mock_user.is_authenticated = True
            mock_user.role = 'Admin'
            mock_user.name = 'Test Admin'
            mock_user.email = 'admin@example.com'
            return mock_user

    def login_as_user(self):
        """Helper to simulate regular user login."""
        with patch('flask_login.current_user') as mock_user:
            mock_user.is_authenticated = True
            mock_user.role = 'User'
            mock_user.name = 'Test User'
            mock_user.email = 'user@example.com'
            return mock_user

    def test_add_properties_get(self):
        """Test GET request to add properties page."""
        mock_user = self.login_as_user()
        
        with patch('builtins.open', mock_open(read_data='[]')):
            response = self.client.get('/properties/add_properties')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'add_properties.html', response.data)

    @patch('builtins.open', new_callable=mock_open)
    def test_add_property_success(self, mock_file):
        """Test successful property addition."""
        mock_user = self.login_as_user()
        mock_file.return_value.read.return_value = '[]'
        
        response = self.client.post(
            '/properties/add_properties',
            json=self.valid_property,
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('Property added successfully', data['message'])

    def test_add_property_validation(self):
        """Test property validation during addition."""
        mock_user = self.login_as_user()
        
        invalid_property = self.valid_property.copy()
        invalid_property['purchase_price'] = -1000
        
        response = self.client.post(
            '/properties/add_properties',
            json=invalid_property,
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

    @patch('builtins.open', new_callable=mock_open)
    def test_edit_properties_get(self, mock_file):
        """Test GET request to edit properties page."""
        mock_user = self.login_as_admin()
        mock_file.return_value.read.return_value = json.dumps([self.valid_property])
        
        response = self.client.get('/properties/edit_properties')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'edit_properties.html', response.data)

    @patch('builtins.open', new_callable=mock_open)
    def test_edit_property_success(self, mock_file):
        """Test successful property edit."""
        mock_user = self.login_as_admin()
        mock_file.return_value.read.return_value = json.dumps([self.valid_property])
        
        edited_property = self.valid_property.copy()
        edited_property['purchase_price'] = 210000
        
        response = self.client.post(
            '/properties/edit_properties',
            json=edited_property,
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_edit_property_unauthorized(self):
        """Test property edit by unauthorized user."""
        mock_user = self.login_as_user()
        
        property_data = self.valid_property.copy()
        property_data['partners'] = [{'name': 'Other User', 'equity_share': 100}]
        
        response = self.client.post(
            '/properties/edit_properties',
            json=property_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 403)

    @patch('builtins.open', new_callable=mock_open)
    def test_remove_property_success(self, mock_file):
        """Test successful property removal."""
        mock_user = self.login_as_admin()
        mock_file.return_value.read.return_value = json.dumps([self.valid_property])
        
        form_data = {
            'property_select': '123 Test St',
            'confirm_input': 'I am sure I want to do this.'
        }
        
        response = self.client.post('/properties/remove_properties', data=form_data)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_remove_property_unauthorized(self):
        """Test property removal by unauthorized user."""
        mock_user = self.login_as_user()
        
        response = self.client.post('/properties/remove_properties')
        self.assertEqual(response.status_code, 403)

    def test_get_property_details_success(self):
        """Test successful property details retrieval."""
        mock_user = self.login_as_user()
        
        with patch('builtins.open', mock_open(read_data=json.dumps([self.valid_property]))):
            response = self.client.get(
                '/properties/get_property_details?address=123 Test St'
            )
            
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('property', data)

    def test_get_property_details_not_found(self):
        """Test property details retrieval for non-existent property."""
        mock_user = self.login_as_user()
        
        with patch('builtins.open', mock_open(read_data='[]')):
            response = self.client.get(
                '/properties/get_property_details?address=nonexistent'
            )
            
            self.assertEqual(response.status_code, 404)

    def test_get_available_partners(self):
        """Test available partners retrieval."""
        mock_user = self.login_as_user()
        test_properties = [
            {
                'address': '123 Test St',
                'partners': [
                    {'name': 'Test User', 'equity_share': 50},
                    {'name': 'Partner User', 'equity_share': 50}
                ]
            }
        ]
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_properties))):
            response = self.client.get('/properties/get_available_partners')
            data = json.loads(response.data)
            
            self.assertTrue(data['success'])
            self.assertIn('partners', data)
            self.assertEqual(len(data['partners']), 2)

class TestPropertyValidation(unittest.TestCase):
    """Test suite for property validation functions."""

    def test_validate_property_data(self):
        """Test property data validation."""
        valid_property = {
            'address': '123 Test St',
            'purchase_price': 200000,
            'down_payment': 40000,
            'primary_loan_rate': 4.5,
            'primary_loan_term': 360,
            'purchase_date': '2024-01-01',
            'loan_amount': 160000,
            'loan_start_date': '2024-01-01',
            'partners': [{'name': 'Test User', 'equity_share': 100}]
        }
        
        is_valid, errors = validate_property_data(valid_property)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_property_data_invalid(self):
        """Test property data validation with invalid data."""
        invalid_cases = [
            ({}, "missing required fields"),
            (
                {'address': '', 'purchase_price': -1000},
                "invalid values"
            ),
            (
                {'address': '123 Test St', 'purchase_date': 'invalid-date'},
                "invalid date format"
            )
        ]
        
        for invalid_data, case_name in invalid_cases:
            with self.subTest(case=case_name):
                is_valid, errors = validate_property_data(invalid_data)
                self.assertFalse(is_valid)
                self.assertTrue(len(errors) > 0)

    def test_validate_partners_data(self):
        """Test partners data validation."""
        valid_partners = [
            {'name': 'Partner 1', 'equity_share': 60},
            {'name': 'Partner 2', 'equity_share': 40}
        ]
        
        errors = validate_partners_data(valid_partners)
        self.assertEqual(len(errors), 0)

    def test_validate_partners_data_invalid(self):
        """Test partners data validation with invalid data."""
        invalid_cases = [
            ([], "empty partners list"),
            (
                [{'name': '', 'equity_share': 100}],
                "empty partner name"
            ),
            (
                [{'name': 'Partner 1', 'equity_share': 90}],
                "total not 100%"
            )
        ]
        
        for invalid_data, case_name in invalid_cases:
            with self.subTest(case=case_name):
                errors = validate_partners_data(invalid_data)
                self.assertTrue(len(errors) > 0)

    def test_sanitize_property_data(self):
        """Test property data sanitization."""
        raw_data = {
            'address': ' 123 Test St ',
            'purchase_price': '200000',
            'monthly_income': {'rental_income': '2000'},
            'monthly_expenses': {
                'utilities': {
                    'water': '100',
                    'electricity': '150'
                }
            },
            'partners': [{'name': 'Test User', 'equity_share': 100}]
        }
        
        sanitized = sanitize_property_data(raw_data)
        self.assertEqual(sanitized['address'], '123 Test St')
        self.assertIsInstance(sanitized['purchase_price'], float)
        self.assertIsInstance(sanitized['monthly_income']['rental_income'], float)
        self.assertIsInstance(sanitized['monthly_expenses']['utilities']['water'], float)

if __name__ == '__main__':
    unittest.main()