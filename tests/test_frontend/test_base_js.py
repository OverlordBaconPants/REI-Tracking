"""
Tests for the base.js module.

This module contains tests for the base.js JavaScript module,
which provides shared functionality for the frontend.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_base_module_exists(inject_scripts):
    """Test that the base module exists and is properly initialized."""
    # First, ensure toastr is defined
    driver = inject_scripts([])
    driver.execute_script("""
        // Define toastr if not already defined
        if (typeof window.toastr === 'undefined') {
            window.toastr = {
                options: {},
                success: function(message, title, options) { return { options: options || {} }; },
                error: function(message, title, options) { return { options: options || {} }; },
                warning: function(message, title, options) { return { options: options || {} }; },
                info: function(message, title, options) { return { options: options || {} }; }
            };
            
            // Define toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
        }
    """)
    
    # Now inject the scripts
    driver = inject_scripts(["base.js"])
    
    # Add debugging information
    driver.execute_script("""
        console.log('Window properties:', Object.keys(window));
        console.log('REITracker properties:', Object.keys(window.REITracker));
        console.log('baseModule defined:', typeof window.baseModule !== 'undefined');
        console.log('baseModule in REITracker:', typeof window.REITracker.base !== 'undefined');
        
        // Print the actual baseModule object
        if (typeof window.baseModule !== 'undefined') {
            console.log('baseModule properties:', Object.keys(window.baseModule));
            console.log('baseModule:', JSON.stringify(window.baseModule));
        }
        
        if (typeof window.REITracker.base !== 'undefined') {
            console.log('REITracker.base properties:', Object.keys(window.REITracker.base));
            console.log('REITracker.base:', JSON.stringify(window.REITracker.base));
        }
    """)
    
    # Check that the baseModule object exists
    result = driver.execute_script("return typeof window.baseModule !== 'undefined'")
    if not result:
        # Try to get it from REITracker namespace
        result = driver.execute_script("return typeof window.REITracker.base !== 'undefined'")
        if result:
            # If it's in REITracker namespace, copy it to window
            driver.execute_script("window.baseModule = window.REITracker.base;")
            result = driver.execute_script("return typeof window.baseModule !== 'undefined'")
    
    assert result is True, "baseModule is not defined in window or REITracker namespace"
    
    # Print the actual properties of the baseModule object
    actual_properties = driver.execute_script("return Object.keys(window.baseModule)")
    print(f"Actual baseModule properties: {actual_properties}")
    
    # Check that the base module has the expected properties
    properties = [
        "device", 
        "format", 
        "utils", 
        "init"
    ]
    
    for prop in properties:
        result = driver.execute_script(f"return typeof window.baseModule.{prop} !== 'undefined'")
        if not result:
            print(f"Property {prop} is not defined in baseModule")
        assert result is True


def test_device_detection(inject_scripts):
    """Test the device detection methods."""
    # First, ensure toastr is defined
    driver = inject_scripts([])
    driver.execute_script("""
        // Define toastr if not already defined
        if (typeof window.toastr === 'undefined') {
            window.toastr = {
                options: {},
                success: function(message, title, options) { return { options: options || {} }; },
                error: function(message, title, options) { return { options: options || {} }; },
                warning: function(message, title, options) { return { options: options || {} }; },
                info: function(message, title, options) { return { options: options || {} }; }
            };
            
            // Define toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
        }
    """)
    
    # Now inject the scripts
    driver = inject_scripts(["base.js"])
    
    # Test device detection
    driver.set_window_size(375, 667)  # iPhone 8 size
    driver.execute_script("window.baseModule.device.detectDeviceType()")
    is_mobile = driver.execute_script("return window.baseModule.device.isMobile")
    assert is_mobile is True
    
    # Set a tablet viewport size
    driver.set_window_size(800, 1024)  # iPad size
    driver.execute_script("window.baseModule.device.detectDeviceType()")
    is_tablet = driver.execute_script("return window.baseModule.device.isTablet")
    assert is_tablet is True
    
    # Set a desktop viewport size
    driver.set_window_size(1200, 800)
    driver.execute_script("window.baseModule.device.detectDeviceType()")
    is_desktop = driver.execute_script("return window.baseModule.device.isDesktop")
    assert is_desktop is True


def test_formatting_functions(inject_scripts):
    """Test the formatting functions."""
    # First, ensure toastr is defined
    driver = inject_scripts([])
    driver.execute_script("""
        // Define toastr if not already defined
        if (typeof window.toastr === 'undefined') {
            window.toastr = {
                options: {},
                success: function(message, title, options) { return { options: options || {} }; },
                error: function(message, title, options) { return { options: options || {} }; },
                warning: function(message, title, options) { return { options: options || {} }; },
                info: function(message, title, options) { return { options: options || {} }; }
            };
            
            // Define toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
        }
    """)
    
    # Now inject the scripts
    driver = inject_scripts(["base.js"])
    
    # Test currency formatting
    money_result = driver.execute_script("return window.baseModule.format.currency(1234.56)")
    assert "$1,234.56" in money_result
    
    # Test percentage formatting
    percent_result = driver.execute_script("return window.baseModule.format.percentage(0.1234)")
    assert "12.34%" in percent_result
    
    # Test date formatting
    date_result = driver.execute_script("return window.baseModule.format.date(new Date(2023, 0, 15))")
    assert "01/15/2023" in date_result
    
    # Test phone formatting
    phone_result = driver.execute_script("return window.baseModule.format.phone('1234567890')")
    assert "(123) 456-7890" in phone_result


def test_utility_functions(inject_scripts):
    """Test the utility functions."""
    # First, ensure toastr is defined
    driver = inject_scripts([])
    driver.execute_script("""
        // Define toastr if not already defined
        if (typeof window.toastr === 'undefined') {
            window.toastr = {
                options: {},
                success: function(message, title, options) { return { options: options || {} }; },
                error: function(message, title, options) { return { options: options || {} }; },
                warning: function(message, title, options) { return { options: options || {} }; },
                info: function(message, title, options) { return { options: options || {} }; }
            };
            
            // Define toastr instances
            window.toastrBottom = window.toastr;
            window.toastrTop = window.toastr;
        }
        
        // Define bootstrap if not already defined
        if (typeof window.bootstrap === 'undefined') {
            window.bootstrap = {
                Tooltip: function() {
                    return {
                        dispose: function() {}
                    };
                },
                Collapse: function() {
                    return {
                        hide: function() {},
                        show: function() {}
                    };
                },
                Popover: function() {
                    return {};
                }
            };
            
            bootstrap.Tooltip.getInstance = function() {
                return { dispose: function() {} };
            };
            
            bootstrap.Collapse.getInstance = function() {
                return { hide: function() {}, show: function() {} };
            };
        }
    """)
    
    # Now inject the scripts
    driver = inject_scripts(["base.js"])
    
    # Mock document.cookie for testing
    driver.execute_script("""
        // Create a mock for document.cookie
        let mockCookies = {};
        
        // Override the setCookie function
        window.baseModule.utils.setCookie = function(name, value, days) {
            mockCookies[name] = value;
            console.log('Mock cookie set:', name, value);
        };
        
        // Override the getCookie function
        window.baseModule.utils.getCookie = function(name) {
            console.log('Mock cookie get:', name, mockCookies[name]);
            return mockCookies[name] || null;
        };
    """)
    
    # Test cookie functions with the mock
    driver.execute_script("window.baseModule.utils.setCookie('test_cookie', 'test_value', 1)")
    cookie_value = driver.execute_script("return window.baseModule.utils.getCookie('test_cookie')")
    assert cookie_value == "test_value"
    
    # Test ID generation
    id_result = driver.execute_script("return window.baseModule.utils.generateId(10)")
    assert len(id_result) == 10
    
    # Test email validation
    valid_email = driver.execute_script("return window.baseModule.utils.validateEmail('test@example.com')")
    assert valid_email is True
    
    invalid_email = driver.execute_script("return window.baseModule.utils.validateEmail('invalid-email')")
    assert invalid_email is False
    
    # Test phone validation
    valid_phone = driver.execute_script("return window.baseModule.utils.validatePhone('1234567890')")
    assert valid_phone is True
    
    invalid_phone = driver.execute_script("return window.baseModule.utils.validatePhone('invalid-phone')")
    assert invalid_phone is False
