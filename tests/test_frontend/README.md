# Frontend Testing Framework

This directory contains tests for the frontend JavaScript code of the REI-Tracker application.

## Overview

The frontend testing framework uses:

- **pytest** as the test runner
- **Selenium WebDriver** for browser automation
- **Chrome** (headless) as the browser for testing

## Test Structure

The tests are organized into several categories:

1. **Minimal Tests**: These are simplified tests that mock dependencies and test core functionality in isolation.
   - `test_minimal.py`: Basic test to verify the testing infrastructure
   - `test_base_minimal.py`: Tests for the base.js module
   - `test_notifications_minimal.py`: Tests for the notifications.js module
   - `test_form_validator_minimal.py`: Tests for the form_validator.js module
   - `test_data_formatter_minimal.py`: Tests for the data_formatter.js module
   - `test_main_minimal.py`: Tests for the main.js module

2. **Integration Tests**: These tests verify that components work together correctly.
   - `test_base_js.py`: Tests for the base.js module with its dependencies
   - `test_notifications_js.py`: Tests for the notifications.js module with its dependencies
   - `test_form_validator_js.py`: Tests for the form_validator.js module with its dependencies
   - `test_data_formatter_js.py`: Tests for the data_formatter.js module with its dependencies
   - `test_main_js.py`: Tests for the main.js module with its dependencies

3. **HTML Tests**: These tests verify that HTML templates are correctly structured.
   - `test_base_html.py`: Tests for the base.html template

## Running Tests

To run all frontend tests:

```bash
cd tests/test_frontend
python run_tests.py
```

To run a specific test file:

```bash
cd tests/test_frontend
python run_tests.py --test-file test_minimal.py
```

To run tests with verbose output:

```bash
cd tests/test_frontend
python run_tests.py --verbose
```

## Test Configuration

The test configuration is defined in `conftest.py`, which includes:

- Fixtures for setting up the test environment
- Mock implementations of external dependencies
- Utilities for injecting JavaScript into the test page

All required dependencies are included in the main project's `requirements.txt` file.

## Testing Approach

### Mocking Dependencies

Since frontend JavaScript often depends on external libraries like jQuery, Bootstrap, and Chart.js, we use mocks to simulate these dependencies. This allows us to test our code in isolation without requiring the actual libraries to be loaded.

### Handling ES6 Modules

Some of our JavaScript files use ES6 module syntax (`import`/`export`), which isn't directly supported in the browser without proper module loading. For testing these files, we:

1. Remove the `export` statements
2. Inject the code directly into the page
3. Manually assign the module to the appropriate namespace

### Testing DOM Interactions

For tests that require DOM interaction, we:

1. Create a simple HTML page with the necessary elements
2. Inject our JavaScript code
3. Use Selenium to interact with the page and verify the results

## Adding New Tests

When adding new tests:

1. Create a new test file following the naming convention `test_*.py`
2. Use the appropriate fixtures from `conftest.py`
3. Mock any external dependencies
4. Inject the JavaScript code to be tested
5. Write assertions to verify the expected behavior

## Best Practices

- Keep tests focused on a single piece of functionality
- Use mocks to isolate the code being tested
- Verify both the functionality and the error handling
- Clean up any temporary files or resources created during the test
- Use descriptive test names and comments to explain the purpose of each test
