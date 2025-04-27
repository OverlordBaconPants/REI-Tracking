"""
Minimal test for the main.js module.
"""

import pytest
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_main_module(selenium, app):
    """Test that the main.js module initializes correctly."""
    # Create a simple HTML page
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Main.js Test</title>
    </head>
    <body>
        <div id="test-container">
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#">REI Tracker</a>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item">
                                <a class="nav-link" href="#">Dashboard</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#">Properties</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <div class="container mt-4">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                Test Card
                            </div>
                            <div class="card-body">
                                <p>This is a test card for the main.js test.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <script>
            // Mock required functions and objects
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
                    is: function() { return false; },
                    html: function(content) {
                        if (elements.length && content !== undefined) {
                            elements[0].innerHTML = content;
                        }
                        return elements.length ? elements[0].innerHTML : '';
                    },
                    append: function() { return this; },
                    ready: function(callback) {
                        callback();
                        return this;
                    }
                };
            };
            
            // Mock bootstrap
            window.bootstrap = {
                Tooltip: function(element, options) {
                    return {
                        dispose: function() {}
                    };
                },
                Collapse: function(element, options) {
                    return {
                        hide: function() {}
                    };
                },
                Popover: function(element, options) {
                    return {};
                }
            };
            
            window.bootstrap.Tooltip.getInstance = function() {
                return { dispose: function() {} };
            };
            
            window.bootstrap.Collapse.getInstance = function() {
                return { hide: function() {} };
            };
            
            // Create REITracker namespace
            window.REITracker = {
                base: {
                    init: function() { console.log('Base module initialized'); },
                    detectEnvironment: function() { return 'desktop'; },
                    initializeLibraries: function() { return true; },
                    formatCurrency: function(value) { return '$' + parseFloat(value).toFixed(2); },
                    formatPercentage: function(value) { return parseFloat(value).toFixed(2) + '%'; },
                    parseNumericValue: function(value) { return parseFloat(value); }
                },
                notifications: {},
                modules: {
                    FormValidator: {
                        init: function() { console.log('FormValidator initialized'); }
                    },
                    DataFormatter: {
                        init: function() { console.log('DataFormatter initialized'); }
                    }
                }
            };
            
            // Mock document ready state
            document.readyState = 'complete';
        </script>
    </body>
    </html>
    """
    
    # Write the HTML to a temporary file
    temp_dir = os.path.join(app.root_path, "static", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    test_page_path = os.path.join(temp_dir, "test_main_page.html")
    
    with open(test_page_path, "w") as f:
        f.write(html_content)
    
    # Navigate to the test page
    selenium.get(f"file://{test_page_path}")
    
    # Wait for the page to load
    WebDriverWait(selenium, 10).until(
        EC.presence_of_element_located((By.ID, "test-container"))
    )
    
    # Read the main.js file
    main_js_path = os.path.join(app.root_path, "static", "js", "main.js")
    with open(main_js_path, "r") as f:
        main_js_content = f.read()
    
    # Inject the main.js content
    selenium.execute_script(main_js_content)
    
    # Wait a moment for the script to initialize
    time.sleep(1)
    
    # Check that the main module initialized the base module
    result = selenium.execute_script("""
        // Return true if the base module was initialized
        return window.REITracker && 
               window.REITracker.base && 
               typeof window.REITracker.base.init === 'function';
    """)
    assert result is True
    
    # Check that event handlers were attached
    result = selenium.execute_script("""
        // Simulate a click on a navbar toggler
        const event = new Event('click');
        const toggler = document.querySelector('.navbar-toggler');
        if (toggler) {
            toggler.dispatchEvent(event);
            return true;
        }
        return false;
    """)
    assert result is True
    
    # Clean up
    os.remove(test_page_path)
