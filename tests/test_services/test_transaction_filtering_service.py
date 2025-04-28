"""
Test module for the transaction filtering functionality in TransactionService.

This module contains tests for the transaction filtering and grouping methods.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from unittest.mock import MagicMock

from src.models.transaction import Transaction, Reimbursement
from src.models.property import Property, Partner
from src.models.user import User, PropertyAccess
from src.services.transaction_service import TransactionService
from src.services.property_access_service import PropertyAccessService
from src.repositories.transaction_repository import TransactionRepository
from src.repositories.user_repository import UserRepository
from src.repositories.property_repository import PropertyRepository


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
                Partner(name="User One", equity_share=Decimal("50")),
                Partner(name="User Two", equity_share=Decimal("50"))
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
        ),
        Property(
            id="property3",
            address="789 Pine St, City, State",
            purchase_date="2024-03-10",
            purchase_price=Decimal("180000.00"),
            partners=[
                Partner(name="User Two", equity_share=Decimal("75")),
                Partner(name="User Three", equity_share=Decimal("25"))
            ]
        )
    ]
    
    return properties


@pytest.fixture
def mock_users() -> List[User]:
    """Create a list of mock users for testing."""
    users = [
        User(
            id="user1",
            first_name="User",
            last_name="One",
            name="User One",
            email="user1@example.com",
            password="hashed_password1",
            role="User",
            property_access=[
                PropertyAccess(property_id="property1", access_level="owner", equity_share=50),
                PropertyAccess(property_id="property2", access_level="owner", equity_share=100)
            ]
        ),
        User(
            id="user2",
            first_name="User",
            last_name="Two",
            name="User Two",
            email="user2@example.com",
            password="hashed_password2",
            role="User",
            property_access=[
                PropertyAccess(property_id="property1", access_level="owner", equity_share=50),
                PropertyAccess(property_id="property3", access_level="owner", equity_share=75)
            ]
        ),
        User(
            id="user3",
            first_name="User",
            last_name="Three",
            name="User Three",
            email="user3@example.com",
            password="hashed_password3",
            role="User",
            property_access=[
                PropertyAccess(property_id="property3", access_level="owner", equity_share=25)
            ]
        ),
        User(
            id="admin",
            first_name="Admin",
            last_name="User",
            name="Admin User",
            email="admin@example.com",
            password="hashed_password_admin",
            role="Admin",
            property_access=[]
        )
    ]
    
    return users


@pytest.fixture
def transaction_service(mocker, mock_transactions, mock_properties, mock_users):
    """Create a transaction service with mocked repositories."""
    # Mock transaction repository
    transaction_repo = MagicMock(spec=TransactionRepository)
    transaction_repo.get_all.return_value = mock_transactions
    
    # Mock property repository
    property_repo = MagicMock(spec=PropertyRepository)
    property_repo.get_all.return_value = mock_properties
    
    # Mock user repository
    user_repo = MagicMock(spec=UserRepository)
    user_repo.get_all.return_value = mock_users
    user_repo.get_by_id = lambda user_id: next((u for u in mock_users if u.id == user_id), None)
    
    # Mock property access service
    property_access_service = MagicMock(spec=PropertyAccessService)
    property_access_service.user_repository = user_repo
    property_access_service.property_repository = property_repo
    
    # Set up property access service methods
    def get_accessible_properties(user_id):
        user = user_repo.get_by_id(user_id)
        if user.role == "Admin":
            return mock_properties
        
        accessible_property_ids = {access.property_id for access in user.property_access}
        return [p for p in mock_properties if p.id in accessible_property_ids]
    
    property_access_service.get_accessible_properties.side_effect = get_accessible_properties
    
    # Create transaction service
    service = TransactionService()
    service.transaction_repo = transaction_repo
    service.property_access_service = property_access_service
    
    return service


class TestTransactionFiltering:
    """Test class for transaction filtering functionality."""
    
    def test_get_transactions_no_filters(self, transaction_service):
        """Test getting transactions without filters."""
        # Act
        result = transaction_service.get_transactions("user1", {})
        
        # Assert
        assert len(result) == 5  # User1 has access to property1 and property2
        assert all(t.property_id in ["property1", "property2"] for t in result)
    
    def test_get_transactions_admin_access(self, transaction_service):
        """Test admin access to all transactions."""
        # Act
        result = transaction_service.get_transactions("admin", {})
        
        # Assert
        assert len(result) == 6  # Admin has access to all properties
    
    def test_get_transactions_property_filter(self, transaction_service):
        """Test filtering transactions by property."""
        # Act
        result = transaction_service.get_transactions("user1", {"property_id": "property1"})
        
        # Assert
        assert len(result) == 3
        assert all(t.property_id == "property1" for t in result)
    
    def test_get_transactions_type_filter(self, transaction_service):
        """Test filtering transactions by type."""
        # Act
        result = transaction_service.get_transactions("user1", {"type": "income"})
        
        # Assert
        assert len(result) == 2
        assert all(t.type == "income" for t in result)
    
    def test_get_transactions_category_filter(self, transaction_service):
        """Test filtering transactions by category."""
        # Act
        result = transaction_service.get_transactions("user1", {"category": "maintenance"})
        
        # Assert
        assert len(result) == 2
        assert all(t.category == "maintenance" for t in result)
    
    def test_get_transactions_date_range_filter(self, transaction_service):
        """Test filtering transactions by date range."""
        # Arrange
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Act
        result = transaction_service.get_transactions("user1", {"start_date": today, "end_date": today})
        
        # Assert
        assert len(result) == 2
        assert all(t.date == today for t in result)
    
    def test_get_transactions_reimbursement_status_filter(self, transaction_service):
        """Test filtering transactions by reimbursement status."""
        # Act
        result = transaction_service.get_transactions("user1", {"reimbursement_status": "pending"})
        
        # Assert
        assert len(result) == 1
        assert result[0].id == "5"
        assert result[0].reimbursement.reimbursement_status == "pending"
    
    def test_get_transactions_description_search(self, transaction_service):
        """Test searching transactions by description."""
        # Act
        result = transaction_service.get_transactions("user1", {"description": "repair"})
        
        # Assert
        assert len(result) == 2
        assert all("repair" in t.description.lower() for t in result)
    
    def test_get_transactions_multiple_filters(self, transaction_service):
        """Test filtering transactions with multiple criteria."""
        # Arrange
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Act
        result = transaction_service.get_transactions("user1", {
            "type": "expense",
            "start_date": yesterday,
            "end_date": yesterday
        })
        
        # Assert
        assert len(result) == 2
        assert all(t.type == "expense" and t.date == yesterday for t in result)


class TestTransactionGrouping:
    """Test class for transaction grouping functionality."""
    
    def test_get_transactions_by_property(self, transaction_service):
        """Test grouping transactions by property."""
        # Act
        result = transaction_service.get_transactions_by_property("user1", {})
        
        # Assert
        assert len(result) == 2  # User1 has access to 2 properties
        assert "property1" in result
        assert "property2" in result
        assert len(result["property1"]) == 3
        assert len(result["property2"]) == 2
    
    def test_get_transactions_with_property_info(self, transaction_service):
        """Test getting transactions with property information."""
        # Act
        result = transaction_service.get_transactions_with_property_info("user1", {})
        
        # Assert
        assert len(result) == 5  # User1 has access to 5 transactions
        
        # Check that each result has both transaction and property
        for transaction, property_obj in result:
            assert isinstance(transaction, Transaction)
            assert isinstance(property_obj, Property)
            assert transaction.property_id == property_obj.id
    
    def test_get_property_summaries(self, transaction_service):
        """Test getting property financial summaries."""
        # Act
        result = transaction_service.get_property_summaries("user1", {})
        
        # Assert
        assert len(result) == 2  # User1 has access to 2 properties
        
        # Check property1 summary
        assert "property1" in result
        property1_summary = result["property1"]
        assert property1_summary["transaction_count"] == 3
        assert property1_summary["income_total"] == Decimal("1000.00")
        assert property1_summary["expense_total"] == Decimal("325.00")
        assert property1_summary["net_amount"] == Decimal("675.00")
        
        # Check property2 summary
        assert "property2" in result
        property2_summary = result["property2"]
        assert property2_summary["transaction_count"] == 2
        assert property2_summary["income_total"] == Decimal("1200.00")
        assert property2_summary["expense_total"] == Decimal("350.00")
        assert property2_summary["net_amount"] == Decimal("850.00")
