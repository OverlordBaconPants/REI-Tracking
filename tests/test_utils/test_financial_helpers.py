"""
Unit tests for financial helper utility functions.

This module contains tests for the utility functions in src/utils/financial_helpers.py.
"""

import pytest
from decimal import Decimal

from src.utils.financial_helpers import (
    calculate_cash_on_cash_return,
    calculate_cap_rate,
    calculate_debt_service_coverage_ratio,
    calculate_expense_ratio,
    calculate_gross_rent_multiplier,
    calculate_price_per_unit,
    calculate_breakeven_occupancy,
    calculate_roi,
    calculate_monthly_loan_payment,
    calculate_remaining_loan_balance,
    calculate_mao_for_ltr,
    calculate_mao_for_brrrr
)
from src.utils.money import Money, Percentage

class TestCalculateCashOnCashReturn:
    """Tests for the calculate_cash_on_cash_return function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        annual_cash_flow = Money(12000)
        total_investment = Money(100000)
        result = calculate_cash_on_cash_return(annual_cash_flow, total_investment)
        assert result.value == 12.0
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        annual_cash_flow = Decimal('12000')
        total_investment = Decimal('100000')
        result = calculate_cash_on_cash_return(annual_cash_flow, total_investment)
        assert result.value == 12.0
    
    def test_with_float_values(self):
        """Test with float values."""
        annual_cash_flow = 12000.0
        total_investment = 100000.0
        result = calculate_cash_on_cash_return(annual_cash_flow, total_investment)
        assert result.value == 12.0
    
    def test_zero_investment(self):
        """Test with zero investment."""
        annual_cash_flow = Money(12000)
        total_investment = Money(0)
        result = calculate_cash_on_cash_return(annual_cash_flow, total_investment)
        assert result.value == float('inf')
    
    def test_negative_cash_flow(self):
        """Test with negative cash flow."""
        annual_cash_flow = Money(-12000)
        total_investment = Money(100000)
        result = calculate_cash_on_cash_return(annual_cash_flow, total_investment)
        assert result.value == -12.0

class TestCalculateCapRate:
    """Tests for the calculate_cap_rate function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        annual_noi = Money(24000)
        property_value = Money(300000)
        result = calculate_cap_rate(annual_noi, property_value)
        assert result.value == 8.0
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        annual_noi = Decimal('24000')
        property_value = Decimal('300000')
        result = calculate_cap_rate(annual_noi, property_value)
        assert result.value == 8.0
    
    def test_with_float_values(self):
        """Test with float values."""
        annual_noi = 24000.0
        property_value = 300000.0
        result = calculate_cap_rate(annual_noi, property_value)
        assert result.value == 8.0
    
    def test_zero_property_value(self):
        """Test with zero property value."""
        annual_noi = Money(24000)
        property_value = Money(0)
        result = calculate_cap_rate(annual_noi, property_value)
        assert result.value == 0.0
    
    def test_negative_noi(self):
        """Test with negative NOI."""
        annual_noi = Money(-24000)
        property_value = Money(300000)
        result = calculate_cap_rate(annual_noi, property_value)
        assert result.value == -8.0

class TestCalculateDebtServiceCoverageRatio:
    """Tests for the calculate_debt_service_coverage_ratio function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        annual_noi = Money(24000)
        annual_debt_service = Money(18000)
        result = calculate_debt_service_coverage_ratio(annual_noi, annual_debt_service)
        assert result == 1.3333333333333333
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        annual_noi = Decimal('24000')
        annual_debt_service = Decimal('18000')
        result = calculate_debt_service_coverage_ratio(annual_noi, annual_debt_service)
        assert result == 1.3333333333333333
    
    def test_with_float_values(self):
        """Test with float values."""
        annual_noi = 24000.0
        annual_debt_service = 18000.0
        result = calculate_debt_service_coverage_ratio(annual_noi, annual_debt_service)
        assert result == 1.3333333333333333
    
    def test_zero_debt_service(self):
        """Test with zero debt service."""
        annual_noi = Money(24000)
        annual_debt_service = Money(0)
        result = calculate_debt_service_coverage_ratio(annual_noi, annual_debt_service)
        assert result == float('inf')
    
    def test_negative_noi(self):
        """Test with negative NOI."""
        annual_noi = Money(-24000)
        annual_debt_service = Money(18000)
        result = calculate_debt_service_coverage_ratio(annual_noi, annual_debt_service)
        assert result == -1.3333333333333333

class TestCalculateExpenseRatio:
    """Tests for the calculate_expense_ratio function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        annual_expenses = Money(12000)
        annual_income = Money(30000)
        result = calculate_expense_ratio(annual_expenses, annual_income)
        assert result.value == 40.0
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        annual_expenses = Decimal('12000')
        annual_income = Decimal('30000')
        result = calculate_expense_ratio(annual_expenses, annual_income)
        assert result.value == 40.0
    
    def test_with_float_values(self):
        """Test with float values."""
        annual_expenses = 12000.0
        annual_income = 30000.0
        result = calculate_expense_ratio(annual_expenses, annual_income)
        assert result.value == 40.0
    
    def test_zero_income(self):
        """Test with zero income."""
        annual_expenses = Money(12000)
        annual_income = Money(0)
        result = calculate_expense_ratio(annual_expenses, annual_income)
        assert result.value == 0.0
    
    def test_expenses_greater_than_income(self):
        """Test with expenses greater than income."""
        annual_expenses = Money(40000)
        annual_income = Money(30000)
        result = calculate_expense_ratio(annual_expenses, annual_income)
        assert result.value > 100.0

class TestCalculateGrossRentMultiplier:
    """Tests for the calculate_gross_rent_multiplier function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        purchase_price = Money(300000)
        annual_rent = Money(30000)
        result = calculate_gross_rent_multiplier(purchase_price, annual_rent)
        assert result == 10.0
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        purchase_price = Decimal('300000')
        annual_rent = Decimal('30000')
        result = calculate_gross_rent_multiplier(purchase_price, annual_rent)
        assert result == 10.0
    
    def test_with_float_values(self):
        """Test with float values."""
        purchase_price = 300000.0
        annual_rent = 30000.0
        result = calculate_gross_rent_multiplier(purchase_price, annual_rent)
        assert result == 10.0
    
    def test_zero_annual_rent(self):
        """Test with zero annual rent."""
        purchase_price = Money(300000)
        annual_rent = Money(0)
        result = calculate_gross_rent_multiplier(purchase_price, annual_rent)
        assert result == 0.0

class TestCalculatePricePerUnit:
    """Tests for the calculate_price_per_unit function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        purchase_price = Money(1000000)
        unit_count = 4
        result = calculate_price_per_unit(purchase_price, unit_count)
        assert result.dollars == 250000
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        purchase_price = Decimal('1000000')
        unit_count = 4
        result = calculate_price_per_unit(purchase_price, unit_count)
        assert result.dollars == 250000
    
    def test_with_float_values(self):
        """Test with float values."""
        purchase_price = 1000000.0
        unit_count = 4
        result = calculate_price_per_unit(purchase_price, unit_count)
        assert result.dollars == 250000
    
    def test_zero_unit_count(self):
        """Test with zero unit count."""
        purchase_price = Money(1000000)
        unit_count = 0
        result = calculate_price_per_unit(purchase_price, unit_count)
        assert result.dollars == 0
    
    def test_negative_unit_count(self):
        """Test with negative unit count."""
        purchase_price = Money(1000000)
        unit_count = -4
        result = calculate_price_per_unit(purchase_price, unit_count)
        assert result.dollars == 0

class TestCalculateBreakevenOccupancy:
    """Tests for the calculate_breakeven_occupancy function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        annual_expenses = Money(12000)
        annual_debt_service = Money(18000)
        annual_potential_income = Money(36000)
        result = calculate_breakeven_occupancy(annual_expenses, annual_debt_service, annual_potential_income)
        assert result.value == 83.33333333333333
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        annual_expenses = Decimal('12000')
        annual_debt_service = Decimal('18000')
        annual_potential_income = Decimal('36000')
        result = calculate_breakeven_occupancy(annual_expenses, annual_debt_service, annual_potential_income)
        assert result.value == 83.33333333333333
    
    def test_with_float_values(self):
        """Test with float values."""
        annual_expenses = 12000.0
        annual_debt_service = 18000.0
        annual_potential_income = 36000.0
        result = calculate_breakeven_occupancy(annual_expenses, annual_debt_service, annual_potential_income)
        assert result.value == 83.33333333333333
    
    def test_zero_potential_income(self):
        """Test with zero potential income."""
        annual_expenses = Money(12000)
        annual_debt_service = Money(18000)
        annual_potential_income = Money(0)
        result = calculate_breakeven_occupancy(annual_expenses, annual_debt_service, annual_potential_income)
        assert result.value == 100.0
    
    def test_expenses_greater_than_income(self):
        """Test with expenses greater than income."""
        annual_expenses = Money(20000)
        annual_debt_service = Money(20000)
        annual_potential_income = Money(30000)
        result = calculate_breakeven_occupancy(annual_expenses, annual_debt_service, annual_potential_income)
        assert result.value == 100.0

class TestCalculateROI:
    """Tests for the calculate_roi function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        initial_investment = Money(100000)
        total_return = Money(20000)
        result = calculate_roi(initial_investment, total_return)
        assert result.value == 20.0
    
    def test_with_decimal_values(self):
        """Test with Decimal values."""
        initial_investment = Decimal('100000')
        total_return = Decimal('20000')
        result = calculate_roi(initial_investment, total_return)
        assert result.value == 20.0
    
    def test_with_float_values(self):
        """Test with float values."""
        initial_investment = 100000.0
        total_return = 20000.0
        result = calculate_roi(initial_investment, total_return)
        assert result.value == 20.0
    
    def test_zero_investment(self):
        """Test with zero investment."""
        initial_investment = Money(0)
        total_return = Money(20000)
        result = calculate_roi(initial_investment, total_return)
        assert result.value == float('inf')
    
    def test_annualized_roi(self):
        """Test annualized ROI calculation."""
        initial_investment = Money(100000)
        total_return = Money(40000)
        time_period_years = 2.0
        result = calculate_roi(initial_investment, total_return, time_period_years)
        # Expected: ((1 + 0.4)^(1/2) - 1) * 100 = 18.32%
        assert round(result.value, 2) == 18.32

class TestCalculateMonthlyLoanPayment:
    """Tests for the calculate_monthly_loan_payment function."""
    
    def test_standard_amortizing_loan(self):
        """Test standard amortizing loan."""
        loan_amount = Money(200000)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        result = calculate_monthly_loan_payment(loan_amount, interest_rate, loan_term_months)
        assert round(result.dollars, 2) == 1013.37
    
    def test_interest_only_loan(self):
        """Test interest-only loan."""
        loan_amount = Money(200000)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        result = calculate_monthly_loan_payment(loan_amount, interest_rate, loan_term_months, is_interest_only=True)
        assert round(result.dollars, 2) == 750.00
    
    def test_zero_interest_loan(self):
        """Test zero-interest loan."""
        loan_amount = Money(200000)
        interest_rate = Percentage(0)
        loan_term_months = 360
        result = calculate_monthly_loan_payment(loan_amount, interest_rate, loan_term_months)
        assert round(result.dollars, 2) == 555.56
    
    def test_zero_loan_amount(self):
        """Test zero loan amount."""
        loan_amount = Money(0)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        result = calculate_monthly_loan_payment(loan_amount, interest_rate, loan_term_months)
        assert result.dollars == 0
    
    def test_zero_loan_term(self):
        """Test zero loan term."""
        loan_amount = Money(200000)
        interest_rate = Percentage(4.5)
        loan_term_months = 0
        result = calculate_monthly_loan_payment(loan_amount, interest_rate, loan_term_months)
        assert result.dollars == 0

class TestCalculateRemainingLoanBalance:
    """Tests for the calculate_remaining_loan_balance function."""
    
    def test_standard_amortizing_loan(self):
        """Test standard amortizing loan."""
        loan_amount = Money(200000)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        payments_made = 60
        result = calculate_remaining_loan_balance(loan_amount, interest_rate, loan_term_months, payments_made)
        assert round(result.dollars, 2) == 184422.60
    
    def test_interest_only_loan(self):
        """Test interest-only loan."""
        loan_amount = Money(200000)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        payments_made = 60
        result = calculate_remaining_loan_balance(loan_amount, interest_rate, loan_term_months, payments_made, is_interest_only=True)
        assert result.dollars == 200000
    
    def test_zero_interest_loan(self):
        """Test zero-interest loan."""
        loan_amount = Money(200000)
        interest_rate = Percentage(0)
        loan_term_months = 360
        payments_made = 60
        result = calculate_remaining_loan_balance(loan_amount, interest_rate, loan_term_months, payments_made)
        assert round(result.dollars, 2) == 166666.67
    
    def test_zero_loan_amount(self):
        """Test zero loan amount."""
        loan_amount = Money(0)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        payments_made = 60
        result = calculate_remaining_loan_balance(loan_amount, interest_rate, loan_term_months, payments_made)
        assert result.dollars == 0
    
    def test_payments_made_equals_term(self):
        """Test payments made equals term."""
        loan_amount = Money(200000)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        payments_made = 360
        result = calculate_remaining_loan_balance(loan_amount, interest_rate, loan_term_months, payments_made)
        assert result.dollars == 0
    
    def test_payments_made_exceeds_term(self):
        """Test payments made exceeds term."""
        loan_amount = Money(200000)
        interest_rate = Percentage(4.5)
        loan_term_months = 360
        payments_made = 400
        result = calculate_remaining_loan_balance(loan_amount, interest_rate, loan_term_months, payments_made)
        assert result.dollars == 0

class TestCalculateMAOForLTR:
    """Tests for the calculate_mao_for_ltr function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        monthly_income = Money(3000)
        monthly_expenses = Money(1000)
        target_monthly_cash_flow = Money(200)
        target_cap_rate = Percentage(8)
        result = calculate_mao_for_ltr(
            monthly_income, monthly_expenses, target_monthly_cash_flow, target_cap_rate)
        # Expected: min(NOI/cap_rate, supportable_loan/ltv)
        # NOI = (3000 - 1000) * 12 = 24000
        # cap_rate_mao = 24000 / 0.08 = 300000
        # monthly_cash_available = 3000 - 1000 - 200 = 1800
        # Exact value depends on loan payment calculation
        assert result.dollars > 0
    
    def test_zero_income(self):
        """Test zero income."""
        monthly_income = Money(0)
        monthly_expenses = Money(1000)
        target_monthly_cash_flow = Money(200)
        target_cap_rate = Percentage(8)
        result = calculate_mao_for_ltr(
            monthly_income, monthly_expenses, target_monthly_cash_flow, target_cap_rate)
        assert result.dollars == 0
    
    def test_expenses_exceed_income(self):
        """Test expenses exceed income."""
        monthly_income = Money(1000)
        monthly_expenses = Money(2000)
        target_monthly_cash_flow = Money(200)
        target_cap_rate = Percentage(8)
        result = calculate_mao_for_ltr(
            monthly_income, monthly_expenses, target_monthly_cash_flow, target_cap_rate)
        assert result.dollars == 0
    
    def test_zero_cap_rate(self):
        """Test zero cap rate."""
        monthly_income = Money(3000)
        monthly_expenses = Money(1000)
        target_monthly_cash_flow = Money(200)
        target_cap_rate = Percentage(0)
        result = calculate_mao_for_ltr(
            monthly_income, monthly_expenses, target_monthly_cash_flow, target_cap_rate)
        # Should use cash flow MAO since cap rate MAO is 0
        assert result.dollars > 0

class TestCalculateMAOForBRRRR:
    """Tests for the calculate_mao_for_brrrr function."""
    
    def test_basic_calculation(self):
        """Test basic calculation."""
        arv = Money(300000)
        renovation_costs = Money(50000)
        closing_costs = Money(5000)
        holding_costs = Money(5000)
        refinance_ltv_percentage = Percentage(75)
        max_cash_left = Money(10000)
        result = calculate_mao_for_brrrr(
            arv, renovation_costs, closing_costs, holding_costs, 
            refinance_ltv_percentage, max_cash_left)
        # Expected: loan_amount - renovation_costs - closing_costs - holding_costs + max_cash_left
        # loan_amount = 300000 * 0.75 = 225000
        # MAO = 225000 - 50000 - 5000 - 5000 + 10000 = 175000
        assert result.dollars == 175000
    
    def test_zero_arv(self):
        """Test zero ARV."""
        arv = Money(0)
        renovation_costs = Money(50000)
        closing_costs = Money(5000)
        holding_costs = Money(5000)
        result = calculate_mao_for_brrrr(arv, renovation_costs, closing_costs, holding_costs)
        assert result.dollars == 0
    
    def test_high_costs(self):
        """Test high costs."""
        arv = Money(300000)
        renovation_costs = Money(200000)
        closing_costs = Money(20000)
        holding_costs = Money(20000)
        refinance_ltv_percentage = Percentage(75)
        max_cash_left = Money(10000)
        result = calculate_mao_for_brrrr(
            arv, renovation_costs, closing_costs, holding_costs, 
            refinance_ltv_percentage, max_cash_left)
        # Expected: loan_amount - renovation_costs - closing_costs - holding_costs + max_cash_left
        # loan_amount = 300000 * 0.75 = 225000
        # MAO = 225000 - 200000 - 20000 - 20000 + 10000 = -5000 (capped at 0)
        assert result.dollars == 0
