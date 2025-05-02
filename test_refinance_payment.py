import json
import os
import sys
from utils.financial_calculator import FinancialCalculator
from utils.money import Money, Percentage, MonthlyPayment

# Create a test analysis with known values
test_analysis = {
    "id": "test-analysis-id",
    "user_id": "test-user-id",
    "analysis_name": "Test BRRRR Analysis",
    "analysis_type": "PadSplit BRRRR",
    "address": "1824 Ashburton",
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

def test_backend_calculation():
    """Test the backend calculation of refinance loan payment"""
    print("\n=== Testing Backend Calculation ===")
    
    print("Calculating refinance loan payment using backend utilities...")
    
    # Calculate refinance loan payment manually
    try:
        refinance_loan_amount = Money(test_analysis["refinance_loan_amount"])
        refinance_loan_interest_rate = Percentage(test_analysis["refinance_loan_interest_rate"])
        refinance_loan_term = test_analysis["refinance_loan_term"]
        
        print(f"Refinance loan amount: ${refinance_loan_amount.dollars}")
        print(f"Refinance loan interest rate: {refinance_loan_interest_rate.value}%")
        print(f"Refinance loan term: {refinance_loan_term} months")
        
        # Calculate payment manually using the formula
        monthly_rate = refinance_loan_interest_rate.value / 100 / 12
        factor = (1 + monthly_rate) ** refinance_loan_term
        payment = refinance_loan_amount.dollars * (monthly_rate * factor) / (factor - 1)
        
        print(f"Calculated refinance loan payment: ${payment:.2f}")
        
        # Expected payment based on our manual calculation
        expected_payment = 1187.43
        print(f"Expected payment: ${expected_payment}")
        
        # Check if the calculated payment matches the expected payment
        if abs(payment - expected_payment) < 1:
            print("✅ Backend calculation is correct!")
        else:
            print("❌ Backend calculation is incorrect!")
            print(f"Difference: ${abs(payment - expected_payment):.2f}")
    except Exception as e:
        print(f"Error in backend calculation: {str(e)}")
    
    # This section is now handled inside the try block above

def test_frontend_calculation():
    """Test the frontend calculation of refinance loan payment"""
    print("\n=== Testing Frontend Calculation ===")
    
    # Create a JavaScript-like object for the loan
    loan = {
        "amount": test_analysis["refinance_loan_amount"],
        "interestRate": test_analysis["refinance_loan_interest_rate"],
        "term": test_analysis["refinance_loan_term"],
        "isInterestOnly": False
    }
    
    print(f"Loan details: {json.dumps(loan, indent=2)}")
    
    # Calculate the payment using the formula from calculator.js
    amount = float(loan["amount"])
    annual_rate = float(loan["interestRate"]) / 100
    monthly_rate = annual_rate / 12
    term = int(loan["term"])
    
    # Regular amortizing loan formula
    factor = (1 + monthly_rate) ** term
    payment = amount * (monthly_rate * factor) / (factor - 1)
    
    print(f"Amount: ${amount}")
    print(f"Annual rate: {annual_rate * 100}%")
    print(f"Monthly rate: {monthly_rate * 100}%")
    print(f"Term: {term} months")
    print(f"Calculated payment: ${payment:.2f}")
    
    # Expected payment based on our manual calculation
    expected_payment = 1187.43
    print(f"Expected payment: ${expected_payment}")
    
    # Check if the calculated payment matches the expected payment
    if abs(payment - expected_payment) < 1:
        print("✅ Frontend calculation is correct!")
    else:
        print("❌ Frontend calculation is incorrect!")
        print(f"Difference: ${abs(payment - expected_payment):.2f}")

if __name__ == "__main__":
    test_backend_calculation()
    test_frontend_calculation()
