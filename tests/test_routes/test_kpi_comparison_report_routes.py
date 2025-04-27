"""
Unit tests for the KPI comparison report routes.
"""

import io
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from flask import Flask, g

from src.routes.property_financial_routes import property_financial_bp


@patch('src.routes.property_financial_routes.g')
@patch('src.routes.property_financial_routes.property_financial_service')
@patch('src.routes.property_financial_routes.kpi_report_generator')
class TestKPIComparisonReportRoutes(unittest.TestCase):
    """Test cases for the KPI comparison report routes."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a Flask app
        self.app = Flask(__name__)
        self.app.register_blueprint(property_financial_bp)
        self.client = self.app.test_client()
        
        # Set up test context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Mock the login_required decorator
        self.login_patcher = patch('src.routes.property_financial_routes.login_required')
        self.mock_login_required = self.login_patcher.start()
        self.mock_login_required.return_value = lambda f: f
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.app_context.pop()
        self.login_patcher.stop()
    
    @patch('src.routes.property_financial_routes.send_file')
    def test_generate_kpi_comparison_report(self, mock_send_file, mock_kpi_generator, mock_property_service, mock_g):
        """Test generating a KPI comparison report."""
        # Set up mock g
        mock_g.current_user = MagicMock()
        mock_g.current_user.id = "123"
        mock_g.current_user.name = "Test User"
        
        # Create a mock property
        mock_property = MagicMock()
        mock_property.id = "456"
        mock_property.address = "123 Main St, Anytown, USA"
        type(mock_property).id = PropertyMock(return_value="456")
        type(mock_property).address = PropertyMock(return_value="123 Main St, Anytown, USA")
        
        # Set up mock property service
        mock_property_service.property_repo.get_by_id.return_value = mock_property
        
        # Set up mock send_file
        mock_send_file.return_value = "PDF file"
        
        # Make the request
        response = self.client.get('/api/property-financials/kpi-report/456?analysis_id=789')
        
        # Assert that the property repository was called correctly
        mock_property_service.property_repo.get_by_id.assert_called_once_with("456")
        
        # Assert that the report generator was called correctly
        mock_kpi_generator.generate.assert_called_once()
        args, kwargs = mock_kpi_generator.generate.call_args
        self.assertEqual(kwargs['property_id'], "456")
        self.assertEqual(kwargs['user_id'], "123")
        self.assertEqual(kwargs['analysis_id'], "789")
        
        # Assert that send_file was called
        mock_send_file.assert_called_once()
        args, kwargs = mock_send_file.call_args
        self.assertEqual(kwargs['mimetype'], 'application/pdf')
        self.assertEqual(kwargs['as_attachment'], True)
        self.assertTrue('KPI_Comparison_Report_123_Main_St' in kwargs['download_name'])
    
    def test_generate_kpi_comparison_report_property_not_found(self, mock_kpi_generator, mock_property_service, mock_g):
        """Test generating a KPI comparison report when the property is not found."""
        # Set up mock g
        mock_g.current_user = MagicMock()
        mock_g.current_user.id = "123"
        mock_g.current_user.name = "Test User"
        
        # Set up mock property service
        mock_property_service.property_repo.get_by_id.return_value = None
        
        # Make the request
        response = self.client.get('/api/property-financials/kpi-report/456')
        
        # Assert that the property repository was called correctly
        mock_property_service.property_repo.get_by_id.assert_called_once_with("456")
        
        # Assert that the response is correct
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Property not found', response.data)
    
    def test_generate_kpi_comparison_report_with_error(self, mock_kpi_generator, mock_property_service, mock_g):
        """Test generating a KPI comparison report when an error occurs."""
        # Set up mock g
        mock_g.current_user = MagicMock()
        mock_g.current_user.id = "123"
        mock_g.current_user.name = "Test User"
        
        # Create a mock property
        mock_property = MagicMock()
        mock_property.id = "456"
        mock_property.address = "123 Main St, Anytown, USA"
        type(mock_property).id = PropertyMock(return_value="456")
        type(mock_property).address = PropertyMock(return_value="123 Main St, Anytown, USA")
        
        # Set up mock property service
        mock_property_service.property_repo.get_by_id.return_value = mock_property
        
        # Set up mock kpi generator to raise an exception
        mock_kpi_generator.generate.side_effect = ValueError("Test error")
        
        # Make the request
        response = self.client.get('/api/property-financials/kpi-report/456')
        
        # Assert that the property repository was called correctly
        mock_property_service.property_repo.get_by_id.assert_called_once_with("456")
        
        # Assert that the report generator was called correctly
        mock_kpi_generator.generate.assert_called_once()
        
        # Assert that the response is correct
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Test error', response.data)
    
    def test_generate_kpi_comparison_report_with_date_range(self, mock_kpi_generator, mock_property_service, mock_g):
        """Test generating a KPI comparison report with a date range."""
        # Set up mock g
        mock_g.current_user = MagicMock()
        mock_g.current_user.id = "123"
        mock_g.current_user.name = "Test User"
        
        # Create a mock property
        mock_property = MagicMock()
        mock_property.id = "456"
        mock_property.address = "123 Main St, Anytown, USA"
        type(mock_property).id = PropertyMock(return_value="456")
        type(mock_property).address = PropertyMock(return_value="123 Main St, Anytown, USA")
        
        # Set up mock property service
        mock_property_service.property_repo.get_by_id.return_value = mock_property
        
        # Make the request with date range
        response = self.client.get('/api/property-financials/kpi-report/456?start_date=2025-01-01&end_date=2025-04-01')
        
        # Assert that the report generator was called correctly
        mock_kpi_generator.generate.assert_called_once()
        args, kwargs = mock_kpi_generator.generate.call_args
        self.assertEqual(kwargs['property_id'], "456")
        self.assertEqual(kwargs['user_id'], "123")
        self.assertEqual(kwargs['start_date'], "2025-01-01")
        self.assertEqual(kwargs['end_date'], "2025-04-01")
        
        # Assert that the metadata contains the date range
        metadata = kwargs['metadata']
        self.assertEqual(metadata['date_range'], "2025-01-01 to 2025-04-01")


if __name__ == '__main__':
    unittest.main()
