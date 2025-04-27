"""
Test module for the transaction filtering routes.

This module contains tests for the transaction filtering API endpoints.
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.models.transaction import Transaction, Reimbursement
from src.models.property import Property, Partner
from src.models.user import User, PropertyAccess
from src.services.transaction_service import TransactionService
from src.routes.transaction_routes import transaction_bp


@pytest.fixture
def mock_transactions() -> List[Transaction]:
    """Create a list of mock transactions for testing."""
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    transactions = [
        # Property 1 transactions
        Transaction(
            id="1",
            property_id="property1",
            type="income",
            category="rent",
            description="Rent payment",
            amount=Decimal("1000.00"),
            date=today,
            collector_payer="John Doe"
        ),
        Transaction(
            id="2",
            property_id="property1",
            type="expense",
            category="maintenance",
            description="Plumbing repair",
            amount=Decimal("250.00"),
            date=yesterday,
            collector_payer="Plumber Inc."
        ),
        
        # Property 2 transactions
        Transaction(
            id="3",
            property_id="property2",
            type="income",
            category="rent",
            description="Rent payment",
            amount=Decimal("1200.00"),
            date=today,
            collector_payer="Jane Smith"
        )
    ]
    
    return transactions


@pytest.fixture
def mock_properties() -> List[Property]:
    """Create a list of mock properties for testing."""
    properties = [
        Property(
            id="property1",
            address="123 Main St, City, State",
            purchase_date="2024-01-15",
            purchase_price=Decimal("200000.00"),
            partners=[
                Partner(name="User One", equity_share=Decimal("100"))
            ]
        ),
        Property(
            id="property2",
            address="456 Oak Ave, City, State",
            purchase_date="2024-02-20",
            purchase_price=Decimal("250000.00"),
            partners=[
                Partner(name="User One", equity_share=Decimal("100"))
            ]
        )
    ]
    
    return properties


@pytest.fixture
def mock_current_user():
    """Create a mock current user for testing."""
    return User(
        id="user1",
        name="User One",
        email="user1@example.com",
        role="User",
        property_access=[
            PropertyAccess(property_id="property1", access_level="owner", equity_share=100),
            PropertyAccess(property_id="property2", access_level="owner", equity_share=100)
        ]
    )


@pytest.fixture
def app(mock_current_user):
    """Create a Flask app for testing."""
    from flask import Flask, g
    
    app = Flask(__name__)
    app.register_blueprint(transaction_bp)
    
    @app.before_request
    def before_request():
        g.current_user = mock_current_user
    
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


class TestTransactionFilteringRoutes:
    """Test class for transaction filtering routes."""
    
    @patch('src.routes.transaction_routes.transaction_service')
    def test_get_transactions_no_filters(self, mock_service, client, mock_transactions):
        """Test getting transactions without filters."""
        # Arrange
        mock_service.get_transactions.return_value = mock_transactions
        
        # Act
        response = client.get('/api/transactions/')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['transactions']) == 3
        
        # Verify service call
        mock_service.get_transactions.assert_called_once()
        args, kwargs = mock_service.get_transactions.call_args
        assert args[0] == 'user1'  # user_id
        assert args[1] == {}  # filters
    
    @patch('src.routes.transaction_routes.transaction_service')
    def test_get_transactions_with_filters(self, mock_service, client, mock_transactions):
        """Test getting transactions with filters."""
        # Arrange
        filtered_transactions = [t for t in mock_transactions if t.property_id == "property1"]
        mock_service.get_transactions.return_value = filtered_transactions
        
        # Act
        response = client.get('/api/transactions/?property_id=property1&type=income')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify service call
        mock_service.get_transactions.assert_called_once()
        args, kwargs = mock_service.get_transactions.call_args
        assert args[0] == 'user1'  # user_id
        assert args[1]['property_id'] == 'property1'
        assert args[1]['type'] == 'income'
    
    @patch('src.routes.transaction_routes.transaction_service')
    def test_get_transactions_by_property(self, mock_service, client, mock_transactions):
        """Test getting transactions grouped by property."""
        # Arrange
        grouped_transactions = {
            "property1": [t for t in mock_transactions if t.property_id == "property1"],
            "property2": [t for t in mock_transactions if t.property_id == "property2"]
        }
        mock_service.get_transactions_by_property.return_value = grouped_transactions
        
        # Act
        response = client.get('/api/transactions/by-property')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'grouped_transactions' in data
        assert 'property1' in data['grouped_transactions']
        assert 'property2' in data['grouped_transactions']
        assert len(data['grouped_transactions']['property1']) == 2
        assert len(data['grouped_transactions']['property2']) == 1
    
    @patch('src.routes.transaction_routes.transaction_service')
    def test_get_property_summaries(self, mock_service, client, mock_properties):
        """Test getting property summaries."""
        # Arrange
        summaries = {
            "property1": {
                "property": mock_properties[0],
                "transaction_count": 2,
                "income_total": Decimal("1000.00"),
                "expense_total": Decimal("250.00"),
                "net_amount": Decimal("750.00")
            },
            "property2": {
                "property": mock_properties[1],
                "transaction_count": 1,
                "income_total": Decimal("1200.00"),
                "expense_total": Decimal("0.00"),
                "net_amount": Decimal("1200.00")
            }
        }
        mock_service.get_property_summaries.return_value = summaries
        
        # Act
        response = client.get('/api/transactions/property-summaries')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'property_summaries' in data
        assert 'property1' in data['property_summaries']
        assert 'property2' in data['property_summaries']
        
        # Check property1 summary
        property1_summary = data['property_summaries']['property1']
        assert property1_summary['transaction_count'] == 2
        assert property1_summary['income_total'] == "1000.00"
        assert property1_summary['expense_total'] == "250.00"
        assert property1_summary['net_amount'] == "750.00"
    
    @patch('src.routes.transaction_routes.transaction_service')
    def test_get_transactions_with_property_info(self, mock_service, client, mock_transactions, mock_properties):
        """Test getting transactions with property info."""
        # Arrange
        transaction_property_pairs = [
            (mock_transactions[0], mock_properties[0]),
            (mock_transactions[1], mock_properties[0]),
            (mock_transactions[2], mock_properties[1])
        ]
        mock_service.get_transactions_with_property_info.return_value = transaction_property_pairs
        
        # Act
        response = client.get('/api/transactions/with-property-info')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'transactions_with_property' in data
        assert len(data['transactions_with_property']) == 3
        
        # Check structure of response
        first_item = data['transactions_with_property'][0]
        assert 'transaction' in first_item
        assert 'property' in first_item
        assert first_item['transaction']['id'] == "1"
        assert first_item['property']['id'] == "property1"
    
    @patch('src.routes.transaction_routes.transaction_service')
    def test_filter_parsing(self, mock_service, client):
        """Test parsing of filter parameters."""
        # Arrange
        mock_service.get_transactions.return_value = []
        
        # Act
        response = client.get(
            '/api/transactions/?property_id=property1&type=income&category=rent'
            '&start_date=2025-01-01&end_date=2025-12-31'
            '&reimbursement_status=pending&description=payment'
        )
        
        # Assert
        assert response.status_code == 200
        
        # Verify service call with correct filters
        mock_service.get_transactions.assert_called_once()
        args, kwargs = mock_service.get_transactions.call_args
        filters = args[1]
        
        assert filters['property_id'] == 'property1'
        assert filters['type'] == 'income'
        assert filters['category'] == 'rent'
        assert filters['start_date'] == '2025-01-01'
        assert filters['end_date'] == '2025-12-31'
        assert filters['reimbursement_status'] == 'pending'
        assert filters['description'] == 'payment'
    
    @patch('src.routes.transaction_routes.transaction_service')
    def test_multiple_property_ids(self, mock_service, client):
        """Test filtering by multiple property IDs."""
        # Arrange
        mock_service.get_transactions.return_value = []
        
        # Act
        response = client.get('/api/transactions/?property_ids=property1,property2')
        
        # Assert
        assert response.status_code == 200
        
        # Verify service call with correct filters
        mock_service.get_transactions.assert_called_once()
        args, kwargs = mock_service.get_transactions.call_args
        filters = args[1]
        
        assert 'property_ids' in filters
        assert filters['property_ids'] == ['property1', 'property2']
