# analysis_schema.py
"""Schema definition for property investment analyses."""


ANALYSIS_SCHEMA = {
    # Core fields
    'id': {'type': 'string', 'format': 'uuid'},
    'user_id': {'type': 'string'},
    'created_at': {'type': 'string', 'format': 'datetime'},
    'updated_at': {'type': 'string', 'format': 'datetime'},
    'analysis_type': {'type': 'string'},
    'analysis_name': {'type': 'string'},

    # Property details
    'address': {'type': 'string'},
    'property_type': {'type': 'string', 'optional': True, 
        'allowed_values': [
            'Single Family',
            'Condo',
            'Townhouse',
            'Manufactured',
            'Multi-Family'
        ]
    },
    'square_footage': {'type': 'integer', 'optional': True},
    'lot_size': {'type': 'integer', 'optional': True},
    'year_built': {'type': 'integer', 'optional': True},
    'bedrooms': {'type': 'integer', 'optional': True},
    'bathrooms': {'type': 'float', 'optional': True},

    # Comps data fields
    'comps_data': {
        'type': 'object',
        'optional': True,  # Not all analyses will have comps run
        'properties': {
            'last_run': {
                'type': 'string',
                'format': 'datetime',
                'optional': True,
                'description': 'ISO 8601 datetime when comps were last run'
            },
            'run_count': {
                'type': 'integer',
                'optional': True,
                'description': 'Number of times comps have been run in current session'
            },
            'estimated_value': {
                'type': 'integer',
                'optional': True,
                'description': 'Estimated value based on comps'
            },
            'value_range_low': {
                'type': 'integer',
                'optional': True,
                'description': 'Lower bound of estimated value range'
            },
            'value_range_high': {
                'type': 'integer',
                'optional': True,
                'description': 'Upper bound of estimated value range'
            },
            'comparables': {
                'type': 'array',
                'optional': True,
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                        'formattedAddress': {'type': 'string'},
                        'city': {'type': 'string'},
                        'state': {'type': 'string'},
                        'zipCode': {'type': 'string'},
                        'propertyType': {'type': 'string'},
                        'bedrooms': {'type': 'integer'},
                        'bathrooms': {'type': 'float'},
                        'squareFootage': {'type': 'integer'},
                        'yearBuilt': {'type': 'integer'},
                        'price': {'type': 'integer'},
                        'listingType': {'type': 'string'},
                        'listedDate': {
                            'type': 'string',
                            'format': 'datetime'
                        },
                        'removedDate': {
                            'type': 'string',
                            'format': 'datetime',
                            'optional': True
                        },
                        'daysOnMarket': {'type': 'integer'},
                        'distance': {'type': 'float'},
                        'correlation': {'type': 'float'}
                    }
                }
            }
        }
    },

    # Balloon Options
    'has_balloon_payment': {'type': 'boolean'},
    'balloon_due_date': {'type': 'string', 'format': 'date'},  # ISO format date
    'balloon_refinance_ltv_percentage': {'type': 'float'},
    'balloon_refinance_loan_amount': {'type': 'integer'},
    'balloon_refinance_loan_interest_rate': {'type': 'float'},
    'balloon_refinance_loan_term': {'type': 'integer'},
    'balloon_refinance_loan_down_payment': {'type': 'integer'},
    'balloon_refinance_loan_closing_costs': {'type': 'integer'},

    # Purchase details
    'purchase_price': {'type': 'integer'},
    'after_repair_value': {'type': 'integer'},
    'renovation_costs': {'type': 'integer'},
    'renovation_duration': {'type': 'integer'},
    'cash_to_seller': {'type': 'integer'},
    'closing_costs': {'type': 'integer'},
    'assignment_fee': {'type': 'integer'},
    'marketing_costs': {'type': 'integer'},
    'furnishing_costs': {'type': 'integer','optional': True},

    # Income
    'monthly_rent': {'type': 'integer'},

    # Operating expenses
    'property_taxes': {'type': 'integer'},
    'insurance': {'type': 'integer'},
    'hoa_coa_coop': {'type': 'integer'},
    'management_fee_percentage': {'type': 'float'},
    'capex_percentage': {'type': 'float'},
    'vacancy_percentage': {'type': 'float'},
    'repairs_percentage': {'type': 'float'},

    # Notes
    'notes': {
        'type': 'string',
        'maxLength': 1000,  # Limit to 1,000 characters
        'description': 'User notes about the analysis'
    },

    # PadSplit specific
    'utilities': {'type': 'integer'},
    'internet': {'type': 'integer'},
    'cleaning': {'type': 'integer'},
    'pest_control': {'type': 'integer'},
    'landscaping': {'type': 'integer'},
    'padsplit_platform_percentage': {'type': 'float'},

    # Loan fields
    'initial_loan_name': {'type': 'string'},
    'initial_loan_amount': {'type': 'integer'},
    'initial_loan_interest_rate': {'type': 'float'},
    'initial_interest_only': {'type': 'boolean'},
    'initial_loan_term': {'type': 'integer'},
    'initial_loan_down_payment': {'type': 'integer'},
    'initial_loan_closing_costs': {'type': 'integer'},

    'refinance_loan_name': {'type': 'string'},
    'refinance_ltv_percentage': {'type': 'float'},
    'refinance_loan_amount': {'type': 'integer'},
    'refinance_loan_interest_rate': {'type': 'float'},
    'refinance_loan_term': {'type': 'integer'},
    'refinance_loan_down_payment': {'type': 'integer'},
    'refinance_loan_closing_costs': {'type': 'integer'},

    'loan1_interest_only': {'type': 'boolean'},
    'loan2_interest_only': {'type': 'boolean'},
    'loan3_interest_only': {'type': 'boolean'},

    'loan1_loan_name': {'type': 'string'},
    'loan1_loan_amount': {'type': 'integer'},
    'loan1_loan_interest_rate': {'type': 'float'},
    'loan1_loan_term': {'type': 'integer'},
    'loan1_loan_down_payment': {'type': 'integer'},
    'loan1_loan_closing_costs': {'type': 'integer'},

    'loan2_loan_name': {'type': 'string'},
    'loan2_loan_amount': {'type': 'integer'},
    'loan2_loan_interest_rate': {'type': 'float'},
    'loan2_loan_term': {'type': 'integer'},
    'loan2_loan_down_payment': {'type': 'integer'},
    'loan2_loan_closing_costs': {'type': 'integer'},

    'loan3_loan_name': {'type': 'string'},
    'loan3_loan_amount': {'type': 'integer'},
    'loan3_loan_interest_rate': {'type': 'float'},
    'loan3_loan_term': {'type': 'integer'},
    'loan3_loan_down_payment': {'type': 'integer'},
    'loan3_loan_closing_costs': {'type': 'integer'},

    # Lease Option fields
    'option_consideration_fee': {
        'type': 'integer',
        'optional': False,
        'description': 'Non-refundable upfront fee for lease option'
    },
    'option_term_months': {
        'type': 'integer',
        'optional': False,
        'description': 'Duration of option period in months'
    },
    'strike_price': {
        'type': 'integer',
        'optional': False,
        'description': 'Agreed upon future purchase price'
    },
    'monthly_rent_credit_percentage': {
        'type': 'float',
        'optional': False,
        'description': 'Percentage of monthly rent applied as credit'
    },
    'rent_credit_cap': {
        'type': 'integer',
        'optional': False,
        'description': 'Maximum total rent credit allowed'
    },

    # Multi-Family specific fields
    'total_units': {'type': 'integer', 'optional': False},
    'occupied_units': {'type': 'integer', 'optional': False},
    'floors': {'type': 'integer', 'optional': False},
    'other_income': {'type': 'integer', 'optional': True},
    'total_potential_income': {'type': 'integer', 'optional': True},

    # Multi-Family operating expenses
    'common_area_maintenance': {'type': 'integer', 'optional': False},
    'elevator_maintenance': {'type': 'integer', 'optional': True},
    'staff_payroll': {'type': 'integer', 'optional': False},
    'trash_removal': {'type': 'integer', 'optional': False},
    'common_utilities': {'type': 'integer', 'optional': False},

    # Unit Types array (will be handled as JSON string in storage)
    'unit_types': {
        'type': 'string',  # JSON string of unit type array
        'optional': False,
        'description': 'Array of unit types and their details'
    },
}

# Mobile-specific optional fields
MOBILE_OPTIONAL_FIELDS = [
    'lot_size',
    'year_built',
    'furnishing_costs',
    'other_income',
    'elevator_maintenance',
]
