"""
Shared pytest fixtures for frontend tests.
"""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture
def browser(request):
    """Fixture for WebDriver instance."""
    browser_name = os.environ.get("BROWSER", "chrome")
    headless = os.environ.get("HEADLESS", "true").lower() == "true"
    device = os.environ.get("DEVICE", "desktop")
    
    if browser_name.lower() == "chrome":
        options = Options()
        if headless:
            options.add_argument("--headless")
        
        # Set device emulation
        if device != "desktop":
            device_metrics = {
                "tablet": {"width": 1024, "height": 768, "pixelRatio": 2.0},
                "mobile": {"width": 375, "height": 812, "pixelRatio": 3.0}
            }
            metrics = device_metrics.get(device)
            options.add_experimental_option("mobileEmulation", {
                "deviceMetrics": metrics
            })
        
        driver = webdriver.Chrome(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    
    driver.maximize_window()
    
    yield driver
    
    driver.quit()

@pytest.fixture(scope="session")
def base_url():
    """Fixture for base URL."""
    return "http://localhost:5000"

@pytest.fixture(scope="session")
def test_user():
    """Fixture for test user credentials."""
    return {
        "email": "test_user@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }

def pytest_configure(config):
    """Configure pytest metadata."""
    pass
