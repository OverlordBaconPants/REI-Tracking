from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from services.user_service import get_user_by_email
from services.transaction_service import get_properties_for_user, get_transactions_for_view
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
import requests
import pandas as pd

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

def amortize(principal, annual_rate, years):
    monthly_rate = annual_rate / 12
    num_payments = int(years * 12)
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    
    balance = principal
    cumulative_interest = 0
    cumulative_principal = 0
    
    for month in range(1, num_payments + 1):
        interest = balance * monthly_rate
        principal_paid = payment - interest
        balance -= principal_paid
        
        cumulative_interest += interest
        cumulative_principal += principal_paid
        
        yield {
            'month': month,
            'payment': payment,
            'principal': principal_paid,
            'interest': interest,
            'balance': max(0, balance),
            'cumulative_interest': cumulative_interest,
            'cumulative_principal': cumulative_principal
        }

def calculate_equity(property_address):
    properties = get_properties_for_user(current_user.id, current_user.name)
    property_data = next((prop for prop in properties if prop['address'] == property_address), None)
    
    if not property_data:
        return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

    loan_amount = float(property_data['loan_amount'])
    interest_rate = float(property_data['primary_loan_rate']) / 100
    loan_term = float(property_data['primary_loan_term']) / 12  # Convert months to years
    loan_start_date = datetime.strptime(property_data['loan_start_date'], '%Y-%m-%d').date()

    schedule = list(amortize(loan_amount, interest_rate, loan_term))

    today = date.today()
    months_into_loan = relativedelta(today, loan_start_date).months + relativedelta(today, loan_start_date).years * 12

    if months_into_loan <= 0:
        return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

    last_month_equity = schedule[months_into_loan - 1]['principal'] if months_into_loan > 0 else 0
    equity_gained_since_acquisition = sum(payment['principal'] for payment in schedule[:months_into_loan])

    return {
        'last_month_equity': last_month_equity,
        'equity_gained_since_acquisition': equity_gained_since_acquisition
    }

def calculate_cumulative_amortization(properties):
    all_schedules = []
    for prop in properties:
        loan_amount = float(prop['loan_amount'])
        interest_rate = float(prop['primary_loan_rate']) / 100
        loan_term = float(prop['primary_loan_term']) / 12  # Convert months to years
        loan_start_date = datetime.strptime(prop['loan_start_date'], '%Y-%m-%d').date()

        schedule = list(amortize(loan_amount, interest_rate, loan_term))
        df = pd.DataFrame(schedule)
        df['date'] = [loan_start_date + relativedelta(months=i) for i in range(len(df))]
        df['property'] = prop['address']
        all_schedules.append(df)

    combined_df = pd.concat(all_schedules)
    combined_df = combined_df.sort_values('date')

    cumulative_df = combined_df.groupby('date').agg({
        'balance': 'sum',
        'cumulative_interest': 'sum',
        'cumulative_principal': 'sum'
    }).reset_index()

    cumulative_df = cumulative_df.rename(columns={
        'balance': 'Portfolio Loan Balance',
        'cumulative_interest': 'Portfolio Interest',
        'cumulative_principal': 'Portfolio Principal'
    })

    return cumulative_df.to_dict('records')

@main_bp.route('/main')
@login_required
def main():
    logging.info(f"Main dashboard accessed by user: {current_user.email}")
    user = get_user_by_email(current_user.email)
    
    # Get user properties
    user_properties = get_properties_for_user(user['email'], user['name'])
    
    # Calculate equity
    for prop in user_properties:
        equity = calculate_equity(prop['address'])
        prop['last_month_equity'] = equity['last_month_equity']
        prop['equity_gained_since_acquisition'] = equity['equity_gained_since_acquisition']

    # Calculate totals
    total_last_month_equity = sum(prop['last_month_equity'] for prop in user_properties)
    total_equity_gained_since_acquisition = sum(prop['equity_gained_since_acquisition'] for prop in user_properties)

    # Get pending transactions
    pending_transactions = get_transactions_for_view(
        user['email'], 
        user['name'], 
        reimbursement_status='pending'
    )

    # Calculate cumulative amortization
    cumulative_amortization = calculate_cumulative_amortization(user_properties)

    return render_template('main/main.html', 
                           name=user['name'],
                           user_properties=user_properties,
                           total_last_month_equity=total_last_month_equity,
                           total_equity_gained_since_acquisition=total_equity_gained_since_acquisition,
                           pending_transactions=pending_transactions,
                           cumulative_amortization=cumulative_amortization)

@main_bp.route('/properties')
@login_required
def properties():
    return render_template('main/properties.html')
