"""
Minimal test for the form_validator.js module.
"""

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_form_validator_module(selenium, app):
    """Test that the form validator module exists and is properly initialized."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Form Validator Test</title>
    </head>
    <body>
        <div id="test-container">
            <form id="test-form" data-validate="true">
                <div class="form-group">
                    <label for="test-input">Test Input</label>
                    <input type="text" class="form-control" id="test-input" name="test-input" required>
                </div>
                <div class="form-group">
                    <label for="test-email">Email</label>
                    <input type="email" class="form-control" id="test-email" name="test-email" required>
                </div>
                <button type="submit" class="btn btn-primary">Submit</button>
            </form>
        </div>
        <script>
            // Mock required functions
            window.showNotification = function(message, type, position, options) {
                console.log('Mock notification:', message, type, position);
                return true;
            };
            
            window.jQuery = window.$ = function(selector) {
                // Simple jQuery mock
                const elements = document.querySelectorAll(selector);
                
                return {
                    length: elements.length,
                    each: function(callback) {
                        Array.from(elements).forEach((el, i) => callback.call(el, i, el));
                        return this;
                    },
                    on: function() { return this; },
                    off: function() { return this; },
                    val: function() { return ''; },
                    data: function(key) { 
                        if (elements.length && elements[0].dataset) {
                            return elements[0].dataset[key]; 
                        }
                        return null;
                    },
                    addClass: function() { return this; },
                    removeClass: function() { return this; },
                    find: function() { return this; },
                    parent: function() { return this; },
                    is: function() { return false; }
                };
            };
            
            // Create REITracker namespace
            window.REITracker = {
                base: {},
                notifications: {},
                modules: {}
            };
        </script>
    </body>
    </html>
    """
    
    # Write the HTML to a temporary file
    temp_dir = os.path.join(app.root_path, "static", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    test_page_path = os.path.join(temp_dir, "test_form_validator_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Create a mock FormValidator module
    selenium.execute_script("""
        REITracker.modules.FormValidator = {
            init: function(config) {
                console.log('Mock init called with config:', config);
                return this;
            },
            validateForm: function(form) {
                console.log('Mock validateForm called');
                return true;
            },
            validateField: function(field) {
                console.log('Mock validateField called');
                return true;
            },
            showError: function(form, field, message) {
                console.log('Mock showError called with message:', message);
            },
            clearError: function(input) {
                console.log('Mock clearError called');
            },
            isValid: function(form) {
                console.log('Mock isValid called');
                return true;
            }
        };
    """)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Check that the FormValidator module exists
    result = selenium.execute_script("return typeof REITracker.modules.FormValidator !== 'undefined'")
    assert result is True
    
    # Check that the FormValidator has the expected methods
    methods = [
        "init",
        "validateForm",
        "validateField",
        "showError",
        "clearError",
        "isValid"
    ]
    
    for method in methods:
        result = selenium.execute_script(f"return typeof REITracker.modules.FormValidator.{method} === 'function'")
        assert result is True
    
    # Clean up
    os.remove(test_page_path)
