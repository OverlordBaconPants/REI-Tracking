"""
Property partners tab page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class PropertyPartnersTab(BasePage):
    """Page object for the property partners tab."""
    
    # Locators
    PARTNER_TABLE = (By.ID, "partner-table")
    PARTNER_ROWS = (By.CSS_SELECTOR, "#partner-table tbody tr")
    ADD_PARTNER_BUTTON = (By.ID, "add-partner-button")
    TOTAL_EQUITY_PERCENTAGE = (By.ID, "total-equity-percentage")
    
    def __init__(self, driver):
        """Initialize the property partners tab object."""
        super().__init__(driver)
        # This is a tab within the property detail page, not a separate page
        self.url = None
    
    def get_partner_count(self):
        """Get the number of partners in the table."""
        return len(self.find_elements(self.PARTNER_ROWS))
    
    def click_add_partner(self):
        """
        Click the add partner button.
        
        Returns:
            AddPartnerModal object
        """
        self.wait_and_click(self.ADD_PARTNER_BUTTON)
        from tests.test_frontend.page_objects.property.add_partner_modal import AddPartnerModal
        return AddPartnerModal(self.driver)
    
    def get_total_equity_percentage(self):
        """
        Get the total equity percentage text.
        
        Returns:
            String representing the total equity percentage
        """
        return self.get_text(self.TOTAL_EQUITY_PERCENTAGE)
    
    def is_partner_listed(self, partner_name):
        """
        Check if a partner is listed in the table.
        
        Args:
            partner_name: Name of the partner to check
            
        Returns:
            True if the partner is listed, False otherwise
        """
        return self.find_partner_row(partner_name) is not None
    
    def find_partner_row(self, partner_name):
        """
        Find the row containing the specified partner.
        
        Args:
            partner_name: Name of the partner to find
            
        Returns:
            WebElement if found, None otherwise
        """
        rows = self.find_elements(self.PARTNER_ROWS)
        for row in rows:
            if partner_name in row.text:
                return row
        return None
    
    def get_partner_equity(self, partner_name):
        """
        Get the equity percentage for a partner.
        
        Args:
            partner_name: Name of the partner
            
        Returns:
            String representing the equity percentage, or None if partner not found
        """
        partner_row = self.find_partner_row(partner_name)
        if partner_row:
            equity_cell = partner_row.find_element(By.CSS_SELECTOR, ".partner-equity")
            return equity_cell.text
        return None
    
    def click_edit_partner(self, partner_name):
        """
        Click the edit button for a partner.
        
        Args:
            partner_name: Name of the partner to edit
            
        Returns:
            EditPartnerModal object
        """
        partner_row = self.find_partner_row(partner_name)
        if partner_row:
            edit_button = partner_row.find_element(By.CSS_SELECTOR, ".edit-partner-button")
            edit_button.click()
            from tests.test_frontend.page_objects.property.edit_partner_modal import EditPartnerModal
            return EditPartnerModal(self.driver)
        raise Exception(f"Partner {partner_name} not found in table")
    
    def click_delete_partner(self, partner_name):
        """
        Click the delete button for a partner.
        
        Args:
            partner_name: Name of the partner to delete
            
        Returns:
            ConfirmModal object
        """
        partner_row = self.find_partner_row(partner_name)
        if partner_row:
            delete_button = partner_row.find_element(By.CSS_SELECTOR, ".delete-partner-button")
            delete_button.click()
            from tests.test_frontend.page_objects.components.modals import ConfirmModal
            return ConfirmModal(self.driver)
        raise Exception(f"Partner {partner_name} not found in table")
    
    def is_partner_manager(self, partner_name):
        """
        Check if a partner is designated as the property manager.
        
        Args:
            partner_name: Name of the partner to check
            
        Returns:
            True if the partner is the property manager, False otherwise
        """
        partner_row = self.find_partner_row(partner_name)
        if partner_row:
            manager_indicator = partner_row.find_elements(By.CSS_SELECTOR, ".manager-indicator")
            return len(manager_indicator) > 0 and manager_indicator[0].is_displayed()
        return False
