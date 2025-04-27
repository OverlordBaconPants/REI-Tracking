"""
Unit tests for the KPI dashboard and KPI comparison tool.
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import session

from src.main import application


class TestKPIDashboard(unittest.TestCase):
    """Test cases for the KPI dashboard and KPI comparison tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = application
        self.client = self.app.test_client()
        
        # Set up test context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Set up test session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 'test_user_id'
            sess['_test_mode'] = True
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.app_context.pop()
    
    @patch('src.routes.dashboards_routes.current_user')
    def test_kpi_dashboard_access(self, mock_current_user):
        """Test accessing the KPI dashboard."""
        # Set up mock current_user
        mock_current_user.name = "Test User"
        mock_current_user.is_authenticated = True
        mock_current_user.is_admin.return_value = False
        mock_current_user.get_accessible_properties.return_value = ["property1"]
        
        # Access the KPI dashboard
        response = self.client.get('/dashboards/kpi')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'KPI Dashboard', response.data)
    
    @patch('src.routes.dashboards_routes.current_user')
    @patch('src.services.property_financial_service.get_properties_for_user')
    def test_kpi_comparison_tool_access(self, mock_get_properties, mock_current_user):
        """Test accessing the KPI comparison tool."""
        # Set up mock current_user
        mock_current_user.name = "Test User"
        mock_current_user.id = "test_user_id"
        mock_current_user.is_authenticated = True
        mock_current_user.is_admin.return_value = False
        mock_current_user.get_accessible_properties.return_value = ["property1"]
        
        # Set up mock properties
        mock_get_properties.return_value = [
            {"id": "property1", "address": "123 Main St, Anytown, USA"}
        ]
        
        # Access the KPI comparison tool
        response = self.client.get('/dashboards/kpi-comparison')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'KPI Comparison Tool', response.data)
        self.assertIn(b'Select Property', response.data)
        self.assertIn(b'Generate KPI Comparison Report', response.data)
    
    @patch('src.routes.dashboards_routes.current_user')
    def test_kpi_dash_access(self, mock_current_user):
        """Test accessing the KPI dash component."""
        # Set up mock current_user
        mock_current_user.name = "Test User"
        mock_current_user.is_authenticated = True
        mock_current_user.is_admin.return_value = False
        mock_current_user.get_accessible_properties.return_value = ["property1"]
        
        # Access the KPI dash component
        response = self.client.get('/dashboards/_dash/kpi/')
        
        # Assert response
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
