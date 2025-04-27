"""
Minimal test for the notifications.js module.
"""

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_notifications_module(selenium, app):
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
                success: function(message, title, options) { 
                    console.log('Success:', message);
                    return { options: options || {} }; 
                },
                error: function(message, title, options) { 
                    console.log('Error:', message);
                    return { options: options || {} }; 
                },
                warning: function(message, title, options) { 
                    console.log('Warning:', message);
                    return { options: options || {} }; 
                },
                info: function(message, title, options) { 
                    console.log('Info:', message);
                    return { options: options || {} }; 
                }
            };
            
            // Create a copy for bottom toasts
            window.toastrBottom = window.toastr;
            
            // Mock bootstrap
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
        </script>
    </body>
    </html>
    """
    
    # Write the HTML to a temporary file
    temp_dir = os.path.join(app.root_path, "static", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    test_page_path = os.path.join(temp_dir, "test_notifications_page.html")
    
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
    
    # Check that the showNotification function exists
    result = selenium.execute_script("return typeof window.showNotification === 'function'")
    assert result is True
    
    # Check that other notification functions exist
    functions = [
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
    
    # Test showing a notification
    result = selenium.execute_script("return window.showSuccess('Test notification')")
    assert result is not None
    
    # Clean up
    os.remove(test_page_path)
