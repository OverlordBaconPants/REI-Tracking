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

class TestAnalysisReportFinal:
    """Final tests for AnalysisReport class."""
    
    def test_from_analysis_with_minimal_data(self):
        """Test creating report from analysis with minimal data."""
        # Create a mock Analysis object
        mock_analysis = MagicMock()
        
        # Set up the mock data
        today = datetime.now().strftime('%Y-%m-%d')
        mock_analysis.data = {
            "id": "12345678-1234-5678-1234-567812345678",
            "user_id": "user123",
            "analysis_name": "Minimal Analysis",
            "analysis_type": "LTR",
            "address": "123 Main St",
            "created_at": today,
            "updated_at": today
        }
        
        # Set up the mock get_report_data method
        mock_analysis.get_report_data.return_value = {
            "metrics": {
                "monthly_cash_flow": "$100",
                "annual_cash_flow": "$1200"
            }
        }
        
        # Create report from the mock analysis
        report = AnalysisReport.from_analysis(mock_analysis)
        
        # Verify basic fields
        assert report.id == "12345678-1234-5678-1234-567812345678"
        assert report.user_id == "user123"
        assert report.analysis_name == "Minimal Analysis"
        assert report.analysis_type == "LTR"
        assert report.address == "123 Main St"
        
        # Verify default values for missing fields
        assert report.square_footage == 0
        assert report.lot_size == 0
        assert report.year_built == 0
        assert report.purchase_price == 0
        assert report.after_repair_value == 0
        assert report.renovation_costs == 0
        assert report.renovation_duration == 0
        assert report.monthly_rent == 0
        
        # Verify metrics
        assert report.metrics["monthly_cash_flow"] == "$100"
        assert report.metrics["annual_cash_flow"] == "$1200"

class TestLoanCalculatorFinal:
    """Final tests for LoanCalculator class."""
    
    def test_calculate_payment_negative_amount(self):
        """Test calculating payment with negative loan amount."""
        # Create a loan details object with mocked validation
        with patch.object(LoanDetails, '__post_init__'):
            loan = LoanDetails(
                amount=Money(-1000),
                interest_rate=Percentage(5.0),
                term=360,
                is_interest_only=False
            )
            
            # Test the calculation directly
            result = LoanCalculator.calculate_payment(loan)
            assert isinstance(result, Money)
            assert result.dollars == 0
    
    def test_calculate_payment_negative_term(self):
        """Test calculating payment with negative term."""
        # Create a loan details object with mocked validation
        with patch.object(LoanDetails, '__post_init__'):
            loan = LoanDetails(
                amount=Money(100000),
                interest_rate=Percentage(5.0),
                term=-12,
                is_interest_only=False
            )
            
            # Test the calculation directly
            result = LoanCalculator.calculate_payment(loan)
            assert isinstance(result, Money)
            assert result.dollars == 0

class TestMultiFamilyAnalysisFinal:
    """Final tests for MultiFamilyAnalysis class."""
    
    @pytest.fixture
    def sample_multifamily_data(self):
        """Create sample data for multi-family analysis."""
        today = datetime.now().strftime('%Y-%m-%d')
        unit_types = [
            {
                "type": "1BR",
                "count": 4,
                "occupied": 3,
                "square_footage": 750,
                "rent": 1200
            },
            {
                "type": "2BR",
                "count": 2,
                "occupied": 2,
                "square_footage": 1000,
                "rent": 1500
            }
        ]
        
        return {
            "id": "12345678-1234-5678-1234-567812345678",
            "user_id": "user123",
            "created_at": today,
            "updated_at": today,
            "analysis_type": "Multi-Family",
            "analysis_name": "Test Multi-Family",
            "address": "123 Main St, Test City, TS 12345",
            "purchase_price": 600000,
            "property_taxes": 500,
            "insurance": 300,
            "hoa_coa_coop": 0,
            "management_fee_percentage": 8,
            "capex_percentage": 5,
            "vacancy_percentage": 5,
            "repairs_percentage": 5,
            "total_units": 6,
            "occupied_units": 5,
            "floors": 2,
            "elevator_maintenance": 200,
            "common_area_maintenance": 150,
            "staff_payroll": 1000,
            "trash_removal": 100,
            "common_utilities": 300,
            "other_income": 200,
            "unit_types": json.dumps(unit_types),
            "loan1_loan_amount": 480000,
            "loan1_loan_interest_rate": 4.5,
            "loan1_loan_term": 360,
            "loan1_interest_only": False
        }
    
    def test_gross_rent_multiplier_zero_rent(self, sample_multifamily_data):
        """Test gross rent multiplier calculation with zero rent."""
        # Modify data to have zero rent
        data = sample_multifamily_data.copy()
        unit_types = json.loads(data['unit_types'])
        for unit in unit_types:
            unit['rent'] = 0
        data['unit_types'] = json.dumps(unit_types)
        
        # Create analysis with patched validation
        with patch.object(MultiFamilyAnalysis, '_validate_type_specific_requirements'):
            analysis = MultiFamilyAnalysis(data)
            
            # Test gross rent multiplier
            result = analysis.gross_rent_multiplier
            assert result == 0
    
    def test_price_per_unit_zero_units(self, sample_multifamily_data):
        """Test price per unit calculation with zero units."""
        # Modify data to have zero units
        data = sample_multifamily_data.copy()
        data['total_units'] = 0
        
        # Create analysis with patched validation
        with patch.object(MultiFamilyAnalysis, '_validate_type_specific_requirements'):
            analysis = MultiFamilyAnalysis(data)
            
            # Test price per unit
            result = analysis.price_per_unit
            assert isinstance(result, Money)
            assert result.dollars == 0
    
    def test_occupancy_rate_zero_units(self, sample_multifamily_data):
        """Test occupancy rate calculation with zero units."""
        # Modify data to have zero units
        data = sample_multifamily_data.copy()
        data['total_units'] = 0
        
        # Create analysis with patched validation
        with patch.object(MultiFamilyAnalysis, '_validate_type_specific_requirements'):
            analysis = MultiFamilyAnalysis(data)
            
            # Test occupancy rate
            result = analysis.occupancy_rate
            assert isinstance(result, Percentage)
            assert result.value == 0
