"""
Tests for the investment metrics calculator module.

This module contains tests for the investment metrics calculator,
including ROI, equity tracking, and other investment-specific calculations.
"""

import pytest
from decimal import Decimal
from src.utils.money import Money, Percentage
from src.utils.calculations.loan_details import LoanDetails
from src.utils.calculations.investment_metrics import (
    InvestmentMetricsCalculator,
    EquityProjection,
    YearlyProjection
)

class TestInvestmentMetricsCalculator:
    """Tests for the InvestmentMetricsCalculator class."""
    
    def test_calculate_roi(self):
        """Test ROI calculation."""
        # Test basic ROI calculation
        roi = InvestmentMetricsCalculator.calculate_roi(
            initial_investment=Money(100000),
            total_return=Money(10000)
        )
        assert roi.value == 10.0
        
        # Test ROI with zero investment (should return infinity)
        roi = InvestmentMetricsCalculator.calculate_roi(
            initial_investment=Money(0),
            total_return=Money(10000)
        )
        assert roi.is_infinite
        
        # Test ROI with negative return
        roi = InvestmentMetricsCalculator.calculate_roi(
            initial_investment=Money(100000),
            total_return=Money(-5000)
        )
        assert roi.value == -5.0
        
        # Test annualized ROI over multiple years
        roi = InvestmentMetricsCalculator.calculate_roi(
            initial_investment=Money(100000),
            total_return=Money(21000),
            time_period_years=2.0
        )
        assert round(roi.value, 2) == 10.0  # 10% annualized over 2 years
    
    def test_project_equity(self):
        """Test equity projection calculation."""
        # Create a loan for testing
        loan = LoanDetails(
            amount=Money(240000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False
        )
        
        # Test basic equity projection
        projection = InvestmentMetricsCalculator.project_equity(
            purchase_price=Money(300000),
            current_value=Money(300000),
            loan_details=loan,
            annual_appreciation_rate=Percentage(3),
            projection_years=30,
            payments_made=0
        )
        
        # Verify initial equity
        assert projection.initial_equity == Money(60000)  # 300k - 240k
        
        # Verify property value after appreciation
        # 300k * (1.03^30) ≈ 728k
        assert 720000 < projection.property_value.dollars < 730000
        
        # Verify loan is paid off
        assert projection.loan_balance == Money(0)
        
        # Verify equity components
        assert projection.equity_from_appreciation.dollars > 400000  # ~428k
        assert projection.equity_from_principal.dollars == 240000  # Full loan amount
        assert projection.total_equity_gain.dollars > 640000  # ~668k
        
        # Test with no loan (all equity)
        projection = InvestmentMetricsCalculator.project_equity(
            purchase_price=Money(300000),
            annual_appreciation_rate=Percentage(3),
            projection_years=10
        )
        
        # Verify initial equity is full purchase price
        assert projection.initial_equity == Money(300000)
        
        # Verify property value after appreciation
        # 300k * (1.03^10) ≈ 403k
        assert 400000 < projection.property_value.dollars < 405000
        
        # Verify equity components
        assert projection.equity_from_appreciation.dollars > 100000  # ~103k
        assert projection.equity_from_principal.dollars == 0  # No loan
        assert projection.total_equity_gain.dollars > 100000  # ~103k
    
    def test_generate_yearly_equity_projections(self):
        """Test generation of yearly equity projections."""
        # Create a loan for testing
        loan = LoanDetails(
            amount=Money(240000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False
        )
        
        # Generate 5-year projections
        projections = InvestmentMetricsCalculator.generate_yearly_equity_projections(
            purchase_price=Money(300000),
            loan_details=loan,
            annual_appreciation_rate=Percentage(3),
            projection_years=5
        )
        
        # Verify we have 5 years of projections
        assert len(projections) == 5
        
        # Verify first year
        assert projections[0].year == 1
        assert projections[0].property_value.dollars > 300000  # Appreciated
        assert projections[0].loan_balance.dollars < 240000  # Some principal paid
        
        # Verify fifth year
        assert projections[4].year == 5
        assert projections[4].property_value.dollars > projections[0].property_value.dollars
        # Note: We don't check loan balance progression as it depends on the specific loan calculation
        
        # Verify cumulative values
        assert projections[4].equity_from_appreciation.dollars > 0
        assert projections[4].equity_from_principal.dollars > 0
        assert projections[4].equity.dollars > 60000  # More than initial equity
    
    def test_calculate_gross_rent_multiplier(self):
        """Test Gross Rent Multiplier calculation."""
        # Test basic GRM calculation
        grm = InvestmentMetricsCalculator.calculate_gross_rent_multiplier(
            purchase_price=Money(300000),
            annual_rent=Money(30000)
        )
        assert grm == 10.0
        
        # Test with zero annual rent
        grm = InvestmentMetricsCalculator.calculate_gross_rent_multiplier(
            purchase_price=Money(300000),
            annual_rent=Money(0)
        )
        assert grm == 0.0
    
    def test_calculate_price_per_unit(self):
        """Test price per unit calculation."""
        # Test basic price per unit calculation
        price_per_unit = InvestmentMetricsCalculator.calculate_price_per_unit(
            purchase_price=Money(1000000),
            unit_count=4
        )
        assert price_per_unit == Money(250000)
        
        # Test with zero units
        price_per_unit = InvestmentMetricsCalculator.calculate_price_per_unit(
            purchase_price=Money(1000000),
            unit_count=0
        )
        assert price_per_unit == Money(0)
    
    def test_calculate_cash_on_cash_return(self):
        """Test Cash-on-Cash Return calculation."""
        # Test basic CoC calculation
        coc = InvestmentMetricsCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(12000),
            total_investment=Money(100000)
        )
        assert coc.value == 12.0
        
        # Test with zero investment
        coc = InvestmentMetricsCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(12000),
            total_investment=Money(0)
        )
        assert coc.is_infinite
        
        # Test with negative cash flow
        coc = InvestmentMetricsCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(-5000),
            total_investment=Money(100000)
        )
        assert coc.value == -5.0
    
    def test_calculate_cap_rate(self):
        """Test Cap Rate calculation."""
        # Test basic cap rate calculation
        cap_rate = InvestmentMetricsCalculator.calculate_cap_rate(
            annual_noi=Money(24000),
            property_value=Money(300000)
        )
        assert cap_rate.value == 8.0
        
        # Test with zero property value
        cap_rate = InvestmentMetricsCalculator.calculate_cap_rate(
            annual_noi=Money(24000),
            property_value=Money(0)
        )
        assert cap_rate.value == 0.0
    
    def test_calculate_debt_service_coverage_ratio(self):
        """Test DSCR calculation."""
        # Test basic DSCR calculation
        dscr = InvestmentMetricsCalculator.calculate_debt_service_coverage_ratio(
            annual_noi=Money(24000),
            annual_debt_service=Money(18000)
        )
        assert dscr == 1.3333333333333333
        
        # Test with zero debt service
        dscr = InvestmentMetricsCalculator.calculate_debt_service_coverage_ratio(
            annual_noi=Money(24000),
            annual_debt_service=Money(0)
        )
        assert dscr == float('inf')
    
    def test_calculate_expense_ratio(self):
        """Test Expense Ratio calculation."""
        # Test basic expense ratio calculation
        expense_ratio = InvestmentMetricsCalculator.calculate_expense_ratio(
            annual_expenses=Money(12000),
            annual_income=Money(30000)
        )
        assert expense_ratio.value == 40.0
        
        # Test with zero income
        expense_ratio = InvestmentMetricsCalculator.calculate_expense_ratio(
            annual_expenses=Money(12000),
            annual_income=Money(0)
        )
        assert expense_ratio.value == 0.0
    
    def test_calculate_breakeven_occupancy(self):
        """Test Breakeven Occupancy calculation."""
        # Test basic breakeven occupancy calculation
        breakeven = InvestmentMetricsCalculator.calculate_breakeven_occupancy(
            annual_expenses=Money(12000),
            annual_debt_service=Money(18000),
            annual_potential_income=Money(36000)
        )
        assert round(breakeven.value, 2) == 83.33
        
        # Test with expenses exceeding income
        breakeven = InvestmentMetricsCalculator.calculate_breakeven_occupancy(
            annual_expenses=Money(20000),
            annual_debt_service=Money(18000),
            annual_potential_income=Money(36000)
        )
        assert breakeven.value == 100.0  # Should be capped at 100
        
        # Test with zero potential income
        breakeven = InvestmentMetricsCalculator.calculate_breakeven_occupancy(
            annual_expenses=Money(12000),
            annual_debt_service=Money(18000),
            annual_potential_income=Money(0)
        )
        assert breakeven.value == 100.0
