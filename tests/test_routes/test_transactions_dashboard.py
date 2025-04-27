"""
Tests for the transactions dashboard functionality.

This module contains tests for the transactions dashboard routes and functionality.
"""

import pytest
from flask import url_for
from unittest.mock import patch, MagicMock

from src.models.transaction import Transaction
from src.repositories.transaction_repository import TransactionRepository
from tests.test_routes.auth_fixture import AuthActions

@pytest.fixture
def auth(client):
    """Authentication fixture for testing."""
    return AuthActions(client)


@pytest.fixture
def mock_transaction_service():
    """Mock the transaction service for testing."""
    with patch('src.dash_apps.dash_transactions.TransactionService') as mock_service:
        # Create a mock instance
        mock_instance = MagicMock()
        
        # Configure the mock instance to return test transactions
        mock_instance.get_transactions.return_value = [
            Transaction(
                id="test-transaction-1",
                property_id="test-property-1",
                type="income",
                category="Rent",
                description="Test Income Transaction",
                amount=1000.00,
                date="2025-01-01",
                collector_payer="Test Tenant"
            ),
            Transaction(
                id="test-transaction-2",
                property_id="test-property-2",
                type="expense",
                category="Repairs",
                description="Test Expense Transaction",
                amount=500.00,
                date="2025-01-15",
                collector_payer="Test Contractor"
            )
        ]
        
        # Configure the mock constructor to return our mock instance
        mock_service.return_value = mock_instance
        
        yield mock_service


@pytest.fixture
def mock_property_access_service():
    """Mock the property access service for testing."""
    with patch('src.dash_apps.dash_transactions.PropertyAccessService') as mock_service:
        # Create a mock instance
        mock_instance = MagicMock()
        
        # Configure the mock instance to return test properties
        from src.models.property import Property
        mock_instance.get_accessible_properties.return_value = [
            Property(
                id="test-property-1",
                address="123 Test St, Test City, Test State 12345",
                purchase_date="2025-01-01",
                purchase_price=200000.00
            ),
            Property(
                id="test-property-2",
                address="456 Sample Ave, Sample City, Sample State 67890",
                purchase_date="2025-02-01",
                purchase_price=300000.00
            )
        ]
        
        # Configure the mock constructor to return our mock instance
        mock_service.return_value = mock_instance
        
        yield mock_service


def test_transactions_dashboard_route(client, auth):
    """Test that the transactions dashboard route returns a 200 status code."""
    # Log in as a test user
    auth.login()
    
    # Access the transactions dashboard
    response = client.get('/dashboards/transactions')
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Check that the response contains the expected content
    assert b'Transactions Dashboard' in response.data


def test_transactions_dash_route(client, auth):
    """Test that the transactions dash route returns a 200 status code."""
    # Log in as a test user
    auth.login()
    
    # Access the transactions dash route
    response = client.get('/dashboards/_dash/transactions/')
    
    # Check that the response is successful
    assert response.status_code == 200


def test_transactions_dash_with_mocks(client, auth, mock_transaction_service, mock_property_access_service):
    """Test the transactions dash with mocked services."""
    # Log in as a test user
    auth.login()
    
    # Access the transactions dash route
    response = client.get('/dashboards/_dash/transactions/')
    
    # Check that the response is successful
    assert response.status_code == 200
    
    # Verify that the mock services were called
    # Note: We can't easily verify this directly since the services are instantiated
    # inside the Dash callbacks, which are not executed during the test.
    # A more comprehensive test would use Selenium or similar to interact with the UI.
