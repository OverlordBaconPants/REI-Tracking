"""
Integration tests for dashboard routes.

This module contains integration tests for the dashboard routes,
ensuring that they work correctly with the authentication system.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import url_for, session

from src.routes.dashboards_routes import blueprint as dashboards_blueprint
from .auth_fixture import auth


class TestDashboardRoutesIntegration:
    """Integration tests for dashboard routes."""

    def test_dashboard_index_with_auth(self, client, auth):
        """Test dashboard index with authentication."""
        # Login as a user with property access
        auth.login()
        
        # Access the dashboard index
        response = client.get('/dashboards/')
        
        # Check that the response is successful
        assert response.status_code == 200
        assert b'Portfolio Dashboard' in response.data
        assert b'Amortization Dashboard' in response.data
        assert b'Transactions Dashboard' in response.data
        assert b'KPI Dashboard' in response.data

    def test_dashboard_index_with_admin(self, client, auth):
        """Test dashboard index with admin authentication."""
        # Login as an admin
        auth.login_as_admin()
        
        # Access the dashboard index
        response = client.get('/dashboards/')
        
        # Check that the response is successful
        assert response.status_code == 200
        assert b'Portfolio Dashboard' in response.data

    def test_dashboard_index_with_no_properties(self, client, auth):
        """Test dashboard index with a user that has no property access."""
        # Login as a user with no property access
        auth.login_no_properties()
        
        # Access the dashboard index
        response = client.get('/dashboards/')
        
        # Check that the response shows the no access page
        assert response.status_code == 200
        assert b'No Dashboard Access' in response.data
        assert b'You don\'t have access to any properties' in response.data

    def test_portfolio_view_with_auth(self, client, auth):
        """Test portfolio view with authentication."""
        # Login as a user with property access
        auth.login()
        
        # Access the portfolio view
        response = client.get('/dashboards/portfolio')
        
        # Check that the response is successful
        assert response.status_code == 200
        assert b'Portfolio Overview' in response.data

    def test_portfolio_view_with_no_properties(self, client, auth):
        """Test portfolio view with a user that has no property access."""
        # Login as a user with no property access
        auth.login_no_properties()
        
        # Access the portfolio view
        response = client.get('/dashboards/portfolio')
        
        # Check that the response shows the no access page
        assert response.status_code == 200
        assert b'No Dashboard Access' in response.data

    @patch('src.routes.dashboards_routes.current_app')
    def test_portfolio_dash_with_auth(self, mock_current_app, client, auth):
        """Test portfolio dash with authentication."""
        # Login as a user with property access
        auth.login()
        
        # Mock the portfolio dash index method
        mock_dash = MagicMock()
        mock_current_app.portfolio_dash = mock_dash
        mock_dash.index.return_value = 'Dashboard Content'
        
        # Access the portfolio dash
        response = client.get('/dashboards/_dash/portfolio/')
        
        # Verify that the dash index method was called
        mock_dash.index.assert_called_once()

    @patch('src.routes.dashboards_routes.current_app')
    def test_portfolio_dash_with_no_properties(self, mock_current_app, client, auth):
        """Test portfolio dash with a user that has no property access."""
        # Login as a user with no property access
        auth.login_no_properties()
        
        # Access the portfolio dash
        response = client.get('/dashboards/_dash/portfolio/')
        
        # Check that the response shows the no access page
        assert response.status_code == 200
        assert b'No Dashboard Access' in response.data

    def test_amortization_view_with_auth(self, client, auth):
        """Test amortization view with authentication."""
        # Login as a user with property access
        auth.login()
        
        # Access the amortization view
        with patch('src.routes.dashboards_routes.render_template') as mock_render:
            mock_render.return_value = 'Amortization Dashboard'
            response = client.get('/dashboards/amortization')
            
            # Check that the template was rendered
            mock_render.assert_called_once()
            assert 'dashboards/amortization.html' in mock_render.call_args[0]

    def test_transactions_view_with_auth(self, client, auth):
        """Test transactions view with authentication."""
        # Login as a user with property access
        auth.login()
        
        # Access the transactions view
        with patch('src.routes.dashboards_routes.render_template') as mock_render:
            mock_render.return_value = 'Transactions Dashboard'
            response = client.get('/dashboards/transactions')
            
            # Check that the template was rendered
            mock_render.assert_called_once()
            assert 'dashboards/transactions.html' in mock_render.call_args[0]

    def test_kpi_view_with_auth(self, client, auth):
        """Test KPI view with authentication."""
        # Login as a user with property access
        auth.login()
        
        # Access the KPI view
        with patch('src.routes.dashboards_routes.render_template') as mock_render:
            mock_render.return_value = 'KPI Dashboard'
            response = client.get('/dashboards/kpi')
            
            # Check that the template was rendered
            mock_render.assert_called_once()
            assert 'dashboards/kpi.html' in mock_render.call_args[0]
