import pytest
from utils.mao_calculator import calculate_mao
from unittest.mock import patch, MagicMock

def test_calculate_mao_with_user_defaults():
    """Test MAO calculation with user defaults."""
    # Test data
    arv = 200000
    analysis_data = {
        'analysis_type': 'BRRRR',
        'renovation_costs': 30000,
        'renovation_duration': 3,
        'closing_costs': 5000,
        'property_taxes': 200,
        'insurance': 100,
        'utilities': 150
    }
    
    # Test with no user defaults
    result = calculate_mao(arv, analysis_data)
    assert 'value' in result
    # Expected calculation: (200000 * 0.75) - 30000 - 5000 - (450 * 3) + 10000
    expected_value = (200000 * 0.75) - 30000 - 5000 - (450 * 3) + 10000
    assert result['value'] == expected_value
    assert result['ltv_percentage'] == 75.0
    assert result['max_cash_left'] == 10000
    
    # Test with user defaults
    user_defaults = {
        'ltv_percentage': 80.0,
        'monthly_holding_costs': 500,
        'max_cash_left': 15000
    }
    result = calculate_mao(arv, analysis_data, user_defaults)
    assert 'value' in result
    # Expected calculation: (200000 * 0.8) - 30000 - 5000 - (500 * 3) + 15000
    expected_value = (200000 * 0.8) - 30000 - 5000 - (500 * 3) + 15000
    assert result['value'] == expected_value
    assert result['ltv_percentage'] == 80.0
    assert result['monthly_holding_costs'] == 500
    assert result['max_cash_left'] == 15000
    
    # Test with partial user defaults
    user_defaults = {
        'ltv_percentage': 85.0
    }
    result = calculate_mao(arv, analysis_data, user_defaults)
    assert 'value' in result
    # Expected calculation: (200000 * 0.85) - 30000 - 5000 - (450 * 3) + 10000
    expected_value = (200000 * 0.85) - 30000 - 5000 - (450 * 3) + 10000
    assert result['value'] == expected_value
    assert result['ltv_percentage'] == 85.0
    assert result['max_cash_left'] == 10000  # Default value
    
    # Test with negative result (should be clamped to 0)
    analysis_data['renovation_costs'] = 300000  # Very high renovation costs
    result = calculate_mao(arv, analysis_data, user_defaults)
    assert result['value'] == 0

def test_calculate_mao_with_analysis_type_specific_ltv():
    """Test MAO calculation with analysis type specific LTV."""
    # Test data
    arv = 200000
    
    # Test with BRRRR analysis type and refinance_ltv_percentage
    analysis_data = {
        'analysis_type': 'BRRRR',
        'renovation_costs': 30000,
        'renovation_duration': 3,
        'closing_costs': 5000,
        'refinance_ltv_percentage': 70.0
    }
    
    # User defaults should be overridden by analysis-specific LTV
    user_defaults = {
        'ltv_percentage': 80.0,
        'monthly_holding_costs': 500,
        'max_cash_left': 15000
    }
    
    result = calculate_mao(arv, analysis_data, user_defaults)
    assert result['ltv_percentage'] == 70.0  # Should use refinance_ltv_percentage
    
    # Test with balloon payment
    analysis_data = {
        'analysis_type': 'LTR',
        'renovation_costs': 30000,
        'renovation_duration': 3,
        'closing_costs': 5000,
        'has_balloon_payment': True,
        'balloon_refinance_ltv_percentage': 65.0
    }
    
    result = calculate_mao(arv, analysis_data, user_defaults)
    assert result['ltv_percentage'] == 65.0  # Should use balloon_refinance_ltv_percentage
