"""
Authentication workflow utilities.
"""
from tests.test_frontend.page_objects.login_page import LoginPage
from tests.test_frontend.base.logger import TestLogger

class AuthWorkflows:
    """Authentication workflow utilities."""
    
    @staticmethod
    def login(driver, email, password, remember_me=False, logger=None):
        """
        Login workflow.
        
        Args:
            driver: WebDriver instance
            email: User email
            password: User password
            remember_me: Whether to check the "Remember Me" checkbox
            logger: Optional logger instance
            
        Returns:
            The dashboard page object if login is successful, otherwise the login page
        """
        if logger:
            TestLogger.log_step(logger, "Login workflow started")
        
        login_page = LoginPage(driver)
        
        if logger:
            TestLogger.log_step(logger, "Navigate to login page")
        login_page.navigate_to()
        
        if logger:
            TestLogger.log_step(logger, f"Login with email: {email}")
        result_page = login_page.login(email, password, remember_me)
        
        if "/main" in driver.current_url:
            if logger:
                TestLogger.log_step(logger, "Login successful")
            return result_page
        else:
            if logger:
                TestLogger.log_step(logger, "Login failed")
                error_message = login_page.get_error_message()
                if error_message:
                    TestLogger.log_step(logger, f"Error message: {error_message}")
            return login_page
    
    @staticmethod
    def logout(driver, logger=None):
        """
        Logout workflow.
        
        Args:
            driver: WebDriver instance
            logger: Optional logger instance
            
        Returns:
            The login page object
        """
        from selenium.webdriver.common.by import By
        from tests.test_frontend.page_objects.components.navigation import NavigationComponent
        
        if logger:
            TestLogger.log_step(logger, "Logout workflow started")
        
        # Use the navigation component to logout
        nav = NavigationComponent(driver)
        
        if logger:
            TestLogger.log_step(logger, "Click user dropdown")
        nav.click_user_dropdown()
        
        if logger:
            TestLogger.log_step(logger, "Click logout")
        nav.click_logout()
        
        # Return the login page
        login_page = LoginPage(driver)
        
        if logger:
            TestLogger.log_step(logger, "Verify redirect to login page")
            if login_page.is_login_page():
                TestLogger.log_step(logger, "Logout successful")
            else:
                TestLogger.log_step(logger, "Logout failed")
        
        return login_page
    
    @staticmethod
    def register(driver, email, password, first_name, last_name, logger=None):
        """
        Registration workflow.
        
        Args:
            driver: WebDriver instance
            email: User email
            password: User password
            first_name: User first name
            last_name: User last name
            logger: Optional logger instance
            
        Returns:
            The dashboard page object if registration is successful, otherwise the signup page
        """
        from tests.test_frontend.page_objects.signup_page import SignupPage
        
        if logger:
            TestLogger.log_step(logger, "Registration workflow started")
        
        signup_page = SignupPage(driver)
        
        if logger:
            TestLogger.log_step(logger, "Navigate to signup page")
        signup_page.navigate_to()
        
        if logger:
            TestLogger.log_step(logger, f"Register with email: {email}")
        result_page = signup_page.register(email, password, first_name, last_name)
        
        if "/main" in driver.current_url:
            if logger:
                TestLogger.log_step(logger, "Registration successful")
            return result_page
        else:
            if logger:
                TestLogger.log_step(logger, "Registration failed")
                error_message = signup_page.get_error_message()
                if error_message:
                    TestLogger.log_step(logger, f"Error message: {error_message}")
            return signup_page
    
    @staticmethod
    def forgot_password(driver, email, logger=None):
        """
        Forgot password workflow.
        
        Args:
            driver: WebDriver instance
            email: User email
            logger: Optional logger instance
            
        Returns:
            The forgot password page object
        """
        from tests.test_frontend.page_objects.forgot_password_page import ForgotPasswordPage
        
        if logger:
            TestLogger.log_step(logger, "Forgot password workflow started")
        
        forgot_password_page = ForgotPasswordPage(driver)
        
        if logger:
            TestLogger.log_step(logger, "Navigate to forgot password page")
        forgot_password_page.navigate_to()
        
        if logger:
            TestLogger.log_step(logger, f"Submit forgot password request for email: {email}")
        forgot_password_page.submit_forgot_password(email)
        
        if logger:
            success_message = forgot_password_page.get_success_message()
            if success_message:
                TestLogger.log_step(logger, f"Success message: {success_message}")
                TestLogger.log_step(logger, "Forgot password request successful")
            else:
                error_message = forgot_password_page.get_error_message()
                if error_message:
                    TestLogger.log_step(logger, f"Error message: {error_message}")
                    TestLogger.log_step(logger, "Forgot password request failed")
        
        return forgot_password_page
