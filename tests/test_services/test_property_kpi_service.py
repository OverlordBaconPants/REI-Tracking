import pytest
import os
import sys
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import datetime, date

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.property_kpi_service import PropertyKPIService
from utils.money import Money, Percentage
from utils.financial_calculator import FinancialCalculator

@pytest.fixture
def sample_properties_data():
    """Sample properties data for testing."""
    return [
        {
            "address": "123 Main St",
            "purchase_price": 200000,
            "purchase_date": "2022-01-15",
            "down_payment": 40000,
            "closing_costs": 5000,
            "renovation_costs": 15000,
            "marketing_costs": 1000,
            "holding_costs": 2000
        },
        {
            "address": "456 Oak Ave",
            "purchase_price": 300000,
            "purchase_date": "2021-06-10",
            "down_payment": 60000,
            "closing_costs": 7500,
            "renovation_costs": 25000,
            "marketing_costs": 1500,
            "holding_costs": 3000
        }
    ]

@pytest.fixture
def sample_transactions():
    """Sample transactions data for testing."""
    return [
        {
            "id": "1",
            "property_id": "123 Main St",
            "type": "income",
            "category": "Rent",
            "description": "January Rent",
            "amount": 2000,
            "date": "2022-02-01",
            "collector_payer": "Tenant"
        },
        {
            "id": "2",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Property Taxes",
            "description": "Annual Property Taxes",
            "amount": 2400,
            "date": "2022-02-15",
            "collector_payer": "County"
        },
        {
            "id": "3",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Insurance",
            "description": "Annual Insurance Premium",
            "amount": 1200,
            "date": "2022-02-20",
            "collector_payer": "Insurance Company"
        },
        {
            "id": "4",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Mortgage",
            "description": "February Mortgage Payment",
            "amount": 1000,
            "date": "2022-02-01",
            "collector_payer": "Bank"
        },
        {
            "id": "5",
            "property_id": "123 Main St",
            "type": "income",
            "category": "Rent",
            "description": "February Rent",
            "amount": 2000,
            "date": "2022-03-01",
            "collector_payer": "Tenant"
        },
        {
            "id": "6",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Mortgage",
            "description": "March Mortgage Payment",
            "amount": 1000,
            "date": "2022-03-01",
            "collector_payer": "Bank"
        },
        {
            "id": "7",
            "property_id": "456 Oak Ave",
            "type": "income",
            "category": "Rent",
            "description": "January Rent",
            "amount": 3000,
            "date": "2022-02-01",
            "collector_payer": "Tenant"
        },
        {
            "id": "8",
            "property_id": "456 Oak Ave",
            "type": "expense",
            "category": "Mortgage",
            "description": "February Mortgage Payment",
            "amount": 1500,
            "date": "2022-02-01",
            "collector_payer": "Bank"
        }
    ]

@pytest.fixture
def property_kpi_service(sample_properties_data):
    """Create a PropertyKPIService instance with sample data."""
    return PropertyKPIService(sample_properties_data)

class TestPropertyKPIService:
    """Test cases for the PropertyKPIService class."""

    def test_safe_json(self, property_kpi_service):
        """Test safe_json method for handling Decimal values."""
        # Test with Decimal
        assert property_kpi_service.safe_json(Decimal('10.5')) == 10.5
        
        # Test with Infinity
        assert property_kpi_service.safe_json(Decimal('Infinity')) is None
        
        # Test with dict containing Decimal
        test_dict = {'value': Decimal('10.5'), 'infinity': Decimal('Infinity')}
        result = property_kpi_service.safe_json(test_dict)
        assert result == {'value': 10.5, 'infinity': None}
        
        # Test with list containing Decimal
        test_list = [Decimal('10.5'), Decimal('Infinity')]
        result = property_kpi_service.safe_json(test_list)
        assert result == [10.5, None]
        
        # Test with regular value
        assert property_kpi_service.safe_json("test") == "test"

    def test_get_kpi_dashboard_data(self, property_kpi_service, sample_transactions):
        """Test get_kpi_dashboard_data method."""
        # Mock the get_ytd_kpis and get_since_acquisition_kpis methods
        with patch.object(PropertyKPIService, 'get_ytd_kpis') as mock_ytd, \
             patch.object(PropertyKPIService, 'get_since_acquisition_kpis') as mock_acquisition, \
             patch.object(PropertyKPIService, '_has_complete_history') as mock_history:
            
            # Set up mock return values
            mock_ytd.return_value = {'test': 'ytd_data'}
            mock_acquisition.return_value = {'test': 'acquisition_data'}
            mock_history.return_value = True
            
            # Call the method
            result = property_kpi_service.get_kpi_dashboard_data('123 Main St', sample_transactions)
            
            # Verify the result
            assert result['year_to_date'] == {'test': 'ytd_data'}
            assert result['since_acquisition'] == {'test': 'acquisition_data'}
            assert result['analysis_comparison'] is None
            assert result['metadata']['has_complete_history'] is True
            assert result['metadata']['available_analyses'] == []
            
            # Verify the mocks were called correctly
            mock_ytd.assert_called_once_with('123 Main St', [t for t in sample_transactions if t['property_id'] == '123 Main St'])
            mock_acquisition.assert_called_once_with('123 Main St', [t for t in sample_transactions if t['property_id'] == '123 Main St'])
            mock_history.assert_called_once_with('123 Main St', [t for t in sample_transactions if t['property_id'] == '123 Main St'])

    def test_get_ytd_kpis(self, property_kpi_service, sample_transactions):
        """Test get_ytd_kpis method."""
        # Mock the calculate_property_kpis method
        with patch.object(PropertyKPIService, 'calculate_property_kpis') as mock_calculate:
            # Set up mock return value
            mock_calculate.return_value = {'test': 'ytd_data'}
            
            # Mock today's date to ensure consistent testing
            with patch('services.property_kpi_service.date') as mock_date:
                mock_date.today.return_value = date(2022, 3, 15)
                mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
                
                # Call the method
                result = property_kpi_service.get_ytd_kpis('123 Main St', sample_transactions)
                
                # Verify the result
                assert result == {'test': 'ytd_data'}
                
                # Verify the mock was called correctly
                mock_calculate.assert_called_once_with(
                    '123 Main St', 
                    sample_transactions,
                    start_date='2022-01-01',
                    end_date='2022-03-15'
                )

    def test_get_since_acquisition_kpis(self, property_kpi_service, sample_transactions):
        """Test get_since_acquisition_kpis method."""
        # Mock the calculate_property_kpis method
        with patch.object(PropertyKPIService, 'calculate_property_kpis') as mock_calculate:
            # Set up mock return value
            mock_calculate.return_value = {'test': 'acquisition_data'}
            
            # Mock today's date to ensure consistent testing
            with patch('services.property_kpi_service.date') as mock_date:
                mock_date.today.return_value = date(2022, 3, 15)
                mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
                
                # Call the method
                result = property_kpi_service.get_since_acquisition_kpis('123 Main St', sample_transactions)
                
                # Verify the result
                assert result == {'test': 'acquisition_data'}
                
                # Verify the mock was called correctly
                mock_calculate.assert_called_once_with(
                    '123 Main St', 
                    sample_transactions,
                    start_date='2022-01-15',
                    end_date='2022-03-15'
                )

    def test_get_since_acquisition_kpis_missing_purchase_date(self, property_kpi_service, sample_transactions):
        """Test get_since_acquisition_kpis method with missing purchase date."""
        # Create a property without a purchase date
        property_kpi_service.properties_data['789 Pine St'] = {
            "address": "789 Pine St",
            "purchase_price": 250000
        }
        
        # Call the method
        result = property_kpi_service.get_since_acquisition_kpis('789 Pine St', sample_transactions)
        
        # Verify the result is an empty KPI dict
        assert result == property_kpi_service._get_empty_kpi_dict()

    def test_calculate_property_kpis(self, property_kpi_service, sample_transactions):
        """Test calculate_property_kpis method."""
        # Mock the necessary methods
        with patch.object(PropertyKPIService, '_filter_transactions_by_date') as mock_filter, \
             patch.object(PropertyKPIService, '_calculate_monthly_metrics') as mock_metrics, \
             patch.object(PropertyKPIService, '_compute_kpi_metrics') as mock_compute, \
             patch.object(PropertyKPIService, 'safe_json') as mock_safe_json:
            
            # Set up mock return values
            filtered_transactions = [t for t in sample_transactions if t['property_id'] == '123 Main St']
            mock_filter.return_value = filtered_transactions
            mock_metrics.return_value = {'avg_monthly_noi': Decimal('500')}
            mock_compute.return_value = {'test': 'kpi_data'}
            mock_safe_json.return_value = {'test': 'safe_kpi_data'}
            
            # Call the method
            result = property_kpi_service.calculate_property_kpis(
                '123 Main St', 
                sample_transactions,
                start_date='2022-01-01',
                end_date='2022-03-15'
            )
            
            # Verify the result
            assert result == {'test': 'safe_kpi_data'}
            
            # Verify the mocks were called correctly
            mock_filter.assert_called_once_with(
                sample_transactions,
                '2022-01-01',
                '2022-03-15'
            )
            mock_metrics.assert_called_once_with(filtered_transactions)
            mock_compute.assert_called_once_with(
                property_kpi_service.properties_data['123 Main St'],
                {'avg_monthly_noi': Decimal('500')},
                filtered_transactions,
                '2022-01-01',
                '2022-03-15'
            )
            mock_safe_json.assert_called_once_with({'test': 'kpi_data'})

    def test_calculate_property_kpis_missing_property(self, property_kpi_service, sample_transactions):
        """Test calculate_property_kpis method with missing property."""
        # Call the method with a non-existent property
        result = property_kpi_service.calculate_property_kpis(
            'non-existent-property', 
            sample_transactions
        )
        
        # Verify the result is an empty KPI dict
        assert result == property_kpi_service._get_empty_kpi_dict()

    def test_calculate_property_kpis_no_transactions(self, property_kpi_service):
        """Test calculate_property_kpis method with no transactions."""
        # Mock the _filter_transactions_by_date method to return an empty list
        with patch.object(PropertyKPIService, '_filter_transactions_by_date') as mock_filter:
            mock_filter.return_value = []
            
            # Call the method
            result = property_kpi_service.calculate_property_kpis(
                '123 Main St', 
                []
            )
            
            # Verify the result is an empty KPI dict
            assert result == property_kpi_service._get_empty_kpi_dict()

    def test_compute_kpi_metrics(self, property_kpi_service, sample_transactions):
        """Test _compute_kpi_metrics method."""
        # Mock the necessary methods
        with patch.object(PropertyKPIService, '_calculate_total_investment') as mock_investment, \
             patch.object(PropertyKPIService, '_calculate_dscr') as mock_dscr, \
             patch.object(PropertyKPIService, '_has_complete_history') as mock_history, \
             patch.object(PropertyKPIService, '_calculate_refinance_impact') as mock_refinance, \
             patch.object(FinancialCalculator, 'calculate_cap_rate') as mock_cap_rate, \
             patch.object(FinancialCalculator, 'calculate_cash_on_cash_return') as mock_coc:
            
            # Set up mock return values
            mock_investment.return_value = Decimal('63000')  # down_payment + closing_costs + renovation_costs + marketing_costs + holding_costs
            mock_dscr.return_value = Decimal('1.5')
            mock_history.return_value = True
            mock_refinance.return_value = {'has_refinanced': False}
            mock_cap_rate.return_value = Percentage(6.0)
            mock_coc.return_value = Percentage(8.0)
            
            # Monthly metrics
            monthly_metrics = {
                'avg_monthly_income': Decimal('2000'),
                'avg_monthly_expenses': Decimal('300'),
                'avg_monthly_mortgage': Decimal('1000'),
                'avg_monthly_noi': Decimal('1700')
            }
            
            # Property details
            property_details = property_kpi_service.properties_data['123 Main St']
            
            # Filtered transactions
            filtered_transactions = [t for t in sample_transactions if t['property_id'] == '123 Main St']
            
            # Call the method
            result = property_kpi_service._compute_kpi_metrics(
                property_details,
                monthly_metrics,
                filtered_transactions,
                '2022-01-01',
                '2022-03-15'
            )
            
            # Verify the result
            assert result['net_operating_income']['monthly'] == Decimal('1700')
            assert result['net_operating_income']['annual'] == Decimal('1700') * Decimal('12')
            assert result['total_income']['monthly'] == Decimal('2000')
            assert result['total_income']['annual'] == Decimal('2000') * Decimal('12')
            assert result['total_expenses']['monthly'] == Decimal('300')
            assert result['total_expenses']['annual'] == Decimal('300') * Decimal('12')
            assert result['cap_rate'] == Decimal('6.0')
            assert result['cash_on_cash_return'] == Decimal('8.0')
            assert result['debt_service_coverage_ratio'] == Decimal('1.5')
            assert result['cash_invested'] == Decimal('63000')
            assert result['metadata']['has_complete_history'] is True
            assert result['metadata']['data_quality']['confidence_level'] == 'high'
            assert result['metadata']['data_quality']['refinance_info'] == {'has_refinanced': False}
            
            # Verify the mocks were called correctly
            mock_investment.assert_called_once_with(property_details)
            mock_dscr.assert_called_once_with(Decimal('1700'), Decimal('1000'))
            mock_history.assert_called_once_with('123 Main St', filtered_transactions)
            mock_refinance.assert_called_once_with('123 Main St', filtered_transactions, '2022-01-01', '2022-03-15')
            mock_cap_rate.assert_called_once()
            mock_coc.assert_called_once()

    def test_calculate_dscr(self, property_kpi_service):
        """Test _calculate_dscr method."""
        # Mock the FinancialCalculator.calculate_dscr method
        with patch.object(FinancialCalculator, 'calculate_dscr') as mock_dscr:
            mock_dscr.return_value = 1.5
            
            # Call the method
            result = property_kpi_service._calculate_dscr(Decimal('1500'), Decimal('1000'))
            
            # Verify the result
            assert result == Decimal('1.5')
            
            # Verify the mock was called correctly
            mock_dscr.assert_called_once_with(
                noi=Money(Decimal('1500')),
                debt_service=Money(Decimal('1000'))
            )

    def test_calculate_dscr_zero_mortgage(self, property_kpi_service):
        """Test _calculate_dscr method with zero mortgage payment."""
        # Call the method with zero mortgage payment
        result = property_kpi_service._calculate_dscr(Decimal('1500'), Decimal('0'))
        
        # Verify the result is None
        assert result is None

    def test_calculate_monthly_metrics(self, property_kpi_service, sample_transactions):
        """Test _calculate_monthly_metrics method."""
        # Filter transactions for a specific property
        property_transactions = [t for t in sample_transactions if t['property_id'] == '123 Main St']
        
        # Call the method
        result = property_kpi_service._calculate_monthly_metrics(property_transactions)
        
        # Verify the result
        # We have 2 months of data (Feb and Mar) with:
        # - Income: $2000 per month
        # - Expenses: $2400 (property taxes) + $1200 (insurance) = $3600 / 2 months = $1800 per month
        # - Mortgage: $1000 per month
        # - NOI: $2000 - $1800 = $200 per month
        assert result['avg_monthly_income'] == Decimal('2000')
        assert result['avg_monthly_expenses'] == Decimal('1800')
        assert result['avg_monthly_mortgage'] == Decimal('1000')
        assert result['avg_monthly_noi'] == Decimal('200')

    def test_calculate_monthly_metrics_no_transactions(self, property_kpi_service):
        """Test _calculate_monthly_metrics method with no transactions."""
        # Call the method with an empty list
        result = property_kpi_service._calculate_monthly_metrics([])
        
        # Verify the result
        assert result['avg_monthly_income'] == Decimal('0')
        assert result['avg_monthly_expenses'] == Decimal('0')
        assert result['avg_monthly_mortgage'] == Decimal('0')
        assert result['avg_monthly_noi'] == Decimal('0')

    def test_calculate_total_investment(self, property_kpi_service):
        """Test _calculate_total_investment method."""
        # Get property details
        property_details = property_kpi_service.properties_data['123 Main St']
        
        # Call the method
        result = property_kpi_service._calculate_total_investment(property_details)
        
        # Verify the result
        # down_payment + closing_costs + renovation_costs + marketing_costs + holding_costs
        # 40000 + 5000 + 15000 + 1000 + 2000 = 63000
        assert result == Decimal('63000')

    def test_has_complete_history(self, property_kpi_service, sample_transactions):
        """Test _has_complete_history method."""
        # Mock datetime.now to ensure consistent testing
        with patch('services.property_kpi_service.date') as mock_date, \
             patch('services.property_kpi_service.datetime') as mock_datetime:
            
            # Set up mock return values
            mock_date.today.return_value = date(2022, 3, 15)
            mock_datetime.strptime.side_effect = datetime.strptime
            
            # Filter transactions for a specific property
            property_transactions = [t for t in sample_transactions if t['property_id'] == '123 Main St']
            
            # Call the method
            result = property_kpi_service._has_complete_history('123 Main St', property_transactions)
            
            # Verify the result
            # The property was purchased on 2022-01-15 and has transactions from 2022-02-01 to 2022-03-01
            # This is within the allowed gaps (MAX_START_GAP_DAYS=30, MAX_END_GAP_DAYS=45)
            assert result is True

    def test_has_complete_history_no_transactions(self, property_kpi_service):
        """Test _has_complete_history method with no transactions."""
        # Call the method with an empty list
        result = property_kpi_service._has_complete_history('123 Main St', [])
        
        # Verify the result
        assert result is False

    def test_has_complete_history_missing_property(self, property_kpi_service, sample_transactions):
        """Test _has_complete_history method with missing property."""
        # Call the method with a non-existent property
        result = property_kpi_service._has_complete_history('non-existent-property', sample_transactions)
        
        # Verify the result
        assert result is False

    def test_calculate_refinance_impact(self, property_kpi_service, sample_transactions):
        """Test _calculate_refinance_impact method."""
        # Filter transactions for a specific property
        property_transactions = [t for t in sample_transactions if t['property_id'] == '123 Main St']
        
        # Call the method
        result = property_kpi_service._calculate_refinance_impact(
            '123 Main St',
            property_transactions,
            '2022-01-01',
            '2022-03-15'
        )
        
        # Verify the result
        # We have 2 mortgage payments of $1000 each, so no refinance detected
        assert result['has_refinanced'] is False
        assert result['original_debt_service'] == 1000.0
        assert result['current_debt_service'] == 1000.0

    def test_calculate_refinance_impact_no_mortgage(self, property_kpi_service):
        """Test _calculate_refinance_impact method with no mortgage transactions."""
        # Call the method with an empty list
        result = property_kpi_service._calculate_refinance_impact(
            '123 Main St',
            [],
            '2022-01-01',
            '2022-03-15'
        )
        
        # Verify the result
        assert result['has_refinanced'] is False
        assert result['original_debt_service'] == 0
        assert result['current_debt_service'] == 0

    def test_filter_transactions_by_date(self, property_kpi_service, sample_transactions):
        """Test _filter_transactions_by_date method."""
        # Call the method
        result = property_kpi_service._filter_transactions_by_date(
            sample_transactions,
            '2022-02-01',
            '2022-02-28'
        )
        
        # Verify the result
        # We should have 6 transactions in February
        assert len(result) == 6
        assert all(t['date'] >= '2022-02-01' and t['date'] <= '2022-02-28' for t in result)

    def test_filter_transactions_by_date_no_start(self, property_kpi_service, sample_transactions):
        """Test _filter_transactions_by_date method with no start date."""
        # Call the method
        result = property_kpi_service._filter_transactions_by_date(
            sample_transactions,
            None,
            '2022-02-28'
        )
        
        # Verify the result
        # We should have 6 transactions on or before February 28
        assert len(result) == 6
        assert all(t['date'] <= '2022-02-28' for t in result)

    def test_filter_transactions_by_date_no_end(self, property_kpi_service, sample_transactions):
        """Test _filter_transactions_by_date method with no end date."""
        # Call the method
        result = property_kpi_service._filter_transactions_by_date(
            sample_transactions,
            '2022-03-01',
            None
        )
        
        # Verify the result
        # We should have 2 transactions on or after March 1
        assert len(result) == 2
        assert all(t['date'] >= '2022-03-01' for t in result)

    def test_get_empty_kpi_dict(self, property_kpi_service):
        """Test _get_empty_kpi_dict method."""
        # Call the method
        result = property_kpi_service._get_empty_kpi_dict()
        
        # Verify the result
        assert result['net_operating_income']['monthly'] == 0
        assert result['net_operating_income']['annual'] == 0
        assert result['total_income']['monthly'] == 0
        assert result['total_income']['annual'] == 0
        assert result['total_expenses']['monthly'] == 0
        assert result['total_expenses']['annual'] == 0
        assert result['cap_rate'] == 0
        assert result['cash_on_cash_return'] == 0
        assert result['debt_service_coverage_ratio'] == 0
        assert result['cash_invested'] == 0
        assert result['metadata']['has_complete_history'] is False
        assert result['metadata']['data_quality']['confidence_level'] == 'low'
        assert result['metadata']['data_quality']['refinance_info']['has_refinanced'] is False
        assert result['metadata']['data_quality']['refinance_info']['original_debt_service'] == 0
        assert result['metadata']['data_quality']['refinance_info']['current_debt_service'] == 0
