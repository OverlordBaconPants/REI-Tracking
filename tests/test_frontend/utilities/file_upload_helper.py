"""
File upload helper utilities for UI testing.
"""
import os
import time
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def upload_test_file(driver, file_upload_element, test_file_name):
    """
    Upload a test file during UI testing.
    
    Args:
        driver: WebDriver instance
        file_upload_element: The file upload element
        test_file_name: Name of the test file to upload (relative to test_files directory)
    
    Returns:
        The absolute path to the uploaded file
    """
    # Get the absolute path to the test file
    test_files_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'test_data', 
        'test_files'
    )
    file_path = os.path.abspath(os.path.join(test_files_dir, test_file_name))
    
    # Ensure the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test file not found: {file_path}")
    
    # Send the file path to the file upload element
    file_upload_element.send_keys(file_path)
    
    # Return the file path for verification
    return file_path


def wait_for_file_upload_complete(driver, upload_status_element, timeout=10):
    """
    Wait for a file upload to complete.
    
    Args:
        driver: WebDriver instance
        upload_status_element: Locator tuple for the element that indicates upload status
        timeout: Maximum time to wait in seconds
    
    Returns:
        True if upload completed successfully, False otherwise
    """
    try:
        # Wait for the upload status element to indicate completion
        WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element(upload_status_element, "Upload complete")
        )
        return True
    except:
        return False


def get_uploaded_file_name(file_path):
    """
    Get the file name from a file path.
    
    Args:
        file_path: Full path to the file
    
    Returns:
        The file name
    """
    return os.path.basename(file_path)


def verify_file_upload(driver, file_name_element, file_path):
    """
    Verify that a file was uploaded successfully.
    
    Args:
        driver: WebDriver instance
        file_name_element: Locator tuple for the element that displays the file name
        file_path: Path to the uploaded file
    
    Returns:
        True if the file name is displayed, False otherwise
    """
    file_name = get_uploaded_file_name(file_path)
    try:
        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(file_name_element)
        )
        return file_name in element.text
    except:
        return False
