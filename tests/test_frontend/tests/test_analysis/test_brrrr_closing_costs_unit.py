import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

class TestBRRRRClosingCostsUnit:
    """Unit test class for verifying that the closing costs fields in BRRRR analysis are independent."""

    def test_closing_cost_sync_handler_removed(self):
        """
        Test that the initClosingCostSyncHandler function no longer syncs the closing costs fields.
        """
        # Read the brrrr.js file
        with open(os.path.join(os.path.dirname(__file__), '../../../../static/js/analysis/brrrr.js'), 'r') as f:
            brrrr_js_content = f.read()
        
        # Check that the initClosingCostSyncHandler function is empty
        assert "initClosingCostSyncHandler() {" in brrrr_js_content
        assert "// This function is now empty as we no longer want to sync the closing costs fields" in brrrr_js_content
        assert "// The Purchase Details Closing Costs and Initial Financing Closing Costs should be separate" in brrrr_js_content
        
        # Check that the old event listeners are not present
        assert "closingCostsInput.addEventListener('input', () => {" not in brrrr_js_content
        assert "initialLoanClosingCostsInput.value = closingCostsInput.value" not in brrrr_js_content
        assert "initialLoanClosingCostsInput.addEventListener('input', () => {" not in brrrr_js_content
        assert "closingCostsInput.value = initialLoanClosingCostsInput.value" not in brrrr_js_content
        
        # Check that the processFormData function no longer syncs the fields
        assert "// No longer syncing closing_costs to initial_loan_closing_costs" in brrrr_js_content
        assert "// Each field will maintain its own value" in brrrr_js_content
        assert "analysisData.initial_loan_closing_costs = analysisData.closing_costs" not in brrrr_js_content
        
        # Check that the populateFields method uses the correct field values
        assert "AnalysisCore.setFieldValue('closing_costs', analysis.closing_costs || analysis.initial_loan_closing_costs)" in brrrr_js_content
