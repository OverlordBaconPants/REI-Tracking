"""
Pytest configuration for frontend tests.

This module contains fixtures and configuration for testing frontend JavaScript components.
"""

import pytest
import os
import time
from flask import Flask, url_for, render_template_string
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
    # Create a new Flask application for testing to avoid context issues
    test_app = Flask(__name__)
    test_app.config.update({
        "TESTING": True,
        "SERVER_NAME": "localhost.localdomain",
        "SECRET_KEY": "test-key"
    })
    
    # Configure the app to use the templates from the test directory first, then fall back to the main application
    test_app.template_folder = os.path.join(os.path.dirname(__file__), 'templates')
    test_app.static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'static')
    
    # Add a jinja loader that looks in both the test templates and the main application templates
    from jinja2 import ChoiceLoader, FileSystemLoader
    test_app.jinja_loader = ChoiceLoader([
        FileSystemLoader(test_app.template_folder),
        FileSystemLoader(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'templates'))
    ])
    
    # Add a simple route for testing
    @test_app.route('/')
    def index():
        return render_template_string('''
            {% extends "base.html" %}
            {% block title %}Test Page{% endblock %}
            {% block content %}
                <h1>Test Page</h1>
                <p>This is a test page for frontend testing.</p>
            {% endblock %}
        ''')
    
    # Add a route for flash messages testing
    @test_app.route('/flash-test')
    def flash_test():
        # Add flash messages directly in the route
        from flask import flash
        flash('Test success message', 'success')
        flash('Test error message', 'error')
        
        return render_template_string('''
            {% extends "base.html" %}
            {% block title %}Flash Test{% endblock %}
            {% block content %}
                <h1>Flash Test</h1>
            {% endblock %}
        ''')
    
    # Add a route for block structure testing
    @test_app.route('/block-test')
    def block_test():
        return render_template_string('''
            {% extends "base.html" %}
            {% block title %}Custom Title{% endblock %}
            {% block styles %}
                <meta name="test" content="test-value">
            {% endblock %}
            {% block content %}
                <h1>Custom Content</h1>
            {% endblock %}
            {% block extra_js %}
                <script>console.log('Custom script');</script>
            {% endblock %}
        ''')
    
    # Create an application context
    with test_app.app_context():
        yield test_app


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
def test_page(app):
    """Get the path to the test HTML page with the required JavaScript files."""
    # Use the template from the test_frontend/templates directory
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'test_page.html')
    
    # Ensure the template exists
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Test page template not found at {template_path}")
    
    return template_path


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
        
        # Inject each script
        for script in scripts:
            # Read the script content
            # First, try to find the script in the test directory
            test_script_path = os.path.join(os.path.dirname(__file__), 'static', 'js', script)
            
            # If not found in test directory, fall back to the main application's static folder
            if os.path.exists(test_script_path):
                script_path = test_script_path
            else:
                # Check if the path already includes 'js/' prefix
                if not script.startswith('js/'):
                    script_path = os.path.join(app.static_folder, 'js', script)
                else:
                    script_path = os.path.join(app.static_folder, script)
            
            try:
                with open(script_path, "r") as f:
                    script_content = f.read()
                
                # Print the script content for debugging
                print(f"Script content for {script}:")
                print(script_content[:200] + "..." if len(script_content) > 200 else script_content)
                
                # Inject the script directly
                selenium.execute_script(script_content)
                print(f"Directly executed script: {script}")
                
                # Check if baseModule is defined
                result = selenium.execute_script("return typeof window.baseModule !== 'undefined'")
                print(f"baseModule defined after direct execution: {result}")
                
                if result:
                    # Get the properties of baseModule
                    properties = selenium.execute_script("return Object.keys(window.baseModule)")
                    print(f"baseModule properties after direct execution: {properties}")
                
                # Give the script time to execute
                time.sleep(0.5)
            except Exception as e:
                print(f"Error loading script {script}: {e}")
                raise
        
        return selenium
    
    return _inject_scripts
