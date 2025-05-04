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

class TestAnalysisServiceCoverageFinal(unittest.TestCase):
    """Final test cases for the AnalysisService class focused on improving coverage."""

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

    def test_optimize_metrics_for_mobile(self):
        """Test optimizing metrics for mobile display."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Test metrics data
            metrics = {
                'cash_on_cash_return': 12.345,
                'roi': 15.678,
                'monthly_cash_flow': 456.789,
                'annual_cash_flow': 5481.456,
                'vacancy_rate': 5.123,
                'debt_service_ratio': 1.456789
            }
            
            # Optimize metrics for mobile
            optimized = service._optimize_metrics_for_mobile(metrics)
            
            # Check the results
            self.assertEqual(optimized['cash_on_cash_return'], 12.3)  # One decimal for percentage
            self.assertEqual(optimized['roi'], 15.7)  # One decimal for percentage
            self.assertEqual(optimized['monthly_cash_flow'], 457)  # No decimals for currency
            self.assertEqual(optimized['annual_cash_flow'], 5481)  # No decimals for currency
            self.assertEqual(optimized['vacancy_rate'], 5.1)  # One decimal for percentage
            self.assertEqual(optimized['debt_service_ratio'], 1.46)  # Two decimals for ratios

    def test_validate_storage_data(self):
        """Test validating data before storage."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Valid storage data
            valid_data = {
                'id': str(uuid.uuid4()),
                'user_id': 'test-user-id',
                'analysis_type': 'LTR',
                'analysis_name': 'Test Analysis',
                'monthly_rent': 1800,
                'property_taxes': 200,
                'insurance': 100,
                'management_fee_percentage': 8.0,
                'capex_percentage': 5.0,
                'vacancy_percentage': 5.0,
                'repairs_percentage': 5.0
            }
            
            # This should not raise an exception
            service._validate_storage_data(valid_data)
            
            # Invalid data - missing required field
            invalid_data = valid_data.copy()
            del invalid_data['analysis_name']
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_storage_data(invalid_data)
            
            # Invalid data - invalid ID format
            invalid_id_data = valid_data.copy()
            invalid_id_data['id'] = 'not-a-uuid'
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_storage_data(invalid_id_data)
            
            # Invalid data - invalid percentage
            invalid_percentage_data = valid_data.copy()
            invalid_percentage_data['management_fee_percentage'] = 101.0  # Over 100%
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_storage_data(invalid_percentage_data)
            
            # Invalid data - invalid date format
            invalid_date_data = valid_data.copy()
            invalid_date_data['balloon_due_date'] = 'not-a-date'
            
            # This should raise a ValueError
            with self.assertRaises(ValueError):
                service._validate_storage_data(invalid_date_data)

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
            
            # Mock write_json to fail all tries
            with patch('services.analysis_service.write_json', side_effect=IOError("Test error")) as mock_write_json:
                with patch('time.sleep') as mock_sleep:
                    # This should raise an IOError
                    with self.assertRaises(IOError):
                        service._save_with_retries(filepath, test_data)
                        
                        # Verify write_json was called max_retries times
                        self.assertEqual(mock_write_json.call_count, 3)
                        # Verify sleep was called max_retries-1 times
                        self.assertEqual(mock_sleep.call_count, 2)

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
            
            # Test with missing ANALYSES_DIR config
            with patch.dict(self.app.config, {'ANALYSES_DIR': None}):
                # This should raise a ValueError
                with self.assertRaises(ValueError):
                    service._get_analysis_filepath(analysis_id, user_id)

    def test_find_analysis_owner(self):
        """Test finding the owner of an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock os.path.exists to return True for a specific path
            with patch('os.path.exists', side_effect=lambda path: 'test-user-id' in path):
                with patch('os.listdir', return_value=['test-user-id']):
                    # Find the owner
                    owner = service.find_analysis_owner(self.test_analysis['id'])
                    
                    # Check the result
                    self.assertEqual(owner, 'test-user-id')
            
            # Mock os.path.exists to return False for all paths
            with patch('os.path.exists', return_value=False):
                with patch('os.listdir', return_value=['test-user-id']):
                    # Find the owner
                    owner = service.find_analysis_owner('non-existent-id')
                    
                    # Check the result
                    self.assertIsNone(owner)

    def test_process_analysis_data(self):
        """Test processing a single analysis file."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock create_analysis
            with patch('services.analysis_service.create_analysis') as mock_create_analysis:
                # Mock the analysis object
                mock_analysis = MagicMock()
                mock_analysis.get_report_data.return_value = {'metrics': {'cash_flow': '$500'}}
                mock_create_analysis.return_value = mock_analysis
                
                # Process the analysis data
                result = service._process_analysis_data(self.test_analysis, 'test-user-id', 'test_file.json')
                
                # Check the result
                self.assertEqual(result['id'], self.test_analysis['id'])
                self.assertEqual(result['analysis_name'], self.test_analysis['analysis_name'])
                self.assertEqual(result['calculated_metrics'], {'cash_flow': '$500'})
                
                # Test with error
                with patch.object(mock_analysis, 'get_report_data', side_effect=Exception("Test error")):
                    # Process the analysis data with error
                    result = service._process_analysis_data(self.test_analysis, 'test-user-id', 'test_file.json')
                    
                    # Check the result
                    self.assertIsNone(result)

    def test_paginate_analyses(self):
        """Test paginating a list of analyses."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Create a list of analyses
            analyses = [
                {'id': '1', 'analysis_name': 'Analysis 1'},
                {'id': '2', 'analysis_name': 'Analysis 2'},
                {'id': '3', 'analysis_name': 'Analysis 3'},
                {'id': '4', 'analysis_name': 'Analysis 4'},
                {'id': '5', 'analysis_name': 'Analysis 5'}
            ]
            
            # Paginate the analyses - page 1, 2 per page
            page_analyses, total_pages = service._paginate_analyses(analyses, 1, 2)
            
            # Check the results
            self.assertEqual(len(page_analyses), 2)
            self.assertEqual(page_analyses[0]['id'], '1')
            self.assertEqual(page_analyses[1]['id'], '2')
            self.assertEqual(total_pages, 3)
            
            # Paginate the analyses - page 2, 2 per page
            page_analyses, total_pages = service._paginate_analyses(analyses, 2, 2)
            
            # Check the results
            self.assertEqual(len(page_analyses), 2)
            self.assertEqual(page_analyses[0]['id'], '3')
            self.assertEqual(page_analyses[1]['id'], '4')
            self.assertEqual(total_pages, 3)
            
            # Paginate the analyses - page 3, 2 per page
            page_analyses, total_pages = service._paginate_analyses(analyses, 3, 2)
            
            # Check the results
            self.assertEqual(len(page_analyses), 1)
            self.assertEqual(page_analyses[0]['id'], '5')
            self.assertEqual(total_pages, 3)
            
            # Paginate the analyses - empty list
            page_analyses, total_pages = service._paginate_analyses([], 1, 2)
            
            # Check the results
            self.assertEqual(len(page_analyses), 0)
            self.assertEqual(total_pages, 1)

if __name__ == '__main__':
    unittest.main()
