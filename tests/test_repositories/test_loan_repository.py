import pytest
import os
import json
from datetime import date, timedelta
from src.models.loan import Loan, LoanType, LoanStatus
from src.repositories.loan_repository import LoanRepository
from src.utils.money import Money, Percentage

class TestLoanRepository:
    """Test suite for the LoanRepository class."""
    
    @pytest.fixture
    def repo(self, tmpdir):
        """Create a temporary repository for testing."""
        # Create a temporary data directory
        data_dir = tmpdir.mkdir("data")
        
        # Create a repository
        repo = LoanRepository(str(data_dir))
        
        # Return the repository
        return repo
    
    @pytest.fixture
    def sample_loan(self):
        """Create a sample loan for testing."""
        return Loan(
            id="loan123",
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            lender="Test Bank",
            loan_number="L12345"
        )
    
    def test_create_loan(self, repo, sample_loan):
        """Test creating a loan."""
        # Create the loan
        created_loan = repo.create(sample_loan)
        
        # Check that the loan was created
        assert created_loan.id == sample_loan.id
        assert created_loan.property_id == sample_loan.property_id
        assert created_loan.amount.dollars == sample_loan.amount.dollars
        
        # Check that the loan was saved to the repository
        loans = repo.get_all()
        assert len(loans) == 1
        assert loans[0].id == sample_loan.id
    
    def test_get_loan_by_id(self, repo, sample_loan):
        """Test getting a loan by ID."""
        # Create the loan
        repo.create(sample_loan)
        
        # Get the loan by ID
        loan = repo.get_loan_by_id(sample_loan.id)
        
        # Check that the loan was retrieved
        assert loan is not None
        assert loan.id == sample_loan.id
        assert loan.property_id == sample_loan.property_id
        
        # Try to get a non-existent loan
        loan = repo.get_loan_by_id("non-existent")
        assert loan is None
    
    def test_get_loans_by_property(self, repo):
        """Test getting loans by property ID."""
        # Create some loans
        loan1 = Loan(
            id="loan1",
            property_id="prop1",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today()
        )
        
        loan2 = Loan(
            id="loan2",
            property_id="prop1",
            loan_type=LoanType.ADDITIONAL,
            amount=Money(50000),
            interest_rate=Percentage(5.0),
            term_months=180,
            start_date=date.today()
        )
        
        loan3 = Loan(
            id="loan3",
            property_id="prop2",
            loan_type=LoanType.INITIAL,
            amount=Money(300000),
            interest_rate=Percentage(4.0),
            term_months=360,
            start_date=date.today()
        )
        
        # Add the loans to the repository
        repo.create(loan1)
        repo.create(loan2)
        repo.create(loan3)
        
        # Get loans for property 1
        loans = repo.get_loans_by_property("prop1")
        
        # Check that we got the right loans
        assert len(loans) == 2
        assert any(loan.id == "loan1" for loan in loans)
        assert any(loan.id == "loan2" for loan in loans)
        
        # Get loans for property 2
        loans = repo.get_loans_by_property("prop2")
        
        # Check that we got the right loans
        assert len(loans) == 1
        assert loans[0].id == "loan3"
        
        # Get loans for a non-existent property
        loans = repo.get_loans_by_property("non-existent")
        assert len(loans) == 0
    
    def test_get_active_loans_by_property(self, repo):
        """Test getting active loans by property ID."""
        # Create some loans
        loan1 = Loan(
            id="loan1",
            property_id="prop1",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            status=LoanStatus.ACTIVE
        )
        
        loan2 = Loan(
            id="loan2",
            property_id="prop1",
            loan_type=LoanType.ADDITIONAL,
            amount=Money(50000),
            interest_rate=Percentage(5.0),
            term_months=180,
            start_date=date.today(),
            status=LoanStatus.PAID_OFF
        )
        
        # Add the loans to the repository
        repo.create(loan1)
        repo.create(loan2)
        
        # Get active loans for property 1
        loans = repo.get_active_loans_by_property("prop1")
        
        # Check that we got only the active loan
        assert len(loans) == 1
        assert loans[0].id == "loan1"
    
    def test_update_loan(self, repo, sample_loan):
        """Test updating a loan."""
        # Create the loan
        repo.create(sample_loan)
        
        # Update the loan
        updated_data = {
            "amount": "$250000",
            "interest_rate": "5.0%",
            "lender": "New Bank"
        }
        
        updated_loan = repo.update_loan(sample_loan.id, updated_data)
        
        # Check that the loan was updated
        assert updated_loan is not None
        assert updated_loan.id == sample_loan.id
        assert updated_loan.amount.dollars == 250000
        assert updated_loan.interest_rate.value == 5.0
        assert updated_loan.lender == "New Bank"
        
        # Check that other properties were preserved
        assert updated_loan.property_id == sample_loan.property_id
        assert updated_loan.term_months == sample_loan.term_months
        
        # Try to update a non-existent loan
        updated_loan = repo.update_loan("non-existent", updated_data)
        assert updated_loan is None
    
    def test_delete_loan(self, repo, sample_loan):
        """Test deleting a loan."""
        # Create the loan
        repo.create(sample_loan)
        
        # Delete the loan
        success = repo.delete_loan(sample_loan.id)
        
        # Check that the loan was deleted
        assert success is True
        assert repo.get_loan_by_id(sample_loan.id) is None
        
        # Try to delete a non-existent loan
        success = repo.delete_loan("non-existent")
        assert success is False
    
    def test_refinance_loan(self, repo, sample_loan):
        """Test refinancing a loan."""
        # Create the loan
        repo.create(sample_loan)
        
        # Refinance the loan
        new_loan_data = {
            "property_id": sample_loan.property_id,
            "amount": "$220000",
            "interest_rate": "3.75%",
            "term_months": 360,
            "start_date": date.today().isoformat(),
            "lender": "Refinance Bank"
        }
        
        new_loan = repo.refinance_loan(sample_loan.id, new_loan_data)
        
        # Check that the new loan was created
        assert new_loan is not None
        assert new_loan.loan_type == LoanType.REFINANCE
        assert new_loan.amount.dollars == 220000
        assert new_loan.interest_rate.value == 3.75
        assert new_loan.refinanced_from_id == sample_loan.id
        
        # Check that the old loan was marked as refinanced
        old_loan = repo.get_loan_by_id(sample_loan.id)
        assert old_loan.status == LoanStatus.REFINANCED
        
        # Try to refinance a non-existent loan
        new_loan = repo.refinance_loan("non-existent", new_loan_data)
        assert new_loan is None
    
    def test_pay_off_loan(self, repo, sample_loan):
        """Test marking a loan as paid off."""
        # Create the loan
        repo.create(sample_loan)
        
        # Pay off the loan
        payoff_date = date.today() - timedelta(days=30)
        updated_loan = repo.pay_off_loan(sample_loan.id, payoff_date)
        
        # Check that the loan was marked as paid off
        assert updated_loan is not None
        assert updated_loan.status == LoanStatus.PAID_OFF
        assert updated_loan.last_updated == payoff_date
        assert updated_loan.current_balance.dollars == 0
        
        # Try to pay off a non-existent loan
        updated_loan = repo.pay_off_loan("non-existent", payoff_date)
        assert updated_loan is None
    
    def test_update_loan_balance(self, repo, sample_loan):
        """Test updating a loan's balance."""
        # Create the loan
        repo.create(sample_loan)
        
        # Update the balance
        as_of_date = date.today() + timedelta(days=365)  # 1 year from now
        updated_loan = repo.update_loan_balance(sample_loan.id, as_of_date)
        
        # Check that the balance was updated
        assert updated_loan is not None
        assert updated_loan.current_balance is not None
        assert updated_loan.current_balance.dollars < sample_loan.amount.dollars
        assert updated_loan.last_updated == as_of_date
        
        # Try to update the balance of a non-existent loan
        updated_loan = repo.update_loan_balance("non-existent", as_of_date)
        assert updated_loan is None
    
    def test_get_total_debt_for_property(self, repo):
        """Test calculating the total debt for a property."""
        # Create some loans
        loan1 = Loan(
            id="loan1",
            property_id="prop1",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            status=LoanStatus.ACTIVE
        )
        
        loan2 = Loan(
            id="loan2",
            property_id="prop1",
            loan_type=LoanType.ADDITIONAL,
            amount=Money(50000),
            interest_rate=Percentage(5.0),
            term_months=180,
            start_date=date.today(),
            status=LoanStatus.ACTIVE
        )
        
        loan3 = Loan(
            id="loan3",
            property_id="prop1",
            loan_type=LoanType.ADDITIONAL,
            amount=Money(30000),
            interest_rate=Percentage(6.0),
            term_months=120,
            start_date=date.today(),
            status=LoanStatus.PAID_OFF
        )
        
        # Add the loans to the repository
        repo.create(loan1)
        repo.create(loan2)
        repo.create(loan3)
        
        # Calculate the total debt
        total_debt = repo.get_total_debt_for_property("prop1")
        
        # Check that only active loans were included
        assert total_debt.dollars == 250000  # 200000 + 50000
    
    def test_get_total_monthly_payment_for_property(self, repo):
        """Test calculating the total monthly payment for a property."""
        # Create some loans
        loan1 = Loan(
            id="loan1",
            property_id="prop1",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            status=LoanStatus.ACTIVE
        )
        
        loan2 = Loan(
            id="loan2",
            property_id="prop1",
            loan_type=LoanType.ADDITIONAL,
            amount=Money(50000),
            interest_rate=Percentage(5.0),
            term_months=180,
            start_date=date.today(),
            status=LoanStatus.ACTIVE
        )
        
        # Add the loans to the repository
        repo.create(loan1)
        repo.create(loan2)
        
        # Calculate the total monthly payment
        total_payment = repo.get_total_monthly_payment_for_property("prop1")
        
        # Check that the total payment is the sum of the individual payments
        loan1_payment = loan1.monthly_payment.dollars
        loan2_payment = loan2.monthly_payment.dollars
        expected_total = loan1_payment + loan2_payment
        
        assert abs(total_payment.dollars - expected_total) < 0.01
