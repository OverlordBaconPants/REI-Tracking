import unittest
import os
import sys
import json
import uuid
import datetime
from flask import Flask

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.analysis_service import AnalysisService

class TestAnalysisServiceRefinance(unittest.TestCase):
    """Test cases for the AnalysisService class focusing on refinance loan payment calculation."""

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
            "analysis_name": "Test BRRRR Analysis",
            "analysis_type": "PadSplit BRRRR",
            "address": "1824 Ashburton",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d"),
            "purchase_price": 150000,
            "after_repair_value": 235000,
            "renovation_costs": 25000,
            "renovation_duration": 3,
            "initial_loan_amount": 140000,
            "initial_loan_down_payment": 10000,
            "initial_loan_interest_rate": 12,
            "initial_loan_term": 12,
            "initial_interest_only": True,
            "initial_loan_closing_costs": 5000,
            "refinance_ltv_percentage": 75,
            "refinance_loan_amount": 176250,  # 75% of ARV (235000)
            "refinance_loan_interest_rate": 7.125,
            "refinance_loan_term": 360,  # 30 years
            "refinance_loan_closing_costs": 5000,
            "monthly_rent": 3000,
            "property_taxes": 200,
            "insurance": 100,
            "management_fee_percentage": 8,
            "capex_percentage": 2,
            "vacancy_percentage": 4,
            "repairs_percentage": 2,
            "furnishing_costs": 10000,
            "utilities": 200,
            "internet": 100,
            "cleaning": 150,
            "pest_control": 50,
            "landscaping": 100,
            "padsplit_platform_percentage": 15
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

    def test_refinance_loan_payment_calculation(self):
        """Test that refinance loan payment is correctly calculated for BRRRR analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Get the analysis
            analysis = service.get_analysis(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check if the analysis was retrieved
            self.assertIsNotNone(analysis, "Analysis should be retrieved successfully")
            
            # Check if calculated_metrics exists
            self.assertIn('calculated_metrics', analysis, "Analysis should have calculated_metrics")
            
            # Check if refinance_loan_payment is in calculated_metrics
            self.assertIn('refinance_loan_payment', analysis['calculated_metrics'], 
                         "calculated_metrics should include refinance_loan_payment")
            
            # Get the refinance loan payment
            refinance_loan_payment = analysis['calculated_metrics']['refinance_loan_payment']
            
            # Convert to float for comparison (removing $ and commas)
            payment_value = float(refinance_loan_payment.replace('$', '').replace(',', ''))
            
            # Expected payment for $176,250 at 7.125% for 360 months is $1,187.43
            expected_payment = 1187.43
            
            # Check if the calculated payment matches the expected payment
            self.assertAlmostEqual(payment_value, expected_payment, delta=1, 
                                  msg="Refinance loan payment should be approximately $1,187.43")

    def test_initial_loan_payment_calculation(self):
        """Test that initial loan payment is correctly calculated for BRRRR analysis."""
        with self.app.app_context():
            # Create an instance of AnalysisService
            service = AnalysisService()
            
            # Get the analysis
            analysis = service.get_analysis(self.test_analysis['id'], self.test_analysis['user_id'])
            
            # Check if the analysis was retrieved
            self.assertIsNotNone(analysis, "Analysis should be retrieved successfully")
            
            # Check if calculated_metrics exists
            self.assertIn('calculated_metrics', analysis, "Analysis should have calculated_metrics")
            
            # Check if initial_loan_payment is in calculated_metrics
            self.assertIn('initial_loan_payment', analysis['calculated_metrics'], 
                         "calculated_metrics should include initial_loan_payment")
            
            # Get the initial loan payment
            initial_loan_payment = analysis['calculated_metrics']['initial_loan_payment']
            
            # Convert to float for comparison (removing $ and commas)
            payment_value = float(initial_loan_payment.replace('$', '').replace(',', ''))
            
            # Expected payment for $140,000 at 12% interest-only is $1,400
            expected_payment = 1400.00
            
            # Check if the calculated payment matches the expected payment
            self.assertAlmostEqual(payment_value, expected_payment, delta=1, 
                                  msg="Initial loan payment should be approximately $1,400.00")

if __name__ == '__main__':
    unittest.main()
