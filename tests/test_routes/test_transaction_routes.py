"""
Test module for transaction routes.

This module contains tests for the transaction routes.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime
from flask import session, g

from src.models.transaction import Transaction, Reimbursement


@pytest.fixture
def mock_transaction():
    """Create a mock transaction for testing."""
    return Transaction(
        id="test-transaction-1",
        property_id="123 Main St",
        type="expense",
        category="Maintenance",
        description="Test transaction",
        amount=Decimal("100.00"),
        date="2025-01-01",
        collector_payer="Test User"
    )


@pytest.fixture
def mock_transactions():
    """Create a list of mock transactions for testing."""
    return [
        Transaction(
            id="test-transaction-1",
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction 1",
            amount=Decimal("100.00"),
            date="2025-01-01",
            collector_payer="Test User"
        ),
        Transaction(
            id="test-transaction-2",
            property_id="456 Oak Ave",
            type="income",
            category="Rent",
            description="Test transaction 2",
            amount=Decimal("1000.00"),
            date="2025-01-15",
            collector_payer="Tenant"
        ),
        Transaction(
            id="test-transaction-3",
            property_id="123 Main St",
            type="expense",
            category="Utilities",
            description="Test transaction 3",
            amount=Decimal("50.00"),
            date="2025-01-20",
            collector_payer="Test User",
            reimbursement=Reimbursement(
                date_shared="2025-01-25",
                share_description="Split with partners",
                reimbursement_status="completed"
            )
        )
    ]


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return MagicMock(
        id="test-user",
        name="Test User",
        is_admin=False,
        is_authenticated=True,
        is_active=True
    )


class TestTransactionRoutes:
    """Test class for transaction routes."""

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_get_transactions(self, mock_property_access, mock_repo, client, mock_transactions, mock_user):
        """Test getting transactions."""
        # Mock repository response
        mock_repo.get_all.return_value = mock_transactions
        
        # Mock property access service
        mock_property_access.get_accessible_properties.return_value = [
            MagicMock(id="123 Main St"),
            MagicMock(id="456 Oak Ave")
        ]
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.get("/api/transactions/")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "transactions" in data
            assert len(data["transactions"]) == 3
            
            # Verify transaction data
            transactions = data["transactions"]
            assert transactions[0]["id"] == "test-transaction-1"
            assert transactions[1]["id"] == "test-transaction-2"
            assert transactions[2]["id"] == "test-transaction-3"
            
            # Verify repository was called
            mock_repo.get_all.assert_called_once()
            mock_property_access.get_accessible_properties.assert_called_once_with("test-user")

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_get_transactions_with_filters(self, mock_property_access, mock_repo, client, mock_transactions, mock_user):
        """Test getting transactions with filters."""
        # Mock repository response
        mock_repo.get_all.return_value = mock_transactions
        
        # Mock property access service
        mock_property_access.get_accessible_properties.return_value = [
            MagicMock(id="123 Main St"),
            MagicMock(id="456 Oak Ave")
        ]
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request with filters
            response = client.get("/api/transactions/?property_id=123 Main St&type=expense")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "transactions" in data
            assert len(data["transactions"]) == 2  # Only the expense transactions for 123 Main St
            
            # Verify transaction data
            transactions = data["transactions"]
            assert transactions[0]["id"] == "test-transaction-1"
            assert transactions[0]["property_id"] == "123 Main St"
            assert transactions[0]["type"] == "expense"
            
            assert transactions[1]["id"] == "test-transaction-3"
            assert transactions[1]["property_id"] == "123 Main St"
            assert transactions[1]["type"] == "expense"

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_create_transaction(self, mock_property_access, mock_repo, client, mock_transaction, mock_user):
        """Test creating a transaction."""
        # Mock repository response
        mock_repo.create.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Create transaction data
            transaction_data = {
                "property_id": "123 Main St",
                "type": "expense",
                "category": "Maintenance",
                "description": "Test transaction",
                "amount": 100.00,
                "date": "2025-01-01",
                "collector_payer": "Test User"
            }
            
            # Make request
            response = client.post(
                "/api/transactions/",
                data=json.dumps(transaction_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 201
            data = json.loads(response.data)
            assert "transaction" in data
            assert data["transaction"]["id"] == "test-transaction-1"
            assert data["message"] == "Transaction created successfully"
            
            # Verify repository was called
            mock_repo.create.assert_called_once()
            mock_property_access.can_manage_property.assert_called_once_with(
                "test-user", "123 Main St"
            )

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_create_transaction_unauthorized(self, mock_property_access, mock_repo, client, mock_user):
        """Test creating a transaction without permission."""
        # Mock property access service
        mock_property_access.can_manage_property.return_value = False
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Create transaction data
            transaction_data = {
                "property_id": "123 Main St",
                "type": "expense",
                "category": "Maintenance",
                "description": "Test transaction",
                "amount": 100.00,
                "date": "2025-01-01",
                "collector_payer": "Test User"
            }
            
            # Make request
            response = client.post(
                "/api/transactions/",
                data=json.dumps(transaction_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 403
            data = json.loads(response.data)
            assert "error" in data
            assert "permission" in data["error"]
            
            # Verify repository was not called
            mock_repo.create.assert_not_called()
            mock_property_access.can_manage_property.assert_called_once_with(
                "test-user", "123 Main St"
            )

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_get_transaction(self, mock_property_access, mock_repo, client, mock_transaction, mock_user):
        """Test getting a specific transaction."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_access_property.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.get("/api/transactions/test-transaction-1")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "transaction" in data
            assert data["transaction"]["id"] == "test-transaction-1"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
            mock_property_access.can_access_property.assert_called_once_with(
                "test-user", "123 Main St"
            )

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_update_transaction(self, mock_property_access, mock_repo, client, mock_transaction, mock_user):
        """Test updating a transaction."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        mock_repo.update.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Update data
            update_data = {
                "description": "Updated description",
                "amount": 150.00
            }
            
            # Make request
            response = client.put(
                "/api/transactions/test-transaction-1",
                data=json.dumps(update_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "transaction" in data
            assert data["message"] == "Transaction updated successfully"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
            mock_repo.update.assert_called_once()
            mock_property_access.can_manage_property.assert_called_once_with(
                "test-user", "123 Main St"
            )

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_delete_transaction(self, mock_property_access, mock_repo, client, mock_transaction, mock_user):
        """Test deleting a transaction."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.delete("/api/transactions/test-transaction-1")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["message"] == "Transaction deleted successfully"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
            mock_repo.delete.assert_called_once_with("test-transaction-1")
            mock_property_access.can_manage_property.assert_called_once_with(
                "test-user", "123 Main St"
            )

    @patch('src.routes.transaction_routes.transaction_repo')
    @patch('src.routes.transaction_routes.property_access_service')
    def test_update_reimbursement(self, mock_property_access, mock_repo, client, mock_transaction, mock_user):
        """Test updating reimbursement status."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        mock_repo.update.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Update data
            update_data = {
                "date_shared": "2025-02-01",
                "share_description": "Split with partners",
                "reimbursement_status": "completed"
            }
            
            # Make request
            response = client.put(
                "/api/transactions/reimbursement/test-transaction-1",
                data=json.dumps(update_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "transaction" in data
            assert data["message"] == "Reimbursement updated successfully"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
            mock_repo.update.assert_called_once()
            mock_property_access.can_manage_property.assert_called_once_with(
                "test-user", "123 Main St"
            )
