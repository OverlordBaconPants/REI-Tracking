import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from decimal import Decimal

from src.models.loan import Loan, LoanType, LoanStatus, BalloonPayment
from src.services.property_financial_service import PropertyFinancialService
from src.utils.money import Money, Percentage

class TestLoanTracking:
    """Test suite for loan tracking functionality."""
    
    @pytest.fixture
    def mock_loan_service(self):
        """Create a mock loan service."""
        with patch('src.services.loan_service.LoanService') as mock:
            yield mock
    
    @pytest.fixture
    def property_financial_service(self, mock_loan_service):
        """Create a property financial service with mocked dependencies."""
        service = PropertyFinancialService()
        service.loan_repo = MagicMock()
        return service
    
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
            start_date=date.today() - timedelta(days=365),  # 1 year ago
            lender="Test Bank",
            loan_number="L12345"
        )
    
    @pytest.fixture
    def sample_secondary_loan(self):
        """Create a sample secondary loan for testing."""
        return Loan(
            id="loan456",
            property_id="prop123",
            loan_type=LoanType.SELLER_FINANCING,
            amount=Money(50000),
            interest_rate=Percentage(6.0),
            term_months=120,
            start_date=date.today() - timedelta(days=365),  # 1 year ago
            lender="Seller",
            loan_number="SF789"
        )
    
    def test_get_loan_details(self, property_financial_service, sample_loan, sample_secondary_loan):
        """Test getting loan details for a property."""
        # Directly patch the LoanService class
        with patch('src.services.property_financial_service.LoanService') as mock_loan_service:
            mock_instance = MagicMock()
            mock_instance.get_active_loans_by_property.return_value = [sample_loan, sample_secondary_loan]
            mock_instance.get_total_debt_for_property.return_value = Money(240000)
            mock_instance.get_total_monthly_payment_for_property.return_value = Money(1500)
            mock_loan_service.return_value = mock_instance
            
            # Call the method inside the context manager
            loan_details = property_financial_service._get_loan_details("prop123")
        
        # Verify the result
        assert loan_details["has_loans"] is True
        assert loan_details["total_debt"] == Money(240000)
        assert loan_details["monthly_payment"] == Money(1500)
        assert len(loan_details["loans"]) == 2
        
        # Verify loan details
        primary_loan = loan_details["loans"][0]
        assert primary_loan["id"] == "loan123"
        assert primary_loan["loan_type"] == "initial"
        assert primary_loan["amount"] == Money(200000)
        assert primary_loan["interest_rate"] == Percentage(4.5)
        assert primary_loan["term_months"] == 360
        assert primary_loan["is_interest_only"] is False
        assert primary_loan["lender"] == "Test Bank"
        assert primary_loan["loan_number"] == "L12345"
        assert "current_balance" in primary_loan
        assert "monthly_payment" in primary_loan
        assert "monthly_principal" in primary_loan
        assert "monthly_interest" in primary_loan
        assert "equity_from_principal" in primary_loan
        assert "monthly_equity_gain" in primary_loan
        
        # Verify secondary loan
        secondary_loan = loan_details["loans"][1]
        assert secondary_loan["id"] == "loan456"
        assert secondary_loan["loan_type"] == "seller_financing"
        assert secondary_loan["amount"] == Money(50000)
        assert secondary_loan["interest_rate"] == Percentage(6.0)
        assert secondary_loan["term_months"] == 120
        assert secondary_loan["lender"] == "Seller"
    
    def test_get_loan_details_no_loans(self, property_financial_service, mock_loan_service):
        """Test getting loan details when there are no loans."""
        # Set up mock loan service
        mock_loan_service_instance = mock_loan_service.return_value
        mock_loan_service_instance.get_active_loans_by_property.return_value = []
        
        # Call the method
        loan_details = property_financial_service._get_loan_details("prop123")
        
        # Verify the result
        assert loan_details["has_loans"] is False
        assert loan_details["total_debt"] == Decimal("0")
        assert loan_details["monthly_payment"] == Decimal("0")
        assert len(loan_details["loans"]) == 0
    
    def test_calculate_property_equity_with_loans(self, property_financial_service):
        """Test calculating property equity with loan details."""
        # Mock the _get_loan_details method
        property_financial_service._get_loan_details = MagicMock(return_value={
            "has_loans": True,
            "total_debt": Money(240000),
            "monthly_payment": Money(1500),
            "loans": [
                {
                    "id": "loan123",
                    "name": "Initial Loan",
                    "loan_type": "initial",
                    "amount": Money(200000),
                    "interest_rate": Percentage(4.5),
                    "term_months": 360,
                    "start_date": date.today() - timedelta(days=365),
                    "is_interest_only": False,
                    "lender": "Test Bank",
                    "loan_number": "L12345",
                    "current_balance": Money(195000),
                    "monthly_payment": Money(1013.37),
                    "monthly_principal": Money(263.37),
                    "monthly_interest": Money(750.00),
                    "equity_from_principal": Money(5000),
                    "monthly_equity_gain": Money(263.37)
                },
                {
                    "id": "loan456",
                    "name": "Seller Financing",
                    "loan_type": "seller_financing",
                    "amount": Money(50000),
                    "interest_rate": Percentage(6.0),
                    "term_months": 120,
                    "start_date": date.today() - timedelta(days=365),
                    "is_interest_only": False,
                    "lender": "Seller",
                    "loan_number": "SF789",
                    "current_balance": Money(45000),
                    "monthly_payment": Money(555.10),
                    "monthly_principal": Money(305.10),
                    "monthly_interest": Money(250.00),
                    "equity_from_principal": Money(5000),
                    "monthly_equity_gain": Money(305.10)
                }
            ]
        })
        
        # Mock the property_access_service and property_repo
        property_financial_service.property_access_service = MagicMock()
        property_financial_service.property_access_service.can_access_property.return_value = True
        
        property_financial_service.property_repo = MagicMock()
        property_financial_service.property_repo.get_by_id.return_value = MagicMock(
            id="prop123",
            address="123 Main St",
            purchase_price=Decimal("300000"),
            purchase_date="2024-04-27",
            partners=[
                MagicMock(name="user1", equity_share=Decimal("100"))
            ]
        )
        
        # Call the method
        equity_data = property_financial_service.calculate_property_equity("prop123", "user1")
        
        # Verify the result
        assert equity_data["property_id"] == "prop123"
        assert equity_data["address"] == "123 Main St"
        assert equity_data["purchase_price"] == "300000"
        assert equity_data["total_loan_balance"] == "240000.0"
        assert equity_data["initial_equity"] == "50000.0"  # 300000 - 250000
        assert "current_equity" in equity_data
        assert "equity_gain" in equity_data
        assert "equity_from_loan_paydown" in equity_data
        assert "equity_from_appreciation" in equity_data
        assert "monthly_equity_gain" in equity_data
        assert "monthly_equity_gain_from_loans" in equity_data
        assert equity_data["monthly_equity_gain_from_loans"] == "568.47"  # 263.37 + 305.10
        assert "loan_details" in equity_data
        assert "partner_equity" in equity_data
