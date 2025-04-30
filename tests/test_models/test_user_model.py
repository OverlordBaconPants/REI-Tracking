"""
Test module for the User model.

This module contains tests for the User model, including property access functionality.
"""

import pytest
from src.models.user import User, PropertyAccess


class TestUserModel:
    """Test cases for the User model."""
    
    def test_user_creation(self):
        """Test creating a user."""
        # Create a user
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User"
        )
        
        # Check user properties
        assert user.id == "test-user-id"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.name == "Test User"
        assert user.password == "hashed-password"
        assert user.role == "User"
        assert user.property_access == []
    
    def test_user_with_property_access(self):
        """Test creating a user with property access."""
        # Create property access
        property_access = PropertyAccess(
            property_id="test-property-id",
            access_level="owner",
            equity_share=50.0
        )
        
        # Create a user with property access
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User",
            property_access=[property_access]
        )
        
        # Check property access
        assert len(user.property_access) == 1
        assert user.property_access[0].property_id == "test-property-id"
        assert user.property_access[0].access_level == "owner"
        assert user.property_access[0].equity_share == 50.0
    
    def test_has_property_access(self):
        """Test checking if a user has access to a property."""
        # Create property access
        property_access = PropertyAccess(
            property_id="test-property-id",
            access_level="owner",
            equity_share=50.0
        )
        
        # Create a user with property access
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User",
            property_access=[property_access]
        )
        
        # Check property access
        assert user.has_property_access("test-property-id")
        assert user.has_property_access("test-property-id", "owner")
        assert user.has_property_access("test-property-id", "manager")
        assert user.has_property_access("test-property-id", "editor")
        assert user.has_property_access("test-property-id", "viewer")
        assert not user.has_property_access("nonexistent-property-id")
    
    def test_has_property_access_with_different_levels(self):
        """Test checking if a user has access to a property with different access levels."""
        # Create property access with different levels
        property_access_owner = PropertyAccess(
            property_id="property-owner",
            access_level="owner",
            equity_share=50.0
        )
        property_access_manager = PropertyAccess(
            property_id="property-manager",
            access_level="manager",
            equity_share=0.0
        )
        property_access_editor = PropertyAccess(
            property_id="property-editor",
            access_level="editor",
            equity_share=0.0
        )
        property_access_viewer = PropertyAccess(
            property_id="property-viewer",
            access_level="viewer",
            equity_share=0.0
        )
        
        # Create a user with property access
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User",
            property_access=[
                property_access_owner,
                property_access_manager,
                property_access_editor,
                property_access_viewer
            ]
        )
        
        # Check property access with different levels
        # Owner can access at all levels
        assert user.has_property_access("property-owner", "owner")
        assert user.has_property_access("property-owner", "manager")
        assert user.has_property_access("property-owner", "editor")
        assert user.has_property_access("property-owner", "viewer")
        
        # Manager can access at manager, editor, and viewer levels
        assert not user.has_property_access("property-manager", "owner")
        assert user.has_property_access("property-manager", "manager")
        assert user.has_property_access("property-manager", "editor")
        assert user.has_property_access("property-manager", "viewer")
        
        # Editor can access at editor and viewer levels
        assert not user.has_property_access("property-editor", "owner")
        assert not user.has_property_access("property-editor", "manager")
        assert user.has_property_access("property-editor", "editor")
        assert user.has_property_access("property-editor", "viewer")
        
        # Viewer can access only at viewer level
        assert not user.has_property_access("property-viewer", "owner")
        assert not user.has_property_access("property-viewer", "manager")
        assert not user.has_property_access("property-viewer", "editor")
        assert user.has_property_access("property-viewer", "viewer")
    
    def test_admin_property_access(self):
        """Test that admin users have access to all properties."""
        # Create an admin user
        admin_user = User(
            id="admin-user-id",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="hashed-password",
            role="Admin"
        )
        
        # Check property access
        assert admin_user.has_property_access("any-property-id")
        assert admin_user.has_property_access("any-property-id", "owner")
        assert admin_user.has_property_access("any-property-id", "manager")
        assert admin_user.has_property_access("any-property-id", "editor")
        assert admin_user.has_property_access("any-property-id", "viewer")
    
    def test_is_property_manager(self):
        """Test checking if a user is a property manager."""
        # Create property access
        property_access_manager = PropertyAccess(
            property_id="property-manager",
            access_level="manager",
            equity_share=0.0
        )
        property_access_editor = PropertyAccess(
            property_id="property-editor",
            access_level="editor",
            equity_share=0.0
        )
        
        # Create a user with property access
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User",
            property_access=[
                property_access_manager,
                property_access_editor
            ]
        )
        
        # Check if user is a property manager
        assert user.is_property_manager("property-manager")
        assert not user.is_property_manager("property-editor")
        assert not user.is_property_manager("nonexistent-property-id")
    
    def test_is_property_owner(self):
        """Test checking if a user is a property owner."""
        # Create property access
        property_access_owner = PropertyAccess(
            property_id="property-owner",
            access_level="owner",
            equity_share=50.0
        )
        property_access_manager = PropertyAccess(
            property_id="property-manager",
            access_level="manager",
            equity_share=0.0
        )
        
        # Create a user with property access
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User",
            property_access=[
                property_access_owner,
                property_access_manager
            ]
        )
        
        # Check if user is a property owner
        assert user.is_property_owner("property-owner")
        assert not user.is_property_owner("property-manager")
        assert not user.is_property_owner("nonexistent-property-id")
    
    def test_get_accessible_properties(self):
        """Test getting properties a user has access to."""
        # Create property access
        property_access_1 = PropertyAccess(
            property_id="property-1",
            access_level="owner",
            equity_share=50.0
        )
        property_access_2 = PropertyAccess(
            property_id="property-2",
            access_level="manager",
            equity_share=0.0
        )
        
        # Create a user with property access
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User",
            property_access=[
                property_access_1,
                property_access_2
            ]
        )
        
        # Get accessible properties
        accessible_properties = user.get_accessible_properties()
        assert len(accessible_properties) == 2
        assert "property-1" in accessible_properties
        assert "property-2" in accessible_properties
        
        # Get accessible properties with required level
        owner_properties = user.get_accessible_properties("owner")
        assert len(owner_properties) == 1
        assert "property-1" in owner_properties
        
        manager_properties = user.get_accessible_properties("manager")
        assert len(manager_properties) == 2
        assert "property-1" in manager_properties
        assert "property-2" in manager_properties
    
    def test_admin_get_accessible_properties(self):
        """Test that admin users return an empty set for get_accessible_properties."""
        # Create an admin user
        admin_user = User(
            id="admin-user-id",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="hashed-password",
            role="Admin"
        )
        
        # Get accessible properties
        accessible_properties = admin_user.get_accessible_properties()
        assert accessible_properties == set()
    
    def test_model_dump_excludes_password(self):
        """Test that model_dump excludes the password field."""
        # Create a user
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User"
        )
        
        # Get dictionary representation
        user_dict = user.model_dump()
        
        # Check that password is excluded
        assert "password" not in user_dict
    
    def test_dict_method_excludes_password(self):
        """Test that dict method excludes the password field."""
        # Create a user
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User"
        )
        
        # Get dictionary representation
        user_dict = user.dict()
        
        # Check that password is excluded
        assert "password" not in user_dict
    
    def test_email_validation(self):
        """Test email validation."""
        # Valid email
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="User"
        )
        assert user.email == "test@example.com"
        
        # Invalid email
        with pytest.raises(ValueError):
            User(
                id="test-user-id",
                email="invalid-email",
                first_name="Test",
                last_name="User",
                password="hashed-password",
                role="User"
            )
    
    def test_role_validation(self):
        """Test role validation."""
        # Valid role
        user = User(
            id="test-user-id",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="hashed-password",
            role="Admin"
        )
        assert user.role == "Admin"
        
        # Invalid role
        with pytest.raises(ValueError):
            User(
                id="test-user-id",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                password="hashed-password",
                role="InvalidRole"
            )
    
    def test_property_access_validation(self):
        """Test property access validation."""
        # Valid access level
        property_access = PropertyAccess(
            property_id="test-property-id",
            access_level="owner",
            equity_share=50.0
        )
        assert property_access.access_level == "owner"
        
        # Invalid access level
        with pytest.raises(ValueError):
            PropertyAccess(
                property_id="test-property-id",
                access_level="invalid-level",
                equity_share=50.0
            )
