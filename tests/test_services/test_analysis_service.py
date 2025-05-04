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

class TestAnalysisService(unittest.TestCase):
    """Test cases for the AnalysisService class."""

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

    def test_normalize_data(self):
        """Test normalizing analysis data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with various types
            test_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "purchase_price": "200000",  # String that should be converted to int
                "monthly_rent": 1800.50,     # Float that should be preserved
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
            self.assertEqual(normalized["monthly_rent"], 1800.50)
            self.assertEqual(normalized["loan1_interest_only"], True)
            self.assertEqual(normalized["management_fee_percentage"], 8.5)
            self.assertEqual(normalized["has_balloon_payment"], True)
            self.assertEqual(normalized["balloon_due_date"], "2025-01-01")
            self.assertEqual(normalized["balloon_refinance_loan_amount"], 150000)
            
            # Test with has_balloon_payment = False
            test_data["has_balloon_payment"] = False
            normalized = service.normalize_data(test_data)
            
            # Check balloon fields are zeroed out
            self.assertEqual(normalized["balloon_refinance_loan_amount"], 0)
            self.assertIsNone(normalized["balloon_due_date"])

    def test_validate_analysis_data_valid(self):
        """Test validating valid analysis data."""
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

    def test_validate_analysis_data_invalid(self):
        """Test validating invalid analysis data."""
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
            
            # Invalid monthly rent
            invalid_data = {
                "analysis_name": "Test Analysis",
                "analysis_type": "LTR",
                "monthly_rent": -100  # Negative rent
            }
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    def test_validate_lease_option(self):
        """Test validating lease option data."""
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
            
            # Invalid lease option - strike price <= purchase price
            invalid_data = valid_data.copy()
            invalid_data["strike_price"] = 190000  # Lower than purchase price
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid lease option - negative option fee
            invalid_data = valid_data.copy()
            invalid_data["option_consideration_fee"] = -1000
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)
            
            # Invalid lease option - rent credit percentage > 100
            invalid_data = valid_data.copy()
            invalid_data["monthly_rent_credit_percentage"] = 110
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_data)

    @patch('services.analysis_service.create_analysis')
    @patch('utils.standardized_metrics.register_metrics')
    def test_create_analysis(self, mock_register_metrics, mock_create_analysis):
        """Test creating a new analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the create_analysis function
            mock_analysis = MagicMock()
            mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
            mock_create_analysis.return_value = mock_analysis
            
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

    @patch('services.analysis_service.create_analysis')
    @patch('utils.standardized_metrics.register_metrics')
    def test_update_analysis(self, mock_register_metrics, mock_create_analysis):
        """Test updating an existing analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the create_analysis function
            mock_analysis = MagicMock()
            mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$600'}}
            mock_create_analysis.return_value = mock_analysis
            
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

    def test_delete_analysis(self):
        """Test deleting an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Delete the analysis
            result = service.delete_analysis(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check the result
            self.assertTrue(result)
            
            # Verify the file was deleted
            self.assertFalse(os.path.exists(self.test_file_path))

    def test_delete_analysis_not_found(self):
        """Test deleting a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Try to delete a non-existent analysis
            with self.assertRaises(ValueError):
                service.delete_analysis("non-existent-id", "test-user-id")
    
    def test_refinance_analysis(self):
        """Test refinancing an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Refinance data
            refinance_data = {
                "refinance_loan_amount": 180000,
                "refinance_loan_interest_rate": 4.0,
                "refinance_loan_term": 360,
                "refinance_loan_closing_costs": 3500,
                "refinance_date": datetime.datetime.now().strftime("%Y-%m-%d")
            }
            
            # Mock get_analysis to return our test analysis
            with patch.object(service, 'get_analysis', return_value=self.test_analysis):
                # Mock _save_analysis to avoid file operations
                with patch.object(service, '_save_analysis') as mock_save:
                    # Mock create_analysis to return a mock analysis object
                    with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                        mock_analysis = MagicMock()
                        mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$600'}}
                        mock_create_analysis.return_value = mock_analysis
                        
                        # Perform the refinance
                        result = service.refinance_analysis(self.test_analysis['id'], self.test_analysis['user_id'], refinance_data)
            
            # Check the result
            self.assertTrue(result['success'])
            self.assertEqual(result['analysis']['refinance_loan_amount'], 180000)
            self.assertEqual(result['analysis']['refinance_loan_interest_rate'], 4.0)
            self.assertEqual(result['analysis']['refinance_loan_term'], 360)
            self.assertEqual(result['analysis']['refinance_loan_closing_costs'], 3500)
            self.assertIn('refinance_date', result['analysis'])
            self.assertEqual(result['analysis']['calculated_metrics'], {'cash_flow': '$600'})
    
    def test_refinance_analysis_not_found(self):
        """Test refinancing a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Refinance data
            refinance_data = {
                "refinance_loan_amount": 180000,
                "refinance_loan_interest_rate": 4.0,
                "refinance_loan_term": 360,
                "refinance_loan_closing_costs": 3500
            }
            
            # Mock get_analysis to return None (analysis not found)
            with patch.object(service, 'get_analysis', return_value=None):
                # Perform the refinance
                result = service.refinance_analysis("non-existent-id", "test-user-id", refinance_data)
            
            # Check the result
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], "Analysis not found")
    
    def test_add_balloon_payment(self):
        """Test adding a balloon payment to an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Balloon payment data
            balloon_data = {
                "has_balloon_payment": True,
                "balloon_due_date": (datetime.datetime.now() + datetime.timedelta(days=365*5)).strftime("%Y-%m-%d"),
                "balloon_refinance_loan_amount": 150000,
                "balloon_refinance_loan_interest_rate": 4.25,
                "balloon_refinance_loan_term": 360,
                "balloon_refinance_loan_closing_costs": 3000
            }
            
            # Mock get_analysis to return our test analysis
            with patch.object(service, 'get_analysis', return_value=self.test_analysis):
                # Mock _save_analysis to avoid file operations
                with patch.object(service, '_save_analysis') as mock_save:
                    # Mock create_analysis to return a mock analysis object
                    with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                        mock_analysis = MagicMock()
                        mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$550'}}
                        mock_create_analysis.return_value = mock_analysis
                        
                        # Add the balloon payment
                        result = service.add_balloon_payment(self.test_analysis['id'], self.test_analysis['user_id'], balloon_data)
            
            # Check the result
            self.assertTrue(result['success'])
            self.assertTrue(result['analysis']['has_balloon_payment'])
            self.assertEqual(result['analysis']['balloon_refinance_loan_amount'], 150000)
            self.assertEqual(result['analysis']['balloon_refinance_loan_interest_rate'], 4.25)
            self.assertEqual(result['analysis']['balloon_refinance_loan_term'], 360)
            self.assertEqual(result['analysis']['balloon_refinance_loan_closing_costs'], 3000)
            self.assertIn('balloon_due_date', result['analysis'])
            self.assertEqual(result['analysis']['calculated_metrics'], {'cash_flow': '$550'})
    
    def test_add_balloon_payment_not_found(self):
        """Test adding a balloon payment to a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Balloon payment data
            balloon_data = {
                "has_balloon_payment": True,
                "balloon_due_date": (datetime.datetime.now() + datetime.timedelta(days=365*5)).strftime("%Y-%m-%d"),
                "balloon_refinance_loan_amount": 150000,
                "balloon_refinance_loan_interest_rate": 4.25,
                "balloon_refinance_loan_term": 360,
                "balloon_refinance_loan_closing_costs": 3000
            }
            
            # Mock get_analysis to return None (analysis not found)
            with patch.object(service, 'get_analysis', return_value=None):
                # Add the balloon payment
                result = service.add_balloon_payment("non-existent-id", "test-user-id", balloon_data)
            
            # Check the result
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], "Analysis not found")
    
    def test_remove_balloon_payment(self):
        """Test removing a balloon payment from an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create a test analysis with a balloon payment
            analysis_with_balloon = self.test_analysis.copy()
            analysis_with_balloon['has_balloon_payment'] = True
            analysis_with_balloon['balloon_due_date'] = (datetime.datetime.now() + datetime.timedelta(days=365*5)).strftime("%Y-%m-%d")
            analysis_with_balloon['balloon_refinance_loan_amount'] = 150000
            analysis_with_balloon['balloon_refinance_loan_interest_rate'] = 4.25
            analysis_with_balloon['balloon_refinance_loan_term'] = 360
            analysis_with_balloon['balloon_refinance_loan_closing_costs'] = 3000
            
            # Mock get_analysis to return our test analysis with balloon
            with patch.object(service, 'get_analysis', return_value=analysis_with_balloon):
                # Mock _save_analysis to avoid file operations
                with patch.object(service, '_save_analysis') as mock_save:
                    # Mock create_analysis to return a mock analysis object
                    with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                        mock_analysis = MagicMock()
                        mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                        mock_create_analysis.return_value = mock_analysis
                        
                        # Remove the balloon payment
                        result = service.remove_balloon_payment(analysis_with_balloon['id'], analysis_with_balloon['user_id'])
            
            # Check the result
            self.assertTrue(result['success'])
            self.assertFalse(result['analysis']['has_balloon_payment'])
            self.assertEqual(result['analysis']['balloon_refinance_loan_amount'], 0)
            self.assertIsNone(result['analysis']['balloon_due_date'])
            self.assertEqual(result['analysis']['calculated_metrics'], {'cash_flow': '$500'})
    
    def test_remove_balloon_payment_not_found(self):
        """Test removing a balloon payment from a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis to return None (analysis not found)
            with patch.object(service, 'get_analysis', return_value=None):
                # Remove the balloon payment
                result = service.remove_balloon_payment("non-existent-id", "test-user-id")
            
            # Check the result
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], "Analysis not found")
    
    def test_duplicate_analysis(self):
        """Test duplicating an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis to return our test analysis
            with patch.object(service, 'get_analysis', return_value=self.test_analysis):
                # Mock _save_analysis to avoid file operations
                with patch.object(service, '_save_analysis') as mock_save:
                    # Mock uuid.uuid4 to return a predictable value
                    with patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345679')):
                        # Mock create_analysis to return a mock analysis object
                        with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                            mock_analysis = MagicMock()
                            mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                            mock_create_analysis.return_value = mock_analysis
                            
                            # Duplicate the analysis
                            result = service.duplicate_analysis(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check the result
            self.assertTrue(result['success'])
            self.assertEqual(result['analysis']['id'], '12345678-1234-5678-1234-567812345679')
            self.assertEqual(result['analysis']['analysis_name'], "Copy of Test LTR Analysis")
            self.assertEqual(result['analysis']['analysis_type'], self.test_analysis['analysis_type'])
            self.assertEqual(result['analysis']['purchase_price'], self.test_analysis['purchase_price'])
            self.assertEqual(result['analysis']['calculated_metrics'], {'cash_flow': '$500'})
    
    def test_duplicate_analysis_not_found(self):
        """Test duplicating a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis to return None (analysis not found)
            with patch.object(service, 'get_analysis', return_value=None):
                # Duplicate the analysis
                result = service.duplicate_analysis("non-existent-id", "test-user-id")
            
            # Check the result
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], "Analysis not found")
    
    def test_search_analyses(self):
        """Test searching analyses."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create a second test analysis
            second_analysis = self.test_analysis.copy()
            second_analysis['id'] = str(uuid.uuid4())
            second_analysis['analysis_name'] = "Investment Property on Oak Street"
            second_analysis['address'] = "456 Oak Street, Test City, TS 12345"
            
            second_file_path = os.path.join(
                self.app.config['ANALYSES_DIR'], 
                f"{second_analysis['id']}_{second_analysis['user_id']}.json"
            )
            with open(second_file_path, 'w') as f:
                json.dump(second_analysis, f)
            
            try:
                # Search for analyses with "Test" in the name
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    results = service.search_analyses(self.test_analysis['user_id'], "Test")
                
                # Check the results
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['analysis_name'], "Test LTR Analysis")
                
                # Search for analyses with "Oak" in the name or address
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    results = service.search_analyses(self.test_analysis['user_id'], "Oak")
                
                # Check the results
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]['analysis_name'], "Investment Property on Oak Street")
                
                # Search for analyses with "Street" in the address
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    results = service.search_analyses(self.test_analysis['user_id'], "Street")
                
                # Check the results
                self.assertEqual(len(results), 2)  # Both analyses have "Street" in the address
                
                # Search for analyses with no match
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    results = service.search_analyses(self.test_analysis['user_id'], "NoMatch")
                
                # Check the results
                self.assertEqual(len(results), 0)
            
            finally:
                # Clean up the second test file
                try:
                    os.remove(second_file_path)
                except:
                    pass

    @patch('services.analysis_service.fetch_property_comps')
    @patch('services.analysis_service.fetch_rental_comps')
    def test_run_comps_by_address(self, mock_fetch_rental_comps, mock_fetch_property_comps):
        """Test running comps by address."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the fetch_property_comps function
            mock_fetch_property_comps.return_value = {
                'price': 200000,
                'priceRangeLow': 190000,
                'priceRangeHigh': 210000,
                'comparables': [{'address': '123 Comp St', 'price': 195000}],
                'last_run': datetime.datetime.now().isoformat()
            }
            
            # Mock the fetch_rental_comps function
            mock_fetch_rental_comps.return_value = {
                'estimated_rent': 1800,
                'rental_comps': [{'address': '123 Rental St', 'rent': 1750}]
            }
            
            # Run comps by address
            result = service.run_comps_by_address("123 Test Street", "test-user-id")
            
            # Check the result
            self.assertIsNotNone(result)
            self.assertIn('estimated_value', result)
            self.assertIn('value_range_low', result)
            self.assertIn('value_range_high', result)
            self.assertIn('comparables', result)
            self.assertIn('rental_comps', result)
            
            # Verify mocks were called
            mock_fetch_property_comps.assert_called_once()
            mock_fetch_rental_comps.assert_called_once()

    @patch('services.analysis_service.fetch_property_comps')
    def test_run_comps_by_address_api_error(self, mock_fetch_property_comps):
        """Test running comps by address with API error."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the fetch_property_comps function to raise an error
            mock_fetch_property_comps.side_effect = RentcastAPIError("API Error")
            
            # Run comps by address should raise an error
            with self.assertRaises(RentcastAPIError):
                service.run_comps_by_address("123 Test Street", "test-user-id")

    @patch('services.analysis_service.fetch_property_comps')
    @patch('services.analysis_service.fetch_rental_comps')
    @patch('services.analysis_service.update_analysis_comps')
    def test_run_property_comps(self, mock_update_analysis_comps, mock_fetch_rental_comps, mock_fetch_property_comps):
        """Test running property comps for an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the fetch_property_comps function
            mock_fetch_property_comps.return_value = {
                'price': 200000,
                'priceRangeLow': 190000,
                'priceRangeHigh': 210000,
                'comparables': [{'address': '123 Comp St', 'price': 195000}],
                'last_run': datetime.datetime.now().isoformat()
            }
            
            # Mock the fetch_rental_comps function
            mock_fetch_rental_comps.return_value = {
                'estimated_rent': 1800,
                'rental_comps': [{'address': '123 Rental St', 'rent': 1750}]
            }
            
            # Mock the update_analysis_comps function
            updated_analysis = self.test_analysis.copy()
            updated_analysis['comps_data'] = {
                'last_run': datetime.datetime.now().isoformat(),
                'estimated_value': 200000,
                'value_range_low': 190000,
                'value_range_high': 210000,
                'comparables': [{'address': '123 Comp St', 'price': 195000}],
                'rental_comps': {
                    'estimated_rent': 1800,
                    'rental_comps': [{'address': '123 Rental St', 'rent': 1750}]
                }
            }
            mock_update_analysis_comps.return_value = updated_analysis
            
            # Run property comps
            with patch.object(service, 'get_analysis', return_value=self.test_analysis):
                with patch.object(service, '_save_analysis') as mock_save:
                    result = service.run_property_comps(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check the result
            self.assertIsNotNone(result)
            self.assertIn('comps_data', result)
            self.assertIn('estimated_value', result['comps_data'])
            self.assertIn('comparables', result['comps_data'])
            self.assertIn('rental_comps', result['comps_data'])
            
            # Verify mocks were called
            mock_fetch_property_comps.assert_called_once()
            mock_fetch_rental_comps.assert_called_once()
            mock_update_analysis_comps.assert_called_once()

    @patch('services.analysis_service.generate_report')
    def test_generate_pdf_report(self, mock_generate_report):
        """Test generating a PDF report."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock the generate_report function
            mock_buffer = BytesIO(b"PDF content")
            mock_generate_report.return_value = mock_buffer
            
            # Generate a PDF report
            with patch.object(service, 'get_analysis', return_value=self.test_analysis):
                result = service.generate_pdf_report(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check the result
            self.assertEqual(result, mock_buffer)
            
            # Verify mock was called
            mock_generate_report.assert_called_once()

    def test_get_analyses_for_user(self):
        """Test retrieving all analyses for a user."""
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
                # Get all analyses for the user
                with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                    # Mock the create_analysis function
                    mock_analysis = MagicMock()
                    mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                    mock_create_analysis.return_value = mock_analysis
                    
                    analyses, total_pages = service.get_analyses_for_user(self.test_analysis['user_id'])
                
                # Check the results
                self.assertEqual(len(analyses), 2)
                self.assertEqual(total_pages, 1)
                
                # Check pagination
                analyses_page1, total_pages = service.get_analyses_for_user(self.test_analysis['user_id'], page=1, per_page=1)
                self.assertEqual(len(analyses_page1), 1)
                self.assertEqual(total_pages, 2)
                
                analyses_page2, total_pages = service.get_analyses_for_user(self.test_analysis['user_id'], page=2, per_page=1)
                self.assertEqual(len(analyses_page2), 1)
                self.assertEqual(total_pages, 2)
                
                # Check that the analyses on different pages are different
                self.assertNotEqual(analyses_page1[0]['id'], analyses_page2[0]['id'])
            
            finally:
                # Clean up the second test file
                try:
                    os.remove(second_file_path)
                except:
                    pass

if __name__ == '__main__':
    unittest.main()
