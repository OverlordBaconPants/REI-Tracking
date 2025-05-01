# Test Persona for UI Testing

This directory contains the test persona data and utilities for UI testing. The test persona provides consistent test data for UI testing, including a dedicated test user, diverse property portfolio, comprehensive analyses, various loan scenarios, transaction history with reimbursements, and MAO calculation defaults.

## Overview

The test persona is designed to provide comprehensive test data that covers all features of the REI-Tracker application. This ensures that UI tests have consistent, predictable data to work with, making tests more reliable and easier to maintain.

## Components

- **`test_persona.py`**: Defines the test persona data, including:
  - `TEST_USER`: A dedicated test user with consistent credentials
  - `TEST_PROPERTIES`: A diverse property portfolio covering different investment strategies
  - `TEST_ANALYSES`: Comprehensive analyses for each property covering all supported strategies
  - `TEST_LOANS`: Various loan scenarios including standard, balloon, interest-only, etc.
  - `TEST_TRANSACTIONS`: Transactions with different types, categories, and reimbursement statuses
  - `MAO_CALCULATION_DEFAULTS`: Default values for Maximum Allowable Offer calculations
  - `TEST_PERSONA`: A complete dictionary containing all test persona data

- **`test_files/`**: Directory containing test files for transaction documentation:
  - `receipts/`: PDF receipts for expense transactions
  - `leases/`: PDF lease agreements for rental properties
  - `bank_statements/`: PDF bank statements for income transactions
  - `misc/`: Miscellaneous test files

## Setup

To set up the test environment with the test persona:

```bash
cd tests/test_frontend
python setup_test_environment.py
```

This will:
1. Create necessary test files (PDFs, etc.)
2. Seed the test database with test persona data
3. Set up directories for test screenshots and reports

## Usage

### Authentication

Use the `login_as_test_user` method from `auth_workflows.py` to log in with the test persona credentials:

```python
from tests.test_frontend.workflows.auth_workflows import AuthWorkflows

# Login as the test user
dashboard_page = AuthWorkflows.login_as_test_user(browser, logger=logger)
```

### File Uploads

Use the `upload_test_file` function from `file_upload_helper.py` to upload test files:

```python
from tests.test_frontend.utilities.file_upload_helper import upload_test_file

# Upload a test file
file_path = upload_test_file(browser, file_upload_element, "receipts/plumbing_repair_receipt.pdf")
```

### Example Test

Here's an example test that uses the test persona:

```python
from tests.test_frontend.base.base_test import BaseTest
from tests.test_frontend.workflows.auth_workflows import AuthWorkflows
from tests.test_frontend.test_data.test_persona import TEST_USER

class TestLoginWithTestPersona(BaseTest):
    """Test class demonstrating how to use the test persona for authentication."""
    
    def test_login_with_test_persona(self, browser, logger):
        """Test logging in with the test persona credentials."""
        # Login as the test user
        dashboard_page = AuthWorkflows.login_as_test_user(browser, logger=logger)
        
        # Verify login was successful
        assert "/main" in browser.current_url, "Login failed, not redirected to dashboard"
        
        # Verify user name is displayed in the navigation
        user_dropdown = WebDriverWait(browser, 10).until(
            EC.visibility_of_element_located((By.ID, "user-dropdown"))
        )
        assert f"{TEST_USER['first_name']} {TEST_USER['last_name']}" in user_dropdown.text
```

## Benefits

- **Consistency**: Tests run against the same data each time, making them more reliable
- **Comprehensive Coverage**: The test persona covers all features and edge cases
- **Clear Test Intent**: Using an obviously fake email address makes it clear this is test data
- **Isolation**: Keeps testing separate from any real user data
- **Documentation**: The test persona serves as living documentation of the application's data structures
