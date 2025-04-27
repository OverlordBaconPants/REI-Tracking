"""
Test module for the property financial routes.

This module provides tests for the property financial routes, including equity tracking,
cash flow calculations, and comparison of actual performance to analysis projections.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from decimal import Decimal

from src.main import app
from src.models.property import Property, MonthlyIncome, MonthlyExpenses, Utilities
from src.models.user import User


class TestPropertyFinancialRoutes(unittest.TestCase):
    """Test case for the property financial routes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create test user
        self.test_user = User(
            id="user123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password",
            role="Admin"
        )
        
        # Create test property
        self.test_property = Property(
            id="prop123",
            address="123 Test St",
            purchase_price=Decimal("200000"),
            purchase_date="2023-01-01",
            monthly_income=MonthlyIncome(
                rental_income=Decimal("1500"),
                parking_income=Decimal("100"),
                laundry_income=Decimal("0"),
                other_income=Decimal("0"),
                income_notes="January rent; January parking"
            ),
            monthly_expenses=MonthlyExpenses(
                property_tax=Decimal("2400"),
                insurance=Decimal("1200"),
                repairs=Decimal("0"),
                capex=Decimal("0"),
                property_management=Decimal("0"),
                hoa_fees=Decimal("0"),
                utilities=Utilities(
                    water=Decimal("50"),
                    electricity=Decimal("0"),
                    gas=Decimal("0"),
                    trash=Decimal("0")
                ),
                expense_notes="Annual property tax; Annual insurance; January water bill"
            )
        )
        
        # Create test financial summary
        self.test_summary = {
            "property_id": "prop123",
            "address": "123 Test St",
            "income_total": "1600",
            "expense_total": "3650",
            "net_cash_flow": "-2050",
            "utility_total": "50",
            "maintenance_total": "0",
            "capex_total": "0",
            "income_breakdown": {
                "rental_income": "1500",
                "parking_income": "100",
                "laundry_income": "0",
                "other_income": "0"
            },
            "expense_breakdown": {
                "property_tax": "2400",
                "insurance": "1200",
                "repairs": "0",
                "capex": "0",
                "property_management": "0",
                "hoa_fees": "0",
                "other_expenses": "0"
            },
            "utility_breakdown": {
                "water": "50",
                "electricity": "0",
                "gas": "0",
                "trash": "0"
            },
            "income_notes": "January rent; January parking",
            "expense_notes": "Annual property tax; Annual insurance; January water bill"
        }
        
        # Create test maintenance and capex records
        self.test_records = [
            {
                "id": "trans6",
                "property_id": "prop123",
                "type": "expense",
                "category": "Repairs",
                "description": "Fix leaky faucet",
                "amount": "150",
                "date": "2023-02-05",
                "collector_payer": "Owner"
            },
            {
                "id": "trans7",
                "property_id": "prop123",
                "type": "expense",
                "category": "Capital Expenditures",
                "description": "New water heater",
                "amount": "800",
                "date": "2023-02-10",
                "collector_payer": "Owner"
            }
        ]
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_update_property_financials(self, mock_g, mock_service):
        """Test updating property financials."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.update_property_financials.return_value = self.test_property
        
        # Make request
        response = self.app.post('/api/property-financials/update/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Property financials updated successfully')
        self.assertIn('property', data)
        
        # Verify service was called correctly
        mock_service.update_property_financials.assert_called_once_with('prop123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_update_property_financials_not_found(self, mock_g, mock_service):
        """Test updating property financials when property not found."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.update_property_financials.return_value = None
        
        # Make request
        response = self.app.post('/api/property-financials/update/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Property not found or update failed')
        
        # Verify service was called correctly
        mock_service.update_property_financials.assert_called_once_with('prop123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_get_property_financial_summary(self, mock_g, mock_service):
        """Test getting property financial summary."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.get_property_financial_summary.return_value = self.test_summary
        
        # Make request
        response = self.app.get('/api/property-financials/summary/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('summary', data)
        self.assertEqual(data['summary']['property_id'], 'prop123')
        self.assertEqual(data['summary']['address'], '123 Test St')
        self.assertEqual(data['summary']['income_total'], '1600')
        self.assertEqual(data['summary']['expense_total'], '3650')
        
        # Verify service was called correctly
        mock_service.get_property_financial_summary.assert_called_once_with('prop123', 'user123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_get_property_financial_summary_no_access(self, mock_g, mock_service):
        """Test getting property financial summary with no access."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.get_property_financial_summary.side_effect = ValueError("User does not have access to this property")
        
        # Make request
        response = self.app.get('/api/property-financials/summary/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'User does not have access to this property')
        
        # Verify service was called correctly
        mock_service.get_property_financial_summary.assert_called_once_with('prop123', 'user123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_get_all_property_financials(self, mock_g, mock_service):
        """Test getting all property financials."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.get_all_property_financials.return_value = [self.test_summary]
        
        # Make request
        response = self.app.get('/api/property-financials/all')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('summaries', data)
        self.assertEqual(len(data['summaries']), 1)
        self.assertEqual(data['summaries'][0]['property_id'], 'prop123')
        
        # Verify service was called correctly
        mock_service.get_all_property_financials.assert_called_once_with('user123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_update_all_property_financials(self, mock_g, mock_service):
        """Test updating all property financials."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.update_all_property_financials.return_value = 1
        
        # Make request
        response = self.app.post('/api/property-financials/update-all')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Updated financials for 1 properties')
        self.assertEqual(data['updated_count'], 1)
        
        # Verify service was called correctly
        mock_service.update_all_property_financials.assert_called_once()
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_update_all_property_financials_not_admin(self, mock_g, mock_service):
        """Test updating all property financials when not admin."""
        # Set up mocks
        user = User(
            id="user123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password="password",
            role="User"
        )
        user.is_admin = MagicMock(return_value=False)
        mock_g.current_user = user
        
        # Make request
        response = self.app.post('/api/property-financials/update-all')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 403)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Only administrators can update all property financials')
        
        # Verify service was not called
        mock_service.update_all_property_financials.assert_not_called()
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_get_maintenance_and_capex_records(self, mock_g, mock_service):
        """Test getting maintenance and capex records."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.get_maintenance_and_capex_records.return_value = self.test_records
        
        # Make request
        response = self.app.get('/api/property-financials/maintenance-capex/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('records', data)
        self.assertEqual(len(data['records']), 2)
        self.assertEqual(data['records'][0]['id'], 'trans6')
        self.assertEqual(data['records'][0]['category'], 'Repairs')
        self.assertEqual(data['records'][1]['id'], 'trans7')
        self.assertEqual(data['records'][1]['category'], 'Capital Expenditures')
        
        # Verify service was called correctly
        mock_service.get_maintenance_and_capex_records.assert_called_once_with('prop123', 'user123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_get_maintenance_and_capex_records_no_access(self, mock_g, mock_service):
        """Test getting maintenance and capex records with no access."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.get_maintenance_and_capex_records.side_effect = ValueError("User does not have access to this property")
        
        # Make request
        response = self.app.get('/api/property-financials/maintenance-capex/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'User does not have access to this property')
        
        # Verify service was called correctly
        mock_service.get_maintenance_and_capex_records.assert_called_once_with('prop123', 'user123')


    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_calculate_property_equity(self, mock_g, mock_service):
        """Test calculating property equity."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.calculate_property_equity.return_value = {
            "property_id": "prop123",
            "address": "123 Test St",
            "purchase_price": "200000",
            "purchase_date": "2023-01-01",
            "months_owned": 12,
            "estimated_current_value": "206000",
            "total_loan_balance": "156000",
            "initial_equity": "40000",
            "current_equity": "50000",
            "equity_gain": "10000",
            "equity_from_loan_paydown": "4000",
            "equity_from_appreciation": "6000",
            "monthly_equity_gain": "833.33",
            "partner_equity": {
                "Partner 1": {
                    "equity_share": "60",
                    "initial_equity": "24000",
                    "current_equity": "30000",
                    "equity_gain": "6000"
                },
                "Partner 2": {
                    "equity_share": "40",
                    "initial_equity": "16000",
                    "current_equity": "20000",
                    "equity_gain": "4000"
                }
            }
        }
        
        # Make request
        response = self.app.get('/api/property-financials/equity/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('equity_details', data)
        self.assertEqual(data['equity_details']['property_id'], 'prop123')
        self.assertEqual(data['equity_details']['address'], '123 Test St')
        self.assertEqual(data['equity_details']['purchase_price'], '200000')
        self.assertEqual(data['equity_details']['months_owned'], 12)
        self.assertEqual(data['equity_details']['initial_equity'], '40000')
        self.assertEqual(data['equity_details']['current_equity'], '50000')
        self.assertEqual(data['equity_details']['equity_gain'], '10000')
        
        # Verify service was called correctly
        mock_service.calculate_property_equity.assert_called_once_with('prop123', 'user123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_calculate_property_equity_no_access(self, mock_g, mock_service):
        """Test calculating property equity with no access."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.calculate_property_equity.side_effect = ValueError("User does not have access to this property")
        
        # Make request
        response = self.app.get('/api/property-financials/equity/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'User does not have access to this property')
        
        # Verify service was called correctly
        mock_service.calculate_property_equity.assert_called_once_with('prop123', 'user123')
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_calculate_cash_flow_metrics(self, mock_g, mock_service):
        """Test calculating cash flow metrics."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.calculate_cash_flow_metrics.return_value = {
            'net_operating_income': {
                'monthly': '1200',
                'annual': '14400'
            },
            'total_income': {
                'monthly': '1500',
                'annual': '18000'
            },
            'total_expenses': {
                'monthly': '300',
                'annual': '3600'
            },
            'cash_flow': {
                'monthly': '400',
                'annual': '4800'
            },
            'cap_rate': '7.2',
            'cash_on_cash_return': '12.0',
            'debt_service_coverage_ratio': '1.5',
            'cash_invested': '40000',
            'metadata': {
                'has_complete_history': True,
                'data_quality': {
                    'confidence_level': 'high',
                    'refinance_info': {
                        'has_refinanced': False,
                        'original_debt_service': '800',
                        'current_debt_service': '800'
                    }
                }
            }
        }
        
        # Make request
        response = self.app.get('/api/property-financials/cash-flow/prop123?start_date=2023-01-01&end_date=2023-12-31')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('metrics', data)
        self.assertIn('net_operating_income', data['metrics'])
        self.assertIn('total_income', data['metrics'])
        self.assertIn('total_expenses', data['metrics'])
        self.assertIn('cash_flow', data['metrics'])
        self.assertIn('cap_rate', data['metrics'])
        self.assertIn('cash_on_cash_return', data['metrics'])
        self.assertIn('debt_service_coverage_ratio', data['metrics'])
        
        # Verify service was called correctly
        mock_service.calculate_cash_flow_metrics.assert_called_once_with(
            'prop123', 
            'user123',
            start_date='2023-01-01',
            end_date='2023-12-31'
        )
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_calculate_cash_flow_metrics_no_access(self, mock_g, mock_service):
        """Test calculating cash flow metrics with no access."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.calculate_cash_flow_metrics.side_effect = ValueError("User does not have access to this property")
        
        # Make request
        response = self.app.get('/api/property-financials/cash-flow/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'User does not have access to this property')
        
        # Verify service was called correctly
        mock_service.calculate_cash_flow_metrics.assert_called_once_with(
            'prop123', 
            'user123',
            start_date=None,
            end_date=None
        )
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_compare_actual_to_projected(self, mock_g, mock_service):
        """Test comparing actual performance to analysis projections."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.compare_actual_to_projected.return_value = {
            'property_id': 'prop123',
            'address': '123 Test St',
            'actual_metrics': {
                'net_operating_income': {
                    'monthly': '1200',
                    'annual': '14400'
                },
                'total_income': {
                    'monthly': '1500',
                    'annual': '18000'
                },
                'total_expenses': {
                    'monthly': '300',
                    'annual': '3600'
                },
                'cash_flow': {
                    'monthly': '400',
                    'annual': '4800'
                },
                'cap_rate': '7.2',
                'cash_on_cash_return': '12.0',
                'debt_service_coverage_ratio': '1.5'
            },
            'projected_metrics': {
                'net_operating_income': {
                    'monthly': '1280',
                    'annual': '15360'
                },
                'total_income': {
                    'monthly': '1600',
                    'annual': '19200'
                },
                'total_expenses': {
                    'monthly': '320',
                    'annual': '3840'
                },
                'cash_flow': {
                    'monthly': '450',
                    'annual': '5400'
                },
                'cap_rate': '7.68',
                'cash_on_cash_return': '13.5',
                'debt_service_coverage_ratio': '1.6'
            },
            'comparison': {
                'income': {
                    'monthly_variance': '-100',
                    'monthly_variance_percentage': '-6.25',
                    'is_better_than_projected': False
                },
                'expenses': {
                    'monthly_variance': '-20',
                    'monthly_variance_percentage': '-6.25',
                    'is_better_than_projected': True
                },
                'noi': {
                    'monthly_variance': '-80',
                    'monthly_variance_percentage': '-6.25',
                    'is_better_than_projected': False
                },
                'cash_flow': {
                    'monthly_variance': '-50',
                    'monthly_variance_percentage': '-11.11',
                    'is_better_than_projected': False
                },
                'overall': {
                    'performance_score': 25.0,
                    'metrics_better_than_projected': 1,
                    'total_metrics_compared': 4,
                    'is_better_than_projected': False
                }
            },
            'analysis_details': {
                'id': 'analysis123',
                'name': 'Test Analysis',
                'type': 'LTR'
            },
            'available_analyses': [
                {
                    'id': 'analysis123',
                    'name': 'Test Analysis'
                }
            ]
        }
        
        # Make request
        response = self.app.get('/api/property-financials/compare/prop123?analysis_id=analysis123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('comparison', data)
        self.assertIn('actual_metrics', data['comparison'])
        self.assertIn('projected_metrics', data['comparison'])
        self.assertIn('comparison', data['comparison'])
        self.assertIn('analysis_details', data['comparison'])
        self.assertIn('available_analyses', data['comparison'])
        
        # Verify service was called correctly
        mock_service.compare_actual_to_projected.assert_called_once_with(
            'prop123', 
            'user123',
            analysis_id='analysis123'
        )
    
    @patch('src.routes.property_financial_routes.property_financial_service')
    @patch('flask.g')
    def test_compare_actual_to_projected_no_access(self, mock_g, mock_service):
        """Test comparing actual performance to analysis projections with no access."""
        # Set up mocks
        mock_g.current_user = self.test_user
        mock_service.compare_actual_to_projected.side_effect = ValueError("User does not have access to this property")
        
        # Make request
        response = self.app.get('/api/property-financials/compare/prop123')
        
        # Parse response
        data = json.loads(response.data)
        
        # Verify response
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'User does not have access to this property')
        
        # Verify service was called correctly
        mock_service.compare_actual_to_projected.assert_called_once_with(
            'prop123', 
            'user123',
            analysis_id=None
        )


if __name__ == '__main__':
    unittest.main()
