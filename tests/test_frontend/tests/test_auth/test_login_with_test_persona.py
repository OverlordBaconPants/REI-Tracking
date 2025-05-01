"""
Example test demonstrating how to use the test persona for authentication.
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.test_frontend.base.base_test import BaseTest
from tests.test_frontend.workflows.auth_workflows import AuthWorkflows
from tests.test_frontend.test_data.test_persona import TEST_USER


class TestLoginWithTestPersona(BaseTest):
    """Test class demonstrating how to use the test persona for authentication."""
    
    def test_login_with_test_persona(self, browser, logger):
        """
        Test logging in with the test persona credentials.
        
        This test demonstrates how to use the test persona for authentication
        in UI tests. It uses the AuthWorkflows.login_as_test_user method to
        log in with the test persona credentials.
        """
        # Login as the test user
        dashboard_page = AuthWorkflows.login_as_test_user(browser, logger=logger)
        
        # Verify login was successful
        assert "/main" in browser.current_url, "Login failed, not redirected to dashboard"
        
        # Verify user name is displayed in the navigation
        user_dropdown = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "user-dropdown"))
        )
        assert f"{TEST_USER['first_name']} {TEST_USER['last_name']}" in user_dropdown.text
        
        # Logout
        login_page = AuthWorkflows.logout(browser, logger=logger)
        
        # Verify logout was successful
        assert login_page.is_login_page(), "Logout failed, not redirected to login page"
