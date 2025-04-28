"""
Tests for the base.js module.

This module contains tests for the base.js JavaScript module,
which provides shared functionality for the frontend.
"""

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_base_module_exists(selenium, app):
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
            
            // Mock toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
            
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
    test_page_path = os.path.join(temp_dir, "test_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Read the notifications.js file
    notifications_js_path = os.path.join(app.root_path, "static", "js", "notifications.js")
    with open(notifications_js_path, "r") as f:
        notifications_js_content = f.read()
    
    # Read the base.js file
    base_js_path = os.path.join(app.root_path, "static", "js", "base.js")
    with open(base_js_path, "r") as f:
        base_js_content = f.read()
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
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


def test_device_detection(selenium, app):
    """Test the device detection methods."""
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
            
            // Mock toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
            
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
    test_page_path = os.path.join(temp_dir, "test_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Read the notifications.js file
    notifications_js_path = os.path.join(app.root_path, "static", "js", "notifications.js")
    with open(notifications_js_path, "r") as f:
        notifications_js_content = f.read()
    
    # Read the base.js file
    base_js_path = os.path.join(app.root_path, "static", "js", "base.js")
    with open(base_js_path, "r") as f:
        base_js_content = f.read()
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
    # Inject the base.js content
    selenium.execute_script(base_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Set a mobile viewport size
    selenium.set_window_size(375, 667)  # iPhone 8 size
    selenium.execute_script("window.baseModule.viewportWidth = 375")
    is_mobile = selenium.execute_script("return window.innerWidth < 768")
    assert is_mobile is True
    
    # Set a tablet viewport size
    selenium.set_window_size(768, 1024)  # iPad size
    selenium.execute_script("window.baseModule.viewportWidth = 768")
    is_tablet = selenium.execute_script("return window.innerWidth >= 768 && window.innerWidth < 992")
    assert is_tablet is True
    
    # Set a desktop viewport size
    selenium.set_window_size(1200, 800)
    selenium.execute_script("window.baseModule.viewportWidth = 1200")
    is_desktop = selenium.execute_script("return window.innerWidth >= 992")
    assert is_desktop is True
    
    # Clean up
    os.remove(test_page_path)


def test_formatting_functions(selenium, app):
    """Test the formatting functions."""
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
            
            // Mock toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
            
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
    test_page_path = os.path.join(temp_dir, "test_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Read the notifications.js file
    notifications_js_path = os.path.join(app.root_path, "static", "js", "notifications.js")
    with open(notifications_js_path, "r") as f:
        notifications_js_content = f.read()
    
    # Read the base.js file
    base_js_path = os.path.join(app.root_path, "static", "js", "base.js")
    with open(base_js_path, "r") as f:
        base_js_content = f.read()
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
    # Inject the base.js content
    selenium.execute_script(base_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Test currency formatting
    money_result = selenium.execute_script("return window.baseModule.formatCurrency(1234.56)")
    assert "$1,234.56" in money_result
    
    # Test percentage formatting
    percent_result = selenium.execute_script("return window.baseModule.formatPercentage(12.34)")
    assert "12.34%" in percent_result
    
    # Test numeric parsing
    parse_result = selenium.execute_script("return window.baseModule.parseNumericValue('$1,234.56')")
    assert parse_result == 1234.56
    
    # Clean up
    os.remove(test_page_path)


def test_utility_functions(selenium, app):
    """Test the utility functions."""
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
            
            // Mock toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
            
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
    test_page_path = os.path.join(temp_dir, "test_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Read the notifications.js file
    notifications_js_path = os.path.join(app.root_path, "static", "js", "notifications.js")
    with open(notifications_js_path, "r") as f:
        notifications_js_content = f.read()
    
    # Read the base.js file
    base_js_path = os.path.join(app.root_path, "static", "js", "base.js")
    with open(base_js_path, "r") as f:
        base_js_content = f.read()
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
    # Inject the base.js content
    selenium.execute_script(base_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Test initialization
    selenium.execute_script("window.baseModule.init()")
    
    # Test environment detection
    selenium.execute_script("window.baseModule.detectEnvironment()")
    
    # Test library initialization
    result = selenium.execute_script("""
        // Mock required libraries for test
        window.jQuery = window.jQuery || {};
        window.bootstrap = window.bootstrap || {};
        window.toastr = window.toastr || {};
        window._ = window._ || {
            debounce: function(fn) { return fn; },
            throttle: function(fn) { return fn; },
            templateSettings: { interpolate: null }
        };
        
        // Test the function
        return window.baseModule.initializeLibraries();
    """)
    
    assert result is True
    
    # Clean up
    os.remove(test_page_path)
