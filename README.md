# 🏠  Real Estate Analysis and Portfolio Tracking 📊 

## Project Overview
This project provides a Flask- and Dash-based Python web application for real estate investors and partners to manage their investment portfolios. The application enables comprehensive real estate investment tracking, analysis, and management with the following key features:

🏠 Property Portfolio Management - Track properties, assign partner equity shares, designate property managers, and monitor performance metrics
💰 Financial Calculation Engine - Calculate investment metrics including CoC return, ROI, cap rates, and DSCR with proper decimal handling
💵 Transaction Management System - Record, categorize, and report on property-related financial transactions with equity-based splitting
📊 Analysis System - Conduct detailed property analyses across multiple strategies (LTR, BRRRR, Lease Option, Multi-Family, PadSplit)
📈 Property Valuation - Integrate with RentCast API for accurate property comps and market valuations
🌐 Address Services - Leverage Geoapify for address validation, autocomplete, and geocoding
📱 Dynamic Dashboards - View customized KPI reports, equity tracking, and portfolio summaries
🔒 User Authentication - Secure multi-user access with role-based permissions and property-specific access controls
📄 Report Generation - Create professional PDF reports for analyses, transactions, and portfolio performance

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