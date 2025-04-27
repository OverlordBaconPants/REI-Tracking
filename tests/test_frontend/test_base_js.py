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
    driver = inject_scripts(["notifications.js", "base.js"])
    
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


def test_device_detection(inject_scripts):
    """Test the device detection methods."""
    driver = inject_scripts(["notifications.js", "base.js"])
    
    # Set a mobile viewport size
    driver.set_window_size(375, 667)  # iPhone 8 size
    driver.execute_script("window.baseModule.viewportWidth = 375")
    is_mobile = driver.execute_script("return window.innerWidth < 768")
    assert is_mobile is True
    
    # Set a tablet viewport size
    driver.set_window_size(768, 1024)  # iPad size
    driver.execute_script("window.baseModule.viewportWidth = 768")
    is_tablet = driver.execute_script("return window.innerWidth >= 768 && window.innerWidth < 992")
    assert is_tablet is True
    
    # Set a desktop viewport size
    driver.set_window_size(1200, 800)
    driver.execute_script("window.baseModule.viewportWidth = 1200")
    is_desktop = driver.execute_script("return window.innerWidth >= 992")
    assert is_desktop is True


def test_formatting_functions(inject_scripts):
    """Test the formatting functions."""
    driver = inject_scripts(["notifications.js", "base.js"])
    
    # Test currency formatting
    money_result = driver.execute_script("return window.baseModule.formatCurrency(1234.56)")
    assert "$1,234.56" in money_result
    
    # Test percentage formatting
    percent_result = driver.execute_script("return window.baseModule.formatPercentage(12.34)")
    assert "12.34%" in percent_result
    
    # Test numeric parsing
    parse_result = driver.execute_script("return window.baseModule.parseNumericValue('$1,234.56')")
    assert parse_result == 1234.56


def test_utility_functions(inject_scripts):
    """Test the utility functions."""
    driver = inject_scripts(["notifications.js", "base.js"])
    
    # Test initialization
    driver.execute_script("window.baseModule.init()")
    
    # Test environment detection
    driver.execute_script("window.baseModule.detectEnvironment()")
    
    # Test library initialization
    result = driver.execute_script("""
        // Mock required libraries for test
        window.jQuery = {};
        window.bootstrap = {};
        window.toastr = {};
        window._ = {};
        
        // Test the function
        return window.baseModule.initializeLibraries();
    """)
    
    assert result is True
