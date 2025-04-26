"""
Test module for the analysis calculation module.

This module contains tests for the analysis calculation classes and functions.
"""

import pytest
from decimal import Decimal
from src.utils.money import Money, Percentage
from src.utils.calculations.analysis import (
    BaseAnalysis, LTRAnalysis, BRRRRAnalysis, LeaseOptionAnalysis,
    MultiFamilyAnalysis, PadSplitAnalysis, create_analysis, AnalysisResult
)


class TestAnalysisResult:
    """Test the AnalysisResult class."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        result = AnalysisResult()
        
        assert isinstance(result.monthly_cash_flow, Money)
        assert isinstance(result.annual_cash_flow, Money)
        assert isinstance(result.cash_on_cash_return, Percentage)
        assert isinstance(result.cap_rate, Percentage)
        assert isinstance(result.roi, Percentage)
        assert isinstance(result.total_investment, Money)
        assert isinstance(result.monthly_income, Money)
        assert isinstance(result.monthly_expenses, Money)
        assert isinstance(result.expense_ratio, Percentage)
        assert isinstance(result.price_per_unit, Money)
        assert isinstance(result.breakeven_occupancy, Percentage)
        assert isinstance(result.mao, Money)
        
        assert result.monthly_cash_flow.dollars == 0
        assert result.debt_service_coverage_ratio == 0.0
        assert result.gross_rent_multiplier == 0.0
    
    def test_str_representation(self):
        """Test string representation."""
        result = AnalysisResult(
            monthly_cash_flow=Money(100),
            annual_cash_flow=Money(1200),
            cash_on_cash_return=Percentage(10),
            cap_rate=Percentage(8),
            roi=Percentage(12),
            total_investment=Money(10000),
            monthly_income=Money(500),
            monthly_expenses=Money(300),
            debt_service_coverage_ratio=1.5,
            expense_ratio=Percentage(60),
            gross_rent_multiplier=10.5,
            price_per_unit=Money(50000),
            breakeven_occupancy=Percentage(80),
            mao=Money(150000)
        )
        
        str_repr = str(result)
        
        assert "$100.00" in str_repr
        assert "$1,200.00" in str_repr
        assert "10.000%" in str_repr
        assert "8.000%" in str_repr
        assert "1.50" in str_repr
        assert "10.50" in str_repr
        assert "$50,000.00" in str_repr
        assert "80.000%" in str_repr
        assert "$150,000.00" in str_repr


class TestBaseAnalysis:
    """Test the BaseAnalysis class."""
    
    @pytest.fixture
    def basic_data(self):
        """Fixture for basic analysis data."""
        return {
            'analysis_name': 'Test Analysis',
            'address': '123 Main St',
            'purchase_price': 200000,
            'monthly_rent': 1500,
            'property_taxes': 2400,
            'insurance': 1200,
            'closing_costs': 3000,
            'management_fee_percentage': 8,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'utilities': 0,
            'initial_loan_amount': 160000,
            'initial_loan_interest_rate': 4.5,
            'initial_loan_term': 360
        }
    
    def test_init(self, basic_data):
        """Test initialization."""
        analysis = BaseAnalysis(basic_data)
        
        assert analysis.data == basic_data
        assert analysis.validation_result is not None
    
    def test_validate_valid_data(self, basic_data):
        """Test validation with valid data."""
        analysis = BaseAnalysis(basic_data)
        result = analysis.validate()
        
        assert result.is_valid()
        assert len(result.errors) == 0
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        data = {
            'analysis_name': 'Test Analysis',
            'address': '123 Main St'
            # Missing purchase_price and monthly_rent
        }
        
        analysis = BaseAnalysis(data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 2
        
        error_fields = [error.field for error in result.errors]
        assert 'purchase_price' in error_fields
        assert 'monthly_rent' in error_fields
    
    def test_validate_invalid_numeric_fields(self):
        """Test validation with invalid numeric fields."""
        data = {
            'analysis_name': 'Test Analysis',
            'address': '123 Main St',
            'purchase_price': -100000,  # Negative value
            'monthly_rent': 'invalid',  # Not a number
            'property_taxes': 2400
        }
        
        analysis = BaseAnalysis(data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 2
    
    def test_validate_invalid_percentage_fields(self):
        """Test validation with invalid percentage fields."""
        data = {
            'analysis_name': 'Test Analysis',
            'address': '123 Main St',
            'purchase_price': 200000,
            'monthly_rent': 1500,
            'management_fee_percentage': 120,  # Over 100%
            'capex_percentage': -5  # Negative percentage
        }
        
        analysis = BaseAnalysis(data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 2
    
    def test_get_loan_details(self, basic_data):
        """Test getting loan details."""
        analysis = BaseAnalysis(basic_data)
        
        loan = analysis.get_loan_details('initial_loan')
        
        assert loan is not None
        assert loan.amount.dollars == 160000
        assert loan.interest_rate.value == 4.5
        assert loan.term == 360
        assert loan.is_interest_only is False
        assert loan.name == 'Initial Loan'
        
        # Test non-existent loan
        assert analysis.get_loan_details('nonexistent_loan') is None
    
    def test_calculate_monthly_income(self, basic_data):
        """Test calculating monthly income."""
        analysis = BaseAnalysis(basic_data)
        
        income = analysis.calculate_monthly_income()
        
        assert income.dollars == 1500
    
    def test_calculate_monthly_expenses(self, basic_data):
        """Test calculating monthly expenses."""
        analysis = BaseAnalysis(basic_data)
        
        expenses = analysis.calculate_monthly_expenses()
        
        # Property taxes: 2400/12 = 200
        # Insurance: 1200/12 = 100
        # Management fee: 1500 * 0.08 = 120
        # CapEx: 1500 * 0.05 = 75
        # Vacancy: 1500 * 0.05 = 75
        # Repairs: 1500 * 0.05 = 75
        # Total: 645
        assert expenses.dollars == pytest.approx(645)
    
    def test_calculate_loan_payments(self, basic_data):
        """Test calculating loan payments."""
        analysis = BaseAnalysis(basic_data)
        
        payments = analysis.calculate_loan_payments()
        
        # 160000 loan at 4.5% for 30 years = ~$810.70
        assert payments.dollars == pytest.approx(810.70, abs=1)
    
    def test_calculate_monthly_cash_flow(self, basic_data):
        """Test calculating monthly cash flow."""
        analysis = BaseAnalysis(basic_data)
        
        cash_flow = analysis.calculate_monthly_cash_flow()
        
        # Income: 1500
        # Expenses: ~645
        # Loan payments: ~810.70
        # Cash flow: ~44.30
        assert cash_flow.dollars == pytest.approx(44.30, abs=1)
    
    def test_calculate_total_investment(self, basic_data):
        """Test calculating total investment."""
        # Add down payment to basic data
        data = basic_data.copy()
        data['initial_loan_down_payment'] = 40000
        
        analysis = BaseAnalysis(data)
        
        investment = analysis.calculate_total_investment()
        
        # Down payment: 40000
        # Closing costs: 3000
        # Total: 43000
        assert investment.dollars == 43000
    
    def test_calculate_cash_on_cash_return(self, basic_data):
        """Test calculating cash-on-cash return."""
        # Add down payment to basic data
        data = basic_data.copy()
        data['initial_loan_down_payment'] = 40000
        
        analysis = BaseAnalysis(data)
        
        coc = analysis.calculate_cash_on_cash_return()
        
        # Annual cash flow: ~44.30 * 12 = ~531.60
        # Total investment: 43000
        # CoC: ~531.60 / 43000 * 100 = ~1.24%
        assert coc.value == pytest.approx(1.24, abs=0.1)
    
    def test_calculate_cap_rate(self, basic_data):
        """Test calculating cap rate."""
        analysis = BaseAnalysis(basic_data)
        
        cap_rate = analysis.calculate_cap_rate()
        
        # NOI: (1500 - 645) * 12 = 10260
        # Purchase price: 200000
        # Cap rate: 10260 / 200000 * 100 = 5.13%
        assert cap_rate.value == pytest.approx(5.13, abs=0.1)
    
    def test_calculate_debt_service_coverage_ratio(self, basic_data):
        """Test calculating DSCR."""
        analysis = BaseAnalysis(basic_data)
        
        dscr = analysis.calculate_debt_service_coverage_ratio()
        
        # NOI: 1500 - 645 = 855
        # Debt service: ~810.70
        # DSCR: 855 / 810.70 = ~1.05
        assert dscr == pytest.approx(1.05, abs=0.1)
    
    def test_calculate_expense_ratio(self, basic_data):
        """Test calculating expense ratio."""
        analysis = BaseAnalysis(basic_data)
        
        ratio = analysis.calculate_expense_ratio()
        
        # Expenses: 645
        # Income: 1500
        # Ratio: 645 / 1500 * 100 = 43%
        assert ratio.value == pytest.approx(43, abs=1)
    
    def test_calculate_gross_rent_multiplier(self, basic_data):
        """Test calculating gross rent multiplier."""
        analysis = BaseAnalysis(basic_data)
        
        grm = analysis.calculate_gross_rent_multiplier()
        
        # Purchase price: 200000
        # Annual rent: 1500 * 12 = 18000
        # GRM: 200000 / 18000 = 11.11
        assert grm == pytest.approx(11.11, abs=0.1)
    
    def test_calculate_breakeven_occupancy(self, basic_data):
        """Test calculating breakeven occupancy."""
        analysis = BaseAnalysis(basic_data)
        
        occupancy = analysis.calculate_breakeven_occupancy()
        
        # Expenses: 645
        # Loan payments: ~810.70
        # Total expenses: ~1455.70
        # Income: 1500
        # Breakeven: 1455.70 / 1500 * 100 = ~97%
        assert occupancy.value == pytest.approx(97, abs=1)
    
    def test_analyze(self, basic_data):
        """Test the analyze method."""
        # Add down payment to basic data
        data = basic_data.copy()
        data['initial_loan_down_payment'] = 40000
        
        analysis = BaseAnalysis(data)
        
        result = analysis.analyze()
        
        assert isinstance(result, AnalysisResult)
        assert result.monthly_cash_flow.dollars == pytest.approx(44.30, abs=1)
        assert result.annual_cash_flow.dollars == pytest.approx(531.60, abs=12)
        assert result.cash_on_cash_return.value == pytest.approx(1.24, abs=0.1)
        assert result.cap_rate.value == pytest.approx(5.13, abs=0.1)
        assert result.total_investment.dollars == 43000
        assert result.monthly_income.dollars == 1500
        assert result.monthly_expenses.dollars == pytest.approx(645, abs=1)
        assert result.debt_service_coverage_ratio == pytest.approx(1.05, abs=0.1)
        assert result.expense_ratio.value == pytest.approx(43, abs=1)
        assert result.gross_rent_multiplier == pytest.approx(11.11, abs=0.1)
        assert result.breakeven_occupancy.value == pytest.approx(97, abs=1)


class TestLTRAnalysis:
    """Test the LTRAnalysis class."""
    
    @pytest.fixture
    def ltr_data(self):
        """Fixture for LTR analysis data."""
        return {
            'analysis_type': 'LTR',
            'analysis_name': 'Test LTR Analysis',
            'address': '123 Main St',
            'purchase_price': 200000,
            'monthly_rent': 1500,
            'property_taxes': 2400,
            'insurance': 1200,
            'closing_costs': 3000,
            'management_fee_percentage': 8,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'initial_loan_amount': 160000,
            'initial_loan_interest_rate': 4.5,
            'initial_loan_term': 360,
            'initial_loan_down_payment': 40000
        }
    
    def test_validate_required_fields(self, ltr_data):
        """Test validation of required fields for LTR."""
        analysis = LTRAnalysis(ltr_data)
        result = analysis.validate()
        
        assert result.is_valid()
        
        # Remove required fields
        invalid_data = ltr_data.copy()
        del invalid_data['property_taxes']
        del invalid_data['insurance']
        
        analysis = LTRAnalysis(invalid_data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 2
    
    def test_calculate_mao(self, ltr_data):
        """Test calculating MAO for LTR."""
        analysis = LTRAnalysis(ltr_data)
        
        mao = analysis.calculate_mao()
        
        # This is a complex calculation, just ensure it returns a Money object
        assert isinstance(mao, Money)
        assert mao.dollars > 0


class TestBRRRRAnalysis:
    """Test the BRRRRAnalysis class."""
    
    @pytest.fixture
    def brrrr_data(self):
        """Fixture for BRRRR analysis data."""
        return {
            'analysis_type': 'BRRRR',
            'analysis_name': 'Test BRRRR Analysis',
            'address': '123 Main St',
            'purchase_price': 150000,
            'monthly_rent': 1500,
            'property_taxes': 2400,
            'insurance': 1200,
            'closing_costs': 3000,
            'management_fee_percentage': 8,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'after_repair_value': 250000,
            'renovation_costs': 50000,
            'renovation_duration': 3,
            'initial_loan_amount': 120000,
            'initial_loan_interest_rate': 6.0,
            'initial_loan_term': 360,
            'initial_loan_down_payment': 30000,
            'refinance_loan_amount': 187500,  # 75% of ARV
            'refinance_loan_interest_rate': 4.5,
            'refinance_loan_term': 360,
            'refinance_ltv_percentage': 75
        }
    
    def test_validate_required_fields(self, brrrr_data):
        """Test validation of required fields for BRRRR."""
        analysis = BRRRRAnalysis(brrrr_data)
        result = analysis.validate()
        
        assert result.is_valid()
        
        # Remove required fields
        invalid_data = brrrr_data.copy()
        del invalid_data['after_repair_value']
        del invalid_data['renovation_costs']
        del invalid_data['renovation_duration']
        
        analysis = BRRRRAnalysis(invalid_data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 3
    
    def test_calculate_mao(self, brrrr_data):
        """Test calculating MAO for BRRRR."""
        analysis = BRRRRAnalysis(brrrr_data)
        
        mao = analysis.calculate_mao()
        
        # ARV: 250000
        # Loan amount (75% LTV): 187500
        # Renovation costs: 50000
        # Closing costs: 3000
        # Holding costs: calculated based on renovation duration
        # Max cash left: 10000 (default)
        # MAO should be positive
        assert isinstance(mao, Money)
        assert mao.dollars > 0
    
    def test_calculate_total_investment_with_refinance(self, brrrr_data):
        """Test calculating total investment with refinance."""
        analysis = BRRRRAnalysis(brrrr_data)
        
        investment = analysis.calculate_total_investment()
        
        # Initial investment: down payment + closing costs + renovation costs = 30000 + 3000 + 50000 = 83000
        # Cash out from refinance: refinance_loan - initial_loan = 187500 - 120000 = 67500
        # Final investment: 83000 - 67500 = 15500
        assert investment.dollars == pytest.approx(15500, abs=1)


class TestLeaseOptionAnalysis:
    """Test the LeaseOptionAnalysis class."""
    
    @pytest.fixture
    def lease_option_data(self):
        """Fixture for Lease Option analysis data."""
        return {
            'analysis_type': 'LeaseOption',
            'analysis_name': 'Test Lease Option Analysis',
            'address': '123 Main St',
            'purchase_price': 200000,
            'monthly_rent': 1500,
            'property_taxes': 2400,
            'insurance': 1200,
            'closing_costs': 1000,
            'option_consideration_fee': 5000,
            'option_term_months': 24,
            'strike_price': 210000,
            'monthly_rent_credit': 200
        }
    
    def test_validate_required_fields(self, lease_option_data):
        """Test validation of required fields for Lease Option."""
        analysis = LeaseOptionAnalysis(lease_option_data)
        result = analysis.validate()
        
        assert result.is_valid()
        
        # Remove required fields
        invalid_data = lease_option_data.copy()
        del invalid_data['option_consideration_fee']
        del invalid_data['option_term_months']
        del invalid_data['strike_price']
        
        analysis = LeaseOptionAnalysis(invalid_data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 3
    
    def test_calculate_monthly_income(self, lease_option_data):
        """Test calculating monthly income for Lease Option."""
        analysis = LeaseOptionAnalysis(lease_option_data)
        
        income = analysis.calculate_monthly_income()
        
        # Rent: 1500
        # Rent credit: 200
        # Total: 1700
        assert income.dollars == 1700
    
    def test_calculate_total_investment(self, lease_option_data):
        """Test calculating total investment for Lease Option."""
        analysis = LeaseOptionAnalysis(lease_option_data)
        
        investment = analysis.calculate_total_investment()
        
        # Option fee: 5000
        # Closing costs: 1000
        # Total: 6000
        assert investment.dollars == 6000
    
    def test_calculate_effective_purchase_price(self, lease_option_data):
        """Test calculating effective purchase price for Lease Option."""
        analysis = LeaseOptionAnalysis(lease_option_data)
        
        price = analysis.calculate_effective_purchase_price()
        
        # Strike price: 210000
        # Total rent credits: 200 * 24 = 4800
        # Option fee: 5000
        # Effective price: 210000 - 4800 - 5000 = 200200
        assert price.dollars == 200200


class TestMultiFamilyAnalysis:
    """Test the MultiFamilyAnalysis class."""
    
    @pytest.fixture
    def multi_family_data(self):
        """Fixture for Multi-Family analysis data."""
        return {
            'analysis_type': 'MultiFamily',
            'analysis_name': 'Test Multi-Family Analysis',
            'address': '123 Main St',
            'purchase_price': 500000,
            'monthly_rent': 1000,  # Per unit
            'property_taxes': 6000,
            'insurance': 3000,
            'total_units': 5,
            'occupied_units': 4,
            'management_fee_percentage': 8,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'initial_loan_amount': 400000,
            'initial_loan_interest_rate': 4.5,
            'initial_loan_term': 360,
            'initial_loan_down_payment': 100000
        }
    
    def test_validate_required_fields(self, multi_family_data):
        """Test validation of required fields for Multi-Family."""
        analysis = MultiFamilyAnalysis(multi_family_data)
        result = analysis.validate()
        
        assert result.is_valid()
        
        # Remove required fields
        invalid_data = multi_family_data.copy()
        del invalid_data['total_units']
        del invalid_data['occupied_units']
        
        analysis = MultiFamilyAnalysis(invalid_data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 2
    
    def test_calculate_monthly_income(self, multi_family_data):
        """Test calculating monthly income for Multi-Family."""
        analysis = MultiFamilyAnalysis(multi_family_data)
        
        income = analysis.calculate_monthly_income()
        
        # Rent per unit: 1000
        # Occupied units: 4
        # Total: 4000
        assert income.dollars == 4000
    
    def test_calculate_price_per_unit(self, multi_family_data):
        """Test calculating price per unit for Multi-Family."""
        analysis = MultiFamilyAnalysis(multi_family_data)
        
        price_per_unit = analysis.calculate_price_per_unit()
        
        # Purchase price: 500000
        # Total units: 5
        # Price per unit: 100000
        assert price_per_unit.dollars == 100000
    
    def test_analyze(self, multi_family_data):
        """Test the analyze method for Multi-Family."""
        analysis = MultiFamilyAnalysis(multi_family_data)
        
        result = analysis.analyze()
        
        # Ensure price_per_unit is calculated
        assert result.price_per_unit.dollars == 100000


class TestPadSplitAnalysis:
    """Test the PadSplitAnalysis class."""
    
    @pytest.fixture
    def padsplit_data(self):
        """Fixture for PadSplit analysis data."""
        return {
            'analysis_type': 'PadSplit',
            'analysis_name': 'Test PadSplit Analysis',
            'address': '123 Main St',
            'purchase_price': 200000,
            'monthly_rent': 3000,  # Total for all rooms
            'property_taxes': 2400,
            'insurance': 1200,
            'furnishing_costs': 10000,
            'padsplit_platform_percentage': 12,
            'management_fee_percentage': 8,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'initial_loan_amount': 160000,
            'initial_loan_interest_rate': 4.5,
            'initial_loan_term': 360,
            'initial_loan_down_payment': 40000
        }
    
    def test_validate_required_fields(self, padsplit_data):
        """Test validation of required fields for PadSplit."""
        analysis = PadSplitAnalysis(padsplit_data)
        result = analysis.validate()
        
        assert result.is_valid()
        
        # Remove required fields
        invalid_data = padsplit_data.copy()
        del invalid_data['furnishing_costs']
        del invalid_data['padsplit_platform_percentage']
        
        analysis = PadSplitAnalysis(invalid_data)
        result = analysis.validate()
        
        assert not result.is_valid()
        assert len(result.errors) == 2
    
    def test_calculate_monthly_expenses(self, padsplit_data):
        """Test calculating monthly expenses for PadSplit."""
        analysis = PadSplitAnalysis(padsplit_data)
        
        expenses = analysis.calculate_monthly_expenses()
        
        # Base expenses (property taxes, insurance, etc.)
        # Plus PadSplit platform fee: 3000 * 0.12 = 360
        assert expenses.dollars > 0
        
        # Create a copy without platform fee for comparison
        data_without_platform = padsplit_data.copy()
        data_without_platform['padsplit_platform_percentage'] = 0
        analysis_without_platform = PadSplitAnalysis(data_without_platform)
        expenses_without_platform = analysis_without_platform.calculate_monthly_expenses()
        
        # Difference should be the platform fee
        assert expenses.dollars - expenses_without_platform.dollars == pytest.approx(360, abs=1)


class TestCreateAnalysis:
    """Test the create_analysis factory function."""
    
    def test_create_ltr_analysis(self):
        """Test creating an LTR analysis."""
        data = {'analysis_type': 'LTR'}
        analysis = create_analysis(data)
        
        assert isinstance(analysis, LTRAnalysis)
    
    def test_create_brrrr_analysis(self):
        """Test creating a BRRRR analysis."""
        data = {'analysis_type': 'BRRRR'}
        analysis = create_analysis(data)
        
        assert isinstance(analysis, BRRRRAnalysis)
    
    def test_create_lease_option_analysis(self):
        """Test creating a Lease Option analysis."""
        data = {'analysis_type': 'LeaseOption'}
        analysis = create_analysis(data)
        
        assert isinstance(analysis, LeaseOptionAnalysis)
    
    def test_create_multi_family_analysis(self):
        """Test creating a Multi-Family analysis."""
        data = {'analysis_type': 'MultiFamily'}
        analysis = create_analysis(data)
        
        assert isinstance(analysis, MultiFamilyAnalysis)
    
    def test_create_padsplit_analysis(self):
        """Test creating a PadSplit analysis."""
        data = {'analysis_type': 'PadSplit'}
        analysis = create_analysis(data)
        
        assert isinstance(analysis, PadSplitAnalysis)
    
    def test_create_invalid_analysis_type(self):
        """Test creating an analysis with an invalid type."""
        data = {'analysis_type': 'InvalidType'}
        
        with pytest.raises(ValueError):
            create_analysis(data)
    
    def test_create_missing_analysis_type(self):
        """Test creating an analysis with missing type."""
        data = {}
        
        with pytest.raises(ValueError):
            create_analysis(data)
