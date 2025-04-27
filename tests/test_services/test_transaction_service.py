"""
Test module for transaction service.

This module contains tests for the transaction service.
"""

import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime

from src.models.transaction import Transaction, Reimbursement
from src.services.transaction_service import TransactionService


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


class TestTransactionService:
    """Test class for transaction service."""

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_get_transactions(self, mock_property_access_class, mock_repo_class, mock_transactions):
        """Test getting transactions."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock repository response
        mock_repo.get_all.return_value = mock_transactions
        
        # Mock property access service
        mock_property_access.get_accessible_properties.return_value = [
            MagicMock(id="123 Main St"),
            MagicMock(id="456 Oak Ave")
        ]
        
        # Create service and call method
        service = TransactionService()
        result = service.get_transactions("test-user")
        
        # Check result
        assert len(result) == 3
        assert result[0].id == "test-transaction-1"
        assert result[1].id == "test-transaction-2"
        assert result[2].id == "test-transaction-3"
        
        # Verify repository was called
        mock_repo.get_all.assert_called_once()
        mock_property_access.get_accessible_properties.assert_called_once_with("test-user")

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_get_transactions_with_filters(self, mock_property_access_class, mock_repo_class, mock_transactions):
        """Test getting transactions with filters."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock repository response
        mock_repo.get_all.return_value = mock_transactions
        
        # Mock property access service
        mock_property_access.get_accessible_properties.return_value = [
            MagicMock(id="123 Main St"),
            MagicMock(id="456 Oak Ave")
        ]
        
        # Create service and call method with filters
        service = TransactionService()
        filters = {
            "property_id": "123 Main St",
            "type": "expense"
        }
        result = service.get_transactions("test-user", filters)
        
        # Check result
        assert len(result) == 2  # Only the expense transactions for 123 Main St
        assert result[0].id == "test-transaction-1"
        assert result[0].property_id == "123 Main St"
        assert result[0].type == "expense"
        
        assert result[1].id == "test-transaction-3"
        assert result[1].property_id == "123 Main St"
        assert result[1].type == "expense"

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_create_transaction(self, mock_property_access_class, mock_repo_class, mock_transaction):
        """Test creating a transaction."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock repository response
        mock_repo.create.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Create transaction data
        transaction_data = {
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Maintenance",
            "description": "Test transaction",
            "amount": Decimal("100.00"),
            "date": "2025-01-01",
            "collector_payer": "Test User"
        }
        
        # Create service and call method
        service = TransactionService()
        result = service.create_transaction(transaction_data, "test-user")
        
        # Check result
        assert result is not None
        assert result.id == "test-transaction-1"
        
        # Verify repository was called
        mock_repo.create.assert_called_once()
        mock_property_access.can_manage_property.assert_called_once_with(
            "test-user", "123 Main St"
        )

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_create_transaction_unauthorized(self, mock_property_access_class, mock_repo_class):
        """Test creating a transaction without permission."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = False
        
        # Create transaction data
        transaction_data = {
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Maintenance",
            "description": "Test transaction",
            "amount": Decimal("100.00"),
            "date": "2025-01-01",
            "collector_payer": "Test User"
        }
        
        # Create service and call method
        service = TransactionService()
        result = service.create_transaction(transaction_data, "test-user")
        
        # Check result
        assert result is None
        
        # Verify repository was not called
        mock_repo.create.assert_not_called()
        mock_property_access.can_manage_property.assert_called_once_with(
            "test-user", "123 Main St"
        )

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_get_transaction(self, mock_property_access_class, mock_repo_class, mock_transaction):
        """Test getting a specific transaction."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_access_property.return_value = True
        
        # Create service and call method
        service = TransactionService()
        result = service.get_transaction("test-transaction-1", "test-user")
        
        # Check result
        assert result is not None
        assert result.id == "test-transaction-1"
        
        # Verify repository was called
        mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
        mock_property_access.can_access_property.assert_called_once_with(
            "test-user", "123 Main St"
        )

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_update_transaction(self, mock_property_access_class, mock_repo_class, mock_transaction):
        """Test updating a transaction."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        mock_repo.update.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Update data
        update_data = {
            "description": "Updated description",
            "amount": Decimal("150.00")
        }
        
        # Create service and call method
        service = TransactionService()
        result = service.update_transaction("test-transaction-1", update_data, "test-user")
        
        # Check result
        assert result is not None
        assert result.id == "test-transaction-1"
        
        # Verify repository was called
        mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
        mock_repo.update.assert_called_once()
        mock_property_access.can_manage_property.assert_called_once_with(
            "test-user", "123 Main St"
        )

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_delete_transaction(self, mock_property_access_class, mock_repo_class, mock_transaction):
        """Test deleting a transaction."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Create service and call method
        service = TransactionService()
        result = service.delete_transaction("test-transaction-1", "test-user")
        
        # Check result
        assert result is True
        
        # Verify repository was called
        mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
        mock_repo.delete.assert_called_once_with("test-transaction-1")
        mock_property_access.can_manage_property.assert_called_once_with(
            "test-user", "123 Main St"
        )

    @patch('src.services.transaction_service.TransactionRepository')
    @patch('src.services.transaction_service.PropertyAccessService')
    def test_update_reimbursement(self, mock_property_access_class, mock_repo_class, mock_transaction):
        """Test updating reimbursement status."""
        # Set up mocks
        mock_repo = mock_repo_class.return_value
        mock_property_access = mock_property_access_class.return_value
        
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_transaction
        mock_repo.update.return_value = mock_transaction
        
        # Mock property access service
        mock_property_access.can_manage_property.return_value = True
        
        # Update data
        update_data = {
            "date_shared": "2025-02-01",
            "share_description": "Split with partners",
            "reimbursement_status": "completed"
        }
        
        # Create service and call method
        service = TransactionService()
        result = service.update_reimbursement("test-transaction-1", update_data, "test-user")
        
        # Check result
        assert result is not None
        assert result.id == "test-transaction-1"
        
        # Verify repository was called
        mock_repo.get_by_id.assert_called_once_with("test-transaction-1")
        mock_repo.update.assert_called_once()
        mock_property_access.can_manage_property.assert_called_once_with(
            "test-user", "123 Main St"
        )
