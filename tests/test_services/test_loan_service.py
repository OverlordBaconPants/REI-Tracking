import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from src.models.loan import Loan, LoanType, LoanStatus, BalloonPayment
from src.repositories.loan_repository import LoanRepository
from src.services.loan_service import LoanService
from src.utils.money import Money, Percentage

class TestLoanService:
    """Test suite for the LoanService class."""
    
    @pytest.fixture
    def mock_repo(self):
        """Create a mock repository for testing."""
        return MagicMock(spec=LoanRepository)
    
    @pytest.fixture
    def service(self, mock_repo):
        """Create a service with a mock repository for testing."""
        return LoanService(mock_repo)
    
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
    
    def test_get_loans_by_property(self, service, mock_repo, sample_loan):
        """Test getting loans by property ID."""
        # Set up the mock repository
        mock_repo.get_loans_by_property.return_value = [sample_loan]
        
        # Call the service method
        loans = service.get_loans_by_property("prop123")
        
        # Check that the repository method was called
        mock_repo.get_loans_by_property.assert_called_once_with("prop123")
        
        # Check the result
        assert len(loans) == 1
        assert loans[0].id == sample_loan.id
    
    def test_get_active_loans_by_property(self, service, mock_repo, sample_loan):
        """Test getting active loans by property ID."""
        # Set up the mock repository
        mock_repo.get_active_loans_by_property.return_value = [sample_loan]
        
        # Call the service method
        loans = service.get_active_loans_by_property("prop123")
        
        # Check that the repository method was called
        mock_repo.get_active_loans_by_property.assert_called_once_with("prop123")
        
        # Check the result
        assert len(loans) == 1
        assert loans[0].id == sample_loan.id
    
    def test_get_loan_by_id(self, service, mock_repo, sample_loan):
        """Test getting a loan by ID."""
        # Set up the mock repository
        mock_repo.get_loan_by_id.return_value = sample_loan
        
        # Call the service method
        loan = service.get_loan_by_id("loan123")
        
        # Check that the repository method was called
        mock_repo.get_loan_by_id.assert_called_once_with("loan123")
        
        # Check the result
        assert loan is not None
        assert loan.id == sample_loan.id
    
    def test_create_loan(self, service, mock_repo, sample_loan):
        """Test creating a loan."""
        # Set up the mock repository
        mock_repo.create_loan.return_value = sample_loan
        
        # Create loan data
        loan_data = {
            "property_id": "prop123",
            "loan_type": "initial",
            "amount": "200000",
            "interest_rate": "4.5%",
            "term_months": 360,
            "start_date": date.today().isoformat()
        }
        
        # Call the service method
        loan = service.create_loan(loan_data)
        
        # Check that the repository method was called
        mock_repo.create_loan.assert_called_once()
        
        # Check the result
        assert loan is not None
        assert loan.id == sample_loan.id
    
    def test_create_loan_validation_error(self, service, mock_repo):
        """Test validation error when creating a loan."""
        # Create invalid loan data (missing required fields)
        loan_data = {
            "property_id": "prop123",
            "loan_type": "initial",
            # Missing amount, interest_rate, term_months, start_date
        }
        
        # Call the service method and expect a ValueError
        with pytest.raises(ValueError):
            service.create_loan(loan_data)
        
        # Check that the repository method was not called
        mock_repo.create_loan.assert_not_called()
    
    def test_update_loan(self, service, mock_repo, sample_loan):
        """Test updating a loan."""
        # Set up the mock repository
        mock_repo.update_loan.return_value = sample_loan
        
        # Update loan data
        loan_data = {
            "amount": "250000",
            "interest_rate": "5.0%"
        }
        
        # Call the service method
        loan = service.update_loan("loan123", loan_data)
        
        # Check that the repository method was called
        mock_repo.update_loan.assert_called_once_with("loan123", loan_data)
        
        # Check the result
        assert loan is not None
        assert loan.id == sample_loan.id
    
    def test_delete_loan(self, service, mock_repo):
        """Test deleting a loan."""
        # Set up the mock repository
        mock_repo.delete_loan.return_value = True
        
        # Call the service method
        result = service.delete_loan("loan123")
        
        # Check that the repository method was called
        mock_repo.delete_loan.assert_called_once_with("loan123")
        
        # Check the result
        assert result is True
    
    def test_refinance_loan(self, service, mock_repo, sample_loan):
        """Test refinancing a loan."""
        # Set up the mock repository
        new_loan = Loan(
            id="loan456",
            property_id="prop123",
            loan_type=LoanType.REFINANCE,
            amount=Money(220000),
            interest_rate=Percentage(3.75),
            term_months=360,
            start_date=date.today(),
            refinanced_from_id="loan123"
        )
        mock_repo.refinance_loan.return_value = new_loan
        
        # Refinance loan data
        loan_data = {
            "property_id": "prop123",
            "amount": "220000",
            "interest_rate": "3.75%",
            "term_months": 360,
            "start_date": date.today().isoformat()
        }
        
        # Call the service method
        loan = service.refinance_loan("loan123", loan_data)
        
        # Check that the repository method was called
        mock_repo.refinance_loan.assert_called_once_with("loan123", loan_data)
        
        # Check the result
        assert loan is not None
        assert loan.id == new_loan.id
        assert loan.loan_type == LoanType.REFINANCE
        assert loan.refinanced_from_id == "loan123"
    
    def test_pay_off_loan(self, service, mock_repo, sample_loan):
        """Test marking a loan as paid off."""
        # Set up the mock repository
        paid_off_loan = sample_loan
        paid_off_loan.status = LoanStatus.PAID_OFF
        mock_repo.pay_off_loan.return_value = paid_off_loan
        
        # Call the service method
        payoff_date = date.today() - timedelta(days=30)
        loan = service.pay_off_loan("loan123", payoff_date)
        
        # Check that the repository method was called
        mock_repo.pay_off_loan.assert_called_once_with("loan123", payoff_date)
        
        # Check the result
        assert loan is not None
        assert loan.status == LoanStatus.PAID_OFF
    
    def test_update_loan_balance(self, service, mock_repo, sample_loan):
        """Test updating a loan's balance."""
        # Set up the mock repository
        updated_loan = sample_loan
        updated_loan.current_balance = Money(195000)
        mock_repo.update_loan_balance.return_value = updated_loan
        
        # Call the service method
        as_of_date = date.today() + timedelta(days=365)
        loan = service.update_loan_balance("loan123", as_of_date)
        
        # Check that the repository method was called
        mock_repo.update_loan_balance.assert_called_once_with("loan123", as_of_date)
        
        # Check the result
        assert loan is not None
        assert loan.current_balance.dollars == 195000
    
    def test_get_total_debt_for_property(self, service, mock_repo):
        """Test calculating the total debt for a property."""
        # Set up the mock repository
        mock_repo.get_total_debt_for_property.return_value = Money(250000)
        
        # Call the service method
        as_of_date = date.today()
        total_debt = service.get_total_debt_for_property("prop123", as_of_date)
        
        # Check that the repository method was called
        mock_repo.get_total_debt_for_property.assert_called_once_with("prop123", as_of_date)
        
        # Check the result
        assert total_debt.dollars == 250000
    
    def test_get_total_monthly_payment_for_property(self, service, mock_repo):
        """Test calculating the total monthly payment for a property."""
        # Set up the mock repository
        mock_repo.get_total_monthly_payment_for_property.return_value = Money(1500)
        
        # Call the service method
        total_payment = service.get_total_monthly_payment_for_property("prop123")
        
        # Check that the repository method was called
        mock_repo.get_total_monthly_payment_for_property.assert_called_once_with("prop123")
        
        # Check the result
        assert total_payment.dollars == 1500
    
    def test_generate_amortization_schedule(self, service, mock_repo, sample_loan):
        """Test generating an amortization schedule."""
        # Set up the mock repository
        mock_repo.get_loan_by_id.return_value = sample_loan
        
        # Create a sample schedule
        schedule = [
            {
                'period': 1,
                'payment': Money(1013.37),
                'principal': Money(263.37),
                'interest': Money(750.00),
                'remaining_balance': Money(199736.63),
                'date': date.today().isoformat()
            },
            {
                'period': 2,
                'payment': Money(1013.37),
                'principal': Money(264.36),
                'interest': Money(749.01),
                'remaining_balance': Money(199472.27),
                'date': (date.today() + timedelta(days=30)).isoformat()
            }
        ]
        
        # Mock the generate_amortization_schedule method on the loan
        sample_loan.generate_amortization_schedule = MagicMock(return_value=schedule)
        
        # Call the service method
        result = service.generate_amortization_schedule("loan123", 2)
        
        # Check that the repository method was called
        mock_repo.get_loan_by_id.assert_called_once_with("loan123")
        
        # Check that the loan method was called
        sample_loan.generate_amortization_schedule.assert_called_once_with(2)
        
        # Check the result
        assert len(result) == 2
        assert result[0]['period'] == 1
        assert result[1]['period'] == 2
    
    def test_compare_loans(self, service):
        """Test comparing loan options."""
        # Create loan options
        loan_options = [
            {
                "name": "Option 1",
                "property_id": "prop123",
                "loan_type": "initial",
                "amount": "200000",
                "interest_rate": "4.5%",
                "term_months": 360,
                "start_date": date.today().isoformat()
            },
            {
                "name": "Option 2",
                "property_id": "prop123",
                "loan_type": "initial",
                "amount": "200000",
                "interest_rate": "3.75%",
                "term_months": 360,
                "start_date": date.today().isoformat()
            }
        ]
        
        # Call the service method
        comparison = service.compare_loans(loan_options)
        
        # Check the result
        assert 'loans' in comparison
        assert len(comparison['loans']) == 2
        assert comparison['loans'][0]['name'] == "Option 1"
        assert comparison['loans'][1]['name'] == "Option 2"
        assert 'summary' in comparison
    
    def test_calculate_balloon_payment(self, service, mock_repo, sample_loan):
        """Test calculating balloon payment details."""
        # Set up the mock repository
        mock_repo.get_loan_by_id.return_value = sample_loan
        
        # Call the service method
        balloon_details = service.calculate_balloon_payment("loan123", 60)
        
        # Check that the repository method was called
        mock_repo.get_loan_by_id.assert_called_once_with("loan123")
        
        # Check the result
        assert 'balloon_amount' in balloon_details
        assert 'balloon_date' in balloon_details
        assert 'monthly_payment' in balloon_details
        assert 'total_payments_before_balloon' in balloon_details
    
    def test_update_balloon_payment(self, service, mock_repo, sample_loan):
        """Test updating a loan with balloon payment details."""
        # Set up the mock repository
        mock_repo.get_loan_by_id.return_value = sample_loan
        
        # Create balloon details
        balloon_details = {
            'balloon_amount': "$180000.00",
            'balloon_date': (date.today() + timedelta(days=60*30)).isoformat(),
            'monthly_payment': "$1013.37",
            'total_payments_before_balloon': "$60802.20"
        }
        
        # Mock the calculate_balloon_payment method
        service.calculate_balloon_payment = MagicMock(return_value=balloon_details)
        
        # Mock the update_loan method
        updated_loan = sample_loan
        updated_loan.balloon_payment = BalloonPayment(
            term_months=60,
            amount=Money(180000),
            due_date=date.today() + timedelta(days=60*30)
        )
        service.update_loan = MagicMock(return_value=updated_loan)
        
        # Call the service method
        loan = service.update_balloon_payment("loan123", 60)
        
        # Check that the methods were called
        service.calculate_balloon_payment.assert_called_once_with("loan123", 60)
        service.update_loan.assert_called_once()
        
        # Check the result
        assert loan is not None
        assert loan.balloon_payment is not None
        assert loan.balloon_payment.term_months == 60
    
    def test_validate_loan_data(self, service):
        """Test validating loan data."""
        # Valid loan data
        valid_data = {
            "property_id": "prop123",
            "loan_type": "initial",
            "amount": "200000",
            "interest_rate": "4.5%",
            "term_months": 360,
            "start_date": date.today().isoformat()
        }
        
        # This should not raise an exception
        service._validate_loan_data(valid_data)
        
        # Invalid loan data (missing required fields)
        invalid_data = {
            "property_id": "prop123",
            "loan_type": "initial",
            # Missing amount, interest_rate, term_months, start_date
        }
        
        # This should raise a ValueError
        with pytest.raises(ValueError):
            service._validate_loan_data(invalid_data)
        
        # Invalid loan type
        invalid_type_data = {
            "property_id": "prop123",
            "loan_type": "invalid_type",
            "amount": "200000",
            "interest_rate": "4.5%",
            "term_months": 360,
            "start_date": date.today().isoformat()
        }
        
        # This should raise a ValueError
        with pytest.raises(ValueError):
            service._validate_loan_data(invalid_type_data)
        
        # Invalid interest rate
        invalid_rate_data = {
            "property_id": "prop123",
            "loan_type": "initial",
            "amount": "200000",
            "interest_rate": "40%",  # Too high
            "term_months": 360,
            "start_date": date.today().isoformat()
        }
        
        # This should raise a ValueError
        with pytest.raises(ValueError):
            service._validate_loan_data(invalid_rate_data)
