# tests/test_integrations/test_property_workflow.py
import unittest
from unittest.mock import patch
from app import create_app

class TestPropertyWorkflow(unittest.TestCase):
    """Integration tests for complete property-related workflows"""
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_complete_property_workflow(self):
        """Test complete property workflow: add, update, analyze, delete"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = '123'

        # Step 1: Add property
        property_data = {
            'address': '123 Test St',
            'purchase_price': 200000,
            'purchase_date': '2024-01-01'
        }
        
        response = self.client.post(
            '/api/properties',
            json=property_data
        )
        self.assertEqual(response.status_code, 201)
        property_id = json.loads(response.data)['property_id']

        # Step 2: Add transaction
        transaction_data = {
            'property_id': property_id,
            'amount': 2000,
            'category': 'RENT',
            'date': '2024-02-01'
        }
        
        response = self.client.post(
            '/api/transactions',
            json=transaction_data
        )
        self.assertEqual(response.status_code, 201)

        # Step 3: Create analysis
        analysis_data = {
            'property_id': property_id,
            'analysis_type': 'ACQUISITION',
            'assumptions': {
                'holding_period': 5,
                'appreciation_rate': 0.03
            }
        }
        
        response = self.client.post(
            '/api/analyses',
            json=analysis_data
        )
        self.assertEqual(response.status_code, 201)

        # Step 4: Verify property metrics
        response = self.client.get(f'/api/properties/{property_id}/metrics')
        self.assertEqual(response.status_code, 200)
        metrics = json.loads(response.data)
        self.assertIn('monthly_cashflow', metrics)

        # Step 5: Delete property
        response = self.client.delete(f'/api/properties/{property_id}')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()