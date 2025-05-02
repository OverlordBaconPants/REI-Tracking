import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.test_frontend.base.base_test import BaseTest
from tests.test_frontend.page_objects.login_page import LoginPage
import time

class TestBRRRRClosingCosts(BaseTest):
    """Test class for verifying that the closing costs fields in BRRRR analysis are independent."""

    def test_closing_costs_fields_are_independent(self):
        """
        Test that the Purchase Details Closing Costs and Initial Financing Closing Costs
        fields are independent and can have different values.
        """
        # Login
        login_page = LoginPage(self.driver)
        login_page.login(self.test_user["email"], self.test_user["password"])
        
        # Navigate to create analysis page
        self.driver.get(self.base_url + "/analyses/create_analysis")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "analysis_type"))
        )
        
        # Select BRRRR analysis type
        analysis_type_select = self.driver.find_element(By.ID, "analysis_type")
        for option in analysis_type_select.find_elements(By.TAG_NAME, "option"):
            if "BRRRR" in option.text and "PadSplit" not in option.text:
                option.click()
                break
        
        # Wait for BRRRR form to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "closing_costs"))
        )
        
        # Fill in required fields
        self.driver.find_element(By.ID, "analysis_name").send_keys("Test BRRRR Analysis")
        self.driver.find_element(By.ID, "address").send_keys("123 Test St, Testville, TS 12345")
        self.driver.find_element(By.ID, "purchase_price").send_keys("200000")
        self.driver.find_element(By.ID, "after_repair_value").send_keys("250000")
        self.driver.find_element(By.ID, "renovation_costs").send_keys("30000")
        self.driver.find_element(By.ID, "renovation_duration").send_keys("3")
        self.driver.find_element(By.ID, "initial_loan_amount").send_keys("160000")
        self.driver.find_element(By.ID, "initial_loan_down_payment").send_keys("40000")
        self.driver.find_element(By.ID, "initial_loan_interest_rate").send_keys("8")
        self.driver.find_element(By.ID, "initial_loan_term").send_keys("12")
        self.driver.find_element(By.ID, "refinance_loan_interest_rate").send_keys("5")
        self.driver.find_element(By.ID, "refinance_loan_term").send_keys("360")
        self.driver.find_element(By.ID, "refinance_loan_closing_costs").send_keys("5000")
        self.driver.find_element(By.ID, "monthly_rent").send_keys("2000")
        self.driver.find_element(By.ID, "property_taxes").send_keys("200")
        self.driver.find_element(By.ID, "insurance").send_keys("100")
        
        # Get the closing costs fields
        purchase_closing_costs = self.driver.find_element(By.ID, "closing_costs")
        initial_loan_closing_costs = self.driver.find_element(By.ID, "initial_loan_closing_costs")
        
        # Set different values for the closing costs fields
        purchase_closing_costs.clear()
        purchase_closing_costs.send_keys("3000")
        
        initial_loan_closing_costs.clear()
        initial_loan_closing_costs.send_keys("4500")
        
        # Wait a moment to ensure any potential synchronization would have happened
        time.sleep(1)
        
        # Verify that the fields have different values
        assert purchase_closing_costs.get_attribute("value") == "3000", "Purchase closing costs should be 3000"
        assert initial_loan_closing_costs.get_attribute("value") == "4500", "Initial loan closing costs should be 4500"
        
        # Change one field and verify the other doesn't change
        purchase_closing_costs.clear()
        purchase_closing_costs.send_keys("3500")
        time.sleep(1)
        
        assert purchase_closing_costs.get_attribute("value") == "3500", "Purchase closing costs should be 3500"
        assert initial_loan_closing_costs.get_attribute("value") == "4500", "Initial loan closing costs should still be 4500"
        
        # Change the other field and verify the first doesn't change
        initial_loan_closing_costs.clear()
        initial_loan_closing_costs.send_keys("5500")
        time.sleep(1)
        
        assert purchase_closing_costs.get_attribute("value") == "3500", "Purchase closing costs should still be 3500"
        assert initial_loan_closing_costs.get_attribute("value") == "5500", "Initial loan closing costs should be 5500"
