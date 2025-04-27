"""
Tests for the occupancy calculator route.
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

def test_occupancy_calculator_view_accessible(client, test_user):
    """Test that the occupancy calculator view is accessible."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the occupancy calculator
    response = client.get('/dashboards/occupancy-calculator')
    
    # Should return 200 OK
    assert response.status_code == 200
    
    # Check for expected content
    assert b'Occupancy Rate Calculator' in response.data
    assert b'Calculate and analyze occupancy rates for multi-family properties' in response.data
    assert b'Total Units' in response.data
    assert b'Occupied Units' in response.data
    assert b'Average Rent per Unit' in response.data
    assert b'Target Occupancy Rate' in response.data
    assert b'Market Average Occupancy Rate' in response.data

def test_occupancy_calculator_form_elements(client, test_user):
    """Test that the occupancy calculator form contains all required elements."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the occupancy calculator
    response = client.get('/dashboards/occupancy-calculator')
    
    # Check for form elements
    assert b'<form id="occupancy-calculator-form">' in response.data
    assert b'<input type="number" class="form-control" id="total-units"' in response.data
    assert b'<input type="number" class="form-control" id="occupied-units"' in response.data
    assert b'<input type="number" class="form-control" id="average-rent"' in response.data
    assert b'<input type="number" class="form-control" id="target-occupancy"' in response.data
    assert b'<input type="number" class="form-control" id="market-occupancy"' in response.data
    assert b'<button type="submit" class="btn btn-primary">' in response.data

def test_occupancy_calculator_results_container(client, test_user):
    """Test that the occupancy calculator results container exists."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the occupancy calculator
    response = client.get('/dashboards/occupancy-calculator')
    
    # Check for results container elements
    assert b'<div id="results-container" style="display: none;">' in response.data
    assert b'<div class="alert mb-4" id="occupancy-alert">' in response.data
    assert b'<h4 class="alert-heading">Current Occupancy Rate</h4>' in response.data
    assert b'<h2 class="text-center my-4" id="occupancy-rate-result">0%</h2>' in response.data
    assert b'<p class="card-text text-center fs-4" id="potential-revenue-result">$0</p>' in response.data
    assert b'<p class="card-text text-center fs-4" id="actual-revenue-result">$0</p>' in response.data
    assert b'<p class="card-text text-center fs-4" id="revenue-gap-result">$0</p>' in response.data
    assert b'<p class="card-text text-center fs-4" id="units-needed-result">0</p>' in response.data
    assert b'<p class="card-text text-center fs-4" id="breakeven-occupancy-result">0%</p>' in response.data
    assert b'<p class="card-text text-center fs-4" id="net-income-result">$0</p>' in response.data
    assert b'<div class="progress mb-3" style="height: 25px;">' in response.data
    assert b'<button type="button" class="btn btn-outline-primary" id="print-results">' in response.data

def test_occupancy_calculator_javascript_included(client, test_user):
    """Test that the occupancy calculator JavaScript is included."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the occupancy calculator
    response = client.get('/dashboards/occupancy-calculator')
    
    # Check for JavaScript inclusion
    assert b'<script type="module" src="' in response.data
    assert b'occupancy_calculator.js' in response.data
