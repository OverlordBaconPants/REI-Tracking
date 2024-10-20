# 🏠 REI Tracking Project

## 📝 Description

This project is a Flask- and Dash-based Python web application that allows partners to track and adjudicate incomes and expenses (per equity splits) and create and access useful reports tracking Key Performance Indicators such as CoC Return, net monthly cash flow, and amortization schedules.

## ✨ Features

- 🔑 User Authentication (Login/Logout)
- 📝 User Registration
- 🔄 Password Reset
- 🍞 Breadcrumb Navigation
- 🚀 Bootstrap-based Responsive Design
- 💰 Income and Expense Tracking
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
│
├── app.py
├── config.py
├── requirements.txt
│
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   └── main.py
│
├── models/
│   └── user.py
│
├── services/
│   └── user_service.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── forgot_password.html
│   └── main.html
│
└── static/
    └── favicon.ico
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