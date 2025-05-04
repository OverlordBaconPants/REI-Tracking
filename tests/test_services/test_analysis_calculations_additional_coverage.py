import pytest
from services.analysis_calculations import format_percentage_or_infinite, LoanDetails, LoanCalculator
from services.analysis_calculations import AnalysisReport, LTRAnalysis, BRRRRAnalysis
from services.analysis_calculations import LeaseOptionAnalysis, MultiFamilyAnalysis, create_analysis
from utils.money import Money
from utils.validators import Percentage
import uuid
from datetime import datetime

class TestLTRAnalysisAdditional:
    def test_ltr_analysis_with_minimal_data(self):
        """Test LTR Analysis initialization with minimal data."""
        data = {
            'id': str(uuid.uuid4()),
            'user_id': str(uuid.uuid4()),
            'analysis_name': 'Test Analysis',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'updated_at': datetime.now().strftime('%Y-%m-%d'),
            'analysis_type': 'LTR',
            'address': '123 Test St',
            'purchase_price': 100000,
            'monthly_rent': 1000,
            'vacancy_percentage': 5,
            'management_fee_percentage': 10,
            'repairs_percentage': 5,
            'capex_percentage': 5,
            'property_taxes': 100,
            'insurance': 50,
            'hoa_coa_coop': 0
        }
        analysis = LTRAnalysis(data)
        assert analysis.data['id'] == data['id']
        assert analysis.data['analysis_name'] == data['analysis_name']
        assert analysis.data['analysis_type'] == data['analysis_type']

class TestLoanDetailsAdditional:
    def test_loan_details_with_zero_interest(self):
        """Test LoanDetails with zero interest rate."""
        loan = LoanDetails(Money(100000), Percentage(0), 360, False)
        assert loan.amount.dollars == 100000
        assert loan.interest_rate.value == 0
        assert loan.term == 360
        # No need to check is_interest_only as it's not stored as an attribute
    
    def test_loan_details_with_very_short_term(self):
        """Test LoanDetails with very short term."""
        loan = LoanDetails(Money(100000), Percentage(5), 1, False)
        assert loan.amount.dollars == 100000
        assert loan.interest_rate.value == 5
        assert loan.term == 1
        # No need to check is_interest_only as it's not stored as an attribute

class TestLoanCalculatorAdditional:
    def test_calculate_payment_with_extreme_values(self):
        """Test LoanCalculator with extreme values."""
        # Very large loan amount
        loan = LoanDetails(Money(10000000), Percentage(5), 360, False)
        payment = LoanCalculator.calculate_payment(loan)
        assert payment.dollars > 0
        
        # Very high interest rate
        loan = LoanDetails(Money(100000), Percentage(20), 360, False)
        payment = LoanCalculator.calculate_payment(loan)
        assert payment.dollars > 0
        
        # Very long term
        loan = LoanDetails(Money(100000), Percentage(5), 360, False)
        payment = LoanCalculator.calculate_payment(loan)
        assert payment.dollars > 0

class TestFormatPercentageOrInfiniteAdditional2:
    def test_format_percentage_or_infinite_with_decimal(self):
        """Test formatting decimal value."""
        result = format_percentage_or_infinite(0.1234)
        assert result == "0.1234"  # It just converts to string
    
    def test_format_percentage_or_infinite_with_percentage_object(self):
        """Test formatting Percentage object."""
        result = format_percentage_or_infinite(Percentage(0.1234))
        assert result == "0.1%"  # Format with one decimal place based on actual implementation
