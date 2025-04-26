# Development Guide

This document provides guidelines for developing the REI-Tracker application.

## Getting Started

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

The application will be available at http://localhost:5000.

### Running Tests

To run the tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=src
```

## Project Structure

The project follows a modular structure with clear separation of concerns:

- **Models**: Data models using Pydantic
- **Repositories**: Data persistence layer
- **Services**: Business logic layer
- **Routes**: API endpoints
- **Utils**: Utility functions and classes

See [Project Structure](project_structure.md) for more details.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Use 4 spaces for indentation.
- Maximum line length is 100 characters.
- Use docstrings for all modules, classes, and functions.

### Naming Conventions

- Use `snake_case` for variables, functions, and methods.
- Use `PascalCase` for classes.
- Use `UPPER_CASE` for constants.
- Use descriptive names that reflect the purpose of the variable, function, or class.

### Documentation

- Document all modules, classes, and functions with docstrings.
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Keep documentation up-to-date with code changes.

## Git Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/feature-name`
- Bug fix branches: `bugfix/bug-name`
- Release branches: `release/version`

### Commit Messages

- Use clear and descriptive commit messages.
- Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- Keep the first line under 50 characters.
- Provide more details in the commit body if necessary.

Example:
```
Add user authentication functionality

- Implement user registration
- Implement user login
- Add password hashing
- Add session management
```

### Pull Requests

- Create a pull request for each feature or bug fix.
- Provide a clear description of the changes.
- Reference any related issues.
- Ensure all tests pass before merging.

## Testing

### Test Structure

- Tests are organized by module type (models, repositories, services, routes, utils).
- Each test file corresponds to a module in the application.
- Use descriptive test names that reflect what is being tested.

### Test Coverage

- Aim for at least 80% test coverage.
- Focus on testing business logic and edge cases.
- Use mocks and fixtures to isolate tests.

## API Documentation

See [API Documentation](api_documentation.md) for details on the API endpoints.

## Deployment

### Production Setup

1. Set up a production server with Python 3.9 or higher.
2. Clone the repository and install dependencies.
3. Create a `.env` file with production settings.
4. Set up a WSGI server (e.g., Gunicorn) to run the application.
5. Set up a reverse proxy (e.g., Nginx) to handle requests.

### Environment Variables

- `FLASK_ENV`: Set to `production` for production environment.
- `SECRET_KEY`: A secure random string for session encryption.
- `GEOAPIFY_API_KEY`: API key for Geoapify services.
- `RENTCAST_API_KEY`: API key for Rentcast services.

## Troubleshooting

### Common Issues

- **File permissions**: Ensure that the application has write access to the data directory.
- **API keys**: Verify that the API keys are correctly set in the `.env` file.
- **Database errors**: Check that the JSON files are valid and not corrupted.

### Logging

- Check the log file at `logs/app.log` for error messages.
- Set the log level to `DEBUG` in development for more detailed logs.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Run tests to ensure they pass.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
