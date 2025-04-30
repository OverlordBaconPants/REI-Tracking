import unittest
from unittest.mock import patch, mock_open, MagicMock
from flask import url_for
from werkzeug.datastructures import FileStorage
from io import BytesIO
import json
import os
from app import create_app
import pandas as pd

class TestTransactionsRoutes(unittest.TestCase):
    """Test suite for transaction routes."""

    def setUp(self):
        """Set up test environment."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Sample test data
        self.valid_transaction = {
            'property_id': '123',
            'type': 'EXPENSE',
            'category': 'REPAIRS',
            'description': 'Test repair',
            'amount': 100.00,
            'date': '2024-01-01',
            'collector_payer': 'Test User',
            'documentation_file': 'test.pdf',
            'reimbursement': {
                'date_shared': '2024-01-02',
                'share_description': 'Test share',
                'reimbursement_status': 'pending'
            }
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
            mock_user.id = 'admin@example.com'
            return mock_user

    def login_as_user(self):
        """Helper to simulate regular user login."""
        with patch('flask_login.current_user') as mock_user:
            mock_user.is_authenticated = True
            mock_user.role = 'User'
            mock_user.name = 'Test User'
            mock_user.email = 'user@example.com'
            mock_user.id = 'user@example.com'
            return mock_user

    def test_transactions_list_auth_required(self):
        """Test transactions list requires authentication."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    @patch('routes.transactions.get_properties_for_user')
    def test_add_transaction_get(self, mock_get_properties):
        """Test GET request to add transaction page."""
        mock_user = self.login_as_user()
        mock_get_properties.return_value = [{'address': '123 Test St'}]
        
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'add_transactions.html', response.data)

    @patch('routes.transactions.get_properties_for_user')
    @patch('routes.transactions.add_transaction')
    @patch('routes.transactions.is_duplicate_transaction')
    def test_add_transaction_success(self, mock_is_duplicate, mock_add, mock_get_properties):
        """Test successful transaction addition."""
        mock_user = self.login_as_user()
        mock_get_properties.return_value = [{'address': '123 Test St'}]
        mock_is_duplicate.return_value = False
        
        # Create test file
        test_file = (BytesIO(b'test file content'), 'test.pdf')
        
        data = self.valid_transaction.copy()
        data['documentation_file'] = test_file
        
        response = self.client.post(
            '/add',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 302)
        mock_add.assert_called_once()

    def test_add_transaction_no_file(self):
        """Test transaction addition without file."""
        mock_user = self.login_as_user()
        
        response = self.client.post(
            '/add',
            data=self.valid_transaction,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 302)
        self.assertIn(b'No file provided', response.data)

    @patch('routes.transactions.get_transaction_by_id')
    def test_edit_transaction_unauthorized(self, mock_get_transaction):
        """Test transaction edit by unauthorized user."""
        mock_user = self.login_as_user()
        mock_get_transaction.return_value = self.valid_transaction
        
        response = self.client.get('/edit/1')
        self.assertEqual(response.status_code, 403)

    @patch('routes.transactions.get_transaction_by_id')
    @patch('routes.transactions.get_properties_for_user')
    def test_edit_transaction_admin(self, mock_get_properties, mock_get_transaction):
        """Test transaction edit by admin."""
        mock_user = self.login_as_admin()
        mock_get_transaction.return_value = self.valid_transaction
        mock_get_properties.return_value = [{'address': '123 Test St'}]
        
        response = self.client.get('/edit/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'edit_transactions.html', response.data)

    def test_bulk_import_get(self):
        """Test GET request to bulk import page."""
        mock_user = self.login_as_user()
        
        response = self.client.get('/bulk_import')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'bulk_import.html', response.data)

    @patch('routes.transactions.process_bulk_import')
    def test_bulk_import_success(self, mock_process):
        """Test successful bulk import."""
        mock_user = self.login_as_user()
        mock_process.return_value = {
            'success': True,
            'stats': {
                'processed_rows': 10,
                'imported_count': 8,
                'skipped_rows': 2
            }
        }
        
        # Create test Excel file
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Amount': [100.00],
            'Description': ['Test']
        })
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        data = {
            'file': (excel_file, 'test.xlsx'),
            'column_mapping': json.dumps({
                'date': 'Date',
                'amount': 'Amount',
                'description': 'Description'
            })
        }
        
        response = self.client.post(
            '/bulk_import',
            data=data,
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])

    def test_get_columns(self):
        """Test getting columns from uploaded file."""
        mock_user = self.login_as_user()
        
        # Create test Excel file
        df = pd.DataFrame({
            'Date': [],
            'Amount': [],
            'Description': []
        })
        excel_file = BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        response = self.client.post(
            '/get_columns',
            data={'file': (excel_file, 'test.xlsx')},
            content_type='multipart/form-data'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('columns', response_data)
        self.assertEqual(len(response_data['columns']), 3)

    @patch('routes.transactions.get_artifact')
    def test_get_artifact(self, mock_get_artifact):
        """Test artifact retrieval."""
        mock_user = self.login_as_user()
        mock_get_artifact.return_value = 'test content'
        
        response = self.client.get('/artifact/test.pdf')
        self.assertEqual(response.status_code, 200)

    def test_get_artifact_not_found(self):
        """Test artifact not found."""
        mock_user = self.login_as_user()
        
        response = self.client.get('/artifact/nonexistent.pdf')
        self.assertEqual(response.status_code, 404)

    @patch('routes.transactions.get_partners_for_property')
    def test_get_property_partners(self, mock_get_partners):
        """Test getting property partners."""
        mock_user = self.login_as_user()
        mock_get_partners.return_value = [{'name': 'Test Partner'}]
        
        response = self.client.get('/api/partners?property_id=123')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)

class TestFileHandling(unittest.TestCase):
    """Test suite for file handling functions."""

    def test_allowed_file(self):
        """Test file extension validation."""
        test_cases = [
            ('test.pdf', 'documentation', True),
            ('test.doc', 'documentation', False),
            ('test.xlsx', 'import', True),
            ('test.txt', 'import', False)
        ]
        
        for filename, file_type, expected in test_cases:
            with self.subTest(filename=filename):
                result = allowed_file(filename, file_type)
                self.assertEqual(result, expected)

    def test_secure_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ('test file.pdf', 'test_file.pdf'),
            ('../test.pdf', 'test.pdf'),
            ('Test File (1).pdf', 'Test_File_1.pdf')
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = secure_filename(input_name)
                self.assertEqual(result, expected)

class TestBulkImportProcessing(unittest.TestCase):
    """Test suite for bulk import processing."""

    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_process_excel_file(self):
        """Test processing Excel file."""
        # Create test data
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Amount': [100.00],
            'Description': ['Test']
        })
        
        # Save to temporary file
        temp_file = 'test_import.xlsx'
        df.to_excel(temp_file, index=False)
        
        try:
            # Process the file
            column_mapping = {
                'date': 'Date',
                'amount': 'Amount',
                'description': 'Description'
            }
            
            results = process_bulk_import(temp_file, column_mapping)
            
            self.assertTrue(results['success'])
            self.assertEqual(results['stats']['processed_rows'], 1)
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_process_csv_file(self):
        """Test processing CSV file."""
        # Create test data
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Amount': [100.00],
            'Description': ['Test']
        })
        
        # Save to temporary file
        temp_file = 'test_import.csv'
        df.to_csv(temp_file, index=False)
        
        try:
            # Process the file
            column_mapping = {
                'date': 'Date',
                'amount': 'Amount',
                'description': 'Description'
            }
            
            results = process_bulk_import(temp_file, column_mapping)
            
            self.assertTrue(results['success'])
            self.assertEqual(results['stats']['processed_rows'], 1)
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == '__main__':
    unittest.main()