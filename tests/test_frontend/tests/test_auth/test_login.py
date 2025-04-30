"""
Tests for login functionality.
"""
import pytest
from selenium.webdriver.common.by import By
from tests.test_frontend.base.base_test import BaseTest
from tests.test_frontend.page_objects.login_page import LoginPage
from tests.test_frontend.base.logger import TestLogger

class TestLogin(BaseTest):
    """Test cases for login functionality."""
    
    def setup_method(self):
        """Set up the test."""
        self.logger = TestLogger.setup_logging()
        TestLogger.log_test_start(self.logger, self._testMethodName)
        self.login_page = LoginPage(self.driver)
    
    def teardown_method(self):
        """Tear down the test."""
        TestLogger.log_test_end(self.logger, self._testMethodName)
    
    def test_successful_login(self, test_user):
        """Test successful login with valid credentials."""
        TestLogger.log_step(self.logger, "Navigate to login page")
        self.login_page.navigate_to()
        
        TestLogger.log_step(self.logger, "Enter valid credentials and submit")
        dashboard_page = self.login_page.login(
            test_user["email"], 
            test_user["password"]
        )
        
        TestLogger.log_step(self.logger, "Verify redirect to dashboard")
        self.assert_url_contains("/main")
        
        TestLogger.log_step(self.logger, "Verify user is logged in")
        user_dropdown = (By.ID, "user-dropdown")
        self.assert_element_displayed(user_dropdown)
    
    def test_failed_login_invalid_password(self, test_user):
        """Test failed login with invalid password."""
        TestLogger.log_step(self.logger, "Navigate to login page")
        self.login_page.navigate_to()
        
        TestLogger.log_step(self.logger, "Enter invalid credentials and submit")
        self.login_page.login(
            test_user["email"], 
            "wrong_password"
        )
        
        TestLogger.log_step(self.logger, "Verify error message")
        error_message = self.login_page.get_error_message()
        assert error_message is not None
        assert "Invalid" in error_message or "incorrect" in error_message.lower()
        
        TestLogger.log_step(self.logger, "Verify still on login page")
        assert self.login_page.is_login_page()
    
    def test_failed_login_invalid_email(self):
        """Test failed login with invalid email."""
        TestLogger.log_step(self.logger, "Navigate to login page")
        self.login_page.navigate_to()
        
        TestLogger.log_step(self.logger, "Enter invalid credentials and submit")
        self.login_page.login(
            "nonexistent@example.com", 
            "password123"
        )
        
        TestLogger.log_step(self.logger, "Verify error message")
        error_message = self.login_page.get_error_message()
        assert error_message is not None
        assert "Invalid" in error_message or "not found" in error_message.lower()
        
        TestLogger.log_step(self.logger, "Verify still on login page")
        assert self.login_page.is_login_page()
    
    def test_remember_me_functionality(self, test_user):
        """Test remember me functionality."""
        TestLogger.log_step(self.logger, "Navigate to login page")
        self.login_page.navigate_to()
        
        TestLogger.log_step(self.logger, "Login with remember me checked")
        dashboard_page = self.login_page.login(
            test_user["email"], 
            test_user["password"],
            remember_me=True
        )
        
        TestLogger.log_step(self.logger, "Verify redirect to dashboard")
        self.assert_url_contains("/main")
        
        TestLogger.log_step(self.logger, "Verify remember me cookie is set")
        remember_cookie = self.driver.get_cookie("remember_token")
        assert remember_cookie is not None
    
    def test_navigation_to_forgot_password(self):
        """Test navigation to forgot password page."""
        TestLogger.log_step(self.logger, "Navigate to login page")
        self.login_page.navigate_to()
        
        TestLogger.log_step(self.logger, "Click forgot password link")
        forgot_password_page = self.login_page.click_forgot_password()
        
        TestLogger.log_step(self.logger, "Verify navigation to forgot password page")
        self.assert_url_contains("/forgot_password")
    
    def test_navigation_to_signup(self):
        """Test navigation to signup page."""
        TestLogger.log_step(self.logger, "Navigate to login page")
        self.login_page.navigate_to()
        
        TestLogger.log_step(self.logger, "Click signup link")
        signup_page = self.login_page.click_signup()
        
        TestLogger.log_step(self.logger, "Verify navigation to signup page")
        self.assert_url_contains("/signup")
