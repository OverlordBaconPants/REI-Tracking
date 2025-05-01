# 🏠 Real Estate Analysis and Portfolio Tracking 📊 

## Project Overview
This project provides a Flask- and Dash-based Python web application for real estate investors and partners to manage their investment portfolios. The application enables comprehensive real estate investment tracking, analysis, and management with the following key features:

🏠 Property Portfolio Management - Track properties, assign partner equity shares, designate property managers, and monitor performance metrics  
💰 Financial Calculation Engine - Calculate investment metrics including CoC return, ROI, cap rates, and DSCR with proper decimal handling  
💵 Transaction Management System - Record, categorize, filter, and report on property-related financial transactions with equity-based splitting, reimbursement tracking, property-specific permissions, and comprehensive filtering capabilities  
📊 Analysis System - Conduct detailed property analyses across multiple strategies (LTR, BRRRR, Lease Option, Multi-Family, PadSplit)  
📈 Property Valuation - Integrate with RentCast API for accurate property comps and market valuations with correlation scoring, range indicators, and market statistics  
🌐 Address Services - Leverage Geoapify for address validation, autocomplete, and geocoding  
📱 Dynamic Dashboards - View customized KPI reports, equity tracking, and portfolio summaries  
🔒 User Authentication - Secure multi-user access with role-based permissions, session management, security features, and an informative landing page for unauthenticated users  
📄 Report Generation - Create professional PDF reports for analyses, transactions, and portfolio performance  
🎨 User Interface - Responsive design with Bootstrap Spacelab theme, modular JavaScript architecture, and accessibility optimizations  

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/REI-Tracker.git
   cd REI-Tracker
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your configuration settings.

### Running the Application

To run the application in development mode:

```bash
python -m src.main
```

Or use the startup script:

```bash
./startup.sh
```

The application will be available at http://localhost:5000.

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
  - Properties displayed in ascending alphanumeric order for consistent navigation
  - Standardized address formatting for clear property identification
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
  - Consolidated with comparable properties functionality for improved UI organization

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
- **Consistent Functionality**: The "Run Comps" button works identically for both new and existing analyses
  - Standardized field names ensure property values display correctly in all contexts
  - Address-based comps fetching for new analyses before they're saved
  - Analysis ID-based comps fetching for existing analyses

## API Documentation

REI-Tracker provides a comprehensive REST API for interacting with the application programmatically.

### Base Routes

#### Health Check

```
GET /health
```

Returns the health status of the API.

**Response**:
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

#### API Version

```
GET /api/version
```

Returns the API version information.

**Response**:
```json
{
  "version": "1.0.0",
  "name": "REI-Tracker API"
}
```

### User Routes

#### Register

```
POST /api/users/register
```

Registers a new user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user"
}
```

#### Login

```
POST /api/users/login
```

Logs in a user.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Get Current User

```
GET /api/users/me
```

Gets the current user.

#### Update User

```
PUT /api/users/<user_id>
```

Updates a user.

**Parameters**:
- `user_id`: The ID of the user to update

### Property Routes

- `GET /api/properties` - List all properties
- `GET /api/properties/{id}` - Get property details
- `POST /api/properties` - Create a new property
- `PUT /api/properties/{id}` - Update a property
- `DELETE /api/properties/{id}` - Delete a property

### Transaction Routes

- `GET /api/transactions` - List all transactions
- `GET /api/transactions/{id}` - Get transaction details
- `POST /api/transactions` - Create a new transaction
- `PUT /api/transactions/{id}` - Update a transaction
- `DELETE /api/transactions/{id}` - Delete a transaction
- `POST /api/transactions/import` - Bulk import transactions

### Analysis Routes

- `GET /api/analysis/property/{id}` - Get property analysis
- `GET /api/analysis/portfolio` - Get portfolio analysis

### Error Responses

#### 400 Bad Request

```json
{
  "success": false,
  "errors": {
    "field_name": ["Error message"]
  }
}
```

#### 401 Unauthorized

```json
{
  "success": false,
  "errors": {
    "_error": ["Not logged in"]
  }
}
```

## Project Structure

The project follows a modular structure with clear separation of concerns:

```
REI-Tracker/
├── README.md                 # Project overview and setup instructions
├── PLANNING.md               # Project planning and workflow guidelines
├── TASKS.md                  # Task list and progress tracking
├── DATA_STRUCTURES.md        # Comprehensive documentation of all data structures
├── AUTOMATED_TESTING_IMPLEMENTATION.md # Automated testing implementation plan
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── pytest.ini                # Pytest configuration
├── wsgi.py                   # WSGI entry point for production servers
├── app.py                    # Main application module
├── __init__.py               # Package initialization
├── startup.sh                # Startup script for development
├── models/                   # Data models
│   ├── __init__.py
│   └── models.py             # Database models
├── routes/                   # API routes
│   ├── analyses.py           # Analysis routes
│   ├── api.py                # API routes
│   ├── app.py                # App routes
│   ├── auth.py               # Authentication routes
│   ├── dashboards.py         # Dashboard routes
│   ├── main.py               # Main routes
│   ├── monitor.py            # Monitoring routes
│   ├── properties.py         # Property routes
│   └── transactions.py       # Transaction routes
├── services/                 # Business logic services
│   ├── analysis_calculations.py # Analysis calculations
│   ├── analysis_schema.py    # Analysis schema validation
│   ├── analysis_service.py   # Analysis service
│   ├── property_kpi_service.py # Property KPI service
│   ├── report_generator.py   # Report generation service
│   ├── transaction_import_service.py # Transaction import service
│   ├── transaction_report_generator.py # Transaction report generator
│   ├── transaction_service.py # Transaction service
│   └── user_service.py       # User service
├── static/                   # Static assets
│   ├── css/                  # CSS files
│   │   └── styles.css        # Main stylesheet
│   ├── images/               # Image files
│   │   ├── logo.png          # Logo image
│   │   └── logo-blue.png     # Blue logo variant
│   └── js/                   # JavaScript files
│       ├── base.js           # Base JavaScript functionality
│       ├── config.js         # Configuration
│       ├── main.js           # Main JavaScript functionality
│       ├── notifications.js  # Notification system
│       ├── analysis/         # Analysis-specific JavaScript
│       │   ├── brrrr.js      # BRRRR analysis
│       │   ├── calculator.js # Analysis calculator
│       │   ├── comps_handler.js # Comps handler
│       │   ├── core.js       # Core analysis functionality
│       │   ├── form_handler.js # Form handling
│       │   ├── lease_option.js # Lease option analysis
│       │   ├── ltr.js        # Long-term rental analysis
│       │   ├── multi_family.js # Multi-family analysis
│       │   ├── multi-family.js # Alternative multi-family analysis
│       │   ├── property_details.js # Property details
│       │   ├── registry.js   # Analysis registry
│       │   ├── renderer.js   # Analysis renderer
│       │   ├── ui_helpers.js # UI helpers
│       │   └── validators.js # Validators
│       └── modules/          # JavaScript modules
│           ├── add_properties.js # Add properties
│           ├── add_transactions.js # Add transactions
│           ├── analysis.js   # Analysis module
│           ├── auth.js       # Authentication module
│           ├── bulk_import.js # Bulk import
│           ├── comps_handler.js # Comps handler
│           ├── dashboards.js # Dashboards
│           ├── edit_properties.js # Edit properties
│           ├── edit_transactions.js # Edit transactions
│           ├── kpi_comparison.js # KPI comparison
│           ├── kpi_dashboard.js # KPI dashboard
│           ├── landing.js    # Landing page
│           ├── loan_term_toggle.js # Loan term toggle
│           ├── main.js       # Main module
│           ├── mao_calculator.js # MAO calculator
│           ├── password_validation.js # Password validation
│           ├── remove_properties.js # Remove properties
│           ├── view_edit_analysis.js # View/edit analysis
│           ├── view_transactions.js # View transactions
│           └── welcome.js    # Welcome page
├── templates/                # HTML templates
│   ├── 403.html             # 403 error page
│   ├── 404.html             # 404 error page
│   ├── 500.html             # 500 error page
│   ├── base.html            # Base template
│   ├── bulk_import.html     # Bulk import page
│   ├── forgot_password.html # Forgot password page
│   ├── index.html           # Index page
│   ├── landing.html         # Landing page
│   ├── login.html           # Login page
│   ├── new_user_welcome.html # New user welcome page
│   ├── signup.html          # Signup page
│   ├── analyses/            # Analysis templates
│   │   ├── _analysis_cards.html # Analysis cards partial
│   │   ├── _loan_section.html # Loan section partial
│   │   ├── create_analysis.html # Create analysis page
│   │   ├── kpi_comparison.html # KPI comparison page
│   │   ├── mao_calculator.html # MAO calculator page
│   │   └── view_edit_analysis.html # View/edit analysis page
│   ├── dashboards/          # Dashboard templates
│   │   ├── dash_amortization.html # Amortization dashboard
│   │   └── dash_transactions.html # Transactions dashboard
│   ├── main/                # Main templates
│   │   ├── amortization.html # Amortization page
│   │   ├── dashboards.html  # Dashboards page
│   │   ├── main.html        # Main page
│   │   ├── portfolio.html   # Portfolio page
│   │   ├── properties.html  # Properties page
│   │   └── transactions.html # Transactions page
│   ├── properties/          # Property templates
│   │   ├── add_properties.html # Add properties page
│   │   ├── edit_properties.html # Edit properties page
│   │   ├── remove_properties.html # Remove properties page
│   │   └── logs/            # Property logs
│   │       └── app.log.1    # Application log
│   └── transactions/        # Transaction templates
│       ├── add_transactions.html # Add transactions page
│       ├── bulk_import.html # Bulk import page
│       ├── edit_transactions.html # Edit transactions page
│       ├── remove_transactions.html # Remove transactions page
│       └── view_transactions.html # View transactions page
├── utils/                    # Utility functions
│   ├── api_mappers.py       # API mappers
│   ├── calculators.py       # Calculators
│   ├── comps_handler.py     # Comps handler
│   ├── converters.py        # Converters
│   ├── error_handling.py    # Error handling
│   ├── financial_calculator.py # Financial calculator
│   ├── flash.py             # Flash messages
│   ├── json_handler.py      # JSON handler
│   ├── mao_calculator.py    # MAO calculator
│   ├── money.py             # Money utilities
│   ├── response_handler.py  # Response handler
│   ├── standardized_metrics.py # Standardized metrics
│   ├── utils.py             # General utilities
│   └── validators.py        # Validators
├── dash_apps/                # Dash applications
│   ├── __init__.py
│   ├── dash_amortization.py # Amortization dashboard
│   ├── dash_portfolio.py    # Portfolio dashboard
│   └── dash_transactions.py # Transactions dashboard
├── data/                     # Data files
│   └── categories.json      # Category data
├── flask_session/           # Flask session files
│   ├── 2029240f6d1128be89ddc32729463129
│   ├── 8c3f3bf6892ab30c7fca76c70af9cd80
│   └── e3fc915900934af5eb1f2680a17026b1
├── logs/                     # Log files
│   └── .gitkeep             # Git keep file
└── tests/                    # Tests
    ├── test_frontend/       # Frontend tests
    │   ├── conftest.py      # Pytest fixtures
    │   ├── run_tests.py     # Test runner script
    │   ├── base/            # Test framework foundation
    │   │   ├── __init__.py
    │   │   ├── base_test.py # Base test class
    │   │   ├── browser.py   # Browser setup
    │   │   ├── config.py    # Test configuration
    │   │   └── logger.py    # Test logging
    │   ├── page_objects/    # Page Object Models
    │   │   ├── __init__.py
    │   │   ├── base_page.py # Base page object
    │   │   ├── login_page.py # Login page object
    │   │   ├── property/    # Property page objects
    │   │   ├── transaction/ # Transaction page objects
    │   │   ├── analysis/    # Analysis page objects
    │   │   ├── dashboard/   # Dashboard page objects
    │   │   └── components/  # Component page objects
    │   ├── test_data/       # Test data
    │   │   ├── __init__.py
    │   │   ├── users.py     # User test data
    │   │   ├── properties.py # Property test data
    │   │   ├── transactions.py # Transaction test data
    │   │   ├── analyses.py  # Analysis test data
    │   │   └── test_files/  # Test files
    │   ├── utilities/       # Test utilities
    │   │   ├── __init__.py
    │   │   ├── data_generator.py # Data generator
    │   │   ├── screenshot.py # Screenshot utilities
    │   │   ├── wait_helper.py # Wait helpers
    │   │   └── assertion_helper.py # Assertion helpers
    │   ├── workflows/       # Test workflows
    │   │   ├── __init__.py
    │   │   ├── auth_workflows.py # Authentication workflows
    │   │   ├── property_workflows.py # Property workflows
    │   │   ├── transaction_workflows.py # Transaction workflows
    │   │   └── analysis_workflows.py # Analysis workflows
    │   └── tests/           # Test cases
    │       ├── test_auth/   # Authentication tests
    │       ├── test_property/ # Property tests
    │       ├── test_transaction/ # Transaction tests
    │       ├── test_analysis/ # Analysis tests
    │       ├── test_dashboard/ # Dashboard tests
    │       └── test_integrated/ # Integrated tests
    ├── test_models/         # Model tests
    ├── test_services/       # Service tests
    ├── test_routes/         # Route tests
    └── test_utils/          # Utility tests
```

## Development Guide

### Coding Standards

#### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Use 4 spaces for indentation.
- Maximum line length is 100 characters.
- Use docstrings for all modules, classes, and functions.

#### Naming Conventions

- Use `snake_case` for variables, functions, and methods.
- Use `PascalCase` for classes.
- Use `UPPER_CASE` for constants.
- Use descriptive names that reflect the purpose of the variable, function, or class.

#### Documentation

- Document all modules, classes, and functions with docstrings.
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Keep documentation up-to-date with code changes.

### Testing

#### Backend Tests
Run backend tests with pytest:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=src
```

#### Test Persona for UI Testing
The project includes a comprehensive test persona for UI testing:

- **Dedicated Test User**: A test user with consistent credentials for authentication testing
- **Diverse Property Portfolio**: Test properties covering different investment strategies
- **Comprehensive Analyses**: Analyses for each property covering all supported strategies
- **Various Loan Scenarios**: Different loan types including standard, balloon, interest-only, etc.
- **Transaction History**: Transactions with different types, categories, and reimbursement statuses
- **MAO Calculation Defaults**: Default values for Maximum Allowable Offer calculations

To set up the test environment with the test persona:

```bash
cd tests/test_frontend
python setup_test_environment.py
```

This will:
1. Create necessary test files (PDFs, etc.)
2. Seed the test database with test persona data
3. Set up directories for test screenshots and reports

#### Frontend Tests
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

All required dependencies for frontend testing are included in the main project's `requirements.txt` file. For more details, see the [Frontend Testing README](tests/test_frontend/README.md) and the [Test Persona Documentation](tests/test_frontend/test_data/README.md).

### Git Workflow

#### Branching Strategy

- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/feature-name`
- Bug fix branches: `bugfix/bug-name`
- Release branches: `release/version`

#### Commit Messages

- Use clear and descriptive commit messages.
- Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- Keep the first line under 50 characters.
- Provide more details in the commit body if necessary.

### Deployment

#### Production Setup

1. Set up a production server with Python 3.9 or higher.
2. Clone the repository and install dependencies.
3. Create a `.env` file with production settings.
4. Set up a WSGI server (e.g., Gunicorn) to run the application.
5. Set up a reverse proxy (e.g., Nginx) to handle requests.

#### Environment Variables

- `FLASK_ENV`: Set to `production` for production environment.
- `SECRET_KEY`: A secure random string for session encryption.
- `GEOAPIFY_API_KEY`: API key for Geoapify services.
- `RENTCAST_API_KEY`: API key for Rentcast services.

## Tech Stack
- Python 3.9+
- Flask web framework
- Plotly Dash for interactive dashboards
- Pydantic for data validation
- PyTest for testing
- Bootstrap Spacelab theme for UI
- JavaScript with modular architecture
