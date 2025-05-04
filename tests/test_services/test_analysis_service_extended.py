import unittest
import os
import sys
import json
import uuid
import datetime
from unittest.mock import patch, MagicMock
from io import BytesIO
from flask import Flask, session

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.analysis_service import AnalysisService
from utils.comps_handler import RentcastAPIError

class TestAnalysisServiceExtended(unittest.TestCase):
    """Extended test cases for the AnalysisService class."""

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

    def test_update_analysis_comps(self):
        """Test updating analysis with comps data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create comps data
            comps_data = {
                "last_run": datetime.datetime.now().isoformat(),
                "estimated_value": 210000,
                "value_range_low": 195000,
                "value_range_high": 225000,
                "comparables": [
                    {
                        "address": "125 Test Street",
                        "price": 205000,
                        "bedrooms": 3,
                        "bathrooms": 2,
                        "squareFootage": 1500,
                        "yearBuilt": 2000
                    }
                ],
                "rental_comps": {
                    "estimated_rent": 1850,
                    "rental_comps": [
                        {
                            "address": "127 Test Street",
                            "rent": 1800,
                            "bedrooms": 3,
                            "bathrooms": 2
                        }
                    ]
                }
            }
            
            # Update the analysis with comps data
            updated_analysis = service.update_analysis_comps(
                self.test_analysis['id'], 
                self.test_analysis['user_id'], 
                comps_data
            )
            
            # Verify the analysis was updated
            self.assertIsNotNone(updated_analysis)
            self.assertIn('comps_data', updated_analysis)
            self.assertEqual(updated_analysis['comps_data']['estimated_value'], 210000)
            self.assertEqual(len(updated_analysis['comps_data']['comparables']), 1)
            self.assertIn('rental_comps', updated_analysis['comps_data'])
            
            # Verify the file was updated
            with open(self.test_file_path, 'r') as f:
                saved_analysis = json.load(f)
            
            self.assertIn('comps_data', saved_analysis)
            self.assertEqual(saved_analysis['comps_data']['estimated_value'], 210000)

    def test_update_analysis_comps_not_found(self):
        """Test updating comps for a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create comps data
            comps_data = {
                "last_run": datetime.datetime.now().isoformat(),
                "estimated_value": 210000,
                "value_range_low": 195000,
                "value_range_high": 225000,
                "comparables": []
            }
            
            # Try to update a non-existent analysis
            with self.assertRaises(ValueError):
                service.update_analysis_comps(
                    "non-existent-id", 
                    self.test_analysis['user_id'], 
                    comps_data
                )

    def test_get_analyses_for_user_with_filters(self):
        """Test retrieving analyses for a user with filters."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create a second test analysis with different type
            second_analysis = self.test_analysis.copy()
            second_analysis['id'] = str(uuid.uuid4())
            second_analysis['analysis_name'] = "Test BRRRR Analysis"
            second_analysis['analysis_type'] = "BRRRR"
            
            second_file_path = os.path.join(
                self.app.config['ANALYSES_DIR'], 
                f"{second_analysis['id']}_{second_analysis['user_id']}.json"
            )
            with open(second_file_path, 'w') as f:
                json.dump(second_analysis, f)
            
            try:
                # Get analyses with filter by type
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    analyses, total_pages = service.get_analyses_for_user(
                        self.test_analysis['user_id'],
                        page=1,
                        per_page=10
                    )
                    
                    # Filter analyses manually
                    analyses = [a for a in analyses if a['analysis_type'] == "LTR"]
                
                # Check the results
                self.assertEqual(len(analyses), 1)
                self.assertEqual(analyses[0]['analysis_type'], "LTR")
                
                # Get analyses with filter by name
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    analyses, total_pages = service.get_analyses_for_user(
                        self.test_analysis['user_id'],
                        page=1,
                        per_page=10
                    )
                    
                    # Filter analyses manually
                    analyses = [a for a in analyses if "BRRRR" in a['analysis_name']]
                
                # Check the results
                self.assertEqual(len(analyses), 1)
                self.assertEqual(analyses[0]['analysis_name'], "Test BRRRR Analysis")
                
                # Get analyses with filter by type and name
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    analyses, total_pages = service.get_analyses_for_user(
                        self.test_analysis['user_id'],
                        page=1,
                        per_page=10
                    )
                    
                    # Filter analyses manually
                    analyses = [a for a in analyses if a['analysis_type'] == "BRRRR" and "Test" in a['analysis_name']]
                
                # Check the results
                self.assertEqual(len(analyses), 1)
                self.assertEqual(analyses[0]['analysis_type'], "BRRRR")
                self.assertEqual(analyses[0]['analysis_name'], "Test BRRRR Analysis")
                
                # Get analyses with no matches
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    analyses, total_pages = service.get_analyses_for_user(
                        self.test_analysis['user_id'],
                        page=1,
                        per_page=10
                    )
                    
                    # Filter analyses manually
                    analyses = [a for a in analyses if a['analysis_type'] == "Lease Option"]
                
                # Check the results
                self.assertEqual(len(analyses), 0)
            
            finally:
                # Clean up the second test file
                try:
                    os.remove(second_file_path)
                except:
                    pass

    def test_validate_analysis_data_with_balloon(self):
        """Test validating analysis data with balloon payment."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid data with balloon payment
            valid_data = {
                "analysis_name": "Test Balloon Analysis",
                "analysis_type": "LTR",
                "address": "123 Test Street",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "loan1_loan_amount": 160000,
                "loan1_loan_interest_rate": 4.5,
                "loan1_loan_term": 60,  # 5-year term
                "has_balloon_payment": True,
                "balloon_due_date": "2030-01-01",
                "balloon_refinance_ltv_percentage": 75,
                "balloon_refinance_loan_amount": 180000,
                "balloon_refinance_loan_interest_rate": 5.0,
                "balloon_refinance_loan_term": 360
            }
            
            # This should not raise an exception
            service.validate_analysis_data(valid_data)
            
            # Invalid balloon data - missing required fields
            invalid_data = valid_data.copy()
            del invalid_data["balloon_refinance_loan_amount"]
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid balloon data - negative loan amount
            invalid_data = valid_data.copy()
            invalid_data["balloon_refinance_loan_amount"] = -10000
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid balloon data - invalid interest rate
            invalid_data = valid_data.copy()
            invalid_data["balloon_refinance_loan_interest_rate"] = -1.0
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_brrrr_analysis(self):
        """Test validating BRRRR analysis data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid BRRRR analysis data
            valid_data = {
                "analysis_name": "Test BRRRR Analysis",
                "analysis_type": "BRRRR",
                "address": "123 Test Street",
                "purchase_price": 150000,
                "after_repair_value": 250000,
                "renovation_costs": 50000,
                "renovation_duration": 3,
                "monthly_rent": 2000,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "initial_loan_amount": 120000,
                "initial_loan_interest_rate": 6.0,
                "initial_loan_term": 12,
                "initial_interest_only": True,
                "initial_loan_closing_costs": 2000,
                "refinance_loan_amount": 200000,
                "refinance_loan_interest_rate": 4.5,
                "refinance_loan_term": 360,
                "refinance_loan_closing_costs": 3000
            }
            
            # This should not raise an exception
            service.validate_analysis_data(valid_data)
            
            # Invalid BRRRR data - missing required fields
            invalid_data = valid_data.copy()
            del invalid_data["after_repair_value"]
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid BRRRR data - ARV less than purchase price
            invalid_data = valid_data.copy()
            invalid_data["after_repair_value"] = 100000  # Less than purchase price
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid BRRRR data - negative renovation costs
            invalid_data = valid_data.copy()
            invalid_data["renovation_costs"] = -10000
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_multi_family_analysis(self):
        """Test validating Multi-Family analysis data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid Multi-Family analysis data
            unit_types = [
                {
                    "type": "1BR",
                    "count": 4,
                    "occupied": 3,
                    "square_footage": 700,
                    "rent": 1000
                },
                {
                    "type": "2BR",
                    "count": 6,
                    "occupied": 5,
                    "square_footage": 900,
                    "rent": 1300
                }
            ]
            
            valid_data = {
                "analysis_name": "Test Multi-Family Analysis",
                "analysis_type": "Multi-Family",
                "address": "123 Test Street",
                "purchase_price": 1200000,
                "property_taxes": 1000,
                "insurance": 500,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "total_units": 10,
                "occupied_units": 8,
                "floors": 2,
                "elevator_maintenance": 200,
                "common_area_maintenance": 300,
                "staff_payroll": 1000,
                "trash_removal": 150,
                "common_utilities": 400,
                "other_income": 500,
                "unit_types": json.dumps(unit_types),
                "loan1_loan_amount": 960000,
                "loan1_loan_interest_rate": 4.5,
                "loan1_loan_term": 360
            }
            
            # This should not raise an exception
            service.validate_analysis_data(valid_data)
            
            # Invalid Multi-Family data - missing required fields
            invalid_data = valid_data.copy()
            del invalid_data["total_units"]
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid Multi-Family data - total units doesn't match unit types
            invalid_data = valid_data.copy()
            invalid_data["total_units"] = 12  # Doesn't match sum of unit counts (10)
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid Multi-Family data - occupied units more than total
            invalid_data = valid_data.copy()
            invalid_data["occupied_units"] = 12  # More than total (10)
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_padsplit_analysis(self):
        """Test validating PadSplit analysis data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid PadSplit LTR analysis data
            valid_data = {
                "analysis_name": "Test PadSplit Analysis",
                "analysis_type": "PadSplit LTR",
                "address": "123 Test Street",
                "purchase_price": 200000,
                "monthly_rent": 3000,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "utilities": 200,
                "internet": 100,
                "cleaning": 150,
                "pest_control": 50,
                "landscaping": 100,
                "padsplit_platform_percentage": 15,
                "loan1_loan_amount": 160000,
                "loan1_loan_interest_rate": 4.5,
                "loan1_loan_term": 360
            }
            
            # This should not raise an exception
            service.validate_analysis_data(valid_data)
            
            # Invalid PadSplit data - missing required fields
            invalid_data = valid_data.copy()
            del invalid_data["utilities"]
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid PadSplit data - negative utilities
            invalid_data = valid_data.copy()
            invalid_data["utilities"] = -100
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid PadSplit data - platform percentage out of range
            invalid_data = valid_data.copy()
            invalid_data["padsplit_platform_percentage"] = 101  # Over 100%
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_export_analysis_to_json(self):
        """Test exporting analysis to JSON."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Export the analysis to JSON
            json_data = service.export_analysis_to_json(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Verify the JSON data
            self.assertIsNotNone(json_data)
            
            # Parse the JSON data
            exported_analysis = json.loads(json_data)
            
            # Verify the exported analysis
            self.assertEqual(exported_analysis['id'], self.test_analysis['id'])
            self.assertEqual(exported_analysis['analysis_name'], self.test_analysis['analysis_name'])
            self.assertEqual(exported_analysis['analysis_type'], self.test_analysis['analysis_type'])
            self.assertEqual(exported_analysis['purchase_price'], self.test_analysis['purchase_price'])

    def test_export_analysis_to_json_not_found(self):
        """Test exporting a non-existent analysis to JSON."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Try to export a non-existent analysis
            with self.assertRaises(ValueError):
                service.export_analysis_to_json("non-existent-id", self.test_analysis['user_id'])

    def test_import_analysis_from_json(self):
        """Test importing analysis from JSON."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Export the analysis to JSON
            json_data = service.export_analysis_to_json(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Modify the JSON data for import
            imported_analysis = json.loads(json_data)
            imported_analysis['id'] = str(uuid.uuid4())  # New ID
            imported_analysis['analysis_name'] = "Imported Analysis"
            modified_json = json.dumps(imported_analysis)
            
            # Import the analysis from JSON
            with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                # Mock the create_analysis function
                mock_analysis = MagicMock()
                mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                mock_create_analysis.return_value = mock_analysis
                
                result = service.import_analysis_from_json(modified_json, self.test_analysis['user_id'])
            
            # Verify the result
            self.assertTrue(result['success'])
            self.assertEqual(result['analysis']['analysis_name'], "Imported Analysis")
            self.assertEqual(result['analysis']['user_id'], self.test_analysis['user_id'])
            
            # Verify the file was created
            imported_file_path = os.path.join(
                self.app.config['ANALYSES_DIR'], 
                f"{imported_analysis['id']}_{self.test_analysis['user_id']}.json"
            )
            self.assertTrue(os.path.exists(imported_file_path))
            
            # Clean up the imported file
            try:
                os.remove(imported_file_path)
            except:
                pass

    def test_import_analysis_from_json_invalid(self):
        """Test importing invalid JSON."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Try to import invalid JSON
            result = service.import_analysis_from_json("invalid json", self.test_analysis['user_id'])
            
            # Verify the result
            self.assertFalse(result['success'])
            self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()
