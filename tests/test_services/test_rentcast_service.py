"""
Test module for the RentcastService.

This module contains tests for the RentcastService class.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json

from src.services.rentcast_service import RentcastService


class TestRentcastService:
    """Test class for RentcastService."""
    
    @pytest.fixture
    def service(self):
        """Create a RentcastService instance for testing."""
        with patch('src.services.rentcast_service.current_config') as mock_config:
            mock_config.RENTCAST_API_KEY = 'test_api_key'
            service = RentcastService()
            return service
    
    @pytest.fixture
    def mock_response(self):
        """Create a mock response for API calls."""
        mock = MagicMock()
        mock.json.return_value = {}
        mock.raise_for_status.return_value = None
        return mock
    
    def test_init(self, service):
        """Test RentcastService initialization."""
        assert service.api_key == 'test_api_key'
        assert service.base_url == 'https://api.rentcast.io/v1'
    
    @patch('src.services.rentcast_service.requests.get')
    def test_get_rental_estimate(self, mock_get, service, mock_response):
        """Test get_rental_estimate method."""
        # Setup mock response
        mock_response.json.return_value = {
            'rent': 1500,
            'rentRangeLow': 1400,
            'rentRangeHigh': 1600
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = service.get_rental_estimate(
            address='123 Main St',
            bedrooms=3,
            bathrooms=2,
            square_feet=1500
        )
        
        # Verify result
        assert result == mock_response.json.return_value
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['headers']['X-Api-Key'] == 'test_api_key'
        assert kwargs['params']['address'] == '123 Main St'
        assert kwargs['params']['bedrooms'] == 3
        assert kwargs['params']['bathrooms'] == 2
        assert kwargs['params']['squareFootage'] == 1500
    
    @patch('src.services.rentcast_service.requests.get')
    def test_get_property_comparables(self, mock_get, service, mock_response):
        """Test get_property_comparables method."""
        # Setup mock response
        mock_response.json.return_value = {
            'comparables': [
                {
                    'id': '1',
                    'formattedAddress': '123 Main St',
                    'price': 300000
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = service.get_property_comparables(
            address='123 Main St',
            bedrooms=3,
            bathrooms=2,
            square_feet=1500,
            radius_miles=1.0,
            limit=10
        )
        
        # Verify result
        assert result == mock_response.json.return_value
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['headers']['X-Api-Key'] == 'test_api_key'
        assert kwargs['params']['address'] == '123 Main St'
        assert kwargs['params']['radius'] == 1.0
        assert kwargs['params']['limit'] == 10
    
    @patch('src.services.rentcast_service.requests.get')
    def test_get_property_value_estimate(self, mock_get, service, mock_response):
        """Test get_property_value_estimate method."""
        # Setup mock response
        mock_response.json.return_value = {
            'value': 300000,
            'valueLow': 280000,
            'valueHigh': 320000
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = service.get_property_value_estimate(
            address='123 Main St',
            bedrooms=3,
            bathrooms=2,
            square_feet=1500,
            year_built=2000
        )
        
        # Verify result
        assert result == mock_response.json.return_value
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['headers']['X-Api-Key'] == 'test_api_key'
        assert kwargs['params']['address'] == '123 Main St'
        assert kwargs['params']['yearBuilt'] == 2000
    
    @patch('src.services.rentcast_service.requests.get')
    def test_get_market_statistics(self, mock_get, service, mock_response):
        """Test get_market_statistics method."""
        # Setup mock response
        mock_response.json.return_value = {
            'averageRent': 1500,
            'averagePrice': 300000,
            'averageDaysOnMarket': 30
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = service.get_market_statistics(
            city='San Francisco',
            state='CA'
        )
        
        # Verify result
        assert result == mock_response.json.return_value
        
        # Verify API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['headers']['X-Api-Key'] == 'test_api_key'
        assert kwargs['params']['city'] == 'San Francisco'
        assert kwargs['params']['state'] == 'CA'
    
    def test_calculate_correlation_score(self, service):
        """Test calculate_correlation_score method."""
        # Test case 1: Perfect match
        subject_property = {
            'bedrooms': 3,
            'bathrooms': 2,
            'squareFootage': 1500,
            'yearBuilt': 2000
        }
        comparable = {
            'bedrooms': 3,
            'bathrooms': 2,
            'squareFootage': 1500,
            'yearBuilt': 2000,
            'distance': 0
        }
        score = service.calculate_correlation_score(subject_property, comparable)
        assert score == 100.0
        
        # Test case 2: Different bedrooms
        comparable['bedrooms'] = 4
        score = service.calculate_correlation_score(subject_property, comparable)
        assert score < 100.0
        assert score > 80.0  # Should still be high
        
        # Test case 3: Different bathrooms
        comparable['bedrooms'] = 3
        comparable['bathrooms'] = 3
        score = service.calculate_correlation_score(subject_property, comparable)
        assert score < 100.0
        assert score > 80.0  # Should still be high
        
        # Test case 4: Different square footage
        comparable['bathrooms'] = 2
        comparable['squareFootage'] = 2000
        score = service.calculate_correlation_score(subject_property, comparable)
        assert score < 100.0
        assert score > 80.0  # Should still be high
        
        # Test case 5: Different year built
        comparable['squareFootage'] = 1500
        comparable['yearBuilt'] = 1980
        score = service.calculate_correlation_score(subject_property, comparable)
        assert score < 100.0
        assert score > 80.0  # Should still be high
        
        # Test case 6: Different distance
        comparable['yearBuilt'] = 2000
        comparable['distance'] = 1.5
        score = service.calculate_correlation_score(subject_property, comparable)
        assert score < 100.0
        assert score > 70.0  # Should still be fairly high
        
        # Test case 7: Very different property
        comparable = {
            'bedrooms': 5,
            'bathrooms': 4,
            'squareFootage': 3000,
            'yearBuilt': 1950,
            'distance': 2.0
        }
        score = service.calculate_correlation_score(subject_property, comparable)
        assert score < 70.0  # Should be lower
    
    def test_format_comparables_for_analysis_empty(self, service):
        """Test format_comparables_for_analysis method with empty data."""
        # Test with empty data
        result = service.format_comparables_for_analysis({})
        
        # Verify result structure
        assert 'last_run' in result
        assert result['run_count'] == 1
        assert result['estimated_value'] == 0
        assert result['value_range_low'] == 0
        assert result['value_range_high'] == 0
        assert result['comparables'] == []
    
    def test_format_comparables_for_analysis(self, service):
        """Test format_comparables_for_analysis method with sample data."""
        # Create sample data
        comparables_data = {
            'bedrooms': 3,
            'bathrooms': 2,
            'squareFootage': 1500,
            'yearBuilt': 2000,
            'comparables': [
                {
                    'id': '1',
                    'formattedAddress': '123 Main St',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'zipCode': '94105',
                    'propertyType': 'Single Family',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'squareFootage': 1500,
                    'yearBuilt': 2000,
                    'price': 300000,
                    'listingType': 'SOLD',
                    'listedDate': '2023-01-01',
                    'removedDate': '2023-02-01',
                    'daysOnMarket': 30,
                    'distance': 0.5
                },
                {
                    'id': '2',
                    'formattedAddress': '456 Oak St',
                    'city': 'San Francisco',
                    'state': 'CA',
                    'zipCode': '94105',
                    'propertyType': 'Single Family',
                    'bedrooms': 4,
                    'bathrooms': 2.5,
                    'squareFootage': 1800,
                    'yearBuilt': 1995,
                    'price': 350000,
                    'listingType': 'SOLD',
                    'listedDate': '2023-01-15',
                    'removedDate': '2023-02-15',
                    'daysOnMarket': 30,
                    'distance': 1.0
                }
            ]
        }
        
        # Call method
        result = service.format_comparables_for_analysis(comparables_data)
        
        # Verify result structure
        assert 'last_run' in result
        assert result['run_count'] == 1
        assert result['estimated_value'] > 0
        assert result['value_range_low'] > 0
        assert result['value_range_high'] > 0
        assert len(result['comparables']) == 2
        
        # Verify comparables are sorted by correlation score
        assert result['comparables'][0]['correlation'] >= result['comparables'][1]['correlation']
        
        # Verify correlation scores are calculated
        assert result['comparables'][0]['correlation'] > 0
        assert result['comparables'][1]['correlation'] > 0
        
        # Verify average correlation is calculated
        assert 'average_correlation' in result
        assert result['average_correlation'] > 0
