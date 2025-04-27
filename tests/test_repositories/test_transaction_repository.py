"""
Test module for the TransactionRepository class.

This module contains tests for the transaction repository filtering methods.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

from src.models.transaction import Transaction, Reimbursement
from src.repositories.transaction_repository import TransactionRepository


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
        Transaction(
            id="3",
            property_id="property1",
            type="expense",
            category="utilities",
            description="Water bill",
            amount=Decimal("75.00"),
            date=last_week,
            collector_payer="Water Company",
            reimbursement=Reimbursement(
                date_shared="2025-04-20",
                share_description="Shared with tenants",
                reimbursement_status="completed"
            )
        ),
        
        # Property 2 transactions
        Transaction(
            id="4",
            property_id="property2",
            type="income",
            category="rent",
            description="Rent payment",
            amount=Decimal("1200.00"),
            date=today,
            collector_payer="Jane Smith"
        ),
        Transaction(
            id="5",
            property_id="property2",
            type="expense",
            category="maintenance",
            description="HVAC repair",
            amount=Decimal("350.00"),
            date=yesterday,
            collector_payer="HVAC Services",
            reimbursement=Reimbursement(
                reimbursement_status="pending"
            )
        ),
        
        # Property 3 transactions
        Transaction(
            id="6",
            property_id="property3",
            type="income",
            category="other",
            description="Security deposit",
            amount=Decimal("800.00"),
            date=last_week,
            collector_payer="New Tenant"
        )
    ]
    
    return transactions


class TestTransactionRepository:
    """Test class for TransactionRepository."""
    
    def test_get_by_property(self, mocker, mock_transactions):
        """Test filtering transactions by property."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        # Act
        result = repo.get_by_property("property1")
        
        # Assert
        assert len(result) == 3
        assert all(t.property_id == "property1" for t in result)
    
    def test_get_by_date_range(self, mocker, mock_transactions):
        """Test filtering transactions by date range."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Act
        result = repo.get_by_date_range(yesterday, today)
        
        # Assert
        assert len(result) == 4
        for t in result:
            transaction_date = datetime.strptime(t.date, "%Y-%m-%d").date()
            assert (
                datetime.strptime(yesterday, "%Y-%m-%d").date() <= transaction_date <= 
                datetime.strptime(today, "%Y-%m-%d").date()
            )
    
    def test_get_by_category(self, mocker, mock_transactions):
        """Test filtering transactions by category."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        # Act
        result = repo.get_by_category("maintenance")
        
        # Assert
        assert len(result) == 2
        assert all(t.category == "maintenance" for t in result)
    
    def test_get_by_category_with_type(self, mocker, mock_transactions):
        """Test filtering transactions by category and type."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        # Act
        result = repo.get_by_category("rent", "income")
        
        # Assert
        assert len(result) == 2
        assert all(t.category == "rent" and t.type == "income" for t in result)
    
    def test_get_by_description_search(self, mocker, mock_transactions):
        """Test searching transactions by description."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        # Act
        result = repo.get_by_description_search("repair")
        
        # Assert
        assert len(result) == 2
        assert all("repair" in t.description.lower() for t in result)
    
    def test_get_by_properties(self, mocker, mock_transactions):
        """Test filtering transactions by multiple properties."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        # Act
        result = repo.get_by_properties({"property1", "property3"})
        
        # Assert
        assert len(result) == 4
        assert all(t.property_id in {"property1", "property3"} for t in result)
    
    def test_get_pending_reimbursements(self, mocker, mock_transactions):
        """Test getting transactions with pending reimbursements."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        # Act
        result = repo.get_pending_reimbursements()
        
        # Assert
        assert len(result) == 1
        assert result[0].id == "5"
        assert result[0].reimbursement.reimbursement_status == "pending"
    
    def test_get_completed_reimbursements(self, mocker, mock_transactions):
        """Test getting transactions with completed reimbursements."""
        # Arrange
        repo = TransactionRepository()
        mocker.patch.object(repo, 'get_all', return_value=mock_transactions)
        
        # Act
        result = repo.get_completed_reimbursements()
        
        # Assert
        assert len(result) == 1
        assert result[0].id == "3"
        assert result[0].reimbursement.reimbursement_status == "completed"
