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

class TestAnalysisServiceCoverageFinalAdditional(unittest.TestCase):
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

    def test_run_comps_by_address(self):
        """Test running comps by address."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock fetch_property_comps
            with patch('utils.comps_handler.fetch_property_comps') as mock_fetch_property_comps:
                # Set up mock return value
                mock_fetch_property_comps.return_value = {
                    'price': 250000,
                    'priceRangeLow': 230000,
                    'priceRangeHigh': 270000,
                    'comparables': [
                        {'address': '123 Comp St', 'price': 245000},
                        {'address': '456 Comp St', 'price': 255000}
                    ],
                    'last_run': datetime.datetime.now().isoformat(),
                    'mao': 200000
                }
                
                # Mock fetch_rental_comps
                with patch('utils.comps_handler.fetch_rental_comps') as mock_fetch_rental_comps:
                    # Set up mock return value
                    mock_fetch_rental_comps.return_value = {
                        'estimated_rent': 1800,
                        'rental_comps': [
                            {'address': '123 Rental St', 'rent': 1750},
                            {'address': '456 Rental St', 'rent': 1850}
                        ]
                    }
                    
                    # Run comps by address
                    result = service.run_comps_by_address('123 Test St', 'test-user-id')
                    
                    # Verify the result
                    self.assertIsNotNone(result)
                    self.assertIn('comparables', result)
                    self.assertEqual(len(result['comparables']), 2)
                    self.assertIn('mao', result)
                    self.assertEqual(result['mao'], 200000)
                    
                    # Verify fetch_property_comps was called with correct arguments
                    mock_fetch_property_comps.assert_called_once()
                    args, kwargs = mock_fetch_property_comps.call_args
                    self.assertEqual(kwargs['address'], '123 Test St')
                    
                    # Verify fetch_rental_comps was called with correct arguments
                    mock_fetch_rental_comps.assert_called_once()
                    args, kwargs = mock_fetch_rental_comps.call_args
                    self.assertEqual(kwargs['address'], '123 Test St')

    def test_run_comps_by_address_missing_address(self):
        """Test running comps by address with missing address."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Run comps by address with missing address
            with self.assertRaises(ValueError):
                service.run_comps_by_address('', 'test-user-id')

    def test_run_comps_by_address_api_error(self):
        """Test running comps by address with API error."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock fetch_property_comps to raise RentcastAPIError
            with patch('utils.comps_handler.fetch_property_comps') as mock_fetch_property_comps:
                from utils.comps_handler import RentcastAPIError
                mock_fetch_property_comps.side_effect = RentcastAPIError("API error")
                
                # Run comps by address
                with self.assertRaises(RentcastAPIError):
                    service.run_comps_by_address('123 Test St', 'test-user-id')

    def test_run_property_comps(self):
        """Test running property comps for an analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis
            with patch.object(service, 'get_analysis') as mock_get_analysis:
                # Set up mock return value
                mock_get_analysis.return_value = {
                    'id': str(uuid.uuid4()),
                    'user_id': 'test-user-id',
                    'analysis_name': 'Test Analysis',
                    'analysis_type': 'LTR',
                    'address': '123 Test St',
                    'property_type': 'Single Family',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'square_footage': 1500
                }
                
                # Mock fetch_property_comps
                with patch('utils.comps_handler.fetch_property_comps') as mock_fetch_property_comps:
                    # Set up mock return value
                    mock_fetch_property_comps.return_value = {
                        'price': 250000,
                        'priceRangeLow': 230000,
                        'priceRangeHigh': 270000,
                        'comparables': [
                            {'address': '123 Comp St', 'price': 245000},
                            {'address': '456 Comp St', 'price': 255000}
                        ],
                        'last_run': datetime.datetime.now().isoformat(),
                        'mao': 200000
                    }
                    
                    # Mock fetch_rental_comps
                    with patch('utils.comps_handler.fetch_rental_comps') as mock_fetch_rental_comps:
                        # Set up mock return value
                        mock_fetch_rental_comps.return_value = {
                            'estimated_rent': 1800,
                            'rental_comps': [
                                {'address': '123 Rental St', 'rent': 1750},
                                {'address': '456 Rental St', 'rent': 1850}
                            ]
                        }
                        
                        # Mock update_analysis_comps
                        with patch('utils.comps_handler.update_analysis_comps') as mock_update_analysis_comps:
                            # Set up mock return value
                            mock_update_analysis_comps.return_value = {
                                'id': str(uuid.uuid4()),
                                'user_id': 'test-user-id',
                                'analysis_name': 'Test Analysis',
                                'analysis_type': 'LTR',
                                'address': '123 Test St',
                                'comps_data': {
                                    'last_run': datetime.datetime.now().isoformat(),
                                    'run_count': 1,
                                    'estimated_value': 250000,
                                    'value_range_low': 230000,
                                    'value_range_high': 270000,
                                    'comparables': [
                                        {'address': '123 Comp St', 'price': 245000},
                                        {'address': '456 Comp St', 'price': 255000}
                                    ],
                                    'mao': 200000,
                                    'rental_comps': {
                                        'estimated_rent': 1800,
                                        'rental_comps': [
                                            {'address': '123 Rental St', 'rent': 1750},
                                            {'address': '456 Rental St', 'rent': 1850}
                                        ]
                                    }
                                }
                            }
                            
                            # Mock _save_analysis
                            with patch.object(service, '_save_analysis') as mock_save_analysis:
                                # Run property comps
                                result = service.run_property_comps(str(uuid.uuid4()), 'test-user-id')
                                
                                # Verify the result
                                self.assertIsNotNone(result)
                                self.assertIn('comps_data', result)
                                self.assertIn('comparables', result['comps_data'])
                                self.assertEqual(len(result['comps_data']['comparables']), 2)
                                
                                # Verify get_analysis was called
                                mock_get_analysis.assert_called_once()
                                
                                # Verify fetch_property_comps was called
                                mock_fetch_property_comps.assert_called_once()
                                
                                # Verify fetch_rental_comps was called
                                mock_fetch_rental_comps.assert_called_once()
                                
                                # Verify update_analysis_comps was called
                                mock_update_analysis_comps.assert_called_once()
                                
                                # Verify _save_analysis was called
                                mock_save_analysis.assert_called_once()

    def test_run_property_comps_analysis_not_found(self):
        """Test running property comps for a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis to return None
            with patch.object(service, 'get_analysis', return_value=None):
                # Run property comps
                result = service.run_property_comps(str(uuid.uuid4()), 'test-user-id')
                
                # Verify the result
                self.assertIsNone(result)

    def test_run_property_comps_missing_address(self):
        """Test running property comps for an analysis with missing address."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis
            with patch.object(service, 'get_analysis') as mock_get_analysis:
                # Set up mock return value with missing address
                mock_get_analysis.return_value = {
                    'id': str(uuid.uuid4()),
                    'user_id': 'test-user-id',
                    'analysis_name': 'Test Analysis',
                    'analysis_type': 'LTR'
                    # No address field
                }
                
                # Run property comps
                with self.assertRaises(ValueError):
                    service.run_property_comps(str(uuid.uuid4()), 'test-user-id')

    def test_run_property_comps_update_error(self):
        """Test running property comps with error in update_analysis_comps."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis
            with patch.object(service, 'get_analysis') as mock_get_analysis:
                # Set up mock return value
                mock_get_analysis.return_value = {
                    'id': str(uuid.uuid4()),
                    'user_id': 'test-user-id',
                    'analysis_name': 'Test Analysis',
                    'analysis_type': 'LTR',
                    'address': '123 Test St',
                    'property_type': 'Single Family',
                    'bedrooms': 3,
                    'bathrooms': 2,
                    'square_footage': 1500
                }
                
                # Mock fetch_property_comps
                with patch('utils.comps_handler.fetch_property_comps') as mock_fetch_property_comps:
                    # Set up mock return value
                    mock_fetch_property_comps.return_value = {
                        'price': 250000,
                        'priceRangeLow': 230000,
                        'priceRangeHigh': 270000,
                        'comparables': [
                            {'address': '123 Comp St', 'price': 245000},
                            {'address': '456 Comp St', 'price': 255000}
                        ],
                        'last_run': datetime.datetime.now().isoformat(),
                        'mao': 200000
                    }
                    
                    # Mock fetch_rental_comps
                    with patch('utils.comps_handler.fetch_rental_comps') as mock_fetch_rental_comps:
                        # Set up mock return value
                        mock_fetch_rental_comps.return_value = {
                            'estimated_rent': 1800,
                            'rental_comps': [
                                {'address': '123 Rental St', 'rent': 1750},
                                {'address': '456 Rental St', 'rent': 1850}
                            ]
                        }
                        
                        # Mock update_analysis_comps to raise an exception
                        with patch('utils.comps_handler.update_analysis_comps', side_effect=Exception("Test error")):
                            # Mock _save_analysis
                            with patch.object(service, '_save_analysis') as mock_save_analysis:
                                # Run property comps
                                result = service.run_property_comps(str(uuid.uuid4()), 'test-user-id')
                                
                                # Verify the result
                                self.assertIsNotNone(result)
                                self.assertIn('comps_data', result)
                                self.assertIn('comparables', result['comps_data'])
                                self.assertEqual(len(result['comps_data']['comparables']), 2)
                                
                                # Verify _save_analysis was called
                                mock_save_analysis.assert_called_once()

    def test_generate_pdf_report(self):
        """Test generating a PDF report."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis
            with patch.object(service, 'get_analysis') as mock_get_analysis:
                # Set up mock return value
                mock_get_analysis.return_value = {
                    'id': str(uuid.uuid4()),
                    'user_id': 'test-user-id',
                    'analysis_name': 'Test Analysis',
                    'analysis_type': 'LTR',
                    'address': '123 Test St',
                    'calculated_metrics': {
                        'cash_on_cash_return': 10.5,
                        'roi': 15.2,
                        'monthly_cash_flow': 250,
                        'annual_cash_flow': 3000
                    }
                }
                
                # Mock get_metrics
                with patch('utils.standardized_metrics.get_metrics', return_value=None):
                    # Mock extract_calculated_metrics
                    with patch('utils.standardized_metrics.extract_calculated_metrics') as mock_extract_metrics:
                        mock_extract_metrics.return_value = {
                            'cash_on_cash_return': 10.5,
                            'roi': 15.2,
                            'monthly_cash_flow': 250,
                            'annual_cash_flow': 3000
                        }
                        
                        # Mock register_metrics
                        with patch('utils.standardized_metrics.register_metrics') as mock_register_metrics:
                            # Mock generate_report
                            with patch('services.report_generator.generate_report') as mock_generate_report:
                                # Set up mock return value
                                mock_buffer = BytesIO(b'PDF content')
                                mock_generate_report.return_value = mock_buffer
                                
                                # Generate PDF report
                                result = service.generate_pdf_report(str(uuid.uuid4()), 'test-user-id')
                                
                                # Verify the result
                                self.assertEqual(result, mock_buffer)
                                
                                # Verify get_analysis was called
                                mock_get_analysis.assert_called_once()
                                
                                # Verify extract_calculated_metrics was called
                                mock_extract_metrics.assert_called_once()
                                
                                # Verify register_metrics was called
                                mock_register_metrics.assert_called_once()
                                
                                # Verify generate_report was called
                                mock_generate_report.assert_called_once()

    def test_generate_pdf_report_analysis_not_found(self):
        """Test generating a PDF report for a non-existent analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis to return None
            with patch.object(service, 'get_analysis', return_value=None):
                # Generate PDF report
                with self.assertRaises(ValueError):
                    service.generate_pdf_report(str(uuid.uuid4()), 'test-user-id')

    def test_generate_pdf_report_with_registered_metrics(self):
        """Test generating a PDF report with already registered metrics."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Mock get_analysis
            with patch.object(service, 'get_analysis') as mock_get_analysis:
                # Set up mock return value
                mock_get_analysis.return_value = {
                    'id': str(uuid.uuid4()),
                    'user_id': 'test-user-id',
                    'analysis_name': 'Test Analysis',
                    'analysis_type': 'LTR',
                    'address': '123 Test St',
                    'calculated_metrics': {
                        'cash_on_cash_return': 10.5,
                        'roi': 15.2,
                        'monthly_cash_flow': 250,
                        'annual_cash_flow': 3000
                    }
                }
                
                # Mock get_metrics to return metrics
                with patch('utils.standardized_metrics.get_metrics') as mock_get_metrics:
                    mock_get_metrics.return_value = {
                        'cash_on_cash_return': 10.5,
                        'roi': 15.2,
                        'monthly_cash_flow': 250,
                        'annual_cash_flow': 3000
                    }
                    
                    # Mock extract_calculated_metrics
                    with patch('utils.standardized_metrics.extract_calculated_metrics') as mock_extract_metrics:
                        # Mock generate_report
                        with patch('services.report_generator.generate_report') as mock_generate_report:
                            # Set up mock return value
                            mock_buffer = BytesIO(b'PDF content')
                            mock_generate_report.return_value = mock_buffer
                            
                            # Generate PDF report
                            result = service.generate_pdf_report(str(uuid.uuid4()), 'test-user-id')
                            
                            # Verify the result
                            self.assertEqual(result, mock_buffer)
                            
                            # Verify get_analysis was called
                            mock_get_analysis.assert_called_once()
                            
                            # Verify get_metrics was called
                            mock_get_metrics.assert_called_once()
                            
                            # Verify extract_calculated_metrics was not called
                            mock_extract_metrics.assert_not_called()
                            
                            # Verify generate_report was called
                            mock_generate_report.assert_called_once()

if __name__ == '__main__':
    unittest.main()
