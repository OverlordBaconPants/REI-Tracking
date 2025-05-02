import os
import sys
import json
import uuid
from flask import Flask, current_app
from services.analysis_service import AnalysisService
import datetime

# Create a test analysis with known values
test_analysis = {
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

def create_app():
    """Create a test Flask app"""
    app = Flask(__name__)
    app.config['ANALYSES_DIR'] = 'test_analyses'
    app.config['DATA_DIR'] = 'test_data'
    return app

def test_analysis_service():
    """Test the AnalysisService with our changes"""
    print("\n=== Testing AnalysisService ===")
    
    # Create a test Flask app
    app = create_app()
    
    # Create the test analyses directory if it doesn't exist
    os.makedirs(app.config['ANALYSES_DIR'], exist_ok=True)
    
    # Create a test analysis file
    test_file_path = os.path.join(app.config['ANALYSES_DIR'], f"{test_analysis['id']}_{test_analysis['user_id']}.json")
    with open(test_file_path, 'w') as f:
        json.dump(test_analysis, f)
    
    print(f"Created test analysis file at {test_file_path}")
    
    # Test the AnalysisService within the app context
    with app.app_context():
        try:
            service = AnalysisService()
            analysis = service.get_analysis(test_analysis['id'], test_analysis['user_id'])
            
            if analysis:
                print("Analysis retrieved successfully")
                
                # Check if refinance_loan_payment is in calculated_metrics
                calculated_metrics = analysis.get('calculated_metrics', {})
                refinance_loan_payment = calculated_metrics.get('refinance_loan_payment')
                
                if refinance_loan_payment:
                    print(f"Refinance loan payment found: {refinance_loan_payment}")
                    
                    # Convert to float for comparison
                    payment_value = float(refinance_loan_payment.replace('$', '').replace(',', ''))
                    expected_payment = 1187.43
                    
                    if abs(payment_value - expected_payment) < 1:
                        print("✅ AnalysisService calculation is correct!")
                    else:
                        print("❌ AnalysisService calculation is incorrect!")
                        print(f"Difference: ${abs(payment_value - expected_payment):.2f}")
                else:
                    print("❌ Refinance loan payment not found in calculated metrics")
            else:
                print("❌ Analysis not found")
                
        except Exception as e:
            print(f"Error testing AnalysisService: {str(e)}")
    
    # Clean up the test file
    try:
        os.remove(test_file_path)
        print(f"Removed test analysis file: {test_file_path}")
    except:
        print(f"Could not remove test file: {test_file_path}")
    
    # Try to remove the test directory
    try:
        os.rmdir(app.config['ANALYSES_DIR'])
        print(f"Removed test directory: {app.config['ANALYSES_DIR']}")
    except:
        print(f"Could not remove test directory: {app.config['ANALYSES_DIR']}")

if __name__ == "__main__":
    test_analysis_service()
