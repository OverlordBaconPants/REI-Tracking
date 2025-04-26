# Project Structure

This document provides an overview of the REI-Tracker application's project structure.

## Directory Structure

```
REI-Tracker/
├── README.md                 # Project overview and setup instructions
├── PLANNING.md               # Project planning and workflow guidelines
├── TASKS.md                  # Task list and progress tracking
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment variables
├── pytest.ini                # Pytest configuration
├── wsgi.py                   # WSGI entry point for production servers
├── src/                      # Source code
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main application module
│   ├── config.py             # Configuration settings
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   ├── base_model.py     # Base model class
│   │   ├── user.py           # User model
│   │   ├── property.py       # Property model
│   │   ├── transaction.py    # Transaction model
│   │   ├── analysis.py       # Analysis model
│   │   └── category.py       # Category model
│   ├── repositories/         # Data repositories
│   │   ├── __init__.py
│   │   ├── base_repository.py # Base repository class
│   │   ├── user_repository.py # User repository
│   │   ├── property_repository.py # Property repository
│   │   ├── transaction_repository.py # Transaction repository
│   │   ├── analysis_repository.py # Analysis repository
│   │   └── category_repository.py # Category repository
│   ├── services/             # Business logic services
│   │   ├── __init__.py
│   │   ├── file_service.py   # File operations service
│   │   ├── validation_service.py # Data validation service
│   │   ├── geoapify_service.py # Geoapify API service
│   │   └── rentcast_service.py # Rentcast API service
│   ├── routes/               # API routes
│   │   ├── __init__.py
│   │   ├── base_routes.py    # Base routes
│   │   ├── user_routes.py    # User routes
│   │   ├── property_routes.py # Property routes
│   │   ├── transaction_routes.py # Transaction routes
│   │   └── analysis_routes.py # Analysis routes
│   └── utils/                # Utility functions
│       ├── __init__.py
│       ├── logging_utils.py  # Logging utilities
│       ├── file_utils.py     # File utilities
│       └── validation_utils.py # Validation utilities
├── tests/                    # Tests
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_config.py        # Configuration tests
│   ├── test_models/          # Model tests
│   │   ├── __init__.py
│   │   └── test_base_model.py # Base model tests
│   ├── test_repositories/    # Repository tests
│   │   ├── __init__.py
│   │   └── test_base_repository.py # Base repository tests
│   ├── test_services/        # Service tests
│   │   └── __init__.py
│   ├── test_routes/          # Route tests
│   │   ├── __init__.py
│   │   └── test_base_routes.py # Base route tests
│   └── test_utils/           # Utility tests
│       ├── __init__.py
│       └── test_file_utils.py # File utility tests
├── data/                     # Data files
│   ├── categories.json       # Category data
│   ├── properties.json       # Property data
│   ├── transactions.json     # Transaction data
│   ├── users.json            # User data
│   ├── analyses/             # Analysis data files
│   └── uploads/              # Uploaded files
└── docs/                     # Documentation
    ├── project_structure.md  # Project structure documentation
    ├── api_documentation.md  # API documentation
    └── development_guide.md  # Development guide
```

## Module Descriptions

### Models

The `models` package contains Pydantic models that represent the application's data structures:

- `base_model.py`: Base model class with common functionality
- `user.py`: User model for authentication and user management
- `property.py`: Property model for real estate property management
- `transaction.py`: Transaction model for financial transaction management
- `analysis.py`: Analysis model for property investment analysis
- `category.py`: Category model for income and expense categorization

### Repositories

The `repositories` package contains repository classes that handle data persistence:

- `base_repository.py`: Base repository class with common CRUD operations
- `user_repository.py`: User repository for user data persistence
- `property_repository.py`: Property repository for property data persistence
- `transaction_repository.py`: Transaction repository for transaction data persistence
- `analysis_repository.py`: Analysis repository for analysis data persistence
- `category_repository.py`: Category repository for category data persistence

### Services

The `services` package contains service classes that implement business logic:

- `file_service.py`: File service for file operations
- `validation_service.py`: Validation service for data validation
- `geoapify_service.py`: Geoapify service for address services
- `rentcast_service.py`: Rentcast service for property valuation services

### Routes

The `routes` package contains Flask blueprints that define API routes:

- `base_routes.py`: Base routes for health check and static files
- `user_routes.py`: User routes for authentication and user management
- `property_routes.py`: Property routes for property management
- `transaction_routes.py`: Transaction routes for transaction management
- `analysis_routes.py`: Analysis routes for analysis management

### Utils

The `utils` package contains utility functions and classes:

- `logging_utils.py`: Logging utilities for consistent logging
- `file_utils.py`: File utilities for file operations
- `validation_utils.py`: Validation utilities for data validation

## Data Storage

The application uses JSON files for data storage:

- `data/categories.json`: Category data
- `data/analyses/`: Analysis data files (one per analysis)
- `data/uploads/`: Uploaded files (e.g., transaction documentation)
- `data/users.json`: User data
- `data/properties.json`: Property data
- `data/transactions.json`: Transaction data

## Configuration

The application uses environment variables for configuration, with defaults defined in the `config.py` module. The `.env.example` file provides a template for the required environment variables.

## Testing

The application uses pytest for testing, with fixtures defined in `conftest.py`. Tests are organized by module type (models, repositories, services, routes, utils).
