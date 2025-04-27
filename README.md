# 🏠  Real Estate Analysis and Portfolio Tracking 📊 

## Project Overview
This project provides a Flask- and Dash-based Python web application for real estate investors and partners to manage their investment portfolios. The application enables comprehensive real estate investment tracking, analysis, and management with the following key features:

🏠 Property Portfolio Management - Track properties, assign partner equity shares, designate property managers, and monitor performance metrics
💰 Financial Calculation Engine - Calculate investment metrics including CoC return, ROI, cap rates, and DSCR with proper decimal handling
💵 Transaction Management System - Record, categorize, and report on property-related financial transactions with equity-based splitting
📊 Analysis System - Conduct detailed property analyses across multiple strategies (LTR, BRRRR, Lease Option, Multi-Family, PadSplit)
📈 Property Valuation - Integrate with RentCast API for accurate property comps and market valuations with correlation scoring, range indicators, and market statistics
🌐 Address Services - Leverage Geoapify for address validation, autocomplete, and geocoding
📱 Dynamic Dashboards - View customized KPI reports, equity tracking, and portfolio summaries
🔒 User Authentication - Secure multi-user access with role-based permissions, session management, and security features
📄 Report Generation - Create professional PDF reports for analyses, transactions, and portfolio performance

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
- Naming conventions:
  - `snake_case` for variables and functions
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

## Testing
Run tests with pytest:

```bash
pytest
```

## Documentation
- All functions include Google-style docstrings
- Complex logic includes inline comments with `# Reason:` prefix
