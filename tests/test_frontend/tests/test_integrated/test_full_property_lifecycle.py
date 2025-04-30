"""
Tests for full property lifecycle workflow.
"""
import pytest
from selenium.webdriver.common.by import By
from tests.test_frontend.base.base_test import BaseTest
from tests.test_frontend.page_objects.login_page import LoginPage
from tests.test_frontend.page_objects.property.property_list_page import PropertyListPage
from tests.test_frontend.utilities.data_generator import DataGenerator
from tests.test_frontend.base.logger import TestLogger
from tests.test_frontend.workflows.auth_workflows import AuthWorkflows
from tests.test_frontend.workflows.property_workflows import PropertyWorkflows

class TestFullPropertyLifecycle(BaseTest):
    """Test cases for full property lifecycle workflow."""
    
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
    
    def teardown_method(self):
        """Tear down the test."""
        TestLogger.log_test_end(self.logger, self._testMethodName)
    
    def test_full_property_lifecycle(self):
        """
        Test the complete lifecycle of a property:
        1. Create property
        2. Add partners with equity shares
        3. Edit property details
        4. Delete property
        """
        # Step 1: Create property
        TestLogger.log_step(self.logger, "Step 1: Create property")
        property_data = DataGenerator.generate_property()
        property_data = PropertyWorkflows.create_property(
            self.driver,
            property_data,
            logger=self.logger
        )
        
        # Verify property was created
        assert "id" in property_data, "Property ID not found in created property data"
        property_id = property_data["id"]
        
        # Step 2: Add partners with equity shares
        TestLogger.log_step(self.logger, "Step 2: Add partners with equity shares")
        
        # Add first partner (25% equity)
        partner1_data = {
            "name": "Partner One",
            "email": "partner.one@example.com",
            "equity_percentage": 25,
            "is_manager": True
        }
        PropertyWorkflows.add_partner_to_property(
            self.driver,
            property_id,
            partner1_data,
            logger=self.logger
        )
        
        # Add second partner (25% equity)
        partner2_data = {
            "name": "Partner Two",
            "email": "partner.two@example.com",
            "equity_percentage": 25,
            "is_manager": False
        }
        PropertyWorkflows.add_partner_to_property(
            self.driver,
            property_id,
            partner2_data,
            logger=self.logger
        )
        
        # Verify partners were added
        TestLogger.log_step(self.logger, "Verify partners were added")
        from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
        property_detail_page = PropertyDetailPage(self.driver)
        partners_tab = property_detail_page.navigate_to_partners_tab()
        
        assert partners_tab.is_partner_listed("Partner One"), "Partner One not found in partners list"
        assert partners_tab.is_partner_listed("Partner Two"), "Partner Two not found in partners list"
        assert partners_tab.is_partner_manager("Partner One"), "Partner One is not marked as manager"
        assert not partners_tab.is_partner_manager("Partner Two"), "Partner Two is incorrectly marked as manager"
        
        # Verify total equity percentage
        total_equity = partners_tab.get_total_equity_percentage()
        assert "50%" in total_equity, f"Expected total equity to be 50%, but got {total_equity}"
        
        # Step 3: Edit property details
        TestLogger.log_step(self.logger, "Step 3: Edit property details")
        property_edit_page = property_detail_page.click_edit_property()
        
        # Update property details
        new_property_name = f"Updated {property_data['name']}"
        property_edit_page.fill_name(new_property_name)
        property_edit_page.fill_bedrooms(int(property_data["bedrooms"]) + 1)
        
        # Submit changes
        property_detail_page = property_edit_page.submit_form()
        
        # Verify property details were updated
        TestLogger.log_step(self.logger, "Verify property details were updated")
        assert property_detail_page.get_property_name() == new_property_name, "Property name was not updated"
        
        # Step 4: Delete property
        TestLogger.log_step(self.logger, "Step 4: Delete property")
        property_edit_page = property_detail_page.click_edit_property()
        confirm_modal = property_edit_page.click_delete()
        property_list_page = confirm_modal.confirm()
        
        # Verify property was deleted
        TestLogger.log_step(self.logger, "Verify property was deleted")
        assert not property_list_page.is_property_listed(new_property_name), "Property still exists after deletion"
    
    def test_property_with_full_partner_equity(self):
        """
        Test creating a property with partners that have 100% total equity:
        1. Create property
        2. Add partners with total 100% equity
        3. Verify equity distribution
        4. Clean up
        """
        # Step 1: Create property
        TestLogger.log_step(self.logger, "Step 1: Create property")
        property_data = DataGenerator.generate_property()
        property_data = PropertyWorkflows.create_property(
            self.driver,
            property_data,
            logger=self.logger
        )
        
        # Verify property was created
        assert "id" in property_data, "Property ID not found in created property data"
        property_id = property_data["id"]
        
        # Step 2: Add partners with total 100% equity
        TestLogger.log_step(self.logger, "Step 2: Add partners with total 100% equity")
        
        # Add first partner (40% equity)
        partner1_data = {
            "name": "Major Partner",
            "email": "major.partner@example.com",
            "equity_percentage": 40,
            "is_manager": True
        }
        PropertyWorkflows.add_partner_to_property(
            self.driver,
            property_id,
            partner1_data,
            logger=self.logger
        )
        
        # Add second partner (35% equity)
        partner2_data = {
            "name": "Medium Partner",
            "email": "medium.partner@example.com",
            "equity_percentage": 35,
            "is_manager": False
        }
        PropertyWorkflows.add_partner_to_property(
            self.driver,
            property_id,
            partner2_data,
            logger=self.logger
        )
        
        # Add third partner (25% equity)
        partner3_data = {
            "name": "Minor Partner",
            "email": "minor.partner@example.com",
            "equity_percentage": 25,
            "is_manager": False
        }
        PropertyWorkflows.add_partner_to_property(
            self.driver,
            property_id,
            partner3_data,
            logger=self.logger
        )
        
        # Step 3: Verify equity distribution
        TestLogger.log_step(self.logger, "Step 3: Verify equity distribution")
        from tests.test_frontend.page_objects.property.property_detail_page import PropertyDetailPage
        property_detail_page = PropertyDetailPage(self.driver)
        partners_tab = property_detail_page.navigate_to_partners_tab()
        
        # Verify all partners are listed
        assert partners_tab.is_partner_listed("Major Partner"), "Major Partner not found in partners list"
        assert partners_tab.is_partner_listed("Medium Partner"), "Medium Partner not found in partners list"
        assert partners_tab.is_partner_listed("Minor Partner"), "Minor Partner not found in partners list"
        
        # Verify equity percentages
        assert "40%" in partners_tab.get_partner_equity("Major Partner"), "Major Partner equity incorrect"
        assert "35%" in partners_tab.get_partner_equity("Medium Partner"), "Medium Partner equity incorrect"
        assert "25%" in partners_tab.get_partner_equity("Minor Partner"), "Minor Partner equity incorrect"
        
        # Verify total equity is 100%
        total_equity = partners_tab.get_total_equity_percentage()
        assert "100%" in total_equity, f"Expected total equity to be 100%, but got {total_equity}"
        
        # Step 4: Clean up
        TestLogger.log_step(self.logger, "Step 4: Clean up - delete property")
        PropertyWorkflows.delete_property(self.driver, property_id, logger=self.logger)
