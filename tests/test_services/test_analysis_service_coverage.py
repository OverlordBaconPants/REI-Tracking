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

class TestAnalysisServiceCoverage(unittest.TestCase):
    """Test cases for the AnalysisService class focused on improving coverage."""

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

    def test_normalize_data_with_various_types(self):
        """Test normalizing analysis data with various data types."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with various types
            test_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "purchase_price": "200000",  # String that should be converted to int
                "monthly_rent": "1800.50",   # String that should be converted to float
                "loan1_interest_only": "true",  # String that should be converted to boolean
                "management_fee_percentage": "8.5",  # String that should be converted to float
                "has_balloon_payment": True,
                "balloon_due_date": "2025-01-01",
                "balloon_refinance_loan_amount": "150000"
            }
            
            # Normalize the data
            normalized = service.normalize_data(test_data)
            
            # Check conversions
            self.assertEqual(normalized["purchase_price"], 200000)
            self.assertEqual(normalized["monthly_rent"], 1800)  # Float converted to int
            self.assertEqual(normalized["loan1_interest_only"], True)
            self.assertEqual(normalized["management_fee_percentage"], 8.5)
            self.assertEqual(normalized["has_balloon_payment"], True)
            self.assertEqual(normalized["balloon_due_date"], "2025-01-01")
            self.assertEqual(normalized["balloon_refinance_loan_amount"], 150000)

    def test_normalize_data_with_mobile_flag(self):
        """Test normalizing analysis data with mobile flag."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data
            test_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "purchase_price": 200000,
                "monthly_rent": 1800
            }
            
            # Normalize the data with mobile flag
            normalized = service.normalize_data(test_data, is_mobile=True)
            
            # Check that the data was normalized correctly
            self.assertEqual(normalized["analysis_name"], "Test Analysis")
            self.assertEqual(normalized["analysis_type"], "LTR")
            self.assertEqual(normalized["purchase_price"], 200000)
            self.assertEqual(normalized["monthly_rent"], 1800)

    def test_normalize_data_with_balloon_payment(self):
        """Test normalizing analysis data with balloon payment."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with balloon payment
            test_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "has_balloon_payment": True,
                "balloon_due_date": "2025-01-01",
                "balloon_refinance_loan_amount": 150000,
                "balloon_refinance_loan_interest_rate": 4.5,
                "balloon_refinance_loan_term": 360
            }
            
            # Normalize the data
            normalized = service.normalize_data(test_data)
            
            # Check balloon payment fields
            self.assertTrue(normalized["has_balloon_payment"])
            self.assertEqual(normalized["balloon_due_date"], "2025-01-01")
            self.assertEqual(normalized["balloon_refinance_loan_amount"], 150000)
            self.assertEqual(normalized["balloon_refinance_loan_interest_rate"], 4.5)
            self.assertEqual(normalized["balloon_refinance_loan_term"], 360)
            
            # Test with has_balloon_payment = False
            test_data["has_balloon_payment"] = False
            normalized = service.normalize_data(test_data)
            
            # Check balloon fields are zeroed out
            self.assertFalse(normalized["has_balloon_payment"])
            self.assertEqual(normalized["balloon_refinance_loan_amount"], 0)
            self.assertIsNone(normalized["balloon_due_date"])

    def test_normalize_data_with_lease_option(self):
        """Test normalizing analysis data with lease option."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with lease option
            test_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "Lease Option",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "option_consideration_fee": 5000,
                "option_term_months": 24,
                "strike_price": 220000,
                "monthly_rent_credit_percentage": 25,
                "rent_credit_cap": 10000
            }
            
            # Normalize the data
            normalized = service.normalize_data(test_data)
            
            # Check lease option fields
            self.assertEqual(normalized["option_consideration_fee"], 5000)
            self.assertEqual(normalized["option_term_months"], 24)
            self.assertEqual(normalized["strike_price"], 220000)
            self.assertEqual(normalized["monthly_rent_credit_percentage"], 25.0)
            self.assertEqual(normalized["rent_credit_cap"], 10000)
            
            # Test with non-lease option analysis type
            test_data["analysis_type"] = "LTR"
            normalized = service.normalize_data(test_data)
            
            # Check lease option fields are zeroed out
            self.assertEqual(normalized["option_consideration_fee"], 0)
            self.assertEqual(normalized["option_term_months"], 0)
            self.assertEqual(normalized["strike_price"], 0)
            self.assertEqual(normalized["monthly_rent_credit_percentage"], 0.0)
            self.assertEqual(normalized["rent_credit_cap"], 0)

    def test_normalize_data_with_special_formats(self):
        """Test normalizing analysis data with special formats."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with special formats
            test_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "id": "",  # Empty UUID should be generated
                "created_at": ""  # Empty datetime should be generated
            }
            
            # Normalize the data
            normalized = service.normalize_data(test_data)
            
            # Check UUID and datetime fields
            self.assertTrue(uuid.UUID(normalized["id"]))  # Valid UUID
            self.assertTrue(normalized["created_at"])  # Non-empty datetime

    def test_validate_analysis_data_valid_ltr(self):
        """Test validating valid LTR analysis data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid LTR analysis data
            valid_data = {
                "analysis_name": "Test LTR Analysis",
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
                "loan1_loan_term": 360
            }
            
            # This should not raise an exception
            service.validate_analysis_data(valid_data)

    def test_validate_analysis_data_invalid_missing_fields(self):
        """Test validating analysis data with missing required fields."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Missing required fields
            invalid_data = {
                "analysis_name": "Test Analysis"
                # Missing analysis_type
            }
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_analysis_data_invalid_rent(self):
        """Test validating analysis data with invalid rent."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Invalid monthly rent
            invalid_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "monthly_rent": -100  # Negative rent
            }
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_lease_option_valid(self):
        """Test validating valid lease option data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid lease option data
            valid_data = {
                "analysis_name": "Test Lease Option",
                "analysis_type": "Lease Option",
                "address": "123 Test Street",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "option_consideration_fee": 5000,
                "option_term_months": 24,
                "strike_price": 220000,  # Higher than purchase price
                "monthly_rent_credit_percentage": 25,
                "rent_credit_cap": 10000
            }
            
            # This should not raise an exception
            service.validate_analysis_data(valid_data)

    def test_validate_lease_option_invalid_strike_price(self):
        """Test validating lease option data with invalid strike price."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Invalid lease option - strike price <= purchase price
            invalid_data = {
                "analysis_name": "Test Lease Option",
                "analysis_type": "Lease Option",
                "address": "123 Test Street",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "option_consideration_fee": 5000,
                "option_term_months": 24,
                "strike_price": 190000,  # Lower than purchase price
                "monthly_rent_credit_percentage": 25,
                "rent_credit_cap": 10000
            }
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_lease_option_invalid_option_fee(self):
        """Test validating lease option data with invalid option fee."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Invalid lease option - negative option fee
            invalid_data = {
                "analysis_name": "Test Lease Option",
                "analysis_type": "Lease Option",
                "address": "123 Test Street",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "option_consideration_fee": -1000,  # Negative option fee
                "option_term_months": 24,
                "strike_price": 220000,
                "monthly_rent_credit_percentage": 25,
                "rent_credit_cap": 10000
            }
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_lease_option_invalid_rent_credit_percentage(self):
        """Test validating lease option data with invalid rent credit percentage."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Invalid lease option - rent credit percentage > 100
            invalid_data = {
                "analysis_name": "Test Lease Option",
                "analysis_type": "Lease Option",
                "address": "123 Test Street",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "property_taxes": 200,
                "insurance": 100,
                "management_fee_percentage": 8,
                "capex_percentage": 5,
                "vacancy_percentage": 5,
                "repairs_percentage": 5,
                "option_consideration_fee": 5000,
                "option_term_months": 24,
                "strike_price": 220000,
                "monthly_rent_credit_percentage": 110,  # > 100%
                "rent_credit_cap": 10000
            }
            
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

    def test_validate_loans(self):
        """Test validating loan data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid loan data
            valid_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "address": "123 Test Street",
                "purchase_price": 200000,
                "monthly_rent": 1800,
                "loan1_loan_amount": 160000,
                "loan1_loan_interest_rate": 4.5,
                "loan1_loan_term": 360,
                "loan2_loan_amount": 20000,
                "loan2_loan_interest_rate": 6.0,
                "loan2_loan_term": 120
            }
            
            # This should not raise an exception
            service._validate_loans(valid_data)
            
            # Invalid loan data - interest rate > 30%
            invalid_data = valid_data.copy()
            invalid_data["loan1_loan_interest_rate"] = 35.0
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_loans(invalid_data)
            
            # Invalid loan data - loan term > 360 months
            invalid_data = valid_data.copy()
            invalid_data["loan1_loan_term"] = 400
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_loans(invalid_data)

    def test_validate_field_type(self):
        """Test validating field types."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test integer field
            service._validate_field_type("purchase_price", 200000)
            service._validate_field_type("purchase_price", "200000")  # String that can be converted to int
            
            # Test float field
            service._validate_field_type("management_fee_percentage", 8.5)
            service._validate_field_type("management_fee_percentage", "8.5")  # String that can be converted to float
            
            # Test string field
            service._validate_field_type("analysis_name", "Test Analysis")
            service._validate_field_type("analysis_name", 123)  # Non-string that can be converted to string
            
            # Test boolean field
            service._validate_field_type("has_balloon_payment", True)
            service._validate_field_type("has_balloon_payment", "true")  # String that can be converted to boolean
            service._validate_field_type("has_balloon_payment", 1)  # Integer that can be converted to boolean
            
            # Test invalid boolean
            with self.assertRaises(ValueError):
                service._validate_field_type("has_balloon_payment", "not a boolean")

    def test_create_analysis(self):
        """Test creating a new analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the create_analysis function
            with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                mock_analysis = MagicMock()
                mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                mock_create_analysis.return_value = mock_analysis
                
                # Mock the register_metrics function
                with patch('utils.standardized_metrics.register_metrics') as mock_register_metrics:
                    # Mock the _save_analysis method
                    with patch.object(service, '_save_analysis') as mock_save:
                        # Test data
                        test_data = {
                            "analysis_name": "New Test Analysis",
                            "analysis_type": "LTR",
                            "address": "456 New Street",
                            "purchase_price": 250000,
                            "monthly_rent": 2000,
                            "property_taxes": 250,
                            "insurance": 120,
                            "management_fee_percentage": 8,
                            "capex_percentage": 5,
                            "vacancy_percentage": 5,
                            "repairs_percentage": 5,
                            "loan1_loan_amount": 200000,
                            "loan1_loan_interest_rate": 4.25,
                            "loan1_loan_term": 360
                        }
                        
                        # Create the analysis
                        result = service.create_analysis(test_data, "test-user-id")
                        
                        # Check the result
                        self.assertTrue(result['success'])
                        self.assertEqual(result['analysis']['analysis_name'], "New Test Analysis")
                        self.assertEqual(result['analysis']['analysis_type'], "LTR")
                        self.assertEqual(result['analysis']['purchase_price'], 250000)
                        self.assertEqual(result['analysis']['calculated_metrics'], {'cash_flow': '$500'})
                        
                        # Verify mocks were called
                        mock_create_analysis.assert_called_once()
                        mock_register_metrics.assert_called_once()
                        mock_save.assert_called_once()

    def test_update_analysis(self):
        """Test updating an existing analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the get_analysis method
            with patch.object(service, 'get_analysis', return_value=self.test_analysis):
                # Mock the create_analysis function
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$600'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Mock the register_metrics function
                    with patch('utils.standardized_metrics.register_metrics') as mock_register_metrics:
                        # Mock the _save_analysis method
                        with patch.object(service, '_save_analysis') as mock_save:
                            # Mock the _log_balloon_data and _log_comps_data methods
                            with patch.object(service, '_log_balloon_data') as mock_log_balloon:
                                with patch.object(service, '_log_comps_data') as mock_log_comps:
                                    # Test data for update
                                    update_data = self.test_analysis.copy()
                                    update_data["monthly_rent"] = 2000  # Increase rent
                                    
                                    # Update the analysis
                                    result = service.update_analysis(update_data, "test-user-id")
                                    
                                    # Check the result
                                    self.assertTrue(result['success'])
                                    self.assertEqual(result['analysis']['monthly_rent'], 2000)
                                    self.assertEqual(result['analysis']['calculated_metrics'], {'cash_flow': '$600'})
                                    
                                    # Verify mocks were called
                                    mock_create_analysis.assert_called_once()
                                    mock_register_metrics.assert_called_once()
                                    mock_save.assert_called_once()
                                    mock_log_balloon.assert_called_once()
                                    mock_log_comps.assert_called_once()

    def test_update_analysis_missing_id(self):
        """Test updating an analysis with missing ID."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data without ID
            update_data = self.test_analysis.copy()
            del update_data["id"]
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.update_analysis(update_data, "test-user-id")

    def test_update_analysis_not_found(self):
        """Test updating a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the get_analysis method to return None
            with patch.object(service, 'get_analysis', return_value=None):
                # Test data with non-existent ID
                update_data = self.test_analysis.copy()
                update_data["id"] = "non-existent-id"
                
                # This should raise a ValueError
                with self.assertRaises(ValueError):
                    service.update_analysis(update_data, "test-user-id")

    def test_get_analysis(self):
        """Test retrieving an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Get the analysis
            with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                # Mock the create_analysis function
                mock_analysis = MagicMock()
                mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                mock_create_analysis.return_value = mock_analysis
                
                # Mock the register_metrics function
                with patch('utils.standardized_metrics.register_metrics') as mock_register_metrics:
                    analysis = service.get_analysis(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check if the analysis was retrieved
            self.assertIsNotNone(analysis)
            self.assertEqual(analysis['id'], self.test_analysis['id'])
            self.assertEqual(analysis['analysis_name'], self.test_analysis['analysis_name'])
            self.assertEqual(analysis['analysis_type'], self.test_analysis['analysis_type'])
            self.assertEqual(analysis['purchase_price'], self.test_analysis['purchase_price'])
            self.assertEqual(analysis['calculated_metrics'], {'cash_flow': '$500'})

    def test_get_analysis_not_found(self):
        """Test retrieving a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Try to get a non-existent analysis
            analysis = service.get_analysis("non-existent-id", "test-user-id")
            
            # Check that None is returned
            self.assertIsNone(analysis)

    def test_get_analysis_brrrr_refinance(self):
        """Test retrieving a BRRRR analysis with refinance loan."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create a BRRRR analysis with refinance loan
            brrrr_analysis = self.test_analysis.copy()
            brrrr_analysis['id'] = str(uuid.uuid4())
            brrrr_analysis['analysis_type'] = "BRRRR"
            brrrr_analysis['refinance_loan_amount'] = 180000
            brrrr_analysis['refinance_loan_interest_rate'] = 4.0
            brrrr_analysis['refinance_loan_term'] = 360
            
            # Create a test file for the BRRRR analysis
            brrrr_file_path = os.path.join(
                self.app.config['ANALYSES_DIR'], 
                f"{brrrr_analysis['id']}_{brrrr_analysis['user_id']}.json"
            )
            with open(brrrr_file_path, 'w') as f:
                json.dump(brrrr_analysis, f)
            
            try:
                # Get the analysis
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$600'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    # Mock the register_metrics function
                    with patch('utils.standardized_metrics.register_metrics') as mock_register_metrics:
                        # Mock the FinancialCalculator.calculate_loan_payment method
                        with patch('utils.financial_calculator.FinancialCalculator.calculate_loan_payment') as mock_calculate_payment:
                            # Mock the payment object
                            mock_payment = MagicMock()
                            mock_payment.total = 859.35
                            mock_calculate_payment.return_value = mock_payment
                            
                            analysis = service.get_analysis(brrrr_analysis['id'], brrrr_analysis['user_id'])
                
                # Check if the analysis was retrieved
                self.assertIsNotNone(analysis)
                self.assertEqual(analysis['analysis_type'], "BRRRR")
                self.assertEqual(analysis['refinance_loan_amount'], 180000)
                self.assertEqual(analysis['refinance_loan_interest_rate'], 4.0)
                self.assertEqual(analysis['refinance_loan_term'], 360)
                
                # Check that refinance_loan_payment is in calculated_metrics
                self.assertIn('refinance_loan_payment', analysis['calculated_metrics'])
            
            finally:
                # Clean up the BRRRR test file
                try:
                    os.remove(brrrr_file_path)
                except:
                    pass
