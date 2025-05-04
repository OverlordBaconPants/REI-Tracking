import pytest
import json
import threading
from unittest.mock import patch, MagicMock
from decimal import Decimal

from utils.standardized_metrics import (
    register_metrics, get_metrics, cached_generate_kpi_data,
    generate_kpi_data, extract_calculated_metrics, _generate_kpi_data_impl,
    format_kpi_values_for_display, get_fallback_kpi_data,
    calculate_noi, calculate_cap_rate, calculate_cash_on_cash,
    calculate_dscr, calculate_expense_ratio
)
from utils.money import Money, Percentage


class TestMetricsRegistry:
    """Test suite for metrics registry functions."""

    def test_register_and_get_metrics(self):
        """Test registering and retrieving metrics."""
        # Generate a unique analysis ID for this test
        analysis_id = "test-analysis-1"
        test_metrics = {"noi": 1000, "cap_rate": 0.08}
        
        # Register metrics
        register_metrics(analysis_id, test_metrics)
        
        # Retrieve metrics
        retrieved_metrics = get_metrics(analysis_id)
        
        # Verify metrics were stored correctly
        assert retrieved_metrics is not None
        assert retrieved_metrics["noi"] == 1000
        assert retrieved_metrics["cap_rate"] == 0.08
        
        # Verify that modifying the original metrics doesn't affect the stored copy
        test_metrics["noi"] = 2000
        retrieved_metrics_after = get_metrics(analysis_id)
        assert retrieved_metrics_after["noi"] == 1000  # Should still be the original value

    def test_register_metrics_with_empty_id(self):
        """Test registering metrics with an empty ID."""
        # Try to register metrics with an empty ID
        register_metrics("", {"noi": 1000})
        
        # Verify that no metrics were stored
        assert get_metrics("") is None

    def test_get_metrics_nonexistent_id(self):
        """Test retrieving metrics for a non-existent ID."""
        # Try to retrieve metrics for a non-existent ID
        retrieved_metrics = get_metrics("non-existent-id")
        
        # Verify that None is returned
        assert retrieved_metrics is None

    def test_thread_safety(self):
        """Test thread safety of the metrics registry."""
        # Generate unique analysis IDs for this test
        analysis_id_1 = "thread-test-1"
        analysis_id_2 = "thread-test-2"
        
        # Define metrics to register
        metrics_1 = {"noi": 1000, "cap_rate": 0.08}
        metrics_2 = {"noi": 2000, "cap_rate": 0.09}
        
        # Define functions to run in threads
        def register_thread_1():
            register_metrics(analysis_id_1, metrics_1)
            
        def register_thread_2():
            register_metrics(analysis_id_2, metrics_2)
            
        # Create and start threads
        thread_1 = threading.Thread(target=register_thread_1)
        thread_2 = threading.Thread(target=register_thread_2)
        
        thread_1.start()
        thread_2.start()
        
        # Wait for threads to complete
        thread_1.join()
        thread_2.join()
        
        # Verify that both sets of metrics were stored correctly
        assert get_metrics(analysis_id_1) == metrics_1
        assert get_metrics(analysis_id_2) == metrics_2


class TestKPIGeneration:
    """Test suite for KPI generation functions."""

    def test_cached_generate_kpi_data_with_dict(self):
        """Test cached_generate_kpi_data with dictionary input."""
        # Create test analysis data
        analysis = {
            "metrics": {
                "noi": 1000,
                "cap_rate": 0.08,
                "cash_on_cash": 0.12,
                "dscr": 1.5,
                "expense_ratio": 0.35
            }
        }
        
        # Call the function
        kpi_data = cached_generate_kpi_data(json.dumps(analysis))
        
        # Verify KPI data
        assert kpi_data["noi"] == 1000
        assert kpi_data["cap_rate"] == 0.08
        assert kpi_data["cash_on_cash"] == 0.12
        assert kpi_data["dscr"] == 1.5
        assert kpi_data["expense_ratio"] == 0.35
        
        # Verify favorable flags
        assert kpi_data["noi_favorable"] is True  # 1000 > 800 target
        assert kpi_data["cap_rate_favorable"] is True  # 0.08 is between 0.06 and 0.12
        assert kpi_data["cash_on_cash_favorable"] is True  # 0.12 > 0.10 target
        assert kpi_data["dscr_favorable"] is True  # 1.5 > 1.25 target
        assert kpi_data["expense_ratio_favorable"] is True  # 0.35 < 0.40 target

    def test_cached_generate_kpi_data_with_string(self):
        """Test cached_generate_kpi_data with JSON string input."""
        # Create test analysis data as JSON string
        analysis_json = json.dumps({
            "metrics": {
                "noi": 700,
                "cap_rate": 0.05,
                "cash_on_cash": 0.08,
                "dscr": 1.2,
                "expense_ratio": 0.45
            }
        })
        
        # Call the function
        kpi_data = cached_generate_kpi_data(analysis_json)
        
        # Verify KPI data
        assert kpi_data["noi"] == 700
        assert kpi_data["cap_rate"] == 0.05
        assert kpi_data["cash_on_cash"] == 0.08
        assert kpi_data["dscr"] == 1.2
        assert kpi_data["expense_ratio"] == 0.45
        
        # Verify favorable flags
        assert kpi_data["noi_favorable"] is False  # 700 < 800 target
        assert kpi_data["cap_rate_favorable"] is False  # 0.05 < 0.06 min
        assert kpi_data["cash_on_cash_favorable"] is False  # 0.08 < 0.10 target
        assert kpi_data["dscr_favorable"] is False  # 1.2 < 1.25 target
        assert kpi_data["expense_ratio_favorable"] is False  # 0.45 > 0.40 target

    def test_cached_generate_kpi_data_caching(self):
        """Test that cached_generate_kpi_data actually caches results."""
        # Create test analysis data
        analysis_json = json.dumps({
            "metrics": {
                "noi": 1000,
                "cap_rate": 0.08,
                "cash_on_cash": 0.12,
                "dscr": 1.5,
                "expense_ratio": 0.35
            }
        })
        
        # Call the function twice with the same input
        kpi_data_1 = cached_generate_kpi_data(analysis_json)
        kpi_data_2 = cached_generate_kpi_data(analysis_json)
        
        # Verify that both calls return the same object (cached)
        assert kpi_data_1 is kpi_data_2

    def test_generate_kpi_data_success(self):
        """Test generate_kpi_data with successful calculation."""
        # Create test analysis data
        analysis = {
            "metrics": {
                "noi": 1000,
                "cap_rate": 0.08,
                "cash_on_cash": 0.12,
                "dscr": 1.5,
                "expense_ratio": 0.35
            }
        }
        
        # Call the function
        kpi_data = generate_kpi_data(analysis)
        
        # Verify KPI data
        assert kpi_data["noi"] == 1000
        assert kpi_data["cap_rate"] == 0.08
        assert kpi_data["cash_on_cash"] == 0.12
        assert kpi_data["dscr"] == 1.5
        assert kpi_data["expense_ratio"] == 0.35

    @patch('utils.standardized_metrics.extract_calculated_metrics')
    def test_generate_kpi_data_error(self, mock_extract):
        """Test generate_kpi_data with error handling."""
        # Mock extract_calculated_metrics to raise an exception
        mock_extract.side_effect = Exception("Test error")
        
        # Create test analysis data
        analysis = {"metrics": {}}
        
        # Call the function
        kpi_data = generate_kpi_data(analysis)
        
        # Verify that fallback data is returned
        assert kpi_data["error"] is True
        assert kpi_data["noi"] == 0
        assert kpi_data["cap_rate"] == 0
        assert kpi_data["cash_on_cash"] == 0
        assert kpi_data["dscr"] == 0
        assert kpi_data["expense_ratio"] == 0

    def test_extract_calculated_metrics_complete(self):
        """Test extract_calculated_metrics with all metrics already present."""
        # Create test analysis data with all metrics
        analysis = {
            "metrics": {
                "noi": 1000,
                "cap_rate": 0.08,
                "cash_on_cash": 0.12,
                "dscr": 1.5,
                "expense_ratio": 0.35
            }
        }
        
        # Call the function
        result = extract_calculated_metrics(analysis)
        
        # Verify that the metrics are unchanged
        assert result["metrics"]["noi"] == 1000
        assert result["metrics"]["cap_rate"] == 0.08
        assert result["metrics"]["cash_on_cash"] == 0.12
        assert result["metrics"]["dscr"] == 1.5
        assert result["metrics"]["expense_ratio"] == 0.35

    @patch('utils.standardized_metrics.calculate_noi')
    @patch('utils.standardized_metrics.calculate_cap_rate')
    @patch('utils.standardized_metrics.calculate_cash_on_cash')
    @patch('utils.standardized_metrics.calculate_dscr')
    @patch('utils.standardized_metrics.calculate_expense_ratio')
    def test_extract_calculated_metrics_missing(self, mock_expense_ratio, mock_dscr, 
                                              mock_cash_on_cash, mock_cap_rate, mock_noi):
        """Test extract_calculated_metrics with missing metrics."""
        # Set up mock return values
        mock_noi.return_value = 1000
        mock_cap_rate.return_value = 0.08
        mock_cash_on_cash.return_value = 0.12
        mock_dscr.return_value = 1.5
        mock_expense_ratio.return_value = 0.35
        
        # Create test analysis data with no metrics
        analysis = {"property": {"value": 100000}}
        
        # Call the function
        result = extract_calculated_metrics(analysis)
        
        # Verify that the metrics were calculated
        assert result["metrics"]["noi"] == 1000
        assert result["metrics"]["cap_rate"] == 0.08
        assert result["metrics"]["cash_on_cash"] == 0.12
        assert result["metrics"]["dscr"] == 1.5
        assert result["metrics"]["expense_ratio"] == 0.35
        
        # Verify that the calculation functions were called
        mock_noi.assert_called_once()
        mock_cap_rate.assert_called_once()
        mock_cash_on_cash.assert_called_once()
        mock_dscr.assert_called_once()
        mock_expense_ratio.assert_called_once()

    def test_extract_calculated_metrics_json_string(self):
        """Test extract_calculated_metrics with JSON string input."""
        # Create test analysis data as JSON string
        analysis_json = json.dumps({
            "metrics": {
                "noi": 1000,
                "cap_rate": 0.08,
                "cash_on_cash": 0.12,
                "dscr": 1.5,
                "expense_ratio": 0.35
            }
        })
        
        # Call the function
        result = extract_calculated_metrics(analysis_json)
        
        # Verify that the metrics are unchanged
        assert result["metrics"]["noi"] == 1000
        assert result["metrics"]["cap_rate"] == 0.08
        assert result["metrics"]["cash_on_cash"] == 0.12
        assert result["metrics"]["dscr"] == 1.5
        assert result["metrics"]["expense_ratio"] == 0.35

    def test_extract_calculated_metrics_error(self):
        """Test extract_calculated_metrics error handling."""
        # Create invalid input that will cause an error
        analysis = None
        
        # Call the function
        result = extract_calculated_metrics(analysis)
        
        # Verify that the original analysis is returned
        assert result is None

    def test_format_kpi_values_for_display(self):
        """Test format_kpi_values_for_display function."""
        # Create test KPI data
        kpi_data = {
            "noi": 1000,
            "cap_rate": 0.08,
            "cash_on_cash": 0.12,
            "dscr": 1.5,
            "expense_ratio": 0.35,
            "other_field": "unchanged"
        }
        
        # Call the function
        formatted = format_kpi_values_for_display(kpi_data)
        
        # Verify formatting
        assert formatted["noi"] == "$1000.00"
        assert formatted["cap_rate"] == "8.0%"
        assert formatted["cash_on_cash"] == "12.0%"
        assert formatted["dscr"] == "1.50"
        assert formatted["expense_ratio"] == "35.0%"
        assert formatted["other_field"] == "unchanged"
        
        # Verify that the original data is unchanged
        assert kpi_data["noi"] == 1000
        assert kpi_data["cap_rate"] == 0.08

    def test_format_kpi_values_already_formatted(self):
        """Test format_kpi_values_for_display with already formatted values."""
        # Create test KPI data with already formatted values
        kpi_data = {
            "noi": "$1000.00",
            "cap_rate": "8.0%",
            "cash_on_cash": "12.0%",
            "dscr": "1.50",
            "expense_ratio": "35.0%"
        }
        
        # Call the function
        formatted = format_kpi_values_for_display(kpi_data)
        
        # Verify that values are unchanged
        assert formatted["noi"] == "$1000.00"
        assert formatted["cap_rate"] == "8.0%"
        assert formatted["cash_on_cash"] == "12.0%"
        assert formatted["dscr"] == "1.50"
        assert formatted["expense_ratio"] == "35.0%"

    def test_get_fallback_kpi_data(self):
        """Test get_fallback_kpi_data function."""
        # Call the function
        fallback = get_fallback_kpi_data()
        
        # Verify fallback data
        assert fallback["noi"] == 0
        assert fallback["cap_rate"] == 0
        assert fallback["cash_on_cash"] == 0
        assert fallback["dscr"] == 0
        assert fallback["expense_ratio"] == 0
        assert fallback["error"] is True
        
        # Verify that all favorable flags are False
        assert fallback["noi_favorable"] is False
        assert fallback["cap_rate_favorable"] is False
        assert fallback["cash_on_cash_favorable"] is False
        assert fallback["dscr_favorable"] is False
        assert fallback["expense_ratio_favorable"] is False


class TestCalculationFunctions:
    """Test suite for individual calculation functions."""

    @patch('utils.standardized_metrics.get_total_income')
    @patch('utils.standardized_metrics.get_total_expenses')
    @patch('utils.financial_calculator.FinancialCalculator.calculate_noi')
    def test_calculate_noi(self, mock_calc_noi, mock_expenses, mock_income):
        """Test calculate_noi function."""
        # Set up mock return values
        mock_income.return_value = 5000
        mock_expenses.return_value = 2000
        mock_calc_noi.return_value = Money(3000)
        
        # Create test analysis data
        analysis = {"financials": {}}
        
        # Call the function
        result = calculate_noi(analysis)
        
        # Verify result
        assert result == 3000
        
        # Verify that the helper functions were called
        mock_income.assert_called_once_with(analysis)
        mock_expenses.assert_called_once_with(analysis)
        
        # Verify that the calculator was called with the right arguments
        mock_calc_noi.assert_called_once()
        args, kwargs = mock_calc_noi.call_args
        assert kwargs["income"].dollars == 5000
        assert kwargs["expenses"].dollars == 2000

    @patch('utils.standardized_metrics.calculate_noi')
    @patch('utils.financial_calculator.FinancialCalculator.calculate_cap_rate')
    def test_calculate_cap_rate(self, mock_calc_cap_rate, mock_noi):
        """Test calculate_cap_rate function."""
        # Set up mock return values
        mock_noi.return_value = 1000
        mock_calc_cap_rate.return_value = Percentage(8)
        
        # Create test analysis data
        analysis = {
            "metrics": {},
            "property": {"value": 150000}
        }
        
        # Call the function
        result = calculate_cap_rate(analysis)
        
        # Verify result
        assert result == Decimal("0.08")
        
        # Verify that the calculator was called with the right arguments
        mock_calc_cap_rate.assert_called_once()
        args, kwargs = mock_calc_cap_rate.call_args
        assert kwargs["annual_noi"].dollars == 12000  # 1000 * 12
        assert kwargs["property_value"].dollars == 150000

    @patch('utils.standardized_metrics.calculate_noi')
    @patch('utils.standardized_metrics.get_annual_debt_service')
    @patch('utils.financial_calculator.FinancialCalculator.calculate_cash_on_cash_return')
    def test_calculate_cash_on_cash(self, mock_calc_coc, mock_debt_service, mock_noi):
        """Test calculate_cash_on_cash function."""
        # Set up mock return values
        mock_noi.return_value = 1000
        mock_debt_service.return_value = 6000
        mock_calc_coc.return_value = Percentage(12)
        
        # Create test analysis data
        analysis = {
            "metrics": {},
            "investment": {"total_cash_invested": 50000}
        }
        
        # Call the function
        result = calculate_cash_on_cash(analysis)
        
        # Verify result
        assert result == Decimal("0.12")
        
        # Verify that the calculator was called with the right arguments
        mock_calc_coc.assert_called_once()
        args, kwargs = mock_calc_coc.call_args
        assert kwargs["annual_cash_flow"].dollars == 6000  # (1000 * 12) - 6000
        assert kwargs["total_investment"].dollars == 50000

    @patch('utils.standardized_metrics.calculate_noi')
    @patch('utils.standardized_metrics.get_monthly_debt_service')
    @patch('utils.financial_calculator.FinancialCalculator.calculate_dscr')
    def test_calculate_dscr(self, mock_calc_dscr, mock_debt_service, mock_noi):
        """Test calculate_dscr function."""
        # Set up mock return values
        mock_noi.return_value = 1000
        mock_debt_service.return_value = 800
        mock_calc_dscr.return_value = 1.25
        
        # Create test analysis data
        analysis = {"metrics": {}}
        
        # Call the function
        result = calculate_dscr(analysis)
        
        # Verify result
        assert result == 1.25
        
        # Verify that the calculator was called with the right arguments
        mock_calc_dscr.assert_called_once()
        args, kwargs = mock_calc_dscr.call_args
        assert kwargs["noi"].dollars == 1000
        assert kwargs["debt_service"].dollars == 800

    @patch('utils.standardized_metrics.get_total_expenses')
    @patch('utils.standardized_metrics.get_total_income')
    @patch('utils.financial_calculator.FinancialCalculator.calculate_expense_ratio')
    def test_calculate_expense_ratio(self, mock_calc_er, mock_income, mock_expenses):
        """Test calculate_expense_ratio function."""
        # Set up mock return values
        mock_expenses.return_value = 2000
        mock_income.return_value = 5000
        mock_calc_er.return_value = Percentage(40)
        
        # Create test analysis data
        analysis = {"financials": {}}
        
        # Call the function
        result = calculate_expense_ratio(analysis)
        
        # Verify result
        assert result == Decimal("0.4")
        
        # Verify that the calculator was called with the right arguments
        mock_calc_er.assert_called_once()
        args, kwargs = mock_calc_er.call_args
        assert kwargs["expenses"].dollars == 2000
        assert kwargs["income"].dollars == 5000
