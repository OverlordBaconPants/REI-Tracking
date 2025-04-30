import unittest
from unittest.mock import patch, mock_open, MagicMock
from flask import json
from app import create_app
from datetime import datetime, timezone
import os
import uuid
from io import BytesIO

class TestAnalysesRoutes(unittest.TestCase):
    """Test suite for analysis routes."""

    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Sample test data
        self.test_analysis = {
            'analysis_type': 'BRRRR',
            'analysis_name': 'Test Analysis',
            'property_address': '123 Test St',
            'purchase_price': '200000',
            'after_repair_value': '250000',
            'renovation_costs': '30000',
            'renovation_duration': '3',
            'monthly_rent': '2000',
            'operating_expenses': {
                'property_taxes': '2400',
                'insurance': '1200',
                'management': '10',
                'capex': '5',
                'vacancy': '5'
            },
            'initial_loan': {
                'amount': '160000',
                'rate': '7.5',
                'term': '360'
            }
        }
        
        # Create test user session
        with self.client.session_transaction() as sess:
            sess['user_id'] = '123'
            sess['_fresh'] = True

    def tearDown(self):
        """Clean up after each test."""
        self.ctx.pop()

    def test_create_analysis_get_unauthorized(self):
        """Test GET create_analysis without authentication."""
        with self.client.session_transaction() as sess:
            sess.clear()
        response = self.client.get('/create_analysis')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_create_analysis_get_authorized(self):
        """Test GET create_analysis with authentication."""
        response = self.client.get('/create_analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'create_analysis.html', response.data)

    @patch('services.analysis_calculations.create_analysis')
    def test_create_analysis_post_success(self, mock_create):
        """Test successful analysis creation."""
        mock_create.return_value = MagicMock(
            purchase_price=MagicMock(format=lambda: '$200,000'),
            after_repair_value=MagicMock(format=lambda: '$250,000'),
            renovation_costs=MagicMock(format=lambda: '$30,000'),
            monthly_rent=MagicMock(format=lambda: '$2,000'),
            calculate_monthly_cash_flow=MagicMock(return_value=MagicMock(format=lambda: '$500')),
            calculate_annual_cash_flow=MagicMock(return_value=MagicMock(format=lambda: '$6,000')),
            operating_expenses=MagicMock(
                calculate_total=MagicMock(return_value=MagicMock(format=lambda: '$800')),
                property_taxes=MagicMock(format=lambda: '$200'),
                insurance=MagicMock(format=lambda: '$100'),
                calculate_management_fee=MagicMock(return_value=MagicMock(format=lambda: '$200')),
                calculate_capex=MagicMock(return_value=MagicMock(format=lambda: '$100')),
                calculate_vacancy=MagicMock(return_value=MagicMock(format=lambda: '$200'))
            ),
            calculate_total_cash_invested=MagicMock(return_value=MagicMock(format=lambda: '$70,000'))
        )

        response = self.client.post(
            '/create_analysis',
            json=self.test_analysis,
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('Analysis created successfully', data['message'])
        self.assertIn('analysis', data)

    def test_create_analysis_post_invalid_data(self):
        """Test analysis creation with invalid data."""
        invalid_analysis = {'invalid': 'data'}
        response = self.client.post(
            '/create_analysis',
            json=invalid_analysis,
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data['message'].lower())

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_analysis_success(self, mock_file, mock_exists):
        """Test successful retrieval of analysis."""
        analysis_id = str(uuid.uuid4())
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.test_analysis)

        response = self.client.get(f'/get_analysis/{analysis_id}')
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('analysis', data)

    def test_get_analysis_not_found(self):
        """Test getting non-existent analysis."""
        response = self.client.get(f'/get_analysis/{uuid.uuid4()}')
        data = json.loads(response.data)
        
        self.assertFalse(data['success'])
        self.assertIn('not found', data['message'].lower())

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_update_analysis_success(self, mock_file, mock_exists):
        """Test successful analysis update."""
        analysis_id = str(uuid.uuid4())
        self.test_analysis['id'] = analysis_id
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(self.test_analysis)

        response = self.client.post(
            '/update_analysis',
            json=self.test_analysis,
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('updated successfully', data['message'].lower())

    def test_update_analysis_missing_id(self):
        """Test analysis update without ID."""
        invalid_analysis = self.test_analysis.copy()
        invalid_analysis.pop('id', None)
        
        response = self.client.post(
            '/update_analysis',
            json=invalid_analysis,
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('id is required', data['message'].lower())

    def test_view_edit_analysis_unauthorized(self):
        """Test view/edit analysis page without authentication."""
        with self.client.session_transaction() as sess:
            sess.clear()
        response = self.client.get('/view_edit_analysis')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    @patch('routes.analyses.get_paginated_analyses')
    def test_view_edit_analysis_success(self, mock_get_analyses):
        """Test successful view/edit analysis page load."""
        mock_get_analyses.return_value = ([], 0)
        response = self.client.get('/view_edit_analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'view_edit_analysis.html', response.data)

    @patch('routes.analyses.get_paginated_analyses')
    def test_view_edit_analysis_with_data(self, mock_get_analyses):
        """Test view/edit analysis page with existing analyses."""
        mock_analyses = [{
            'id': str(uuid.uuid4()),
            'analysis_name': 'Test Analysis',
            'created_at': datetime.now(timezone.utc).isoformat()
        }]
        mock_get_analyses.return_value = (mock_analyses, 1)
        
        response = self.client.get('/view_edit_analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Analysis', response.data)

    @patch('services.report_generator.generate_lender_report')
    def test_generate_pdf_success(self, mock_generate):
        """Test successful PDF generation."""
        analysis_id = str(uuid.uuid4())
        mock_generate.return_value = BytesIO(b"PDF content")

        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_analysis))):
            response = self.client.get(f'/generate_pdf/{analysis_id}')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.mimetype, 'application/pdf')

    def test_generate_pdf_not_found(self):
        """Test PDF generation for non-existent analysis."""
        response = self.client.get(f'/generate_pdf/{uuid.uuid4()}')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', data['error'].lower())

    def test_pagination(self):
        """Test analysis pagination functionality."""
        # Test first page
        response = self.client.get('/view_edit_analysis?page=1')
        self.assertEqual(response.status_code, 200)

        # Test invalid page number
        response = self.client.get('/view_edit_analysis?page=999999')
        self.assertEqual(response.status_code, 200)

    @patch('os.listdir')
    @patch('os.path.exists')
    def test_get_paginated_analyses(self, mock_exists, mock_listdir):
        """Test pagination function directly."""
        mock_exists.return_value = True
        mock_listdir.return_value = [
            f"{uuid.uuid4()}_123.json" for _ in range(15)
        ]

        analyses, total_pages = get_paginated_analyses(1, 10)
        self.assertEqual(total_pages, 2)
        self.assertLessEqual(len(analyses), 10)

    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test invalid JSON
        response = self.client.post(
            '/create_analysis',
            data='invalid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

        # Test server error simulation
        with patch('services.analysis_calculations.create_analysis', 
                  side_effect=Exception('Test error')):
            response = self.client.post(
                '/create_analysis',
                json=self.test_analysis,
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()