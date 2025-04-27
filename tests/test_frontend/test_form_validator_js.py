"""
Tests for the form_validator.js module.

This module contains tests for the form_validator.js JavaScript module,
which provides form validation functionality for the frontend.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_form_validator_module_exists(inject_scripts):
    """Test that the form validator module exists and is properly initialized."""
    driver = inject_scripts(["base.js", "modules/form_validator.js"])
    
    # Check that the module exists
    result = driver.execute_script("return typeof REITracker.modules !== 'undefined' && typeof REITracker.modules.formValidator !== 'undefined'")
    assert result is True
    
    # Check that the module has the expected methods
    methods = [
        "init", 
        "validateForm", 
        "validateField", 
        "showError", 
        "clearError",
        "getFieldValue",
        "isFieldValid"
    ]
    
    for method in methods:
        result = driver.execute_script(f"return typeof REITracker.modules.formValidator.{method} === 'function'")
        assert result is True


def test_form_validation_initialization(inject_scripts):
    """Test that the form validator initializes correctly."""
    driver = inject_scripts(["base.js", "modules/form_validator.js"])
    
    # Add a test form to the page
    driver.execute_script("""
        var form = document.createElement('form');
        form.id = 'test-validation-form';
        form.setAttribute('data-validate', 'true');
        
        var input = document.createElement('input');
        input.type = 'text';
        input.name = 'test-field';
        input.id = 'test-field';
        input.required = true;
        
        form.appendChild(input);
        document.body.appendChild(form);
    """)
    
    # Initialize the form validator
    driver.execute_script("REITracker.modules.formValidator.init()")
    
    # Check that the form has been initialized for validation
    result = driver.execute_script("return document.getElementById('test-validation-form').hasAttribute('novalidate')")
    assert result is True


def test_required_field_validation(inject_scripts):
    """Test validation of required fields."""
    driver = inject_scripts(["base.js", "modules/form_validator.js"])
    
    # Add a test form with a required field
    driver.execute_script("""
        var form = document.createElement('form');
        form.id = 'required-field-form';
        form.setAttribute('data-validate', 'true');
        
        var input = document.createElement('input');
        input.type = 'text';
        input.name = 'required-field';
        input.id = 'required-field';
        input.required = true;
        
        var errorContainer = document.createElement('div');
        errorContainer.className = 'invalid-feedback';
        
        form.appendChild(input);
        form.appendChild(errorContainer);
        document.body.appendChild(form);
        
        // Initialize the form validator
        REITracker.modules.formValidator.init();
    """)
    
    # Test empty field validation
    is_valid = driver.execute_script("""
        var field = document.getElementById('required-field');
        field.value = '';
        return REITracker.modules.formValidator.validateField(field);
    """)
    
    assert is_valid is False
    
    # Check that error message is displayed
    error_class = driver.execute_script("return document.getElementById('required-field').classList.contains('is-invalid')")
    assert error_class is True
    
    # Test with valid input
    is_valid = driver.execute_script("""
        var field = document.getElementById('required-field');
        field.value = 'Test value';
        return REITracker.modules.formValidator.validateField(field);
    """)
    
    assert is_valid is True
    
    # Check that error message is cleared
    error_class = driver.execute_script("return document.getElementById('required-field').classList.contains('is-invalid')")
    assert error_class is False


def test_email_field_validation(inject_scripts):
    """Test validation of email fields."""
    driver = inject_scripts(["base.js", "modules/form_validator.js"])
    
    # Add a test form with an email field
    driver.execute_script("""
        var form = document.createElement('form');
        form.id = 'email-field-form';
        form.setAttribute('data-validate', 'true');
        
        var input = document.createElement('input');
        input.type = 'email';
        input.name = 'email-field';
        input.id = 'email-field';
        input.required = true;
        
        var errorContainer = document.createElement('div');
        errorContainer.className = 'invalid-feedback';
        
        form.appendChild(input);
        form.appendChild(errorContainer);
        document.body.appendChild(form);
        
        // Initialize the form validator
        REITracker.modules.formValidator.init();
    """)
    
    # Test invalid email
    is_valid = driver.execute_script("""
        var field = document.getElementById('email-field');
        field.value = 'not-an-email';
        return REITracker.modules.formValidator.validateField(field);
    """)
    
    assert is_valid is False
    
    # Test valid email
    is_valid = driver.execute_script("""
        var field = document.getElementById('email-field');
        field.value = 'test@example.com';
        return REITracker.modules.formValidator.validateField(field);
    """)
    
    assert is_valid is True


def test_number_field_validation(inject_scripts):
    """Test validation of number fields."""
    driver = inject_scripts(["base.js", "modules/form_validator.js"])
    
    # Add a test form with a number field
    driver.execute_script("""
        var form = document.createElement('form');
        form.id = 'number-field-form';
        form.setAttribute('data-validate', 'true');
        
        var input = document.createElement('input');
        input.type = 'number';
        input.name = 'number-field';
        input.id = 'number-field';
        input.min = '0';
        input.max = '100';
        input.required = true;
        
        var errorContainer = document.createElement('div');
        errorContainer.className = 'invalid-feedback';
        
        form.appendChild(input);
        form.appendChild(errorContainer);
        document.body.appendChild(form);
        
        // Initialize the form validator
        REITracker.modules.formValidator.init();
    """)
    
    # Test invalid number (below min)
    is_valid = driver.execute_script("""
        var field = document.getElementById('number-field');
        field.value = '-10';
        return REITracker.modules.formValidator.validateField(field);
    """)
    
    assert is_valid is False
    
    # Test invalid number (above max)
    is_valid = driver.execute_script("""
        var field = document.getElementById('number-field');
        field.value = '200';
        return REITracker.modules.formValidator.validateField(field);
    """)
    
    assert is_valid is False
    
    # Test valid number
    is_valid = driver.execute_script("""
        var field = document.getElementById('number-field');
        field.value = '50';
        return REITracker.modules.formValidator.validateField(field);
    """)
    
    assert is_valid is True


def test_form_submission_validation(inject_scripts):
    """Test validation on form submission."""
    driver = inject_scripts(["base.js", "modules/form_validator.js"])
    
    # Add a test form with multiple fields
    driver.execute_script("""
        var form = document.createElement('form');
        form.id = 'submission-form';
        form.setAttribute('data-validate', 'true');
        
        // Add a text field
        var textInput = document.createElement('input');
        textInput.type = 'text';
        textInput.name = 'text-field';
        textInput.id = 'text-field';
        textInput.required = true;
        
        // Add an email field
        var emailInput = document.createElement('input');
        emailInput.type = 'email';
        emailInput.name = 'email-field';
        emailInput.id = 'email-field';
        emailInput.required = true;
        
        // Add a submit button
        var submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.id = 'submit-button';
        submitButton.textContent = 'Submit';
        
        // Add error containers
        var textErrorContainer = document.createElement('div');
        textErrorContainer.className = 'invalid-feedback';
        
        var emailErrorContainer = document.createElement('div');
        emailErrorContainer.className = 'invalid-feedback';
        
        // Add a submission tracker
        var submissionTracker = document.createElement('div');
        submissionTracker.id = 'submission-tracker';
        submissionTracker.textContent = 'Not submitted';
        
        form.appendChild(textInput);
        form.appendChild(textErrorContainer);
        form.appendChild(emailInput);
        form.appendChild(emailErrorContainer);
        form.appendChild(submitButton);
        document.body.appendChild(form);
        document.body.appendChild(submissionTracker);
        
        // Initialize the form validator
        REITracker.modules.formValidator.init();
        
        // Add a submit handler
        document.getElementById('submission-form').addEventListener('submit', function(e) {
            e.preventDefault();
            document.getElementById('submission-tracker').textContent = 'Form submitted';
        });
    """)
    
    # Try to submit with invalid fields
    driver.execute_script("""
        var form = document.getElementById('submission-form');
        form.dispatchEvent(new Event('submit'));
    """)
    
    # Check that the form was not submitted
    submission_status = driver.execute_script("return document.getElementById('submission-tracker').textContent")
    assert submission_status == "Not submitted"
    
    # Fill in valid values and submit
    driver.execute_script("""
        document.getElementById('text-field').value = 'Test value';
        document.getElementById('email-field').value = 'test@example.com';
        var form = document.getElementById('submission-form');
        form.dispatchEvent(new Event('submit'));
    """)
    
    # Check that the form was submitted
    submission_status = driver.execute_script("return document.getElementById('submission-tracker').textContent")
    assert submission_status == "Form submitted"
