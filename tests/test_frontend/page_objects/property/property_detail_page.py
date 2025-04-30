"""
Property detail page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class PropertyDetailPage(BasePage):
    """Page object for the property detail page."""
    
    # Locators
    PROPERTY_NAME = (By.ID, "property-name")
    PROPERTY_ADDRESS = (By.ID, "property-address")
    PROPERTY_DETAILS_TAB = (By.ID, "property-details-tab")
    FINANCIAL_TAB = (By.ID, "financial-tab")
    TRANSACTIONS_TAB = (By.ID, "transactions-tab")
    PARTNERS_TAB = (By.ID, "partners-tab")
    ANALYSIS_TAB = (By.ID, "analysis-tab")
    DOCUMENTS_TAB = (By.ID, "documents-tab")
    
    # Property details section
    PURCHASE_PRICE = (By.ID, "purchase-price")
    PURCHASE_DATE = (By.ID, "purchase-date")
    BEDROOMS = (By.ID, "bedrooms")
    BATHROOMS = (By.ID, "bathrooms")
    SQUARE_FEET = (By.ID, "square-feet")
    
    # Financial section
    MONTHLY_RENT = (By.ID, "monthly-rent")
    MONTHLY_EXPENSES = (By.ID, "monthly-expenses")
    MONTHLY_CASHFLOW = (By.ID, "monthly-cashflow")
    CASH_ON_CASH_RETURN = (By.ID, "cash-on-cash-return")
    CAP_RATE = (By.ID, "cap-rate")
    
    # Partners section
    PARTNER_TABLE = (By.ID, "partner-table")
    PARTNER_ROWS = (By.CSS_SELECTOR, "#partner-table tbody tr")
    ADD_PARTNER_BUTTON = (By.ID, "add-partner-button")
    
    # Edit buttons
    EDIT_PROPERTY_BUTTON = (By.ID, "edit-property-button")
    DELETE_PROPERTY_BUTTON = (By.ID, "delete-property-button")
    
    def __init__(self, driver):
        """Initialize the property detail page object."""
        super().__init__(driver)
        # The URL will be set dynamically based on the property ID
        self.url = None
    
    def get_property_name(self):
        """Get the property name text."""
        return self.get_text(self.PROPERTY_NAME)
    
    def get_property_address(self):
        """Get the property address text."""
        return self.get_text(self.PROPERTY_ADDRESS)
    
    def click_property_details_tab(self):
        """Click the property details tab."""
        self.wait_and_click(self.PROPERTY_DETAILS_TAB)
        return self
    
    def click_financial_tab(self):
        """Click the financial tab."""
        self.wait_and_click(self.FINANCIAL_TAB)
        return self
    
    def click_transactions_tab(self):
        """Click the transactions tab."""
        self.wait_and_click(self.TRANSACTIONS_TAB)
        return self
    
    def click_partners_tab(self):
        """Click the partners tab."""
        self.wait_and_click(self.PARTNERS_TAB)
        return self
    
    def click_analysis_tab(self):
        """Click the analysis tab."""
        self.wait_and_click(self.ANALYSIS_TAB)
        return self
    
    def click_documents_tab(self):
        """Click the documents tab."""
        self.wait_and_click(self.DOCUMENTS_TAB)
        return self
    
    def get_purchase_price(self):
        """Get the purchase price text."""
        return self.get_text(self.PURCHASE_PRICE)
    
    def get_purchase_date(self):
        """Get the purchase date text."""
        return self.get_text(self.PURCHASE_DATE)
    
    def get_bedrooms(self):
        """Get the bedrooms text."""
        return self.get_text(self.BEDROOMS)
    
    def get_bathrooms(self):
        """Get the bathrooms text."""
        return self.get_text(self.BATHROOMS)
    
    def get_square_feet(self):
        """Get the square feet text."""
        return self.get_text(self.SQUARE_FEET)
    
    def get_monthly_rent(self):
        """Get the monthly rent text."""
        self.click_financial_tab()
        return self.get_text(self.MONTHLY_RENT)
    
    def get_monthly_expenses(self):
        """Get the monthly expenses text."""
        self.click_financial_tab()
        return self.get_text(self.MONTHLY_EXPENSES)
    
    def get_monthly_cashflow(self):
        """Get the monthly cashflow text."""
        self.click_financial_tab()
        return self.get_text(self.MONTHLY_CASHFLOW)
    
    def get_cash_on_cash_return(self):
        """Get the cash on cash return text."""
        self.click_financial_tab()
        return self.get_text(self.CASH_ON_CASH_RETURN)
    
    def get_cap_rate(self):
        """Get the cap rate text."""
        self.click_financial_tab()
        return self.get_text(self.CAP_RATE)
    
    def get_partner_count(self):
        """Get the number of partners in the table."""
        self.click_partners_tab()
        return len(self.find_elements(self.PARTNER_ROWS))
    
    def click_add_partner(self):
        """Click the add partner button."""
        self.click_partners_tab()
        self.wait_and_click(self.ADD_PARTNER_BUTTON)
        from tests.test_frontend.page_objects.property.add_partner_modal import AddPartnerModal
        return AddPartnerModal(self.driver)
    
    def click_edit_property(self):
        """Click the edit property button."""
        self.wait_and_click(self.EDIT_PROPERTY_BUTTON)
        from tests.test_frontend.page_objects.property.property_edit_page import PropertyEditPage
        return PropertyEditPage(self.driver)
    
    def click_delete_property(self):
        """Click the delete property button."""
        self.wait_and_click(self.DELETE_PROPERTY_BUTTON)
        from tests.test_frontend.page_objects.components.modals import ConfirmModal
        return ConfirmModal(self.driver)
    
    def navigate_to_property_list(self):
        """Navigate to the property list page."""
        from tests.test_frontend.page_objects.property.property_list_page import PropertyListPage
        property_list_page = PropertyListPage(self.driver)
        property_list_page.navigate_to()
        return property_list_page
    
    def navigate_to_transactions_tab(self):
        """Navigate to the transactions tab."""
        self.click_transactions_tab()
        from tests.test_frontend.page_objects.transaction.property_transactions_page import PropertyTransactionsPage
        return PropertyTransactionsPage(self.driver)
    
    def navigate_to_partners_tab(self):
        """Navigate to the partners tab."""
        self.click_partners_tab()
        from tests.test_frontend.page_objects.property.property_partners_tab import PropertyPartnersTab
        return PropertyPartnersTab(self.driver)
    
    def navigate_to_analysis_tab(self):
        """Navigate to the analysis tab."""
        self.click_analysis_tab()
        from tests.test_frontend.page_objects.analysis.property_analysis_page import PropertyAnalysisPage
        return PropertyAnalysisPage(self.driver)
