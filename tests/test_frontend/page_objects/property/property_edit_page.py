"""
Property edit page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage
from tests.test_frontend.page_objects.property.property_create_page import PropertyCreatePage

class PropertyEditPage(PropertyCreatePage):
    """
    Page object for the property edit page.
    
    Inherits from PropertyCreatePage since most of the form fields and methods are the same.
    """
    
    # Additional locators specific to the edit page
    DELETE_BUTTON = (By.ID, "delete-property-button")
    
    def __init__(self, driver):
        """Initialize the property edit page object."""
        super().__init__(driver)
        # The URL will be set dynamically based on the property ID
        self.url = None
    
    def click_delete(self):
        """
        Click the delete button.
        
        Returns:
            ConfirmModal object
        """
        self.wait_and_click(self.DELETE_BUTTON)
        from tests.test_frontend.page_objects.components.modals import ConfirmModal
        return ConfirmModal(self.driver)
    
    def submit_form(self):
        """
        Submit the form.
        
        Returns:
            PropertyDetailPage object if successful
        """
        self.wait_and_click(self.SUBMIT_BUTTON)
        
        # Check if we're redirected to the property detail page
        if "/properties/" in self.driver.current_url and "/edit" not in self.driver.current_url:
            from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
            return PropertyDetailPage(self.driver)
        
        # If we're still on the edit page, return self
        return self
    
    def update_property(self, property_data):
        """
        Update a property with the provided data.
        
        Args:
            property_data: Dictionary containing property data
            
        Returns:
            PropertyDetailPage object if successful
        """
        # Clear existing values before filling in new ones
        self.driver.find_element(*self.PROPERTY_NAME_INPUT).clear()
        self.driver.find_element(*self.STREET_INPUT).clear()
        self.driver.find_element(*self.CITY_INPUT).clear()
        self.driver.find_element(*self.STATE_INPUT).clear()
        self.driver.find_element(*self.ZIP_INPUT).clear()
        self.driver.find_element(*self.PURCHASE_PRICE_INPUT).clear()
        self.driver.find_element(*self.PURCHASE_DATE_INPUT).clear()
        self.driver.find_element(*self.BEDROOMS_INPUT).clear()
        self.driver.find_element(*self.BATHROOMS_INPUT).clear()
        self.driver.find_element(*self.SQUARE_FEET_INPUT).clear()
        
        # Fill in new values
        self.fill_name(property_data["name"])
        self.fill_address(
            property_data["address"]["street"],
            property_data["address"]["city"],
            property_data["address"]["state"],
            property_data["address"]["zip"]
        )
        self.fill_purchase_price(property_data["purchase_price"])
        self.fill_purchase_date(property_data["purchase_date"])
        self.fill_bedrooms(property_data["bedrooms"])
        self.fill_bathrooms(property_data["bathrooms"])
        self.fill_square_feet(property_data["square_feet"])
        
        return self.submit_form()
