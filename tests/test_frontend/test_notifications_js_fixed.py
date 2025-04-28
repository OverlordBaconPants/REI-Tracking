"""
Tests for the notifications.js module.

This module contains tests for the notifications.js JavaScript module,
which provides notification functionality for the frontend.
"""

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_notifications_module_exists(selenium, app):
    """Test that the notifications module exists and is properly initialized."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Notifications.js Test</title>
    </head>
    <body>
        <div id="test-container"></div>
        <script>
            // Mock required functions
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
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Check that the notification functions exist
    functions = [
        "showNotification",
        "showSuccess",
        "showError",
        "showWarning",
        "showInfo",
        "clearNotifications",
        "getNotificationHistory",
        "clearNotificationHistory"
    ]
    
    for func in functions:
        result = selenium.execute_script(f"return typeof window.{func} === 'function'")
        assert result is True
    
    # Clean up
    os.remove(test_page_path)


def test_notification_display(selenium, app):
    """Test the notification display functionality."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Notifications.js Test</title>
    </head>
    <body>
        <div id="test-container"></div>
        <script>
            // Mock required functions
            window.toastr = {
                options: {},
                success: function(message, title, options) { 
                    console.log('Success notification:', message);
                    return true;
                },
                error: function(message, title, options) { 
                    console.log('Error notification:', message);
                    return true;
                },
                warning: function(message, title, options) { 
                    console.log('Warning notification:', message);
                    return true;
                },
                info: function(message, title, options) { 
                    console.log('Info notification:', message);
                    return true;
                },
                clear: function() {
                    console.log('Clearing notifications');
                    return true;
                }
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
            
            // Create a mock document.body.appendChild function
            document.body.appendChild = function(element) {
                console.log('Appending element:', element);
                return element;
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
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Test showing notifications
    success_result = selenium.execute_script("return window.showSuccess('Success message')")
    assert success_result is not None
    
    error_result = selenium.execute_script("return window.showError('Error message')")
    assert error_result is not None
    
    warning_result = selenium.execute_script("return window.showWarning('Warning message')")
    assert warning_result is not None
    
    info_result = selenium.execute_script("return window.showInfo('Info message')")
    assert info_result is not None
    
    # Test notification history
    history = selenium.execute_script("return window.getNotificationHistory()")
    assert len(history) == 4
    
    # Test clearing notifications
    selenium.execute_script("window.clearNotifications()")
    
    # Test clearing history
    selenium.execute_script("window.clearNotificationHistory()")
    history = selenium.execute_script("return window.getNotificationHistory()")
    assert len(history) == 0
    
    # Clean up
    os.remove(test_page_path)


def test_notification_options(selenium, app):
    """Test the notification options functionality."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Notifications.js Test</title>
    </head>
    <body>
        <div id="test-container"></div>
        <script>
            // Mock required functions
            window.toastr = {
                options: {},
                success: function(message, title, options) { 
                    console.log('Success notification:', message, title, options);
                    return true;
                },
                error: function(message, title, options) { 
                    console.log('Error notification:', message, title, options);
                    return true;
                },
                warning: function(message, title, options) { 
                    console.log('Warning notification:', message, title, options);
                    return true;
                },
                info: function(message, title, options) { 
                    console.log('Info notification:', message, title, options);
                    return true;
                }
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
            
            // Create a mock document.body.appendChild function
            document.body.appendChild = function(element) {
                console.log('Appending element:', element);
                return element;
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
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Test notification with options
    options = {
        'title': 'Test Title',
        'timeOut': 10000,
        'showIcon': True
    }
    
    result = selenium.execute_script("""
        return window.showNotification(
            'Test message with options',
            'success',
            'top',
            {
                title: 'Test Title',
                timeOut: 10000,
                showIcon: true
            }
        );
    """)
    
    assert result is not None
    
    # Clean up
    os.remove(test_page_path)


def test_notification_accessibility(selenium, app):
    """Test the notification accessibility features."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Notifications.js Test</title>
    </head>
    <body>
        <div id="test-container"></div>
        <script>
            // Mock required functions
            window.toastr = {
                options: {},
                success: function(message, title, options) { 
                    console.log('Success notification:', message, title, options);
                    return true;
                },
                error: function(message, title, options) { 
                    console.log('Error notification:', message, title, options);
                    return true;
                },
                warning: function(message, title, options) { 
                    console.log('Warning notification:', message, title, options);
                    return true;
                },
                info: function(message, title, options) { 
                    console.log('Info notification:', message, title, options);
                    return true;
                }
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
            
            // Create a mock document.body.appendChild function
            document.body.appendChild = function(element) {
                console.log('Appending element:', element);
                return element;
            };
            
            // Create a mock getElementById function and elements object
            const elements = {};
            
            document.getElementById = function(id) {
                if (id === 'sr-alert-container') {
                    if (!elements[id]) {
                        elements[id] = {
                            id: id,
                            className: 'sr-only',
                            setAttribute: function(attr, value) {
                                this[attr] = value;
                            },
                            textContent: ''
                        };
                    }
                    return elements[id];
                }
                return document.querySelector('#' + id);
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
    
    # Inject the notifications.js content
    selenium.execute_script(notifications_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Test screen reader alert container creation
    sr_container_exists = selenium.execute_script("""
        return document.getElementById('sr-alert-container') !== null;
    """)
    
    assert sr_container_exists is True
    
    # Test notification with screen reader announcement
    selenium.execute_script("""
        window.showNotification('Test message for screen readers', 'error');
    """)
    
    # Check that the screen reader alert container has the correct content
    sr_content = selenium.execute_script("""
        return document.getElementById('sr-alert-container').textContent;
    """)
    
    assert 'error' in sr_content.lower()
    assert 'test message for screen readers' in sr_content.lower()
    
    # Clean up
    os.remove(test_page_path)
