"""
Test module for dashboard authentication.

This module contains tests for the dashboard authentication system,
ensuring that only authenticated users with proper permissions can access dashboards.
"""

import pytest
from flask import url_for
from unittest.mock import patch, MagicMock

from src.routes.dashboards_routes import blueprint as dashboards_blueprint
from .auth_fixture import auth  # Import the auth fixture


class TestDashboardAuthentication:
    """Test class for dashboard authentication."""

    @pytest.fixture
    def authenticated_client(self, client, auth):
        """Return an authenticated client."""
        auth.login()
        return client

    @pytest.fixture
    def admin_client(self, client, auth):
        """Return an authenticated admin client."""
        auth.login_as_admin()
        return client

    @pytest.fixture
    def no_property_client(self, client, auth):
        """Return an authenticated client with no property access."""
        auth.login_no_properties()
        return client

    def test_dashboard_index_requires_login(self, client):
        """Test that dashboard index requires login."""
        response = client.get('/dashboards/')
        assert response.status_code == 302  # Redirect to login page

    def test_dashboard_index_authenticated(self, authenticated_client):
        """Test that authenticated users can access dashboard index."""
        response = authenticated_client.get('/dashboards/')
        assert response.status_code == 200
        assert b'Portfolio Dashboard' in response.data
        assert b'Amortization Dashboard' in response.data
        assert b'Transactions Dashboard' in response.data
        assert b'KPI Dashboard' in response.data

    def test_dashboard_index_admin(self, admin_client):
        """Test that admin users can access dashboard index."""
        response = admin_client.get('/dashboards/')
        assert response.status_code == 200
        assert b'Portfolio Dashboard' in response.data

    def test_dashboard_index_no_properties(self, no_property_client):
        """Test that users with no properties see access denied."""
        response = no_property_client.get('/dashboards/')
        assert response.status_code == 200
        assert b'No Dashboard Access' in response.data
        assert b'You don\'t have access to any properties' in response.data

    def test_portfolio_view_requires_login(self, client):
        """Test that portfolio view requires login."""
        response = client.get('/dashboards/portfolio')
        assert response.status_code == 302  # Redirect to login page

    def test_portfolio_view_authenticated(self, authenticated_client):
        """Test that authenticated users can access portfolio view."""
        response = authenticated_client.get('/dashboards/portfolio')
        assert response.status_code == 200
        assert b'Portfolio Overview' in response.data

    def test_portfolio_view_no_properties(self, no_property_client):
        """Test that users with no properties see access denied for portfolio view."""
        response = no_property_client.get('/dashboards/portfolio')
        assert response.status_code == 200
        assert b'No Dashboard Access' in response.data

    def test_amortization_view_requires_login(self, client):
        """Test that amortization view requires login."""
        response = client.get('/dashboards/amortization')
        assert response.status_code == 302  # Redirect to login page

    def test_amortization_view_authenticated(self, authenticated_client):
        """Test that authenticated users can access amortization view."""
        with patch('src.routes.dashboards_routes.render_template') as mock_render:
            mock_render.return_value = 'Amortization Dashboard'
            response = authenticated_client.get('/dashboards/amortization')
            mock_render.assert_called_once()
            assert 'dashboards/amortization.html' in mock_render.call_args[0]

    def test_transactions_view_requires_login(self, client):
        """Test that transactions view requires login."""
        response = client.get('/dashboards/transactions')
        assert response.status_code == 302  # Redirect to login page

    def test_transactions_view_authenticated(self, authenticated_client):
        """Test that authenticated users can access transactions view."""
        with patch('src.routes.dashboards_routes.render_template') as mock_render:
            mock_render.return_value = 'Transactions Dashboard'
            response = authenticated_client.get('/dashboards/transactions')
            mock_render.assert_called_once()
            assert 'dashboards/transactions.html' in mock_render.call_args[0]

    def test_kpi_view_requires_login(self, client):
        """Test that KPI view requires login."""
        response = client.get('/dashboards/kpi')
        assert response.status_code == 302  # Redirect to login page

    def test_kpi_view_authenticated(self, authenticated_client):
        """Test that authenticated users can access KPI view."""
        with patch('src.routes.dashboards_routes.render_template') as mock_render:
            mock_render.return_value = 'KPI Dashboard'
            response = authenticated_client.get('/dashboards/kpi')
            mock_render.assert_called_once()
            assert 'dashboards/kpi.html' in mock_render.call_args[0]

    @patch('src.routes.dashboards_routes.current_app')
    def test_portfolio_dash_requires_login(self, mock_current_app, client):
        """Test that portfolio dash requires login."""
        response = client.get('/dashboards/_dash/portfolio/')
        assert response.status_code == 302  # Redirect to login page

    @patch('src.routes.dashboards_routes.current_app')
    def test_portfolio_dash_authenticated(self, mock_current_app, authenticated_client):
        """Test that authenticated users can access portfolio dash."""
        # Mock the portfolio dash index method
        mock_dash = MagicMock()
        mock_current_app.portfolio_dash = mock_dash
        mock_dash.index.return_value = 'Dashboard Content'

        response = authenticated_client.get('/dashboards/_dash/portfolio/')
        
        # Verify that the dash index method was called
        mock_dash.index.assert_called_once()

    @patch('src.routes.dashboards_routes.current_app')
    def test_amortization_dash_requires_login(self, mock_current_app, client):
        """Test that amortization dash requires login."""
        response = client.get('/dashboards/_dash/amortization/')
        assert response.status_code == 302  # Redirect to login page

    @patch('src.routes.dashboards_routes.current_app')
    def test_amortization_dash_authenticated(self, mock_current_app, authenticated_client):
        """Test that authenticated users can access amortization dash."""
        # Mock the amortization dash index method
        mock_dash = MagicMock()
        mock_current_app.amortization_dash = mock_dash
        mock_dash.index.return_value = 'Dashboard Content'

        response = authenticated_client.get('/dashboards/_dash/amortization/')
        
        # Verify that the dash index method was called
        mock_dash.index.assert_called_once()

    @patch('src.routes.dashboards_routes.current_app')
    def test_transactions_dash_requires_login(self, mock_current_app, client):
        """Test that transactions dash requires login."""
        response = client.get('/dashboards/_dash/transactions/')
        assert response.status_code == 302  # Redirect to login page

    @patch('src.routes.dashboards_routes.current_app')
    def test_transactions_dash_authenticated(self, mock_current_app, authenticated_client):
        """Test that authenticated users can access transactions dash."""
        # Mock the transactions dash index method
        mock_dash = MagicMock()
        mock_current_app.transactions_dash = mock_dash
        mock_dash.index.return_value = 'Dashboard Content'

        response = authenticated_client.get('/dashboards/_dash/transactions/')
        
        # Verify that the dash index method was called
        mock_dash.index.assert_called_once()

    @patch('src.routes.dashboards_routes.current_app')
    def test_kpi_dash_requires_login(self, mock_current_app, client):
        """Test that KPI dash requires login."""
        response = client.get('/dashboards/_dash/kpi/')
        assert response.status_code == 302  # Redirect to login page

    @patch('src.routes.dashboards_routes.current_app')
    def test_kpi_dash_authenticated(self, mock_current_app, authenticated_client):
        """Test that authenticated users can access KPI dash."""
        # Mock the KPI dash index method
        mock_dash = MagicMock()
        mock_current_app.kpi_dash = mock_dash
        mock_dash.index.return_value = 'Dashboard Content'

        response = authenticated_client.get('/dashboards/_dash/kpi/')
        
        # Verify that the dash index method was called
        mock_dash.index.assert_called_once()
