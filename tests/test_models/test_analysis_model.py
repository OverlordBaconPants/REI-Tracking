"""
Test module for the Analysis model.

This module contains tests for the Analysis model, focusing on the fields
and their consistency with the documentation.
"""

import pytest
from decimal import Decimal
from src.models.analysis import Analysis, LoanDetails, CompsData, UnitType


class TestAnalysisModel:
    """Test the Analysis model."""
    
    @pytest.fixture
    def basic_analysis_data(self):
        """Fixture for basic analysis data."""
        return {
            "id": "test-analysis-id",
            "user_id": "test-user-id",
            "analysis_type": "LTR",
            "analysis_name": "Test Analysis",
            "address": "123 Main St",
            "square_footage": 1500,
            "lot_size": 5000,
            "year_built": 2000,
            "bedrooms": 3,
            "bathrooms": 2,
            "purchase_price": 200000,
            "monthly_rent": 1500,
            "property_taxes": 2400,
            "insurance": 1200,
            "management_fee_percentage": 8,
            "capex_percentage": 5,
            "vacancy_percentage": 5,
            "repairs_percentage": 5,
            "initial_loan_amount": 160000,
            "initial_loan_interest_rate": 4.5,
            "initial_loan_term": 360,
            "initial_loan_down_payment": 40000,
            "initial_loan_closing_costs": 3000,
            "created_at": "2023-01-01T00:00:00.000Z",
            "updated_at": "2023-01-01T00:00:00.000Z"
        }
    
    def test_create_analysis(self, basic_analysis_data):
        """Test creating an Analysis instance."""
        analysis = Analysis(**basic_analysis_data)
        
        assert analysis.id == "test-analysis-id"
        assert analysis.user_id == "test-user-id"
        assert analysis.analysis_type == "LTR"
        assert analysis.analysis_name == "Test Analysis"
        assert analysis.address == "123 Main St"
        assert analysis.square_footage == 1500
        assert analysis.lot_size == 5000
        assert analysis.year_built == 2000
        assert analysis.bedrooms == 3
        assert analysis.bathrooms == 2
        assert analysis.purchase_price == 200000
        assert analysis.monthly_rent == 1500
        assert analysis.property_taxes == 2400
        assert analysis.insurance == 1200
        assert analysis.management_fee_percentage == 8
        assert analysis.capex_percentage == 5
        assert analysis.vacancy_percentage == 5
        assert analysis.repairs_percentage == 5
        assert analysis.initial_loan_amount == 160000
        assert analysis.initial_loan_interest_rate == 4.5
        assert analysis.initial_loan_term == 360
        assert analysis.initial_loan_down_payment == 40000
        assert analysis.initial_loan_closing_costs == 3000
        assert analysis.created_at == "2023-01-01T00:00:00.000Z"
        assert analysis.updated_at == "2023-01-01T00:00:00.000Z"
    
    def test_get_initial_loan(self, basic_analysis_data):
        """Test getting initial loan details."""
        analysis = Analysis(**basic_analysis_data)
        
        loan = analysis.get_initial_loan()
        
        assert loan is not None
        assert loan.loan_name == "Initial Loan"
        assert loan.loan_amount == Decimal("160000")
        assert loan.loan_interest_rate == Decimal("4.5")
        assert loan.loan_term == 360
        assert loan.loan_down_payment == Decimal("40000")
        assert loan.loan_closing_costs == Decimal("3000")
        assert loan.is_interest_only is False
    
    def test_calculate_monthly_payment(self, basic_analysis_data):
        """Test calculating monthly payment."""
        analysis = Analysis(**basic_analysis_data)
        
        loan = analysis.get_initial_loan()
        payment = analysis.calculate_monthly_payment(loan)
        
        # 160000 loan at 4.5% for 30 years = ~$810.70
        assert payment == pytest.approx(Decimal("810.70"), abs=Decimal("1"))
    
    def test_calculate_monthly_cash_flow(self, basic_analysis_data):
        """Test calculating monthly cash flow."""
        analysis = Analysis(**basic_analysis_data)
        
        cash_flow = analysis.calculate_monthly_cash_flow()
        
        # Income: 1500
        # Expenses: ~645 (property_taxes: 200, insurance: 100, management: 120, capex: 75, vacancy: 75, repairs: 75)
        # Loan payments: ~810.70
        # Cash flow: ~44.30
        assert cash_flow == pytest.approx(Decimal("44.30"), abs=Decimal("1"))
    
    def test_calculate_cap_rate(self, basic_analysis_data):
        """Test calculating cap rate."""
        analysis = Analysis(**basic_analysis_data)
        
        cap_rate = analysis.calculate_cap_rate()
        
        # NOI: (1500 - 645) * 12 = 10260
        # Purchase price: 200000
        # Cap rate: 10260 / 200000 * 100 = 5.13%
        assert cap_rate == pytest.approx(Decimal("5.13"), abs=Decimal("0.1"))
    
    def test_calculate_cash_on_cash_return(self, basic_analysis_data):
        """Test calculating cash-on-cash return."""
        analysis = Analysis(**basic_analysis_data)
        
        coc = analysis.calculate_cash_on_cash_return()
        
        # Annual cash flow: ~44.30 * 12 = ~531.60
        # Total investment: 40000 + 3000 = 43000
        # CoC: ~531.60 / 43000 * 100 = ~1.24%
        assert coc == pytest.approx(Decimal("1.24"), abs=Decimal("0.1"))
    
    def test_loan_details_class(self):
        """Test the LoanDetails class."""
        loan = LoanDetails(
            loan_name="Test Loan",
            loan_amount=Decimal("200000"),
            loan_interest_rate=Decimal("4.5"),
            loan_term=360,
            loan_down_payment=Decimal("40000"),
            loan_closing_costs=Decimal("3000"),
            is_interest_only=False
        )
        
        assert loan.loan_name == "Test Loan"
        assert loan.loan_amount == Decimal("200000")
        assert loan.loan_interest_rate == Decimal("4.5")
        assert loan.loan_term == 360
        assert loan.loan_down_payment == Decimal("40000")
        assert loan.loan_closing_costs == Decimal("3000")
        assert loan.is_interest_only is False
    
    def test_comps_data_class(self):
        """Test the CompsData class."""
        comps_data = CompsData(
            last_run="2023-01-01T00:00:00.000Z",
            run_count=1,
            estimated_value=220000,
            value_range_low=200000,
            value_range_high=240000,
            comparables=[
                {
                    "id": "comp1",
                    "formattedAddress": "456 Oak St",
                    "price": 225000,
                    "bedrooms": 3,
                    "bathrooms": 2,
                    "squareFootage": 1600,
                    "yearBuilt": 1998,
                    "distance": 0.5,
                    "correlation": 0.95
                }
            ]
        )
        
        assert comps_data.last_run == "2023-01-01T00:00:00.000Z"
        assert comps_data.run_count == 1
        assert comps_data.estimated_value == 220000
        assert comps_data.value_range_low == 200000
        assert comps_data.value_range_high == 240000
        assert len(comps_data.comparables) == 1
        assert comps_data.comparables[0]["id"] == "comp1"
    
    def test_unit_type_class(self):
        """Test the UnitType class."""
        unit_type = UnitType(
            name="1BR/1BA",
            count=4,
            bedrooms=1,
            bathrooms=1.0,
            square_footage=700,
            rent=1000
        )
        
        assert unit_type.name == "1BR/1BA"
        assert unit_type.count == 4
        assert unit_type.bedrooms == 1
        assert unit_type.bathrooms == 1.0
        assert unit_type.square_footage == 700
        assert unit_type.rent == 1000
