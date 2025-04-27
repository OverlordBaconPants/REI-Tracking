"""
Tests for transaction report routes.
"""

import io
import json
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, g

from src.models.user import User
from src.models.transaction import Transaction
from src.routes.transaction_routes import transaction_bp


@pytest.fixture
def app():
    """Create a Flask application for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SERVER_NAME'] = 'localhost'  # Required for URL generation
    
    # Register blueprint with proper URL prefix
    app.register_blueprint(transaction_bp)
    
    # Create application context
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def mock_transaction_service():
    """Mock transaction service."""
    with patch('src.routes.transaction_routes.transaction_service') as mock:
        yield mock


@pytest.fixture
def mock_report_generator():
    """Mock report generator."""
    with patch('src.routes.transaction_routes.report_generator') as mock:
        yield mock


@pytest.fixture
def authenticated_client(app, client):
    """Client with authenticated user."""
    # Create a mock user
    user = User(
        id='user123',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password='hashed-password',
        role='User'
    )
    
    # Create a test client with session
    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        sess['user_role'] = user.role
    
    # Mock the auth service to return our user
    with patch('src.routes.transaction_routes.g') as mock_g:
        mock_g.current_user = user
        yield client


class TestTransactionReportRoutes:
    """Tests for transaction report routes."""
    
    def test_generate_transaction_report(self, authenticated_client, mock_transaction_service, mock_report_generator):
        """Test generating a transaction report."""
        # Mock transactions
        transactions = [
            Transaction(
                id='trans1',
                property_id='prop1',
                type='income',
                category='Rent',
                amount=1000.00,
                date='2025-01-01',
                description='January Rent',
                collector_payer='Tenant',
                documentation_file='receipt.pdf'
            ),
            Transaction(
                id='trans2',
                property_id='prop1',
                type='expense',
                category='Repairs',
                amount=200.00,
                date='2025-01-15',
                description='Plumbing repair',
                collector_payer='Plumber',
                documentation_file='invoice.pdf'
            )
        ]
        
        # Mock transaction service
        mock_transaction_service.get_transactions.return_value = transactions
        
        # Mock report generator
        mock_report_generator.generate.return_value = None
        
        # Make request
        response = authenticated_client.get('/api/transactions/report?property_id=prop1&start_date=2025-01-01&end_date=2025-01-31')
        
        # Check response
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'
        assert response.headers['Content-Disposition'].startswith('attachment; filename=')
        
        # Check that transaction service was called with correct parameters
        mock_transaction_service.get_transactions.assert_called_once()
        args, kwargs = mock_transaction_service.get_transactions.call_args
        assert args[0] == 'user123'  # user_id
        assert args[1]['property_id'] == 'prop1'
        assert args[1]['start_date'] == '2025-01-01'
        assert args[1]['end_date'] == '2025-01-31'
        
        # Check that report generator was called with correct parameters
        mock_report_generator.generate.assert_called_once()
        args, kwargs = mock_report_generator.generate.call_args
        assert len(args[0]) == 2  # transaction_dicts
        assert isinstance(args[1], io.BytesIO)  # output_buffer
        assert args[2]['title'] == 'Transaction Report'  # metadata
        assert args[2]['property_name'] == 'prop1'
        assert args[2]['date_range'] == '2025-01-01 to 2025-01-31'
    
    def test_generate_documentation_archive(self, authenticated_client, mock_transaction_service, mock_report_generator):
        """Test generating a documentation archive."""
        # Mock transactions
        transactions = [
            Transaction(
                id='trans1',
                property_id='prop1',
                type='income',
                category='Rent',
                amount=1000.00,
                date='2025-01-01',
                description='January Rent',
                collector_payer='Tenant',
                documentation_file='receipt.pdf'
            ),
            Transaction(
                id='trans2',
                property_id='prop1',
                type='expense',
                category='Repairs',
                amount=200.00,
                date='2025-01-15',
                description='Plumbing repair',
                collector_payer='Plumber',
                documentation_file='invoice.pdf'
            )
        ]
        
        # Mock transaction service
        mock_transaction_service.get_transactions.return_value = transactions
        
        # Mock report generator
        mock_report_generator.generate_zip_archive.return_value = None
        
        # Make request
        response = authenticated_client.get('/api/transactions/documentation-archive?property_id=prop1&start_date=2025-01-01&end_date=2025-01-31')
        
        # Check response
        assert response.status_code == 200
        assert response.mimetype == 'application/zip'
        assert response.headers['Content-Disposition'].startswith('attachment; filename=')
        
        # Check that transaction service was called with correct parameters
        mock_transaction_service.get_transactions.assert_called_once()
        args, kwargs = mock_transaction_service.get_transactions.call_args
        assert args[0] == 'user123'  # user_id
        assert args[1]['property_id'] == 'prop1'
        assert args[1]['start_date'] == '2025-01-01'
        assert args[1]['end_date'] == '2025-01-31'
        
        # Check that report generator was called with correct parameters
        mock_report_generator.generate_zip_archive.assert_called_once()
        args, kwargs = mock_report_generator.generate_zip_archive.call_args
        assert len(args[0]) == 2  # transaction_dicts
        assert isinstance(args[1], io.BytesIO)  # output_buffer
    
    def test_generate_transaction_report_error(self, authenticated_client, mock_transaction_service, mock_report_generator):
        """Test error handling when generating a transaction report."""
        # Mock transaction service to raise an exception
        mock_transaction_service.get_transactions.side_effect = Exception("Test error")
        
        # Make request
        response = authenticated_client.get('/api/transactions/report')
        
        # Check response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
        assert 'Test error' in data['error']
        
        # Check that report generator was not called
        mock_report_generator.generate.assert_not_called()
    
    def test_generate_documentation_archive_error(self, authenticated_client, mock_transaction_service, mock_report_generator):
        """Test error handling when generating a documentation archive."""
        # Mock transaction service to raise an exception
        mock_transaction_service.get_transactions.side_effect = Exception("Test error")
        
        # Make request
        response = authenticated_client.get('/api/transactions/documentation-archive')
        
        # Check response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
        assert 'Test error' in data['error']
        
        # Check that report generator was not called
        mock_report_generator.generate_zip_archive.assert_not_called()
