import unittest
from unittest.mock import patch, Mock
from flask import url_for
from app import create_app
import json

class TestDashboardRoutes(unittest.TestCase):
    """Test suite for dashboard routes."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Create mock dash apps
        self.mock_portfolio_dash = Mock()
        self.mock_portfolio_dash.index.return_value = "Portfolio Dashboard"
        self.app.portfolio_dash = self.mock_portfolio_dash
        
        self.mock_amortization_dash = Mock()
        self.mock_amortization_dash.index.return_value = "Amortization Dashboard"
        self.app.amortization_dash = self.mock_amortization_dash

    def tearDown(self):
        """Clean up after each test."""
        self.ctx.pop()

    def login(self, session_id='123'):
        """Helper method to simulate user login."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = session_id
            sess['_fresh'] = True

    def test_dashboards_landing_unauthorized(self):
        """Test dashboard landing page without authentication."""
        response = self.client.get('/dashboards')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_dashboards_landing_authorized(self):
        """Test dashboard landing page with authentication."""
        self.login()
        response = self.client.get('/dashboards')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dashboards.html', response.data)

    def test_portfolio_view_unauthorized(self):
        """Test portfolio view without authentication."""
        response = self.client.get('/dashboards/portfolio/view')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_portfolio_view_authorized(self):
        """Test portfolio view with authentication."""
        self.login()
        response = self.client.get('/dashboards/portfolio/view')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'portfolio.html', response.data)

    def test_portfolio_view_error(self):
        """Test portfolio view error handling."""
        self.login()
        # Simulate error by removing dash app
        del self.app.portfolio_dash
        
        with self.assertRaises(Exception):
            self.client.get('/dashboards/portfolio/view')

    def test_amortization_view_unauthorized(self):
        """Test amortization view without authentication."""
        response = self.client.get('/dashboards/amortization/view')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_amortization_view_authorized(self):
        """Test amortization view with authentication."""
        self.login()
        response = self.client.get('/dashboards/amortization/view')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'amortization.html', response.data)

    def test_amortization_view_error(self):
        """Test amortization view error handling."""
        self.login()
        # Simulate error by removing dash app
        del self.app.amortization_dash
        
        with self.assertRaises(Exception):
            self.client.get('/dashboards/amortization/view')

    def test_portfolio_dash_unauthorized(self):
        """Test portfolio dashboard without authentication."""
        response = self.client.get('/dashboards/_dash/portfolio/any_path')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_portfolio_dash_authorized(self):
        """Test portfolio dashboard with authentication."""
        self.login()
        response = self.client.get('/dashboards/_dash/portfolio/any_path')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "Portfolio Dashboard")

    def test_amortization_dash_unauthorized(self):
        """Test amortization dashboard without authentication."""
        response = self.client.get('/dashboards/_dash/amortization/any_path')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_amortization_dash_authorized(self):
        """Test amortization dashboard with authentication."""
        self.login()
        response = self.client.get('/dashboards/_dash/amortization/any_path')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "Amortization Dashboard")

    def test_dash_app_initialization(self):
        """Test that dash apps are properly initialized."""
        self.assertIsNotNone(self.app.portfolio_dash)
        self.assertIsNotNone(self.app.amortization_dash)

    @patch('routes.dashboards.get_properties_for_user')
    def test_portfolio_with_data(self, mock_get_properties):
        """Test portfolio view with actual property data."""
        self.login()
        
        # Mock property data
        mock_get_properties.return_value = [
            {
                'address': '123 Test St',
                'purchase_price': 200000,
                'current_value': 250000
            }
        ]
        
        response = self.client.get('/dashboards/portfolio/view')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'portfolio.html', response.data)

    @patch('routes.dashboards.get_properties_for_user')
    def test_portfolio_no_data(self, mock_get_properties):
        """Test portfolio view with no property data."""
        self.login()
        
        # Mock empty property data
        mock_get_properties.return_value = []
        
        response = self.client.get('/dashboards/portfolio/view')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'portfolio.html', response.data)

    def test_session_handling(self):
        """Test session handling across requests."""
        # Test with valid session
        self.login()
        response = self.client.get('/dashboards')
        self.assertEqual(response.status_code, 200)
        
        # Test with expired session
        with self.client.session_transaction() as sess:
            sess.clear()
        response = self.client.get('/dashboards')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_concurrent_dashboard_access(self):
        """Test accessing multiple dashboards concurrently."""
        self.login()
        
        # Make concurrent requests to different dashboards
        response1 = self.client.get('/dashboards/portfolio/view')
        response2 = self.client.get('/dashboards/amortization/view')
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)

if __name__ == '__main__':
    unittest.main()