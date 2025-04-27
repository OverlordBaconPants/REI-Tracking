"""
Pytest configuration for frontend tests.

This module contains fixtures and configuration for testing frontend JavaScript components.
"""

import pytest
import os
import time
from flask import Flask, url_for
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from src.main import application


@pytest.fixture(scope="session")
def app():
    """Configure the Flask app for the tests."""
    # Configure the existing application for testing
    application.config.update({
        "TESTING": True,
        "SERVER_NAME": "localhost.localdomain",
    })
    
    # Create an application context
    with application.app_context():
        yield application


@pytest.fixture(scope="session")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="session")
def chrome_options():
    """Chrome options for the Selenium WebDriver."""
    options = Options()
    
    # Check if headless mode is enabled (default is True)
    headless = os.environ.get('HEADLESS', 'true').lower() == 'true'
    if headless:
        options.add_argument("--headless")
    
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return options


@pytest.fixture(scope="function")
def selenium(chrome_options):
    """Selenium WebDriver with Chrome or Firefox."""
    browser_name = os.environ.get('PYTEST_BROWSER', 'chrome').lower()
    
    if browser_name == 'chrome':
        service = Service(ChromeDriverManager().install())
        driver = WebDriver(service=service, options=chrome_options)
    else:
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from webdriver_manager.firefox import GeckoDriverManager
        
        firefox_options = FirefoxOptions()
        headless = os.environ.get('HEADLESS', 'true').lower() == 'true'
        if headless:
            firefox_options.add_argument("--headless")
        
        service = FirefoxService(GeckoDriverManager().install())
        driver = selenium.webdriver.Firefox(service=service, options=firefox_options)
    
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def test_page(tmpdir):
    """Create a test HTML page with the required JavaScript files."""
    # Create a simple HTML page that includes our JavaScript files
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>JavaScript Test Page</title>
        <link href="https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/spacelab/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.css" rel="stylesheet">
    </head>
    <body>
        <div id="test-container">
            <!-- Test content will be added here -->
            <div id="notification-test"></div>
            <div id="form-test">
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
            <div id="data-test">
                <div id="chart-container" data-chart="bar" data-chart-data='{"labels":["A","B","C"],"datasets":[{"label":"Test","data":[1,2,3]}]}'>
                </div>
                <div id="table-container" data-table data-table-data='{"headers":[{"key":"name","label":"Name"},{"key":"value","label":"Value"}],"rows":[{"name":"Test","value":123}]}'>
                </div>
            </div>
        </div>

        <!-- JavaScript Dependencies -->
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        
        <!-- Test scripts will be injected here -->
        <script id="test-scripts"></script>
    </body>
    </html>
    """
    
    # Write the HTML to a temporary file
    test_page = tmpdir.join("test_page.html")
    test_page.write(html_content)
    
    return str(test_page)


@pytest.fixture(scope="function")
def inject_scripts(selenium, test_page, app):
    """Inject JavaScript files into the test page and navigate to it."""
    def _inject_scripts(scripts):
        # Navigate to the test page
        selenium.get(f"file://{test_page}")
        
        # Wait for the page to load
        WebDriverWait(selenium, 10).until(
            EC.presence_of_element_located((By.ID, "test-container"))
        )
        
        # Mock required libraries BEFORE loading any scripts
        selenium.execute_script("""
            // Mock jQuery if not available
            if (typeof jQuery === 'undefined') {
                window.jQuery = window.$ = function(selector) {
                    return {
                        on: function() { return this; },
                        off: function() { return this; },
                        addClass: function() { return this; },
                        removeClass: function() { return this; },
                        attr: function() { return this; },
                        data: function() { return {}; },
                        each: function(callback) { callback.call(this); return this; },
                        val: function() { return ''; },
                        text: function() { return ''; },
                        html: function() { return ''; },
                        append: function() { return this; },
                        prepend: function() { return this; },
                        find: function() { return this; },
                        parent: function() { return this; },
                        parents: function() { return this; },
                        closest: function() { return this; },
                        is: function() { return false; },
                        trigger: function() { return this; }
                    };
                };
            }
            
            // Mock lodash if not available
            if (typeof _ === 'undefined') {
                window._ = {
                    debounce: function(func, wait) {
                        return function() {
                            return func.apply(this, arguments);
                        };
                    },
                    throttle: function(func, wait) {
                        return function() {
                            return func.apply(this, arguments);
                        };
                    },
                    templateSettings: {
                        interpolate: null
                    }
                };
            }
            
            // Mock toastr
            window.toastr = {
                options: {},
                success: function(message, title, options) { return { options: options || {} }; },
                error: function(message, title, options) { return { options: options || {} }; },
                warning: function(message, title, options) { return { options: options || {} }; },
                info: function(message, title, options) { return { options: options || {} }; }
            };
            
            // Mock bootstrap
            window.bootstrap = {
                Tooltip: function(element, options) {
                    this.dispose = function() {};
                    return this;
                },
                Collapse: function() {
                    this.hide = function() {};
                    return this;
                },
                Popover: function() {
                    return this;
                }
            };
            bootstrap.Tooltip.getInstance = function() { return { dispose: function() {} }; };
            bootstrap.Collapse.getInstance = function() { return { hide: function() {} }; };
            
            // Create REITracker namespace
            window.REITracker = {
                base: {},
                notifications: {},
                modules: {}
            };
        """)
        
        # Inject each script
        for script in scripts:
            # Read the script content
            script_path = os.path.join(app.root_path, "static", "js", script)
            with open(script_path, "r") as f:
                script_content = f.read()
            
            # Inject the script
            selenium.execute_script(f"""
                var script = document.createElement('script');
                script.textContent = `{script_content}`;
                document.head.appendChild(script);
            """)
            
            # Give the script time to execute
            time.sleep(0.5)
        
        return selenium
    
    return _inject_scripts
