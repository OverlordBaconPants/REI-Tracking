"""
Property list page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class PropertyListPage(BasePage):
    """Page object for the property list page."""
    
    # Locators
    ADD_PROPERTY_BUTTON = (By.ID, "add-property-btn")
    PROPERTY_TABLE = (By.ID, "property-table")
    PROPERTY_ROWS = (By.CSS_SELECTOR, "#property-table tbody tr")
    SEARCH_INPUT = (By.ID, "property-search")
    FILTER_DROPDOWN = (By.ID, "property-filter")
    SORT_DROPDOWN = (By.ID, "property-sort")
    
    def __init__(self, driver):
        """Initialize the property list page object."""
        super().__init__(driver)
        self.url = "/properties"
    
    def click_add_property(self):
        """Click the add property button."""
        self.wait_and_click(self.ADD_PROPERTY_BUTTON)
        from tests.test_frontend.page_objects.property.property_create_page import PropertyCreatePage
        return PropertyCreatePage(self.driver)
    
    def search_for_property(self, search_term):
        """
        Search for a property by name or address.
        
        Args:
            search_term: Search term to enter
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.SEARCH_INPUT, search_term)
        return self
    
    def filter_properties(self, filter_option):
        """
        Filter properties by option.
        
        Args:
            filter_option: Filter option to select
            
        Returns:
            Self for method chaining
        """
        from selenium.webdriver.support.ui import Select
        
        filter_element = self.wait_for_visibility(self.FILTER_DROPDOWN)
        select = Select(filter_element)
        select.select_by_visible_text(filter_option)
        return self
    
    def sort_properties(self, sort_option):
        """
        Sort properties by option.
        
        Args:
            sort_option: Sort option to select
            
        Returns:
            Self for method chaining
        """
        from selenium.webdriver.support.ui import Select
        
        sort_element = self.wait_for_visibility(self.SORT_DROPDOWN)
        select = Select(sort_element)
        select.select_by_visible_text(sort_option)
        return self
    
    def get_property_count(self):
        """Get the number of properties in the table."""
        return len(self.find_elements(self.PROPERTY_ROWS))
    
    def open_property_details(self, property_name):
        """
        Open property details for the specified property.
        
        Args:
            property_name: Name of the property to open
            
        Returns:
            PropertyDetailPage object
        """
        property_row = self.find_property_row(property_name)
        if property_row:
            property_row.find_element(By.CSS_SELECTOR, ".property-name a").click()
            from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
            return PropertyDetailPage(self.driver)
        raise Exception(f"Property {property_name} not found in table")
    
    def find_property_row(self, property_name):
        """
        Find the row containing the specified property.
        
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
    
    def select_property(self, property_name):
        """
        Select a property by clicking its checkbox.
        
        Args:
            property_name: Name of the property to select
            
        Returns:
            Self for method chaining
        """
        property_row = self.find_property_row(property_name)
        if property_row:
            checkbox = property_row.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
            checkbox.click()
            return self
        raise Exception(f"Property {property_name} not found in table")
    
    def click_delete_property(self):
        """
        Click the delete property button.
        
        Returns:
            ConfirmModal object
        """
        delete_button = (By.ID, "delete-selected-btn")
        self.wait_and_click(delete_button)
        from tests.test_frontend.page_objects.components.modals import ConfirmModal
        return ConfirmModal(self.driver)
    
    def click_edit_property(self):
        """
        Click the edit property button.
        
        Returns:
            PropertyEditPage object
        """
        edit_button = (By.ID, "edit-selected-btn")
        self.wait_and_click(edit_button)
        from tests.test_frontend.page_objects.property.property_edit_page import PropertyEditPage
        return PropertyEditPage(self.driver)
