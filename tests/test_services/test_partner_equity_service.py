"""
Test module for the PartnerEquityService.

This module contains tests for the PartnerEquityService.
"""

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime

from src.models.property import Property, Partner
from src.models.partner_contribution import PartnerContribution
from src.services.partner_equity_service import PartnerEquityService


class TestPartnerEquityService:
    """Test class for the PartnerEquityService."""
    
    @pytest.fixture
    def mock_property_repository(self):
        """Create a mock property repository."""
        mock_repo = MagicMock()
        
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
        
        partner2 = MagicMock(spec=Partner)
        partner2.name = "Partner 2"
        partner2.equity_share = Decimal("40")
        partner2.is_property_manager = False
        
        test_property.partners = [partner1, partner2]
        
        # Configure mock repository
        mock_repo.get_by_id.return_value = test_property
        mock_repo.update.return_value = True
        
        return mock_repo
    
    @pytest.fixture
    def mock_contribution_repository(self):
        """Create a mock partner contribution repository."""
        mock_repo = MagicMock()
        
        # Create test contributions
        test_contributions = [
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
            ),
            PartnerContribution(
                id="dist-1",
                property_id="test-property-id",
                partner_name="Partner 1",
                amount=Decimal("1000"),
                contribution_type="distribution",
                date="2025-03-15"
            )
        ]
        
        # Configure mock repository
        mock_repo.get_by_property.return_value = test_contributions
        mock_repo.get_by_partner.return_value = [test_contributions[0], test_contributions[2]]
        mock_repo.get_by_property_and_partner.return_value = [test_contributions[0], test_contributions[2]]
        mock_repo.create.return_value = test_contributions[0]
        mock_repo.get_total_contributions_by_property.return_value = {
            "Partner 1": 9000.0,  # 10000 - 1000
            "Partner 2": 5000.0
        }
        
        return mock_repo
    
    @pytest.fixture
    def service(self, mock_property_repository, mock_contribution_repository):
        """Create a PartnerEquityService with mock repositories."""
        return PartnerEquityService(
            property_repository=mock_property_repository,
            partner_contribution_repository=mock_contribution_repository
        )
    
    def test_add_partner(self, service, mock_property_repository):
        """Test adding a partner to a property."""
        # Test adding a new partner
        result = service.add_partner(
            property_id="test-property-id",
            partner_name="Partner 3",
            equity_share=Decimal("0"),
            is_property_manager=False
        )
        
        assert result is True
        mock_property_repository.update.assert_called_once()
    
    def test_add_partner_already_exists(self, service, mock_property_repository):
        """Test adding a partner that already exists."""
        # Test adding an existing partner
        result = service.add_partner(
            property_id="test-property-id",
            partner_name="Partner 1",
            equity_share=Decimal("60"),
            is_property_manager=True
        )
        
        assert result is False
        mock_property_repository.update.assert_not_called()
    
    def test_remove_partner(self, service, mock_property_repository):
        """Test removing a partner from a property."""
        # Test removing an existing partner
        result = service.remove_partner(
            property_id="test-property-id",
            partner_name="Partner 2"
        )
        
        assert result is True
        mock_property_repository.update.assert_called_once()
    
    def test_remove_partner_not_exists(self, service, mock_property_repository):
        """Test removing a partner that doesn't exist."""
        # Test removing a non-existent partner
        result = service.remove_partner(
            property_id="test-property-id",
            partner_name="Partner 3"
        )
        
        assert result is False
        mock_property_repository.update.assert_not_called()
    
    def test_update_partner_equity(self, service, mock_property_repository):
        """Test updating a partner's equity share."""
        # Test updating an existing partner's equity share
        result = service.update_partner_equity(
            property_id="test-property-id",
            partner_name="Partner 1",
            equity_share=Decimal("70")
        )
        
        assert result is True
        mock_property_repository.update.assert_called_once()
    
    def test_update_partner_equity_not_exists(self, service, mock_property_repository):
        """Test updating equity for a partner that doesn't exist."""
        # Test updating a non-existent partner's equity share
        result = service.update_partner_equity(
            property_id="test-property-id",
            partner_name="Partner 3",
            equity_share=Decimal("10")
        )
        
        assert result is False
        mock_property_repository.update.assert_not_called()
    
    def test_update_partner_visibility_settings(self, service, mock_property_repository):
        """Test updating a partner's visibility settings."""
        # Test updating an existing partner's visibility settings
        visibility_settings = {
            "financial_details": False,
            "transaction_history": True,
            "partner_contributions": True,
            "property_documents": False
        }
        
        result = service.update_partner_visibility_settings(
            property_id="test-property-id",
            partner_name="Partner 1",
            visibility_settings=visibility_settings
        )
        
        assert result is True
        mock_property_repository.update.assert_called_once()
    
    def test_update_partner_visibility_settings_not_exists(self, service, mock_property_repository):
        """Test updating visibility settings for a partner that doesn't exist."""
        # Test updating a non-existent partner's visibility settings
        visibility_settings = {
            "financial_details": False,
            "transaction_history": True,
            "partner_contributions": True,
            "property_documents": False
        }
        
        result = service.update_partner_visibility_settings(
            property_id="test-property-id",
            partner_name="Partner 3",
            visibility_settings=visibility_settings
        )
        
        assert result is False
        mock_property_repository.update.assert_not_called()
    
    def test_add_contribution(self, service, mock_contribution_repository):
        """Test adding a contribution for a partner."""
        # Test adding a contribution
        contribution_id = service.add_contribution(
            property_id="test-property-id",
            partner_name="Partner 1",
            amount=Decimal("5000"),
            contribution_type="contribution",
            date="2025-02-15",
            notes="Additional investment"
        )
        
        assert contribution_id is not None
        mock_contribution_repository.create.assert_called_once()
    
    def test_get_contributions_by_property(self, service, mock_contribution_repository):
        """Test getting contributions for a property."""
        # Test getting contributions by property
        contributions = service.get_contributions_by_property("test-property-id")
        
        assert len(contributions) == 3
        mock_contribution_repository.get_by_property.assert_called_once_with("test-property-id")
    
    def test_get_contributions_by_partner(self, service, mock_contribution_repository):
        """Test getting contributions for a partner."""
        # Test getting contributions by partner
        contributions = service.get_contributions_by_partner("Partner 1")
        
        assert len(contributions) == 2
        mock_contribution_repository.get_by_partner.assert_called_once_with("Partner 1")
    
    def test_get_contributions_by_property_and_partner(self, service, mock_contribution_repository):
        """Test getting contributions for a property and partner."""
        # Test getting contributions by property and partner
        contributions = service.get_contributions_by_property_and_partner(
            "test-property-id", "Partner 1"
        )
        
        assert len(contributions) == 2
        mock_contribution_repository.get_by_property_and_partner.assert_called_once_with(
            "test-property-id", "Partner 1"
        )
    
    def test_get_total_contributions_by_property(self, service, mock_contribution_repository):
        """Test getting total contributions for a property."""
        # Test getting total contributions by property
        totals = service.get_total_contributions_by_property("test-property-id")
        
        assert len(totals) == 2
        assert totals["Partner 1"] == 9000.0
        assert totals["Partner 2"] == 5000.0
        mock_contribution_repository.get_total_contributions_by_property.assert_called_once_with(
            "test-property-id"
        )
