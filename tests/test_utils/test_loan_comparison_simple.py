import pytest
from datetime import date
from src.utils.calculations.loan_details import LoanDetails
from src.utils.money import Money, Percentage

class TestLoanComparisonSimple:
    """Test suite for loan comparison functionality without using the LoanComparison class directly."""
    
    def test_loan_details_comparison(self):
        """Test comparing different loan options using LoanDetails."""
        # Create loan details objects
        loan1 = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False,
            name="Option 1"
        )
        
        loan2 = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(3.75),
            term=360,
            is_interest_only=False,
            name="Option 2"
        )
        
        loan3 = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.0),
            term=180,
            is_interest_only=False,
            name="Option 3"
        )
        
        # Calculate monthly payments
        payment1 = loan1.calculate_payment().total
        payment2 = loan2.calculate_payment().total
        payment3 = loan3.calculate_payment().total
        
        # Check that Option 2 has the lowest monthly payment
        assert payment2.dollars < payment1.dollars
        
        # Check that Option 3 has the highest monthly payment
        assert payment3.dollars > payment1.dollars
        assert payment3.dollars > payment2.dollars
        
        # Calculate total interest for each loan
        total_interest1 = (payment1.dollars * loan1.term) - loan1.amount.dollars
        total_interest2 = (payment2.dollars * loan2.term) - loan2.amount.dollars
        total_interest3 = (payment3.dollars * loan3.term) - loan3.amount.dollars
        
        # Check that Option 3 has the lowest total interest
        assert total_interest3 < total_interest1
        assert total_interest3 < total_interest2
        
        # Calculate interest-to-principal ratio for each loan
        ratio1 = total_interest1 / loan1.amount.dollars
        ratio2 = total_interest2 / loan2.amount.dollars
        ratio3 = total_interest3 / loan3.amount.dollars
        
        # Check that Option 3 has the lowest interest-to-principal ratio
        assert ratio3 < ratio1
        assert ratio3 < ratio2
    
    def test_refinance_analysis(self):
        """Test analyzing refinance savings."""
        # Create current loan details
        current_loan = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False,
            name="Current Loan"
        )
        
        # Create new loan details (refinance)
        new_loan = LoanDetails(
            amount=Money(190000),  # Remaining balance after 5 years
            interest_rate=Percentage(3.75),
            term=360,
            is_interest_only=False,
            name="New Loan"
        )
        
        # Calculate monthly payments
        current_payment = current_loan.calculate_payment().total
        new_payment = new_loan.calculate_payment().total
        
        # Calculate monthly savings
        monthly_savings = current_payment.dollars - new_payment.dollars
        
        # Check that the new loan has a lower monthly payment
        assert monthly_savings > 0
        
        # Calculate total interest for each loan
        current_total_interest = (current_payment.dollars * current_loan.term) - current_loan.amount.dollars
        new_total_interest = (new_payment.dollars * new_loan.term) - new_loan.amount.dollars
        
        # Calculate interest savings
        interest_savings = current_total_interest - new_total_interest
        
        # Calculate break-even point with $4000 closing costs
        closing_costs = 4000
        break_even_months = closing_costs / monthly_savings
        
        # Check that there are interest savings
        assert interest_savings > 0
        
        # Check that the break-even point is reasonable
        assert 0 < break_even_months < 60  # Less than 5 years
    
    def test_interest_only_comparison(self):
        """Test comparing interest-only vs. amortizing loans."""
        # Create an interest-only loan
        interest_only_loan = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=True,
            name="Interest Only"
        )
        
        # Create an amortizing loan
        amortizing_loan = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False,
            name="Amortizing"
        )
        
        # Calculate monthly payments
        interest_only_payment = interest_only_loan.calculate_payment().total
        amortizing_payment = amortizing_loan.calculate_payment().total
        
        # Check that interest-only has a lower monthly payment
        assert interest_only_payment.dollars < amortizing_payment.dollars
        
        # Calculate total interest for each loan
        interest_only_total_interest = interest_only_payment.dollars * interest_only_loan.term
        amortizing_total_interest = (amortizing_payment.dollars * amortizing_loan.term) - amortizing_loan.amount.dollars
        
        # Check that interest-only has higher total interest
        assert interest_only_total_interest > amortizing_total_interest
