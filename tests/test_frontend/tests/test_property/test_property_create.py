"""
Tests for property creation functionality.
"""
import pytest
from selenium.webdriver.common.by import By
from tests.test_frontend.base.base_test import BaseTest
from tests.test_frontend.page_objects.login_page import LoginPage
from tests.test_frontend.page_objects.property.property_list_page import PropertyListPage
from tests.test_frontend.utilities.data_generator import DataGenerator
from tests.test_frontend.base.logger import TestLogger
from tests.test_frontend.workflows.auth_workflows import AuthWorkflows

class TestPropertyCreation(BaseTest):
    """Test cases for property creation functionality."""
    
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
        
        # Navigate to property list page
        self.property_list_page = PropertyListPage(self.driver)
        self.property_list_page.navigate_to()
    
    def teardown_method(self):
        """Tear down the test."""
        TestLogger.log_test_end(self.logger, self._testMethodName)
    
    def test_create_property_with_valid_data(self):
        """Test creating a property with valid data."""
        TestLogger.log_step(self.logger, "Generate test property data")
        property_data = DataGenerator.generate_property()
        
        TestLogger.log_step(self.logger, "Get initial property count")
        initial_count = self.property_list_page.get_property_count()
        
        TestLogger.log_step(self.logger, "Click add property button")
        property_create_page = self.property_list_page.click_add_property()
        
        TestLogger.log_step(self.logger, "Fill property form with test data")
        property_detail_page = property_create_page.create_property(property_data)
        
        TestLogger.log_step(self.logger, "Verify successful creation notification")
        self.assert_notification("Property created successfully")
        
        TestLogger.log_step(self.logger, "Verify property details page shows correct information")
        assert property_detail_page.get_property_name() == property_data["name"]
        assert property_data["address"]["street"] in property_detail_page.get_property_address()
        
        TestLogger.log_step(self.logger, "Navigate back to property list")
        property_list_page = property_detail_page.navigate_to_property_list()
        
        TestLogger.log_step(self.logger, "Verify property count increased")
        assert property_list_page.get_property_count() == initial_count + 1
        
        TestLogger.log_step(self.logger, "Verify property appears in list")
        assert property_list_page.is_property_listed(property_data["name"])
    
    def test_create_property_with_missing_required_fields(self):
        """Test creating a property with missing required fields."""
        TestLogger.log_step(self.logger, "Click add property button")
        property_create_page = self.property_list_page.click_add_property()
        
        TestLogger.log_step(self.logger, "Submit form without filling required fields")
        property_create_page.submit_form()
        
        TestLogger.log_step(self.logger, "Verify form validation errors")
        # Check for validation error messages
        error_messages = self.driver.find_elements(By.CSS_SELECTOR, ".invalid-feedback")
        assert len(error_messages) > 0
        
        TestLogger.log_step(self.logger, "Verify still on create page")
        assert "/properties/add" in self.driver.current_url
    
    def test_cancel_property_creation(self):
        """Test canceling property creation."""
        TestLogger.log_step(self.logger, "Get initial property count")
        initial_count = self.property_list_page.get_property_count()
        
        TestLogger.log_step(self.logger, "Click add property button")
        property_create_page = self.property_list_page.click_add_property()
        
        TestLogger.log_step(self.logger, "Fill some fields")
        property_create_page.fill_name("Test Property - To Be Canceled")
        
        TestLogger.log_step(self.logger, "Click cancel button")
        property_list_page = property_create_page.cancel()
        
        TestLogger.log_step(self.logger, "Verify property count unchanged")
        assert property_list_page.get_property_count() == initial_count
        
        TestLogger.log_step(self.logger, "Verify property not in list")
        assert not property_list_page.is_property_listed("Test Property - To Be Canceled")
    
    def test_create_property_with_special_characters(self):
        """Test creating a property with special characters in the name and address."""
        TestLogger.log_step(self.logger, "Generate test property data with special characters")
        property_data = DataGenerator.generate_property()
        property_data["name"] = "Test Property #123 & Special! Chars"
        property_data["address"]["street"] = "123 Main St. #456"
        
        TestLogger.log_step(self.logger, "Click add property button")
        property_create_page = self.property_list_page.click_add_property()
        
        TestLogger.log_step(self.logger, "Fill property form with test data")
        property_detail_page = property_create_page.create_property(property_data)
        
        TestLogger.log_step(self.logger, "Verify successful creation notification")
        self.assert_notification("Property created successfully")
        
        TestLogger.log_step(self.logger, "Verify property details page shows correct information")
        assert property_detail_page.get_property_name() == property_data["name"]
        assert property_data["address"]["street"] in property_detail_page.get_property_address()
