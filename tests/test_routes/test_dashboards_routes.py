"""
Test module for dashboard routes.

This module contains tests for the dashboard routes, including
portfolio dashboard routes.
"""

import pytest
from flask import url_for
from unittest.mock import patch, MagicMock

from src.routes.dashboards_routes import blueprint as dashboards_blueprint


class TestDashboardsRoutes:
    """Test class for dashboard routes."""

    @pytest.fixture
    def authenticated_client(self, client, auth):
        """Return an authenticated client."""
        auth.login()
        return client

    def test_dashboards_index_requires_login(self, client):
        """Test that dashboards index requires login."""
        response = client.get('/dashboards/')
        assert response.status_code == 302  # Redirect to login page

    def test_dashboards_index_authenticated(self, authenticated_client):
        """Test that authenticated users can access dashboards index."""
        response = authenticated_client.get('/dashboards/')
        assert response.status_code == 200
        assert b'Portfolio Dashboard' in response.data

    def test_portfolio_view_requires_login(self, client):
        """Test that portfolio view requires login."""
        response = client.get('/dashboards/portfolio')
        assert response.status_code == 302  # Redirect to login page

    def test_portfolio_view_authenticated(self, authenticated_client):
        """Test that authenticated users can access portfolio view."""
        response = authenticated_client.get('/dashboards/portfolio')
        assert response.status_code == 200
        assert b'Portfolio Overview' in response.data

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
