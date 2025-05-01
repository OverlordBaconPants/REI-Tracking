import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.test_frontend.base.base_test import BaseTest

class TestMAODefaultsUI(BaseTest):
    """Test the MAO defaults UI functionality."""
    
    def test_mao_defaults_modal(self):
        """Test the MAO defaults modal functionality."""
        # Login
        self.login()
        
        # Navigate to analysis page
        self.browser.get(self.get_url('/analyses/create_analysis'))
        
        # Fill in required fields
        self.browser.find_element(By.ID, 'analysis_name').send_keys('Test Analysis')
        self.browser.find_element(By.ID, 'address').send_keys('123 Test St, Test City, TS 12345')
        
        # Run comps
        self.browser.find_element(By.ID, 'runCompsBtn').click()
        
        # Wait for comps to load
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'maoValue'))
        )
        
        # Click on Change MAO Default Values button
        self.browser.find_element(By.ID, 'changeMaoDefaultsBtn').click()
        
        # Wait for modal to appear
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'maoDefaultsModal'))
        )
        
        # Verify modal fields
        ltv_input = self.browser.find_element(By.ID, 'ltv_percentage')
        monthly_costs_input = self.browser.find_element(By.ID, 'monthly_holding_costs')
        max_cash_input = self.browser.find_element(By.ID, 'max_cash_left')
        
        assert ltv_input.get_attribute('value') != ''
        assert monthly_costs_input.get_attribute('value') != ''
        assert max_cash_input.get_attribute('value') != ''
        
        # Update values
        ltv_input.clear()
        ltv_input.send_keys('80')
        monthly_costs_input.clear()
        monthly_costs_input.send_keys('500')
        max_cash_input.clear()
        max_cash_input.send_keys('15000')
        
        # Save changes
        self.browser.find_element(By.ID, 'saveMaoDefaultsBtn').click()
        
        # Wait for success notification
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'toast-success'))
        )
        
        # Verify notification text
        toast = self.browser.find_element(By.CLASS_NAME, 'toast-success')
        assert 'MAO default values updated successfully' in toast.text
        
        # Wait for modal to close
        WebDriverWait(self.browser, 10).until(
            EC.invisibility_of_element_located((By.ID, 'maoDefaultsModal'))
        )
        
        # Test cancel button
        # Click on Change MAO Default Values button again
        self.browser.find_element(By.ID, 'changeMaoDefaultsBtn').click()
        
        # Wait for modal to appear
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'maoDefaultsModal'))
        )
        
        # Click cancel button
        self.browser.find_element(By.ID, 'cancelMaoDefaultsBtn').click()
        
        # Wait for info notification
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'toast-info'))
        )
        
        # Verify notification text
        toast = self.browser.find_element(By.CLASS_NAME, 'toast-info')
        assert 'MAO default values changes cancelled' in toast.text
    
    def test_mao_defaults_validation(self):
        """Test validation of MAO defaults form."""
        # Login
        self.login()
        
        # Navigate to analysis page
        self.browser.get(self.get_url('/analyses/create_analysis'))
        
        # Fill in required fields
        self.browser.find_element(By.ID, 'analysis_name').send_keys('Test Analysis')
        self.browser.find_element(By.ID, 'address').send_keys('123 Test St, Test City, TS 12345')
        
        # Run comps
        self.browser.find_element(By.ID, 'runCompsBtn').click()
        
        # Wait for comps to load
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'maoValue'))
        )
        
        # Click on Change MAO Default Values button
        self.browser.find_element(By.ID, 'changeMaoDefaultsBtn').click()
        
        # Wait for modal to appear
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, 'maoDefaultsModal'))
        )
        
        # Test invalid LTV percentage
        ltv_input = self.browser.find_element(By.ID, 'ltv_percentage')
        ltv_input.clear()
        ltv_input.send_keys('150')  # Invalid: > 100%
        
        # Try to save
        self.browser.find_element(By.ID, 'saveMaoDefaultsBtn').click()
        
        # Wait for error notification
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'toast-error'))
        )
        
        # Verify notification text
        toast = self.browser.find_element(By.CLASS_NAME, 'toast-error')
        assert 'LTV percentage must be between 0 and 100' in toast.text
        
        # Test invalid monthly holding costs
        ltv_input.clear()
        ltv_input.send_keys('80')  # Valid
        
        monthly_costs_input = self.browser.find_element(By.ID, 'monthly_holding_costs')
        monthly_costs_input.clear()
        monthly_costs_input.send_keys('-100')  # Invalid: negative
        
        # Try to save
        self.browser.find_element(By.ID, 'saveMaoDefaultsBtn').click()
        
        # Wait for error notification
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'toast-error'))
        )
        
        # Verify notification text
        toast = self.browser.find_element(By.CLASS_NAME, 'toast-error')
        assert 'Monthly holding costs must be a positive number' in toast.text
        
        # Test invalid max cash left
        monthly_costs_input.clear()
        monthly_costs_input.send_keys('500')  # Valid
        
        max_cash_input = self.browser.find_element(By.ID, 'max_cash_left')
        max_cash_input.clear()
        max_cash_input.send_keys('-1000')  # Invalid: negative
        
        # Try to save
        self.browser.find_element(By.ID, 'saveMaoDefaultsBtn').click()
        
        # Wait for error notification
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'toast-error'))
        )
        
        # Verify notification text
        toast = self.browser.find_element(By.CLASS_NAME, 'toast-error')
        assert 'Max cash left must be a positive number' in toast.text
