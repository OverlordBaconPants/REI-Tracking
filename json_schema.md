# JSON Schema Documentation

- id: UUID string
- user_id: string
- created_at: ISO 8601 datetime string
- updated_at: ISO 8601 datetime string
- analysis_type: string
- analysis_name: string

- address: string
- square_footage: integer
- lot_size: integer
- year_built: integer

- purchase_price: integer
- after_repair_value: integer
- renovation_costs: integer
- renovation_duration: integer
- cash_to_seller: integer
- closing_costs: integer
- assignment_fee: integer
- marketing_costs: integer

- monthly_rent: integer

- property_taxes: integer
- insurance: integer
- hoa_coa_coop: integer
- management_fee_percentage: float
- capex_percentage: float
- vacancy_percentage: float
- repairs_percentage: float
- utilities: integer
- internet: integer
- cleaning: integer
- pest_control: integer
- landscaping: integer
- padsplit_platform_percentage: float

- initial_loan_name: string
- initial_loan_amount: integer
- initial_loan_interest_rate: float
- initial_loan_term: integer
- initial_loan_down_payment: integer
- initial_loan_closing_costs: integer

- refinance_loan_name: string
- refinance_loan_amount: integer
- refinance_loan_interest_rate: float
- refinance_loan_term: integer
- refinance_loan_down_payment: integer
- refinance_loan_closing_costs: integer

- loan1_loan_name: string
- loan1_loan_amount: integer
- loan1_loan_interest_rate: float
- loan1_loan_term: integer
- loan1_loan_down_payment: integer
- loan1_loan_closing_costs: integer

- loan2_loan_name: string
- loan2_loan_amount: integer
- loan2_loan_interest_rate: float
- loan2_loan_term: integer
- loan2_loan_down_payment: integer
- loan2_loan_closing_costs: integer

- loan3_loan_name: string
- loan3_loan_amount: integer
- loan3_loan_interest_rate: float
- loan3_loan_term: integer
- loan3_loan_down_payment: integer
- loan3_loan_closing_costs: integer

## Analysis Workflow:
1. User selects Create Analysis
2. User selects Analysis Type
3. System displays form fields appropriate for the analysis type in Financial Details tab
4. User enters data
5. System validates data 
6. User submits forms
7. System writes analysis to unique JSON file as raw data (see Background Notes)
8. System shows user the Report Tab, showing calculated metrics formatted as currency or percentages as appropriate
9. System provides an option to Download PDF of the contents of the Reports Tab
10. System provides user options to edit analysis or return to View/Edit Analyses page.
11. When editing an analysis, the system only overwrites fields if the newly-edited value differs from the value stored in the JSON object.
12. The system does not create another unique ID for edits but instead uses the existing ID.

## Background Notes:
1. Store required data in JSON as raw data (str, int, bool, float). Calculated and derived values are created and calculated at run-time.
2. Currency and percentage values are only formatted for the Reports Tab output and reports downloaded as PDF.
3. Currency format follows "$X,XXX.XX" pattern
4. Percentage format follows "XX.XXX%" pattern
5. Date-times are in ISO 8601 format
6. Fields made available to the user depend upon the analysis type selected. Assume null values unless specified otherwise by the user. For example, if performing an LTR analysis, then BRRRR-specific fields will be assumed null
7. Currency and percentage formats are performed at the frontend only for the Reports Tab and when generating reports to download as PDF.