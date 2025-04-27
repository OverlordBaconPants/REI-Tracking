"""
Unit tests for the KPI comparison report generator.
"""

import io
import unittest
from unittest.mock import patch, MagicMock, ANY
from decimal import Decimal

from src.services.kpi_comparison_report_generator import KPIComparisonReportGenerator


class TestKPIComparisonReportGenerator(unittest.TestCase):
    """Test cases for the KPI comparison report generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.report_generator = KPIComparisonReportGenerator()
        
        # Sample comparison data
        self.comparison_data = {
            "property_id": "123",
            "address": "123 Main St, Anytown, USA",
            "actual_metrics": {
                "total_income": {
                    "monthly": "1000.00",
                    "annual": "12000.00"
                },
                "total_expenses": {
                    "monthly": "600.00",
                    "annual": "7200.00"
                },
                "net_operating_income": {
                    "monthly": "400.00",
                    "annual": "4800.00"
                },
                "cash_flow": {
                    "monthly": "200.00",
                    "annual": "2400.00"
                },
                "cap_rate": "5.00",
                "cash_on_cash_return": "8.00",
                "debt_service_coverage_ratio": "1.50"
            },
            "projected_metrics": {
                "total_income": {
                    "monthly": "1200.00",
                    "annual": "14400.00"
                },
                "total_expenses": {
                    "monthly": "500.00",
                    "annual": "6000.00"
                },
                "net_operating_income": {
                    "monthly": "700.00",
                    "annual": "8400.00"
                },
                "cash_flow": {
                    "monthly": "500.00",
                    "annual": "6000.00"
                },
                "cap_rate": "7.00",
                "cash_on_cash_return": "10.00",
                "debt_service_coverage_ratio": "2.00"
            },
            "comparison": {
                "income": {
                    "monthly_variance": "-200.00",
                    "monthly_variance_percentage": "-16.67",
                    "is_better_than_projected": False
                },
                "expenses": {
                    "monthly_variance": "100.00",
                    "monthly_variance_percentage": "20.00",
                    "is_better_than_projected": False
                },
                "noi": {
                    "monthly_variance": "-300.00",
                    "monthly_variance_percentage": "-42.86",
                    "is_better_than_projected": False
                },
                "cash_flow": {
                    "monthly_variance": "-300.00",
                    "monthly_variance_percentage": "-60.00",
                    "is_better_than_projected": False
                },
                "cap_rate": {
                    "variance": "-2.00",
                    "variance_percentage": "-28.57",
                    "is_better_than_projected": False
                },
                "cash_on_cash_return": {
                    "variance": "-2.00",
                    "variance_percentage": "-20.00",
                    "is_better_than_projected": False
                },
                "debt_service_coverage_ratio": {
                    "variance": "-0.50",
                    "variance_percentage": "-25.00",
                    "is_better_than_projected": False
                },
                "overall": {
                    "performance_score": 0.0,
                    "metrics_better_than_projected": 0,
                    "total_metrics_compared": 7,
                    "is_better_than_projected": False
                }
            },
            "analysis_details": {
                "id": "456",
                "name": "Test Analysis",
                "type": "LTR"
            }
        }
    
    @patch('src.services.kpi_comparison_report_generator.SimpleDocTemplate')
    def test_generate_report(self, mock_simple_doc_template):
        """Test generating a KPI comparison report."""
        # Mock the property financial service
        self.report_generator.property_financial_service = MagicMock()
        self.report_generator.property_financial_service.compare_actual_to_projected.return_value = self.comparison_data
        
        # Mock the SimpleDocTemplate
        mock_doc_instance = mock_simple_doc_template.return_value
        
        # Create a buffer for the PDF
        buffer = io.BytesIO()
        
        # Call the generate method
        self.report_generator.generate(
            property_id="123",
            user_id="456",
            output_buffer=buffer,
            analysis_id="789",
            metadata={"generated_by": "Test User"}
        )
        
        # Assert that the property financial service was called correctly
        self.report_generator.property_financial_service.compare_actual_to_projected.assert_called_once_with(
            "123", "456", analysis_id="789"
        )
        
        # Assert that the SimpleDocTemplate was created correctly
        mock_simple_doc_template.assert_called_once_with(
            buffer,
            pagesize=ANY,
            rightMargin=ANY,
            leftMargin=ANY,
            topMargin=ANY,
            bottomMargin=ANY
        )
        
        # Assert that the build method was called
        mock_doc_instance.build.assert_called_once()
    
    def test_format_decimal(self):
        """Test formatting decimal values."""
        # Test with string values
        self.assertEqual(self.report_generator._format_decimal("1000.00"), "1000.00")
        self.assertEqual(self.report_generator._format_decimal("$1,000.00"), "1000.00")
        self.assertEqual(self.report_generator._format_decimal("5%"), "5.00")
        
        # Test with numeric values
        self.assertEqual(self.report_generator._format_decimal(1000), "1000.00")
        self.assertEqual(self.report_generator._format_decimal(1000.5), "1000.50")
        self.assertEqual(self.report_generator._format_decimal(Decimal("1000.50")), "1000.50")
        
        # Test with invalid values
        self.assertEqual(self.report_generator._format_decimal("invalid"), "0.00")
        self.assertEqual(self.report_generator._format_decimal(None), "0.00")
    
    @patch('src.services.kpi_comparison_report_generator.plt.savefig')
    @patch('src.services.kpi_comparison_report_generator.plt.subplots')
    def test_create_income_expense_comparison_chart(self, mock_subplots, mock_savefig):
        """Test creating an income/expense comparison chart."""
        # Mock the plt.subplots return value
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Call the method
        result = self.report_generator._create_income_expense_comparison_chart(self.comparison_data)
        
        # Assert that the result is a BytesIO object
        self.assertIsInstance(result, io.BytesIO)
        
        # Assert that savefig was called
        mock_savefig.assert_called_once()
    
    @patch('src.services.kpi_comparison_report_generator.plt.savefig')
    @patch('src.services.kpi_comparison_report_generator.plt.subplots')
    def test_create_cash_flow_comparison_chart(self, mock_subplots, mock_savefig):
        """Test creating a cash flow comparison chart."""
        # Mock the plt.subplots return value
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Call the method
        result = self.report_generator._create_cash_flow_comparison_chart(self.comparison_data)
        
        # Assert that the result is a BytesIO object
        self.assertIsInstance(result, io.BytesIO)
        
        # Assert that savefig was called
        mock_savefig.assert_called_once()
    
    @patch('src.services.kpi_comparison_report_generator.plt.savefig')
    @patch('src.services.kpi_comparison_report_generator.plt.subplots')
    def test_create_metrics_comparison_chart(self, mock_subplots, mock_savefig):
        """Test creating a metrics comparison chart."""
        # Mock the plt.subplots return value
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Call the method
        result = self.report_generator._create_metrics_comparison_chart(self.comparison_data)
        
        # Assert that the result is a BytesIO object
        self.assertIsInstance(result, io.BytesIO)
        
        # Assert that savefig was called
        mock_savefig.assert_called_once()


if __name__ == '__main__':
    unittest.main()
