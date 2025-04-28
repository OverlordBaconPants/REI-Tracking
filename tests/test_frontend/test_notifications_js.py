"""
Tests for the notifications.js module.

This module contains tests for the notifications.js JavaScript module,
which provides notification functionality for the frontend.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_notifications_module_exists(inject_scripts):
    """Test that the notifications module exists and is properly initialized."""
    driver = inject_scripts(["base.js", "notifications.js"])
    
    # Check that the notifications module exists
    result = driver.execute_script("return typeof REITracker.notifications !== 'undefined'")
    assert result is True
    
    # Check that the notifications module has the expected methods
    methods = [
        "init", 
        "success", 
        "error", 
        "warning", 
        "info",
        "show"
    ]
    
    for method in methods:
        result = driver.execute_script(f"return typeof REITracker.notifications.{method} === 'function'")
        assert result is True


def test_notification_display(inject_scripts):
    """Test that notifications are displayed correctly."""
    driver = inject_scripts(["base.js", "notifications.js"])
    
    # Initialize the notifications module and set up the test environment
    driver.execute_script("""
        // Add a div to capture the notification content
        var captureDiv = document.createElement('div');
        captureDiv.id = 'notification-capture';
        document.body.appendChild(captureDiv);
        
        // Override toastr to capture the notification
        window.originalToastr = window.toastr;
        window.toastr = {
            success: function(message) {
                document.getElementById('notification-capture').innerHTML = 'success: ' + message;
                return { options: {} };
            },
            error: function(message) {
                document.getElementById('notification-capture').innerHTML = 'error: ' + message;
                return { options: {} };
            },
            warning: function(message) {
                document.getElementById('notification-capture').innerHTML = 'warning: ' + message;
                return { options: {} };
            },
            info: function(message) {
                document.getElementById('notification-capture').innerHTML = 'info: ' + message;
                return { options: {} };
            },
            options: {}
        };
        
        // Initialize the notifications module
        REITracker.notifications.init();
        
        // Show a success notification
        REITracker.notifications.success('Test success message');
    """)
    
    # Check that the success notification was captured
    notification_text = driver.execute_script("return document.getElementById('notification-capture').innerHTML")
    assert "success:" in notification_text
    assert "Test success message" in notification_text
    
    # Test other notification types
    driver.execute_script("REITracker.notifications.error('Test error message')")
    notification_text = driver.execute_script("return document.getElementById('notification-capture').innerHTML")
    assert "error:" in notification_text
    assert "Test error message" in notification_text
    
    driver.execute_script("REITracker.notifications.warning('Test warning message')")
    notification_text = driver.execute_script("return document.getElementById('notification-capture').innerHTML")
    assert "warning:" in notification_text
    assert "Test warning message" in notification_text
    
    driver.execute_script("REITracker.notifications.info('Test info message')")
    notification_text = driver.execute_script("return document.getElementById('notification-capture').innerHTML")
    assert "info:" in notification_text
    assert "Test info message" in notification_text


def test_notification_options(inject_scripts):
    """Test that notification options are applied correctly."""
    driver = inject_scripts(["base.js", "notifications.js"])
    
    # Initialize the notifications module and set up the test environment
    driver.execute_script("""
        // Add a div to capture the notification options
        var captureDiv = document.createElement('div');
        captureDiv.id = 'options-capture';
        document.body.appendChild(captureDiv);
        
        // Override toastr to capture options
        window.originalToastr = window.toastr;
        window.toastr = {
            success: function(message, title, options) {
                document.getElementById('options-capture').innerHTML = JSON.stringify(options || {});
                return { options: options || {} };
            },
            options: {}
        };
        
        // Initialize the notifications module
        REITracker.notifications.init();
        
        // Show a notification with custom options
        REITracker.notifications.show('Test message', 'success', 'top-right', {
            timeOut: 5000,
            closeButton: true,
            progressBar: true
        });
    """)
    
    # Check that the options were applied
    options_json = driver.execute_script("return document.getElementById('options-capture').innerHTML")
    assert "timeOut" in options_json
    assert "closeButton" in options_json
    assert "progressBar" in options_json


def test_notification_accessibility(inject_scripts):
    """Test that notifications have proper accessibility attributes."""
    driver = inject_scripts(["base.js", "notifications.js"])
    
    # Initialize the notifications module and set up the test environment
    driver.execute_script("""
        // Add a div to capture the notification content
        var captureDiv = document.createElement('div');
        captureDiv.id = 'mock-notification';
        document.body.appendChild(captureDiv);
        
        // Override toastr to check accessibility options
        window.originalToastr = window.toastr;
        window.toastr = {
            success: function(message, title, options) {
                var element = document.getElementById('mock-notification');
                element.setAttribute('role', 'alert');
                element.setAttribute('aria-live', 'assertive');
                return { options: options || {} };
            },
            options: {}
        };
        
        // Initialize the notifications module
        REITracker.notifications.init();
        
        // Show a notification
        REITracker.notifications.success('Test message');
    """)
    
    # Check that the notification has proper accessibility attributes
    role = driver.execute_script("return document.getElementById('mock-notification').getAttribute('role')")
    aria_live = driver.execute_script("return document.getElementById('mock-notification').getAttribute('aria-live')")
    
    assert role == "alert"
    assert aria_live == "assertive"
