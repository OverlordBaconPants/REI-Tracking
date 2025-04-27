"""
Test module for the PartnerContribution model.

This module contains tests for the PartnerContribution model.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from src.models.partner_contribution import PartnerContribution


class TestPartnerContribution:
    """Test class for the PartnerContribution model."""
    
    def test_create_valid_contribution(self):
        """Test creating a valid contribution."""
        contribution = PartnerContribution(
            property_id="test-property-id",
            partner_name="Test Partner",
            amount=Decimal("1000.00"),
            contribution_type="contribution",
            date="2025-01-01"
        )
        
        assert contribution.property_id == "test-property-id"
        assert contribution.partner_name == "Test Partner"
        assert contribution.amount == Decimal("1000.00")
        assert contribution.contribution_type == "contribution"
        assert contribution.date == "2025-01-01"
        assert contribution.notes is None
    
    def test_create_valid_distribution(self):
        """Test creating a valid distribution."""
        distribution = PartnerContribution(
            property_id="test-property-id",
            partner_name="Test Partner",
            amount=Decimal("500.00"),
            contribution_type="distribution",
            date="2025-01-15",
            notes="Quarterly distribution"
        )
        
        assert distribution.property_id == "test-property-id"
        assert distribution.partner_name == "Test Partner"
        assert distribution.amount == Decimal("500.00")
        assert distribution.contribution_type == "distribution"
        assert distribution.date == "2025-01-15"
        assert distribution.notes == "Quarterly distribution"
    
    def test_invalid_contribution_type(self):
        """Test creating a contribution with an invalid contribution type."""
        with pytest.raises(ValueError) as excinfo:
            PartnerContribution(
                property_id="test-property-id",
                partner_name="Test Partner",
                amount=Decimal("1000.00"),
                contribution_type="invalid",
                date="2025-01-01"
            )
        
        assert "Contribution type must be one of: contribution, distribution" in str(excinfo.value)
    
    def test_invalid_date_format(self):
        """Test creating a contribution with an invalid date format."""
        with pytest.raises(ValueError) as excinfo:
            PartnerContribution(
                property_id="test-property-id",
                partner_name="Test Partner",
                amount=Decimal("1000.00"),
                contribution_type="contribution",
                date="01/01/2025"  # Invalid format
            )
        
        assert "Invalid date format" in str(excinfo.value)
    
    def test_to_dict(self):
        """Test converting a contribution to a dictionary."""
        contribution = PartnerContribution(
            property_id="test-property-id",
            partner_name="Test Partner",
            amount=Decimal("1000.00"),
            contribution_type="contribution",
            date="2025-01-01",
            notes="Initial investment"
        )
        
        contribution_dict = contribution.dict()
        
        assert contribution_dict["property_id"] == "test-property-id"
        assert contribution_dict["partner_name"] == "Test Partner"
        assert float(contribution_dict["amount"]) == 1000.00
        assert contribution_dict["contribution_type"] == "contribution"
        assert contribution_dict["date"] == "2025-01-01"
        assert contribution_dict["notes"] == "Initial investment"
        assert "id" in contribution_dict
        assert "created_at" in contribution_dict
        assert "updated_at" in contribution_dict
