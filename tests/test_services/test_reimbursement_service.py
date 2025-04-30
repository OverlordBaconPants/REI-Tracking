"""
Test module for the reimbursement service.

This module contains tests for the ReimbursementService class.
"""

import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime

from src.models.transaction import Transaction, Reimbursement
from src.models.property import Property, Partner
from src.services.reimbursement_service import ReimbursementService


class TestReimbursementService(unittest.TestCase):
    """Test case for the ReimbursementService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock repositories and services
        self.transaction_repo = MagicMock()
        self.property_repo = MagicMock()
        self.property_access_service = MagicMock()
        
        # Create reimbursement service with mocks
        self.reimbursement_service = ReimbursementService(
            self.transaction_repo,
            self.property_repo,
            self.property_access_service
        )
        
        # Create test data
        self.user_id = "user123"
        self.transaction_id = "transaction123"
        self.property_id = "property123"
        
        # Create a test transaction
        self.transaction = Transaction(
            id=self.transaction_id,
            property_id=self.property_id,
            type="expense",
            category="Repairs",
            description="Test expense",
            amount=Decimal("100.00"),
            date="2025-04-26",
            collector_payer="John Doe"
        )
        
        # Create test property with partners
        self.property = MagicMock()
        self.property.id = self.property_id
        self.property.address = "123 Main St"
        self.property.partners = [
            Partner(name="John Doe", equity_share=Decimal("60")),
            Partner(name="Jane Smith", equity_share=Decimal("40"))
        ]
        
        # Set up repository mocks
        self.transaction_repo.get_by_id.return_value = self.transaction
        self.property_repo.get_by_id.return_value = self.property
        self.property_access_service.can_access_property.return_value = True
        self.property_access_service.can_manage_property.return_value = True
    
    def test_calculate_reimbursement_shares(self):
        """Test calculating reimbursement shares."""
        # Call the method
        shares = self.reimbursement_service.calculate_reimbursement_shares(
            self.transaction_id, self.user_id
        )
        
        # Verify the result
        self.assertEqual(len(shares), 1)
        self.assertIn("Jane Smith", shares)
        self.assertEqual(shares["Jane Smith"], Decimal("40"))
        
        # Verify repository calls
        self.transaction_repo.get_by_id.assert_called_once_with(self.transaction_id)
        self.property_repo.get_by_id.assert_called_once_with(self.property_id)
        self.property_access_service.can_access_property.assert_called_once_with(
            self.user_id, self.property_id
        )
    
    def test_calculate_reimbursement_shares_transaction_not_found(self):
        """Test calculating reimbursement shares when transaction is not found."""
        # Set up mock
        self.transaction_repo.get_by_id.return_value = None
        
        # Call the method and verify exception
        with self.assertRaises(ValueError):
            self.reimbursement_service.calculate_reimbursement_shares(
                self.transaction_id, self.user_id
            )
    
    def test_calculate_reimbursement_shares_property_not_found(self):
        """Test calculating reimbursement shares when property is not found."""
        # Set up mock
        self.property_repo.get_by_id.return_value = None
        
        # Call the method and verify exception
        with self.assertRaises(ValueError):
            self.reimbursement_service.calculate_reimbursement_shares(
                self.transaction_id, self.user_id
            )
    
    def test_calculate_reimbursement_shares_access_denied(self):
        """Test calculating reimbursement shares when access is denied."""
        # Set up mock
        self.property_access_service.can_access_property.return_value = False
        
        # Call the method and verify exception
        with self.assertRaises(ValueError):
            self.reimbursement_service.calculate_reimbursement_shares(
                self.transaction_id, self.user_id
            )
    
    def test_update_reimbursement(self):
        """Test updating reimbursement."""
        # Set up mock
        self.transaction_repo.update.return_value = self.transaction
        
        # Create reimbursement data
        reimbursement_data = {
            "date_shared": "2025-04-26",
            "share_description": "Test reimbursement",
            "reimbursement_status": "completed"
        }
        
        # Call the method
        result = self.reimbursement_service.update_reimbursement(
            self.transaction_id, reimbursement_data, self.user_id
        )
        
        # Verify the result
        self.assertEqual(result, self.transaction)
        self.assertEqual(result.reimbursement.date_shared, "2025-04-26")
        self.assertEqual(result.reimbursement.share_description, "Test reimbursement")
        self.assertEqual(result.reimbursement.reimbursement_status, "completed")
        
        # Verify repository calls
        self.transaction_repo.get_by_id.assert_called_once_with(self.transaction_id)
        self.property_access_service.can_manage_property.assert_called_once_with(
            self.user_id, self.property_id
        )
        self.transaction_repo.update.assert_called_once()
    
    def test_update_reimbursement_transaction_not_found(self):
        """Test updating reimbursement when transaction is not found."""
        # Set up mock
        self.transaction_repo.get_by_id.return_value = None
        
        # Call the method
        result = self.reimbursement_service.update_reimbursement(
            self.transaction_id, {}, self.user_id
        )
        
        # Verify the result
        self.assertIsNone(result)
    
    def test_update_reimbursement_access_denied(self):
        """Test updating reimbursement when access is denied."""
        # Set up mock
        self.property_access_service.can_manage_property.return_value = False
        
        # Call the method
        result = self.reimbursement_service.update_reimbursement(
            self.transaction_id, {}, self.user_id
        )
        
        # Verify the result
        self.assertIsNone(result)
    
    def test_process_new_transaction_wholly_owned(self):
        """Test processing a new transaction for a wholly-owned property."""
        # Create a wholly-owned property
        wholly_owned_property = MagicMock()
        wholly_owned_property.id = self.property_id
        wholly_owned_property.address = "123 Main St"
        wholly_owned_property.partners = [
            Partner(name="John Doe", equity_share=Decimal("100"))
        ]
        
        # Set up mock
        self.property_repo.get_by_id.return_value = wholly_owned_property
        self.transaction_repo.update.return_value = self.transaction
        
        # Call the method
        result = self.reimbursement_service.process_new_transaction(self.transaction)
        
        # Verify the result
        self.assertEqual(result, self.transaction)
        self.assertIsNotNone(result.reimbursement)
        self.assertEqual(result.reimbursement.reimbursement_status, "completed")
        
        # Verify repository calls
        self.property_repo.get_by_id.assert_called_once_with(self.property_id)
        self.transaction_repo.update.assert_called_once()
    
    def test_get_reimbursement_shares(self):
        """Test getting reimbursement shares on-demand."""
        # Call the method without user_id
        shares = self.reimbursement_service.get_reimbursement_shares(self.transaction_id)
        
        # Verify the result
        self.assertEqual(len(shares), 1)
        self.assertIn("Jane Smith", shares)
        self.assertEqual(shares["Jane Smith"], Decimal("40"))
        
        # Verify repository calls
        self.transaction_repo.get_by_id.assert_called_once_with(self.transaction_id)
        self.property_repo.get_by_id.assert_called_once_with(self.property_id)
        
        # Reset mocks
        self.transaction_repo.get_by_id.reset_mock()
        self.property_repo.get_by_id.reset_mock()
        
        # Call the method with user_id
        shares = self.reimbursement_service.get_reimbursement_shares(
            self.transaction_id, self.user_id
        )
        
        # Verify the result
        self.assertEqual(len(shares), 1)
        self.assertIn("Jane Smith", shares)
        self.assertEqual(shares["Jane Smith"], Decimal("40"))
        
        # Verify repository calls
        self.transaction_repo.get_by_id.assert_called_once_with(self.transaction_id)
        self.property_repo.get_by_id.assert_called_once_with(self.property_id)
        self.property_access_service.can_access_property.assert_called_once_with(
            self.user_id, self.property_id
        )
    
    def test_process_new_transaction_shared_property(self):
        """Test processing a new transaction for a shared property."""
        # Set up mock
        self.transaction_repo.update.return_value = self.transaction
        
        # Call the method
        result = self.reimbursement_service.process_new_transaction(self.transaction)
        
        # Verify the result
        self.assertEqual(result, self.transaction)
        self.assertIsNotNone(result.reimbursement)
        
        # Verify that we can calculate shares on-demand
        shares = self.reimbursement_service.get_reimbursement_shares(self.transaction_id)
        self.assertEqual(len(shares), 1)
        self.assertIn("Jane Smith", shares)
        self.assertEqual(shares["Jane Smith"], Decimal("40"))
        
        # Verify repository calls
        self.property_repo.get_by_id.assert_called_with(self.property_id)
        self.transaction_repo.update.assert_called_once()
    
    def test_process_new_transaction_income(self):
        """Test processing a new income transaction."""
        # Create an income transaction
        income_transaction = Transaction(
            id=self.transaction_id,
            property_id=self.property_id,
            type="income",
            category="Rent",
            description="Test income",
            amount=Decimal("100.00"),
            date="2025-04-26",
            collector_payer="John Doe"
        )
        
        # Call the method
        result = self.reimbursement_service.process_new_transaction(income_transaction)
        
        # Verify the result
        self.assertEqual(result, income_transaction)
        self.assertIsNone(result.reimbursement)
        
        # Verify repository calls - should not call any repositories
        self.property_repo.get_by_id.assert_not_called()
        self.transaction_repo.update.assert_not_called()
    
    def test_get_pending_reimbursements_for_user(self):
        """Test getting pending reimbursements for a user."""
        # Set up mocks
        user = MagicMock()
        user.name = "Jane Smith"
        self.property_access_service.user_repository.get_by_id.return_value = user
        self.property_access_service.get_accessible_properties.return_value = [self.property]
        
        # Create a transaction with pending reimbursement
        transaction = Transaction(
            id=self.transaction_id,
            property_id=self.property_id,
            type="expense",
            category="Repairs",
            description="Test expense",
            amount=Decimal("100.00"),
            date="2025-04-26",
            collector_payer="John Doe",
            reimbursement=Reimbursement(reimbursement_status="pending")
        )
        
        self.transaction_repo.get_pending_reimbursements.return_value = [transaction]
        
        # Call the method
        result = self.reimbursement_service.get_pending_reimbursements_for_user(self.user_id)
        
        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], transaction)
        self.assertEqual(result[0][1], self.property)
        
        # Verify repository calls
        self.property_access_service.user_repository.get_by_id.assert_called_once_with(self.user_id)
        self.property_access_service.get_accessible_properties.assert_called_once_with(self.user_id)
        self.transaction_repo.get_pending_reimbursements.assert_called_once()
    
    def test_get_reimbursements_owed_by_user(self):
        """Test getting reimbursements owed by a user."""
        # Set up mocks
        user = MagicMock()
        user.name = "Jane Smith"
        self.property_access_service.user_repository.get_by_id.return_value = user
        self.property_access_service.get_accessible_properties.return_value = [self.property]
        
        # Create a transaction with pending reimbursement
        transaction = Transaction(
            id=self.transaction_id,
            property_id=self.property_id,
            type="expense",
            category="Repairs",
            description="Test expense",
            amount=Decimal("100.00"),
            date="2025-04-26",
            collector_payer="John Doe",
            reimbursement=Reimbursement(reimbursement_status="pending")
        )
        
        self.transaction_repo.get_pending_reimbursements.return_value = [transaction]
        self.transaction_repo.get_in_progress_reimbursements.return_value = []
        
        # Call the method
        result = self.reimbursement_service.get_reimbursements_owed_by_user(self.user_id)
        
        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], transaction)
        self.assertEqual(result[0][1], self.property)
        
        # Verify repository calls
        self.property_access_service.user_repository.get_by_id.assert_called_once_with(self.user_id)
        self.property_access_service.get_accessible_properties.assert_called_once_with(self.user_id)
        self.transaction_repo.get_pending_reimbursements.assert_called_once()
        self.transaction_repo.get_in_progress_reimbursements.assert_called_once()


if __name__ == '__main__':
    unittest.main()
