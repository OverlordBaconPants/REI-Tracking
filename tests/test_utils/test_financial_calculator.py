import pytest
from decimal import Decimal
from utils.financial_calculator import FinancialCalculator
from utils.money import Money, Percentage, MonthlyPayment


class TestFinancialCalculator:
    """Test suite for the FinancialCalculator class."""

    def test_calculate_loan_payment_standard(self):
        """Test standard loan payment calculation."""
        # Test with Money and Percentage objects
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(100000),
            annual_rate=Percentage(5),
            term=360  # 30 years
        )
        
        assert isinstance(payment, MonthlyPayment)
        assert round(payment.total.dollars, 2) == 536.82
        assert payment.principal.dollars < payment.total.dollars
        assert payment.interest.dollars < payment.total.dollars
        assert round(payment.principal.dollars + payment.interest.dollars, 2) == round(payment.total.dollars, 2)

        # Test with numeric values
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=200000,
            annual_rate=4.5,
            term=180  # 15 years
        )
        
        assert isinstance(payment, MonthlyPayment)
        assert round(payment.total.dollars, 2) == 1529.99
        assert payment.principal.dollars < payment.total.dollars
        assert payment.interest.dollars < payment.total.dollars
        assert round(payment.principal.dollars + payment.interest.dollars, 2) == round(payment.total.dollars, 2)

    def test_calculate_loan_payment_interest_only(self):
        """Test interest-only loan payment calculation."""
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(300000),
            annual_rate=Percentage(6),
            term=360,  # 30 years
            is_interest_only=True
        )
        
        assert isinstance(payment, MonthlyPayment)
        assert round(payment.total.dollars, 2) == 1500.00
        assert payment.principal.dollars == 0
        assert payment.interest.dollars == payment.total.dollars

    def test_calculate_loan_payment_zero_interest(self):
        """Test loan payment calculation with zero interest rate."""
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(120000),
            annual_rate=Percentage(0),
            term=120  # 10 years
        )
        
        assert isinstance(payment, MonthlyPayment)
        assert round(payment.total.dollars, 2) == 1000.00
        assert payment.principal.dollars == payment.total.dollars
        assert payment.interest.dollars == 0

    def test_calculate_loan_payment_edge_cases(self):
        """Test loan payment calculation with edge cases."""
        # Zero loan amount
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(0),
            annual_rate=Percentage(5),
            term=360
        )
        
        assert payment.total.dollars == 0
        assert payment.principal.dollars == 0
        assert payment.interest.dollars == 0

        # Zero term
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(100000),
            annual_rate=Percentage(5),
            term=0
        )
        
        assert payment.total.dollars == 0
        assert payment.principal.dollars == 0
        assert payment.interest.dollars == 0

        # Invalid term (should be handled gracefully)
        payment = FinancialCalculator.calculate_loan_payment(
            loan_amount=Money(100000),
            annual_rate=Percentage(5),
            term="invalid"
        )
        
        assert payment.total.dollars == 0
        assert payment.principal.dollars == 0
        assert payment.interest.dollars == 0

    def test_calculate_cash_on_cash_return_standard(self):
        """Test standard cash-on-cash return calculation."""
        # Test with Money objects
        coc = FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(10000),
            total_investment=Money(100000)
        )
        
        assert isinstance(coc, Percentage)
        assert coc.value == 10.0

        # Test with numeric values
        coc = FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=5000,
            total_investment=50000
        )
        
        assert isinstance(coc, Percentage)
        assert coc.value == 10.0

    def test_calculate_cash_on_cash_return_edge_cases(self):
        """Test cash-on-cash return calculation with edge cases."""
        # Zero investment (should return "Infinite")
        coc = FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(10000),
            total_investment=Money(0)
        )
        
        assert coc == "Infinite"

        # Negative investment (should return "Infinite")
        coc = FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(10000),
            total_investment=Money(-5000)
        )
        
        assert coc == "Infinite"

        # Zero cash flow
        coc = FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(0),
            total_investment=Money(100000)
        )
        
        assert isinstance(coc, Percentage)
        assert coc.value == 0.0

        # Negative cash flow
        coc = FinancialCalculator.calculate_cash_on_cash_return(
            annual_cash_flow=Money(-5000),
            total_investment=Money(100000)
        )
        
        assert isinstance(coc, Percentage)
        assert coc.value == -5.0

    def test_calculate_cap_rate_standard(self):
        """Test standard cap rate calculation."""
        # Test with Money objects
        cap_rate = FinancialCalculator.calculate_cap_rate(
            annual_noi=Money(50000),
            property_value=Money(1000000)
        )
        
        assert isinstance(cap_rate, Percentage)
        assert cap_rate.value == 5.0

        # Test with numeric values
        cap_rate = FinancialCalculator.calculate_cap_rate(
            annual_noi=30000,
            property_value=500000
        )
        
        assert isinstance(cap_rate, Percentage)
        assert cap_rate.value == 6.0

    def test_calculate_cap_rate_edge_cases(self):
        """Test cap rate calculation with edge cases."""
        # Zero property value
        cap_rate = FinancialCalculator.calculate_cap_rate(
            annual_noi=Money(50000),
            property_value=Money(0)
        )
        
        assert isinstance(cap_rate, Percentage)
        assert cap_rate.value == 0.0

        # Zero NOI
        cap_rate = FinancialCalculator.calculate_cap_rate(
            annual_noi=Money(0),
            property_value=Money(1000000)
        )
        
        assert isinstance(cap_rate, Percentage)
        assert cap_rate.value == 0.0

        # Negative NOI
        cap_rate = FinancialCalculator.calculate_cap_rate(
            annual_noi=Money(-10000),
            property_value=Money(1000000)
        )
        
        assert isinstance(cap_rate, Percentage)
        assert cap_rate.value == -1.0

    def test_calculate_noi_standard(self):
        """Test standard NOI calculation."""
        # Test with Money objects
        noi = FinancialCalculator.calculate_noi(
            income=Money(100000),
            expenses=Money(40000)
        )
        
        assert isinstance(noi, Money)
        assert noi.dollars == 60000.0

        # Test with numeric values
        noi = FinancialCalculator.calculate_noi(
            income=50000,
            expenses=20000
        )
        
        assert isinstance(noi, Money)
        assert noi.dollars == 30000.0

    def test_calculate_noi_edge_cases(self):
        """Test NOI calculation with edge cases."""
        # Zero income
        noi = FinancialCalculator.calculate_noi(
            income=Money(0),
            expenses=Money(40000)
        )
        
        assert isinstance(noi, Money)
        assert noi.dollars == -40000.0

        # Zero expenses
        noi = FinancialCalculator.calculate_noi(
            income=Money(100000),
            expenses=Money(0)
        )
        
        assert isinstance(noi, Money)
        assert noi.dollars == 100000.0

        # Expenses greater than income
        noi = FinancialCalculator.calculate_noi(
            income=Money(50000),
            expenses=Money(70000)
        )
        
        assert isinstance(noi, Money)
        assert noi.dollars == -20000.0

    def test_calculate_dscr_standard(self):
        """Test standard DSCR calculation."""
        # Test with Money objects
        dscr = FinancialCalculator.calculate_dscr(
            noi=Money(60000),
            debt_service=Money(40000)
        )
        
        assert isinstance(dscr, float)
        assert dscr == 1.5

        # Test with numeric values
        dscr = FinancialCalculator.calculate_dscr(
            noi=30000,
            debt_service=20000
        )
        
        assert isinstance(dscr, float)
        assert dscr == 1.5

    def test_calculate_dscr_edge_cases(self):
        """Test DSCR calculation with edge cases."""
        # Zero debt service
        dscr = FinancialCalculator.calculate_dscr(
            noi=Money(60000),
            debt_service=Money(0)
        )
        
        assert dscr == 0
        assert dscr == 0

        # Zero NOI
        dscr = FinancialCalculator.calculate_dscr(
            noi=Money(0),
            debt_service=Money(40000)
        )
        
        assert isinstance(dscr, float)
        assert dscr == 0.0

        # Negative NOI
        dscr = FinancialCalculator.calculate_dscr(
            noi=Money(-10000),
            debt_service=Money(40000)
        )
        
        assert isinstance(dscr, float)
        assert dscr == -0.25

    def test_calculate_mao_standard(self):
        """Test standard MAO calculation."""
        # Test with Money and Percentage objects
        mao = FinancialCalculator.calculate_mao(
            arv=Money(200000),
            renovation_costs=Money(30000),
            closing_costs=Money(5000),
            holding_costs=Money(3000),
            ltv_percentage=Percentage(75),
            max_cash_left=Money(10000)
        )
        
        assert isinstance(mao, Money)
        assert mao.dollars == 102000.0  # 200000 * 0.75 - (30000 + 5000 + 3000 + 10000)

        # Test with numeric values
        mao = FinancialCalculator.calculate_mao(
            arv=300000,
            renovation_costs=50000,
            closing_costs=7000,
            holding_costs=5000,
            ltv_percentage=70,
            max_cash_left=15000
        )
        
        assert isinstance(mao, Money)
        assert mao.dollars == 133000.0  # 300000 * 0.7 - (50000 + 7000 + 5000 + 15000)

    def test_calculate_mao_edge_cases(self):
        """Test MAO calculation with edge cases."""
        # Zero ARV
        mao = FinancialCalculator.calculate_mao(
            arv=Money(0),
            renovation_costs=Money(30000),
            closing_costs=Money(5000),
            holding_costs=Money(3000),
            ltv_percentage=Percentage(75),
            max_cash_left=Money(10000)
        )
        
        assert isinstance(mao, Money)
        assert mao.dollars == 0.0  # Result would be negative, but capped at 0

        # High costs resulting in negative MAO (should be capped at 0)
        mao = FinancialCalculator.calculate_mao(
            arv=Money(100000),
            renovation_costs=Money(80000),
            closing_costs=Money(5000),
            holding_costs=Money(3000),
            ltv_percentage=Percentage(75),
            max_cash_left=Money(10000)
        )
        
        assert isinstance(mao, Money)
        assert mao.dollars == 0.0  # 100000 * 0.75 - (80000 + 5000 + 3000 + 10000) = -23000, capped at 0

    def test_calculate_expense_ratio_standard(self):
        """Test standard expense ratio calculation."""
        # Test with Money objects
        expense_ratio = FinancialCalculator.calculate_expense_ratio(
            expenses=Money(40000),
            income=Money(100000)
        )
        
        assert isinstance(expense_ratio, Percentage)
        assert expense_ratio.value == 40.0

        # Test with numeric values
        expense_ratio = FinancialCalculator.calculate_expense_ratio(
            expenses=20000,
            income=50000
        )
        
        assert isinstance(expense_ratio, Percentage)
        assert expense_ratio.value == 40.0

    def test_calculate_expense_ratio_edge_cases(self):
        """Test expense ratio calculation with edge cases."""
        # Zero income
        expense_ratio = FinancialCalculator.calculate_expense_ratio(
            expenses=Money(40000),
            income=Money(0)
        )
        
        assert isinstance(expense_ratio, Percentage)
        assert expense_ratio.value == 0.0

        # Zero expenses
        expense_ratio = FinancialCalculator.calculate_expense_ratio(
            expenses=Money(0),
            income=Money(100000)
        )
        
        assert isinstance(expense_ratio, Percentage)
        assert expense_ratio.value == 0.0

        # Expenses greater than income
        expense_ratio = FinancialCalculator.calculate_expense_ratio(
            expenses=Money(120000),
            income=Money(100000)
        )
        
        assert isinstance(expense_ratio, Percentage)
        assert expense_ratio.value == 120.0

    def test_calculate_gross_rent_multiplier_standard(self):
        """Test standard gross rent multiplier calculation."""
        # Test with Money objects
        grm = FinancialCalculator.calculate_gross_rent_multiplier(
            purchase_price=Money(500000),
            annual_rent=Money(50000)
        )
        
        assert isinstance(grm, float)
        assert grm == 10.0

        # Test with numeric values
        grm = FinancialCalculator.calculate_gross_rent_multiplier(
            purchase_price=300000,
            annual_rent=30000
        )
        
        assert isinstance(grm, float)
        assert grm == 10.0

    def test_calculate_gross_rent_multiplier_edge_cases(self):
        """Test gross rent multiplier calculation with edge cases."""
        # Zero annual rent
        grm = FinancialCalculator.calculate_gross_rent_multiplier(
            purchase_price=Money(500000),
            annual_rent=Money(0)
        )
        
        assert grm == 0
        assert grm == 0

        # Zero purchase price
        grm = FinancialCalculator.calculate_gross_rent_multiplier(
            purchase_price=Money(0),
            annual_rent=Money(50000)
        )
        
        assert isinstance(grm, float)
        assert grm == 0.0
