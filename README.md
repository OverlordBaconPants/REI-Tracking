# 🏠  Real Estate Analysis and Portfolio Tracking 📊 

## Project Overview
This project provides a Flask- and Dash-based Python web application for real estate investors and partners to manage their investment portfolios. The application enables comprehensive real estate investment tracking, analysis, and management with the following key features:

🏠 Property Portfolio Management - Track properties, assign partner equity shares, designate property managers, and monitor performance metrics
💰 Financial Calculation Engine - Calculate investment metrics including CoC return, ROI, cap rates, and DSCR with proper decimal handling
💵 Transaction Management System - Record, categorize, filter, and report on property-related financial transactions with equity-based splitting, reimbursement tracking, property-specific permissions, and comprehensive filtering capabilities
📊 Analysis System - Conduct detailed property analyses across multiple strategies (LTR, BRRRR, Lease Option, Multi-Family, PadSplit)
📈 Property Valuation - Integrate with RentCast API for accurate property comps and market valuations with correlation scoring, range indicators, and market statistics
🌐 Address Services - Leverage Geoapify for address validation, autocomplete, and geocoding
📱 Dynamic Dashboards - View customized KPI reports, equity tracking, and portfolio summaries
🔒 User Authentication - Secure multi-user access with role-based permissions, session management, and security features
📄 Report Generation - Create professional PDF reports for analyses, transactions, and portfolio performance
🎨 User Interface - Responsive design with Bootstrap Spacelab theme, modular JavaScript architecture, and accessibility optimizations

## Core Calculation Components

The application includes robust financial calculation components:

- **Money and Percentage Classes**: Handle monetary values and percentages with proper decimal precision
- **Validation Framework**: Comprehensive validation with error collection and reporting using Pydantic V2
- **Loan Model**: Fully Pydantic-based model with custom validators for Money and Percentage types
- **LoanDetails Model**: Support for various loan types (standard amortizing, interest-only, zero-interest)
- **MonthlyPayment Class**: Track principal and interest components of payments
- **Safe Calculation Decorator**: Error handling for calculations with default values
- **Infinite Value Support**: Handle special cases like infinite ROI when no cash is invested

## Analysis System

The application features a comprehensive property investment analysis system:

- **Base Analysis Class**: Provides common functionality for all analysis types, including validation and core financial calculations
- **Specialized Analysis Types**:
  - **LTR (Long-Term Rental)**: Traditional rental property analysis
  - **BRRRR (Buy, Rehab, Rent, Refinance, Repeat)**: Analysis for the BRRRR investment strategy
  - **Lease Option**: Analysis for lease-to-own arrangements
  - **Multi-Family**: Analysis for multi-unit properties with specialized metrics
  - **PadSplit**: Analysis for room-by-room rental strategy
- **Key Metrics**:
  - Cash flow calculation (monthly and annual)
  - Cash-on-cash return and ROI
  - Cap rate and GRM (Gross Rent Multiplier)
  - DSCR (Debt Service Coverage Ratio)
  - Expense ratio and breakeven occupancy
  - MAO (Maximum Allowable Offer) calculation
- **Factory Pattern**: Simple API for creating the appropriate analysis type based on strategy
- **Complete CRUD Operations**:
  - Create, read, update, and delete analyses via RESTful API
  - Specialized validation for each analysis type
  - Data normalization for consistent storage
  - Calculation endpoint for real-time metrics

## Investment Metrics Calculator

The application includes specialized investment metric calculators:

- **ROI Calculation**: Comprehensive ROI calculation considering both cash flow and equity appreciation
- **Equity Tracking**: Project equity growth over time with appreciation and loan paydown components
- **Year-by-Year Projections**: Detailed yearly equity projections with property value and loan balance tracking
- **Investment-Specific Metrics**:
  - Cash-on-cash return calculation
  - Cap rate calculation
  - Debt service coverage ratio (DSCR)
  - Expense ratio calculation
  - Gross rent multiplier (GRM)
  - Price per unit for multi-family properties
  - Breakeven occupancy calculation

## Financial Calculations

The application provides comprehensive financial calculations for real estate investments:

- **Detailed Cash Flow Breakdown**: Calculate monthly cash flow with comprehensive expense categories
  - Income tracking (rental, parking, laundry, storage, other)
  - Expense tracking (property taxes, insurance, utilities, management fees, CapEx, vacancy, repairs)
  - Multi-family specific expenses (common area maintenance, elevator maintenance, staff payroll, security)
  - Loan payment tracking for multiple loans
  
- **Balloon Payment Analysis**: Analyze the impact of balloon payments on investment returns
  - Pre-balloon and post-balloon cash flow calculations
  - Balloon amount and date projections
  - Refinance loan modeling after balloon payment
  - Post-balloon value calculations with annual increases
  
- **Lease Option Calculations**: Specialized calculations for lease option investments
  - Total rent credits calculation over option term
  - Effective purchase price calculation (strike price minus credits)
  - Rent credit percentage calculation
  - Option equity calculation based on property appreciation
  
- **Refinance Impact Analysis**: Analyze the impact of refinancing on cash flow and returns
  - Pre-refinance and post-refinance cash flow comparison
  - Monthly and annual savings calculations
  - Break-even analysis for closing costs
  - Interest savings calculation over loan term
  - Cash-out amount calculation

## Transaction Filtering System

The application includes a comprehensive transaction filtering system:

- **Property Filtering**: Filter transactions by specific property or multiple properties
- **Date Range Filtering**: Filter transactions by date range with validation
- **Category and Type Filtering**: Filter by transaction type (income/expense) and category
- **Description Search**: Search transactions by description text
- **Multi-property View**: View and group transactions across multiple properties
- **Property-specific Summaries**: Calculate financial summaries (income, expenses, net) by property
- **User-specific Visibility**: Limit transaction visibility based on user's property access permissions
- **Admin Override**: Administrators have full visibility across all properties
- **API Endpoints**: RESTful API endpoints for filtered transactions, grouped transactions, and property summaries

## Partner Equity Management

The application includes a comprehensive partner equity management system:

- **Partner Management**: Add, update, and remove partners with equity share assignment
- **Property Manager Designation**: Designate a partner as property manager with specific permissions
- **Equity Validation**: Ensure total equity shares equal 100% with automatic validation
- **Visibility Settings**: Configure partner-specific visibility settings for financial data
  - Financial details visibility
  - Transaction history visibility
  - Partner contributions visibility
  - Property documents visibility
- **Contribution Tracking**: Record and track partner contributions and distributions
  - Support for both contributions (money in) and distributions (money out)
  - Date tracking for all financial movements
  - Notes and documentation for contributions and distributions
- **Contribution Reporting**: Generate reports on partner contributions and distributions
  - Total contributions by partner
  - Contribution history with filtering options
  - Distribution tracking and history

## Reimbursement System

The application features a sophisticated reimbursement tracking system:

- **Status Tracking**: Track reimbursement status (pending, in_progress, completed) with appropriate validations
- **Documentation Support**: Upload and store documentation for reimbursements
- **Automatic Processing**: Automatically handle reimbursements for wholly-owned properties
- **Equity-Based Calculation**: Calculate reimbursement amounts based on partner equity shares
- **Partner Shares**: Track individual partner shares for each reimbursement
- **API Endpoints**: RESTful API endpoints for updating reimbursement status, calculating shares, and retrieving pending/owed reimbursements
- **User-Specific Views**: View reimbursements pending for the current user and reimbursements owed to others

## Transaction Reporting

The application includes comprehensive transaction reporting capabilities:

- **PDF Report Generation**: Generate professional PDF reports with transaction details
  - Property-specific and multi-property reports
  - Customizable date ranges and filtering options
  - Branded report styling with consistent layouts
  - Transaction details with documentation references
  
- **Financial Summaries**: Comprehensive financial summaries with visualizations
  - Income, expense, and net amount calculations
  - Property-specific financial breakdowns
  - Category-based financial analysis
  - Partner equity-based calculations
  
- **Data Visualizations**: Dynamic charts and graphs for financial data
  - Income vs. expense pie charts
  - Category breakdown bar charts
  - Property comparison visualizations
  - Time-based transaction analysis
  
- **Documentation Bundling**: Create ZIP archives of transaction documentation
  - Organized folder structure by property and date
  - README file with transaction summaries
  - Support for various document types
  - Secure file handling and naming

## KPI Comparison Reports

The application features a robust KPI comparison reporting system:

- **Planned vs. Actual Metrics**: Compare projected performance from analyses with actual results
  - Side-by-side comparison of key financial metrics
  - Variance calculation and highlighting
  - Performance scoring based on metric comparisons
  
- **Comprehensive Metrics Coverage**: Compare a wide range of investment metrics
  - Monthly income and expenses
  - Net Operating Income (NOI)
  - Cash flow
  - Cap rate
  - Cash-on-cash return
  - Debt Service Coverage Ratio (DSCR)
  
- **PDF Report Generation**: Create professional PDF reports with detailed comparisons
  - Property details and performance summary
  - KPI comparison tables with variance calculations
  - Data visualizations for key metrics
  - Support for custom date ranges
  
- **Data Visualizations**: Dynamic charts for metric comparisons
  - Income vs. expenses bar charts
  - NOI and cash flow comparisons
  - Investment metrics comparisons

## Dashboard Routing System with Authentication

The application features a secure dashboard routing system with authentication:

- **Secure Dashboard Routes**: All dashboard routes require authentication
  - Login requirement for all dashboard access
  - Session-based authentication with proper timeout
  - CSRF protection for all dashboard routes
  
- **Dashboard Landing Page**: Central hub for accessing specialized dashboards
  - Card-based navigation to different dashboard types
  - Visual indicators for dashboard status (available, coming soon)
  - Mobile-responsive layout for all screen sizes
  
- **Dashboard-Specific Permissions**: Fine-grained access control
  - Property-based access control for dashboards
  - Role-based permissions (owner, manager, viewer)
  - Admin override for full access
  
- **Mobile-Responsive Design**: Access dashboards from any device
  - Responsive layouts for different screen sizes
  - Touch-friendly controls and visualizations
  - Optimized chart rendering for mobile devices
  
- **Error Handling**: Comprehensive error handling for dashboard routes
  - Custom error pages for authentication failures
  - Access denied page for permission issues
  - Detailed logging for security events

## Portfolio Dashboard

The application features a comprehensive portfolio dashboard:

- **Portfolio Value and Equity Visualizations**: View your entire portfolio at a glance
  - Equity distribution pie chart with property breakdown
  - Total portfolio value calculation and display
  - Total equity and monthly equity gain metrics
  
- **Cash Flow Visualizations**: Analyze cash flow across your portfolio
  - Cash flow by property bar chart
  - Net monthly cash flow calculation and display
  - Color-coded indicators for positive/negative cash flow
  
- **Income and Expense Breakdown**: Understand your financial performance
  - Monthly income by property pie chart
  - Monthly expenses breakdown by category
  - Detailed expense category analysis
  
- **Property Comparison Table**: Compare key metrics across properties
  - Property details with equity share percentages
  - Monthly income and expense breakdown
  - Net cash flow with visual indicators
  - Total equity and monthly equity gain
  - Cash on cash return calculation
  
- **Mobile-Responsive Design**: Access your dashboard from any device
  - Responsive layout for different screen sizes
  - Touch-friendly controls and visualizations
  - Optimized chart rendering for mobile devices
  
- **Time Period Filtering**: Analyze performance over different time periods
  - Filter by last 30 days, 90 days, 6 months, 12 months, or all time
  - Dynamic recalculation of metrics based on selected period
  - Consistent date range application across all visualizations

## Additional Dashboards and Tools

The application includes several specialized dashboards and tools:

- **Amortization Dashboard**: Track loan amortization schedules and equity growth
  - Loan balance and equity visualization
  - Principal and interest breakdown
  - Amortization schedule
  - Equity growth projections
  
- **Transactions Dashboard**: Analyze property transactions with advanced filtering and reporting
  - Comprehensive filtering system with property, type, date range, and description search
  - Reimbursement status filtering with conditional display for wholly-owned properties
  - Mobile-optimized transaction table with responsive column layout
  - Visual indicators for transaction types and status
  - PDF report generation with transaction details and financial summaries
  - Document bundling with ZIP archive creation for transaction documentation
  - Touch-friendly controls and inline document access
  
- **KPI Dashboard**: Monitor key performance indicators for properties
  - Actual vs. projected metrics comparison with variance highlighting
  - Interactive property selector with standardized address display
  - Comprehensive KPI metrics including NOI, cap rate, cash-on-cash return, and DSCR
  - Data quality assessment with confidence level indicators
  - Mobile-responsive design with optimized visualizations
  - Integration with KPI comparison tool for detailed analysis
  
- **KPI Comparison Tool**: Compare planned vs. actual property performance
  - Side-by-side comparison of projected and actual metrics
  - Monthly income and expense comparison with variance calculation
  - Investment metrics comparison (cap rate, cash-on-cash return, DSCR)
  - Performance status indicators (favorable/unfavorable)
  - PDF report generation with detailed metrics and visualizations
  - Support for custom date ranges for targeted analysis

- **MAO Calculator**: Calculate the maximum allowable offer for a property
  - Support for BRRRR-specific MAO calculation
  - Support for different investment strategies (LTR, BRRRR, Lease Option, Multi-Family, PadSplit)
  - Detailed calculation breakdown with step-by-step explanation
  - Print-friendly results for sharing and documentation
  - Integration with property comps data

- **Occupancy Rate Calculator**: Calculate and analyze occupancy rates for multi-family properties
  - Track occupancy over time with visual indicators
  - Calculate revenue impact of occupancy changes
  - Compare to market averages with progress bar visualization
  - Calculate breakeven occupancy rate based on fixed and variable expenses
  - Print-friendly results for sharing and documentation

## User Interface & Frontend Architecture

The application features a modern, responsive user interface with a modular JavaScript architecture:

- **Responsive Design**: Bootstrap Spacelab theme with mobile-first approach
  - Mobile-optimized layouts for all screen sizes
  - Responsive tables and forms with touch-friendly controls
  - Consistent styling with navigation and breadcrumbs
  - Optimized for both desktop and mobile devices
  
- **Modular JavaScript Architecture**: Structured, maintainable frontend code
  - Base module for shared functionality and environment detection
  - Module manager for dynamic loading of page-specific code
  - Dependency management between modules
  - Event-based communication between components
  
- **Enhanced UI Components**: Rich, interactive user interface elements
  - Form system with comprehensive client-side validation
  - Notification system with categorized messages and accessibility features
  - Data visualization components with responsive charts
  - Document viewers and managers for transaction attachments
  
- **Accessibility Optimizations**: Inclusive design for all users
  - ARIA attributes for screen reader compatibility
  - Keyboard navigation support for all interactive elements
  - Focus management for modals and dynamic content
  - High contrast mode support
  
- **Mobile Optimizations**: Enhanced experience on mobile devices
  - Enhanced touch targets for better tap accuracy
  - Mobile keyboard handling for improved form input
  - Visual feedback for touch interactions
  - Performance optimizations for mobile networks
  
- **Performance Features**: Fast, responsive user experience
  - Lazy loading of non-essential components
  - Resource optimization based on device capabilities
  - Reduced motion support for users with motion sensitivity
  - Print-specific styling for reports and documentation

## Loan Tracking and Management

The application includes a comprehensive loan tracking and management system:

- **Multiple Loan Types**: Support for various financing scenarios
  - Primary mortgage financing
  - Secondary/seller financing
  - Refinance loans
  - Additional loans for renovations or improvements

- **Loan Details Tracking**: Comprehensive tracking of loan information
  - Loan amount and interest rate
  - Loan term and start date
  - Payment frequency and amount
  - Loan type classification

- **Balance and Equity Calculations**: Track your loan progress over time
  - Remaining balance calculation based on amortization
  - Principal equity calculation from loan payments
  - Total equity tracking including appreciation
  - Loan-to-value ratio monitoring

- **Monthly Equity Gain Tracking**: Understand the equity building process
  - Principal vs. interest breakdown for each payment
  - Monthly equity gain from loan payments
  - Cumulative equity gained over time
  - Amortization schedule generation

- **Loan Comparison Tools**: Compare different loan scenarios
  - Side-by-side comparison of loan terms
  - Total interest paid calculation
  - Monthly payment comparison
  - Break-even analysis for refinancing

## Bulk Transaction Import

The application features a robust bulk transaction import system:

- **File Format Support**: Import transactions from CSV and Excel files
  - Support for multiple file encodings (UTF-8, Latin1, ISO-8859-1, CP1252)
  - Automatic file type detection and appropriate parsing
  - Error handling for malformed files

- **Column Mapping Interface**: Flexible mapping of file columns to transaction fields
  - Smart auto-mapping based on common column names
  - Required field validation
  - Preview of mapping results

- **Data Validation & Cleaning**: Comprehensive validation of imported data
  - Required field validation
  - Data type validation and conversion
  - Automatic data cleaning and normalization
  - Duplicate transaction detection

- **Import Results Reporting**: Detailed feedback on import results
  - Import statistics (total rows, successful imports, skipped rows)
  - Detailed error reporting by row and field
  - Modification tracking for data transformations

## Property Comps & Valuation

The application features a sophisticated property valuation system:

- **Comparable Properties**: Fetch and analyze comparable properties from RentCast API
- **Correlation Scoring**: Calculate similarity scores between subject property and comps based on:
  - Distance from subject property
  - Bedroom count similarity
  - Bathroom count similarity
  - Square footage similarity
  - Year built similarity
- **Value Estimation**: Generate property value estimates with range indicators:
  - Low value estimate
  - High value estimate
  - Weighted average estimate based on correlation scores
- **Market Statistics**: Access location-based market data for comprehensive analysis
- **Session-based Rate Limiting**: Prevent API abuse with configurable rate limits
- **Data Persistence**: Store comps data for historical analysis and comparison

## Tech Stack
- Python
- Pydantic for data validation
- PyTest for testing
- Bootstrap Spacelab theme for UI
- JavaScript with modular architecture

## Setup and Installation

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt

# Create environment variables file from template
cp .env.example .env
```

## Project Structure

```
project_name/
├── README.md
├── PLANNING.md
├── TASK.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   │   ├── modules/
│   │   │   ├── base.js
│   │   │   ├── main.js
│   │   │   └── notifications.js
│   │   └── images/
│   ├── templates/
│   └── utils/
├── tests/
│   ├── __init__.py
│   ├── test_models/
│   ├── test_routes/
│   ├── test_services/
│   └── test_utils/
└── docs/
```

## Style & Conventions
- Python code follows PEP8 standards
- Type hints are used throughout the codebase
- Code is formatted with `black`
- JavaScript follows modular architecture with ES6 modules
- Naming conventions:
  - `snake_case` for variables and functions
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

## Testing

### Backend Tests
Run backend tests with pytest:

```bash
pytest
```

### Frontend Tests
The project includes a comprehensive frontend testing framework for JavaScript components:

```bash
# Run all frontend tests
cd tests/test_frontend
./run_tests.py

# Run a specific test file
./run_tests.py --test-file test_minimal.py

# Run tests with verbose output
./run_tests.py --verbose

# Run tests with browser visible (not headless)
./run_tests.py --no-headless

# Generate HTML report
./run_tests.py --html-report

# Generate coverage report
./run_tests.py --coverage
```

The frontend testing framework uses:
- **pytest** as the test runner
- **Selenium WebDriver** for browser automation
- **Chrome** (headless by default) as the browser for testing

All required dependencies for frontend testing are included in the main project's `requirements.txt` file. For more details, see the [Frontend Testing README](tests/test_frontend/README.md).

## Documentation
- All functions include Google-style docstrings
- Complex logic includes inline comments with `# Reason:` prefix
