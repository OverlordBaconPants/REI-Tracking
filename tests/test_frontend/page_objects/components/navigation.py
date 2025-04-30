"""
Navigation component page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class NavigationComponent(BasePage):
    """Page object for the navigation component."""
    
    # Locators
    USER_DROPDOWN = (By.ID, "user-dropdown")
    LOGOUT_LINK = (By.ID, "logout-link")
    PROFILE_LINK = (By.ID, "profile-link")
    DASHBOARD_LINK = (By.ID, "dashboard-link")
    PROPERTIES_LINK = (By.ID, "properties-link")
    TRANSACTIONS_LINK = (By.ID, "transactions-link")
    ANALYSES_LINK = (By.ID, "analyses-link")
    
    def __init__(self, driver):
        """Initialize the navigation component."""
        super().__init__(driver)
    
    def click_user_dropdown(self):
        """Click the user dropdown."""
        self.wait_and_click(self.USER_DROPDOWN)
        return self
    
    def click_logout(self):
        """Click the logout link."""
        self.wait_and_click(self.LOGOUT_LINK)
        from tests.test_frontend.page_objects.login_page import LoginPage
        return LoginPage(self.driver)
    
    def click_profile(self):
        """Click the profile link."""
        self.click_user_dropdown()
        self.wait_and_click(self.PROFILE_LINK)
        from tests.test_frontend.page_objects.profile_page import ProfilePage
        return ProfilePage(self.driver)
    
    def click_dashboard(self):
        """Click the dashboard link."""
        self.wait_and_click(self.DASHBOARD_LINK)
        from tests.test_frontend.page_objects.dashboard.portfolio_dashboard_page import PortfolioDashboardPage
        return PortfolioDashboardPage(self.driver)
    
    def click_properties(self):
        """Click the properties link."""
        self.wait_and_click(self.PROPERTIES_LINK)
        from tests.test_frontend.page_objects.property.property_list_page import PropertyListPage
        return PropertyListPage(self.driver)
    
    def click_transactions(self):
        """Click the transactions link."""
        self.wait_and_click(self.TRANSACTIONS_LINK)
        from tests.test_frontend.page_objects.transaction.transaction_list_page import TransactionListPage
        return TransactionListPage(self.driver)
    
    def click_analyses(self):
        """Click the analyses link."""
        self.wait_and_click(self.ANALYSES_LINK)
        from tests.test_frontend.page_objects.analysis.analysis_list_page import AnalysisListPage
        return AnalysisListPage(self.driver)
    
    def is_user_logged_in(self):
        """Check if a user is logged in."""
        return self.is_element_visible(self.USER_DROPDOWN)
    
    def get_username(self):
        """Get the username displayed in the navigation."""
        if self.is_user_logged_in():
            return self.get_text(self.USER_DROPDOWN)
        return None
