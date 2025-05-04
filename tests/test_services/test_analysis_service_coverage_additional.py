import unittest
import os
import sys
import json
import uuid
import datetime
from unittest.mock import patch, MagicMock, mock_open
from flask import Flask, session
from io import BytesIO

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.analysis_service import AnalysisService

class TestAnalysisServiceCoverageAdditional(unittest.TestCase):
    """Additional test cases for the AnalysisService class focused on improving coverage."""

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

    def test_validate_field_type(self):
        """Test validating field types."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test valid field values
            service._validate_field_type('monthly_rent', 1800)
            service._validate_field_type('property_taxes', 200)
            service._validate_field_type('management_fee_percentage', 8)
            
            # Test invalid field values with special formats
            with self.assertRaises(ValueError):
                # UUID format validation should raise ValueError
                service._validate_field_type('id', 'not-a-uuid')
                
            with self.assertRaises(ValueError):
                # Date format validation should raise ValueError
                service._validate_field_type('created_at', 'not-a-date')
                
            with self.assertRaises(ValueError):
                # Boolean validation should raise ValueError
                service._validate_field_type('has_balloon_payment', 'maybe')
            
            # Test non-numeric fields
            service._validate_field_type('analysis_name', 'Test Analysis')
            service._validate_field_type('address', '123 Test Street')

    def test_validate_storage_data_percentages(self):
        """Test validating percentage fields in storage data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid data with percentage fields
            valid_data = {
                'id': str(uuid.uuid4()),
                'user_id': 'test-user-id',
                'analysis_type': 'LTR',
                'analysis_name': 'Test Analysis',
                'management_fee_percentage': 8.0,
                'capex_percentage': 5.0,
                'vacancy_percentage': 0.0,
                'repairs_percentage': 100.0
            }
            
            # This should not raise an exception
            service._validate_storage_data(valid_data)
            
            # Invalid percentage values
            invalid_data = valid_data.copy()
            invalid_data['management_fee_percentage'] = -1.0
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_storage_data(invalid_data)
            
            # Invalid percentage values (over 100%)
            invalid_data = valid_data.copy()
            invalid_data['capex_percentage'] = 101.0
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_storage_data(invalid_data)

    def test_validate_rent_data(self):
        """Test validating rent data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid LTR data
            valid_ltr_data = {
                'analysis_type': 'LTR',
                'monthly_rent': 1800
            }
            
            # This should not raise an exception
            service._validate_rent_data(valid_ltr_data)
            
            # Invalid LTR data - negative rent
            invalid_ltr_data = valid_ltr_data.copy()
            invalid_ltr_data['monthly_rent'] = -100
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_rent_data(invalid_ltr_data)
            
            # Invalid LTR data - non-numeric rent
            invalid_ltr_data = valid_ltr_data.copy()
            invalid_ltr_data['monthly_rent'] = 'not-a-number'
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_rent_data(invalid_ltr_data)
            
            # Valid Multi-Family data
            valid_multi_data = {
                'analysis_type': 'Multi-Family',
                'unit_types': json.dumps([
                    {
                        'type': '1BR',
                        'count': 4,
                        'occupied': 3,
                        'square_footage': 700,
                        'rent': 1000
                    }
                ])
            }
            
            # This should not raise an exception
            service._validate_rent_data(valid_multi_data)
            
            # Invalid Multi-Family data - missing unit_types
            invalid_multi_data = {
                'analysis_type': 'Multi-Family'
            }
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_rent_data(invalid_multi_data)
            
            # Invalid Multi-Family data - empty unit_types
            invalid_multi_data = valid_multi_data.copy()
            invalid_multi_data['unit_types'] = json.dumps([])
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_rent_data(invalid_multi_data)

    def test_normalize_data_with_dates(self):
        """Test normalizing data with date fields."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with date fields
            test_data = {
                'created_at': '2023-01-01',
                'updated_at': datetime.datetime.now().strftime("%Y-%m-%d"),
                'balloon_due_date': '2030-01-01',
                'has_balloon_payment': True
            }
            
            # Normalize the data
            normalized = service.normalize_data(test_data)
            
            # Check the results
            self.assertEqual(normalized['created_at'], '2023-01-01')
            self.assertEqual(normalized['updated_at'], test_data['updated_at'])
            self.assertEqual(normalized['balloon_due_date'], '2030-01-01')
            
            # Test with invalid date format
            invalid_date_data = test_data.copy()
            invalid_date_data['balloon_due_date'] = '01-01-2030'  # Wrong format
            
            # Normalize the data
            normalized = service.normalize_data(invalid_date_data)
            
            # Check the results - should handle invalid format
            self.assertIsNone(normalized.get('balloon_due_date'))
            
            # Test with no balloon payment
            no_balloon_data = test_data.copy()
            no_balloon_data['has_balloon_payment'] = False
            
            # Normalize the data
            normalized = service.normalize_data(no_balloon_data)
            
            # Check the results - balloon date should be None
            self.assertIsNone(normalized.get('balloon_due_date'))

    def test_validate_storage_data_uuid(self):
        """Test validating UUID fields in storage data."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid data with UUID
            valid_uuid = str(uuid.uuid4())
            valid_data = {
                'id': valid_uuid,
                'user_id': 'test-user-id',
                'analysis_type': 'LTR',
                'analysis_name': 'Test Analysis'
            }
            
            # This should not raise an exception
            service._validate_storage_data(valid_data)
            
            # Invalid UUID
            invalid_data = valid_data.copy()
            invalid_data['id'] = 'not-a-uuid'
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_storage_data(invalid_data)

    def test_get_value_method(self):
        """Test the _get_value method."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with various types
            test_data = {
                'string_value': 'test',
                'int_value': 123,
                'float_value': 123.45,
                'bool_value': True,
                'none_value': None,
                'empty_string': '',
                'zero_value': 0,
                'currency_value': '$1,234.56',
                'percentage_value': '12.34%'
            }
            
            # Test getting values
            self.assertEqual(service._get_value(test_data, 'string_value'), 'test')
            self.assertEqual(service._get_value(test_data, 'int_value'), 123)
            self.assertEqual(service._get_value(test_data, 'float_value'), 123.45)
            self.assertEqual(service._get_value(test_data, 'bool_value'), True)
            self.assertIsNone(service._get_value(test_data, 'none_value'))
            # Empty strings are converted to None in _get_value
            self.assertIsNone(service._get_value(test_data, 'empty_string'))
            self.assertEqual(service._get_value(test_data, 'zero_value'), 0)
            
            # Test getting non-existent values
            self.assertIsNone(service._get_value(test_data, 'non_existent'))

    def test_normalize_data_with_formats(self):
        """Test normalizing data with special formats."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with special formats
            test_data = {
                'id': '',  # Empty UUID should be generated
                'created_at': '',  # Empty datetime should be generated
                'updated_at': '',  # Empty datetime should be generated
                'balloon_due_date': '2030-01-01',
                'has_balloon_payment': True
            }
            
            # Normalize the data
            normalized = service.normalize_data(test_data)
            
            # Check the results
            self.assertTrue(uuid.UUID(normalized['id']))  # Should be a valid UUID
            self.assertIsNotNone(normalized['created_at'])  # Should be a valid datetime
            self.assertIsNotNone(normalized['updated_at'])  # Should be a valid datetime
            self.assertEqual(normalized['balloon_due_date'], '2030-01-01')

    def test_compress_analysis_data(self):
        """Test compressing analysis data for mobile."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with various types
            test_data = {
                'analysis_name': 'Test Analysis',
                'monthly_rent': 1800.5678,  # Float with many decimals
                'property_taxes': 200.9876,  # Float with many decimals
                'notes': 'A' * 2000  # Long text field
            }
            
            # Compress the data
            compressed = service._compress_analysis_data(test_data)
            
            # Check the results
            self.assertEqual(compressed['monthly_rent'], 1800.57)  # Rounded to 2 decimals
            self.assertEqual(compressed['property_taxes'], 200.99)  # Rounded to 2 decimals
            self.assertEqual(len(compressed['notes']), 1000)  # Truncated to 1000 chars

    def test_get_analysis_filepath(self):
        """Test getting filepath for analysis storage."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test analysis ID and user ID
            analysis_id = str(uuid.uuid4())
            user_id = 'test-user-id'
            
            # Get filepath
            filepath = service._get_analysis_filepath(analysis_id, user_id)
            
            # Check the result
            expected_filepath = os.path.join(self.app.config['ANALYSES_DIR'], f"{analysis_id}_{user_id}.json")
            self.assertEqual(filepath, expected_filepath)
            
            # Test with special characters
            special_analysis_id = 'test/id'
            special_user_id = 'user/id'
            
            # Get filepath
            filepath = service._get_analysis_filepath(special_analysis_id, special_user_id)
            
            # Check the result - special characters should be replaced
            expected_filepath = os.path.join(self.app.config['ANALYSES_DIR'], f"test_id_user_id.json")
            self.assertEqual(filepath, expected_filepath)

    def test_save_with_retries(self):
        """Test saving data with retry logic."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data
            test_data = {
                'id': str(uuid.uuid4()),
                'user_id': 'test-user-id',
                'analysis_name': 'Test Analysis'
            }
            
            # Mock filepath
            filepath = 'test_file.json'
            
            # Mock write_json to succeed on first try
            with patch('services.analysis_service.write_json') as mock_write_json:
                with patch('os.replace') as mock_replace:
                    # Save with retries
                    service._save_with_retries(filepath, test_data)
                    
                    # Verify write_json was called once
                    mock_write_json.assert_called_once()
                    # Verify os.replace was called once
                    mock_replace.assert_called_once()
            
            # Mock write_json to fail on first try, succeed on second
            with patch('services.analysis_service.write_json', side_effect=[IOError("Test error"), None]) as mock_write_json:
                with patch('os.replace') as mock_replace:
                    with patch('time.sleep') as mock_sleep:
                        # Save with retries
                        service._save_with_retries(filepath, test_data)
                        
                        # Verify write_json was called twice
                        self.assertEqual(mock_write_json.call_count, 2)
                        # Verify os.replace was called once
                        mock_replace.assert_called_once()
                        # Verify sleep was called once
                        mock_sleep.assert_called_once()

    def test_validate_required_fields_method(self):
        """Test validating required fields."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test data with all required fields
            valid_data = {
                'id': str(uuid.uuid4()),
                'user_id': 'test-user-id',
                'analysis_type': 'LTR',
                'analysis_name': 'Test Analysis'
            }
            
            # Define required fields with expected types
            required_fields = {
                'id': str,
                'user_id': str,
                'analysis_type': str,
                'analysis_name': str
            }
            
            # Test with all required fields
            service._validate_required_fields(valid_data, required_fields)
            
            # Test with missing fields
            invalid_data = valid_data.copy()
            del invalid_data['analysis_name']
            with self.assertRaises(ValueError):
                service._validate_required_fields(invalid_data, required_fields)
            
            # Test with None values
            invalid_data = valid_data.copy()
            invalid_data['analysis_name'] = None
            with self.assertRaises(ValueError):
                service._validate_required_fields(invalid_data, required_fields)
            
            # Test with empty string values
            invalid_data = valid_data.copy()
            invalid_data['analysis_name'] = ''
            with self.assertRaises(ValueError):
                service._validate_required_fields(invalid_data, required_fields)

    def test_validate_analysis_data_types(self):
        """Test validating analysis types."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test LTR analysis type
            ltr_data = {
                'analysis_type': 'LTR',
                'analysis_name': 'Test Analysis',
                'monthly_rent': 1800
            }
            
            # This should not raise an exception
            service.validate_analysis_data(ltr_data)
            
            # Test Multi-Family analysis type
            multi_family_data = {
                'analysis_type': 'Multi-Family',
                'analysis_name': 'Test Analysis',
                'unit_types': json.dumps([
                    {
                        'type': '1BR',
                        'count': 4,
                        'occupied': 3,
                        'square_footage': 700,
                        'rent': 1000
                    }
                ])
            }
            
            # This should not raise an exception
            service.validate_analysis_data(multi_family_data)
            
            # Test Lease Option analysis type
            lease_option_data = {
                'analysis_type': 'Lease Option',
                'analysis_name': 'Test Analysis',
                'monthly_rent': 1800,
                'purchase_price': 200000,
                'option_consideration_fee': 5000,
                'option_term_months': 24,
                'strike_price': 220000,
                'monthly_rent_credit_percentage': 25,
                'rent_credit_cap': 10000
            }
            
            # This should not raise an exception
            service.validate_analysis_data(lease_option_data)
            
            # Test BRRRR analysis type
            brrrr_data = {
                'analysis_type': 'BRRRR',
                'analysis_name': 'Test Analysis',
                'monthly_rent': 1800,
                'purchase_price': 200000,
                'rehab_costs': 50000,
                'holding_costs': 5000,
                'after_repair_value': 300000
            }
            
            # This should not raise an exception
            service.validate_analysis_data(brrrr_data)
            
            # Test PadSplit LTR analysis type
            padsplit_data = {
                'analysis_type': 'PadSplit LTR',
                'analysis_name': 'Test Analysis',
                'monthly_rent': 1800,
                'utilities': 200,
                'internet': 100,
                'cleaning': 150,
                'pest_control': 50,
                'landscaping': 100,
                'padsplit_platform_percentage': 15
            }
            
            # This should not raise an exception
            service.validate_analysis_data(padsplit_data)
            
            # Test invalid rent data
            invalid_rent_data = {
                'analysis_type': 'LTR',
                'analysis_name': 'Test Analysis',
                'monthly_rent': -100  # Negative rent should fail validation
            }
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service.validate_analysis_data(invalid_rent_data)

if __name__ == '__main__':
    unittest.main()
