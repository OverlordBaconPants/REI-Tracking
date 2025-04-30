"""
Login page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class LoginPage(BasePage):
    """Page object for the login page."""
    
    # Locators
    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    REMEMBER_ME_CHECKBOX = (By.ID, "remember")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgot Password?")
    SIGNUP_LINK = (By.LINK_TEXT, "Sign up")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    
    def __init__(self, driver):
        """Initialize the login page object."""
        super().__init__(driver)
        self.url = "/login"
    
    def login(self, email, password, remember_me=False):
        """
        Login with the provided credentials.
        
        Args:
            email: User email
            password: User password
            remember_me: Whether to check the "Remember Me" checkbox
            
        Returns:
            The dashboard page object if login is successful
        """
        self.wait_and_send_keys(self.EMAIL_INPUT, email)
        self.wait_and_send_keys(self.PASSWORD_INPUT, password)
        
        if remember_me:
            self.wait_and_click(self.REMEMBER_ME_CHECKBOX)
        
        self.wait_and_click(self.LOGIN_BUTTON)
        
        # Check if login was successful by looking for the dashboard URL
        if "/main" in self.driver.current_url:
            from tests.test_frontend.page_objects.dashboard.portfolio_dashboard_page import PortfolioDashboardPage
            return PortfolioDashboardPage(self.driver)
        
        # If login failed, return self
        return self
    
    def click_forgot_password(self):
        """Click the forgot password link."""
        self.wait_and_click(self.FORGOT_PASSWORD_LINK)
        from tests.test_frontend.page_objects.forgot_password_page import ForgotPasswordPage
        return ForgotPasswordPage(self.driver)
    
    def click_signup(self):
        """Click the signup link."""
        self.wait_and_click(self.SIGNUP_LINK)
        from tests.test_frontend.page_objects.signup_page import SignupPage
        return SignupPage(self.driver)
    
    def get_error_message(self):
        """Get the error message text."""
        if self.is_element_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return None
    
    def is_login_page(self):
        """Check if this is the login page."""
        return "/login" in self.driver.current_url and self.is_element_visible(self.LOGIN_BUTTON)
