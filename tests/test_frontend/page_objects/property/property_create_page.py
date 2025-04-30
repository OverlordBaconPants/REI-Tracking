"""
Property create page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class PropertyCreatePage(BasePage):
    """Page object for the property create page."""
    
    # Locators
    PROPERTY_NAME_INPUT = (By.ID, "property-name")
    STREET_INPUT = (By.ID, "street")
    CITY_INPUT = (By.ID, "city")
    STATE_INPUT = (By.ID, "state")
    ZIP_INPUT = (By.ID, "zip")
    PURCHASE_PRICE_INPUT = (By.ID, "purchase-price")
    PURCHASE_DATE_INPUT = (By.ID, "purchase-date")
    BEDROOMS_INPUT = (By.ID, "bedrooms")
    BATHROOMS_INPUT = (By.ID, "bathrooms")
    SQUARE_FEET_INPUT = (By.ID, "square-feet")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    CANCEL_BUTTON = (By.ID, "cancel-button")
    
    def __init__(self, driver):
        """Initialize the property create page object."""
        super().__init__(driver)
        self.url = "/properties/add"
    
    def fill_name(self, name):
        """
        Fill the property name field.
        
        Args:
            name: Property name
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.PROPERTY_NAME_INPUT, name)
        return self
    
    def fill_address(self, street, city, state, zip_code):
        """
        Fill the address fields.
        
        Args:
            street: Street address
            city: City
            state: State
            zip_code: ZIP code
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.STREET_INPUT, street)
        self.wait_and_send_keys(self.CITY_INPUT, city)
        self.wait_and_send_keys(self.STATE_INPUT, state)
        self.wait_and_send_keys(self.ZIP_INPUT, zip_code)
        return self
    
    def fill_purchase_price(self, price):
        """
        Fill the purchase price field.
        
        Args:
            price: Purchase price
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.PURCHASE_PRICE_INPUT, str(price))
        return self
    
    def fill_purchase_date(self, date):
        """
        Fill the purchase date field.
        
        Args:
            date: Purchase date in YYYY-MM-DD format
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.PURCHASE_DATE_INPUT, date)
        return self
    
    def fill_bedrooms(self, bedrooms):
        """
        Fill the bedrooms field.
        
        Args:
            bedrooms: Number of bedrooms
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.BEDROOMS_INPUT, str(bedrooms))
        return self
    
    def fill_bathrooms(self, bathrooms):
        """
        Fill the bathrooms field.
        
        Args:
            bathrooms: Number of bathrooms
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.BATHROOMS_INPUT, str(bathrooms))
        return self
    
    def fill_square_feet(self, square_feet):
        """
        Fill the square feet field.
        
        Args:
            square_feet: Square footage
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.SQUARE_FEET_INPUT, str(square_feet))
        return self
    
    def submit_form(self):
        """
        Submit the form.
        
        Returns:
            PropertyDetailPage object if successful
        """
        self.wait_and_click(self.SUBMIT_BUTTON)
        
        # Check if we're redirected to the property detail page
        if "/properties/" in self.driver.current_url and "/add" not in self.driver.current_url:
            from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
            return PropertyDetailPage(self.driver)
        
        # If we're still on the create page, return self
        return self
    
    def cancel(self):
        """
        Cancel the form.
        
        Returns:
            PropertyListPage object
        """
        self.wait_and_click(self.CANCEL_BUTTON)
        from tests.test_frontend.page_objects.property.property_list_page import PropertyListPage
        return PropertyListPage(self.driver)
    
    def create_property(self, property_data):
        """
        Create a property with the provided data.
        
        Args:
            property_data: Dictionary containing property data
            
        Returns:
            PropertyDetailPage object if successful
        """
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
