import pytest
import json
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime
import requests
from utils.comps_handler import (
    format_address,
    fetch_property_comps,
    fetch_rental_comps,
    calculate_mao_from_analysis,
    calculate_monthly_holding_costs,
    update_analysis_comps,
    RentcastAPIError
)


class TestFormatAddress:
    """Test suite for the format_address function."""

    def test_format_address_with_street_types(self):
        """Test format_address with various street types."""
        # Test with full street types - note that the function returns abbreviations in uppercase
        assert format_address("123 Main Street, Anytown, CA 12345") == "123 Main ST, Anytown, CA 12345"
        assert format_address("456 Oak Avenue, Somecity, NY 67890") == "456 Oak AVE, Somecity, NY 67890"
        assert format_address("789 Pine Boulevard, Othercity, TX 54321") == "789 Pine BLVD, Othercity, TX 54321"
        assert format_address("101 Cedar Drive, Anothercity, FL 98765") == "101 Cedar DR, Anothercity, FL 98765"
        assert format_address("202 Maple Lane, Smalltown, WA 13579") == "202 Maple LN, Smalltown, WA 13579"
        assert format_address("303 Elm Road, Bigcity, IL 24680") == "303 Elm RD, Bigcity, IL 24680"
        assert format_address("404 Birch Court, Mediumcity, OH 97531") == "404 Birch CT, Mediumcity, OH 97531"
        assert format_address("505 Willow Circle, Tinycity, GA 86420") == "505 Willow CIR, Tinycity, GA 86420"
        assert format_address("606 Spruce Way, Largetown, MI 75319") == "606 Spruce WAY, Largetown, MI 75319"
        assert format_address("707 Fir Trail, Villagetown, PA 95173") == "707 Fir TRL, Villagetown, PA 95173"
        assert format_address("808 Pine Terrace, Hamletcity, AZ 15937") == "808 Pine TER, Hamletcity, AZ 15937"
        assert format_address("909 Oak Square, Townsville, NM 35791") == "909 Oak SQ, Townsville, NM 35791"

    def test_format_address_with_plural_street_types(self):
        """Test format_address with plural street types."""
        assert format_address("123 Main Streets, Anytown, CA 12345") == "123 Main ST, Anytown, CA 12345"
        assert format_address("456 Oak Avenues, Somecity, NY 67890") == "456 Oak AVE, Somecity, NY 67890"

    def test_format_address_with_missing_components(self):
        """Test format_address with missing address components."""
        # Missing zip code
        assert format_address("123 Main St, Anytown, CA") == "123 Main ST, Anytown, CA"
        # Missing state and zip
        assert format_address("123 Main St, Anytown") == "123 Main ST, Anytown"
        # Just street
        assert format_address("123 Main St") == "123 Main ST, "

    def test_format_address_with_united_states(self):
        """Test format_address with 'United States' in the address."""
        assert format_address("123 Main St, Anytown, CA 12345, United States") == "123 Main ST, Anytown, CA 12345"
        assert format_address("123 Main St, Anytown, CA, United States") == "123 Main ST, Anytown, CA"

    def test_format_address_with_extra_spaces_and_commas(self):
        """Test format_address with extra spaces and commas."""
        assert format_address("123  Main  St,  Anytown,  CA  12345") == "123 Main ST, Anytown, CA 12345"
        assert format_address("123 Main St,,  Anytown,, CA, 12345") == "123 Main ST, Anytown"

    def test_format_address_with_exception(self):
        """Test format_address with an exception during processing."""
        # Since we can't easily patch string methods, we'll test the exception handling
        # by creating a scenario that will cause an exception in the function
        
        # We'll use a mock to verify the logger is called
        with patch('utils.comps_handler.logger') as mock_logger:
            # Create a mock for the parts list that will raise an exception when accessed
            with patch('builtins.str.strip', side_effect=Exception("Test exception")):
                # This should not raise an exception due to try/except in format_address
                result = format_address("123 Main St")
                
                # The original address should be returned on error
                assert result == "123 Main St"
                
                # Verify error was logged
                assert mock_logger.error.called
                assert "Error formatting address" in str(mock_logger.error.call_args)
    
    def test_format_address_with_empty_parts(self):
        """Test format_address with empty address parts."""
        # Test with just a comma
        result = format_address(",")
        assert result == ", "
        
        # Test with multiple commas
        result = format_address(",,")
        assert result == ", "


@pytest.fixture
def mock_app_config():
    """Fixture for mocked app configuration."""
    return {
        'RENTCAST_API_BASE_URL': 'https://api.rentcast.io/v1',
        'RENTCAST_API_KEY': 'test_api_key',
        'RENTCAST_COMP_DEFAULTS': {
            'maxRadius': 1.0,
            'daysOld': 180,
            'compCount': 5
        },
        'MAX_COMP_RUNS_PER_SESSION': 3
    }


@pytest.fixture
def mock_session():
    """Fixture for mocked Flask session."""
    # Create a direct mock instead of patching the Flask session
    mock_session = MagicMock()
    mock_session.get.return_value = 0  # Default run count
    
    # Patch the session import in comps_handler
    with patch('utils.comps_handler.session', mock_session):
        yield mock_session


@pytest.fixture
def mock_requests_get():
    """Fixture for mocked requests.get."""
    with patch('utils.comps_handler.requests.get') as mock_get:
        # Create a mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'price': 250000,
            'priceRangeLow': 230000,
            'priceRangeHigh': 270000,
            'comparables': [
                {
                    'id': 'comp1',
                    'price': 245000,
                    'removedDate': '2023-01-15'
                },
                {
                    'id': 'comp2',
                    'price': 265000,
                    'removedDate': '2023-01-10'
                }
            ]
        }
        mock_get.return_value = mock_response
        yield mock_get


class TestFetchPropertyComps:
    """Test suite for the fetch_property_comps function."""

    def test_fetch_property_comps_success(self, mock_app_config, mock_session, mock_requests_get):
        """Test fetch_property_comps with successful API call."""
        with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
            with patch('utils.comps_handler.ApiMapperFactory.get_mapper') as mock_get_mapper:
                # Mock the mapper
                mock_mapper = MagicMock()
                mock_mapper.map_property_comps.return_value = {
                    'last_run': datetime.utcnow().isoformat(),
                    'run_count': 1,
                    'estimated_value': 250000,
                    'value_range_low': 230000,
                    'value_range_high': 270000,
                    'comparables': [
                        {'id': 'comp1', 'price': 245000, 'saleDate': '2023-01-15'},
                        {'id': 'comp2', 'price': 265000, 'saleDate': '2023-01-10'}
                    ]
                }
                mock_get_mapper.return_value = mock_mapper

                # Call the function
                result = fetch_property_comps(
                    mock_app_config,
                    "123 Main St, Anytown, CA 12345",
                    "single_family",
                    3,
                    2,
                    1500
                )

                # Verify the result
                assert result is not None
                assert 'estimated_value' in result
                assert result['estimated_value'] == 250000
                assert len(result['comparables']) == 2

                # Verify the API call
                mock_requests_get.assert_called_once()
                args, kwargs = mock_requests_get.call_args
                assert args[0] == 'https://api.rentcast.io/v1/avm/value'
                assert kwargs['params']['address'] == '123 Main St, Anytown, CA 12345'
                assert kwargs['params']['propertyType'] == 'single_family'
                assert kwargs['params']['bedrooms'] == 3
                assert kwargs['params']['bathrooms'] == 2
                assert kwargs['params']['squareFootage'] == 1500
                assert kwargs['headers']['X-Api-Key'] == 'test_api_key'

                # Verify session update
                mock_session.__setitem__.assert_called_once()

    def test_fetch_property_comps_with_mao_calculation(self, mock_app_config, mock_session, mock_requests_get):
        """Test fetch_property_comps with MAO calculation."""
        with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
            with patch('utils.comps_handler.ApiMapperFactory.get_mapper') as mock_get_mapper:
                # Mock the mapper
                mock_mapper = MagicMock()
                mock_mapper.map_property_comps.return_value = {
                    'last_run': datetime.utcnow().isoformat(),
                    'run_count': 1,
                    'estimated_value': 250000,
                    'value_range_low': 230000,
                    'value_range_high': 270000,
                    'comparables': []
                }
                mock_get_mapper.return_value = mock_mapper

                # Mock calculate_mao
                with patch('utils.comps_handler.calculate_mao') as mock_calculate_mao:
                    mock_calculate_mao.return_value = {
                        'value': 175000,
                        'arv': 250000,
                        'ltv_percentage': 75.0,
                        'renovation_costs': 30000,
                        'closing_costs': 5000,
                        'monthly_holding_costs': 1000,
                        'total_holding_costs': 3000,
                        'holding_months': 3,
                        'max_cash_left': 10000
                    }

                    # Mock the import of get_user_mao_defaults inside the function
                    # We need to patch the function at the point where it's imported
                    with patch('services.user_service.get_user_mao_defaults') as mock_get_defaults:
                        mock_get_defaults.return_value = {
                            'arv_discount': 0,
                            'repair_cost_per_sf': 20,
                            'closing_costs_percentage': 2,
                            'holding_costs_monthly': 1000,
                            'max_cash_left': 10000
                        }

                        # Call the function with analysis data
                        analysis_data = {
                            'user_id': 123,
                            'analysis_type': 'BRRRR',
                            'renovation_costs': 30000,
                            'renovation_duration': 3,
                            'closing_costs': 5000,
                            'refinance_ltv_percentage': 75.0
                        }

                        result = fetch_property_comps(
                            mock_app_config,
                            "123 Main St, Anytown, CA 12345",
                            "single_family",
                            3,
                            2,
                            1500,
                            analysis_data
                        )

                        # Verify the result includes MAO
                        assert result is not None
                        assert 'mao' in result
                        assert result['mao']['value'] == 175000

                        # Verify calculate_mao was called
                        mock_calculate_mao.assert_called_once()
                        args, kwargs = mock_calculate_mao.call_args
                        assert args[0] == 250000  # ARV
                        assert args[1] == analysis_data
    
    def test_fetch_property_comps_mao_calculation_error(self, mock_app_config, mock_session, mock_requests_get):
        """Test fetch_property_comps with error during MAO calculation."""
        with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
            with patch('utils.comps_handler.ApiMapperFactory.get_mapper') as mock_get_mapper:
                # Mock the mapper
                mock_mapper = MagicMock()
                mock_mapper.map_property_comps.return_value = {
                    'last_run': datetime.utcnow().isoformat(),
                    'run_count': 1,
                    'estimated_value': 250000,
                    'value_range_low': 230000,
                    'value_range_high': 270000,
                    'comparables': []
                }
                mock_get_mapper.return_value = mock_mapper

                # Mock calculate_mao to raise an exception
                with patch('utils.comps_handler.calculate_mao', side_effect=Exception("MAO calculation error")):
                    with patch('utils.comps_handler.logger') as mock_logger:
                        # Call the function with analysis data
                        analysis_data = {
                            'user_id': 123,
                            'analysis_type': 'BRRRR',
                            'renovation_costs': 30000,
                            'renovation_duration': 3,
                            'closing_costs': 5000,
                            'refinance_ltv_percentage': 75.0
                        }

                        # This should not raise an exception
                        result = fetch_property_comps(
                            mock_app_config,
                            "123 Main St, Anytown, CA 12345",
                            "single_family",
                            3,
                            2,
                            1500,
                            analysis_data
                        )

                        # Verify the result does not include MAO
                        assert result is not None
                        assert 'mao' not in result
                        
                        # Verify error was logged
                        mock_logger.error.assert_called_once()
                        assert "Error calculating MAO" in mock_logger.error.call_args[0][0]

    def test_fetch_property_comps_missing_config(self, mock_app_config, mock_session):
        """Test fetch_property_comps with missing configuration."""
        # Test missing API base URL
        invalid_config = mock_app_config.copy()
        invalid_config['RENTCAST_API_BASE_URL'] = None

        with pytest.raises(RentcastAPIError) as excinfo:
            fetch_property_comps(
                invalid_config,
                "123 Main St, Anytown, CA 12345",
                "single_family",
                3,
                2,
                1500
            )
        assert "RENTCAST_API_BASE_URL missing" in str(excinfo.value)

        # Test missing API key
        invalid_config = mock_app_config.copy()
        invalid_config['RENTCAST_API_KEY'] = None

        with pytest.raises(RentcastAPIError) as excinfo:
            fetch_property_comps(
                invalid_config,
                "123 Main St, Anytown, CA 12345",
                "single_family",
                3,
                2,
                1500
            )
        assert "RENTCAST_API_KEY missing" in str(excinfo.value)

        # Test missing comp defaults
        invalid_config = mock_app_config.copy()
        invalid_config['RENTCAST_COMP_DEFAULTS'] = None

        with pytest.raises(RentcastAPIError) as excinfo:
            fetch_property_comps(
                invalid_config,
                "123 Main St, Anytown, CA 12345",
                "single_family",
                3,
                2,
                1500
            )
        assert "RENTCAST_COMP_DEFAULTS missing" in str(excinfo.value)

    def test_fetch_property_comps_max_runs_exceeded(self, mock_app_config, mock_session):
        """Test fetch_property_comps with maximum runs exceeded."""
        # Set run count to max
        mock_session.get.return_value = 3  # Max runs is 3

        with pytest.raises(RentcastAPIError) as excinfo:
            fetch_property_comps(
                mock_app_config,
                "123 Main St, Anytown, CA 12345",
                "single_family",
                3,
                2,
                1500
            )
        assert "Maximum comp runs" in str(excinfo.value)

    def test_fetch_property_comps_api_error(self, mock_app_config, mock_session):
        """Test fetch_property_comps with API error."""
        with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
            with patch('utils.comps_handler.requests.get') as mock_get:
                # Mock a failed API call
                mock_get.side_effect = requests.exceptions.RequestException("API error")

                with pytest.raises(RentcastAPIError) as excinfo:
                    fetch_property_comps(
                        mock_app_config,
                        "123 Main St, Anytown, CA 12345",
                        "single_family",
                        3,
                        2,
                        1500
                    )
                assert "Failed to fetch property comps" in str(excinfo.value)

    def test_fetch_property_comps_missing_fields(self, mock_app_config, mock_session, mock_requests_get):
        """Test fetch_property_comps with missing fields in API response."""
        with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
            # Mock a response with missing fields
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                # Missing price, priceRangeLow, priceRangeHigh
                'comparables': [
                    {'id': 'comp1', 'price': 245000, 'removedDate': '2023-01-15'}
                ]
            }
            mock_requests_get.return_value = mock_response

            with patch('utils.comps_handler.ApiMapperFactory.get_mapper') as mock_get_mapper:
                # Mock the mapper
                mock_mapper = MagicMock()
                mock_mapper.map_property_comps.return_value = {
                    'last_run': datetime.utcnow().isoformat(),
                    'run_count': 1,
                    'estimated_value': 0,  # Default value
                    'value_range_low': 0,  # Default value
                    'value_range_high': 0,  # Default value
                    'comparables': [
                        {'id': 'comp1', 'price': 245000, 'saleDate': '2023-01-15'}
                    ]
                }
                mock_get_mapper.return_value = mock_mapper

                # Call the function
                result = fetch_property_comps(
                    mock_app_config,
                    "123 Main St, Anytown, CA 12345",
                    "single_family",
                    3,
                    2,
                    1500
                )

                # Verify the result
                assert result is not None
                assert result['estimated_value'] == 0  # Default value
                assert result['value_range_low'] == 0  # Default value
                assert result['value_range_high'] == 0  # Default value
                assert len(result['comparables']) == 1


class TestFetchRentalComps:
    """Test suite for the fetch_rental_comps function."""

    def test_fetch_rental_comps_success(self, mock_app_config, mock_requests_get):
        """Test fetch_rental_comps with successful API call."""
        # Mock the rental API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'rent': 1500,
            'rentRangeLow': 1400,
            'rentRangeHigh': 1600,
            'confidenceScore': 85,
            'comparables': [
                {'id': 'rent1', 'price': 1450},
                {'id': 'rent2', 'price': 1550}
            ]
        }
        mock_requests_get.return_value = mock_response

        with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
            with patch('utils.comps_handler.ApiMapperFactory.get_mapper') as mock_get_mapper:
                # Mock the mapper
                mock_mapper = MagicMock()
                mock_mapper.map_rental_comps.return_value = {
                    'last_run': datetime.utcnow().isoformat(),
                    'estimated_rent': 1500,
                    'rent_range_low': 1400,
                    'rent_range_high': 1600,
                    'confidence_score': 85,
                    'comparable_rentals': [
                        {'id': 'rent1', 'price': 1450},
                        {'id': 'rent2', 'price': 1550}
                    ]
                }
                mock_get_mapper.return_value = mock_mapper

                # Call the function
                result = fetch_rental_comps(
                    mock_app_config,
                    "123 Main St, Anytown, CA 12345",
                    3,
                    2,
                    1500
                )

                # Verify the result
                assert result is not None
                assert 'estimated_rent' in result
                assert result['estimated_rent'] == 1500
                assert len(result['comparable_rentals']) == 2

                # Verify the API call
                mock_requests_get.assert_called_once()
                args, kwargs = mock_requests_get.call_args
                assert args[0] == 'https://api.rentcast.io/v1/avm/rent/long-term'
                assert kwargs['params']['address'] == '123 Main St, Anytown, CA 12345'
                assert kwargs['params']['propertyType'] == 'single_family'
                assert kwargs['params']['bedrooms'] == 3
                assert kwargs['params']['bathrooms'] == 2
                assert kwargs['params']['squareFootage'] == 1500
                assert kwargs['headers']['X-Api-Key'] == 'test_api_key'
    
    def test_fetch_rental_comps_with_filtering(self, mock_app_config):
        """Test fetch_rental_comps with filtering of comparables."""
        # Mock the rental API response with some invalid rentals
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'rent': 1500,
            'rentRangeLow': 1400,
            'rentRangeHigh': 1600,
            'confidenceScore': 85,
            'comparables': [
                {'id': 'rent1', 'price': 1450},  # Valid
                {'id': 'rent2', 'price': 0},     # Invalid - zero price
                {'id': 'rent3', 'price': 1550}   # Valid
            ]
        }
        
        with patch('utils.comps_handler.requests.get', return_value=mock_response):
            with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
                with patch('utils.comps_handler.ApiMapperFactory.get_mapper') as mock_get_mapper:
                    # Mock the mapper to pass through the filtered comparables
                    mock_mapper = MagicMock()
                    mock_mapper.map_rental_comps.side_effect = lambda x: {
                        'last_run': datetime.utcnow().isoformat(),
                        'estimated_rent': x.get('rent', 0),
                        'rent_range_low': x.get('rentRangeLow', 0),
                        'rent_range_high': x.get('rentRangeHigh', 0),
                        'confidence_score': x.get('confidenceScore', 0),
                        'comparable_rentals': x.get('comparables', [])
                    }
                    mock_get_mapper.return_value = mock_mapper

                    # Call the function
                    result = fetch_rental_comps(
                        mock_app_config,
                        "123 Main St, Anytown, CA 12345",
                        3,
                        2,
                        1500
                    )

                    # Verify the result has filtered comparables
                    assert result is not None
                    assert len(result['comparable_rentals']) == 2  # Only the valid ones
                    # Verify the invalid rental was filtered out
                    prices = [comp.get('price') for comp in result['comparable_rentals']]
                    assert 0 not in prices

    def test_fetch_rental_comps_missing_config(self, mock_app_config):
        """Test fetch_rental_comps with missing configuration."""
        # Test missing API base URL
        invalid_config = mock_app_config.copy()
        invalid_config['RENTCAST_API_BASE_URL'] = None

        with pytest.raises(RentcastAPIError) as excinfo:
            fetch_rental_comps(
                invalid_config,
                "123 Main St, Anytown, CA 12345",
                3,
                2,
                1500
            )
        assert "RENTCAST_API_BASE_URL missing" in str(excinfo.value)

    def test_fetch_rental_comps_api_error(self, mock_app_config):
        """Test fetch_rental_comps with API error."""
        with patch('utils.comps_handler.format_address', return_value='123 Main St, Anytown, CA 12345'):
            with patch('utils.comps_handler.requests.get') as mock_get:
                # Mock a failed API call
                mock_get.side_effect = requests.exceptions.RequestException("API error")

                with pytest.raises(RentcastAPIError) as excinfo:
                    fetch_rental_comps(
                        mock_app_config,
                        "123 Main St, Anytown, CA 12345",
                        3,
                        2,
                        1500
                    )
                assert "Failed to fetch rental comps" in str(excinfo.value)


class TestCalculateMaoFromAnalysis:
    """Test suite for the calculate_mao_from_analysis function."""

    def test_calculate_mao_basic(self):
        """Test calculate_mao_from_analysis with basic inputs."""
        analysis_data = {
            'renovation_costs': 30000,
            'renovation_duration': 3,
            'closing_costs': 5000,
            'property_taxes': 2000,
            'insurance': 1000,
            'utilities': 500,
            'hoa_coa_coop': 0
        }
        arv = 250000

        with patch('utils.comps_handler.calculate_monthly_holding_costs', return_value=1000):
            result = calculate_mao_from_analysis(arv, analysis_data)

            assert result is not None
            assert 'value' in result
            # Expected calculation: 
            # loan_amount (187500) - renovation_costs (30000) - closing_costs (5000) - total_holding_costs (3000) + max_cash_left (10000)
            # = 159500
            assert result['value'] == 159500
            assert result['arv'] == 250000
            assert result['ltv_percentage'] == 75.0
            assert result['renovation_costs'] == 30000
            assert result['closing_costs'] == 5000
            assert result['monthly_holding_costs'] == 1000
            assert result['total_holding_costs'] == 3000
            assert result['holding_months'] == 3
            assert result['max_cash_left'] == 10000

    def test_calculate_mao_brrrr(self):
        """Test calculate_mao_from_analysis with BRRRR analysis type."""
        analysis_data = {
            'analysis_type': 'BRRRR',
            'renovation_costs': 30000,
            'renovation_duration': 3,
            'closing_costs': 5000,
            'refinance_ltv_percentage': 70.0,
            'property_taxes': 2000,
            'insurance': 1000,
            'utilities': 500,
            'hoa_coa_coop': 0,
            'initial_loan_amount': 150000,
            'initial_loan_interest_rate': 12.0
        }
        arv = 250000

        with patch('utils.comps_handler.calculate_monthly_holding_costs', return_value=2500):
            result = calculate_mao_from_analysis(arv, analysis_data)

            assert result is not None
            assert 'value' in result
            # Expected calculation: 
            # loan_amount (175000) - renovation_costs (30000) - closing_costs (5000) - total_holding_costs (7500) + max_cash_left (10000)
            # = 142500
            assert result['value'] == 142500
            assert result['arv'] == 250000
            assert result['ltv_percentage'] == 70.0  # Using refinance LTV
            assert result['renovation_costs'] == 30000
            assert result['closing_costs'] == 5000
            assert result['monthly_holding_costs'] == 2500
            assert result['total_holding_costs'] == 7500
            assert result['holding_months'] == 3
            assert result['max_cash_left'] == 10000

    def test_calculate_mao_balloon(self):
        """Test calculate_mao_from_analysis with balloon payment."""
        analysis_data = {
            'analysis_type': 'LTR',
            'has_balloon_payment': True,
            'balloon_refinance_ltv_percentage': 65.0,
            'renovation_costs': 30000,
            'renovation_duration': 3,
            'closing_costs': 5000,
            'property_taxes': 2000,
            'insurance': 1000,
            'utilities': 500,
            'hoa_coa_coop': 0,
            'loan1_loan_amount': 150000,
            'loan1_loan_interest_rate': 8.0
        }
        arv = 250000

        with patch('utils.comps_handler.calculate_monthly_holding_costs', return_value=2000):
            result = calculate_mao_from_analysis(arv, analysis_data)

            assert result is not None
            assert 'value' in result
            # Expected calculation: 
            # loan_amount (162500) - renovation_costs (30000) - closing_costs (5000) - total_holding_costs (6000) + max_cash_left (10000)
            # = 131500
            assert result['value'] == 131500
            assert result['arv'] == 250000
            assert result['ltv_percentage'] == 65.0  # Using balloon refinance LTV
            assert result['renovation_costs'] == 30000
            assert result['closing_costs'] == 5000
            assert result['monthly_holding_costs'] == 2000
            assert result['total_holding_costs'] == 6000
            assert result['holding_months'] == 3
            assert result['max_cash_left'] == 10000

    def test_calculate_mao_error_handling(self):
        """Test calculate_mao_from_analysis error handling."""
        analysis_data = {
            'renovation_costs': 'invalid',  # Invalid value
            'renovation_duration': 3,
            'closing_costs': 5000
        }
        arv = 250000

        with patch('utils.comps_handler.logger') as mock_logger:
            result = calculate_mao_from_analysis(arv, analysis_data)

            assert result is not None
            assert 'value' in result
            assert result['value'] == 0  # Default value on error
            assert 'error' in result
            mock_logger.error.assert_called_once()


class TestCalculateMonthlyHoldingCosts:
    """Test suite for the calculate_monthly_holding_costs function."""

    def test_calculate_monthly_holding_costs_basic(self):
        """Test calculate_monthly_holding_costs with basic inputs."""
        analysis_data = {
            'property_taxes': 2000,
            'insurance': 1000,
            'utilities': 500,
            'hoa_coa_coop': 200
        }

        result = calculate_monthly_holding_costs(analysis_data)
        assert result == 3700  # Sum of all costs

    def test_calculate_monthly_holding_costs_with_brrrr_loan(self):
        """Test calculate_monthly_holding_costs with BRRRR loan."""
        analysis_data = {
            'analysis_type': 'BRRRR',
            'property_taxes': 2000,
            'insurance': 1000,
            'utilities': 500,
            'hoa_coa_coop': 200,
            'initial_loan_amount': 150000,
            'initial_loan_interest_rate': 12.0  # 12% annual rate
        }

        result = calculate_monthly_holding_costs(analysis_data)
        # Monthly interest: 150000 * (12 / 100 / 12) = 1500
        # Total: 2000 + 1000 + 500 + 200 + 1500 = 5200
        assert result == 5200

    def test_calculate_monthly_holding_costs_with_regular_loan(self):
        """Test calculate_monthly_holding_costs with regular loan."""
        analysis_data = {
            'analysis_type': 'LTR',
            'property_taxes': 2000,
            'insurance': 1000,
            'utilities': 500,
            'hoa_coa_coop': 200,
            'loan1_loan_amount': 150000,
            'loan1_loan_interest_rate': 6.0  # 6% annual rate
        }

        result = calculate_monthly_holding_costs(analysis_data)
        # Monthly interest: 150000 * (6 / 100 / 12) = 750
        # Total: 2000 + 1000 + 500 + 200 + 750 = 4450
        assert result == 4450

    def test_calculate_monthly_holding_costs_with_zero_values(self):
        """Test calculate_monthly_holding_costs with zero values."""
        analysis_data = {
            'property_taxes': 0,
            'insurance': 0,
            'utilities': 0,
            'hoa_coa_coop': 0,
            'loan1_loan_amount': 0,
            'loan1_loan_interest_rate': 0
        }

        result = calculate_monthly_holding_costs(analysis_data)
        assert result == 0


class TestUpdateAnalysisComps:
    """Test suite for the update_analysis_comps function."""

    def test_update_analysis_comps_new_comps_data(self):
        """Test update_analysis_comps with new comps data."""
        # Create a sample analysis without comps_data
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR'
        }

        # Create sample comps data
        comps_data = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_value': 250000,
            'value_range_low': 230000,
            'value_range_high': 270000,
            'comparables': [
                {'id': 'comp1', 'price': 245000},
                {'id': 'comp2', 'price': 265000}
            ]
        }

        # Call the function
        result = update_analysis_comps(analysis, comps_data, run_count=2)

        # Verify the result
        assert result is not None
        assert 'comps_data' in result
        assert result['comps_data']['estimated_value'] == 250000
        assert result['comps_data']['value_range_low'] == 230000
        assert result['comps_data']['value_range_high'] == 270000
        assert len(result['comps_data']['comparables']) == 2
        assert result['comps_data']['run_count'] == 2

    def test_update_analysis_comps_existing_comps_data(self):
        """Test update_analysis_comps with existing comps data."""
        # Create a sample analysis with existing comps_data
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR',
            'comps_data': {
                'last_run': '2023-01-01T00:00:00',
                'run_count': 1,
                'estimated_value': 240000,
                'value_range_low': 220000,
                'value_range_high': 260000,
                'comparables': [
                    {'id': 'old_comp1', 'price': 235000}
                ]
            }
        }

        # Create sample new comps data
        comps_data = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_value': 250000,
            'value_range_low': 230000,
            'value_range_high': 270000,
            'comparables': [
                {'id': 'comp1', 'price': 245000},
                {'id': 'comp2', 'price': 265000}
            ]
        }

        # Call the function
        result = update_analysis_comps(analysis, comps_data, run_count=2)

        # Verify the result
        assert result is not None
        assert 'comps_data' in result
        assert result['comps_data']['estimated_value'] == 250000  # Updated value
        assert result['comps_data']['value_range_low'] == 230000  # Updated value
        assert result['comps_data']['value_range_high'] == 270000  # Updated value
        assert len(result['comps_data']['comparables']) == 2  # Updated comparables
        assert result['comps_data']['run_count'] == 2  # Updated run count

    def test_update_analysis_comps_with_mao(self):
        """Test update_analysis_comps with MAO data."""
        # Create a sample analysis
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR'
        }

        # Create sample comps data with MAO
        comps_data = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_value': 250000,
            'value_range_low': 230000,
            'value_range_high': 270000,
            'comparables': [],
            'mao': {
                'value': 175000,
                'arv': 250000,
                'ltv_percentage': 75.0,
                'renovation_costs': 30000,
                'closing_costs': 5000,
                'monthly_holding_costs': 1000,
                'total_holding_costs': 3000,
                'holding_months': 3,
                'max_cash_left': 10000
            }
        }

        # Call the function
        result = update_analysis_comps(analysis, comps_data)

        # Verify the result
        assert result is not None
        assert 'comps_data' in result
        assert 'mao' in result['comps_data']
        assert result['comps_data']['mao']['value'] == 175000

    def test_update_analysis_comps_with_rental_comps(self):
        """Test update_analysis_comps with rental comps data."""
        # Create a sample analysis
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR'
        }

        # Create sample comps data
        comps_data = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_value': 250000,
            'value_range_low': 230000,
            'value_range_high': 270000,
            'comparables': []
        }

        # Create sample rental comps data
        rental_comps = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_rent': 1500,
            'rent_range_low': 1400,
            'rent_range_high': 1600,
            'confidence_score': 85,
            'comparable_rentals': [
                {'id': 'rent1', 'price': 1450},
                {'id': 'rent2', 'price': 1550}
            ]
        }

        # Call the function
        result = update_analysis_comps(analysis, comps_data, rental_comps)

        # Verify the result
        assert result is not None
        assert 'comps_data' in result
        assert 'rental_comps' in result['comps_data']
        assert result['comps_data']['rental_comps']['estimated_rent'] == 1500
        assert 'cap_rate' in result['comps_data']['rental_comps']  # Cap rate should be calculated

    def test_update_analysis_comps_with_none_comps_data(self):
        """Test update_analysis_comps with None comps_data."""
        # Create a sample analysis
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR'
        }

        # Call the function with None comps_data
        result = update_analysis_comps(analysis, None)

        # Verify the result
        assert result is not None
        assert result == analysis  # Should return the original analysis unchanged

    def test_update_analysis_comps_with_missing_keys(self):
        """Test update_analysis_comps with comps_data missing required keys."""
        # Create a sample analysis
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR'
        }

        # Create sample comps data with missing keys
        comps_data = {
            'last_run': datetime.utcnow().isoformat(),
            # Missing estimated_value, value_range_low, value_range_high, comparables
        }

        # Call the function
        with patch('utils.comps_handler.logger') as mock_logger:
            result = update_analysis_comps(analysis, comps_data)

            # Verify the result
            assert result is not None
            assert result == analysis  # Should return the original analysis unchanged
            mock_logger.error.assert_called_once()
            assert "missing required keys" in mock_logger.error.call_args[0][0]

    def test_update_analysis_comps_with_error(self):
        """Test update_analysis_comps with an error during update."""
        # Create a sample analysis
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR',
            'comps_data': {}  # Empty dict
        }

        # Create a custom dict-like object that raises an exception when updated
        class ExplodingCompsData:
            def __getitem__(self, key):
                return None
                
            def get(self, key, default=None):
                return default
                
            def __contains__(self, key):
                return False
        
        # Create sample comps data using our custom object
        comps_data = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_value': 250000,
            'value_range_low': 230000,
            'value_range_high': 270000,
            'comparables': []
        }

        # Mock the logger
        with patch('utils.comps_handler.logger') as mock_logger:
            # Mock the update method to raise an exception
            with patch.dict(analysis['comps_data'], clear=True):
                # Patch the dictionary's update method indirectly
                with patch('utils.comps_handler.update_analysis_comps', side_effect=lambda a, c, r=None, rc=1: 
                    exec('raise Exception("Test exception")') or a):
                    try:
                        # This will raise our exception
                        update_analysis_comps(analysis, comps_data)
                    except Exception:
                        # The exception should be caught in the real implementation
                        pass
                    
                    # Verify error was logged
                    assert mock_logger.error.called
                    assert "Error updating comps_data" in str(mock_logger.error.call_args)
    
    def test_update_analysis_comps_with_cap_rate_calculation(self):
        """Test update_analysis_comps with cap rate calculation."""
        # Create a sample analysis
        analysis = {
            'analysis_name': 'Test Analysis',
            'analysis_type': 'LTR'
        }

        # Create sample comps data
        comps_data = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_value': 250000,
            'value_range_low': 230000,
            'value_range_high': 270000,
            'comparables': []
        }

        # Create sample rental comps data
        rental_comps = {
            'last_run': datetime.utcnow().isoformat(),
            'estimated_rent': 2000,  # $2000/month
            'rent_range_low': 1800,
            'rent_range_high': 2200,
            'comparable_rentals': []
        }

        # Call the function
        result = update_analysis_comps(analysis, comps_data, rental_comps)

        # Verify the cap rate calculation
        assert result is not None
        assert 'comps_data' in result
        assert 'rental_comps' in result['comps_data']
        assert 'cap_rate' in result['comps_data']['rental_comps']
        
        # Cap rate should be (2000 * 12) / 250000 * 100 = 9.6%
        assert result['comps_data']['rental_comps']['cap_rate'] == 9.6
