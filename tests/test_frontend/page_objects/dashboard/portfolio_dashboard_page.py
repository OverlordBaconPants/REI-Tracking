"""
Portfolio dashboard page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class PortfolioDashboardPage(BasePage):
    """Page object for the portfolio dashboard page."""
    
    # Locators
    DASHBOARD_TITLE = (By.CSS_SELECTOR, "h1.dashboard-title")
    PORTFOLIO_VALUE_CARD = (By.ID, "portfolio-value-card")
    PORTFOLIO_VALUE = (By.ID, "portfolio-value")
    TOTAL_EQUITY_CARD = (By.ID, "total-equity-card")
    TOTAL_EQUITY = (By.ID, "total-equity")
    MONTHLY_CASHFLOW_CARD = (By.ID, "monthly-cashflow-card")
    MONTHLY_CASHFLOW = (By.ID, "monthly-cashflow")
    PROPERTY_TABLE = (By.ID, "property-table")
    PROPERTY_ROWS = (By.CSS_SELECTOR, "#property-table tbody tr")
    TIME_PERIOD_DROPDOWN = (By.ID, "time-period-dropdown")
    TIME_PERIOD_OPTIONS = (By.CSS_SELECTOR, "#time-period-dropdown .dropdown-item")
    
    def __init__(self, driver):
        """Initialize the portfolio dashboard page object."""
        super().__init__(driver)
        self.url = "/main/portfolio"
    
    def get_dashboard_title(self):
        """Get the dashboard title text."""
        return self.get_text(self.DASHBOARD_TITLE)
    
    def get_portfolio_value(self):
        """Get the portfolio value text."""
        return self.get_text(self.PORTFOLIO_VALUE)
    
    def get_total_equity(self):
        """Get the total equity text."""
        return self.get_text(self.TOTAL_EQUITY)
    
    def get_monthly_cashflow(self):
        """Get the monthly cashflow text."""
        return self.get_text(self.MONTHLY_CASHFLOW)
    
    def get_property_count(self):
        """Get the number of properties in the table."""
        return len(self.find_elements(self.PROPERTY_ROWS))
    
    def select_time_period(self, period):
        """
        Select a time period from the dropdown.
        
        Args:
            period: Time period to select (e.g., "30 days", "90 days", "6 months", "12 months", "All time")
            
        Returns:
            Self for method chaining
        """
        self.wait_and_click(self.TIME_PERIOD_DROPDOWN)
        
        # Find the option with the matching text
        options = self.find_elements(self.TIME_PERIOD_OPTIONS)
        for option in options:
            if period.lower() in option.text.lower():
                option.click()
                break
        
        # Wait for the dashboard to update
        self.wait_for_page_load()
        return self
    
    def is_dashboard_loaded(self):
        """Check if the dashboard is loaded."""
        return (self.is_element_visible(self.DASHBOARD_TITLE) and
                self.is_element_visible(self.PORTFOLIO_VALUE_CARD) and
                self.is_element_visible(self.PROPERTY_TABLE))
    
    def click_property_row(self, property_name):
        """
        Click on a property row in the table.
        
        Args:
            property_name: Name of the property to click
            
        Returns:
            PropertyDetailPage object
        """
        property_row = self.find_property_row(property_name)
        if property_row:
            property_row.click()
            from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
            return PropertyDetailPage(self.driver)
        raise Exception(f"Property {property_name} not found in table")
    
    def find_property_row(self, property_name):
        """
        Find a property row in the table.
        
        Args:
            property_name: Name of the property to find
            
        Returns:
            WebElement if found, None otherwise
        """
        rows = self.find_elements(self.PROPERTY_ROWS)
        for row in rows:
            if property_name in row.text:
                return row
        return None
    
    def is_property_listed(self, property_name):
        """
        Check if a property is listed in the table.
        
        Args:
            property_name: Name of the property to check
            
        Returns:
            True if the property is listed, False otherwise
        """
        return self.find_property_row(property_name) is not None
