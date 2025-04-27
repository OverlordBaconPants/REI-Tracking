"""
Tests for the base.js module without dependencies.
"""

import pytest


def test_base_module_exists(inject_scripts):
    """Test that the base module exists and is properly initialized."""
    # First, mock the required functions that base.js might call
    driver = inject_scripts([])
    
    # Mock window.showNotification and other dependencies
    driver.execute_script("""
        // Mock notification function
        window.showNotification = function(message, type, position, options) {
            console.log('Mock notification:', message, type, position);
            return true;
        };
        
        // Mock other required functions/objects
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
        
        // Mock jQuery
        window.jQuery = window.$ = function() {
            return {
                on: function() { return this; },
                off: function() { return this; }
            };
        };
        
        // Mock lodash
        window._ = {
            debounce: function(fn) { return fn; },
            throttle: function(fn) { return fn; },
            templateSettings: { interpolate: null }
        };
    """)
    
    # Now inject the base.js file using the inject_scripts function
    driver = inject_scripts(["base.js"])
    
    # Check that the baseModule object exists
    result = driver.execute_script("return typeof window.baseModule !== 'undefined'")
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
        result = driver.execute_script(f"return typeof window.baseModule.{method} === 'function'")
        assert result is True
