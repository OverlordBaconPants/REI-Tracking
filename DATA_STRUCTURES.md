# Data Structures Documentation

This document provides comprehensive information about all data structures used in the application.

## Table of Contents
1. [Analysis Data Structure](#analysis-data-structure)
2. [Properties Data Structure](#properties-data-structure)
3. [Categories Data Structure](#categories-data-structure)
4. [Users Data Structure](#users-data-structure)
5. [Transactions Data Structure](#transactions-data-structure)

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
- `address`: string
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
- `initial_loan_term`: integer
- `initial_loan_down_payment`: integer
- `initial_loan_closing_costs`: integer

#### Refinance Loan
- `refinance_loan_name`: string
- `refinance_loan_amount`: integer
- `refinance_loan_interest_rate`: float
- `refinance_loan_term`: integer
- `refinance_loan_down_payment`: integer
- `refinance_loan_closing_costs`: integer

#### Additional Loans (1-3)
- `loan1_loan_name`: string
- `loan1_loan_amount`: integer
- `loan1_loan_interest_rate`: float
- `loan1_loan_term`: integer
- `loan1_loan_down_payment`: integer
- `loan1_loan_closing_costs`: integer
- `loan2_loan_name`: string
- `loan2_loan_amount`: integer
- `loan2_loan_interest_rate`: float
- `loan2_loan_term`: integer
- `loan2_loan_down_payment`: integer
- `loan2_loan_closing_costs`: integer
- `loan3_loan_name`: string
- `loan3_loan_amount`: integer
- `loan3_loan_interest_rate`: float
- `loan3_loan_term`: integer
- `loan3_loan_down_payment`: integer
- `loan3_loan_closing_costs`: integer

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
| address | string | Full property address including street, city, state, zip, and country |
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

### Example User Object
```json
"bjmar867@gmail.com": {
  "first_name": "BJ",
  "last_name": "Marshall",
  "name": "BJ Marshall",
  "email": "bjmar867@gmail.com",
  "phone": "+14435465716",
  "password": "pbkdf2:sha256:600000$RW1h6Oalhp4zutww$bfea68cc108126cb1673d76bd8b86c3551d3d8533e1b66412218ce6b1b79d2af",
  "role": "Admin"
}
```

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