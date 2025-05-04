import unittest
import os
import sys
import json
import uuid
import datetime
from unittest.mock import patch, MagicMock, mock_open
from flask import Flask
from io import BytesIO

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.analysis_service import AnalysisService

class TestAnalysisServiceCoverageSimple(unittest.TestCase):
    """Simple test cases for the AnalysisService class focused on improving coverage."""

    def setUp(self):
        """Set up test environment."""
        # Create a test Flask app
        self.app = Flask(__name__)
        self.app.config['ANALYSES_DIR'] = 'test_analyses'
        self.app.config['DATA_DIR'] = 'test_data'
        
        # Create the test analyses directory if it doesn't exist
        os.makedirs(self.app.config['ANALYSES_DIR'], exist_ok=True)
        
        # Create a test analysis with known values
        self.test_analysis = {
            "id": str(uuid.uuid4()),
            "user_id": "test-user-id",
            "analysis_name": "Test LTR Analysis",
            "analysis_type": "LTR",
            "address": "123 Test Street",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d"),
            "purchase_price": 200000,
            "monthly_rent": 1800,
            "property_taxes": 200,
            "insurance": 100,
            "hoa_coa_coop": 0,
            "management_fee_percentage": 8,
            "capex_percentage": 5,
            "vacancy_percentage": 5,
            "repairs_percentage": 5,
            "loan1_loan_amount": 160000,
            "loan1_loan_interest_rate": 4.5,
            "loan1_loan_term": 360,
            "loan1_interest_only": False,
            "loan1_loan_down_payment": 40000,
            "loan1_loan_closing_costs": 3000
        }
        
        # Create a test analysis file
        self.test_file_path = os.path.join(
            self.app.config['ANALYSES_DIR'], 
            f"{self.test_analysis['id']}_{self.test_analysis['user_id']}.json"
        )
        with open(self.test_file_path, 'w') as f:
            json.dump(self.test_analysis, f)

    def tearDown(self):
        """Clean up after tests."""
        # Remove the test file
        try:
            os.remove(self.test_file_path)
        except:
            pass
        
        # Try to remove the test directory
        try:
            os.rmdir(self.app.config['ANALYSES_DIR'])
        except:
            pass

    def test_delete_analysis_success(self):
        """Test deleting an analysis successfully."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Delete the analysis
            result = service.delete_analysis(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check the result
            self.assertTrue(result)
            
            # Verify the file was deleted
            self.assertFalse(os.path.exists(self.test_file_path))

    def test_get_analyses_for_user_basic(self):
        """Test retrieving analyses for a user with basic functionality."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create a second test analysis
            second_analysis = self.test_analysis.copy()
            second_analysis['id'] = str(uuid.uuid4())
            second_analysis['analysis_name'] = "Second Test Analysis"
            
            second_file_path = os.path.join(
                self.app.config['ANALYSES_DIR'], 
                f"{second_analysis['id']}_{second_analysis['user_id']}.json"
            )
            with open(second_file_path, 'w') as f:
                json.dump(second_analysis, f)
            
            try:
                # Mock the create_analysis function to avoid actual analysis creation
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the analysis object
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Get analyses for the user
                    analyses, total_pages = service.get_analyses_for_user(self.test_analysis['user_id'])
                
                # Check the results
                self.assertGreaterEqual(len(analyses), 2)  # At least our two test analyses
                self.assertGreaterEqual(total_pages, 1)
            
            finally:
                # Clean up the second test file
                try:
                    os.remove(second_file_path)
                except:
                    pass

    def test_get_analyses_for_user_with_pagination(self):
        """Test retrieving analyses for a user with pagination."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create multiple test analyses
            analysis_files = []
            for i in range(5):
                analysis = self.test_analysis.copy()
                analysis['id'] = str(uuid.uuid4())
                analysis['analysis_name'] = f"Test Analysis {i+1}"
                
                file_path = os.path.join(
                    self.app.config['ANALYSES_DIR'], 
                    f"{analysis['id']}_{analysis['user_id']}.json"
                )
                with open(file_path, 'w') as f:
                    json.dump(analysis, f)
                
                analysis_files.append(file_path)
            
            try:
                # Mock the create_analysis function to avoid actual analysis creation
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the analysis object
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Get page 1 with 2 items per page
                    analyses_page1, total_pages = service.get_analyses_for_user(
                        self.test_analysis['user_id'],
                        page=1,
                        per_page=2
                    )
                
                # Check the results
                self.assertEqual(len(analyses_page1), 2)
                # We should have multiple pages
                self.assertGreater(total_pages, 1)
            
            finally:
                # Clean up the test files
                for file_path in analysis_files:
                    try:
                        os.remove(file_path)
                    except:
                        pass

    def test_save_analysis(self):
        """Test saving an analysis to a file."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create a test analysis
            test_analysis = {
                "id": str(uuid.uuid4()),
                "user_id": "test-user-id",
                "analysis_name": "Test Save Analysis",
                "analysis_type": "LTR",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
                "updated_at": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            # Mock the write_json function and os.replace
            with patch('services.analysis_service.write_json') as mock_write_json:
                with patch('os.replace') as mock_replace:
                    # Save the analysis
                    service._save_analysis(test_analysis, test_analysis['user_id'])
                    
                    # Verify the write_json was called
                    mock_write_json.assert_called_once()
                    # Verify os.replace was called
                    mock_replace.assert_called_once()

    def test_generate_pdf_report_mock(self):
        """Test generating a PDF report for an analysis with mocking."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the get_analysis method
            with patch.object(service, 'get_analysis', return_value=self.test_analysis):
                # Mock the create_analysis function to avoid actual calculations
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the analysis object
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Mock the standardized_metrics functions
                    with patch('utils.standardized_metrics.extract_calculated_metrics', return_value={'cash_flow': '$500'}):
                        with patch('utils.standardized_metrics.register_metrics'):
                            with patch('utils.standardized_metrics.get_metrics', return_value=None):
                                # Mock the generate_report function - use the exact import path
                                with patch('services.analysis_service.generate_report') as mock_generate_report:
                                    # Mock the return value
                                    mock_buffer = BytesIO(b'PDF data')
                                    mock_generate_report.return_value = mock_buffer
                                    
                                    # Generate the PDF report
                                    result = service.generate_pdf_report(self.test_analysis['id'], self.test_analysis['user_id'])
                                    
                                    # Verify the report generator was called
                                    mock_generate_report.assert_called_once()
                                    
                                    # Check the result
                                    self.assertEqual(result, mock_buffer)

    def test_validate_brrrr_analysis(self):
        """Test validating BRRRR analysis data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create valid BRRRR data
            valid_data = {
                "analysis_type": "BRRRR",
                "analysis_name": "Test BRRRR Analysis",
                "address": "123 Test Street",
                "purchase_price": 100000,
                "monthly_rent": 1000,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "loan1_loan_amount": 80000,
                "loan1_loan_interest_rate": 4.5,
                "loan1_loan_term": 360,
                "loan1_interest_only": False,
                "rehab_costs": 30000,
                "holding_costs": 5000,
                "after_repair_value": 150000
            }
            
            # Validate the data
            result = service.validate_analysis_data(valid_data)
            
            # Check the result
            self.assertTrue(result)
            
            # Test with invalid data (missing rehab_costs)
            invalid_data = valid_data.copy()
            invalid_data.pop("rehab_costs")
            
            # Validate the invalid data
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_normalize_brrrr_data(self):
        """Test normalizing BRRRR data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create BRRRR data with string values
            data = {
                "analysis_type": "BRRRR",
                "purchase_price": "200000",
                "monthly_rent": "1800",
                "property_taxes": "2400",
                "insurance": "1200",
                "management_fee_percentage": "8",
                "capex_percentage": "5",
                "vacancy_percentage": "5",
                "repairs_percentage": "5"
            }
            
            # Normalize the data
            normalized = service.normalize_data(data)
            
            # Check the result
            self.assertEqual(normalized["purchase_price"], 200000)
            self.assertEqual(normalized["monthly_rent"], 1800)
            self.assertEqual(normalized["property_taxes"], 2400)
            self.assertEqual(normalized["management_fee_percentage"], 8.0)
            
    def test_create_analysis_with_id(self):
        """Test creating an analysis with a provided ID."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create analysis data with ID and required fields
            analysis_data = {
                "id": str(uuid.uuid4()),
                "analysis_name": "Test Analysis with ID",
                "analysis_type": "LTR",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "address": "123 Test Street",
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5
            }
            
            # Mock the validate_analysis_data method
            with patch.object(service, 'validate_analysis_data', return_value=True):
                # Mock the normalize_data method
                with patch.object(service, 'normalize_data', return_value=analysis_data):
                    # Mock the _save_analysis method
                    with patch.object(service, '_save_analysis'):
                        # Mock create_analysis to avoid actual calculations
                        with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                            # Mock the analysis object
                            mock_analysis = MagicMock()
                            mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                            mock_create_analysis.return_value = mock_analysis
                            
                            # Create the analysis
                            result = service.create_analysis(analysis_data, "test-user-id")
                            
                            # Check the result
                            self.assertEqual(result["analysis"]["id"], analysis_data["id"])
                            self.assertEqual(result["analysis"]["analysis_name"], "Test Analysis with ID")
                        
    def test_handle_file_errors(self):
        """Test handling file errors in get_analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the open function to raise an error
            with patch('builtins.open', side_effect=IOError("File error")):
                # Try to get an analysis
                result = service.get_analysis("test-id", "test-user-id")
                
                # Check the result
                self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
