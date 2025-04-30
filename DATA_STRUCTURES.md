# Data Structures Documentation

This document provides comprehensive information about all data structures used in the application.

## Table of Contents
1. [Analysis Data Structure](#analysis-data-structure)
2. [Properties Data Structure](#properties-data-structure)
3. [Categories Data Structure](#categories-data-structure)
4. [Users Data Structure](#users-data-structure)
5. [Transactions Data Structure](#transactions-data-structure)
6. [Partner Contributions Data Structure](#partner-contributions-data-structure)
7. [Loans Data Structure](#loans-data-structure)

---

## Analysis Data Structure

The analysis data structure represents various types of property investment analyses.

### Core Fields
- `id`: UUID string
- `user_id`: string
- `created_at`: ISO 8601 datetime string
- `updated_at`: ISO 8601 datetime string
- `analysis_type`: string
- `analysis_name`: string

### Property Details
- `property_id`: string (full property address used as identifier)
- `property_type`: string (Single Family, Condo, Townhouse, Manufactured, Multi-Family)
- `square_footage`: integer
- `lot_size`: integer
- `year_built`: integer
- `bedrooms`: integer
- `bathrooms`: float

### Financial Details
- `purchase_price`: integer
- `after_repair_value`: integer
- `renovation_costs`: integer
- `renovation_duration`: integer
- `furnishing_costs`: integer  // One-time expense for PadSplit furnishing
- `cash_to_seller`: integer
- `closing_costs`: integer
- `assignment_fee`: integer
- `marketing_costs`: integer

### Income Details
- `monthly_rent`: integer

### Expense Details
- `property_taxes`: integer
- `insurance`: integer
- `hoa_coa_coop`: integer
- `management_fee_percentage`: float
- `capex_percentage`: float
- `vacancy_percentage`: float
- `repairs_percentage`: float
- `utilities`: integer
- `internet`: integer
- `cleaning`: integer
- `pest_control`: integer
- `landscaping`: integer
- `padsplit_platform_percentage`: float

### Loan Details

#### Initial Loan
- `initial_loan_name`: string
- `initial_loan_amount`: integer
- `initial_loan_interest_rate`: float
- `initial_interest_only`: boolean (indicates if initial loan is interest-only)
- `initial_loan_term`: integer
- `initial_loan_down_payment`: integer
- `initial_loan_closing_costs`: integer

#### Refinance Loan
- `refinance_loan_name`: string
- `refinance_loan_amount`: integer
- `refinance_loan_interest_rate`: float
- `refinance_ltv_percentage`: float (percentage value for refinance loan-to-value)
- `refinance_loan_term`: integer
- `refinance_loan_down_payment`: integer
- `refinance_loan_closing_costs`: integer

#### Additional Loans (1-3)
- `loan1_loan_name`: string
- `loan1_loan_amount`: integer
- `loan1_loan_interest_rate`: float
- `loan1_interest_only`: boolean (indicates if loan1 is interest-only)
- `loan1_loan_term`: integer
- `loan1_loan_down_payment`: integer
- `loan1_loan_closing_costs`: integer
- `loan2_loan_name`: string
- `loan2_loan_amount`: integer
- `loan2_loan_interest_rate`: float
- `loan2_interest_only`: boolean (indicates if loan2 is interest-only)
- `loan2_loan_term`: integer
- `loan2_loan_down_payment`: integer
- `loan2_loan_closing_costs`: integer
- `loan3_loan_name`: string
- `loan3_loan_amount`: integer
- `loan3_loan_interest_rate`: float
- `loan3_interest_only`: boolean (indicates if loan3 is interest-only)
- `loan3_loan_term`: integer
- `loan3_loan_down_payment`: integer
- `loan3_loan_closing_costs`: integer

### Balloon Payment Fields
- `has_balloon_payment`: boolean (indicates if a balloon payment is configured)
- `balloon_due_date`: string (ISO format date for balloon payment)
- `balloon_refinance_ltv_percentage`: float
- `balloon_refinance_loan_amount`: integer
- `balloon_refinance_loan_interest_rate`: float
- `balloon_refinance_loan_term`: integer
- `balloon_refinance_loan_down_payment`: integer
- `balloon_refinance_loan_closing_costs`: integer

### Lease Option Fields
- `option_consideration_fee`: integer (non-refundable upfront fee for lease option)
- `option_term_months`: integer (duration of option period in months)
- `strike_price`: integer (agreed upon future purchase price)
- `monthly_rent_credit_percentage`: float (percentage of monthly rent applied as credit)
- `rent_credit_cap`: integer (maximum total rent credit allowed)

### Multi-Family Specific Fields
- `total_units`: integer (total number of units in the property)
- `occupied_units`: integer (number of currently occupied units)
- `floors`: integer (number of floors in the building)
- `other_income`: integer (additional income beyond unit rent)
- `total_potential_income`: integer (maximum possible income if fully occupied)
- `common_area_maintenance`: integer (monthly cost for common areas)
- `elevator_maintenance`: integer (monthly cost for elevator maintenance)
- `staff_payroll`: integer (monthly cost for property staff)
- `trash_removal`: integer (monthly cost for trash services)
- `common_utilities`: integer (monthly cost for common area utilities)
- `unit_types`: string (JSON string representing array of unit types)
  ```json
  [
    {
      "type": "1BR/1BA",
      "count": 4,
      "occupied": 3,
      "square_footage": 750,
      "rent": 1200
    },
    {
      "type": "2BR/2BA",
      "count": 2,
      "occupied": 2,
      "square_footage": 1100,
      "rent": 1800
    }
  ]
  ```

### Notes Field
- `notes`: string (user notes about the analysis, max 1000 characters)

### Comps Integration Data
- `comps_data`: object (null if comps haven't been run)
  - `last_run`: ISO 8601 datetime string
  - `run_count`: integer (number of times comps have been run in current session)
  - `estimated_value`: integer
  - `value_range_low`: integer
  - `value_range_high`: integer
  - `comparables`: array of objects
    - `id`: string
    - `formattedAddress`: string
    - `city`: string
    - `state`: string
    - `zipCode`: string
    - `propertyType`: string
    - `bedrooms`: integer
    - `bathrooms`: float
    - `squareFootage`: integer
    - `yearBuilt`: integer
    - `price`: integer
    - `listingType`: string
    - `listedDate`: ISO 8601 datetime string
    - `removedDate`: ISO 8601 datetime string (null if still active)
    - `daysOnMarket`: integer
    - `distance`: float
    - `correlation`: float
  - `rental_comps`: object (null if rental comps haven't been run)
    - `last_run`: ISO 8601 datetime string
    - `estimated_rent`: integer
    - `rent_range_low`: integer
    - `rent_range_high`: integer
    - `comparable_rentals`: array of rental property objects
    - `confidence_score`: float
  - `mao`: object (null if MAO hasn't been calculated)
    - `value`: integer (maximum allowable offer)
    - `arv`: integer (after repair value used in calculation)
    - `ltv_percentage`: float (loan-to-value percentage used)
    - `renovation_costs`: integer
    - `closing_costs`: integer
    - `monthly_holding_costs`: float
    - `total_holding_costs`: float
    - `holding_months`: integer
    - `max_cash_left`: integer

### Example Comps Data
```json
{
  "comps_data": {
    "last_run": "2024-09-28T13:21:51.018Z",
    "run_count": 1,
    "estimated_value": 221000,
    "value_range_low": 208000,
    "value_range_high": 233000,
    "comparables": [
      {
        "id": "unique-comp-id",
        "formattedAddress": "123 Main St",
        "city": "San Antonio",
        "state": "TX",
        "zipCode": "78244",
        "propertyType": "Single Family",
        "bedrooms": 4,
        "bathrooms": 2,
        "squareFootage": 1747,
        "yearBuilt": 1986,
        "price": 229900,
        "listingType": "Standard",
        "listedDate": "2024-04-03T00:00:00.000Z",
        "removedDate": "2024-05-26T00:00:00.000Z",
        "daysOnMarket": 53,
        "distance": 0.2994,
        "correlation": 0.9822
      }
    ]
  }
}
```

### Background Notes
1. Store required data in JSON as raw data (str, int, bool, float). Calculated and derived values are created and calculated at run-time.
2. Currency and percentage values are only formatted for the Reports Tab output and reports downloaded as PDF.
3. Currency format follows "$X,XXX.XX" pattern
4. Percentage format follows "XX.XXX%" pattern
5. Date-times are in ISO 8601 format
6. Fields made available to the user depend upon the analysis type selected. Assume null values unless specified otherwise by the user.
7. Currency and percentage formats are performed at the frontend only for the Reports Tab and when generating reports to download as PDF.

---

## Properties Data Structure

This schema defines the structure for real estate property data, including purchase details, financing, income, expenses, and partnership information.

### Root Object Properties

| Field | Type | Description |
|-------|------|-------------|
| property_id | string | Full property address including street, city, state, zip, and country |
| purchase_price | number | Total purchase price in USD |
| purchase_date | string | Date of purchase (YYYY-MM-DD format) |
| down_payment | number | Down payment amount in USD |
| primary_loan_rate | number | Primary loan interest rate as percentage |
| primary_loan_term | number | Primary loan term in months |
| primary_loan_amount | number | Primary loan amount in USD |
| primary_loan_start_date | string | Primary loan start date (YYYY-MM-DD format) |
| secondary_loan_amount | number | Secondary/seller financing amount in USD |
| secondary_loan_rate | number | Secondary loan interest rate as percentage |
| secondary_loan_term | number | Secondary loan term in months |
| closing_costs | number | Total closing costs in USD |
| renovation_costs | number | Total renovation costs in USD |
| marketing_costs | number | Total marketing costs in USD |
| holding_costs | number | Total holding costs in USD |

### Monthly Income Object
```json
"monthly_income": {
  "rental_income": number,
  "parking_income": number,
  "laundry_income": number,
  "other_income": number,
  "income_notes": string
}
```

### Monthly Expenses Object
```json
"monthly_expenses": {
  "property_tax": number,
  "insurance": number,
  "repairs": number,
  "capex": number,
  "property_management": number,
  "hoa_fees": number,
  "utilities": {
    "water": number,
    "electricity": number,
    "gas": number,
    "trash": number
  },
  "other_expenses": number,
  "expense_notes": string
}
```

### Partners Array
```json
"partners": [
  {
    "name": string,
    "equity_share": number,
    "is_property_manager": boolean
  }
]
```

### Data Types
- All numerical values should include decimal points (e.g., `100.0` instead of `100`)
- Dates should be in ISO 8601 format: YYYY-MM-DD
- Percentages are stored as decimal numbers (e.g., 5.75 for 5.75%)
- Boolean values should be `true` or `false`
- Strings should be enclosed in double quotes

---

## Categories Data Structure

The categories data structure defines the available categories for income and expense transactions.

```json
{
    "income": [
        "Application Fees",
        "Common Area Revenue",
        "Escrow Refund",
        "Insurance Refund",
        "Late Fees",
        "Loan Repayment",
        "Other Income",
        "Parking/Storage Fees",
        "Pet Rent",
        "Rent",
        "Security Deposit",
        "Utility Reimbursement"
    ],
    "expense": [
        "Asset Acquisition",
        "Association Dues",
        "Bank/Financial Fees",
        "Capital Expenditures",
        "Cleaning",
        "Furnishing",
        "Insurance",
        "Landscaping",
        "Legal/Professional Fees",
        "Maintenance",
        "Marketing/Advertising",
        "Mortgage",
        "Other Expense",
        "Permit/License Fees",
        "Pest Control",
        "Property Management Fees",
        "Property Tax",
        "Repairs",
        "Security",
        "Supplies",
        "Utilities"
    ]
}
```

---

## Users Data Structure

The users data structure stores user information, credentials, and roles.

### User Object Structure

| Field | Type | Description |
|-------|------|-------------|
| first_name | string | User's first name |
| last_name | string | User's last name |
| name | string | User's full name |
| email | string | User's email address (used as key in the JSON object) |
| phone | string | User's phone number with country code |
| password | string | Hashed password using PBKDF2 with SHA-256 |
| role | string | User's role (Admin or User) |
| property_access | array | List of properties the user has access to with access levels and equity shares |
| mao_preferences | object | User's preferences for MAO calculations |

### Property Access Object Structure

| Field | Type | Description |
|-------|------|-------------|
| property_id | string | Property identifier (typically the full address) |
| access_level | string | Access level ("owner", "manager", "editor", "viewer") |
| equity_share | number | User's equity share percentage in the property (optional) |

### MAO Preferences Object Structure

| Field | Type | Description |
|-------|------|-------------|
| max_cash_left | number | Maximum cash to leave in a deal (default: 10000) |
| default_ltv_percentage | number | Default loan-to-value percentage (default: 75.0) |
| default_holding_costs_buffer | number | Percentage buffer for holding costs (default: 10.0) |
| default_renovation_contingency | number | Percentage contingency for renovation (default: 15.0) |

### Example User Object
```json
"bjmar867@gmail.com": {
  "first_name": "BJ",
  "last_name": "Marshall",
  "name": "BJ Marshall",
  "email": "bjmar867@gmail.com",
  "phone": "+14435465716",
  "password": "pbkdf2:sha256:600000$RW1h6Oalhp4zutww$bfea68cc108126cb1673d76bd8b86c3551d3d8533e1b66412218ce6b1b79d2af",
  "role": "Admin",
  "property_access": [
    {
      "property_id": "1911 Grinnalds Avenue, Baltimore, MD 21223, United States of America, Baltimore, Maryland, 21223",
      "access_level": "owner",
      "equity_share": 100.0
    },
    {
      "property_id": "454 Guilford Avenue, Hagerstown, MD 21740, United States of America, Hagerstown, Maryland, 21740",
      "access_level": "manager",
      "equity_share": 0.0
    }
  ],
  "mao_preferences": {
    "max_cash_left": 10000,
    "default_ltv_percentage": 75.0,
    "default_holding_costs_buffer": 10.0,
    "default_renovation_contingency": 15.0
  }
}
```

### Access Level Hierarchy
- **owner**: Full access to property, including financial management and partner equity
- **manager**: Can manage property transactions and maintenance, but cannot modify partner equity
- **editor**: Can edit property details and add transactions, but cannot manage reimbursements
- **viewer**: Read-only access to property information

---

## Transactions Data Structure

The transactions data structure records all financial transactions related to properties.

### Transaction Object Structure

| Field | Type | Description |
|-------|------|-------------|
| property_id | string | Property identifier (typically the full address) |
| type | string | Transaction type ("income" or "expense") |
| category | string | Transaction category from categories.json |
| description | string | Description of the transaction |
| amount | number | Transaction amount |
| date | string | Transaction date (YYYY-MM-DD format) |
| collector_payer | string | Name of the person who collected or paid |
| documentation_file | string | Filename of the supporting documentation |
| reimbursement | object | Information about reimbursement status |
| id | string | Unique transaction identifier |

### Reimbursement Object
| Field | Type | Description |
|-------|------|-------------|
| date_shared | string | Date when reimbursement was shared (YYYY-MM-DD format) |
| share_description | string | Description of the sharing status |
| reimbursement_status | string | Status of the reimbursement (e.g., "completed") |

### Example Transaction Object
```json
{
  "property_id": "1911 Grinnalds Avenue, Baltimore, MD 21223, United States of America, Baltimore, Maryland, 21223",
  "type": "expense",
  "category": "Mortgage",
  "description": "2024.05.01 Shellpoint Mortgage",
  "amount": 603.32,
  "date": "2024-05-01",
  "collector_payer": "BJ Marshall",
  "documentation_file": "trans_79_2024_Grinnalds_Shellpoint_Mortgage_Payments.png",
  "reimbursement": {
    "date_shared": "2024-05-01",
    "share_description": "Auto-completed - Single owner property",
    "reimbursement_status": "completed"
  },
  "id": "79"
}
```

### Notes
- The `documentation_file` references a file stored in the `/data/uploads/` directory
- Transaction IDs are assigned sequentially as strings
- The `property_id` uses the full address as an identifier

---

## Partner Contributions Data Structure

The partner contributions data structure tracks financial contributions and distributions between partners for properties.

### Partner Contribution Object Structure

| Field | Type | Description |
|-------|------|-------------|
| property_id | string | Property identifier (typically the full address) |
| partner_name | string | Name of the partner making the contribution or receiving the distribution |
| amount | number | Amount of the contribution or distribution |
| contribution_type | string | Type of transaction ("contribution" or "distribution") |
| date | string | Date of the contribution or distribution (YYYY-MM-DD format) |
| notes | string | Optional notes about the contribution or distribution |

### Example Partner Contribution Object
```json
{
  "property_id": "454 Guilford Avenue, Hagerstown, MD 21740, United States of America, Hagerstown, Maryland, 21740",
  "partner_name": "BJ Marshall",
  "amount": 5000.00,
  "contribution_type": "contribution",
  "date": "2024-05-15",
  "notes": "Initial capital contribution for renovation"
}
```

### Notes
- Contributions represent money invested into a property by a partner
- Distributions represent money taken out of a property by a partner
- The contribution history helps track the changing equity positions of partners over time
- This data structure complements the partner information in the properties.json file

---

## Loans Data Structure

The loans data structure provides comprehensive tracking of loans associated with properties, including detailed information about loan terms, status, and payment details.

### Loan Object Structure

| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier for the loan (UUID) |
| property_id | string | Property identifier the loan is associated with |
| loan_type | string | Type of loan (initial, refinance, additional, heloc, seller_financing, private) |
| amount | string | Loan amount with decimal precision |
| interest_rate | string | Annual interest rate as a percentage |
| term_months | number | Loan term in months |
| start_date | string | Date when the loan started (YYYY-MM-DD format) |
| is_interest_only | boolean | Whether the loan is interest-only |
| balloon_payment | object | Optional balloon payment details |
| lender | string | Name of the lender |
| loan_number | string | Loan identification number from the lender |
| status | string | Current status of the loan (active, paid_off, refinanced, defaulted) |
| refinanced_from_id | string | ID of the loan this refinanced (if applicable) |
| notes | string | Additional notes about the loan |
| name | string | Optional name for the loan |
| monthly_payment | string | Monthly payment amount |
| current_balance | string | Current loan balance |
| last_updated | string | Date when the loan was last updated (YYYY-MM-DD format) |
| created_at | string | ISO 8601 datetime when the loan was created |
| updated_at | string | ISO 8601 datetime when the loan was last updated |

### Balloon Payment Object
| Field | Type | Description |
|-------|------|-------------|
| due_date | string | Date when the balloon payment is due (YYYY-MM-DD format) |
| amount | string | Amount of the balloon payment |
| term_months | number | Number of months until the balloon payment is due |

### Example Loan Object
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "property_id": "454 Guilford Avenue, Hagerstown, MD 21740, United States of America, Hagerstown, Maryland, 21740",
  "loan_type": "initial",
  "amount": "112800.00",
  "interest_rate": "5.73%",
  "term_months": 360,
  "start_date": "2022-08-03",
  "is_interest_only": false,
  "lender": "PennyMac",
  "loan_number": "12345678",
  "status": "active",
  "notes": "Primary mortgage for property purchase",
  "name": "Primary Mortgage",
  "monthly_payment": "658.23",
  "current_balance": "109876.54",
  "last_updated": "2024-04-01",
  "created_at": "2022-08-03T12:00:00.000Z",
  "updated_at": "2024-04-01T15:30:00.000Z"
}
```

### Notes
- The loan data structure supports multiple loans per property
- Loan amounts and interest rates are stored with precise decimal handling
- The structure supports tracking loan status changes over time
- Refinanced loans maintain a reference to the original loan
- The system can generate amortization schedules and calculate remaining balances
