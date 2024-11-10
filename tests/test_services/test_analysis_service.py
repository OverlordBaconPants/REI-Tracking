import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
from decimal import Decimal
from datetime import datetime
import os
from services.analysis_service import AnalysisService

class TestAnalysisService(unittest.TestCase):
    """Test suite for AnalysisService."""

    def setUp(self):
        """Set up test environment."""
        self.service = AnalysisService()
        
        # Sample test data
        self.ltr_data = {
            'analysis_type': 'LTR',
            'analysis_name': 'Test Analysis',
            'property_address': '123 Test St',
            'purchase_price': 200000,
            'after_repair_value': 200000,
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'management_percentage': 10,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'hoa_coa_coop': 100,
            'loans': [{
                'amount': 160000,
                'interest_rate': 4.5,
                'term': 360,
                'down_payment': 40000,
                'closing_costs': 3000
            }]
        }
        
        self.brrrr_data = {
            'analysis_type': 'BRRRR',
            'analysis_name': 'Test BRRRR',
            'property_address': '123 Test St',
            'purchase_price': 200000,
            'after_repair_value': 250000,
            'renovation_costs': 30000,
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'management_percentage': 10,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'initial_loan_amount': 160000,
            'initial_interest_rate': 7.5,
            'initial_loan_term': 360,
            'initial_down_payment': 40000,
            'initial_closing_costs': 3000,
            'refinance_loan_amount': 187500,
            'refinance_interest_rate': 6.5,
            'refinance_loan_term': 360,
            'refinance_closing_costs': 3000
        }

    @patch('services.analysis_service.write_json')
    def test_create_analysis_ltr(self, mock_write):
        """Test creating a long-term rental analysis."""
        result = self.service.create_analysis(self.ltr_data, 'test_user')
        
        self.assertEqual(result['analysis_type'], 'LTR')
        self.assertIn('monthly_cash_flow', result)
        self.assertIn('annual_cash_flow', result)
        self.assertIn('operating_expenses', result)
        
        # Verify calculations
        monthly_income = float(result['monthly_income'])
        monthly_expenses = float(result['total_monthly_expenses'])
        self.assertTrue(monthly_income > monthly_expenses)

    @patch('services.analysis_service.write_json')
    def test_create_analysis_brrrr(self, mock_write):
        """Test creating a BRRRR analysis."""
        result = self.service.create_analysis(self.brrrr_data, 'test_user')
        
        self.assertEqual(result['analysis_type'], 'BRRRR')
        self.assertIn('equity_captured', result)
        self.assertIn('cash_recouped', result)
        self.assertIn('roi', result)
        
        # Verify calculations
        equity = float(result['equity_captured'])
        self.assertEqual(equity, 20000)  # 250000 ARV - 230000 total cost

    def test_validate_analysis_data(self):
        """Test analysis data validation."""
        # Test valid data
        self.assertTrue(self.service.validate_analysis_data(self.ltr_data))
        
        # Test missing required fields
        invalid_data = self.ltr_data.copy()
        del invalid_data['analysis_type']
        with self.assertRaises(ValueError):
            self.service.validate_analysis_data(invalid_data)
        
        # Test negative values
        invalid_data = self.ltr_data.copy()
        invalid_data['purchase_price'] = -100000
        with self.assertRaises(ValueError):
            self.service.validate_analysis_data(invalid_data)
        
        # Test invalid percentages
        invalid_data = self.ltr_data.copy()
        invalid_data['management_percentage'] = 101
        with self.assertRaises(ValueError):
            self.service.validate_analysis_data(invalid_data)

    def test_calculate_monthly_payment(self):
        """Test loan payment calculations."""
        # Test normal case
        payment = self.service._calculate_monthly_payment(200000, 4.5, 360)
        self.assertGreater(payment, 0)
        
        # Test edge cases
        self.assertEqual(self.service._calculate_monthly_payment(0, 4.5, 360), 0)
        self.assertEqual(self.service._calculate_monthly_payment(200000, 0, 360), 0)
        self.assertEqual(self.service._calculate_monthly_payment(200000, 4.5, 0), 0)

    @patch('services.analysis_service.read_json')
    def test_get_analysis(self, mock_read):
        """Test retrieving an analysis."""
        mock_read.return_value = self.ltr_data
        
        result = self.service.get_analysis('test_id', 'test_user')
        self.assertEqual(result['analysis_type'], 'LTR')

    @patch('os.listdir')
    @patch('services.analysis_service.read_json')
    def test_get_analyses_for_user(self, mock_read, mock_listdir):
        """Test retrieving paginated analyses."""
        mock_listdir.return_value = [f'analysis_{i}_test_user.json' for i in range(15)]
        mock_read.return_value = self.ltr_data
        
        analyses, total_pages = self.service.get_analyses_for_user('test_user', page=1, per_page=10)
        self.assertEqual(len(analyses), 10)
        self.assertEqual(total_pages, 2)

    def test_calculate_base_metrics(self):
        """Test calculation of base metrics."""
        result = self.service._calculate_base_metrics(self.ltr_data)
        
        self.assertIn('monthly_income', result)
        self.assertIn('operating_expenses', result)
        self.assertIn('total_operating_expenses', result)
        
        # Verify expense calculations
        expenses = result['operating_expenses']
        self.assertIn('property_taxes', expenses)
        self.assertIn('management', expenses)
        self.assertIn('capex', expenses)
        self.assertIn('vacancy', expenses)

    def test_calculate_padsplit_expenses(self):
        """Test PadSplit expense calculations."""
        padsplit_data = {
            **self.ltr_data,
            'padsplit_platform_percentage': 15,
            'utilities': 200,
            'internet': 50,
            'cleaning_costs': 100,
            'pest_control': 50,
            'landscaping': 100
        }
        
        result = self.service._calculate_padsplit_expenses(padsplit_data)
        
        self.assertIn('platform_fee', result)
        self.assertIn('utilities', result)
        self.assertIn('internet', result)
        self.assertIn('cleaning_costs', result)
        self.assertIn('pest_control', result)
        self.assertIn('landscaping', result)

    @patch('services.analysis_service.write_json')
    def test_update_analysis(self, mock_write):
        """Test updating an analysis."""
        with patch('services.analysis_service.read_json') as mock_read:
            mock_read.return_value = {**self.ltr_data, 'created_at': '2024-01-01T00:00:00'}
            
            updated_data = {**self.ltr_data, 'monthly_rent': 2200}
            result = self.service.update_analysis(updated_data, 'test_user')
            
            self.assertEqual(float(result['monthly_rent']), 2200)
            self.assertIn('updated_at', result)

    @patch('os.path.exists')
    def test_delete_analysis(self, mock_exists):
        """Test deleting an analysis."""
        mock_exists.return_value = True
        
        with patch('os.remove') as mock_remove:
            result = self.service.delete_analysis('test_id', 'test_user')
            self.assertTrue(result)
            mock_remove.assert_called_once()

    def test_calculate_loan_metrics(self):
        """Test loan metrics calculations."""
        loans = [{
            'amount': 160000,
            'interest_rate': 4.5,
            'term': 360,
            'down_payment': 40000,
            'closing_costs': 3000,
            'name': 'Test Loan'
        }]
        
        result = self.service._calculate_loan_metrics(loans)
        
        self.assertIn('total_monthly_payment', result)
        self.assertIn('total_down_payment', result)
        self.assertIn('total_closing_costs', result)
        self.assertIn('loan_details', result)
        
        self.assertEqual(result['total_down_payment'], 40000)
        self.assertEqual(result['total_closing_costs'], 3000)

class TestAnalysisServiceEdgeCases(unittest.TestCase):
    """Test suite for edge cases and error handling."""

    def setUp(self):
        self.service = AnalysisService()

    def test_invalid_analysis_type(self):
        """Test handling of invalid analysis type."""
        data = {
            'analysis_type': 'INVALID',
            'analysis_name': 'Test',
            'property_address': '123 Test St'
        }
        
        with self.assertRaises(ValueError):
            self.service._calculate_analysis(data)

    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        data = {'analysis_type': 'LTR'}
        
        with self.assertRaises(ValueError):
            self.service.validate_analysis_data(data)

    def test_invalid_numeric_values(self):
        """Test handling of invalid numeric values."""
        data = {
            'analysis_type': 'LTR',
            'analysis_name': 'Test',
            'property_address': '123 Test St',
            'purchase_price': 'invalid'
        }
        
        with self.assertRaises(ValueError):
            self.service.validate_analysis_data(data)

    @patch('os.path.exists')
    def test_nonexistent_analysis(self, mock_exists):
        """Test retrieving non-existent analysis."""
        mock_exists.return_value = False
        
        result = self.service.get_analysis('nonexistent', 'test_user')
        self.assertIsNone(result)

    def test_zero_values(self):
        """Test calculations with zero values."""
        data = {
            'analysis_type': 'LTR',
            'analysis_name': 'Test Zero',
            'property_address': '123 Test St',
            'purchase_price': 0,
            'monthly_rent': 0,
            'property_taxes': 0,
            'insurance': 0,
            'management_percentage': 0,
            'capex_percentage': 0,
            'vacancy_percentage': 0
        }
        
        result = self.service._calculate_base_metrics(data)
        self.assertEqual(result['monthly_income'], 0)
        self.assertEqual(result['total_operating_expenses'], 0)

if __name__ == '__main__':
    unittest.main()