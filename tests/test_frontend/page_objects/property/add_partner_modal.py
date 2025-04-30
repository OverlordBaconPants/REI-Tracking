"""
Add partner modal page object.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.components.modals import FormModal

class AddPartnerModal(FormModal):
    """Page object for the add partner modal."""
    
    # Locators
    PARTNER_NAME_INPUT = (By.ID, "partner-name")
    PARTNER_EMAIL_INPUT = (By.ID, "partner-email")
    EQUITY_PERCENTAGE_INPUT = (By.ID, "equity-percentage")
    IS_MANAGER_CHECKBOX = (By.ID, "is-manager")
    
    # Visibility settings
    FINANCIAL_VISIBILITY_CHECKBOX = (By.ID, "financial-visibility")
    TRANSACTION_VISIBILITY_CHECKBOX = (By.ID, "transaction-visibility")
    CONTRIBUTION_VISIBILITY_CHECKBOX = (By.ID, "contribution-visibility")
    DOCUMENT_VISIBILITY_CHECKBOX = (By.ID, "document-visibility")
    
    def fill_partner_name(self, name):
        """
        Fill the partner name field.
        
        Args:
            name: Partner name
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.PARTNER_NAME_INPUT, name)
        return self
    
    def fill_partner_email(self, email):
        """
        Fill the partner email field.
        
        Args:
            email: Partner email
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.PARTNER_EMAIL_INPUT, email)
        return self
    
    def fill_equity_percentage(self, percentage):
        """
        Fill the equity percentage field.
        
        Args:
            percentage: Equity percentage
            
        Returns:
            Self for method chaining
        """
        self.wait_and_send_keys(self.EQUITY_PERCENTAGE_INPUT, str(percentage))
        return self
    
    def set_is_manager(self, is_manager=True):
        """
        Set the is manager checkbox.
        
        Args:
            is_manager: Whether the partner is the property manager
            
        Returns:
            Self for method chaining
        """
        checkbox = self.wait_for_visibility(self.IS_MANAGER_CHECKBOX)
        if (checkbox.is_selected() and not is_manager) or (not checkbox.is_selected() and is_manager):
            checkbox.click()
        return self
    
    def set_financial_visibility(self, visible=True):
        """
        Set the financial visibility checkbox.
        
        Args:
            visible: Whether financial details are visible to the partner
            
        Returns:
            Self for method chaining
        """
        checkbox = self.wait_for_visibility(self.FINANCIAL_VISIBILITY_CHECKBOX)
        if (checkbox.is_selected() and not visible) or (not checkbox.is_selected() and visible):
            checkbox.click()
        return self
    
    def set_transaction_visibility(self, visible=True):
        """
        Set the transaction visibility checkbox.
        
        Args:
            visible: Whether transactions are visible to the partner
            
        Returns:
            Self for method chaining
        """
        checkbox = self.wait_for_visibility(self.TRANSACTION_VISIBILITY_CHECKBOX)
        if (checkbox.is_selected() and not visible) or (not checkbox.is_selected() and visible):
            checkbox.click()
        return self
    
    def set_contribution_visibility(self, visible=True):
        """
        Set the contribution visibility checkbox.
        
        Args:
            visible: Whether partner contributions are visible to the partner
            
        Returns:
            Self for method chaining
        """
        checkbox = self.wait_for_visibility(self.CONTRIBUTION_VISIBILITY_CHECKBOX)
        if (checkbox.is_selected() and not visible) or (not checkbox.is_selected() and visible):
            checkbox.click()
        return self
    
    def set_document_visibility(self, visible=True):
        """
        Set the document visibility checkbox.
        
        Args:
            visible: Whether documents are visible to the partner
            
        Returns:
            Self for method chaining
        """
        checkbox = self.wait_for_visibility(self.DOCUMENT_VISIBILITY_CHECKBOX)
        if (checkbox.is_selected() and not visible) or (not checkbox.is_selected() and visible):
            checkbox.click()
        return self
    
    def add_partner(self, name, email, equity_percentage, is_manager=False, 
                   financial_visible=True, transaction_visible=True, 
                   contribution_visible=True, document_visible=True):
        """
        Add a partner with the provided data.
        
        Args:
            name: Partner name
            email: Partner email
            equity_percentage: Equity percentage
            is_manager: Whether the partner is the property manager
            financial_visible: Whether financial details are visible to the partner
            transaction_visible: Whether transactions are visible to the partner
            contribution_visible: Whether partner contributions are visible to the partner
            document_visible: Whether documents are visible to the partner
            
        Returns:
            PropertyPartnersTab object if successful
        """
        self.fill_partner_name(name)
        self.fill_partner_email(email)
        self.fill_equity_percentage(equity_percentage)
        self.set_is_manager(is_manager)
        self.set_financial_visibility(financial_visible)
        self.set_transaction_visibility(transaction_visible)
        self.set_contribution_visibility(contribution_visible)
        self.set_document_visibility(document_visible)
        
        self.submit()
        
        # Wait for the modal to close
        self.wait_for_invisibility(self.MODAL)
        
        # Return to the partners tab
        from tests.test_frontend.page_objects.property.property_partners_tab import PropertyPartnersTab
        return PropertyPartnersTab(self.driver)
