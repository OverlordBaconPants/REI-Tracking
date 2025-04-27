"""
Tests for the MAO calculator route.
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

def test_mao_calculator_view_accessible(client, test_user):
    """Test that the MAO calculator view is accessible."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the MAO calculator
    response = client.get('/dashboards/mao-calculator')
    
    # Should return 200 OK
    assert response.status_code == 200
    
    # Check for expected content
    assert b'Maximum Allowable Offer (MAO) Calculator' in response.data
    assert b'Calculate the maximum amount you should offer for a property' in response.data
    assert b'Investment Strategy' in response.data

def test_mao_calculator_form_elements(client, test_user):
    """Test that the MAO calculator form contains all required elements."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the MAO calculator
    response = client.get('/dashboards/mao-calculator')
    
    # Check for form elements
    assert b'<form id="mao-calculator-form">' in response.data
    assert b'<select class="form-select" id="analysis-type"' in response.data
    assert b'<option value="LTR">Long-Term Rental (LTR)</option>' in response.data
    assert b'<option value="BRRRR">Buy, Rehab, Rent, Refinance, Repeat (BRRRR)</option>' in response.data
    assert b'<input type="number" class="form-control" id="monthly-rent"' in response.data
    assert b'<input type="number" class="form-control" id="property-taxes"' in response.data
    assert b'<button type="submit" class="btn btn-primary">' in response.data

def test_mao_calculator_results_container(client, test_user):
    """Test that the MAO calculator results container exists."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the MAO calculator
    response = client.get('/dashboards/mao-calculator')
    
    # Check for results container elements
    assert b'<div id="results-container" style="display: none;">' in response.data
    assert b'<h2 class="text-center my-4" id="mao-result">$0</h2>' in response.data
    assert b'<h5>Calculation Breakdown</h5>' in response.data
    assert b'<table class="table table-striped">' in response.data
    assert b'<tbody id="calculation-breakdown">' in response.data
    assert b'<button type="button" class="btn btn-outline-primary" id="print-results">' in response.data

def test_mao_calculator_javascript_included(client, test_user):
    """Test that the MAO calculator JavaScript is included."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the MAO calculator
    response = client.get('/dashboards/mao-calculator')
    
    # Check for JavaScript inclusion
    assert b'<script type="module" src="' in response.data
    assert b'mao_calculator.js' in response.data

def test_mao_calculator_brrrr_specific_fields(client, test_user):
    """Test that the MAO calculator includes BRRRR-specific fields."""
    # Set up test session
    with client.session_transaction() as session:
        session['user_id'] = test_user.id
        session['_fresh'] = True
        session['_test_mode'] = True
    
    # Access the MAO calculator
    response = client.get('/dashboards/mao-calculator')
    
    # Check for BRRRR-specific fields
    assert b'<div id="brrrr-fields" class="strategy-fields" style="display: none;">' in response.data
    assert b'<label for="after-repair-value" class="form-label">After Repair Value (ARV)</label>' in response.data
    assert b'<input type="number" class="form-control" id="after-repair-value"' in response.data
    assert b'<label for="renovation-costs" class="form-label">Renovation Costs</label>' in response.data
    assert b'<input type="number" class="form-control" id="renovation-costs"' in response.data
    assert b'<label for="refinance-ltv-percentage" class="form-label">Refinance LTV %</label>' in response.data
    assert b'<input type="number" class="form-control" id="refinance-ltv-percentage"' in response.data
