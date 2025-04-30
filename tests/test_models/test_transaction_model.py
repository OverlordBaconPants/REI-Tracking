"""
Test module for the Transaction model.

This module contains tests for the Transaction model, including ID field handling
and reimbursement structure.
"""

import pytest
from decimal import Decimal
from src.models.transaction import Transaction, Reimbursement
from src.models.property import Partner


class TestTransactionModel:
    """Test class for Transaction model."""
    
    def test_transaction_id_field(self):
        """Test that the Transaction model has an explicit ID field."""
        # Create a transaction with a specific ID
        transaction = Transaction(
            id="test-id-123",
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe"
        )
        
        # Check that the ID is set correctly
        assert transaction.id == "test-id-123"
        
        # Create a transaction without specifying an ID
        transaction2 = Transaction(
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe"
        )
        
        # Check that an ID is generated automatically
        assert transaction2.id is not None
        assert isinstance(transaction2.id, str)
    
    def test_reimbursement_structure(self):
        """Test the simplified Reimbursement structure."""
        # Create a reimbursement with all fields
        reimbursement = Reimbursement(
            date_shared="2025-04-29",
            share_description="Test share description",
            reimbursement_status="completed"
        )
        
        # Check that the fields are set correctly
        assert reimbursement.date_shared == "2025-04-29"
        assert reimbursement.share_description == "Test share description"
        assert reimbursement.reimbursement_status == "completed"
        
        # Create a reimbursement with minimal fields
        reimbursement2 = Reimbursement()
        
        # Check default values
        assert reimbursement2.date_shared is None
        assert reimbursement2.share_description is None
        assert reimbursement2.reimbursement_status == "pending"
    
    def test_reimbursement_validation(self):
        """Test validation for the Reimbursement model."""
        # Test invalid date format
        with pytest.raises(ValueError):
            Reimbursement(date_shared="invalid-date")
        
        # Test invalid reimbursement status
        with pytest.raises(ValueError):
            Reimbursement(reimbursement_status="invalid-status")
    
    def test_transaction_with_reimbursement(self):
        """Test a transaction with a reimbursement."""
        # Create a transaction with a reimbursement
        transaction = Transaction(
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe",
            reimbursement=Reimbursement(
                date_shared="2025-04-29",
                share_description="Test share description",
                reimbursement_status="completed"
            )
        )
        
        # Check that the reimbursement is set correctly
        assert transaction.reimbursement is not None
        assert transaction.reimbursement.date_shared == "2025-04-29"
        assert transaction.reimbursement.share_description == "Test share description"
        assert transaction.reimbursement.reimbursement_status == "completed"
    
    def test_is_reimbursed(self):
        """Test the is_reimbursed method."""
        # Create a transaction with a completed reimbursement
        transaction = Transaction(
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe",
            reimbursement=Reimbursement(
                reimbursement_status="completed"
            )
        )
        
        # Check that is_reimbursed returns True
        assert transaction.is_reimbursed() is True
        
        # Create a transaction with a pending reimbursement
        transaction2 = Transaction(
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe",
            reimbursement=Reimbursement(
                reimbursement_status="pending"
            )
        )
        
        # Check that is_reimbursed returns False
        assert transaction2.is_reimbursed() is False
        
        # Create a transaction without a reimbursement
        transaction3 = Transaction(
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe"
        )
        
        # Check that is_reimbursed returns False
        assert transaction3.is_reimbursed() is False
    
    def test_calculate_reimbursement_shares(self):
        """Test calculating reimbursement shares based on partner equity."""
        # Create a transaction
        transaction = Transaction(
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe"
        )
        
        # Create partners
        partners = [
            Partner(name="John Doe", equity_share=Decimal("60")),
            Partner(name="Jane Smith", equity_share=Decimal("40"))
        ]
        
        # Calculate reimbursement shares
        shares = transaction.calculate_reimbursement_shares(partners)
        
        # Check that shares are calculated correctly
        # John Doe is the payer, so only Jane Smith should get a share
        assert len(shares) == 1
        assert "Jane Smith" in shares
        assert shares["Jane Smith"] == Decimal("40")
        
        # Test with invalid total equity
        invalid_partners = [
            Partner(name="John Doe", equity_share=Decimal("60")),
            Partner(name="Jane Smith", equity_share=Decimal("30"))
        ]
        
        # Check that ValueError is raised
        with pytest.raises(ValueError):
            transaction.calculate_reimbursement_shares(invalid_partners)
    
    def test_to_dict(self):
        """Test converting a transaction to a dictionary."""
        # Create a transaction with a reimbursement
        transaction = Transaction(
            id="test-id-123",
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-04-29",
            collector_payer="John Doe",
            reimbursement=Reimbursement(
                date_shared="2025-04-29",
                share_description="Test share description",
                reimbursement_status="completed"
            )
        )
        
        # Convert to dictionary
        transaction_dict = transaction.to_dict()
        
        # Check that the dictionary is correct
        assert transaction_dict["id"] == "test-id-123"
        assert transaction_dict["property_id"] == "123 Main St"
        assert transaction_dict["type"] == "expense"
        assert transaction_dict["category"] == "Maintenance"
        assert transaction_dict["description"] == "Test transaction"
        assert transaction_dict["amount"] == "100.00"
        assert transaction_dict["date"] == "2025-04-29"
        assert transaction_dict["collector_payer"] == "John Doe"
        assert "reimbursement" in transaction_dict
        assert transaction_dict["reimbursement"]["date_shared"] == "2025-04-29"
        assert transaction_dict["reimbursement"]["share_description"] == "Test share description"
        assert transaction_dict["reimbursement"]["reimbursement_status"] == "completed"
