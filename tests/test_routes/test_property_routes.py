"""
Test module for property routes.

This module contains tests for the property routes.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from flask import session, g

from src.models.property import Property, Partner
from src.models.user import User, PropertyAccess
from src.services.auth_service import AuthService


@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    user_repo = MagicMock()
    
    # Create a test user
    test_user = MagicMock()
    test_user.id = "test-user"
    test_user.name = "Test User"
    test_user.is_admin.return_value = False
    test_user.is_authenticated = True
    test_user.is_active = True
    test_user.has_property_access.return_value = True
    
    # Set up repository methods
    user_repo.get_by_id.return_value = test_user
    
    # Apply the patch
    with patch('src.services.auth_service.UserRepository', return_value=user_repo):
        yield user_repo


@pytest.fixture
def mock_auth_service(mock_user_repository):
    """Create a mock authentication service."""
    auth_service = MagicMock(spec=AuthService)
    
    # Get the test user from the repository
    test_user = mock_user_repository.get_by_id.return_value
    
    # Set up auth service methods
    auth_service.validate_session.return_value = (True, None)
    auth_service.get_current_user.return_value = test_user
    auth_service.add_security_headers.side_effect = lambda response: response
    
    # Apply the patch
    with patch('src.utils.auth_middleware.AuthService', return_value=auth_service):
        yield auth_service


@pytest.fixture
def mock_user(mock_auth_service):
    """Create a mock user for testing."""
    user = MagicMock()
    user.id = "test-user"
    user.name = "Test User"
    user.is_admin.return_value = False
    user.is_authenticated = True
    user.is_active = True
    user.has_property_access.return_value = True
    return user


@pytest.fixture
def mock_properties():
    """Create mock properties for testing."""
    # Create mock Property objects instead of real ones
    prop1 = MagicMock()
    prop1.id = "prop1"
    prop1.address = "123 Main St"
    prop1.purchase_price = Decimal("200000")
    prop1.purchase_date = "2025-01-01"
    
    # Create mock Partner for prop1
    partner1 = MagicMock()
    partner1.name = "Test User"
    partner1.equity_share = Decimal("100")
    partner1.is_property_manager = True
    partner1.dict.return_value = {
        "name": "Test User",
        "equity_share": "100",
        "is_property_manager": True
    }
    
    prop1.partners = [partner1]
    prop1.dict.return_value = {
        "id": "prop1",
        "address": "123 Main St",
        "purchase_price": "200000",
        "purchase_date": "2025-01-01",
        "partners": [partner1.dict()]
    }
    prop1.get_property_manager.return_value = partner1
    prop1.calculate_cash_flow.return_value = Decimal("500")
    prop1.calculate_cap_rate.return_value = Decimal("6.0")
    prop1.calculate_cash_on_cash_return.return_value = Decimal("8.0")
    
    # Create mock Property 2
    prop2 = MagicMock()
    prop2.id = "prop2"
    prop2.address = "456 Oak Ave"
    prop2.purchase_price = Decimal("300000")
    prop2.purchase_date = "2025-02-01"
    
    # Create mock Partners for prop2
    partner2_1 = MagicMock()
    partner2_1.name = "Test User"
    partner2_1.equity_share = Decimal("50")
    partner2_1.is_property_manager = True
    partner2_1.dict.return_value = {
        "name": "Test User",
        "equity_share": "50",
        "is_property_manager": True
    }
    
    partner2_2 = MagicMock()
    partner2_2.name = "Partner User"
    partner2_2.equity_share = Decimal("50")
    partner2_2.is_property_manager = False
    partner2_2.dict.return_value = {
        "name": "Partner User",
        "equity_share": "50",
        "is_property_manager": False
    }
    
    prop2.partners = [partner2_1, partner2_2]
    prop2.dict.return_value = {
        "id": "prop2",
        "address": "456 Oak Ave",
        "purchase_price": "300000",
        "purchase_date": "2025-02-01",
        "partners": [partner2_1.dict(), partner2_2.dict()]
    }
    prop2.get_property_manager.return_value = partner2_1
    prop2.calculate_cash_flow.return_value = Decimal("700")
    prop2.calculate_cap_rate.return_value = Decimal("7.0")
    prop2.calculate_cash_on_cash_return.return_value = Decimal("9.0")
    
    return [prop1, prop2]


class TestPropertyRoutes:
    """Test class for property routes."""

    @patch('src.routes.property_routes.property_access_service')
    @patch('src.routes.property_routes.property_repository')
    def test_get_properties(self, mock_repo, mock_access_service, client, mock_properties, mock_user):
        """Test getting properties."""
        # Mock repository response
        mock_access_service.get_accessible_properties.return_value = mock_properties
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.get("/api/properties/")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "properties" in data
            assert len(data["properties"]) == 2
            
            # Verify property data
            properties = data["properties"]
            assert properties[0]["address"] == "123 Main St"
            assert properties[1]["address"] == "456 Oak Ave"
            
            # Verify repository was called
            mock_access_service.get_accessible_properties.assert_called_once_with("test-user")

    @patch('src.routes.property_routes.property_access_service')
    @patch('src.routes.property_routes.property_repository')
    def test_get_property(self, mock_repo, mock_access_service, client, mock_properties, mock_user):
        """Test getting a specific property."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_properties[0]
        mock_access_service.get_property_manager.return_value = None
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.get("/api/properties/prop1")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "property" in data
            assert data["property"]["address"] == "123 Main St"
            assert data["property"]["purchase_price"] == "200000"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("prop1")

    @patch('src.routes.property_routes.property_access_service')
    @patch('src.routes.property_routes.property_repository')
    @patch('src.routes.property_routes.geoapify_service')
    def test_create_property(self, mock_geoapify, mock_repo, mock_access_service, client, mock_properties, mock_user):
        """Test creating a property."""
        # Mock repository response
        mock_repo.address_exists.return_value = False
        mock_repo.create.return_value = mock_properties[0]
        
        # Mock geoapify service
        mock_geoapify.standardize_address.return_value = "123 Main St, City, State"
        
        # Mock property access service
        mock_access_service.sync_property_partners.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
            sess['user_name'] = 'Test User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Create property data
            property_data = {
                "address": "123 Main St",
                "purchase_price": 200000,
                "purchase_date": "2025-01-01",
                "partners": [
                    {
                        "name": "Test User",
                        "equity_share": 100,
                        "is_property_manager": True
                    }
                ]
            }
            
            # Make request
            response = client.post(
                "/api/properties/",
                data=json.dumps(property_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 201
            data = json.loads(response.data)
            assert "property" in data
            assert data["message"] == "Property created successfully"
            
            # Verify repository was called
            mock_repo.address_exists.assert_called_once_with("123 Main St")
            mock_repo.create.assert_called_once()
            mock_access_service.sync_property_partners.assert_called_once_with("prop1")

    @patch('src.routes.property_routes.property_access_service')
    @patch('src.routes.property_routes.property_repository')
    @patch('src.routes.property_routes.geoapify_service')
    def test_update_property(self, mock_geoapify, mock_repo, mock_access_service, client, mock_properties, mock_user):
        """Test updating a property."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_properties[0]
        mock_repo.address_exists.return_value = False
        
        # Mock geoapify service
        mock_geoapify.standardize_address.return_value = "456 Oak Ave, City, State"
        
        # Mock property access service
        mock_access_service.sync_property_partners.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Create property data
            property_data = {
                "address": "456 Oak Ave",
                "purchase_price": 250000,
                "purchase_date": "2025-01-01",
                "partners": [
                    {
                        "name": "Test User",
                        "equity_share": 100,
                        "is_property_manager": True
                    }
                ]
            }
            
            # Make request
            response = client.put(
                "/api/properties/prop1",
                data=json.dumps(property_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "property" in data
            assert data["message"] == "Property updated successfully"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("prop1")
            mock_repo.update.assert_called_once()
            mock_access_service.sync_property_partners.assert_called_once_with("prop1")

    @patch('src.routes.property_routes.property_access_service')
    @patch('src.routes.property_routes.property_repository')
    def test_delete_property(self, mock_repo, mock_access_service, client, mock_properties, mock_user):
        """Test deleting a property."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_properties[0]
        mock_repo.delete.return_value = True
        
        # Mock property access service
        mock_user_with_access = MagicMock()
        mock_user_with_access.id = 'test-user'
        mock_access_service.get_users_with_property_access.return_value = [mock_user_with_access]
        mock_access_service.revoke_property_access.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.delete("/api/properties/prop1")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["message"] == "Property deleted successfully"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("prop1")
            mock_repo.delete.assert_called_once_with("prop1")
            mock_access_service.get_users_with_property_access.assert_called_once_with("prop1")
            mock_access_service.revoke_property_access.assert_called_once_with("test-user", "prop1")

    @patch('src.routes.property_routes.property_repository')
    def test_get_property_partners(self, mock_repo, client, mock_properties, mock_user):
        """Test getting partners for a property."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_properties[1]
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.get("/api/properties/prop2/partners")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "partners" in data
            assert len(data["partners"]) == 2
            assert data["partners"][0]["name"] == "Test User"
            assert data["partners"][1]["name"] == "Partner User"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("prop2")

    @patch('src.routes.property_routes.property_access_service')
    @patch('src.routes.property_routes.property_repository')
    def test_update_property_partners(self, mock_repo, mock_access_service, client, mock_properties, mock_user):
        """Test updating partners for a property."""
        # Mock repository response
        mock_repo.get_by_id.return_value = mock_properties[1]
        
        # Mock property access service
        mock_access_service.sync_property_partners.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Create partners data
            partners_data = [
                {
                    "name": "Test User",
                    "equity_share": 75,
                    "is_property_manager": True
                },
                {
                    "name": "Partner User",
                    "equity_share": 25,
                    "is_property_manager": False
                }
            ]
            
            # Make request
            response = client.put(
                "/api/properties/prop2/partners",
                data=json.dumps(partners_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "partners" in data
            assert data["message"] == "Partners updated successfully"
            
            # Verify repository was called
            mock_repo.get_by_id.assert_called_once_with("prop2")
            mock_repo.update.assert_called_once()
            mock_access_service.sync_property_partners.assert_called_once_with("prop2")

    @patch('src.routes.property_routes.property_access_service')
    def test_set_property_manager(self, mock_access_service, client, mock_user):
        """Test setting a property manager."""
        # Mock property access service
        mock_access_service.designate_property_manager.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Create request data
            request_data = {
                "user_id": "partner-user"
            }
            
            # Make request
            response = client.put(
                "/api/properties/prop2/manager",
                data=json.dumps(request_data),
                content_type="application/json"
            )
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["message"] == "Property manager set successfully"
            
            # Verify service was called
            mock_access_service.designate_property_manager.assert_called_once_with(
                user_id="partner-user",
                property_id="prop2",
                current_user_id="test-user"
            )

    @patch('src.routes.property_routes.property_access_service')
    def test_remove_property_manager(self, mock_access_service, client, mock_user):
        """Test removing a property manager."""
        # Mock property access service
        mock_access_service.remove_property_manager.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.delete("/api/properties/prop2/manager")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["message"] == "Property manager removed successfully"
            
            # Verify service was called
            mock_access_service.remove_property_manager.assert_called_once_with(
                property_id="prop2",
                current_user_id="test-user"
            )

    @patch('src.routes.property_routes.property_access_service')
    @patch('src.routes.property_routes.property_repository')
    def test_get_property_by_address(self, mock_repo, mock_access_service, client, mock_properties, mock_user):
        """Test getting a property by address."""
        # Mock repository response
        mock_repo.get_by_address.return_value = mock_properties[0]
        
        # Mock property access service
        mock_access_service.can_access_property.return_value = True
        
        # Use the test client with a request context
        with client.session_transaction() as sess:
            sess['user_id'] = 'test-user'
            sess['user_role'] = 'User'
        
        # Set up g.current_user
        with client.application.app_context():
            g.current_user = mock_user
            
            # Make request
            response = client.get("/api/properties/by-address?address=123%20Main%20St")
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert "property" in data
            assert data["property"]["address"] == "123 Main St"
            
            # Verify repository was called
            mock_repo.get_by_address.assert_called_once_with("123 Main St")
            mock_access_service.can_access_property.assert_called_once_with("test-user", "prop1")
