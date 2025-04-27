import pytest
from datetime import date
from src.utils.calculations.loan_comparison import LoanComparison
from src.utils.money import Money, Percentage
from src.utils.calculations.loan_details import LoanDetails

class TestLoanComparison:
    """Test suite for the LoanComparison utility."""
    
    def test_compare_loans(self):
        """Test comparing multiple loan options."""
        # Create loan options
        loan1 = {
            "name": "Option 1",
            "amount": Money(200000),
            "interest_rate": Percentage(4.5),
            "term_months": 360,
            "is_interest_only": False
        }
        
        loan2 = {
            "name": "Option 2",
            "amount": Money(200000),
            "interest_rate": Percentage(3.75),
            "term_months": 360,
            "is_interest_only": False
        }
        
        loan3 = {
            "name": "Option 3",
            "amount": Money(200000),
            "interest_rate": Percentage(4.0),
            "term_months": 180,
            "is_interest_only": False
        }
        
        # Compare loans
        comparison = LoanComparison.compare_loans([loan1, loan2, loan3])
        
        # Check comparison results
        assert len(comparison['loans']) == 3
        assert comparison['loans'][0]['name'] == "Option 1"
        assert comparison['loans'][1]['name'] == "Option 2"
        assert comparison['loans'][2]['name'] == "Option 3"
        
        # Check that Option 2 has the lowest monthly payment
        assert comparison['loans'][1]['monthly_payment'].dollars < comparison['loans'][0]['monthly_payment'].dollars
        
        # Check that Option 3 has the highest monthly payment but lowest total interest
        assert comparison['loans'][2]['monthly_payment'].dollars > comparison['loans'][0]['monthly_payment'].dollars
        assert comparison['loans'][2]['total_interest'].dollars < comparison['loans'][0]['total_interest'].dollars
        
        # Check metrics and recommendation
        assert 'metrics' in comparison
        assert 'recommendation' in comparison
        assert 'lowest_monthly_payment' in comparison['metrics']
        assert 'lowest_total_interest' in comparison['metrics']
        assert 'lowest_interest_to_principal_ratio' in comparison['metrics']
    
    def test_calculate_refinance_savings(self):
        """Test calculating refinance savings."""
        # Create current loan
        current_loan = {
            "amount": Money(200000),
            "interest_rate": Percentage(4.5),
            "term_months": 360,
            "is_interest_only": False,
            "months_paid": 60  # 5 years into the loan
        }
        
        # Create new loan
        new_loan = {
            "amount": Money(190000),  # Remaining balance after 5 years
            "interest_rate": Percentage(3.75),
            "term_months": 360,
            "is_interest_only": False
        }
        
        # Calculate refinance savings
        closing_costs = Money(4000)
        savings = LoanComparison.calculate_refinance_savings(current_loan, new_loan, closing_costs)
        
        # Check savings results
        assert 'monthly_payment_savings' in savings
        assert 'monthly_payment_before' in savings
        assert 'monthly_payment_after' in savings
        assert 'total_interest_savings' in savings
        assert 'break_even_months' in savings
        
        # Monthly payment should be lower with the new loan
        assert savings['monthly_payment_before'].dollars > savings['monthly_payment_after'].dollars
        
        # Break-even point should be positive
        assert savings['break_even_months'] > 0
    
    def test_interest_to_principal_calculation(self):
        """Test interest-to-principal ratio calculation."""
        # Create a loan option
        loan = {
            "name": "Test Loan",
            "amount": Money(200000),
            "interest_rate": Percentage(4.5),
            "term_months": 360,
            "is_interest_only": False
        }
        
        # Compare the loan (this will calculate the interest-to-principal ratio)
        comparison = LoanComparison.compare_loans([loan])
        
        # Extract the interest-to-principal ratio
        ratio_str = comparison['loans'][0]['interest_to_principal_ratio']
        ratio = float(ratio_str.strip('%')) / 100
        
        # For a 30-year loan at 4.5%, the ratio should be around 0.8
        # (total interest is about 80% of the principal)
        assert 0.7 < ratio < 0.9
