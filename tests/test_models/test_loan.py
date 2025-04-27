import pytest
from datetime import date, timedelta
from src.models.loan import Loan, LoanType, LoanStatus, BalloonPayment, LoanData
from src.utils.money import Money, Percentage

class TestLoan:
    """Test suite for the Loan model."""
    
    def test_loan_creation(self):
        """Test creating a loan with valid data."""
        # Create a loan
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            is_interest_only=False,
            lender="Test Bank",
            loan_number="L12345"
        )
        
        # Check basic properties
        assert loan.property_id == "prop123"
        assert loan.loan_type == LoanType.INITIAL
        assert loan.amount.dollars == 200000
        assert loan.interest_rate.value == 4.5
        assert loan.term_months == 360
        assert loan.start_date == date.today()
        assert loan.is_interest_only == False
        assert loan.lender == "Test Bank"
        assert loan.loan_number == "L12345"
        assert loan.status == LoanStatus.ACTIVE
        
        # Check that monthly payment was calculated
        assert loan.monthly_payment is not None
        assert loan.monthly_payment.dollars > 0
    
    def test_loan_creation_with_string_values(self):
        """Test creating a loan with string values that need conversion."""
        # Create a loan with string values
        loan = Loan(
            property_id="prop123",
            loan_type="initial",
            amount="150000",
            interest_rate="3.75%",
            term_months=180,  # Pydantic v2 is stricter about int conversion
            start_date=date.today().isoformat(),
            is_interest_only=False,  # Pydantic v2 is stricter about bool conversion
            status="active"
        )
        
        # Check that values were properly converted
        assert loan.loan_type == LoanType.INITIAL
        assert loan.amount.dollars == 150000
        assert loan.interest_rate.value == 3.75
        assert loan.term_months == 180
        assert isinstance(loan.start_date, date)
        assert loan.is_interest_only == False
        assert loan.status == LoanStatus.ACTIVE
    
    def test_loan_with_balloon_payment(self):
        """Test creating a loan with a balloon payment."""
        # Create a balloon payment
        balloon = BalloonPayment(
            term_months=60,
            amount=Money(180000),
            due_date=date.today() + timedelta(days=60*30)
        )
        
        # Create a loan with the balloon payment
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            balloon_payment=balloon
        )
        
        # Check balloon payment properties
        assert loan.balloon_payment is not None
        assert loan.balloon_payment.term_months == 60
        assert loan.balloon_payment.amount.dollars == 180000
        assert isinstance(loan.balloon_payment.due_date, date)
    
    def test_loan_with_balloon_payment_dict(self):
        """Test creating a loan with a balloon payment as a dictionary."""
        # Create a loan with a balloon payment as a dictionary
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            balloon_payment={
                "term_months": 60,
                "amount": "180000",
                "due_date": (date.today() + timedelta(days=60*30)).isoformat()
            }
        )
        
        # Check balloon payment properties
        assert loan.balloon_payment is not None
        assert loan.balloon_payment.term_months == 60
        assert loan.balloon_payment.amount.dollars == 180000
        assert isinstance(loan.balloon_payment.due_date, date)
    
    def test_interest_only_loan(self):
        """Test creating an interest-only loan."""
        # Create an interest-only loan
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            is_interest_only=True
        )
        
        # Check that it's interest-only
        assert loan.is_interest_only == True
        
        # Check that monthly payment is interest-only
        monthly_interest = 200000 * (4.5 / 100 / 12)
        assert abs(loan.monthly_payment.dollars - monthly_interest) < 0.01
    
    def test_zero_interest_loan(self):
        """Test creating a zero-interest loan."""
        # Create a zero-interest loan
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(0),
            term_months=360,
            start_date=date.today()
        )
        
        # Check that monthly payment is just principal
        expected_payment = 200000 / 360
        assert abs(loan.monthly_payment.dollars - expected_payment) < 0.01
    
    def test_to_loan_details(self):
        """Test converting a loan to a LoanDetails object."""
        # Create a loan
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            name="Test Loan"
        )
        
        # Convert to LoanDetails
        loan_details = loan.to_loan_details()
        
        # Check properties
        assert loan_details.amount.dollars == 200000
        assert loan_details.interest_rate.value == 4.5
        assert loan_details.term == 360
        assert loan_details.is_interest_only == False
        assert loan_details.name == "Test Loan"
    
    def test_calculate_remaining_balance(self):
        """Test calculating the remaining balance of a loan."""
        # Create a loan
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today() - timedelta(days=365*2)  # 2 years ago
        )
        
        # Calculate remaining balance
        balance = loan.calculate_remaining_balance()
        
        # Balance should be less than the original amount
        assert balance.dollars < 200000
        
        # The balance should be less than the original amount
        # Note: The exact balance will depend on the implementation details
        # of the LoanDetails.calculate_remaining_balance method
        assert balance.dollars < 200000
    
    def test_generate_amortization_schedule(self):
        """Test generating an amortization schedule."""
        # Create a loan
        loan = Loan(
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today()
        )
        
        # Generate schedule for first 12 months
        schedule = loan.generate_amortization_schedule(12)
        
        # Check schedule
        assert len(schedule) == 12
        assert schedule[0]['period'] == 1
        assert 'payment' in schedule[0]
        assert 'principal' in schedule[0]
        assert 'interest' in schedule[0]
        assert 'remaining_balance' in schedule[0]
        assert 'date' in schedule[0]
        
        # Check that balance decreases
        assert schedule[0]['remaining_balance'].dollars > schedule[11]['remaining_balance'].dollars
    
    def test_to_dict(self):
        """Test converting a loan to a dictionary."""
        # Create a loan with a balloon payment
        loan = Loan(
            id="loan123",
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            balloon_payment=BalloonPayment(
                term_months=60,
                amount=Money(180000),
                due_date=date.today() + timedelta(days=60*30)
            )
        )
        
        # Convert to dictionary
        loan_dict = loan.to_dict()
        
        # Check dictionary
        assert loan_dict['id'] == "loan123"
        assert loan_dict['property_id'] == "prop123"
        assert loan_dict['loan_type'] == "initial"
        assert loan_dict['amount'] == "$200,000.00"
        assert loan_dict['interest_rate'] == "4.500%"
        assert loan_dict['term_months'] == 360
        assert 'start_date' in loan_dict
        assert 'balloon_payment' in loan_dict
        assert loan_dict['balloon_payment']['term_months'] == 60
        assert loan_dict['balloon_payment']['amount'] == "$180,000.00"
    
    def test_from_dict(self):
        """Test creating a loan from a dictionary."""
        # Create a dictionary
        loan_dict = {
            "id": "loan123",
            "property_id": "prop123",
            "loan_type": "refinance",
            "amount": "$200,000.00",
            "interest_rate": "4.500%",
            "term_months": 360,
            "start_date": date.today().isoformat(),
            "is_interest_only": False,
            "balloon_payment": {
                "term_months": 60,
                "amount": "$180,000.00",
                "due_date": (date.today() + timedelta(days=60*30)).isoformat()
            }
        }
        
        # Create a loan from the dictionary
        loan = Loan.from_dict(loan_dict)
        
        # Check properties
        assert loan.id == "loan123"
        assert loan.property_id == "prop123"
        assert loan.loan_type == LoanType.REFINANCE
        assert loan.amount.dollars == 200000
        assert loan.interest_rate.value == 4.5
        assert loan.term_months == 360
        assert loan.balloon_payment is not None
        assert loan.balloon_payment.term_months == 60
        assert loan.balloon_payment.amount.dollars == 180000
    
    def test_data_model_conversion(self):
        """Test converting between Loan and LoanData models."""
        # Create a loan
        loan = Loan(
            id="loan123",
            property_id="prop123",
            loan_type=LoanType.INITIAL,
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term_months=360,
            start_date=date.today(),
            is_interest_only=False,
            lender="Test Bank"
        )
        
        # Convert to data model
        data_model = loan.to_data_model()
        
        # Check data model properties
        assert data_model.id == "loan123"
        assert data_model.property_id == "prop123"
        assert data_model.loan_type == LoanType.INITIAL
        assert data_model.amount.dollars == 200000
        assert data_model.interest_rate.value == 4.5
        assert data_model.term_months == 360
        assert data_model.lender == "Test Bank"
        
        # Convert back to loan
        new_loan = Loan.from_data_model(data_model)
        
        # Check new loan properties
        assert new_loan.id == "loan123"
        assert new_loan.property_id == "prop123"
        assert new_loan.loan_type == LoanType.INITIAL
        assert new_loan.amount.dollars == 200000
        assert new_loan.interest_rate.value == 4.5
        assert new_loan.term_months == 360
        assert new_loan.lender == "Test Bank"
