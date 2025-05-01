"""
Test persona data for UI testing.

This module defines a comprehensive test persona with properties, analyses, loans,
transactions, and other data needed for thorough UI testing. The test persona
includes various property types, investment strategies, and financial scenarios
to ensure all application features can be tested.
"""
import uuid
from datetime import datetime, timedelta

# Core test user
TEST_USER = {
    "email": "test.user@rei-tracker-testing.com",
    "password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
    "role": "admin"
}

# Property portfolio
TEST_PROPERTIES = [
    {
        "id": "prop-singlefamily-001",
        "name": "Test Single Family",
        "address": {
            "street": "123 Test Street",
            "city": "Testville",
            "state": "CA",
            "zip": "90210"
        },
        "purchase_price": 250000,
        "purchase_date": "2023-01-15",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500,
        "property_type": "single_family",
        "partners": []  # Wholly owned property
    },
    {
        "id": "prop-multifamily-001",
        "name": "Test Duplex",
        "address": {
            "street": "456 Test Avenue",
            "city": "Testville",
            "state": "CA",
            "zip": "90210"
        },
        "purchase_price": 400000,
        "purchase_date": "2023-03-10",
        "bedrooms": 4,  # Total bedrooms
        "bathrooms": 3,  # Total bathrooms
        "square_feet": 2400,
        "property_type": "multi_family",
        "units": 2,
        "partners": [
            {
                "name": "Test Partner",
                "email": "partner@rei-tracker-testing.com",
                "equity_percentage": 25
            }
        ]
    },
    {
        "id": "prop-brrrr-001",
        "name": "Test BRRRR Property",
        "address": {
            "street": "789 Test Boulevard",
            "city": "Testville",
            "state": "CA",
            "zip": "90210"
        },
        "purchase_price": 180000,
        "purchase_date": "2023-05-20",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1600,
        "property_type": "single_family",
        "partners": []  # Wholly owned property
    },
    {
        "id": "prop-leaseoption-001",
        "name": "Test Lease Option",
        "address": {
            "street": "101 Test Lane",
            "city": "Testville",
            "state": "CA",
            "zip": "90210"
        },
        "purchase_price": 220000,
        "purchase_date": "2023-02-05",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1700,
        "property_type": "single_family",
        "partners": [
            {
                "name": "Test Partner",
                "email": "partner@rei-tracker-testing.com",
                "equity_percentage": 40
            }
        ]
    },
    {
        "id": "prop-multifamily-large-001",
        "name": "Test Apartment Building",
        "address": {
            "street": "202 Test Court",
            "city": "Testville",
            "state": "CA",
            "zip": "90210"
        },
        "purchase_price": 800000,
        "purchase_date": "2023-04-15",
        "bedrooms": 12,  # Total bedrooms
        "bathrooms": 8,  # Total bathrooms
        "square_feet": 6000,
        "property_type": "multi_family",
        "units": 6,
        "partners": [
            {
                "name": "Test Partner",
                "email": "partner@rei-tracker-testing.com",
                "equity_percentage": 20
            },
            {
                "name": "Another Partner",
                "email": "another.partner@rei-tracker-testing.com",
                "equity_percentage": 20
            }
        ]
    },
    {
        "id": "prop-padsplit-brrrr-001",
        "name": "Test PadSplit BRRRR",
        "address": {
            "street": "303 Test Boulevard",
            "city": "Testville",
            "state": "CA",
            "zip": "90210"
        },
        "purchase_price": 160000,
        "purchase_date": "2023-06-15",
        "bedrooms": 5,  # Good for PadSplit
        "bathrooms": 3,
        "square_feet": 2200,
        "property_type": "single_family",
        "partners": [
            {
                "name": "Test Partner",
                "email": "partner@rei-tracker-testing.com",
                "equity_percentage": 30
            },
            {
                "name": "Another Partner",
                "email": "another.partner@rei-tracker-testing.com",
                "equity_percentage": 20
            }
        ]  # 50% ownership for test user, 50% split between partners
    }
]

# Analyses for each property
TEST_ANALYSES = [
    {
        "id": "analysis-ltr-001",
        "property_id": "prop-singlefamily-001",
        "analysis_type": "LTR",
        "purchase_price": 250000,
        "monthly_rent": 2500,
        "property_taxes": 313,  # $3750/year
        "insurance": 125,
        "vacancy_percentage": 5,
        "repairs_percentage": 5,
        "capex_percentage": 5,
        "management_percentage": 10,
        "utilities": 0,
        "other_expenses": 50
    },
    {
        "id": "analysis-brrrr-001",
        "property_id": "prop-brrrr-001",
        "analysis_type": "BRRRR",
        "purchase_price": 180000,
        "rehab_cost": 50000,
        "after_repair_value": 300000,
        "monthly_rent": 2700,
        "refinance_amount_percentage": 75,
        "refinance_interest_rate": 4.5,
        "refinance_term_years": 30,
        "refinance_closing_costs": 4000,
        "property_taxes": 275,  # $3300/year
        "insurance": 150,
        "vacancy_percentage": 5,
        "repairs_percentage": 5,
        "capex_percentage": 5,
        "management_percentage": 10,
        "utilities": 0,
        "other_expenses": 50
    },
    {
        "id": "analysis-leaseoption-001",
        "property_id": "prop-leaseoption-001",
        "analysis_type": "Lease Option",
        "purchase_price": 220000,
        "monthly_rent": 2200,
        "option_consideration_fee": 3000,
        "option_term_months": 24,
        "rent_credit_percentage": 25,
        "strike_price": 250000,
        "property_taxes": 229,  # $2750/year
        "insurance": 110,
        "vacancy_percentage": 0,  # No vacancy with lease option
        "repairs_percentage": 3,
        "capex_percentage": 3,
        "management_percentage": 0,  # Self-managed
        "utilities": 0,
        "other_expenses": 50
    },
    {
        "id": "analysis-multifamily-001",
        "property_id": "prop-multifamily-001",
        "analysis_type": "Multi-Family",
        "purchase_price": 400000,
        "monthly_rent": 4000,  # Total for both units
        "total_units": 2,
        "occupied_units": 2,
        "average_rent_per_unit": 2000,
        "property_taxes": 417,  # $5000/year
        "insurance": 200,
        "vacancy_percentage": 5,
        "repairs_percentage": 5,
        "capex_percentage": 5,
        "management_percentage": 10,
        "utilities": 100,
        "common_area_maintenance": 50,
        "other_expenses": 75
    },
    {
        "id": "analysis-multifamily-large-001",
        "property_id": "prop-multifamily-large-001",
        "analysis_type": "Multi-Family",
        "purchase_price": 800000,
        "monthly_rent": 9000,  # Total for all units
        "total_units": 6,
        "occupied_units": 5,
        "average_rent_per_unit": 1500,
        "property_taxes": 833,  # $10000/year
        "insurance": 400,
        "vacancy_percentage": 7,
        "repairs_percentage": 5,
        "capex_percentage": 7,
        "management_percentage": 8,
        "utilities": 300,
        "common_area_maintenance": 150,
        "elevator_maintenance": 200,
        "staff_payroll": 1000,
        "other_expenses": 100
    },
    {
        "id": "analysis-padsplit-brrrr-001",
        "property_id": "prop-padsplit-brrrr-001",
        "analysis_type": "PadSplit",  # PadSplit strategy
        "purchase_price": 160000,
        "rehab_cost": 65000,  # Higher rehab for PadSplit conversion
        "after_repair_value": 280000,
        "total_rooms": 6,  # Converting to 6 rentable rooms
        "average_rent_per_room": 850,
        "platform_percentage": 8,
        "furnishing_costs": 9000,  # $1500 per room
        "common_area_maintenance": 250,
        "refinance_amount_percentage": 80,  # 80% LTV refinance
        "refinance_interest_rate": 5.25,
        "refinance_term_years": 30,
        "refinance_closing_costs": 4500,
        "property_taxes": 233,  # $2800/year
        "insurance": 175,  # Higher for PadSplit due to more occupants
        "vacancy_percentage": 8,
        "repairs_percentage": 7,
        "capex_percentage": 8,
        "management_percentage": 0,  # Self-managed through PadSplit
        "utilities": 450,  # Utilities included in PadSplit model
        "other_expenses": 100
    }
]

# Loans for each property
TEST_LOANS = [
    {
        "id": "loan-standard-001",
        "property_id": "prop-singlefamily-001",
        "loan_type": "Primary",
        "loan_amount": 200000,  # 80% LTV
        "interest_rate": 4.25,
        "term_months": 360,  # 30 years
        "start_date": "2023-01-15",
        "payment_amount": 983.88,
        "has_balloon": False
    },
    {
        "id": "loan-multifamily-001",
        "property_id": "prop-multifamily-001",
        "loan_type": "Primary",
        "loan_amount": 320000,  # 80% LTV
        "interest_rate": 4.5,
        "term_months": 360,  # 30 years
        "start_date": "2023-03-10",
        "payment_amount": 1621.39,
        "has_balloon": False
    },
    {
        "id": "loan-balloon-001",
        "property_id": "prop-brrrr-001",
        "loan_type": "Primary",
        "loan_amount": 144000,  # 80% of purchase price
        "interest_rate": 6.0,
        "term_months": 360,
        "start_date": "2023-05-20",
        "payment_amount": 863.35,
        "has_balloon": True,
        "balloon_months": 60  # 5-year balloon
    },
    {
        "id": "loan-refinance-001",
        "property_id": "prop-brrrr-001",
        "loan_type": "Refinance",
        "loan_amount": 225000,  # 75% of ARV
        "interest_rate": 4.5,
        "term_months": 360,
        "start_date": "2023-08-15",  # After rehab
        "payment_amount": 1140.04,
        "has_balloon": False
    },
    {
        "id": "loan-interestonly-001",
        "property_id": "prop-leaseoption-001",
        "loan_type": "Primary",
        "loan_amount": 176000,  # 80% LTV
        "interest_rate": 5.0,
        "term_months": 360,
        "start_date": "2023-02-05",
        "payment_amount": 733.33,  # Interest-only payment
        "has_balloon": True,
        "balloon_months": 120,  # 10-year balloon
        "interest_only": True,
        "interest_only_months": 120  # 10 years interest-only
    },
    {
        "id": "loan-multifamily-large-001",
        "property_id": "prop-multifamily-large-001",
        "loan_type": "Primary",
        "loan_amount": 640000,  # 80% LTV
        "interest_rate": 4.75,
        "term_months": 360,  # 30 years
        "start_date": "2023-04-15",
        "payment_amount": 3339.13,
        "has_balloon": False
    },
    {
        "id": "loan-secondary-001",
        "property_id": "prop-multifamily-large-001",
        "loan_type": "Secondary",
        "loan_amount": 80000,  # Additional financing
        "interest_rate": 6.5,
        "term_months": 120,  # 10 years
        "start_date": "2023-04-15",
        "payment_amount": 908.05,
        "has_balloon": False
    },
    {
        "id": "loan-padsplit-brrrr-001",
        "property_id": "prop-padsplit-brrrr-001",
        "loan_type": "Primary",
        "loan_amount": 128000,  # 80% of purchase price
        "interest_rate": 5.5,
        "term_months": 360,
        "start_date": "2023-06-15",
        "payment_amount": 727.01,
        "has_balloon": False
    },
    {
        "id": "loan-padsplit-brrrr-refinance-001",
        "property_id": "prop-padsplit-brrrr-001",
        "loan_type": "Refinance",
        "loan_amount": 224000,  # 80% of ARV
        "interest_rate": 5.25,
        "term_months": 360,
        "start_date": "2023-09-20",  # After rehab
        "payment_amount": 1236.63,
        "has_balloon": False
    }
]

# Transactions for each property
TEST_TRANSACTIONS = [
    # Regular rental income
    {
        "id": "trans-income-001",
        "property_id": "prop-singlefamily-001",
        "date": "2023-02-01",
        "type": "income",
        "category": "Rent",
        "amount": 2500,
        "description": "February 2023 Rent",
        "documentation": "leases/tenant_lease_agreement.pdf",
        "collector": "Test User"
    },
    {
        "id": "trans-income-002",
        "property_id": "prop-singlefamily-001",
        "date": "2023-03-01",
        "type": "income",
        "category": "Rent",
        "amount": 2500,
        "description": "March 2023 Rent",
        "documentation": "leases/tenant_lease_agreement.pdf",
        "collector": "Test User"
    },
    # Expense with reimbursement needed
    {
        "id": "trans-expense-001",
        "property_id": "prop-multifamily-001",
        "date": "2023-03-15",
        "type": "expense",
        "category": "Repairs",
        "amount": 750,
        "description": "Plumbing repair",
        "documentation": "receipts/plumbing_repair_receipt.pdf",
        "payer": "Test User",
        "reimbursement": {
            "status": "pending",
            "date_shared": "2023-03-16",
            "share_description": "Emergency plumbing repair",
            "partner_shares": [
                {
                    "partner_email": "partner@rei-tracker-testing.com",
                    "amount": 187.50,  # 25% of $750
                    "status": "pending"
                }
            ]
        }
    },
    # BRRRR property transactions
    {
        "id": "trans-expense-002",
        "property_id": "prop-brrrr-001",
        "date": "2023-05-25",
        "type": "expense",
        "category": "Renovation",
        "amount": 20000,
        "description": "First phase renovation",
        "documentation": "receipts/contractor_invoice.pdf",
        "payer": "Test User"
    },
    {
        "id": "trans-expense-003",
        "property_id": "prop-brrrr-001",
        "date": "2023-06-15",
        "type": "expense",
        "category": "Renovation",
        "amount": 15000,
        "description": "Second phase renovation",
        "documentation": "receipts/contractor_invoice.pdf",
        "payer": "Test User"
    },
    {
        "id": "trans-expense-004",
        "property_id": "prop-brrrr-001",
        "date": "2023-07-05",
        "type": "expense",
        "category": "Renovation",
        "amount": 15000,
        "description": "Final phase renovation",
        "documentation": "receipts/contractor_invoice.pdf",
        "payer": "Test User"
    },
    # Lease option property transactions
    {
        "id": "trans-income-003",
        "property_id": "prop-leaseoption-001",
        "date": "2023-02-10",
        "type": "income",
        "category": "Option Fee",
        "amount": 3000,
        "description": "Option consideration fee",
        "documentation": "leases/option_agreement.pdf",
        "collector": "Test User"
    },
    {
        "id": "trans-income-004",
        "property_id": "prop-leaseoption-001",
        "date": "2023-03-01",
        "type": "income",
        "category": "Rent",
        "amount": 2200,
        "description": "March 2023 Rent",
        "documentation": "leases/option_agreement.pdf",
        "collector": "Test User"
    },
    # Multi-family property transactions
    {
        "id": "trans-income-005",
        "property_id": "prop-multifamily-001",
        "date": "2023-04-01",
        "type": "income",
        "category": "Rent",
        "amount": 2000,
        "description": "April 2023 Rent - Unit 1",
        "documentation": "leases/unit1_lease.pdf",
        "collector": "Test User"
    },
    {
        "id": "trans-income-006",
        "property_id": "prop-multifamily-001",
        "date": "2023-04-01",
        "type": "income",
        "category": "Rent",
        "amount": 2000,
        "description": "April 2023 Rent - Unit 2",
        "documentation": "leases/unit2_lease.pdf",
        "collector": "Test User"
    },
    # Large multi-family property transactions
    {
        "id": "trans-expense-005",
        "property_id": "prop-multifamily-large-001",
        "date": "2023-05-10",
        "type": "expense",
        "category": "Repairs",
        "amount": 1200,
        "description": "HVAC repair - Unit 3",
        "documentation": "receipts/hvac_repair.pdf",
        "payer": "Test User",
        "reimbursement": {
            "status": "in_progress",
            "date_shared": "2023-05-11",
            "share_description": "HVAC emergency repair",
            "partner_shares": [
                {
                    "partner_email": "partner@rei-tracker-testing.com",
                    "amount": 240.00,  # 20% of $1200
                    "status": "completed",
                    "date_completed": "2023-05-15"
                },
                {
                    "partner_email": "another.partner@rei-tracker-testing.com",
                    "amount": 240.00,  # 20% of $1200
                    "status": "pending"
                }
            ]
        }
    },
    # PadSplit BRRRR property transactions
    {
        "id": "trans-expense-006",
        "property_id": "prop-padsplit-brrrr-001",
        "date": "2023-06-20",
        "type": "expense",
        "category": "Renovation",
        "amount": 15000,
        "description": "First phase renovation payment",
        "documentation": "receipts/contractor_invoice.pdf",
        "payer": "Test User",
        "reimbursement": {
            "status": "pending",
            "date_shared": "2023-06-21",
            "share_description": "Renovation payment 1 of 4",
            "partner_shares": [
                {
                    "partner_email": "partner@rei-tracker-testing.com",
                    "amount": 4500,  # 30% of $15000
                    "status": "pending"
                },
                {
                    "partner_email": "another.partner@rei-tracker-testing.com",
                    "amount": 3000,  # 20% of $15000
                    "status": "pending"
                }
            ]
        }
    },
    {
        "id": "trans-expense-007",
        "property_id": "prop-padsplit-brrrr-001",
        "date": "2023-07-05",
        "type": "expense",
        "category": "Renovation",
        "amount": 18000,
        "description": "Second phase renovation payment",
        "documentation": "receipts/contractor_invoice.pdf",
        "payer": "Test User",
        "reimbursement": {
            "status": "completed",
            "date_shared": "2023-07-06",
            "share_description": "Renovation payment 2 of 4",
            "partner_shares": [
                {
                    "partner_email": "partner@rei-tracker-testing.com",
                    "amount": 5400,  # 30% of $18000
                    "status": "completed",
                    "date_completed": "2023-07-10"
                },
                {
                    "partner_email": "another.partner@rei-tracker-testing.com",
                    "amount": 3600,  # 20% of $18000
                    "status": "completed",
                    "date_completed": "2023-07-09"
                }
            ]
        }
    },
    {
        "id": "trans-expense-008",
        "property_id": "prop-padsplit-brrrr-001",
        "date": "2023-07-25",
        "type": "expense",
        "category": "Furnishings",
        "amount": 9000,
        "description": "Furnishings for all rooms",
        "documentation": "receipts/furniture_invoice.pdf",
        "payer": "Test User",
        "reimbursement": {
            "status": "in_progress",
            "date_shared": "2023-07-26",
            "share_description": "Furniture for PadSplit rooms",
            "partner_shares": [
                {
                    "partner_email": "partner@rei-tracker-testing.com",
                    "amount": 2700,  # 30% of $9000
                    "status": "completed",
                    "date_completed": "2023-07-30"
                },
                {
                    "partner_email": "another.partner@rei-tracker-testing.com",
                    "amount": 1800,  # 20% of $9000
                    "status": "pending"
                }
            ]
        }
    },
    {
        "id": "trans-expense-009",
        "property_id": "prop-padsplit-brrrr-001",
        "date": "2023-08-15",
        "type": "expense",
        "category": "Renovation",
        "amount": 23000,
        "description": "Final phase renovation payment",
        "documentation": "receipts/contractor_invoice.pdf",
        "payer": "Test User",
        "reimbursement": {
            "status": "pending",
            "date_shared": "2023-08-16",
            "share_description": "Renovation payment 3 of 4",
            "partner_shares": [
                {
                    "partner_email": "partner@rei-tracker-testing.com",
                    "amount": 6900,  # 30% of $23000
                    "status": "pending"
                },
                {
                    "partner_email": "another.partner@rei-tracker-testing.com",
                    "amount": 4600,  # 20% of $23000
                    "status": "pending"
                }
            ]
        }
    },
    # Income transactions for PadSplit
    {
        "id": "trans-income-007",
        "property_id": "prop-padsplit-brrrr-001",
        "date": "2023-09-05",
        "type": "income",
        "category": "Rent",
        "amount": 4675,  # 6 rooms at $850 minus 8% platform fee
        "description": "September 2023 PadSplit Income",
        "documentation": "bank_statements/september_bank_statement.pdf",
        "collector": "PadSplit Platform"
    }
]

# MAO calculation defaults
MAO_CALCULATION_DEFAULTS = {
    "money_left_in_deal": 5000,  # Willing to leave $5,000 in a deal
    "ltv_percentage": 80,  # Assuming 80% LTV refinance
    "arv_discount_percentage": 0,  # No discount on ARV
    "closing_costs_percentage": 2,  # 2% closing costs
    "rehab_overage_percentage": 10,  # 10% buffer for rehab costs
    "holding_costs_percentage": 1,  # 1% of purchase price for holding costs
    "min_cash_flow": 200,  # Minimum monthly cash flow
    "min_coc_return": 10  # Minimum cash-on-cash return percentage
}

# Complete test persona data
TEST_PERSONA = {
    "user": TEST_USER,
    "properties": TEST_PROPERTIES,
    "analyses": TEST_ANALYSES,
    "loans": TEST_LOANS,
    "transactions": TEST_TRANSACTIONS,
    "mao_defaults": MAO_CALCULATION_DEFAULTS
}
