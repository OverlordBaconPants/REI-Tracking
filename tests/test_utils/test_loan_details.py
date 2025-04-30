import pytest
from decimal import Decimal
from src.utils.money import Money, Percentage, MonthlyPayment
from src.utils.calculations.loan_details import LoanDetails

class TestLoanDetails:
    def test_initialization(self):
        """Test initialization of LoanDetails objects."""
        # Standard initialization
        loan = LoanDetails(
            amount="$200,000.00",
            interest_rate="4.500%",
            term_months=360,
            is_interest_only=False,
            name="Primary Mortgage"
        )
        
        assert loan.amount == "$200,000.00"
        assert loan.interest_rate == "4.500%"
        assert loan.term_months == 360
        assert loan.is_interest_only == False
        assert loan.name == "Primary Mortgage"
        
        # Initialize with raw values
        loan = LoanDetails(
            amount="$150,000.00",
            interest_rate="3.750%",
            term_months=180
        )
        
        assert loan.amount == "$150,000.00"
        assert loan.interest_rate == "3.750%"
        assert loan.term_months == 180
        assert loan.is_interest_only == False
        assert loan.name is None
    
    def test_validation(self):
        """Test validation of loan parameters."""
        # Valid loan
        LoanDetails(amount="$100,000.00", interest_rate="4.000%", term_months=360)
        
        # Invalid amount
        with pytest.raises(ValueError, match="Loan amount must be greater than 0"):
            LoanDetails(amount="$0.00", interest_rate="4.000%", term_months=360)
            
        with pytest.raises(ValueError, match="Loan amount must be greater than 0"):
            LoanDetails(amount="-$10,000.00", interest_rate="4.000%", term_months=360)
            
        # Invalid interest rate
        with pytest.raises(ValueError, match="Interest rate must be between 0% and 30.0%"):
            LoanDetails(amount="$100,000.00", interest_rate="-1.000%", term_months=360)
            
        with pytest.raises(ValueError, match="Interest rate must be between 0% and 30.0%"):
            LoanDetails(amount="$100,000.00", interest_rate="35.000%", term_months=360)
            
        # Invalid term
        with pytest.raises(ValueError, match="Loan term must be between 1 and 360 months"):
            LoanDetails(amount="$100,000.00", interest_rate="4.000%", term_months=0)
            
        with pytest.raises(ValueError, match="Loan term must be between 1 and 360 months"):
            LoanDetails(amount="$100,000.00", interest_rate="4.000%", term_months=400)
            
        # Invalid is_interest_only
        with pytest.raises(ValueError, match="is_interest_only must be a boolean value"):
            LoanDetails(amount="$100,000.00", interest_rate="4.000%", term_months=360, is_interest_only="yes")
    
    def test_calculate_payment_standard_loan(self):
        """Test payment calculation for standard amortizing loans."""
        # 30-year fixed at 4.5%
        loan = LoanDetails(
            amount="$200,000.00",
            interest_rate="4.500%",
            term_months=360
        )
        
        payment = loan.calculate_payment()
        assert isinstance(payment, MonthlyPayment)
        assert round(payment.total.dollars, 2) == 1013.37
        assert payment.principal.dollars > 0
        assert payment.interest.dollars > 0
        assert round(payment.principal.dollars + payment.interest.dollars, 2) == round(payment.total.dollars, 2)
        
        # 15-year fixed at 3.75%
        loan = LoanDetails(
            amount="$150,000.00",
            interest_rate="3.750%",
            term_months=180
        )
        
        payment = loan.calculate_payment()
        assert round(payment.total.dollars, 2) == 1090.83
    
    def test_calculate_payment_interest_only(self):
        """Test payment calculation for interest-only loans."""
        loan = LoanDetails(
            amount="$300,000.00",
            interest_rate="5.000%",
            term_months=120,
            is_interest_only=True
        )
        
        payment = loan.calculate_payment()
        assert isinstance(payment, MonthlyPayment)
        
        # Interest-only payment should be principal * rate / 12
        expected_interest = 300000 * 0.05 / 12
        assert round(payment.total.dollars, 2) == round(expected_interest, 2)
        assert payment.principal.dollars == 0
        assert round(payment.interest.dollars, 2) == round(expected_interest, 2)
    
    def test_calculate_payment_zero_interest(self):
        """Test payment calculation for zero-interest loans."""
        loan = LoanDetails(
            amount="$10,000.00",
            interest_rate="0.000%",
            term_months=24
        )
        
        payment = loan.calculate_payment()
        assert isinstance(payment, MonthlyPayment)
        
        # Zero-interest payment should be principal / term
        expected_payment = 10000 / 24
        assert round(payment.total.dollars, 2) == round(expected_payment, 2)
        assert round(payment.principal.dollars, 2) == round(expected_payment, 2)
        assert payment.interest.dollars == 0
    
    def test_calculate_remaining_balance(self):
        """Test calculation of remaining balance after payments."""
        loan = LoanDetails(
            amount="$200,000.00",
            interest_rate="4.500%",
            term_months=360
        )
        
        # Test initial balance
        assert loan.calculate_remaining_balance(0).dollars == 200000
        
        # Test after some payments
        balance_after_60 = loan.calculate_remaining_balance(60)
        assert balance_after_60.dollars < 200000
        assert round(balance_after_60.dollars, 2) == 54356.57
        
        # Test after term
        assert loan.calculate_remaining_balance(360).dollars == 0
        
        # Test after term (extra payments)
        assert loan.calculate_remaining_balance(400).dollars == 0
    
    def test_calculate_remaining_balance_interest_only(self):
        """Test remaining balance calculation for interest-only loans."""
        loan = LoanDetails(
            amount="$300,000.00",
            interest_rate="5.000%",
            term_months=120,
            is_interest_only=True
        )
        
        # For interest-only, balance doesn't change until final payment
        assert loan.calculate_remaining_balance(0).dollars == 300000
        assert loan.calculate_remaining_balance(60).dollars == 300000
        assert loan.calculate_remaining_balance(119).dollars == 300000
        assert loan.calculate_remaining_balance(120).dollars == 0
    
    def test_calculate_remaining_balance_zero_interest(self):
        """Test remaining balance calculation for zero-interest loans."""
        loan = LoanDetails(
            amount="$10,000.00",
            interest_rate="0.000%",
            term_months=24
        )
        
        # For zero-interest, balance decreases linearly
        assert loan.calculate_remaining_balance(0).dollars == 10000
        assert loan.calculate_remaining_balance(12).dollars == 5000
        assert loan.calculate_remaining_balance(24).dollars == 0
    
    def test_generate_amortization_schedule(self):
        """Test generation of amortization schedule."""
        loan = LoanDetails(
            amount="$100,000.00",
            interest_rate="6.000%",
            term_months=12
        )
        
        schedule = loan.generate_amortization_schedule()
        
        # Check schedule length
        assert len(schedule) == 12
        
        # Check first payment
        assert schedule[0]['period'] == 1
        assert round(schedule[0]['payment'].dollars, 2) == 8606.64
        assert round(schedule[0]['principal'].dollars, 2) == 8106.64
        assert round(schedule[0]['interest'].dollars, 2) == 500.00
        assert round(schedule[0]['remaining_balance'].dollars, 2) == 91893.36
        
        # Check last payment
        assert schedule[-1]['period'] == 12
        assert round(schedule[-1]['payment'].dollars, 2) == 8606.64
        assert round(schedule[-1]['principal'].dollars, 2) == 8563.82
        assert round(schedule[-1]['interest'].dollars, 2) == 42.82
        assert schedule[-1]['remaining_balance'].dollars == 0
        
        # Check partial schedule
        partial = loan.generate_amortization_schedule(max_periods=6)
        assert len(partial) == 6
        assert partial[0]['period'] == 1
        assert partial[-1]['period'] == 6
    
    def test_generate_amortization_schedule_interest_only(self):
        """Test amortization schedule for interest-only loans."""
        loan = LoanDetails(
            amount="$100,000.00",
            interest_rate="6.000%",
            term_months=12,
            is_interest_only=True
        )
        
        schedule = loan.generate_amortization_schedule()
        
        # Check schedule length
        assert len(schedule) == 12
        
        # Check first payment (interest only)
        assert schedule[0]['period'] == 1
        assert round(schedule[0]['payment'].dollars, 2) == 500.00
        assert schedule[0]['principal'].dollars == 0
        assert round(schedule[0]['interest'].dollars, 2) == 500.00
        assert schedule[0]['remaining_balance'].dollars == 100000
        
        # Check payments 2-11 (interest only)
        assert schedule[5]['period'] == 6
        assert round(schedule[5]['payment'].dollars, 2) == 500.00
        assert schedule[5]['principal'].dollars == 0
        assert round(schedule[5]['interest'].dollars, 2) == 500.00
        assert schedule[5]['remaining_balance'].dollars == 100000
        
        # Check last payment (includes principal)
        assert schedule[-1]['period'] == 12
        assert round(schedule[-1]['payment'].dollars, 2) == 100500.00
        assert round(schedule[-1]['principal'].dollars, 2) == 100000.00
        assert round(schedule[-1]['interest'].dollars, 2) == 500.00
        assert schedule[-1]['remaining_balance'].dollars == 0
    
    def test_generate_amortization_schedule_zero_interest(self):
        """Test amortization schedule for zero-interest loans."""
        loan = LoanDetails(
            amount="$12,000.00",
            interest_rate="0.000%",
            term_months=12
        )
        
        schedule = loan.generate_amortization_schedule()
        
        # Check schedule length
        assert len(schedule) == 12
        
        # Check first payment
        assert schedule[0]['period'] == 1
        assert round(schedule[0]['payment'].dollars, 2) == 1000.00
        assert round(schedule[0]['principal'].dollars, 2) == 1000.00
        assert schedule[0]['interest'].dollars == 0
        assert schedule[0]['remaining_balance'].dollars == 11000
        
        # Check last payment
        assert schedule[-1]['period'] == 12
        assert round(schedule[-1]['payment'].dollars, 2) == 1000.00
        assert round(schedule[-1]['principal'].dollars, 2) == 1000.00
        assert schedule[-1]['interest'].dollars == 0
        assert schedule[-1]['remaining_balance'].dollars == 0
