"""
Tests for the financial calculations module.

This module contains tests for the financial calculations module, including
cash flow calculations, balloon payment analysis, lease option calculations,
and refinance impact analysis.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime

from src.utils.money import Money, Percentage
from src.utils.calculations.loan_details import LoanDetails
from src.utils.calculations.financial_calculations import (
    FinancialCalculator,
    CashFlowBreakdown,
    BalloonAnalysis,
    LeaseOptionCalculation,
    RefinanceImpactAnalysis
)

class TestFinancialCalculator:
    """Tests for the FinancialCalculator class."""
    
    def test_calculate_detailed_cash_flow(self):
        """Test calculating detailed cash flow breakdown."""
        # Test data
        data = {
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'utilities': 100,
            'management_fee_percentage': 10,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'initial_loan_amount': 240000,
            'initial_loan_interest_rate': 4.5,
            'initial_loan_term': 360
        }
        
        # Calculate cash flow
        cash_flow = FinancialCalculator.calculate_detailed_cash_flow(data)
        
        # Verify income
        assert 'Monthly Rent' in cash_flow.income
        assert cash_flow.income['Monthly Rent'] == Money(2000)
        assert cash_flow.total_income == Money(2000)
        
        # Verify expenses
        assert 'Property Taxes' in cash_flow.expenses
        assert cash_flow.expenses['Property Taxes'] == Money(2400) / 12
        assert 'Insurance' in cash_flow.expenses
        assert cash_flow.expenses['Insurance'] == Money(1200) / 12
        assert 'Utilities' in cash_flow.expenses
        assert cash_flow.expenses['Utilities'] == Money(100)
        assert 'Management Fee' in cash_flow.expenses
        assert cash_flow.expenses['Management Fee'] == Money(2000) * Percentage(10) / 100
        assert 'CapEx' in cash_flow.expenses
        assert cash_flow.expenses['CapEx'] == Money(2000) * Percentage(5) / 100
        assert 'Vacancy' in cash_flow.expenses
        assert cash_flow.expenses['Vacancy'] == Money(2000) * Percentage(5) / 100
        assert 'Repairs' in cash_flow.expenses
        assert cash_flow.expenses['Repairs'] == Money(2000) * Percentage(5) / 100
        
        # Verify loan payments
        assert 'Initial Loan' in cash_flow.loan_payments
        loan = LoanDetails(
            amount=Money(240000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False
        )
        expected_payment = loan.calculate_payment().total
        assert cash_flow.loan_payments['Initial Loan'] == expected_payment
        
        # Verify net cash flow
        expected_net_cash_flow = cash_flow.total_income - cash_flow.total_expenses - cash_flow.total_loan_payments
        assert cash_flow.net_cash_flow == expected_net_cash_flow
    
    def test_calculate_detailed_cash_flow_with_additional_income(self):
        """Test calculating detailed cash flow with additional income sources."""
        # Test data
        data = {
            'monthly_rent': 2000,
            'parking_income': 100,
            'laundry_income': 50,
            'storage_income': 75,
            'other_income': 25,
            'property_taxes': 2400,
            'insurance': 1200
        }
        
        # Calculate cash flow
        cash_flow = FinancialCalculator.calculate_detailed_cash_flow(data)
        
        # Verify income
        assert 'Monthly Rent' in cash_flow.income
        assert cash_flow.income['Monthly Rent'] == Money(2000)
        assert 'Parking Income' in cash_flow.income
        assert cash_flow.income['Parking Income'] == Money(100)
        assert 'Laundry Income' in cash_flow.income
        assert cash_flow.income['Laundry Income'] == Money(50)
        assert 'Storage Income' in cash_flow.income
        assert cash_flow.income['Storage Income'] == Money(75)
        assert 'Other Income' in cash_flow.income
        assert cash_flow.income['Other Income'] == Money(25)
        assert cash_flow.total_income == Money(2000 + 100 + 50 + 75 + 25)
    
    def test_calculate_detailed_cash_flow_with_multifamily_expenses(self):
        """Test calculating detailed cash flow with multi-family specific expenses."""
        # Test data
        data = {
            'analysis_type': 'MultiFamily',
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'common_area_maintenance': 300,
            'elevator_maintenance': 200,
            'staff_payroll': 500,
            'security': 150
        }
        
        # Calculate cash flow
        cash_flow = FinancialCalculator.calculate_detailed_cash_flow(data)
        
        # Verify multi-family specific expenses
        assert 'Common Area Maintenance' in cash_flow.expenses
        assert cash_flow.expenses['Common Area Maintenance'] == Money(300)
        assert 'Elevator Maintenance' in cash_flow.expenses
        assert cash_flow.expenses['Elevator Maintenance'] == Money(200)
        assert 'Staff Payroll' in cash_flow.expenses
        assert cash_flow.expenses['Staff Payroll'] == Money(500)
        assert 'Security' in cash_flow.expenses
        assert cash_flow.expenses['Security'] == Money(150)
    
    def test_calculate_balloon_payment_analysis(self):
        """Test calculating balloon payment analysis."""
        # Test data
        data = {
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'initial_loan_amount': 240000,
            'initial_loan_interest_rate': 4.5,
            'initial_loan_term': 360,
            'has_balloon_payment': True,
            'balloon_term_months': 60,
            'balloon_refinance_ltv_percentage': 75,
            'balloon_refinance_interest_rate': 5.0,
            'balloon_refinance_term': 360,
            'property_value': 300000,
            'appreciation_rate': 3,
            'start_date': '2025-01-01'
        }
        
        # Calculate balloon payment analysis
        balloon_analysis = FinancialCalculator.calculate_balloon_payment_analysis(data)
        
        # Verify balloon payment details
        assert balloon_analysis is not None
        assert balloon_analysis.balloon_term_months == 60
        
        # Verify balloon date
        expected_balloon_date = date(2030, 1, 1)  # Approximate
        assert balloon_analysis.balloon_date is not None
        
        # Verify balloon amount
        initial_loan = LoanDetails(
            amount=Money(240000),
            interest_rate=Percentage(4.5),
            term=360,
            is_interest_only=False
        )
        expected_balloon_amount = initial_loan.calculate_remaining_balance(60)
        assert balloon_analysis.balloon_amount == expected_balloon_amount
        
        # Verify refinance loan details
        assert balloon_analysis.refinance_loan_details is not None
        assert balloon_analysis.refinance_loan_details.interest_rate == Percentage(5.0)
        assert balloon_analysis.refinance_loan_details.term == 360
        
        # Verify pre and post balloon cash flows
        assert balloon_analysis.pre_balloon_cash_flow is not None
        assert balloon_analysis.post_balloon_cash_flow is not None
    
    def test_calculate_lease_option_details(self):
        """Test calculating lease option details."""
        # Test data
        data = {
            'analysis_type': 'LeaseOption',
            'monthly_rent': 2000,
            'monthly_rent_credit': 500,
            'option_term_months': 24,
            'strike_price': 300000,
            'option_consideration_fee': 5000
        }
        
        # Calculate lease option details
        lease_option = FinancialCalculator.calculate_lease_option_details(data)
        
        # Verify lease option details
        assert lease_option is not None
        assert lease_option.monthly_rent == Money(2000)
        assert lease_option.monthly_rent_credit == Money(500)
        assert lease_option.option_term_months == 24
        assert lease_option.strike_price == Money(300000)
        assert lease_option.option_consideration_fee == Money(5000)
        
        # Verify calculated values
        assert lease_option.total_rent_credits == Money(500 * 24)
        assert lease_option.effective_purchase_price == Money(300000 - (500 * 24) - 5000)
    
    def test_calculate_refinance_impact(self):
        """Test calculating refinance impact."""
        # Test data
        data = {
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'initial_loan_amount': 240000,
            'initial_loan_interest_rate': 4.5,
            'initial_loan_term': 360,
            'refinance_loan_amount': 250000,
            'refinance_loan_interest_rate': 3.75,
            'refinance_loan_term': 360,
            'refinance_closing_costs': 5000,
            'payments_made': 60
        }
        
        # Calculate refinance impact
        refinance_analysis = FinancialCalculator.calculate_refinance_impact(data)
        
        # Verify refinance impact details
        assert refinance_analysis is not None
        assert refinance_analysis.closing_costs == Money(5000)
        assert refinance_analysis.cash_out_amount == Money(250000 - 240000)
        
        # Verify new loan details
        assert refinance_analysis.new_loan_details is not None
        assert refinance_analysis.new_loan_details.amount == Money(250000)
        assert refinance_analysis.new_loan_details.interest_rate == Percentage(3.75)
        assert refinance_analysis.new_loan_details.term == 360
        
        # Verify cash flow and savings
        assert refinance_analysis.pre_refinance_cash_flow is not None
        assert refinance_analysis.post_refinance_cash_flow is not None
        assert refinance_analysis.monthly_savings is not None
        assert refinance_analysis.annual_savings == refinance_analysis.monthly_savings * 12
        
        # Verify break-even calculation
        if refinance_analysis.monthly_savings.dollars > 0:
            expected_break_even = 5000 / refinance_analysis.monthly_savings.dollars
            assert refinance_analysis.break_even_months == expected_break_even
