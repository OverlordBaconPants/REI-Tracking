"""
Simple tests for dashboard routes.

This module contains simple tests for the dashboard routes,
focusing on basic functionality without complex authentication mocking.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, request, current_app

from src.routes.dashboards_routes import blueprint as dashboards_blueprint


def test_dashboard_routes_registered():
    """Test that dashboard routes are registered."""
    # Check that the blueprint has routes
    assert len(dashboards_blueprint.deferred_functions) > 0
    
    # Check that the blueprint has the correct url_prefix
    assert dashboards_blueprint.url_prefix == '/dashboards'


def test_dashboard_route_functions():
    """Test that the dashboard route functions exist."""
    # Import the route functions directly
    from src.routes.dashboards_routes import (
        dashboards, portfolio_view, amortization_view, 
        transactions_view, kpi_view, portfolio_dash
    )
    
    # Check that they are callable functions
    assert callable(dashboards)
    assert callable(portfolio_view)
    assert callable(amortization_view)
    assert callable(transactions_view)
    assert callable(kpi_view)
    assert callable(portfolio_dash)


def test_dashboard_templates():
    """Test that the dashboard templates exist."""
    import os
    
    # Check that the template files exist
    template_dir = os.path.join('src', 'templates', 'dashboards')
    
    assert os.path.exists(os.path.join(template_dir, 'index.html'))
    assert os.path.exists(os.path.join(template_dir, 'portfolio.html'))
    assert os.path.exists(os.path.join(template_dir, 'amortization.html'))
    assert os.path.exists(os.path.join(template_dir, 'transactions.html'))
    assert os.path.exists(os.path.join(template_dir, 'kpi.html'))
    assert os.path.exists(os.path.join(template_dir, 'coming_soon.html'))
    assert os.path.exists(os.path.join(template_dir, 'no_access.html'))
