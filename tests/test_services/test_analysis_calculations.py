import unittest
from decimal import Decimal
from utils.money import Money, Percentage, MonthlyPayment
from services.analysis_calculations import (
    Loan, OperatingExpenses, LTROperatingExpenses, PadSplitOperatingExpenses,
    BaseAnalysis, LongTermRentalAnalysis, BRRRRAnalysis, PadSplitLTRAnalysis,
    PadSplitBRRRRAnalysis, create_analysis
)

class TestLoan(unittest.TestCase):
    """Test suite for Loan class."""

    def setUp(self):
        """Set up test data."""
        self.loan_data = {
            'amount': Money(200000),
            'interest_rate': Percentage(4.5),
            'term_months': 360,
            'down_payment': Money(40000),
            'closing_costs': Money(3000),
            'name': 'Test Loan'
        }
        self.loan = Loan(**self.loan_data)

    def test_loan_initialization(self):
        """Test loan initialization with different input types."""
        # Test with raw numbers
        loan = Loan(200000, 4.5, 360, 40000, 3000)
        self.assertIsInstance(loan.amount, Money)
        self.assertIsInstance(loan.interest_rate, Percentage)
        self.assertIsInstance(loan.down_payment, Money)
        self.assertIsInstance(loan.closing_costs, Money)

        # Test with Money/Percentage objects
        loan = Loan(Money(200000), Percentage(4.5), 360, Money(40000), Money(3000))
        self.assertEqual(loan.amount, Money(200000))
        self.assertEqual(loan.interest_rate, Percentage(4.5))

    def test_calculate_payment(self):
        """Test monthly payment calculation."""
        payment = self.loan.calculate_payment()
        self.assertIsInstance(payment, MonthlyPayment)
        self.assertTrue(payment.total > Money(0))
        
        # Verify payment components
        self.assertTrue(payment.principal > Money(0))
        self.assertTrue(payment.interest > Money(0))
        self.assertEqual(payment.total, payment.principal + payment.interest)

    def test_total_initial_costs(self):
        """Test calculation of total initial costs."""
        total = self.loan.total_initial_costs()
        self.assertEqual(total, Money(43000))  # 40000 down + 3000 closing

class TestOperatingExpenses(unittest.TestCase):
    """Test suite for operating expenses calculations."""

    def setUp(self):
        """Set up test data."""
        self.base_expenses = OperatingExpenses(
            property_taxes=Money(2400),
            insurance=Money(1200),
            monthly_rent=Money(2000),
            management_percentage=Percentage(10),
            capex_percentage=Percentage(5),
            vacancy_percentage=Percentage(5)
        )
        
        self.ltr_expenses = LTROperatingExpenses(
            property_taxes=Money(2400),
            insurance=Money(1200),
            monthly_rent=Money(2000),
            management_percentage=Percentage(10),
            capex_percentage=Percentage(5),
            vacancy_percentage=Percentage(5),
            repairs_percentage=Percentage(5),
            hoa_coa_coop=Money(100)
        )
        
        self.padsplit_expenses = PadSplitOperatingExpenses(
            property_taxes=Money(2400),
            insurance=Money(1200),
            monthly_rent=Money(2000),
            management_percentage=Percentage(10),
            capex_percentage=Percentage(5),
            vacancy_percentage=Percentage(5),
            platform_percentage=Percentage(15),
            utilities=Money(200),
            internet=Money(50),
            cleaning_costs=Money(100),
            pest_control=Money(50),
            landscaping=Money(100)
        )

    def test_base_expense_calculations(self):
        """Test basic operating expense calculations."""
        self.assertEqual(self.base_expenses.calculate_management_fee(), Money(200))
        self.assertEqual(self.base_expenses.calculate_capex(), Money(100))
        self.assertEqual(self.base_expenses.calculate_vacancy(), Money(100))
        
        total = self.base_expenses.calculate_total()
        self.assertEqual(total, Money(4000))  # Sum of all expenses

    def test_ltr_expense_calculations(self):
        """Test long-term rental specific expenses."""
        self.assertEqual(self.ltr_expenses.calculate_repairs(), Money(100))
        
        total = self.ltr_expenses.calculate_total()
        self.assertTrue(total > self.base_expenses.calculate_total())
        self.assertEqual(total, Money(4200))  # Including repairs and HOA

    def test_padsplit_expense_calculations(self):
        """Test PadSplit specific expenses."""
        self.assertEqual(self.padsplit_expenses.calculate_platform_fee(), Money(300))
        
        total = self.padsplit_expenses.calculate_total()
        self.assertTrue(total > self.base_expenses.calculate_total())
        self.assertEqual(total, Money(4700))  # Including all PadSplit expenses

class TestAnalysisCalculations(unittest.TestCase):
    """Test suite for property analysis calculations."""

    def setUp(self):
        """Set up test data."""
        self.brrrr_data = {
            'analysis_type': 'BRRRR',
            'purchase_price': 200000,
            'after_repair_value': 250000,
            'renovation_costs': 30000,
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'management_percentage': 10,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'initial_loan_amount': 160000,
            'initial_interest_rate': 7.5,
            'initial_loan_term': 360,
            'initial_down_payment': 40000,
            'initial_closing_costs': 3000,
            'refinance_loan_amount': 187500,
            'refinance_interest_rate': 6.5,
            'refinance_loan_term': 360,
            'refinance_down_payment': 0,
            'refinance_closing_costs': 3000,
            'renovation_duration': 3,
            'refinance_ltv_percentage': 75,
            'max_cash_left': 10000
        }
        
        self.ltr_data = {
            'analysis_type': 'Long-Term Rental',
            'purchase_price': 200000,
            'after_repair_value': 200000,
            'renovation_costs': 0,
            'monthly_rent': 2000,
            'property_taxes': 2400,
            'insurance': 1200,
            'management_percentage': 10,
            'capex_percentage': 5,
            'vacancy_percentage': 5,
            'repairs_percentage': 5,
            'hoa_coa_coop': 100,
            'loans': {
                '1': {
                    'amount': 160000,
                    'interest_rate': 6.5,
                    'term': 360,
                    'down_payment': 40000,
                    'closing_costs': 3000
                }
            }
        }

    def test_brrrr_analysis(self):
        """Test BRRRR analysis calculations."""
        analysis = create_analysis(self.brrrr_data)
        
        # Test cash flow calculations
        monthly_cash_flow = analysis.calculate_monthly_cash_flow()
        self.assertIsInstance(monthly_cash_flow, Money)
        self.assertTrue(monthly_cash_flow > Money(0))
        
        # Test equity calculations
        equity_captured = analysis.calculate_equity_captured()
        self.assertEqual(equity_captured, Money(20000))  # ARV - total costs
        
        # Test cash recouped
        cash_recouped = analysis.calculate_cash_recouped()
        self.assertEqual(cash_recouped, Money(27500))  # Refinance - initial loan
        
        # Test MAO calculation
        mao = analysis.calculate_max_allowable_offer()
        self.assertIsInstance(mao, Money)
        self.assertTrue(mao > Money(0))

    def test_ltr_analysis(self):
        """Test long-term rental analysis calculations."""
        analysis = create_analysis(self.ltr_data)
        
        # Test cash flow calculations
        monthly_cash_flow = analysis.calculate_monthly_cash_flow()
        self.assertIsInstance(monthly_cash_flow, Money)
        
        # Test loan payment calculations
        total_loan_payment = analysis.calculate_total_loan_payment()
        self.assertTrue(total_loan_payment > Money(0))
        
        # Test investment calculations
        total_cash_invested = analysis.calculate_total_cash_invested()
        self.assertEqual(total_cash_invested, Money(43000))  # Down payment + closing costs

    def test_padsplit_analysis(self):
        """Test PadSplit analysis calculations."""
        # Modify data for PadSplit
        padsplit_data = self.brrrr_data.copy()
        padsplit_data['analysis_type'] = 'PadSplit BRRRR'
        padsplit_data.update({
            'padsplit_platform_percentage': 15,
            'utilities': 200,
            'internet': 50,
            'cleaning_costs': 100,
            'pest_control': 50,
            'landscaping': 100
        })
        
        analysis = create_analysis(padsplit_data)
        
        # Test PadSplit-specific expenses
        monthly_cash_flow = analysis.calculate_monthly_cash_flow()
        self.assertTrue(monthly_cash_flow < analysis.monthly_rent)
        
        # Verify platform fee is included
        platform_fee = analysis.operating_expenses.calculate_platform_fee()
        self.assertTrue(platform_fee > Money(0))

class TestEdgeCases(unittest.TestCase):
    """Test suite for edge cases and error handling."""

    def test_zero_values(self):
        """Test calculations with zero values."""
        loan = Loan(
            amount=Money(0),
            interest_rate=Percentage(4.5),
            term_months=360,
            down_payment=Money(0),
            closing_costs=Money(0)
        )
        self.assertEqual(loan.calculate_payment().total, Money(0))

    def test_invalid_analysis_type(self):
        """Test creating analysis with invalid type."""
        data = {'analysis_type': 'INVALID'}
        with self.assertRaises(ValueError):
            create_analysis(data)

    def test_negative_values(self):
        """Test handling of negative values."""
        with self.assertRaises(ValueError):
            Money(-1000)
        with self.assertRaises(ValueError):
            Percentage(-5)

    def test_missing_required_data(self):
        """Test analysis creation with missing data."""
        incomplete_data = {'analysis_type': 'BRRRR'}
        with self.assertRaises(Exception):
            create_analysis(incomplete_data)

if __name__ == '__main__':
    unittest.main()