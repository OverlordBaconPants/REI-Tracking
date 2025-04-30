"""
Edit partner modal page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.property.add_partner_modal import AddPartnerModal

class EditPartnerModal(AddPartnerModal):
    """
    Page object for the edit partner modal.
    
    Inherits from AddPartnerModal since most of the form fields and methods are the same.
    """
    
    # Additional locators specific to the edit modal
    DELETE_PARTNER_BUTTON = (By.ID, "delete-partner-button")
    
    def click_delete_partner(self):
        """
        Click the delete partner button.
        
        Returns:
            ConfirmModal object
        """
        self.wait_and_click(self.DELETE_PARTNER_BUTTON)
        from tests.test_frontend.page_objects.components.modals import ConfirmModal
        return ConfirmModal(self.driver)
    
    def update_partner(self, name=None, email=None, equity_percentage=None, is_manager=None, 
                      financial_visible=None, transaction_visible=None, 
                      contribution_visible=None, document_visible=None):
        """
        Update a partner with the provided data.
        
        Args:
            name: Partner name (None to leave unchanged)
            email: Partner email (None to leave unchanged)
            equity_percentage: Equity percentage (None to leave unchanged)
            is_manager: Whether the partner is the property manager (None to leave unchanged)
            financial_visible: Whether financial details are visible to the partner (None to leave unchanged)
            transaction_visible: Whether transactions are visible to the partner (None to leave unchanged)
            contribution_visible: Whether partner contributions are visible to the partner (None to leave unchanged)
            document_visible: Whether documents are visible to the partner (None to leave unchanged)
            
        Returns:
            PropertyPartnersTab object if successful
        """
        # Clear and update fields only if new values are provided
        if name is not None:
            self.driver.find_element(*self.PARTNER_NAME_INPUT).clear()
            self.fill_partner_name(name)
        
        if email is not None:
            self.driver.find_element(*self.PARTNER_EMAIL_INPUT).clear()
            self.fill_partner_email(email)
        
        if equity_percentage is not None:
            self.driver.find_element(*self.EQUITY_PERCENTAGE_INPUT).clear()
            self.fill_equity_percentage(equity_percentage)
        
        # Update checkboxes only if new values are provided
        if is_manager is not None:
            self.set_is_manager(is_manager)
        
        if financial_visible is not None:
            self.set_financial_visibility(financial_visible)
        
        if transaction_visible is not None:
            self.set_transaction_visibility(transaction_visible)
        
        if contribution_visible is not None:
            self.set_contribution_visibility(contribution_visible)
        
        if document_visible is not None:
            self.set_document_visibility(document_visible)
        
        self.submit()
        
        # Wait for the modal to close
        self.wait_for_invisibility(self.MODAL)
        
        # Return to the partners tab
        from tests.test_frontend.page_objects.property.property_partners_tab import PropertyPartnersTab
        return PropertyPartnersTab(self.driver)
