import pytest
from datetime import datetime
from typing import Dict, Any
from utils.api_mappers import RentcastApiMapper, ApiMapperFactory


class TestRentcastApiMapper:
    """Test suite for the RentcastApiMapper class."""

    def test_map_property_comps_valid_input(self):
        """Test map_property_comps with valid input."""
        # Create a sample API response
        api_response = {
            "price": 250000,
            "priceRangeLow": 230000,
            "priceRangeHigh": 270000,
            "comparables": [
                {
                    "id": "comp1",
                    "formattedAddress": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zipCode": "12345",
                    "propertyType": "Single Family",
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "squareFootage": 1500,
                    "yearBuilt": 2000,
                    "price": 245000,
                    "listingType": "For Sale",
                    "listedDate": "2023-01-15",
                    "removedDate": "",
                    "daysOnMarket": 30,
                    "distance": 0.5,
                    "correlation": 0.9
                },
                {
                    "id": "comp2",
                    "formattedAddress": "456 Oak Ave",
                    "city": "Anytown",
                    "state": "CA",
                    "zipCode": "12345",
                    "propertyType": "Single Family",
                    "bedrooms": 4,
                    "bathrooms": 2.5,
                    "squareFootage": 1800,
                    "yearBuilt": 2005,
                    "price": 265000,
                    "listingType": "For Sale",
                    "listedDate": "2023-01-10",
                    "removedDate": "",
                    "daysOnMarket": 35,
                    "distance": 0.7,
                    "correlation": 0.85
                }
            ]
        }

        # Call the method
        result = RentcastApiMapper.map_property_comps(api_response)

        # Verify the result
        assert result is not None
        assert "last_run" in result
        assert result["estimated_value"] == 250000
        assert result["value_range_low"] == 230000
        assert result["value_range_high"] == 270000
        assert result["run_count"] == 1
        assert len(result["comparables"]) == 2

        # Verify the first comparable
        comp1 = result["comparables"][0]
        assert comp1["id"] == "comp1"
        assert comp1["formattedAddress"] == "123 Main St"
        assert comp1["city"] == "Anytown"
        assert comp1["state"] == "CA"
        assert comp1["zipCode"] == "12345"
        assert comp1["propertyType"] == "Single Family"
        assert comp1["bedrooms"] == 3
        assert comp1["bathrooms"] == 2
        assert comp1["squareFootage"] == 1500
        assert comp1["yearBuilt"] == 2000
        assert comp1["price"] == 245000
        assert comp1["listingType"] == "For Sale"
        assert comp1["listedDate"] == "2023-01-15"
        assert comp1["removedDate"] == ""
        assert comp1["daysOnMarket"] == 30
        assert comp1["distance"] == 0.5
        assert comp1["correlation"] == 0.9

        # Verify the second comparable
        comp2 = result["comparables"][1]
        assert comp2["id"] == "comp2"
        assert comp2["formattedAddress"] == "456 Oak Ave"
        assert comp2["city"] == "Anytown"
        assert comp2["state"] == "CA"
        assert comp2["zipCode"] == "12345"
        assert comp2["propertyType"] == "Single Family"
        assert comp2["bedrooms"] == 4
        assert comp2["bathrooms"] == 2.5
        assert comp2["squareFootage"] == 1800
        assert comp2["yearBuilt"] == 2005
        assert comp2["price"] == 265000
        assert comp2["listingType"] == "For Sale"
        assert comp2["listedDate"] == "2023-01-10"
        assert comp2["removedDate"] == ""
        assert comp2["daysOnMarket"] == 35
        assert comp2["distance"] == 0.7
        assert comp2["correlation"] == 0.85

    def test_map_property_comps_missing_fields(self):
        """Test map_property_comps with missing fields."""
        # Create a sample API response with missing fields
        api_response = {
            "price": 250000,
            # Missing priceRangeLow and priceRangeHigh
            "comparables": [
                {
                    "id": "comp1",
                    "formattedAddress": "123 Main St",
                    # Missing some fields
                    "bedrooms": 3,
                    "price": 245000
                }
            ]
        }

        # Call the method
        result = RentcastApiMapper.map_property_comps(api_response)

        # Verify the result
        assert result is not None
        assert "last_run" in result
        assert result["estimated_value"] == 250000
        assert result["value_range_low"] == 0  # Default value
        assert result["value_range_high"] == 0  # Default value
        assert result["run_count"] == 1
        assert len(result["comparables"]) == 1

        # Verify the comparable has default values for missing fields
        comp = result["comparables"][0]
        assert comp["id"] == "comp1"
        assert comp["formattedAddress"] == "123 Main St"
        assert comp["city"] == ""  # Default value
        assert comp["state"] == ""  # Default value
        assert comp["bedrooms"] == 3
        assert comp["price"] == 245000
        assert comp["bathrooms"] == 0  # Default value
        assert comp["squareFootage"] == 0  # Default value

    def test_map_property_comps_empty_input(self):
        """Test map_property_comps with empty input."""
        # Call the method with empty dict
        result = RentcastApiMapper.map_property_comps({})

        # Verify the result is None for empty dict (same as None input)
        assert result is None

    def test_map_property_comps_none_input(self):
        """Test map_property_comps with None input."""
        # Call the method with None
        result = RentcastApiMapper.map_property_comps(None)

        # Verify the result
        assert result is None

    def test_map_rental_comps_valid_input(self):
        """Test map_rental_comps with valid input."""
        # Create a sample API response
        api_response = {
            "rent": 1500,
            "rentRangeLow": 1400,
            "rentRangeHigh": 1600,
            "confidenceScore": 85,
            "comparables": [
                {
                    "id": "rent1",
                    "address": "123 Main St",
                    "rent": 1450,
                    "bedrooms": 3,
                    "bathrooms": 2
                },
                {
                    "id": "rent2",
                    "address": "456 Oak Ave",
                    "rent": 1550,
                    "bedrooms": 3,
                    "bathrooms": 2
                }
            ]
        }

        # Call the method
        result = RentcastApiMapper.map_rental_comps(api_response)

        # Verify the result
        assert result is not None
        assert "last_run" in result
        assert result["estimated_rent"] == 1500
        assert result["rent_range_low"] == 1400
        assert result["rent_range_high"] == 1600
        assert result["confidence_score"] == 85
        assert len(result["comparable_rentals"]) == 2

        # Verify the comparables are passed through as-is
        assert result["comparable_rentals"] == api_response["comparables"]

    def test_map_rental_comps_missing_fields(self):
        """Test map_rental_comps with missing fields."""
        # Create a sample API response with missing fields
        api_response = {
            "rent": 1500,
            # Missing rentRangeLow and rentRangeHigh
            "comparables": [
                {
                    "id": "rent1",
                    "address": "123 Main St",
                    "rent": 1450
                }
            ]
        }

        # Call the method
        result = RentcastApiMapper.map_rental_comps(api_response)

        # Verify the result
        assert result is not None
        assert "last_run" in result
        assert result["estimated_rent"] == 1500
        assert result["rent_range_low"] == 0  # Default value
        assert result["rent_range_high"] == 0  # Default value
        assert result["confidence_score"] == 0  # Default value
        assert len(result["comparable_rentals"]) == 1

    def test_map_rental_comps_empty_input(self):
        """Test map_rental_comps with empty input."""
        # Call the method with empty dict
        result = RentcastApiMapper.map_rental_comps({})

        # Verify the result is None for empty dict (same as None input)
        assert result is None

    def test_map_rental_comps_none_input(self):
        """Test map_rental_comps with None input."""
        # Call the method with None
        result = RentcastApiMapper.map_rental_comps(None)

        # Verify the result
        assert result is None


class TestApiMapperFactory:
    """Test suite for the ApiMapperFactory class."""

    def test_get_mapper_valid_api(self):
        """Test get_mapper with valid API name."""
        # Test with lowercase
        mapper = ApiMapperFactory.get_mapper("rentcast")
        assert mapper == RentcastApiMapper

        # Test with mixed case
        mapper = ApiMapperFactory.get_mapper("RentCast")
        assert mapper == RentcastApiMapper

        # Test with uppercase
        mapper = ApiMapperFactory.get_mapper("RENTCAST")
        assert mapper == RentcastApiMapper

    def test_get_mapper_invalid_api(self):
        """Test get_mapper with invalid API name."""
        # Test with non-existent API
        with pytest.raises(ValueError) as excinfo:
            ApiMapperFactory.get_mapper("nonexistent_api")
        assert "No mapper available for API: nonexistent_api" in str(excinfo.value)

        # Test with empty string
        with pytest.raises(ValueError) as excinfo:
            ApiMapperFactory.get_mapper("")
        assert "No mapper available for API: " in str(excinfo.value)

    def test_get_mapper_none_input(self):
        """Test get_mapper with None input."""
        # This would raise an AttributeError when trying to call .lower() on None
        with pytest.raises(AttributeError):
            ApiMapperFactory.get_mapper(None)
