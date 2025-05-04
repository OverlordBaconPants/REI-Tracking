import pytest
import json
from decimal import Decimal
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from services.analysis_calculations import (
    format_percentage_or_infinite,
    LoanDetails,
    LoanCalculator,
    AnalysisReport,
    Analysis,
    LTRAnalysis,
    BRRRRAnalysis,
    LeaseOptionAnalysis,
    MultiFamilyAnalysis,
    create_analysis
)
from utils.money import Money, Percentage

@pytest.fixture
def sample_ltr_data():
    """Create sample data for LTR analysis."""
    today = datetime.now().strftime('%Y-%m-%d')
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "user_id": "user123",
        "created_at": today,
        "updated_at": today,
        "analysis_type": "LTR",
        "analysis_name": "Test LTR Analysis",
        "address": "123 Main St, Test City, TS 12345",
        "purchase_price": 200000,
        "monthly_rent": 1800,
        "property_taxes": 200,
        "insurance": 100,
        "hoa_coa_coop": 0,
        "management_fee_percentage": 8,
        "capex_percentage": 5,
        "vacancy_percentage": 5,
        "repairs_percentage": 5,
        "loan1_loan_amount": 160000,
        "loan1_loan_interest_rate": 4.5,
        "loan1_loan_term": 360,
        "loan1_interest_only": False,
        "loan1_loan_down_payment": 40000,
        "loan1_loan_closing_costs": 3000
    }

@pytest.fixture
def sample_brrrr_data():
    """Create sample data for BRRRR analysis."""
    today = datetime.now().strftime('%Y-%m-%d')
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "user_id": "user123",
        "created_at": today,
        "updated_at": today,
        "analysis_type": "BRRRR",
        "analysis_name": "Test BRRRR Analysis",
        "address": "123 Main St, Test City, TS 12345",
        "purchase_price": 150000,
        "after_repair_value": 250000,
        "renovation_costs": 50000,
        "renovation_duration": 3,
        "monthly_rent": 2000,
        "property_taxes": 200,
        "insurance": 100,
        "hoa_coa_coop": 0,
        "management_fee_percentage": 8,
        "capex_percentage": 5,
        "vacancy_percentage": 5,
        "repairs_percentage": 5,
        "initial_loan_amount": 120000,
        "initial_loan_interest_rate": 6.0,
        "initial_loan_term": 12,
        "initial_interest_only": True,
        "initial_loan_closing_costs": 2000,
        "refinance_loan_amount": 200000,
        "refinance_loan_interest_rate": 4.5,
        "refinance_loan_term": 360,
        "refinance_loan_closing_costs": 3000
    }

@pytest.fixture
def sample_lease_option_data():
    """Create sample data for Lease Option analysis."""
    today = datetime.now().strftime('%Y-%m-%d')
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "user_id": "user123",
        "created_at": today,
        "updated_at": today,
        "analysis_type": "Lease Option",
        "analysis_name": "Test Lease Option Analysis",
        "address": "123 Main St, Test City, TS 12345",
        "purchase_price": 200000,
        "monthly_rent": 1800,
        "property_taxes": 200,
        "insurance": 100,
        "hoa_coa_coop": 0,
        "management_fee_percentage": 8,
        "capex_percentage": 5,
        "vacancy_percentage": 5,
        "repairs_percentage": 5,
        "option_consideration_fee": 5000,
        "option_term_months": 24,
        "strike_price": 220000,
        "monthly_rent_credit_percentage": 25,
        "rent_credit_cap": 10000
    }

@pytest.fixture
def sample_multi_family_data():
    """Create sample data for Multi-Family analysis."""
    today = datetime.now().strftime('%Y-%m-%d')
    unit_types = [
        {
            "type": "1BR",
            "count": 4,
            "occupied": 3,
            "square_footage": 700,
            "rent": 1000
        },
        {
            "type": "2BR",
            "count": 6,
            "occupied": 5,
            "square_footage": 900,
            "rent": 1300
        }
    ]
    
    return {
        "id": "12345678-1234-5678-1234-567812345678",
        "user_id": "user123",
        "created_at": today,
        "updated_at": today,
        "analysis_type": "Multi-Family",
        "analysis_name": "Test Multi-Family Analysis",
        "address": "123 Main St, Test City, TS 12345",
        "purchase_price": 1200000,
        "property_taxes": 1000,
        "insurance": 500,
        "hoa_coa_coop": 0,
        "management_fee_percentage": 8,
        "capex_percentage": 5,
        "vacancy_percentage": 5,
        "repairs_percentage": 5,
        "total_units": 10,
        "occupied_units": 8,
        "floors": 2,
        "elevator_maintenance": 200,
        "common_area_maintenance": 300,
        "staff_payroll": 1000,
        "trash_removal": 150,
        "common_utilities": 400,
        "other_income": 500,
        "unit_types": json.dumps(unit_types),
        "loan1_loan_amount": 960000,
        "loan1_loan_interest_rate": 4.5,
        "loan1_loan_term": 360,
        "loan1_interest_only": False
    }

class TestFormatPercentageOrInfinite:
    """Test the format_percentage_or_infinite function."""
    
    def test_format_infinite(self):
        """Test formatting 'Infinite' string."""
        result = format_percentage_or_infinite("Infinite")
        assert result == "Infinite"
    
    def test_format_percentage(self):
        """Test formatting Percentage object."""
        result = format_percentage_or_infinite(Percentage(10.5))
        assert result == "10.5%"
    
    def test_format_other_type(self):
        """Test formatting other types."""
        result = format_percentage_or_infinite(15)
        assert result == "15"

class TestLoanDetails:
    """Test the LoanDetails class."""
    
    def test_valid_loan_details(self):
        """Test creating valid loan details."""
        loan = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term=360
        )
        
        assert loan.amount.dollars == 200000
        assert loan.interest_rate.value == 4.5
        assert loan.term == 360
        assert loan.is_interest_only is False
    
    def test_interest_only_loan(self):
        """Test creating interest-only loan."""
        loan = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=True
        )
        
        assert loan.is_interest_only is True
    
    def test_invalid_loan_amount(self):
        """Test validation of negative loan amount."""
        with pytest.raises(ValueError):
            LoanDetails(
                amount=Money(-100000),
                interest_rate=Percentage(4.5),
                term=360
            )
    
    def test_invalid_interest_rate(self):
        """Test validation of invalid interest rate."""
        with pytest.raises(ValueError):
            LoanDetails(
                amount=Money(200000),
                interest_rate=Percentage(-1.5),
                term=360
            )
        
        with pytest.raises(ValueError):
            LoanDetails(
                amount=Money(200000),
                interest_rate=Percentage(35),  # Above MAX_LOAN_INTEREST_RATE
                term=360
            )
    
    def test_invalid_term(self):
        """Test validation of invalid loan term."""
        with pytest.raises(ValueError):
            LoanDetails(
                amount=Money(200000),
                interest_rate=Percentage(4.5),
                term=0
            )
        
        with pytest.raises(ValueError):
            LoanDetails(
                amount=Money(200000),
                interest_rate=Percentage(4.5),
                term=400  # Above MAX_LOAN_TERM
            )

class TestLoanCalculator:
    """Test the LoanCalculator class."""
    
    def test_calculate_payment_amortizing(self):
        """Test calculating payment for amortizing loan."""
        loan = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False
        )
        
        payment = LoanCalculator.calculate_payment(loan)
        assert isinstance(payment, Money)
        assert payment.dollars > 0
        # Expected payment for $200k at 4.5% for 30 years is around $1013
        assert 1000 < payment.dollars < 1050
    
    def test_calculate_payment_interest_only(self):
        """Test calculating payment for interest-only loan."""
        loan = LoanDetails(
            amount=Money(200000),
            interest_rate=Percentage(6.0),
            term=12,
            is_interest_only=True
        )
        
        payment = LoanCalculator.calculate_payment(loan)
        assert isinstance(payment, Money)
        # Expected payment is interest only: $200,000 * 6% / 12 = $1000
        assert abs(payment.dollars - 1000) < 1  # Allow for small rounding differences
    
    def test_calculate_payment_zero_amount(self):
        """Test calculating payment for zero loan amount."""
        # Use a mock instead of creating a real LoanDetails object
        # This avoids the validation in LoanDetails.__post_init__
        loan = MagicMock()
        loan.amount = Money(0)
        loan.interest_rate = Percentage(4.5)
        loan.term = 360
        loan.is_interest_only = False
        
        payment = LoanCalculator.calculate_payment(loan)
        assert payment.dollars == 0
    
    def test_calculate_payment_zero_term(self):
        """Test calculating payment for zero term."""
        # This should be caught by LoanDetails validation, but test the calculator's handling
        loan = MagicMock()
        loan.amount = Money(200000)
        loan.interest_rate = Percentage(4.5)
        loan.term = 0
        loan.is_interest_only = False
        
        payment = LoanCalculator.calculate_payment(loan)
        assert payment.dollars == 0

class TestAnalysisReport:
    """Test the AnalysisReport class."""
    
    def test_to_dict(self, sample_ltr_data):
        """Test converting report to dictionary."""
        # Create a mock Analysis
        mock_analysis = MagicMock()
        mock_analysis.data = sample_ltr_data
        mock_analysis.get_report_data.return_value = {"metrics": {"cash_flow": "$500"}}
        
        # Create report from analysis
        report = AnalysisReport.from_analysis(mock_analysis)
        
        # Convert to dict
        result = report.to_dict()
        
        # Verify result
        assert result["id"] == sample_ltr_data["id"]
        assert result["user_id"] == sample_ltr_data["user_id"]
        assert result["analysis_name"] == sample_ltr_data["analysis_name"]
        assert result["analysis_type"] == sample_ltr_data["analysis_type"]
        assert result["purchase_price"] == sample_ltr_data["purchase_price"]
        assert result["metrics"] == {"cash_flow": "$500"}
    
    def test_from_analysis(self, sample_ltr_data):
        """Test creating report from analysis."""
        # Create a mock Analysis
        mock_analysis = MagicMock()
        mock_analysis.data = sample_ltr_data
        mock_analysis.get_report_data.return_value = {"metrics": {"cash_flow": "$500"}}
        
        # Create report from analysis
        report = AnalysisReport.from_analysis(mock_analysis)
        
        # Verify report
        assert report.id == sample_ltr_data["id"]
        assert report.user_id == sample_ltr_data["user_id"]
        assert report.analysis_name == sample_ltr_data["analysis_name"]
        assert report.analysis_type == sample_ltr_data["analysis_type"]
        assert report.purchase_price == sample_ltr_data["purchase_price"]
        assert report.metrics == {"cash_flow": "$500"}
    
    def test_get_type_specific_data_brrrr(self):
        """Test getting BRRRR-specific data."""
        report = AnalysisReport(
            id="test-id",
            user_id="user123",
            analysis_name="Test BRRRR",
            analysis_type="BRRRR",
            address="123 Main St",
            generated_date=datetime.now().isoformat(),
            square_footage=1500,
            lot_size=5000,
            year_built=2000,
            purchase_price=150000,
            after_repair_value=250000,
            renovation_costs=50000,
            renovation_duration=3,
            monthly_rent=2000,
            property_taxes=200,
            insurance=100,
            hoa_coa_coop=0,
            management_fee_percentage=8,
            capex_percentage=5,
            vacancy_percentage=5,
            repairs_percentage=5,
            metrics={
                "equity_captured": "$50000",
                "cash_recouped": "$30000",
                "total_project_costs": "$200000",
                "holding_costs": "$5000"
            }
        )
        
        result = report.get_type_specific_data()
        assert "equity_captured" in result
        assert "cash_recouped" in result
        assert "total_project_costs" in result
        assert "holding_costs" in result
    
    def test_get_type_specific_data_padsplit(self):
        """Test getting PadSplit-specific data."""
        report = AnalysisReport(
            id="test-id",
            user_id="user123",
            analysis_name="Test PadSplit",
            analysis_type="PadSplit LTR",
            address="123 Main St",
            generated_date=datetime.now().isoformat(),
            square_footage=1500,
            lot_size=5000,
            year_built=2000,
            purchase_price=200000,
            after_repair_value=0,
            renovation_costs=0,
            renovation_duration=0,
            monthly_rent=2500,
            property_taxes=200,
            insurance=100,
            hoa_coa_coop=0,
            management_fee_percentage=8,
            capex_percentage=5,
            vacancy_percentage=5,
            repairs_percentage=5,
            metrics={
                "utilities": "$200",
                "internet": "$100",
                "cleaning": "$150",
                "pest_control": "$50",
                "landscaping": "$100",
                "platform_fee": "$125"
            }
        )
        
        result = report.get_type_specific_data()
        assert "utilities" in result
        assert "internet" in result
        assert "cleaning" in result
        assert "pest_control" in result
        assert "landscaping" in result
        assert "platform_fee" in result
    
    def test_get_type_specific_data_other(self):
        """Test getting data for other analysis types."""
        report = AnalysisReport(
            id="test-id",
            user_id="user123",
            analysis_name="Test LTR",
            analysis_type="LTR",
            address="123 Main St",
            generated_date=datetime.now().isoformat(),
            square_footage=1500,
            lot_size=5000,
            year_built=2000,
            purchase_price=200000,
            after_repair_value=0,
            renovation_costs=0,
            renovation_duration=0,
            monthly_rent=1800,
            property_taxes=200,
            insurance=100,
            hoa_coa_coop=0,
            management_fee_percentage=8,
            capex_percentage=5,
            vacancy_percentage=5,
            repairs_percentage=5,
            metrics={}
        )
        
        result = report.get_type_specific_data()
        assert result == {}

class TestLTRAnalysis:
    """Test the LTRAnalysis class."""
    
    def test_initialization(self, sample_ltr_data):
        """Test initializing LTR analysis."""
        analysis = LTRAnalysis(sample_ltr_data)
        assert analysis.data == sample_ltr_data
    
    def test_invalid_analysis_type(self, sample_ltr_data):
        """Test initializing with invalid analysis type."""
        invalid_data = sample_ltr_data.copy()
        invalid_data["analysis_type"] = "Invalid"
        
        with pytest.raises(ValueError):
            LTRAnalysis(invalid_data)
    
    def test_calculate_monthly_cash_flow(self, sample_ltr_data):
        """Test calculating monthly cash flow."""
        analysis = LTRAnalysis(sample_ltr_data)
        
        # Mock the operating expenses and loan payments methods
        with patch.object(LTRAnalysis, '_calculate_operating_expenses') as mock_expenses, \
             patch.object(LTRAnalysis, '_calculate_loan_payments') as mock_payments:
            
            mock_expenses.return_value = Money(500)
            mock_payments.return_value = Money(800)
            
            # Calculate cash flow
            result = analysis.calculate_monthly_cash_flow()
            
            # Verify result
            # Monthly rent (1800) - expenses (500) - payments (800) = 500
            assert result.dollars == 500
    
    def test_calculate_total_cash_invested(self, sample_ltr_data):
        """Test calculating total cash invested."""
        analysis = LTRAnalysis(sample_ltr_data)
        
        result = analysis.calculate_total_cash_invested()
        
        # Down payment (40000) + closing costs (3000) = 43000
        assert result.dollars == 43000
    
    def test_cash_on_cash_return(self, sample_ltr_data):
        """Test calculating cash on cash return."""
        analysis = LTRAnalysis(sample_ltr_data)
        
        # Mock the cash flow and cash invested methods
        with patch.object(LTRAnalysis, 'calculate_monthly_cash_flow') as mock_cash_flow, \
             patch.object(LTRAnalysis, 'calculate_total_cash_invested') as mock_cash_invested:
            
            mock_cash_flow.return_value = Money(500)  # $500/month
            mock_cash_invested.return_value = Money(50000)  # $50,000 invested
            
            # Calculate cash on cash return
            result = analysis.cash_on_cash_return
            
            # Annual cash flow (500 * 12 = 6000) / cash invested (50000) = 12%
            assert isinstance(result, Percentage)
            assert result.value == 12.0
    
    def test_get_report_data(self, sample_ltr_data):
        """Test getting report data."""
        analysis = LTRAnalysis(sample_ltr_data)
        
        # Mock the core metrics calculation
        with patch.object(LTRAnalysis, '_calculate_core_metrics') as mock_core_metrics, \
             patch.object(LTRAnalysis, '_calculate_type_specific_metrics') as mock_type_metrics:
            
            mock_core_metrics.return_value = {
                "monthly_cash_flow": "$500",
                "annual_cash_flow": "$6000",
                "total_cash_invested": "$43000",
                "cash_on_cash_return": "12.0%",
                "roi": "12.0%"
            }
            
            mock_type_metrics.return_value = {
                "noi": "$1000",
                "cap_rate": "6.0%",
                "dscr": "1.5"
            }
            
            # Get report data
            result = analysis.get_report_data()
            
            # Verify result
            assert "metrics" in result
            assert result["metrics"]["monthly_cash_flow"] == "$500"
            assert result["metrics"]["annual_cash_flow"] == "$6000"
            assert result["metrics"]["noi"] == "$1000"
            assert result["metrics"]["cap_rate"] == "6.0%"
            assert result["metrics"]["dscr"] == "1.5"

class TestBRRRRAnalysis:
    """Test the BRRRRAnalysis class."""
    
    def test_initialization(self, sample_brrrr_data):
        """Test initializing BRRRR analysis."""
        analysis = BRRRRAnalysis(sample_brrrr_data)
        assert analysis.data == sample_brrrr_data
    
    def test_invalid_analysis_type(self, sample_brrrr_data):
        """Test initializing with invalid analysis type."""
        invalid_data = sample_brrrr_data.copy()
        invalid_data["analysis_type"] = "Invalid"
        
        with pytest.raises(ValueError):
            BRRRRAnalysis(invalid_data)
    
    def test_holding_costs(self, sample_brrrr_data):
        """Test calculating holding costs."""
        analysis = BRRRRAnalysis(sample_brrrr_data)
        
        # Calculate holding costs
        result = analysis.holding_costs
        
        # Verify result
        assert isinstance(result, Money)
        assert result.dollars > 0
        
        # Expected holding costs:
        # Monthly fixed expenses (property_taxes + insurance + hoa) = 300
        # Monthly interest on initial loan (120000 * 6% / 12) = 600
        # Total monthly holding costs = 900
        # Total holding costs over 3 months = 2700
        assert abs(result.dollars - 2700) < 10  # Allow for small rounding differences
    
    def test_total_project_costs(self, sample_brrrr_data):
        """Test calculating total project costs."""
        analysis = BRRRRAnalysis(sample_brrrr_data)
        
        # Mock the holding costs property
        with patch.object(BRRRRAnalysis, 'holding_costs', Money(2700)):
            # Calculate total project costs
            result = analysis.total_project_costs
            
            # Verify result
            # Purchase price (150000) + renovation costs (50000) + holding costs (2700) +
            # initial loan closing costs (2000) + refinance loan closing costs (3000) = 207700
            assert result.dollars == 207700
    
    def test_calculate_total_cash_invested(self, sample_brrrr_data):
        """Test calculating total cash invested for BRRRR."""
        analysis = BRRRRAnalysis(sample_brrrr_data)
        
        # Mock the holding costs property
        with patch.object(BRRRRAnalysis, 'holding_costs', Money(2700)):
            # Calculate total cash invested
            result = analysis.calculate_total_cash_invested()
            
            # Verify result
            # Initial investment = purchase price (150000) + renovation costs (50000) + 
            #                     holding costs (2700) + initial loan closing costs (2000) = 204700
            # Initial loan amount = 120000
            # Initial out of pocket = 204700 - 120000 = 84700
            # Cash recouped = refinance loan (200000) - initial loan (120000) - refinance closing costs (3000) = 77000
            # Final investment = 84700 - 77000 = 7700
            assert abs(result.dollars - 7700) < 10  # Allow for small rounding differences
    
    def test_cash_on_cash_return_positive_investment(self, sample_brrrr_data):
        """Test calculating cash on cash return with positive investment."""
        analysis = BRRRRAnalysis(sample_brrrr_data)
        
        # Mock the cash flow and cash invested methods
        with patch.object(BRRRRAnalysis, 'calculate_monthly_cash_flow') as mock_cash_flow, \
             patch.object(BRRRRAnalysis, 'calculate_total_cash_invested') as mock_cash_invested:
            
            mock_cash_flow.return_value = Money(500)  # $500/month
            mock_cash_invested.return_value = Money(10000)  # $10,000 invested
            
            # Calculate cash on cash return
            result = analysis.cash_on_cash_return
            
            # Annual cash flow (500 * 12 = 6000) / cash invested (10000) = 60%
            assert isinstance(result, Percentage)
            assert result.value == 60.0
    
    def test_cash_on_cash_return_zero_investment(self, sample_brrrr_data):
        """Test calculating cash on cash return with zero investment."""
        analysis = BRRRRAnalysis(sample_brrrr_data)
        
        # Mock the cash flow and cash invested methods
        with patch.object(BRRRRAnalysis, 'calculate_monthly_cash_flow') as mock_cash_flow, \
             patch.object(BRRRRAnalysis, 'calculate_total_cash_invested') as mock_cash_invested:
            
            mock_cash_flow.return_value = Money(500)  # $500/month
            mock_cash_invested.return_value = Money(0)  # $0 invested
            
            # Calculate cash on cash return
            result = analysis.cash_on_cash_return
            
            # Should return "Infinite" for zero investment
            assert result == "Infinite"
    
    def test_cash_on_cash_return_negative_investment(self, sample_brrrr_data):
        """Test calculating cash on cash return with negative investment."""
        analysis = BRRRRAnalysis(sample_brrrr_data)
        
        # Mock the cash flow and cash invested methods
        with patch.object(BRRRRAnalysis, 'calculate_monthly_cash_flow') as mock_cash_flow, \
             patch.object(BRRRRAnalysis, 'calculate_total_cash_invested') as mock_cash_invested:
            
            mock_cash_flow.return_value = Money(500)  # $500/month
            mock_cash_invested.return_value = Money(-5000)  # -$5,000 invested (cash out)
            
            # Calculate cash on cash return
            result = analysis.cash_on_cash_return
            
            # Should return "Infinite" for negative investment
            assert result == "Infinite"

class TestLeaseOptionAnalysis:
    """Test the LeaseOptionAnalysis class."""
    
    def test_initialization(self, sample_lease_option_data):
        """Test initializing Lease Option analysis."""
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        assert analysis.data == sample_lease_option_data
    
    def test_invalid_analysis_type(self, sample_lease_option_data):
        """Test initializing with invalid analysis type."""
        invalid_data = sample_lease_option_data.copy()
        invalid_data["analysis_type"] = "Invalid"
        
        with pytest.raises(ValueError):
            LeaseOptionAnalysis(invalid_data)
    
    def test_validate_type_specific_requirements(self, sample_lease_option_data):
        """Test validating lease option specific requirements."""
        # Valid data should not raise an exception
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        
        # Test with invalid strike price (must be greater than purchase price)
        invalid_data = sample_lease_option_data.copy()
        invalid_data["strike_price"] = 180000  # Less than purchase price (200000)
        
        with pytest.raises(ValueError):
            LeaseOptionAnalysis(invalid_data)
        
        # Test with invalid option fee
        invalid_data = sample_lease_option_data.copy()
        invalid_data["option_consideration_fee"] = 0
        
        with pytest.raises(ValueError):
            LeaseOptionAnalysis(invalid_data)
        
        # Test with invalid rent credit percentage
        invalid_data = sample_lease_option_data.copy()
        invalid_data["monthly_rent_credit_percentage"] = 101  # Over 100%
        
        with pytest.raises(ValueError):
            LeaseOptionAnalysis(invalid_data)
        
        # Test with invalid option term
        invalid_data = sample_lease_option_data.copy()
        invalid_data["option_term_months"] = 0
        
        with pytest.raises(ValueError):
            LeaseOptionAnalysis(invalid_data)
    
    def test_total_rent_credits(self, sample_lease_option_data):
        """Test calculating total rent credits."""
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        
        # Expected calculation:
        # Monthly rent: 1800
        # Monthly rent credit percentage: 25%
        # Monthly credit: 1800 * 0.25 = 450
        # Option term: 24 months
        # Total potential credits: 450 * 24 = 10800
        # Rent credit cap: 10000
        # Expected result: 10000 (capped)
        
        result = analysis.total_rent_credits
        assert isinstance(result, Money)
        assert result.dollars == 10000  # Capped at rent_credit_cap
        
        # Test with higher rent credit cap
        modified_data = sample_lease_option_data.copy()
        modified_data["rent_credit_cap"] = 15000
        
        analysis = LeaseOptionAnalysis(modified_data)
        result = analysis.total_rent_credits
        assert result.dollars == 10800  # Not capped, full potential credits
    
    def test_effective_purchase_price(self, sample_lease_option_data):
        """Test calculating effective purchase price."""
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        
        # Expected calculation:
        # Strike price: 220000
        # Total rent credits: 10000
        # Effective purchase price: 220000 - 10000 = 210000
        
        result = analysis.effective_purchase_price
        assert isinstance(result, Money)
        assert result.dollars == 210000
    
    def test_option_roi(self, sample_lease_option_data):
        """Test calculating option ROI."""
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        
        # Mock the annual cash flow
        with patch.object(LeaseOptionAnalysis, 'annual_cash_flow', Money(6000)):
            # Expected calculation:
            # Annual cash flow: 6000
            # Option fee: 5000
            # Option ROI: (6000 / 5000) * 100 = 120%
            
            result = analysis.option_roi
            assert isinstance(result, Percentage)
            assert result.value == 120.0
    
    def test_calculate_breakeven_months(self, sample_lease_option_data):
        """Test calculating breakeven months."""
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        
        # Mock the monthly cash flow
        with patch.object(LeaseOptionAnalysis, 'calculate_monthly_cash_flow', return_value=Money(500)):
            # Expected calculation:
            # Option fee: 5000
            # Monthly cash flow: 500
            # Breakeven months: 5000 / 500 = 10 months
            
            result = analysis.calculate_breakeven_months()
            assert result == 10
        
        # Test with zero monthly cash flow
        with patch.object(LeaseOptionAnalysis, 'calculate_monthly_cash_flow', return_value=Money(0)):
            result = analysis.calculate_breakeven_months()
            assert result == float('inf')
    
    def test_calculate_total_cash_invested(self, sample_lease_option_data):
        """Test calculating total cash invested for Lease Option."""
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        
        # For Lease Option, the main investment is the option fee
        result = analysis.calculate_total_cash_invested()
        assert isinstance(result, Money)
        assert result.dollars == 5000  # Option consideration fee
    
    def test_calculate_type_specific_metrics(self, sample_lease_option_data):
        """Test calculating Lease Option specific metrics."""
        analysis = LeaseOptionAnalysis(sample_lease_option_data)
        
        # Mock required methods
        with patch.object(LeaseOptionAnalysis, 'total_rent_credits', Money(10000)), \
             patch.object(LeaseOptionAnalysis, 'effective_purchase_price', Money(210000)), \
             patch.object(LeaseOptionAnalysis, 'option_roi', Percentage(120.0)), \
             patch.object(LeaseOptionAnalysis, 'calculate_breakeven_months', return_value=10), \
             patch.object(LeaseOptionAnalysis, '_calculate_operating_expenses', return_value=Money(500)), \
             patch.object(LeaseOptionAnalysis, '_calculate_loan_payments', return_value=Money(800)):
            
            # Calculate type-specific metrics
            metrics = analysis._calculate_type_specific_metrics()
            
            # Verify metrics
            assert 'total_rent_credits' in metrics
            assert 'effective_purchase_price' in metrics
            assert 'option_roi' in metrics
            assert 'breakeven_months' in metrics
            assert 'noi' in metrics
            assert 'monthly_noi' in metrics
            assert 'annual_noi' in metrics
            assert 'operating_expense_ratio' in metrics
            assert 'expense_ratio' in metrics
            assert 'monthly_cash_flow' in metrics
            assert 'annual_cash_flow' in metrics
            
            # Check specific values
            assert metrics['total_rent_credits'] == str(Money(10000))
            assert metrics['effective_purchase_price'] == str(Money(210000))
            assert metrics['option_roi'] == str(Percentage(120.0))
            assert metrics['breakeven_months'] == '10'

class TestMultiFamilyAnalysis:
    """Test the MultiFamilyAnalysis class."""
    
    def test_initialization(self, sample_multi_family_data):
        """Test initializing Multi-Family analysis."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        assert analysis.data == sample_multi_family_data
    
    def test_invalid_analysis_type(self, sample_multi_family_data):
        """Test initializing with invalid analysis type."""
        invalid_data = sample_multi_family_data.copy()
        invalid_data["analysis_type"] = "Invalid"
        
        with pytest.raises(ValueError):
            MultiFamilyAnalysis(invalid_data)
    
    def test_validate_type_specific_requirements(self, sample_multi_family_data):
        """Test validating multi-family specific requirements."""
        # Valid data should not raise an exception
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Test with invalid total units
        invalid_data = sample_multi_family_data.copy()
        invalid_data["total_units"] = 0
        
        with pytest.raises(ValueError):
            MultiFamilyAnalysis(invalid_data)
        
        # Test with invalid unit types (empty array)
        invalid_data = sample_multi_family_data.copy()
        invalid_data["unit_types"] = "[]"
        
        with pytest.raises(ValueError):
            MultiFamilyAnalysis(invalid_data)
        
        # Test with mismatched total units
        invalid_data = sample_multi_family_data.copy()
        unit_types = json.loads(invalid_data["unit_types"])
        unit_types[0]["count"] = 3  # Change from 4 to 3, making total 9 instead of 10
        invalid_data["unit_types"] = json.dumps(unit_types)
        
        with pytest.raises(ValueError):
            MultiFamilyAnalysis(invalid_data)
        
        # Test with invalid occupied units
        invalid_data = sample_multi_family_data.copy()
        unit_types = json.loads(invalid_data["unit_types"])
        unit_types[0]["occupied"] = 5  # More than count (4)
        invalid_data["unit_types"] = json.dumps(unit_types)
        
        with pytest.raises(ValueError):
            MultiFamilyAnalysis(invalid_data)
    
    def test_gross_potential_rent(self, sample_multi_family_data):
        """Test calculating gross potential rent."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Expected calculation:
        # Unit type 1: 4 units at $1000 = $4000
        # Unit type 2: 6 units at $1300 = $7800
        # Total: $11800
        
        result = analysis.gross_potential_rent
        assert isinstance(result, Money)
        assert result.dollars == 11800
    
    def test_actual_gross_income(self, sample_multi_family_data):
        """Test calculating actual gross income."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Expected calculation:
        # Unit type 1: 3 occupied units at $1000 = $3000
        # Unit type 2: 5 occupied units at $1300 = $6500
        # Other income: $500
        # Total: $10000
        
        result = analysis.actual_gross_income
        assert isinstance(result, Money)
        assert result.dollars == 10000
    
    def test_net_operating_income(self, sample_multi_family_data):
        """Test calculating net operating income."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Mock the operating expenses method
        with patch.object(MultiFamilyAnalysis, '_calculate_operating_expenses', return_value=Money(3000)):
            # Expected calculation:
            # Gross potential rent: $11800
            # Vacancy loss (5%): $590
            # Other income: $500
            # Effective gross income: $11800 - $590 + $500 = $11710
            # Operating expenses: $3000
            # NOI: $11710 - $3000 = $8710
            
            result = analysis.net_operating_income
            assert isinstance(result, Money)
            assert abs(result.dollars - 8710) < 10  # Allow for small rounding differences
    
    def test_cap_rate(self, sample_multi_family_data):
        """Test calculating cap rate."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Mock the net operating income property
        with patch.object(MultiFamilyAnalysis, 'net_operating_income', Money(8710)):
            # Expected calculation:
            # Annual NOI: $8710 * 12 = $104520
            # Purchase price: $1200000
            # Cap rate: ($104520 / $1200000) * 100 = 8.71%
            
            result = analysis.cap_rate
            assert isinstance(result, Percentage)
            assert abs(result.value - 8.71) < 0.1  # Allow for small rounding differences
    
    def test_occupancy_rate(self, sample_multi_family_data):
        """Test calculating occupancy rate."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Expected calculation:
        # Occupied units: 8
        # Total units: 10
        # Occupancy rate: (8 / 10) * 100 = 80%
        
        result = analysis.occupancy_rate
        assert isinstance(result, Percentage)
        assert result.value == 80.0
    
    def test_price_per_unit(self, sample_multi_family_data):
        """Test calculating price per unit."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Expected calculation:
        # Purchase price: $1200000
        # Total units: 10
        # Price per unit: $1200000 / 10 = $120000
        
        result = analysis.price_per_unit
        assert isinstance(result, Money)
        assert result.dollars == 120000
    
    def test_gross_rent_multiplier(self, sample_multi_family_data):
        """Test calculating gross rent multiplier."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Mock the gross potential rent property
        with patch.object(MultiFamilyAnalysis, 'gross_potential_rent', Money(11800)):
            # Expected calculation:
            # Annual gross rent: $11800 * 12 = $141600
            # Purchase price: $1200000
            # GRM: $1200000 / $141600 = 8.47
            
            result = analysis.gross_rent_multiplier
            assert abs(result - 8.47) < 0.1  # Allow for small rounding differences
    
    def test_calculate_operating_expenses(self, sample_multi_family_data):
        """Test calculating operating expenses for multi-family."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Mock the gross potential rent property
        with patch.object(MultiFamilyAnalysis, 'gross_potential_rent', Money(11800)):
            # Expected calculation:
            # Fixed expenses:
            #   Property taxes: $1000
            #   Insurance: $500
            #   HOA/COA: $0
            # Multi-family specific expenses:
            #   Common area maintenance: $300
            #   Elevator maintenance: $200
            #   Staff payroll: $1000
            #   Trash removal: $150
            #   Common utilities: $400
            # Percentage-based expenses:
            #   Management fee (8%): $11800 * 0.08 = $944
            #   CapEx (5%): $11800 * 0.05 = $590
            #   Vacancy (5%): $11800 * 0.05 = $590
            #   Repairs (5%): $11800 * 0.05 = $590
            # Total: $6264
            
            result = analysis._calculate_operating_expenses()
            assert isinstance(result, Money)
            assert abs(result.dollars - 6264) < 10  # Allow for small rounding differences
    
    def test_calculate_type_specific_metrics(self, sample_multi_family_data):
        """Test calculating Multi-Family specific metrics."""
        analysis = MultiFamilyAnalysis(sample_multi_family_data)
        
        # Mock required methods and properties
        with patch.object(MultiFamilyAnalysis, 'gross_potential_rent', Money(11800)), \
             patch.object(MultiFamilyAnalysis, 'actual_gross_income', Money(10000)), \
             patch.object(MultiFamilyAnalysis, 'net_operating_income', Money(8710)), \
             patch.object(MultiFamilyAnalysis, 'cap_rate', Percentage(8.71)), \
             patch.object(MultiFamilyAnalysis, 'occupancy_rate', Percentage(80.0)), \
             patch.object(MultiFamilyAnalysis, 'price_per_unit', Money(120000)), \
             patch.object(MultiFamilyAnalysis, 'gross_rent_multiplier', 8.47), \
             patch.object(MultiFamilyAnalysis, '_calculate_loan_payments', return_value=Money(4500)), \
             patch.object(MultiFamilyAnalysis, '_calculate_operating_expense_ratio', return_value=0.53):
            
            # Calculate type-specific metrics
            metrics = analysis._calculate_type_specific_metrics()
            
            # Verify metrics
            assert 'gross_potential_rent' in metrics
            assert 'actual_gross_income' in metrics
            assert 'other_income' in metrics
            assert 'net_operating_income' in metrics
            assert 'monthly_noi' in metrics
            assert 'noi_per_unit' in metrics
            assert 'annual_noi' in metrics
            assert 'cap_rate' in metrics
            assert 'dscr' in metrics
            assert 'gross_rent_multiplier' in metrics
            assert 'price_per_unit' in metrics
            assert 'occupancy_rate' in metrics
            assert 'expense_ratio' in metrics
            assert 'operating_expense_ratio' in metrics
            assert 'total_units' in metrics
            assert 'occupied_units' in metrics
            assert 'vacancy_units' in metrics
            assert 'unit_type_summary' in metrics
            
            # Check specific values
            assert metrics['gross_potential_rent'] == str(Money(11800))
            assert metrics['actual_gross_income'] == str(Money(10000))
            assert metrics['net_operating_income'] == str(Money(8710))
            assert metrics['cap_rate'] == str(Percentage(8.71))
            assert metrics['price_per_unit'] == str(Money(120000))
            assert metrics['occupancy_rate'] == str(Percentage(80.0))
            assert metrics['total_units'] == '10'
            assert metrics['occupied_units'] == '8'
            assert metrics['vacancy_units'] == '2'

class TestCreateAnalysis:
    """Test the create_analysis factory function."""
    
    def test_create_ltr_analysis(self, sample_ltr_data):
        """Test creating LTR analysis."""
        analysis = create_analysis(sample_ltr_data)
        assert isinstance(analysis, LTRAnalysis)
    
    def test_create_brrrr_analysis(self, sample_brrrr_data):
        """Test creating BRRRR analysis."""
        analysis = create_analysis(sample_brrrr_data)
        assert isinstance(analysis, BRRRRAnalysis)
    
    def test_create_lease_option_analysis(self, sample_lease_option_data):
        """Test creating Lease Option analysis."""
        analysis = create_analysis(sample_lease_option_data)
        assert isinstance(analysis, LeaseOptionAnalysis)
    
    def test_create_multi_family_analysis(self, sample_multi_family_data):
        """Test creating Multi-Family analysis."""
        analysis = create_analysis(sample_multi_family_data)
        assert isinstance(analysis, MultiFamilyAnalysis)
    
    def test_create_padsplit_ltr_analysis(self, sample_ltr_data):
        """Test creating PadSplit LTR analysis."""
        padsplit_data = sample_ltr_data.copy()
        padsplit_data["analysis_type"] = "PadSplit LTR"
        
        analysis = create_analysis(padsplit_data)
        assert isinstance(analysis, LTRAnalysis)
    
    def test_create_padsplit_brrrr_analysis(self, sample_brrrr_data):
        """Test creating PadSplit BRRRR analysis."""
        padsplit_data = sample_brrrr_data.copy()
        padsplit_data["analysis_type"] = "PadSplit BRRRR"
        
        analysis = create_analysis(padsplit_data)
        assert isinstance(analysis, BRRRRAnalysis)
    
    def test_create_invalid_analysis_type(self, sample_ltr_data):
        """Test creating analysis with invalid type."""
        invalid_data = sample_ltr_data.copy()
        invalid_data["analysis_type"] = "Invalid"
        
        with pytest.raises(ValueError):
            create_analysis(invalid_data)
