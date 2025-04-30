"""
Property workflow utilities.
"""
from tests.test_frontend.page_objects.login_page import LoginPage
from tests.test_frontend.page_objects.property.property_list_page import PropertyListPage
from tests.test_frontend.base.logger import TestLogger
from tests.test_frontend.workflows.auth_workflows import AuthWorkflows

class PropertyWorkflows:
    """Property workflow utilities."""
    
    @staticmethod
    def create_property(driver, property_data, user_email=None, user_password=None, logger=None):
        """
        Create a property workflow.
        
        Args:
            driver: WebDriver instance
            property_data: Dictionary containing property data
            user_email: Optional user email for login (if not already logged in)
            user_password: Optional user password for login (if not already logged in)
            logger: Optional logger instance
            
        Returns:
            Dictionary containing property data and the created property's ID
        """
        if logger:
            TestLogger.log_step(logger, "Create property workflow started")
        
        # Login if credentials provided
        if user_email and user_password:
            if logger:
                TestLogger.log_step(logger, f"Login as {user_email}")
            AuthWorkflows.login(driver, user_email, user_password, logger=logger)
        
        # Navigate to property list page
        if logger:
            TestLogger.log_step(logger, "Navigate to property list page")
        property_list_page = PropertyListPage(driver)
        property_list_page.navigate_to()
        
        # Click add property button
        if logger:
            TestLogger.log_step(logger, "Click add property button")
        property_create_page = property_list_page.click_add_property()
        
        # Fill property form with test data
        if logger:
            TestLogger.log_step(logger, "Fill property form with test data")
        property_detail_page = property_create_page.create_property(property_data)
        
        # Extract property ID from URL
        current_url = driver.current_url
        property_id = None
        if "/properties/" in current_url:
            property_id = current_url.split("/properties/")[1].split("/")[0]
            property_data["id"] = property_id
        
        if logger:
            TestLogger.log_step(logger, f"Property created with ID: {property_id}")
        
        return property_data
    
    @staticmethod
    def add_partner_to_property(driver, property_id, partner_data, logger=None):
        """
        Add a partner to a property workflow.
        
        Args:
            driver: WebDriver instance
            property_id: ID of the property to add the partner to
            partner_data: Dictionary containing partner data
            logger: Optional logger instance
            
        Returns:
            Dictionary containing partner data
        """
        if logger:
            TestLogger.log_step(logger, "Add partner to property workflow started")
        
        # Navigate to property detail page
        if logger:
            TestLogger.log_step(logger, f"Navigate to property detail page for ID: {property_id}")
        driver.get(f"http://localhost:5000/properties/{property_id}")
        
        # Navigate to partners tab
        if logger:
            TestLogger.log_step(logger, "Navigate to partners tab")
        from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
        property_detail_page = PropertyDetailPage(driver)
        partners_tab = property_detail_page.navigate_to_partners_tab()
        
        # Click add partner button
        if logger:
            TestLogger.log_step(logger, "Click add partner button")
        add_partner_modal = partners_tab.click_add_partner()
        
        # Fill partner form with data
        if logger:
            TestLogger.log_step(logger, "Fill partner form with data")
        partners_tab = add_partner_modal.add_partner(
            name=partner_data.get("name", "Test Partner"),
            email=partner_data.get("email", "test.partner@example.com"),
            equity_percentage=partner_data.get("equity_percentage", 25),
            is_manager=partner_data.get("is_manager", False),
            financial_visible=partner_data.get("financial_visible", True),
            transaction_visible=partner_data.get("transaction_visible", True),
            contribution_visible=partner_data.get("contribution_visible", True),
            document_visible=partner_data.get("document_visible", True)
        )
        
        if logger:
            TestLogger.log_step(logger, f"Partner {partner_data.get('name')} added to property {property_id}")
        
        return partner_data
    
    @staticmethod
    def delete_property(driver, property_id, logger=None):
        """
        Delete a property workflow.
        
        Args:
            driver: WebDriver instance
            property_id: ID of the property to delete
            logger: Optional logger instance
            
        Returns:
            True if successful, False otherwise
        """
        if logger:
            TestLogger.log_step(logger, "Delete property workflow started")
        
        try:
            # Navigate to property detail page
            if logger:
                TestLogger.log_step(logger, f"Navigate to property detail page for ID: {property_id}")
            driver.get(f"http://localhost:5000/properties/{property_id}")
            
            # Click edit property button
            if logger:
                TestLogger.log_step(logger, "Click edit property button")
            from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
            property_detail_page = PropertyDetailPage(driver)
            property_edit_page = property_detail_page.click_edit_property()
            
            # Click delete button and confirm
            if logger:
                TestLogger.log_step(logger, "Click delete button and confirm")
            confirm_modal = property_edit_page.click_delete()
            confirm_modal.confirm()
            
            if logger:
                TestLogger.log_step(logger, f"Property {property_id} deleted successfully")
            
            return True
        except Exception as e:
            if logger:
                TestLogger.log_step(logger, f"Error deleting property: {str(e)}")
            return False
    
    @staticmethod
    def get_property_details(driver, property_id, logger=None):
        """
        Get property details workflow.
        
        Args:
            driver: WebDriver instance
            property_id: ID of the property to get details for
            logger: Optional logger instance
            
        Returns:
            Dictionary containing property details
        """
        if logger:
            TestLogger.log_step(logger, "Get property details workflow started")
        
        # Navigate to property detail page
        if logger:
            TestLogger.log_step(logger, f"Navigate to property detail page for ID: {property_id}")
        driver.get(f"http://localhost:5000/properties/{property_id}")
        
        # Extract property details
        from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
        property_detail_page = PropertyDetailPage(driver)
        
        property_details = {
            "id": property_id,
            "name": property_detail_page.get_property_name(),
            "address": property_detail_page.get_property_address(),
            "purchase_price": property_detail_page.get_purchase_price(),
            "purchase_date": property_detail_page.get_purchase_date(),
            "bedrooms": property_detail_page.get_bedrooms(),
            "bathrooms": property_detail_page.get_bathrooms(),
            "square_feet": property_detail_page.get_square_feet()
        }
        
        if logger:
            TestLogger.log_step(logger, f"Property details retrieved for ID: {property_id}")
        
        return property_details
