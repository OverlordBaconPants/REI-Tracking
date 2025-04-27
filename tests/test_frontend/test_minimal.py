"""
Minimal test for the base.js module.
"""

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_base_module(selenium, app):
    """Test that the base module exists and is properly initialized."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Base.js Test</title>
    </head>
    <body>
        <div id="test-container"></div>
        <script>
            // Mock required functions
            window.showNotification = function(message, type, position, options) {
                console.log('Mock notification:', message, type, position);
                return true;
            };
            
            window.toastr = {
                options: {},
                success: function() {},
                error: function() {},
                warning: function() {},
                info: function() {}
            };
            
            window.bootstrap = {
                Tooltip: function() { 
                    return { 
                        dispose: function() {} 
                    }; 
                },
                Collapse: function() {
                    return {
                        hide: function() {}
                    };
                },
                Popover: function() {
                    return {};
                }
            };
            
            window.bootstrap.Tooltip.getInstance = function() {
                return { dispose: function() {} };
            };
            
            window.bootstrap.Collapse.getInstance = function() {
                return { hide: function() {} };
            };
            
            window.jQuery = window.$ = function() {
                return {
                    on: function() { return this; },
                    off: function() { return this; }
                };
            };
            
            window._ = {
                debounce: function(fn) { return fn; },
                throttle: function(fn) { return fn; },
                templateSettings: { interpolate: null }
            };
        </script>
    </body>
    </html>
    """
    
    # Write the HTML to a temporary file
    temp_dir = os.path.join(app.root_path, "static", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    test_page_path = os.path.join(temp_dir, "test_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Read the base.js file
    base_js_path = os.path.join(app.root_path, "static", "js", "base.js")
    with open(base_js_path, "r") as f:
        base_js_content = f.read()
    
    # Inject the base.js content
    selenium.execute_script(base_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Check that the baseModule object exists
    result = selenium.execute_script("return typeof window.baseModule !== 'undefined'")
    assert result is True
    
    # Check that the base module has the expected methods
    methods = [
        "init", 
        "detectEnvironment", 
        "initializeLibraries", 
        "formatCurrency",
        "formatPercentage",
        "parseNumericValue"
    ]
    
    for method in methods:
        result = selenium.execute_script(f"return typeof window.baseModule.{method} === 'function'")
        assert result is True
    
    # Clean up
    os.remove(test_page_path)
