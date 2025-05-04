import unittest
import sys
import os
import json

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.analysis_schema import ANALYSIS_SCHEMA, MOBILE_OPTIONAL_FIELDS

class TestAnalysisSchema(unittest.TestCase):
    """Test cases for the analysis_schema module."""

    def test_schema_structure(self):
        """Test that the schema has the expected structure."""
        # Verify that the schema is a dictionary
        self.assertIsInstance(ANALYSIS_SCHEMA, dict)
        
        # Verify that the schema has the expected core fields
        core_fields = ['id', 'user_id', 'created_at', 'updated_at', 'analysis_type', 'analysis_name']
        for field in core_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_property_details_fields(self):
        """Test that the schema has the expected property details fields."""
        property_fields = ['address', 'property_type', 'square_footage', 'lot_size', 
                          'year_built', 'bedrooms', 'bathrooms']
        for field in property_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_comps_data_structure(self):
        """Test that the comps_data field has the expected structure."""
        self.assertIn('comps_data', ANALYSIS_SCHEMA)
        self.assertIsInstance(ANALYSIS_SCHEMA['comps_data'], dict)
        self.assertIn('type', ANALYSIS_SCHEMA['comps_data'])
        self.assertEqual(ANALYSIS_SCHEMA['comps_data']['type'], 'object')
        self.assertIn('properties', ANALYSIS_SCHEMA['comps_data'])
        
        # Check for expected comps_data properties
        comps_properties = ['last_run', 'estimated_value', 'value_range_low', 
                           'value_range_high', 'comparables']
        for prop in comps_properties:
            self.assertIn(prop, ANALYSIS_SCHEMA['comps_data']['properties'])
    
    def test_balloon_payment_fields(self):
        """Test that the schema has the expected balloon payment fields."""
        balloon_fields = ['has_balloon_payment', 'balloon_due_date', 
                         'balloon_refinance_ltv_percentage', 'balloon_refinance_loan_amount',
                         'balloon_refinance_loan_interest_rate', 'balloon_refinance_loan_term',
                         'balloon_refinance_loan_down_payment', 'balloon_refinance_loan_closing_costs']
        for field in balloon_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_purchase_details_fields(self):
        """Test that the schema has the expected purchase details fields."""
        purchase_fields = ['purchase_price', 'after_repair_value', 'renovation_costs',
                          'renovation_duration', 'cash_to_seller', 'closing_costs',
                          'assignment_fee', 'marketing_costs', 'furnishing_costs']
        for field in purchase_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_income_and_expense_fields(self):
        """Test that the schema has the expected income and expense fields."""
        income_expense_fields = ['monthly_rent', 'property_taxes', 'insurance', 'hoa_coa_coop',
                               'management_fee_percentage', 'capex_percentage',
                               'vacancy_percentage', 'repairs_percentage']
        for field in income_expense_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_padsplit_specific_fields(self):
        """Test that the schema has the expected PadSplit specific fields."""
        padsplit_fields = ['utilities', 'internet', 'cleaning', 'pest_control',
                          'landscaping', 'padsplit_platform_percentage']
        for field in padsplit_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_loan_fields(self):
        """Test that the schema has the expected loan fields."""
        # Test initial and refinance loan fields
        initial_refinance_fields = ['initial_loan_name', 'initial_loan_amount', 
                                  'initial_loan_interest_rate', 'initial_interest_only',
                                  'initial_loan_term', 'initial_loan_down_payment',
                                  'initial_loan_closing_costs', 'refinance_loan_name',
                                  'refinance_ltv_percentage', 'refinance_loan_amount',
                                  'refinance_loan_interest_rate', 'refinance_loan_term',
                                  'refinance_loan_down_payment', 'refinance_loan_closing_costs']
        for field in initial_refinance_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
        
        # Test loan1, loan2, loan3 fields
        for loan_num in range(1, 4):
            loan_fields = [f'loan{loan_num}_interest_only', f'loan{loan_num}_loan_name',
                          f'loan{loan_num}_loan_amount', f'loan{loan_num}_loan_interest_rate',
                          f'loan{loan_num}_loan_term', f'loan{loan_num}_loan_down_payment',
                          f'loan{loan_num}_loan_closing_costs']
            for field in loan_fields:
                self.assertIn(field, ANALYSIS_SCHEMA)
                self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
                self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_lease_option_fields(self):
        """Test that the schema has the expected lease option fields."""
        lease_option_fields = ['option_consideration_fee', 'option_term_months',
                              'strike_price', 'monthly_rent_credit_percentage',
                              'rent_credit_cap']
        for field in lease_option_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
            self.assertIn('optional', ANALYSIS_SCHEMA[field])
            self.assertFalse(ANALYSIS_SCHEMA[field]['optional'])
    
    def test_multi_family_fields(self):
        """Test that the schema has the expected multi-family fields."""
        multi_family_fields = ['total_units', 'occupied_units', 'floors',
                              'other_income', 'total_potential_income',
                              'common_area_maintenance', 'elevator_maintenance',
                              'staff_payroll', 'trash_removal', 'common_utilities',
                              'unit_types']
        for field in multi_family_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIsInstance(ANALYSIS_SCHEMA[field], dict)
            self.assertIn('type', ANALYSIS_SCHEMA[field])
    
    def test_mobile_optional_fields(self):
        """Test that MOBILE_OPTIONAL_FIELDS contains the expected fields."""
        self.assertIsInstance(MOBILE_OPTIONAL_FIELDS, list)
        expected_fields = ['lot_size', 'year_built', 'furnishing_costs', 
                          'other_income', 'elevator_maintenance']
        for field in expected_fields:
            self.assertIn(field, MOBILE_OPTIONAL_FIELDS)
        
        # Verify that all fields in MOBILE_OPTIONAL_FIELDS exist in ANALYSIS_SCHEMA
        for field in MOBILE_OPTIONAL_FIELDS:
            self.assertIn(field, ANALYSIS_SCHEMA)
    
    def test_field_types(self):
        """Test that field types are correctly specified."""
        # Test a sample of fields with different types
        type_tests = {
            'id': 'string',
            'purchase_price': 'integer',
            'management_fee_percentage': 'float',
            'initial_interest_only': 'boolean',
            'comps_data': 'object',
            'unit_types': 'string'  # JSON string of unit type array
        }
        
        for field, expected_type in type_tests.items():
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertEqual(ANALYSIS_SCHEMA[field]['type'], expected_type)
    
    def test_optional_fields(self):
        """Test that optional fields are correctly marked."""
        # Test a sample of optional fields
        optional_fields = ['property_type', 'square_footage', 'lot_size', 
                          'year_built', 'bedrooms', 'bathrooms', 'comps_data']
        
        for field in optional_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            self.assertIn('optional', ANALYSIS_SCHEMA[field])
            self.assertTrue(ANALYSIS_SCHEMA[field]['optional'])
        
        # Test a sample of required fields
        required_fields = ['id', 'user_id', 'analysis_type', 'analysis_name', 
                          'address', 'purchase_price']
        
        for field in required_fields:
            self.assertIn(field, ANALYSIS_SCHEMA)
            # Either 'optional' is not present, or it's explicitly set to False
            if 'optional' in ANALYSIS_SCHEMA[field]:
                self.assertFalse(ANALYSIS_SCHEMA[field]['optional'])

if __name__ == '__main__':
    unittest.main()
