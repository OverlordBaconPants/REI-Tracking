from flask_login import login_required, current_user
from services.user_service import get_user_by_email
from services.transaction_service import get_properties_for_user, get_transactions_for_view
from services.property_kpi_service import PropertyKPIService
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
from typing import Dict, List, Any
import json
import pandas as pd
from flask import Blueprint, render_template, redirect, url_for
from utils.flash import flash_success, flash_error, flash_warning, flash_info

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Landing page for first-time visitors"""
    logger.debug("Index route accessed")
    
    if current_user.is_authenticated:
        logger.info(f"Authenticated user accessing index: {current_user.email}")
        try:
            # Check if user has properties
            user_properties = get_properties_for_user(
                user_id=current_user.email,
                user_name=current_user.name
            )
            
            logger.debug(f"Found {len(user_properties)} properties for user {current_user.email}")
            
            if user_properties:
                logger.info(f"Redirecting user {current_user.email} to main dashboard")
                return redirect(url_for('main.main'))
            else:
                logger.info(f"New user {current_user.email} without properties, showing welcome page")
                return render_template('new_user_welcome.html')
                
        except Exception as e:
            logger.error(f"Error checking user properties: {str(e)}")
            flash_error("An error occurred while loading your properties")
            return render_template('new_user_welcome.html')
    
    logger.debug("Showing landing page to unauthenticated user")
    return render_template('landing.html')

def validate_loan_data(loan_amount: float, interest_rate: float, years: float) -> bool:
    """Validate loan calculation inputs"""
    try:
        if not all(isinstance(x, (int, float)) for x in [loan_amount, interest_rate, years]):
            return False
        if any(x <= 0 for x in [loan_amount, interest_rate, years]):
            return False
        if interest_rate > 100:  # Interest rate should be reasonable
            return False
        if years > 100:  # Loan term should be reasonable
            return False
        return True
    except Exception:
        return False

def amortize(principal: float, annual_rate: float, years: float):
    """Calculate loan amortization schedule"""
    logger.debug(f"Calculating amortization: principal={principal}, rate={annual_rate}, years={years}")
    
    if not validate_loan_data(principal, annual_rate, years):
        logger.error("Invalid loan data provided for amortization calculation")
        raise ValueError("Invalid loan calculation parameters")
    
    try:
        monthly_rate = annual_rate / 12
        num_payments = int(years * 12)
        
        # Calculate monthly payment
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
                'payment': round(payment, 2),
                'principal': round(principal_paid, 2),
                'interest': round(interest, 2),
                'balance': round(max(0, balance), 2),
                'cumulative_interest': round(cumulative_interest, 2),
                'cumulative_principal': round(cumulative_principal, 2)
            }
            
    except Exception as e:
        logger.error(f"Error in amortization calculation: {str(e)}")
        raise

def calculate_equity(property_address: str) -> Dict[str, float]:
    """Calculate equity metrics for a property"""
    logger.debug(f"Calculating equity for property: {property_address}")
    
    try:
        properties = get_properties_for_user(current_user.id, current_user.name)
        property_data = next((prop for prop in properties if prop['address'] == property_address), None)
        
        if not property_data:
            logger.warning(f"Property not found: {property_address}")
            return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

        # Validate required fields using new schema names
        required_fields = ['primary_loan_amount', 'primary_loan_rate', 'primary_loan_term', 'primary_loan_start_date']
        for field in required_fields:
            if field not in property_data or not property_data[field]:
                logger.error(f"Missing required field '{field}' for property {property_address}")
                return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

        loan_amount = float(property_data['primary_loan_amount'])
        interest_rate = float(property_data['primary_loan_rate']) / 100
        loan_term = float(property_data['primary_loan_term']) / 12  # Convert months to years
        
        try:
            loan_start_date = datetime.strptime(property_data['primary_loan_start_date'], '%Y-%m-%d').date()
        except ValueError:
            logger.error(f"Invalid loan start date format for property {property_address}")
            return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

        if not validate_loan_data(loan_amount, interest_rate * 100, loan_term):
            logger.error(f"Invalid loan parameters for property {property_address}")
            return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

        schedule = list(amortize(loan_amount, interest_rate, loan_term))

        today = date.today()
        months_into_loan = relativedelta(today, loan_start_date).months + relativedelta(today, loan_start_date).years * 12

        if months_into_loan <= 0:
            logger.debug(f"Loan hasn't started yet for property {property_address}")
            return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

        last_month_equity = schedule[months_into_loan - 1]['principal'] if months_into_loan > 0 else 0
        equity_gained_since_acquisition = sum(payment['principal'] for payment in schedule[:months_into_loan])
        
        logger.debug(f"Equity calculation completed for {property_address}: "
                    f"last_month={last_month_equity}, total={equity_gained_since_acquisition}")

        return {
            'last_month_equity': round(last_month_equity, 2),
            'equity_gained_since_acquisition': round(equity_gained_since_acquisition, 2)
        }
        
    except Exception as e:
        logger.error(f"Error calculating equity for property {property_address}: {str(e)}")
        return {'last_month_equity': 0, 'equity_gained_since_acquisition': 0}

def calculate_cumulative_amortization(properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate cumulative amortization for multiple properties"""
    logger.debug(f"Calculating cumulative amortization for {len(properties)} properties")
    
    if not properties:
        logger.warning("No properties provided for amortization calculation")
        return []
        
    all_schedules = []
    
    for prop in properties:
        try:
            # Validate required fields using new schema names
            required_fields = ['primary_loan_amount', 'primary_loan_rate', 'primary_loan_term', 
                             'primary_loan_start_date', 'address']
            if not all(field in prop and prop[field] for field in required_fields):
                logger.error(f"Missing required fields for property {prop.get('address', 'Unknown')}")
                continue

            loan_amount = float(prop['primary_loan_amount'])
            interest_rate = float(prop['primary_loan_rate']) / 100
            loan_term = float(prop['primary_loan_term']) / 12  # Convert months to years
            
            try:
                loan_start_date = datetime.strptime(prop['primary_loan_start_date'], '%Y-%m-%d').date()
            except ValueError:
                logger.error(f"Invalid loan start date for property {prop['address']}")
                continue

            if not validate_loan_data(loan_amount, interest_rate * 100, loan_term):
                logger.error(f"Invalid loan parameters for property {prop['address']}")
                continue

            schedule = list(amortize(loan_amount, interest_rate, loan_term))
            df = pd.DataFrame(schedule)
            df['date'] = [loan_start_date + relativedelta(months=i) for i in range(len(df))]
            df['property'] = prop['address']
            all_schedules.append(df)
            
        except Exception as e:
            logger.error(f"Error processing property {prop.get('address', 'Unknown')}: {str(e)}")
            continue

    if not all_schedules:
        logger.warning("No valid schedules generated")
        return []

    try:
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

        logger.debug("Cumulative amortization calculation completed successfully")
        return cumulative_df.to_dict('records')
        
    except Exception as e:
        logger.error(f"Error in cumulative calculations: {str(e)}")
        return []

@main_bp.route('/main')
@login_required
def main():
    """Main dashboard view"""
    logger.info(f"Main dashboard accessed by user: {current_user.email}")
    
    try:
        # Get user data
        user = get_user_by_email(current_user.email)
        if not user:
            logger.error(f"User not found: {current_user.email}")
            flash_error("Unable to load user data")
            return redirect(url_for('auth.login'))
        
        # Get user properties
        user_properties = get_properties_for_user(user['email'], user['name'])
        logger.debug(f"Found {len(user_properties)} properties for user")
        
        # Initialize empty KPI structure
        empty_kpi_structure = {
            'year_to_date': {
                'net_operating_income': {'monthly': 0, 'annual': 0},
                'total_income': {'monthly': 0, 'annual': 0},
                'total_expenses': {'monthly': 0, 'annual': 0},
                'operating_expense_ratio': 0,
                'cap_rate': 0,
                'cash_on_cash_return': 0,
                'debt_service_coverage_ratio': 0
            },
            'since_acquisition': {
                'net_operating_income': {'monthly': 0, 'annual': 0},
                'total_income': {'monthly': 0, 'annual': 0},
                'total_expenses': {'monthly': 0, 'annual': 0},
                'operating_expense_ratio': 0,
                'cap_rate': 0,
                'cash_on_cash_return': 0,
                'debt_service_coverage_ratio': 0
            },
            'analysis_comparison': None,
            'metadata': {
                'has_complete_history': False,
                'available_analyses': []
            }
        }
        
        if not user_properties:
            logger.warning(f"No properties found for user {user['email']}")
            flash_info("Please add some properties to get started")
            return render_template('main/main.html', 
                                name=user['name'],
                                user_properties=[],
                                total_last_month_equity=0,
                                total_equity_gained_since_acquisition=0,
                                pending_your_action=[],
                                pending_others_action=[],
                                cumulative_amortization=[],
                                property_kpis={'default': empty_kpi_structure})

        # Calculate equity
        for prop in user_properties:
            try:
                equity = calculate_equity(prop['address'])
                prop['last_month_equity'] = equity['last_month_equity']
                prop['equity_gained_since_acquisition'] = equity['equity_gained_since_acquisition']
            except Exception as e:
                logger.error(f"Error calculating equity for property {prop['address']}: {str(e)}")
                prop['last_month_equity'] = 0
                prop['equity_gained_since_acquisition'] = 0

        # Calculate totals
        total_last_month_equity = sum(prop['last_month_equity'] for prop in user_properties)
        total_equity_gained_since_acquisition = sum(prop['equity_gained_since_acquisition'] for prop in user_properties)

        # Get properties where user is property manager
        managed_properties = [
            prop['address'] for prop in user_properties
            if any(partner['name'] == user['name'] and partner.get('is_property_manager', False)
                  for partner in prop.get('partners', []))
        ]

        # Get all pending transactions
        all_pending = get_transactions_for_view(
            user['email'], 
            user['name'], 
            reimbursement_status='pending'
        )

        # Get all transactions for KPI calculations
        all_transactions = get_transactions_for_view(user['email'], user['name'])

        # Split into transactions pending user's action vs others' action
        pending_your_action = []
        pending_others_action = []

        for transaction in all_pending:
            # Get property data for this transaction
            property_data = next(
                (prop for prop in user_properties if prop['address'] == transaction['property_id']),
                None
            )
            
            if not property_data:
                continue

            # Find property manager for this transaction
            property_manager = next(
                (partner['name'] for partner in property_data.get('partners', [])
                 if partner.get('is_property_manager', False)),
                'Unknown'
            )

            # Add property manager to transaction data
            transaction['property_manager'] = property_manager

            # Sort into appropriate list
            if transaction['property_id'] in managed_properties:
                pending_your_action.append(transaction)
            else:
                pending_others_action.append(transaction)

        try:
            # Initialize KPI service and calculate KPIs
            kpi_service = PropertyKPIService(user_properties)
            property_kpis = {}
            
            # Get transactions for KPI calculations 
            all_transactions = get_transactions_for_view(user['email'], user['name'])
            
            # Calculate KPIs for each property
            for property_data in user_properties:
                property_id = property_data['address']
                try:
                    # This will now include available analyses in the metadata
                    property_kpis[property_id] = kpi_service.get_kpi_dashboard_data(
                        property_id=property_id,
                        transactions=all_transactions
                    )
                    # Log found analyses for debugging
                    analyses = property_kpis[property_id].get('metadata', {}).get('available_analyses', [])
                    logger.debug(f"Found {len(analyses)} matching analyses for {property_id}")
                    
                except Exception as e:
                    logger.error(f"Error calculating KPIs for property {property_id}: {str(e)}")
                    property_kpis[property_id] = empty_kpi_structure.copy()
                    
        except Exception as e:
            logger.error(f"Error initializing KPI service: {str(e)}")
            # Initialize empty KPIs for all properties
            for property_data in user_properties:
                empty_kpi = empty_kpi_structure.copy()
                empty_kpi['property_details'] = property_data
                property_kpis[property_data['address']] = empty_kpi

        logger.debug("All dashboard data compiled successfully")
        logger.debug(f"Property KPIs structure: {json.dumps(property_kpis, indent=2)}")

        return render_template('main/main.html', 
                            name=user['name'],
                            user_properties=user_properties,
                            total_last_month_equity=total_last_month_equity,
                            total_equity_gained_since_acquisition=total_equity_gained_since_acquisition,
                            pending_your_action=pending_your_action,
                            pending_others_action=pending_others_action,
                            cumulative_amortization=calculate_cumulative_amortization(user_properties),
                            property_kpis=property_kpis)
                            
    except Exception as e:
        logger.error(f"Error loading main dashboard: {str(e)}")
        flash_error("An error occurred while loading the dashboard")
        return render_template('main/main.html',
                            name=current_user.name,
                            user_properties=[],
                            total_last_month_equity=0,
                            total_equity_gained_since_acquisition=0,
                            pending_your_action=[],
                            pending_others_action=[],
                            cumulative_amortization=[],
                            property_kpis={'default': empty_kpi_structure})

@main_bp.route('/properties')
@login_required
def properties():
    """Properties view"""
    logger.debug(f"Properties route accessed by user: {current_user.email}")
    return render_template('main/properties.html')

@main_bp.route('/test-flash')
def test_flash():
    """Test flash messages"""
    logger.debug("Testing flash messages")
    flash_success("This is a success message")
    flash_error("This is an error message")
    flash_warning("This is a warning message")
    flash_info("This is an info message")
    return redirect(url_for('index'))