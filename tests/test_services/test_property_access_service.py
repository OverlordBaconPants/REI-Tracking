"""
Test module for the property access service.

This module contains tests for the PropertyAccessService class.
"""

import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from src.models.user import User, PropertyAccess
from src.models.property import Property, Partner
from src.services.property_access_service import PropertyAccessService


class TestPropertyAccessService(unittest.TestCase):
    """Test case for the PropertyAccessService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user_repository = MagicMock()
        self.property_repository = MagicMock()
        self.service = PropertyAccessService(
            user_repository=self.user_repository,
            property_repository=self.property_repository
        )
    
    def test_grant_property_access_new(self):
        """Test granting property access to a user who doesn't have access yet."""
        # Set up test data
        user = User(
            id="user1",
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            property_access=[]
        )
        
        # Mock the Property object instead of creating a real one
        property_obj = MagicMock()
        property_obj.id = "prop1"
        property_obj.address = "123 Main St"
        property_obj.purchase_price = Decimal("200000")
        property_obj.purchase_date = "2025-01-01"
        property_obj.partners = []
        
        # Set up mocks
        self.user_repository.get_by_id.return_value = user
        self.property_repository.get_by_id.return_value = property_obj
        self.user_repository.update.return_value = True
        
        # Call the method
        result = self.service.grant_property_access(
            user_id="user1",
            property_id="prop1",
            access_level="editor",
            equity_share=10.0,
            current_user_id="admin1"
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(len(user.property_access), 1)
        self.assertEqual(user.property_access[0].property_id, "prop1")
        self.assertEqual(user.property_access[0].access_level, "editor")
        self.assertEqual(user.property_access[0].equity_share, 10.0)
        self.user_repository.update.assert_called_once_with(user)
    
    def test_grant_property_access_existing(self):
        """Test granting property access to a user who already has access."""
        # Set up test data
        user = User(
            id="user1",
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="viewer",
                    equity_share=5.0
                )
            ]
        )
        
        # Mock the Property object instead of creating a real one
        property_obj = MagicMock()
        property_obj.id = "prop1"
        property_obj.address = "123 Main St"
        property_obj.purchase_price = Decimal("200000")
        property_obj.purchase_date = "2025-01-01"
        property_obj.partners = []
        
        # Set up mocks
        self.user_repository.get_by_id.return_value = user
        self.property_repository.get_by_id.return_value = property_obj
        self.user_repository.update.return_value = True
        
        # Call the method
        result = self.service.grant_property_access(
            user_id="user1",
            property_id="prop1",
            access_level="editor",
            equity_share=10.0,
            current_user_id="admin1"
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(len(user.property_access), 1)
        self.assertEqual(user.property_access[0].property_id, "prop1")
        self.assertEqual(user.property_access[0].access_level, "editor")
        self.assertEqual(user.property_access[0].equity_share, 10.0)
        self.user_repository.update.assert_called_once_with(user)
    
    def test_revoke_property_access(self):
        """Test revoking property access from a user."""
        # Set up test data
        user = User(
            id="user1",
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="editor",
                    equity_share=10.0
                ),
                PropertyAccess(
                    property_id="prop2",
                    access_level="viewer",
                    equity_share=None
                )
            ]
        )
        
        # Set up mocks
        self.user_repository.get_by_id.return_value = user
        self.user_repository.update.return_value = True
        
        # Call the method
        result = self.service.revoke_property_access(
            user_id="user1",
            property_id="prop1",
            current_user_id="admin1"
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(len(user.property_access), 1)
        self.assertEqual(user.property_access[0].property_id, "prop2")
        self.user_repository.update.assert_called_once_with(user)
    
    def test_designate_property_manager(self):
        """Test designating a user as a property manager."""
        # Set up test data
        user = User(
            id="user1",
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            name="Test User",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="editor",
                    equity_share=10.0
                )
            ]
        )
        
        # Mock the Property object and its partners
        partner1 = MagicMock()
        partner1.name = "Test User"
        partner1.equity_share = Decimal("10")
        partner1.is_property_manager = False
        
        partner2 = MagicMock()
        partner2.name = "Other User"
        partner2.equity_share = Decimal("90")
        partner2.is_property_manager = False
        
        property_obj = MagicMock()
        property_obj.id = "prop1"
        property_obj.address = "123 Main St"
        property_obj.purchase_price = Decimal("200000")
        property_obj.purchase_date = "2025-01-01"
        property_obj.partners = [partner1, partner2]
        
        # Set up mocks
        self.user_repository.get_by_id.return_value = user
        self.property_repository.get_by_id.return_value = property_obj
        self.user_repository.update.return_value = True
        self.property_repository.update.return_value = True
        
        # Call the method
        result = self.service.designate_property_manager(
            user_id="user1",
            property_id="prop1",
            current_user_id="admin1"
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertEqual(user.property_access[0].access_level, "manager")
        self.assertTrue(property_obj.partners[0].is_property_manager)
        self.assertFalse(property_obj.partners[1].is_property_manager)
        self.user_repository.update.assert_called_once_with(user)
        self.property_repository.update.assert_called_once_with(property_obj)
    
    def test_remove_property_manager(self):
        """Test removing a property manager."""
        # Set up test data
        user = User(
            id="user1",
            email="user@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            name="Test User",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="manager",
                    equity_share=10.0
                )
            ]
        )
        
        # Mock the Property object and its partners
        partner1 = MagicMock()
        partner1.name = "Test User"
        partner1.equity_share = Decimal("10")
        partner1.is_property_manager = True
        
        partner2 = MagicMock()
        partner2.name = "Other User"
        partner2.equity_share = Decimal("90")
        partner2.is_property_manager = False
        
        property_obj = MagicMock()
        property_obj.id = "prop1"
        property_obj.address = "123 Main St"
        property_obj.purchase_price = Decimal("200000")
        property_obj.purchase_date = "2025-01-01"
        property_obj.partners = [partner1, partner2]
        property_obj.get_property_manager.return_value = partner1
        
        # Set up mocks
        self.property_repository.get_by_id.return_value = property_obj
        self.property_repository.update.return_value = True
        self.user_repository.get_all.return_value = [user]
        self.user_repository.update.return_value = True
        
        # Call the method
        result = self.service.remove_property_manager(
            property_id="prop1",
            current_user_id="admin1"
        )
        
        # Assertions
        self.assertTrue(result)
        self.assertFalse(property_obj.partners[0].is_property_manager)
        self.assertEqual(user.property_access[0].access_level, "editor")
        self.property_repository.update.assert_called_once_with(property_obj)
        self.user_repository.update.assert_called_once_with(user)
    
    def test_sync_property_partners(self):
        """Test synchronizing property partners with user access."""
        # Set up test data
        user1 = User(
            id="user1",
            email="user1@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            name="Test User",
            property_access=[]
        )
        
        user2 = User(
            id="user2",
            email="user2@example.com",
            first_name="Other",
            last_name="User",
            password="hashed_password",
            name="Other User",
            property_access=[]
        )
        
        # Mock the Property object and its partners
        partner1 = MagicMock()
        partner1.name = "Test User"
        partner1.equity_share = Decimal("10")
        partner1.is_property_manager = True
        
        partner2 = MagicMock()
        partner2.name = "Other User"
        partner2.equity_share = Decimal("90")
        partner2.is_property_manager = False
        
        property_obj = MagicMock()
        property_obj.id = "prop1"
        property_obj.address = "123 Main St"
        property_obj.purchase_price = Decimal("200000")
        property_obj.purchase_date = "2025-01-01"
        property_obj.partners = [partner1, partner2]
        
        # Set up mocks
        self.property_repository.get_by_id.return_value = property_obj
        self.user_repository.get_all.return_value = [user1, user2]
        
        # Mock grant_property_access
        self.service.grant_property_access = MagicMock(return_value=True)
        
        # Call the method
        result = self.service.sync_property_partners(property_id="prop1")
        
        # Assertions
        self.assertTrue(result)
        self.service.grant_property_access.assert_any_call(
            user_id="user1",
            property_id="prop1",
            access_level="manager",
            equity_share=10.0
        )
        self.service.grant_property_access.assert_any_call(
            user_id="user2",
            property_id="prop1",
            access_level="owner",
            equity_share=90.0
        )
    
    def test_get_users_with_property_access(self):
        """Test getting users with access to a property."""
        # Set up test data
        user1 = User(
            id="user1",
            email="user1@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="manager",
                    equity_share=10.0
                )
            ]
        )
        
        user2 = User(
            id="user2",
            email="user2@example.com",
            first_name="Other",
            last_name="User",
            password="hashed_password",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="viewer",
                    equity_share=None
                )
            ]
        )
        
        user3 = User(
            id="user3",
            email="user3@example.com",
            first_name="Third",
            last_name="User",
            password="hashed_password",
            property_access=[
                PropertyAccess(
                    property_id="prop2",
                    access_level="editor",
                    equity_share=None
                )
            ]
        )
        
        # Set up mocks
        self.user_repository.get_all.return_value = [user1, user2, user3]
        
        # Call the method
        result = self.service.get_users_with_property_access(property_id="prop1")
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertIn(user1, result)
        self.assertIn(user2, result)
        self.assertNotIn(user3, result)
        
        # Test with access level
        result = self.service.get_users_with_property_access(
            property_id="prop1",
            access_level="manager"
        )
        
        # Assertions
        self.assertEqual(len(result), 1)
        self.assertIn(user1, result)
        self.assertNotIn(user2, result)
        self.assertNotIn(user3, result)
    
    def test_get_property_manager(self):
        """Test getting the property manager for a property."""
        # Set up test data
        user1 = User(
            id="user1",
            email="user1@example.com",
            first_name="Test",
            last_name="User",
            password="hashed_password",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="manager",
                    equity_share=10.0
                )
            ]
        )
        
        user2 = User(
            id="user2",
            email="user2@example.com",
            first_name="Other",
            last_name="User",
            password="hashed_password",
            property_access=[
                PropertyAccess(
                    property_id="prop1",
                    access_level="viewer",
                    equity_share=None
                )
            ]
        )
        
        # Mock get_users_with_property_access
        self.service.get_users_with_property_access = MagicMock(return_value=[user1])
        
        # Call the method
        result = self.service.get_property_manager(property_id="prop1")
        
        # Assertions
        self.assertEqual(result, user1)
        self.service.get_users_with_property_access.assert_called_once_with(
            property_id="prop1",
            access_level="manager"
        )
        
        # Test with no manager
        self.service.get_users_with_property_access.return_value = []
        result = self.service.get_property_manager(property_id="prop1")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
