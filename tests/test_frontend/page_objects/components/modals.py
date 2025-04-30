"""
Modal component page objects.
"""
from selenium.webdriver.common.by import By
from tests.test_frontend.page_objects.base_page import BasePage

class BaseModal(BasePage):
    """Base class for modal components."""
    
    # Common locators
    MODAL = (By.CSS_SELECTOR, ".modal.show")
    MODAL_TITLE = (By.CSS_SELECTOR, ".modal-title")
    MODAL_BODY = (By.CSS_SELECTOR, ".modal-body")
    CLOSE_BUTTON = (By.CSS_SELECTOR, ".modal .close, .modal .btn-close")
    
    def __init__(self, driver):
        """Initialize the modal component."""
        super().__init__(driver)
        # Wait for the modal to be visible
        self.wait_for_visibility(self.MODAL)
    
    def get_title(self):
        """Get the modal title text."""
        return self.get_text(self.MODAL_TITLE)
    
    def get_body_text(self):
        """Get the modal body text."""
        return self.get_text(self.MODAL_BODY)
    
    def close(self):
        """Close the modal."""
        self.wait_and_click(self.CLOSE_BUTTON)
        self.wait_for_invisibility(self.MODAL)
        return self
    
    def is_visible(self):
        """Check if the modal is visible."""
        return self.is_element_visible(self.MODAL)


class ConfirmModal(BaseModal):
    """Confirmation modal component."""
    
    # Locators
    CONFIRM_BUTTON = (By.CSS_SELECTOR, ".modal .btn-primary, .modal .btn-danger")
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".modal .btn-secondary")
    
    def confirm(self):
        """Click the confirm button."""
        self.wait_and_click(self.CONFIRM_BUTTON)
        self.wait_for_invisibility(self.MODAL)
        return self
    
    def cancel(self):
        """Click the cancel button."""
        self.wait_and_click(self.CANCEL_BUTTON)
        self.wait_for_invisibility(self.MODAL)
        return self


class AlertModal(BaseModal):
    """Alert modal component."""
    
    # Locators
    OK_BUTTON = (By.CSS_SELECTOR, ".modal .btn-primary, .modal .btn-ok")
    
    def ok(self):
        """Click the OK button."""
        self.wait_and_click(self.OK_BUTTON)
        self.wait_for_invisibility(self.MODAL)
        return self


class FormModal(BaseModal):
    """Form modal component."""
    
    # Locators
    SUBMIT_BUTTON = (By.CSS_SELECTOR, ".modal .btn-primary, .modal button[type='submit']")
    CANCEL_BUTTON = (By.CSS_SELECTOR, ".modal .btn-secondary")
    FORM = (By.CSS_SELECTOR, ".modal form")
    
    def submit(self):
        """Submit the form."""
        self.wait_and_click(self.SUBMIT_BUTTON)
        return self
    
    def cancel(self):
        """Cancel the form."""
        self.wait_and_click(self.CANCEL_BUTTON)
        self.wait_for_invisibility(self.MODAL)
        return self
    
    def fill_field(self, field_name, value):
        """
        Fill a field in the form.
        
        Args:
            field_name: Name attribute of the field
            value: Value to fill
            
        Returns:
            Self for method chaining
        """
        field_locator = (By.NAME, field_name)
        self.wait_and_send_keys(field_locator, value)
        return self
    
    def select_option(self, field_name, option_text):
        """
        Select an option from a dropdown.
        
        Args:
            field_name: Name attribute of the select field
            option_text: Text of the option to select
            
        Returns:
            Self for method chaining
        """
        from selenium.webdriver.support.ui import Select
        
        field_locator = (By.NAME, field_name)
        select_element = self.wait_for_visibility(field_locator)
        select = Select(select_element)
        select.select_by_visible_text(option_text)
        return self
    
    def check_checkbox(self, field_name, check=True):
        """
        Check or uncheck a checkbox.
        
        Args:
            field_name: Name attribute of the checkbox
            check: Whether to check (True) or uncheck (False) the checkbox
            
        Returns:
            Self for method chaining
        """
        field_locator = (By.NAME, field_name)
        checkbox = self.wait_for_visibility(field_locator)
        
        if (checkbox.is_selected() and not check) or (not checkbox.is_selected() and check):
            checkbox.click()
        
        return self
