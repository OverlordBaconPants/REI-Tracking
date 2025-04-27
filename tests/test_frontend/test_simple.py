"""
Simple test to verify the testing infrastructure works.
"""

import pytest


def test_simple(inject_scripts):
    """A simple test that doesn't depend on any external libraries."""
    driver = inject_scripts([])
    
    # Execute a simple script
    result = driver.execute_script("return 1 + 1")
    assert result == 2
