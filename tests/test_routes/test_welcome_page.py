"""
Tests for the welcome page route.
"""

import pytest
from unittest.mock import MagicMock, patch
from flask import url_for, session
from flask_login import login_user

from src.models.user import User, PropertyAccess


@pytest.fixture
def test_user():
    """Create a test user for testing."""
    # Create a mock user with property access
    property_access = [
        PropertyAccess(property_id="prop1", access_level="owner", equity_share=100.0)
    ]

    user = User(
        id="user1",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="hashed_password",
        role="User",
        property_access=property_access
    )
    
    return user


@pytest.fixture
def app():
    """Create a Flask application for testing."""
    from src.main import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-key'
    return app

def test_welcome_page_accessible(client, test_user):
    """Test that the welcome page is accessible."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the welcome page
    response = client.get('/dashboards/welcome')
    
    # Should return 200 OK
    assert response.status_code == 200
    
    # Check for expected content
    assert b'Welcome to REI Tracker' in response.data
    assert b'Your comprehensive solution for real estate investment tracking, analysis, and management.' in response.data
    assert b'Getting Started' in response.data

def test_welcome_page_getting_started_section(client, test_user):
    """Test that the welcome page contains the getting started section."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the welcome page
    response = client.get('/dashboards/welcome')
    
    # Check for getting started section
    assert b'<h2 class="card-title mb-4">Getting Started</h2>' in response.data
    assert b'<div class="welcome-step">' in response.data
    assert b'<div class="welcome-step-number">1</div>' in response.data
    assert b'<h5>Add Your Properties</h5>' in response.data
    assert b'<div class="welcome-step-number">2</div>' in response.data
    assert b'<h5>Track Transactions</h5>' in response.data
    assert b'<div class="welcome-step-number">3</div>' in response.data
    assert b'<h5>Analyze Performance</h5>' in response.data
    assert b'<a href="' in response.data
    assert b'Go to Dashboard' in response.data

def test_welcome_page_feature_cards(client, test_user):
    """Test that the welcome page contains feature cards."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the welcome page
    response = client.get('/dashboards/welcome')
    
    # Check for feature cards
    assert b'<h5 class="mb-0">' in response.data
    assert b'Powerful Calculators' in response.data
    assert b'Interactive Dashboards' in response.data
    assert b'Comprehensive Reports' in response.data
    
    # Check for feature descriptions
    assert b'Maximum Allowable Offer (MAO) Calculator' in response.data
    assert b'Cash-on-Cash Return Calculator' in response.data
    assert b'Portfolio Overview Dashboard' in response.data
    assert b'Amortization Schedule Dashboard' in response.data
    assert b'Transaction Reports with Documentation' in response.data
    assert b'KPI Comparison Reports' in response.data
    
    # Check for feature links
    assert b'Try MAO Calculator' in response.data
    assert b'View Portfolio Dashboard' in response.data
    assert b'Generate KPI Report' in response.data

def test_welcome_page_styling(client, test_user):
    """Test that the welcome page includes custom styling."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the welcome page
    response = client.get('/dashboards/welcome')
    
    # Check for custom styling
    assert b'<style>' in response.data
    assert b'.welcome-page {' in response.data
    assert b'.welcome-logo {' in response.data
    assert b'.welcome-step {' in response.data
    assert b'.welcome-step-number {' in response.data
    assert b'@media (min-width: 768px) {' in response.data
    assert b'@media print {' in response.data
