"""
Base class for all UI tests.
"""
import os
import pytest
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BaseTest:
    """Base class for all UI tests."""
    
    @pytest.fixture(autouse=True)
    def setup(self, browser, base_url):
        """Set up the test environment."""
        self.driver = browser
        self.base_url = base_url
        self.wait = WebDriverWait(self.driver, 10)
        
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        
        yield
        
        # Post-test cleanup
        # (Database reset, etc. can be added here)
    
    def take_screenshot(self, name):
        """Take a screenshot for debugging."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{name}_{timestamp}.png"
        filepath = os.path.join("screenshots", filename)
        self.driver.save_screenshot(filepath)
        return filepath
    
    def assert_notification(self, expected_text, expected_type="success"):
        """Assert that a notification is displayed with the expected text and type."""
        from tests.test_frontend.page_objects.components.notifications import NotificationComponent
        notification = NotificationComponent(self.driver)
        assert notification.is_visible(), "Notification is not visible"
        assert expected_text in notification.get_text(), f"Expected text '{expected_text}' not found in notification"
        assert notification.get_type() == expected_type, f"Expected notification type '{expected_type}' but got '{notification.get_type()}'"
    
    def assert_url_contains(self, expected_path):
        """Assert that the current URL contains the expected path."""
        current_url = self.driver.current_url
        assert expected_path in current_url, f"Expected URL to contain '{expected_path}', but got '{current_url}'"
    
    def assert_element_text(self, locator, expected_text):
        """Assert that an element contains the expected text."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        actual_text = element.text
        assert expected_text in actual_text, f"Expected text '{expected_text}' not found in element text '{actual_text}'"
    
    def assert_element_attribute(self, locator, attribute, expected_value):
        """Assert that an element has the expected attribute value."""
        element = self.wait.until(EC.presence_of_element_located(locator))
        actual_value = element.get_attribute(attribute)
        assert expected_value in actual_value, f"Expected attribute '{attribute}' to contain '{expected_value}', but got '{actual_value}'"
    
    def assert_element_displayed(self, locator):
        """Assert that an element is displayed."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        assert element.is_displayed(), f"Element {locator} is not displayed"
    
    def assert_element_not_displayed(self, locator):
        """Assert that an element is not displayed."""
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        try:
            self.wait.until(EC.visibility_of_element_located(locator))
            assert False, f"Element {locator} is displayed but should not be"
        except (TimeoutException, NoSuchElementException):
            pass
