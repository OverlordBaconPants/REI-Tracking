# 🏠 REI Tracking Project

## 📝 Description

This project is a Flask- and Dash-based Python web application that allows partners to manage some of the acquisition and disposition details of real estate investments:

- 💰 Adjudicate Incomes and Expenses, and Supporting Reimbursement Details and Documentation along Equity Splits between and among Owning Partners
- 📊 Analyze Potential Real Estate Investments across a Number of Acquisition and Disposition Strategies such as LTR, PadSplit, BRRRR, Lease Options, and Multi-Family Dwellings
- 🏠 Automatically Run Comps to Estimate Subject-Property After Rehab Value
- 📄 Generate PDF Reports for both Analyses and Transaction Histories
- 🏢 Add Properties to Your Portfolio, See Aggregate Portfolio Metrics and Dashboards
- 👥 Add/Edit/Remove Partners to Properties in Your Portfolio, Assigning Equity Share as Appropriate
- 📈 See Key Performance Indicators for both Analyses (Anticipate) and Transaction Histories (Real World)

## ✨ Features

- 🔑 User Authentication (Login/Logout)
- 📝 User Registration
- 🔄 Password Reset
- 🍞 Breadcrumb Navigation
- 🚀 Bootstrap-based Responsive Design
- 💰 Income and Expense Tracking
- 📊 Various Deal Analyses, Including Creative and Conventional Financing and Balloon Payments
- 🏢 Portfolio Logging, Analysis, and Dashboards
- 📊 KPI Reporting (CoC Return, Net Monthly Cash Flow, Amortization Schedules)
- 👥 Partner Equity Split Management

## 🛠️ Technologies Used

- Flask
- Dash (planned)
- Flask-Login
- Werkzeug
- Bootstrap (Spacelab theme)
- Jinja2 Templates

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- pip

### 🔧 Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rei-tracking-project.git
   cd rei-tracking-project
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the environment variables:
   ```
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

5. Run the application:
   ```
   flask run
   ```

6. Open your web browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
rei-tracking-project/
.
├── .env
├── .env.example
├── .gitignore
├── analysis_json_schema.md
├── app.log
├── app.py
├── config.py
├── generate_secret.py
├── lib64
├── migration.log
├── migration_20250119_101652.log
├── output.txt
├── properties_json_schema.md
├── README.md
├── refactoring_considerations.md
├── requirements.txt
├── startup.sh
├── test_structure.txt
├── wsgi.py
├── __init__.py
│
├── dash_apps/
│   ├── dash_amortization.py
│   ├── dash_portfolio.py
│   ├── dash_transactions.py
│   ├── __init__.py
│   └── __pycache__/
│
├── data/
│   ├── categories.json
│   ├── properties.json
│   ├── transactions.json
│   ├── users.json
│   ├── analyses/
│   ├── logs/
│   │   └── transactions.log
│   └── uploads/
│       └── reimbursements/
│
├── docs/
│   ├── analysis_json_schema.md
│   └── properties_json_schema.md
│
├── flask_session/
│
├── logs/
│   ├── .gitkeep
│   ├── app.log
│   ├── app.log.1
│   └── app.log.10
│
├── models/
│   ├── models.py
│   ├── __init__.py
│   └── __pycache__/
│
├── routes/
│   ├── analyses.py
│   ├── api.py
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── dashboards.py
│   ├── main.py
│   ├── monitor.py
│   ├── properties.py
│   ├── transactions.py
│   └── __pycache__/
│
├── services/
│   ├── analysis_calculations.py
│   ├── analysis_service.py
│   ├── property_kpi_service.py
│   ├── report_generator.py
│   ├── transaction_import_service.py
│   ├── transaction_report_generator.py
│   ├── transaction_service.py
│   ├── user_service.py
│   └── __pycache__/
│
├── share/
│
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   │   ├── logo-blue.png
│   │   └── logo.png
│   └── js/
│       ├── base.js
│       ├── config.js
│       ├── main.js
│       ├── notifications.js
│       └── modules/
│           ├── add_properties.js
│           ├── add_transactions.js
│           ├── analysis.js
│           ├── auth.js
│           ├── bulk_import.js
│           ├── comps_handler.js
│           ├── dashboards.js
│           ├── edit_properties.js
│           ├── edit_transactions.js
│           ├── kpi_comparison.js
│           ├── kpi_dashboard.js
│           ├── landing.js
│           ├── loan_term_toggle.js
│           ├── main.js
│           ├── mao_calculator.js
│           ├── password_validation.js
│           ├── remove_properties.js
│           ├── view_edit_analysis.js
│           ├── view_transactions.js
│           ├── view_transactions_new.js
│           └── welcome.js
│
├── templates/
│   ├── 403.html
│   ├── 404.html
│   ├── 500.html
│   ├── base.html
│   ├── bulk_import.html
│   ├── forgot_password.html
│   ├── index.html
│   ├── landing.html
│   ├── login.html
│   ├── new_user_welcome.html
│   ├── signup.html
│   ├── analyses/
│   │   ├── create_analysis.html
│   │   ├── kpi_comparison.html
│   │   ├── mao_calculator.html
│   │   ├── view_edit_analysis.html
│   │   ├── _analysis_cards.html
│   │   └── _loan_section.html
│   ├── dashboards/
│   │   ├── dash_amortization.html
│   │   └── dash_transactions.html
│   ├── main/
│   │   ├── amortization.html
│   │   ├── dashboards.html
│   │   ├── main.html
│   │   ├── portfolio.html
│   │   ├── properties.html
│   │   └── transactions.html
│   ├── properties/
│   │   ├── add_properties.html
│   │   ├── edit_properties.html
│   │   ├── remove_properties.html
│   │   └── logs/
│   │       ├── app.log
│   │       └── app.log.1
│   └── transactions/
│       ├── add_transactions.html
│       ├── bulk_import.html
│       ├── edit_transactions.html
│       ├── remove_transactions.html
│       └── view_transactions.html
│
├── utils/
│   ├── calculators.py
│   ├── comps_handler.py
│   ├── flash.py
│   ├── json_handler.py
│   ├── money.py
│   ├── response_handler.py
│   ├── utils.py
│   └── __pycache__/
│
└── __pycache__/
```

## 🔒 Security Features

- Passwords are hashed using Werkzeug's generate_password_hash function
- Flask-Login is used for managing user sessions securely
- CSRF protection is enabled by default in Flask-WTF

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/yourusername/rei-tracking-project/issues).

## 📜 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## 👤 Author

Your Name
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

## 🙏 Acknowledgements

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Bootstrap Spacelab Theme](https://bootswatch.com/spacelab/)
- [Dash Documentation](https://dash.plotly.com/) (for future implementation)