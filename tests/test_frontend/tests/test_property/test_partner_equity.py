"""
Tests for property partner equity management functionality.
"""
import pytest
from selenium.webdriver.common.by import By
from tests.test_frontend.base.base_test import BaseTest
from tests.test_frontend.page_objects.login_page import LoginPage
from tests.test_frontend.page_objects.property.property_list_page import PropertyListPage
from tests.test_frontend.utilities.data_generator import DataGenerator
from tests.test_frontend.base.logger import TestLogger
from tests.test_frontend.workflows.auth_workflows import AuthWorkflows

class TestPartnerEquity(BaseTest):
    """Test cases for property partner equity management functionality."""
    
    def setup_method(self):
        """Set up the test."""
        self.logger = TestLogger.setup_logging()
        TestLogger.log_test_start(self.logger, self._testMethodName)
        
        # Login before each test
        self.login_page = LoginPage(self.driver)
        AuthWorkflows.login(
            self.driver, 
            "test_user@example.com", 
            "password123", 
            logger=self.logger
        )
        
        # Create a test property
        TestLogger.log_step(self.logger, "Create a test property")
        self.property_data = DataGenerator.generate_property()
        self.property_list_page = PropertyListPage(self.driver)
        self.property_list_page.navigate_to()
        property_create_page = self.property_list_page.click_add_property()
        self.property_detail_page = property_create_page.create_property(self.property_data)
        
        # Navigate to partners tab
        TestLogger.log_step(self.logger, "Navigate to partners tab")
        self.partners_tab = self.property_detail_page.navigate_to_partners_tab()
    
    def teardown_method(self):
        """Tear down the test."""
        # Clean up by deleting the test property
        TestLogger.log_step(self.logger, "Clean up - delete test property")
        try:
            self.property_detail_page.click_edit_property().click_delete().confirm()
        except:
            pass  # Ignore errors during cleanup
        
        TestLogger.log_test_end(self.logger, self._testMethodName)
    
    def test_add_partner_with_valid_data(self):
        """Test adding a partner with valid data."""
        TestLogger.log_step(self.logger, "Get initial partner count")
        initial_count = self.partners_tab.get_partner_count()
        
        TestLogger.log_step(self.logger, "Click add partner button")
        add_partner_modal = self.partners_tab.click_add_partner()
        
        TestLogger.log_step(self.logger, "Fill partner form with test data")
        partner_name = "Test Partner"
        partner_email = "test.partner@example.com"
        equity_percentage = 25
        
        partners_tab = add_partner_modal.add_partner(
            name=partner_name,
            email=partner_email,
            equity_percentage=equity_percentage,
            is_manager=False,
            financial_visible=True,
            transaction_visible=True,
            contribution_visible=True,
            document_visible=True
        )
        
        TestLogger.log_step(self.logger, "Verify successful creation notification")
        self.assert_notification("Partner added successfully")
        
        TestLogger.log_step(self.logger, "Verify partner count increased")
        assert partners_tab.get_partner_count() == initial_count + 1
        
        TestLogger.log_step(self.logger, "Verify partner appears in list")
        assert partners_tab.is_partner_listed(partner_name)
        
        TestLogger.log_step(self.logger, "Verify partner equity percentage")
        partner_equity = partners_tab.get_partner_equity(partner_name)
        assert "25%" in partner_equity
        
        TestLogger.log_step(self.logger, "Verify total equity percentage")
        total_equity = partners_tab.get_total_equity_percentage()
        assert "100%" in total_equity
    
    def test_add_multiple_partners(self):
        """Test adding multiple partners with valid equity distribution."""
        TestLogger.log_step(self.logger, "Add first partner")
        add_partner_modal = self.partners_tab.click_add_partner()
        partners_tab = add_partner_modal.add_partner(
            name="Partner One",
            email="partner.one@example.com",
            equity_percentage=30,
            is_manager=False
        )
        
        TestLogger.log_step(self.logger, "Add second partner")
        add_partner_modal = partners_tab.click_add_partner()
        partners_tab = add_partner_modal.add_partner(
            name="Partner Two",
            email="partner.two@example.com",
            equity_percentage=20,
            is_manager=False
        )
        
        TestLogger.log_step(self.logger, "Add third partner")
        add_partner_modal = partners_tab.click_add_partner()
        partners_tab = add_partner_modal.add_partner(
            name="Partner Three",
            email="partner.three@example.com",
            equity_percentage=25,
            is_manager=True
        )
        
        TestLogger.log_step(self.logger, "Verify partner count")
        assert partners_tab.get_partner_count() == 3
        
        TestLogger.log_step(self.logger, "Verify all partners are listed")
        assert partners_tab.is_partner_listed("Partner One")
        assert partners_tab.is_partner_listed("Partner Two")
        assert partners_tab.is_partner_listed("Partner Three")
        
        TestLogger.log_step(self.logger, "Verify manager designation")
        assert partners_tab.is_partner_manager("Partner Three")
        assert not partners_tab.is_partner_manager("Partner One")
        
        TestLogger.log_step(self.logger, "Verify total equity percentage")
        total_equity = partners_tab.get_total_equity_percentage()
        assert "75%" in total_equity  # 30% + 20% + 25% = 75%
    
    def test_edit_partner(self):
        """Test editing a partner."""
        TestLogger.log_step(self.logger, "Add a partner")
        add_partner_modal = self.partners_tab.click_add_partner()
        partners_tab = add_partner_modal.add_partner(
            name="Partner to Edit",
            email="partner.edit@example.com",
            equity_percentage=40,
            is_manager=False
        )
        
        TestLogger.log_step(self.logger, "Edit the partner")
        edit_partner_modal = partners_tab.click_edit_partner("Partner to Edit")
        partners_tab = edit_partner_modal.update_partner(
            name="Updated Partner Name",
            email="updated.partner@example.com",
            equity_percentage=50,
            is_manager=True
        )
        
        TestLogger.log_step(self.logger, "Verify successful update notification")
        self.assert_notification("Partner updated successfully")
        
        TestLogger.log_step(self.logger, "Verify partner name updated")
        assert partners_tab.is_partner_listed("Updated Partner Name")
        assert not partners_tab.is_partner_listed("Partner to Edit")
        
        TestLogger.log_step(self.logger, "Verify partner equity percentage updated")
        partner_equity = partners_tab.get_partner_equity("Updated Partner Name")
        assert "50%" in partner_equity
        
        TestLogger.log_step(self.logger, "Verify manager designation updated")
        assert partners_tab.is_partner_manager("Updated Partner Name")
    
    def test_delete_partner(self):
        """Test deleting a partner."""
        TestLogger.log_step(self.logger, "Add a partner")
        add_partner_modal = self.partners_tab.click_add_partner()
        partners_tab = add_partner_modal.add_partner(
            name="Partner to Delete",
            email="partner.delete@example.com",
            equity_percentage=35,
            is_manager=False
        )
        
        TestLogger.log_step(self.logger, "Get initial partner count")
        initial_count = partners_tab.get_partner_count()
        
        TestLogger.log_step(self.logger, "Delete the partner")
        confirm_modal = partners_tab.click_delete_partner("Partner to Delete")
        partners_tab = confirm_modal.confirm()
        
        TestLogger.log_step(self.logger, "Verify successful deletion notification")
        self.assert_notification("Partner deleted successfully")
        
        TestLogger.log_step(self.logger, "Verify partner count decreased")
        assert partners_tab.get_partner_count() == initial_count - 1
        
        TestLogger.log_step(self.logger, "Verify partner no longer listed")
        assert not partners_tab.is_partner_listed("Partner to Delete")
    
    def test_invalid_equity_percentage(self):
        """Test adding a partner with invalid equity percentage."""
        TestLogger.log_step(self.logger, "Add a partner with 110% equity")
        add_partner_modal = self.partners_tab.click_add_partner()
        add_partner_modal.fill_partner_name("Invalid Equity Partner")
        add_partner_modal.fill_partner_email("invalid.equity@example.com")
        add_partner_modal.fill_equity_percentage(110)
        add_partner_modal.submit()
        
        TestLogger.log_step(self.logger, "Verify error message")
        # Check for validation error message about equity percentage
        error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".invalid-feedback")
        has_equity_error = False
        for error in error_messages:
            if "equity" in error.text.lower() and "100" in error.text:
                has_equity_error = True
                break
        assert has_equity_error, "Expected error message about equity percentage exceeding 100%"
        
        TestLogger.log_step(self.logger, "Verify modal still open")
        assert add_partner_modal.is_visible()
