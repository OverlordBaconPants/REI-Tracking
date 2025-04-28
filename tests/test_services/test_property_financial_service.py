"""
Test module for the property financial service.

This module provides tests for the property financial service, including equity tracking,
cash flow calculations, and comparison of actual performance to analysis projections.
"""

import unittest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import datetime, date, timedelta

from src.models.property import Property, MonthlyIncome, MonthlyExpenses, Utilities, Loan, Partner
from src.models.transaction import Transaction
from src.models.analysis import Analysis
from src.services.property_financial_service import PropertyFinancialService


class TestPropertyFinancialService(unittest.TestCase):
    """Test case for the property financial service."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = PropertyFinancialService()
        
        # Mock repositories and services
        self.service.transaction_repo = MagicMock()
        self.service.property_repo = MagicMock()
        self.service.property_access_service = MagicMock()
        
        # Create test property
        self.test_property = Property(
            id="prop123",
            address="123 Test St",
            purchase_price=Decimal("200000"),
            purchase_date="2023-01-01",
            monthly_income=MonthlyIncome(
                rental_income=Decimal("0"),
                parking_income=Decimal("0"),
                laundry_income=Decimal("0"),
                other_income=Decimal("0")
            ),
            monthly_expenses=MonthlyExpenses(
                property_tax=Decimal("0"),
                insurance=Decimal("0"),
                repairs=Decimal("0"),
                capex=Decimal("0"),
                property_management=Decimal("0"),
                hoa_fees=Decimal("0"),
                utilities=Utilities(
                    water=Decimal("0"),
                    electricity=Decimal("0"),
                    gas=Decimal("0"),
                    trash=Decimal("0")
                )
            )
        )
        
        # Create test transactions
        self.test_transactions = [
            Transaction(
                id="trans1",
                property_id="prop123",
                type="income",
                category="Rental Income",
                description="January rent",
                amount=Decimal("1500"),
                date="2023-01-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans2",
                property_id="prop123",
                type="income",
                category="Parking Income",
                description="January parking",
                amount=Decimal("100"),
                date="2023-01-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans3",
                property_id="prop123",
                type="expense",
                category="Property Tax",
                description="Annual property tax",
                amount=Decimal("2400"),
                date="2023-01-15",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans4",
                property_id="prop123",
                type="expense",
                category="Insurance",
                description="Annual insurance",
                amount=Decimal("1200"),
                date="2023-01-20",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans5",
                property_id="prop123",
                type="expense",
                category="Water",
                description="January water bill",
                amount=Decimal("50"),
                date="2023-01-25",
                collector_payer="Owner"
            )
        ]
    
    def test_update_property_financials(self):
        """Test updating property financials."""
        # Set up mocks
        self.service.property_repo.get_by_id.return_value = self.test_property
        self.service.transaction_repo.get_by_property.return_value = self.test_transactions
        self.service.property_repo.update.return_value = self.test_property
        
        # Call the method
        result = self.service.update_property_financials("prop123")
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "prop123")
        
        # Verify the mocks were called correctly
        self.service.property_repo.get_by_id.assert_called_once_with("prop123")
        self.service.transaction_repo.get_by_property.assert_called_once_with("prop123")
        self.service.property_repo.update.assert_called_once()
    
    def test_update_property_income(self):
        """Test updating property income."""
        # Set up property
        property_obj = self.test_property
        
        # Call the method
        self.service._update_property_income(property_obj, self.test_transactions)
        
        # Verify the income was updated correctly
        self.assertEqual(property_obj.monthly_income.rental_income, Decimal("1500"))
        self.assertEqual(property_obj.monthly_income.parking_income, Decimal("100"))
        self.assertEqual(property_obj.monthly_income.laundry_income, Decimal("0"))
        self.assertEqual(property_obj.monthly_income.other_income, Decimal("0"))
        self.assertIn("January rent", property_obj.monthly_income.income_notes)
        self.assertIn("January parking", property_obj.monthly_income.income_notes)
    
    def test_update_property_expenses(self):
        """Test updating property expenses."""
        # Set up property
        property_obj = self.test_property
        
        # Call the method
        self.service._update_property_expenses(property_obj, self.test_transactions)
        
        # Verify the expenses were updated correctly
        self.assertEqual(property_obj.monthly_expenses.property_tax, Decimal("2400"))
        self.assertEqual(property_obj.monthly_expenses.insurance, Decimal("1200"))
        self.assertEqual(property_obj.monthly_expenses.repairs, Decimal("0"))
        self.assertEqual(property_obj.monthly_expenses.capex, Decimal("0"))
        self.assertEqual(property_obj.monthly_expenses.property_management, Decimal("0"))
        self.assertEqual(property_obj.monthly_expenses.hoa_fees, Decimal("0"))
        
        # Verify utilities were updated correctly
        self.assertEqual(property_obj.monthly_expenses.utilities.water, Decimal("50"))
        self.assertEqual(property_obj.monthly_expenses.utilities.electricity, Decimal("0"))
        self.assertEqual(property_obj.monthly_expenses.utilities.gas, Decimal("0"))
        self.assertEqual(property_obj.monthly_expenses.utilities.trash, Decimal("0"))
        
        # Verify notes were updated
        self.assertIn("Annual property tax", property_obj.monthly_expenses.expense_notes)
        self.assertIn("Annual insurance", property_obj.monthly_expenses.expense_notes)
        self.assertIn("January water bill", property_obj.monthly_expenses.expense_notes)
    
    def test_get_property_financial_summary(self):
        """Test getting property financial summary."""
        # Set up mocks
        self.service.property_access_service.can_access_property.return_value = True
        self.service.property_repo.get_by_id.return_value = self.test_property
        self.service.transaction_repo.get_by_property.return_value = self.test_transactions
        
        # Update property financials for the test
        self.service._update_property_income(self.test_property, self.test_transactions)
        self.service._update_property_expenses(self.test_property, self.test_transactions)
        
        # Call the method
        result = self.service.get_property_financial_summary("prop123", "user123")
        
        # Verify the result
        self.assertEqual(result["property_id"], "prop123")
        self.assertEqual(result["address"], "123 Test St")
        self.assertEqual(result["income_total"], str(Decimal("1600")))  # 1500 + 100
        self.assertEqual(result["expense_total"], str(Decimal("3650")))  # 2400 + 1200 + 50
        self.assertEqual(result["net_cash_flow"], str(Decimal("-2050")))  # 1600 - 3650
        self.assertEqual(result["utility_total"], str(Decimal("50")))  # water bill
        
        # Verify the mocks were called correctly
        self.service.property_access_service.can_access_property.assert_called_once_with("user123", "prop123")
        self.service.property_repo.get_by_id.assert_called_once_with("prop123")
        self.service.transaction_repo.get_by_property.assert_called_once_with("prop123")
    
    def test_get_property_financial_summary_no_access(self):
        """Test getting property financial summary with no access."""
        # Set up mocks
        self.service.property_access_service.can_access_property.return_value = False
        
        # Call the method and verify it raises an exception
        with self.assertRaises(ValueError):
            self.service.get_property_financial_summary("prop123", "user123")
        
        # Verify the mocks were called correctly
        self.service.property_access_service.can_access_property.assert_called_once_with("user123", "prop123")
    
    def test_get_all_property_financials(self):
        """Test getting all property financials."""
        # Set up mocks
        self.service.property_access_service.get_accessible_properties.return_value = [self.test_property]
        self.service.transaction_repo.get_by_property.return_value = self.test_transactions
        
        # Update property financials for the test
        self.service._update_property_income(self.test_property, self.test_transactions)
        self.service._update_property_expenses(self.test_property, self.test_transactions)
        
        # Call the method
        result = self.service.get_all_property_financials("user123")
        
        # Verify the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["property_id"], "prop123")
        self.assertEqual(result[0]["address"], "123 Test St")
        
        # Verify the mocks were called correctly
        self.service.property_access_service.get_accessible_properties.assert_called_once_with("user123")
        self.service.transaction_repo.get_by_property.assert_called_once_with("prop123")
    
    def test_update_all_property_financials(self):
        """Test updating all property financials."""
        # Set up mocks
        self.service.property_repo.get_all.return_value = [self.test_property]
        
        # Mock the update_property_financials method
        self.service.update_property_financials = MagicMock(return_value=self.test_property)
        
        # Call the method
        result = self.service.update_all_property_financials()
        
        # Verify the result
        self.assertEqual(result, 1)
        
        # Verify the mocks were called correctly
        self.service.property_repo.get_all.assert_called_once()
        self.service.update_property_financials.assert_called_once_with("prop123")
    
    def test_get_maintenance_and_capex_records(self):
        """Test getting maintenance and capex records."""
        # Set up mocks
        self.service.property_access_service.can_access_property.return_value = True
        self.service.property_repo.get_by_id.return_value = self.test_property
        
        # Create test maintenance and capex transactions
        maintenance_capex_transactions = [
            Transaction(
                id="trans6",
                property_id="prop123",
                type="expense",
                category="Repairs",
                description="Fix leaky faucet",
                amount=Decimal("150"),
                date="2023-02-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans7",
                property_id="prop123",
                type="expense",
                category="Capital Expenditures",
                description="New water heater",
                amount=Decimal("800"),
                date="2023-02-10",
                collector_payer="Owner"
            )
        ]
        
        self.service.transaction_repo.get_by_property.return_value = maintenance_capex_transactions
        
        # Call the method
        result = self.service.get_maintenance_and_capex_records("prop123", "user123")
        
        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "trans6")
        self.assertEqual(result[0]["category"], "Repairs")
        self.assertEqual(result[1]["id"], "trans7")
        self.assertEqual(result[1]["category"], "Capital Expenditures")
        
        # Verify the mocks were called correctly
        self.service.property_access_service.can_access_property.assert_called_once_with("user123", "prop123")
        self.service.property_repo.get_by_id.assert_called_once_with("prop123")
        self.service.transaction_repo.get_by_property.assert_called_once_with("prop123")


    def test_calculate_property_equity(self):
        """Test calculating property equity."""
        # Set up property with loans
        property_obj = self.test_property
        property_obj.purchase_date = "2023-01-01"
        property_obj.primary_loan = Loan(
            name="Primary Mortgage",
            amount=Decimal("160000"),
            interest_rate=Decimal("4.5"),
            term=360,  # 30 years
            start_date="2023-01-01"
        )
        property_obj.partners = [
            Partner(
                name="Partner 1",
                equity_share=Decimal("60"),
                is_property_manager=True
            ),
            Partner(
                name="Partner 2",
                equity_share=Decimal("40"),
                is_property_manager=False
            )
        ]
        
        # Set up mocks
        self.service.property_access_service.can_access_property.return_value = True
        self.service.property_repo.get_by_id.return_value = property_obj
        
        # Mock datetime.now() to return a fixed date for testing
        with patch('src.services.property_financial_service.date') as mock_date:
            mock_date.today.return_value = date(2024, 1, 1)  # 1 year after purchase
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
            
            # Call the method
            result = self.service.calculate_property_equity("prop123", "user123")
            
            # Verify the result
            self.assertEqual(result["property_id"], "prop123")
            self.assertEqual(result["address"], "123 Test St")
            self.assertEqual(result["purchase_price"], str(Decimal("200000")))
            self.assertEqual(result["months_owned"], 12)  # 1 year = 12 months
            
            # Verify loan balance calculation
            self.assertIn("total_loan_balance", result)
            
            # Verify equity calculations
            self.assertIn("initial_equity", result)
            self.assertIn("current_equity", result)
            self.assertIn("equity_gain", result)
            self.assertIn("equity_from_loan_paydown", result)
            self.assertIn("equity_from_appreciation", result)
            
            # Verify partner equity breakdown
            self.assertIn("partner_equity", result)
            self.assertEqual(len(result["partner_equity"]), 2)
            self.assertIn("Partner 1", result["partner_equity"])
            self.assertIn("Partner 2", result["partner_equity"])
            
            # Verify the mocks were called correctly
            self.service.property_access_service.can_access_property.assert_called_once_with("user123", "prop123")
            self.service.property_repo.get_by_id.assert_called_once_with("prop123")
    
    def test_calculate_loan_balance(self):
        """Test calculating loan balance."""
        # Test case 1: Zero interest loan
        balance1 = self.service._calculate_loan_balance(
            Decimal("100000"),  # loan amount
            Decimal("0"),       # interest rate
            120,                # term (10 years)
            60                  # months elapsed (5 years)
        )
        self.assertEqual(balance1, Decimal("50000"))  # Should be half paid off
        
        # Test case 2: Regular loan
        balance2 = self.service._calculate_loan_balance(
            Decimal("100000"),  # loan amount
            Decimal("4.5"),     # interest rate
            360,                # term (30 years)
            120                 # months elapsed (10 years)
        )
        self.assertTrue(Decimal("80000") < balance2 < Decimal("90000"))  # Approximate check
        
        # Test case 3: Loan fully paid off
        balance3 = self.service._calculate_loan_balance(
            Decimal("100000"),  # loan amount
            Decimal("4.5"),     # interest rate
            360,                # term (30 years)
            360                 # months elapsed (30 years)
        )
        self.assertEqual(balance3, Decimal("0"))
        
        # Test case 4: No payments made yet
        balance4 = self.service._calculate_loan_balance(
            Decimal("100000"),  # loan amount
            Decimal("4.5"),     # interest rate
            360,                # term (30 years)
            0                   # months elapsed (0 years)
        )
        self.assertEqual(balance4, Decimal("100000"))
    
    def test_calculate_monthly_payment(self):
        """Test calculating monthly payment."""
        # Test case 1: Zero interest loan
        payment1 = self.service._calculate_monthly_payment(
            Decimal("120000"),  # loan amount
            Decimal("0"),       # interest rate
            120                 # term (10 years)
        )
        self.assertEqual(payment1, Decimal("1000"))  # $120,000 / 120 months = $1,000/month
        
        # Test case 2: Regular loan
        payment2 = self.service._calculate_monthly_payment(
            Decimal("200000"),  # loan amount
            Decimal("4.5"),     # interest rate
            360                 # term (30 years)
        )
        self.assertTrue(Decimal("1000") < payment2 < Decimal("1100"))  # Approximate check
    
    def test_calculate_cash_flow_metrics(self):
        """Test calculating cash flow metrics."""
        # Set up mocks
        self.service.property_access_service.can_access_property.return_value = True
        self.service.property_repo.get_by_id.return_value = self.test_property
        
        # Create test transactions
        transactions = [
            Transaction(
                id="trans1",
                property_id="prop123",
                type="income",
                category="Rental Income",
                description="January rent",
                amount=Decimal("1500"),
                date="2023-01-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans2",
                property_id="prop123",
                type="expense",
                category="Property Tax",
                description="Property tax payment",
                amount=Decimal("200"),
                date="2023-01-15",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans3",
                property_id="prop123",
                type="expense",
                category="Insurance",
                description="Insurance payment",
                amount=Decimal("100"),
                date="2023-01-20",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans4",
                property_id="prop123",
                type="expense",
                category="Mortgage",
                description="Mortgage payment",
                amount=Decimal("800"),
                date="2023-01-25",
                collector_payer="Owner"
            )
        ]
        self.service.transaction_repo.get_by_property.return_value = transactions
        
        # Mock the filter and calculation methods
        original_filter = self.service._filter_transactions_by_date
        original_calculate = self.service._calculate_monthly_metrics
        original_compute = self.service._compute_cash_flow_metrics
        
        self.service._filter_transactions_by_date = MagicMock(return_value=transactions)
        self.service._calculate_monthly_metrics = MagicMock(return_value={
            'avg_monthly_income': Decimal('1500'),
            'avg_monthly_expenses': Decimal('300'),  # Property Tax + Insurance
            'avg_monthly_mortgage': Decimal('800'),
            'avg_monthly_noi': Decimal('1200')  # Income - Expenses
        })
        self.service._compute_cash_flow_metrics = MagicMock(return_value={
            'net_operating_income': {
                'monthly': '1200',
                'annual': '14400'
            },
            'total_income': {
                'monthly': '1500',
                'annual': '18000'
            },
            'total_expenses': {
                'monthly': '300',
                'annual': '3600'
            },
            'cash_flow': {
                'monthly': '400',
                'annual': '4800'
            },
            'cap_rate': '7.2',
            'cash_on_cash_return': '12.0',
            'debt_service_coverage_ratio': '1.5',
            'cash_invested': '40000',
            'metadata': {
                'has_complete_history': True,
                'data_quality': {
                    'confidence_level': 'high',
                    'refinance_info': {
                        'has_refinanced': False,
                        'original_debt_service': '800',
                        'current_debt_service': '800'
                    }
                }
            }
        })
        
        try:
            # Call the method with date parameters to trigger the filter
            result = self.service.calculate_cash_flow_metrics("prop123", "user123", start_date="2023-01-01", end_date="2023-01-31")
            
            # Verify the result
            self.assertIn('net_operating_income', result)
            self.assertIn('total_income', result)
            self.assertIn('total_expenses', result)
            self.assertIn('cash_flow', result)
            self.assertIn('cap_rate', result)
            self.assertIn('cash_on_cash_return', result)
            self.assertIn('debt_service_coverage_ratio', result)
            self.assertIn('metadata', result)
            
            # Verify the mocks were called correctly
            self.service.property_access_service.can_access_property.assert_called_once_with("user123", "prop123")
            self.service.property_repo.get_by_id.assert_called_once_with("prop123")
            self.service.transaction_repo.get_by_property.assert_called_once_with("prop123")
            self.service._filter_transactions_by_date.assert_called_once()
            self.service._calculate_monthly_metrics.assert_called_once()
            self.service._compute_cash_flow_metrics.assert_called_once()
        finally:
            # Restore original methods
            self.service._filter_transactions_by_date = original_filter
            self.service._calculate_monthly_metrics = original_calculate
            self.service._compute_cash_flow_metrics = original_compute
    
    def test_filter_transactions_by_date(self):
        """Test filtering transactions by date."""
        # Create test transactions
        transactions = [
            Transaction(
                id="trans1",
                property_id="prop123",
                type="income",
                category="Rental Income",
                description="January rent",
                amount=Decimal("1500"),
                date="2023-01-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans2",
                property_id="prop123",
                type="income",
                category="Rental Income",
                description="February rent",
                amount=Decimal("1500"),
                date="2023-02-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans3",
                property_id="prop123",
                type="income",
                category="Rental Income",
                description="March rent",
                amount=Decimal("1500"),
                date="2023-03-05",
                collector_payer="Owner"
            )
        ]
        
        # Test case 1: No date filters
        filtered1 = self.service._filter_transactions_by_date(transactions)
        self.assertEqual(len(filtered1), 3)
        
        # Test case 2: Start date only
        filtered2 = self.service._filter_transactions_by_date(transactions, start_date="2023-02-01")
        self.assertEqual(len(filtered2), 2)
        self.assertEqual(filtered2[0].date, "2023-02-05")
        self.assertEqual(filtered2[1].date, "2023-03-05")
        
        # Test case 3: End date only
        filtered3 = self.service._filter_transactions_by_date(transactions, end_date="2023-02-28")
        self.assertEqual(len(filtered3), 2)
        self.assertEqual(filtered3[0].date, "2023-01-05")
        self.assertEqual(filtered3[1].date, "2023-02-05")
        
        # Test case 4: Both start and end date
        filtered4 = self.service._filter_transactions_by_date(transactions, start_date="2023-01-15", end_date="2023-02-28")
        self.assertEqual(len(filtered4), 1)
        self.assertEqual(filtered4[0].date, "2023-02-05")
    
    def test_calculate_monthly_metrics(self):
        """Test calculating monthly metrics."""
        # Create test transactions
        transactions = [
            # January
            Transaction(
                id="trans1",
                property_id="prop123",
                type="income",
                category="Rental Income",
                description="January rent",
                amount=Decimal("1500"),
                date="2023-01-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans2",
                property_id="prop123",
                type="expense",
                category="Property Tax",
                description="January property tax",
                amount=Decimal("200"),
                date="2023-01-15",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans3",
                property_id="prop123",
                type="expense",
                category="Mortgage",
                description="January mortgage payment",
                amount=Decimal("800"),
                date="2023-01-25",
                collector_payer="Owner"
            ),
            # February
            Transaction(
                id="trans4",
                property_id="prop123",
                type="income",
                category="Rental Income",
                description="February rent",
                amount=Decimal("1500"),
                date="2023-02-05",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans5",
                property_id="prop123",
                type="expense",
                category="Property Tax",
                description="February property tax",
                amount=Decimal("200"),
                date="2023-02-15",
                collector_payer="Owner"
            ),
            Transaction(
                id="trans6",
                property_id="prop123",
                type="expense",
                category="Mortgage",
                description="February mortgage payment",
                amount=Decimal("800"),
                date="2023-02-25",
                collector_payer="Owner"
            )
        ]
        
        # Call the method
        result = self.service._calculate_monthly_metrics(transactions)
        
        # Verify the result
        self.assertEqual(result['avg_monthly_income'], Decimal('1500'))
        self.assertEqual(result['avg_monthly_expenses'], Decimal('200'))
        self.assertEqual(result['avg_monthly_mortgage'], Decimal('800'))
        self.assertEqual(result['avg_monthly_noi'], Decimal('1300'))  # Income - Expenses
    
    def test_compare_actual_to_projected(self):
        """Test comparing actual performance to analysis projections."""
        # Set up mocks
        self.service.property_access_service.can_access_property.return_value = True
        self.service.property_repo.get_by_id.return_value = self.test_property
        
        # Mock the calculate_cash_flow_metrics method
        self.service.calculate_cash_flow_metrics = MagicMock(return_value={
            'net_operating_income': {
                'monthly': '1200',
                'annual': '14400'
            },
            'total_income': {
                'monthly': '1500',
                'annual': '18000'
            },
            'total_expenses': {
                'monthly': '300',
                'annual': '3600'
            },
            'cash_flow': {
                'monthly': '400',
                'annual': '4800'
            },
            'cap_rate': '7.2',
            'cash_on_cash_return': '12.0',
            'debt_service_coverage_ratio': '1.5'
        })
        
        # Mock the _get_analyses_for_property method
        test_analysis = Analysis(
            id="analysis123",
            user_id="user123",
            analysis_type="LTR",
            analysis_name="Test Analysis",
            address="123 Test St",
            purchase_price=200000,
            monthly_rent=1600,
            property_taxes=2400,
            insurance=1200,
            management_fee_percentage=10.0,
            capex_percentage=5.0,
            vacancy_percentage=5.0,
            repairs_percentage=5.0,
            initial_loan_amount=160000,
            initial_loan_interest_rate=4.5,
            initial_loan_term=360
        )
        self.service._get_analyses_for_property = MagicMock(return_value=[test_analysis])
        
        # Mock the _calculate_projected_metrics method
        self.service._calculate_projected_metrics = MagicMock(return_value={
            'net_operating_income': {
                'monthly': '1280',
                'annual': '15360'
            },
            'total_income': {
                'monthly': '1600',
                'annual': '19200'
            },
            'total_expenses': {
                'monthly': '320',
                'annual': '3840'
            },
            'cash_flow': {
                'monthly': '450',
                'annual': '5400'
            },
            'cap_rate': '7.68',
            'cash_on_cash_return': '13.5',
            'debt_service_coverage_ratio': '1.6'
        })
        
        # Mock the _compare_metrics method
        self.service._compare_metrics = MagicMock(return_value={
            'income': {
                'monthly_variance': '-100',
                'monthly_variance_percentage': '-6.25',
                'is_better_than_projected': False
            },
            'expenses': {
                'monthly_variance': '-20',
                'monthly_variance_percentage': '-6.25',
                'is_better_than_projected': True
            },
            'noi': {
                'monthly_variance': '-80',
                'monthly_variance_percentage': '-6.25',
                'is_better_than_projected': False
            },
            'cash_flow': {
                'monthly_variance': '-50',
                'monthly_variance_percentage': '-11.11',
                'is_better_than_projected': False
            },
            'overall': {
                'performance_score': 25.0,
                'metrics_better_than_projected': 1,
                'total_metrics_compared': 4,
                'is_better_than_projected': False
            }
        })
        
        # Call the method
        result = self.service.compare_actual_to_projected("prop123", "user123")
        
        # Verify the result
        self.assertEqual(result['property_id'], "prop123")
        self.assertEqual(result['address'], "123 Test St")
        self.assertIn('actual_metrics', result)
        self.assertIn('projected_metrics', result)
        self.assertIn('comparison', result)
        self.assertIn('analysis_details', result)
        self.assertEqual(result['analysis_details']['id'], "analysis123")
        self.assertEqual(result['analysis_details']['name'], "Test Analysis")
        self.assertEqual(result['analysis_details']['type'], "LTR")
        
        # Verify the mocks were called correctly
        self.service.property_access_service.can_access_property.assert_called_once_with("user123", "prop123")
        self.service.property_repo.get_by_id.assert_called_once_with("prop123")
        self.service.calculate_cash_flow_metrics.assert_called_once_with("prop123", "user123")
        self.service._get_analyses_for_property.assert_called_once_with("prop123", "user123")
        self.service._calculate_projected_metrics.assert_called_once_with(test_analysis)
        self.service._compare_metrics.assert_called_once()


if __name__ == '__main__':
    unittest.main()
