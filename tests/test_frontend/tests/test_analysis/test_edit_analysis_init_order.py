import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

class TestEditAnalysisInitOrder:
    """Unit test class for verifying that the analysis ID is set before initializing UI in core.js."""

    def test_analysis_id_set_before_init_ui(self):
        """
        Test that the analysis ID is set from the URL before initializing UI elements.
        This ensures that the correct form submission handler is used when editing an analysis.
        """
        # Read the core.js file
        with open(os.path.join(os.path.dirname(__file__), '../../../../static/js/analysis/core.js'), 'r') as f:
            core_js_content = f.read()
        
        # Find the init method
        init_method_start = core_js_content.find("async init()")
        init_method_end = core_js_content.find("  },", init_method_start)
        init_method_content = core_js_content[init_method_start:init_method_end]
        
        # Check that the analysis ID is set before initializing UI
        analysis_id_set_index = init_method_content.find("this.state.analysisId = this.getAnalysisIdFromUrl()")
        init_ui_index = init_method_content.find("this.initUI()")
        
        # Assert that the analysis ID is set before initializing UI
        assert analysis_id_set_index > 0, "Analysis ID setting code not found in init method"
        assert init_ui_index > 0, "initUI call not found in init method"
        assert analysis_id_set_index < init_ui_index, "Analysis ID is not set before initializing UI"
        
        # Check that the form handler is set based on the analysis ID
        form_handler_code = """
    // Handle form submission
    if (this.state.analysisId) {
      // Edit mode
      analysisForm.addEventListener('submit', (event) => this.handleEditSubmit(event));
    } else {
      // Create mode
      analysisForm.addEventListener('submit', (event) => this.handleCreateSubmit(event));
    }
"""
        assert form_handler_code.strip() in core_js_content, "Form handler code not found or has been modified"
        
        # Check that handleEditSubmit explicitly uses the update_analysis endpoint
        update_endpoint_code = """
      // Make API call - EXPLICITLY to update_analysis endpoint
      const response = await fetch('/analyses/update_analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisData)
      });
"""
        assert update_endpoint_code.strip() in core_js_content, "Update endpoint code not found or has been modified"
        
    def test_preserve_analysis_id_and_type(self):
        """
        Test that the analysis ID and type are preserved if they're not present in the server response.
        This ensures that the Reports Tab can be populated correctly even if the server response is missing these values.
        """
        # Read the core.js file
        with open(os.path.join(os.path.dirname(__file__), '../../../../static/js/analysis/core.js'), 'r') as f:
            core_js_content = f.read()
        
        # Check that the code to preserve the analysis ID is present
        preserve_id_code = """
      // Verify returned analysis has same ID
      if (!data.analysis.id) {
        console.log(`Server returned undefined analysis ID, using original: ${analysisId}`);
        data.analysis.id = analysisId;
      }"""
        assert preserve_id_code.strip() in core_js_content, "Code to preserve analysis ID not found"
        
        # Check that the code to preserve the analysis type is present
        preserve_type_code = """
      // Verify returned analysis has same type
      if (!data.analysis.analysis_type) {
        console.log(`Server returned undefined analysis type, using original: ${this.state.analysisType}`);
        data.analysis.analysis_type = this.state.analysisType;
      }"""
        assert preserve_type_code.strip() in core_js_content, "Code to preserve analysis type not found"
