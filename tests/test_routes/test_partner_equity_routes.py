"""
Test module for the partner equity routes.

This module contains tests for the partner equity routes.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from decimal import Decimal
from flask import Flask, request, session

from src.models.property import Property, Partner
from src.models.partner_contribution import PartnerContribution
from src.routes.partner_equity_routes import partner_equity_bp


class TestPartnerEquityRoutes:
    """Test class for the partner equity routes."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask test app with the partner equity blueprint."""
        app = Flask(__name__)
        app.register_blueprint(partner_equity_bp)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-key'
        
        # Mock the auth middleware
        with patch('src.routes.partner_equity_routes.login_required') as mock_login:
            with patch('src.routes.partner_equity_routes.property_access_required') as mock_access:
                with patch('src.routes.partner_equity_routes.property_manager_required') as mock_manager:
                    # Configure mocks to pass through the decorated function
                    mock_login.return_value = lambda f: f
                    mock_access.return_value = lambda f: f
                    mock_manager.return_value = lambda f: f
                    
                    yield app
    
    @pytest.fixture
    def client(self, app):
        """Create a test client for the app."""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = 'test-user-id'
                sess['user_email'] = 'test@example.com'
                sess['user_role'] = 'Admin'
                sess['_test_mode'] = True
                sess['login_time'] = "2025-04-27T11:00:00"
                sess['remember'] = False
                sess['expires_at'] = "2025-04-27T12:00:00"
            
            # Add user_id and user_name to request
            @app.before_request
            def before_request():
                request.user_id = 'test-user-id'
                request.user_name = 'Test User'
                
                # Set up g.current_user for the request
                from src.models.user import User, PropertyAccess
                from flask import g
                
                # Create a mock user with admin role
                # The is_admin() method will return True because role is 'Admin'
                g.current_user = User(
                    id='test-user-id',
                    email='test@example.com',
                    first_name='Test',
                    last_name='User',
                    password='hashed_password',
                    role='Admin',
                    property_access=[
                        PropertyAccess(property_id="test-property-id", access_level="owner", equity_share=100.0)
                    ]
                )
            
            yield client
    
    @pytest.fixture
    def mock_property(self):
        """Create a mock property."""
        # Create a mock property instead of a real one
        test_property = MagicMock()
        test_property.id = "test-property-id"
        test_property.address = "123 Test St"
        test_property.purchase_price = Decimal("200000")
        test_property.purchase_date = "2025-01-01"
        
        # Create mock partners
        partner1 = MagicMock(spec=Partner)
        partner1.name = "Partner 1"
        partner1.equity_share = Decimal("60")
        partner1.is_property_manager = True
        partner1.visibility_settings = {
            "financial_details": True,
            "transaction_history": True,
            "partner_contributions": True,
            "property_documents": True
        }
        
        partner2 = MagicMock(spec=Partner)
        partner2.name = "Partner 2"
        partner2.equity_share = Decimal("40")
        partner2.is_property_manager = False
        partner2.visibility_settings = {
            "financial_details": False,
            "transaction_history": True,
            "partner_contributions": True,
            "property_documents": False
        }
        
        test_property.partners = [partner1, partner2]
        test_property.dict = MagicMock(return_value={
            "id": "test-property-id",
            "address": "123 Test St",
            "purchase_price": 200000,
            "purchase_date": "2025-01-01",
            "partners": [
                {
                    "name": "Partner 1",
                    "equity_share": 60,
                    "is_property_manager": True,
                    "visibility_settings": {
                        "financial_details": True,
                        "transaction_history": True,
                        "partner_contributions": True,
                        "property_documents": True
                    }
                },
                {
                    "name": "Partner 2",
                    "equity_share": 40,
                    "is_property_manager": False,
                    "visibility_settings": {
                        "financial_details": False,
                        "transaction_history": True,
                        "partner_contributions": True,
                        "property_documents": False
                    }
                }
            ]
        })
        
        return test_property
    
    @pytest.fixture
    def mock_contributions(self):
        """Create mock contributions."""
        return [
            PartnerContribution(
                id="contrib-1",
                property_id="test-property-id",
                partner_name="Partner 1",
                amount=Decimal("10000"),
                contribution_type="contribution",
                date="2025-01-15"
            ),
            PartnerContribution(
                id="contrib-2",
                property_id="test-property-id",
                partner_name="Partner 2",
                amount=Decimal("5000"),
                contribution_type="contribution",
                date="2025-01-15"
            )
        ]
    
    def test_get_partners(self, client, mock_property):
        """Test getting partners for a property."""
        with patch('src.routes.partner_equity_routes.property_access_service') as mock_service:
            # Configure mock
            mock_service.property_repository.get_by_id.return_value = mock_property
            
            # Mock the property.dict() method to return a proper JSON-serializable object
            with patch.object(mock_property, 'partners', [
                MagicMock(
                    name="Partner 1",
                    equity_share=Decimal("60"),
                    is_property_manager=True,
                    dict=MagicMock(return_value={
                        "name": "Partner 1",
                        "equity_share": 60,
                        "is_property_manager": True,
                        "visibility_settings": {
                            "financial_details": True,
                            "transaction_history": True,
                            "partner_contributions": True,
                            "property_documents": True
                        }
                    })
                ),
                MagicMock(
                    name="Partner 2",
                    equity_share=Decimal("40"),
                    is_property_manager=False,
                    dict=MagicMock(return_value={
                        "name": "Partner 2",
                        "equity_share": 40,
                        "is_property_manager": False,
                        "visibility_settings": {
                            "financial_details": False,
                            "transaction_history": True,
                            "partner_contributions": True,
                            "property_documents": False
                        }
                    })
                )
            ]):
                # Make request
                response = client.get('/api/partner-equity/partners/test-property-id')
                
                # Check response
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert len(data['partners']) == 2
                assert data['partners'][0]['name'] == "Partner 1"
                assert data['partners'][0]['equity_share'] == 60
                assert data['partners'][0]['is_property_manager'] is True
                assert data['partners'][1]['name'] == "Partner 2"
                assert data['partners'][1]['equity_share'] == 40
                assert data['partners'][1]['is_property_manager'] is False
    
    def test_get_partners_property_not_found(self, client):
        """Test getting partners for a property that doesn't exist."""
        with patch('src.routes.partner_equity_routes.property_access_service') as mock_service:
            # Configure mock
            mock_service.property_repository.get_by_id.return_value = None
            
            # Make request
            response = client.get('/api/partner-equity/partners/test-property-id')
            
            # Check response
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Property not found' in data['message']
    
    def test_add_partner(self, client):
        """Test adding a partner to a property."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.add_partner.return_value = True
            
            # Make request
            response = client.post(
                '/api/partner-equity/partners/test-property-id',
                json={
                    'name': 'Partner 3',
                    'equity_share': 10,
                    'is_property_manager': False
                }
            )
            
            # Check response
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Partner added successfully' in data['message']
            
            # Check service call
            mock_service.add_partner.assert_called_once()
    
    def test_add_partner_missing_fields(self, client):
        """Test adding a partner with missing fields."""
        # Make request with missing equity_share
        response = client.post(
            '/api/partner-equity/partners/test-property-id',
            json={
                'name': 'Partner 3'
            }
        )
        
        # Check response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Missing required field' in data['message']
    
    def test_update_partner(self, client):
        """Test updating a partner for a property."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.update_partner_equity.return_value = True
            mock_service.update_partner_visibility_settings.return_value = True
            
            # Make request
            response = client.put(
                '/api/partner-equity/partners/test-property-id/Partner 1',
                json={
                    'equity_share': 70,
                    'visibility_settings': {
                        'financial_details': False,
                        'transaction_history': True,
                        'partner_contributions': True,
                        'property_documents': False
                    }
                }
            )
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Partner updated successfully' in data['message']
            
            # Check service calls
            mock_service.update_partner_equity.assert_called_once()
            mock_service.update_partner_visibility_settings.assert_called_once()
    
    def test_remove_partner(self, client):
        """Test removing a partner from a property."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.remove_partner.return_value = True
            
            # Make request
            response = client.delete('/api/partner-equity/partners/test-property-id/Partner 2')
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Partner removed successfully' in data['message']
            
            # Check service call
            mock_service.remove_partner.assert_called_once()
    
    def test_get_contributions(self, client, mock_contributions):
        """Test getting contributions for a property."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.get_contributions_by_property.return_value = mock_contributions
            
            # Make request
            response = client.get('/api/partner-equity/contributions/test-property-id')
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['contributions']) == 2
            assert data['contributions'][0]['partner_name'] == "Partner 1"
            assert float(data['contributions'][0]['amount']) == 10000.0
            assert data['contributions'][0]['contribution_type'] == "contribution"
            assert data['contributions'][1]['partner_name'] == "Partner 2"
            assert float(data['contributions'][1]['amount']) == 5000.0
            assert data['contributions'][1]['contribution_type'] == "contribution"
    
    def test_get_contributions_by_partner(self, client, mock_contributions):
        """Test getting contributions for a property and partner."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.get_contributions_by_property_and_partner.return_value = [mock_contributions[0]]
            
            # Make request
            response = client.get('/api/partner-equity/contributions/test-property-id?partner_name=Partner 1')
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['contributions']) == 1
            assert data['contributions'][0]['partner_name'] == "Partner 1"
            assert float(data['contributions'][0]['amount']) == 10000.0
            assert data['contributions'][0]['contribution_type'] == "contribution"
    
    def test_add_contribution(self, client):
        """Test adding a contribution for a partner."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.add_contribution.return_value = "new-contrib-id"
            
            # Make request
            response = client.post(
                '/api/partner-equity/contributions/test-property-id',
                json={
                    'partner_name': 'Partner 1',
                    'amount': 5000,
                    'contribution_type': 'contribution',
                    'date': '2025-02-15',
                    'notes': 'Additional investment'
                }
            )
            
            # Check response
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Contribution added successfully' in data['message']
            assert data['contribution_id'] == "new-contrib-id"
            
            # Check service call
            mock_service.add_contribution.assert_called_once()
    
    def test_add_contribution_missing_fields(self, client):
        """Test adding a contribution with missing fields."""
        # Make request with missing amount
        response = client.post(
            '/api/partner-equity/contributions/test-property-id',
            json={
                'partner_name': 'Partner 1',
                'contribution_type': 'contribution',
                'date': '2025-02-15'
            }
        )
        
        # Check response
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Missing required field' in data['message']
    
    def test_get_contribution_totals(self, client):
        """Test getting total contributions for a property."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.get_total_contributions_by_property.return_value = {
                "Partner 1": 9000.0,
                "Partner 2": 5000.0
            }
            
            # Make request
            response = client.get('/api/partner-equity/contributions/totals/test-property-id')
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['totals']['Partner 1'] == 9000.0
            assert data['totals']['Partner 2'] == 5000.0
            
            # Check service call
            mock_service.get_total_contributions_by_property.assert_called_once_with("test-property-id")
    
    def test_get_partner_visibility(self, client, mock_property):
        """Test getting visibility settings for a partner."""
        with patch('src.routes.partner_equity_routes.property_access_service') as mock_service:
            # Configure mock
            mock_service.property_repository.get_by_id.return_value = mock_property
            
            # Make request
            response = client.get('/api/partner-equity/visibility/test-property-id/Partner 2')
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['visibility_settings']['financial_details'] is False
            assert data['visibility_settings']['transaction_history'] is True
            assert data['visibility_settings']['partner_contributions'] is True
            assert data['visibility_settings']['property_documents'] is False
    
    def test_get_partner_visibility_partner_not_found(self, client, mock_property):
        """Test getting visibility settings for a partner that doesn't exist."""
        with patch('src.routes.partner_equity_routes.property_access_service') as mock_service:
            # Configure mock
            mock_service.property_repository.get_by_id.return_value = mock_property
            
            # Make request
            response = client.get('/api/partner-equity/visibility/test-property-id/Partner 3')
            
            # Check response
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'Partner not found' in data['message']
    
    def test_update_partner_visibility(self, client):
        """Test updating visibility settings for a partner."""
        with patch('src.routes.partner_equity_routes.partner_equity_service') as mock_service:
            # Configure mock
            mock_service.update_partner_visibility_settings.return_value = True
            
            # Make request
            response = client.put(
                '/api/partner-equity/visibility/test-property-id/Partner 1',
                json={
                    'financial_details': False,
                    'transaction_history': True,
                    'partner_contributions': True,
                    'property_documents': False
                }
            )
            
            # Check response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'Visibility settings updated successfully' in data['message']
            
            # Check service call
            mock_service.update_partner_visibility_settings.assert_called_once()
