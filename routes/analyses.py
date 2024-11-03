from utils.flash import flash_message
import logging
from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for, send_file
from flask_login import login_required, current_user
from services.report_generator import generate_lender_report, LenderMetricsCalculator
import uuid
from datetime import datetime, timezone
import locale
from io import BytesIO
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import BaseDocTemplate
import os
import json
import logging
import traceback
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle, 
    BaseDocTemplate, Frame, PageTemplate, FrameBreak
)
from config import Config

analyses_bp = Blueprint('analyses', __name__)

# Set the locale to handle comma formatting
locale.setlocale(locale.LC_ALL, '')

def safe_float(value, default=0.0):
    """
    Safely convert a value to float, handling currency formatting.
    
    Args:
        value: The value to convert (string, int, or float)
        default: Default value to return if conversion fails (default: 0.0)
        
    Returns:
        float: The converted number or default value
    """
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Remove currency symbols, commas, and spaces
            cleaned = value.replace('$', '').replace(',', '').replace(' ', '').strip()
            return float(cleaned) if cleaned else default
        return default
    except (ValueError, TypeError):
        return default

def format_currency(value):
    return locale.format_string("%.2f", value, grouping=True)

def sanitize_analysis_data(data):
    """
    Recursively sanitize all numeric values in the analysis data.
    
    Args:
        data: The data structure to sanitize (dict, list, or value)
        
    Returns:
        The sanitized data structure
    """
    if isinstance(data, dict):
        return {k: sanitize_analysis_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_analysis_data(x) for x in data]
    elif isinstance(data, str):
        # Check if it looks like a number
        if any(c.isdigit() for c in data):
            try:
                return safe_float(data)
            except (ValueError, TypeError):
                return data
        return data
    return data

@analyses_bp.route('/create_analysis', methods=['GET', 'POST'])
@login_required
def create_analysis():
    # Handle viewing/editing existing analysis
    analysis_id = request.args.get('analysis_id')
    existing_analysis = None
    
    if analysis_id and request.method == 'GET':
        try:
            # Attempt to get the existing analysis
            response = get_analysis(analysis_id)
            
            # Check if response is a tuple (error response)
            if isinstance(response, tuple):
                return redirect(url_for('analyses.view_edit_analysis'))
            
            # Extract analysis data from response
            analysis_data = response.get_json()
            if not analysis_data or not analysis_data.get('success'):
                return redirect(url_for('analyses.view_edit_analysis'))
                
            existing_analysis = analysis_data['analysis']
            
            # Verify the analysis belongs to the current user
            filename = f"{analysis_id}_{current_user.id}.json"
            analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
            if not os.path.exists(os.path.join(analyses_dir, filename)):
                return redirect(url_for('analyses.view_edit_analysis'))
            
            # Set edit mode flag
            existing_analysis['edit_mode'] = True
            
        except Exception as e:
            logging.error(f"Error fetching analysis: {str(e)}")
            logging.error(traceback.format_exc())
            return redirect(url_for('analyses.view_edit_analysis'))

    if request.method == 'POST':
        try:
            analysis_data = request.json
            analysis_type = analysis_data.get('analysis_type')
            
            # Add user ID and creation timestamp
            analysis_data['user_id'] = current_user.id
            if not analysis_id:  # Only set created_at for new analyses
                analysis_data['created_at'] = datetime.now(tz=timezone.utc).isoformat()

            # Validate required fields based on analysis type
            if analysis_type == 'BRRRR':
                required_fields = [
                    'analysis_name', 'purchase_price', 'renovation_costs', 'renovation_duration',
                    'after_repair_value', 'initial_loan_amount', 'initial_down_payment',
                    'initial_interest_rate', 'initial_loan_term', 'initial_closing_costs',
                    'refinance_loan_amount', 'refinance_down_payment', 'refinance_interest_rate',
                    'refinance_loan_term', 'refinance_closing_costs', 'monthly_rent',
                    'property_taxes', 'insurance', 'maintenance_percentage', 'vacancy_percentage',
                    'capex_percentage', 'management_percentage'
                ]
            else:  # Long-Term Rental
                required_fields = [
                    'analysis_name', 'purchase_price', 'after_repair_value', 'cash_to_seller',
                    'closing_costs', 'assignment_fee', 'marketing_costs', 'renovation_costs',
                    'renovation_duration', 'monthly_rent', 'management_percentage',
                    'capex_percentage', 'repairs_percentage', 'vacancy_percentage',
                    'property_taxes', 'insurance', 'hoa_coa_coop'
                ]

            # Validate required fields
            missing_fields = [field for field in required_fields if field not in analysis_data]
            if missing_fields:
                return jsonify({
                    "success": False, 
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400

            # Calculate analysis results
            analysis_data = calculate_analysis_results(analysis_data)

            # Handle update vs create
            if analysis_id:
                # Verify user owns the analysis before updating
                filename = f"{analysis_id}_{current_user.id}.json"
                analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
                if not os.path.exists(os.path.join(analyses_dir, filename)):
                    return jsonify({
                        "success": False, 
                        "message": "Access denied"
                    }), 403
                
                # Update existing analysis
                analysis_data['id'] = analysis_id
                message = "Analysis updated successfully!"
            else:
                # Create new analysis
                new_analysis_id = str(uuid.uuid4())
                analysis_data['id'] = new_analysis_id
                analysis_id = new_analysis_id
                message = "Analysis created successfully!"

            # Save the analysis data
            filename = f"{analysis_id}_{current_user.id}.json"
            filepath = os.path.join(Config.DATA_DIR, 'analyses', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            return jsonify({
                "success": True, 
                "message": message, 
                "analysis": analysis_data
            })

        except Exception as e:
            logging.error(f"Error processing analysis: {str(e)}")
            logging.error(traceback.format_exc())
            return jsonify({
                "success": False, 
                "message": f"An error occurred: {str(e)}"
            }), 500
    
    # GET request - render the create/edit form
    template_data = {'analysis': existing_analysis} if existing_analysis else {}
    return render_template('analyses/create_analysis.html', **template_data)

def calculate_analysis_results(data):
    try:
        analysis_type = data.get('analysis_type')
        logging.info(f"Calculating results for analysis type: {analysis_type}")
        
        if analysis_type == 'BRRRR':
            result = calculate_brrrr_analysis(data)
        elif analysis_type == 'PadSplit BRRRR':
            result = calculate_padsplit_brrrr_analysis(data)
        elif analysis_type == 'PadSplit LTR':
            result = calculate_padsplit_ltr_analysis(data)
        else:  # Long-Term Rental
            result = calculate_long_term_rental_analysis(data)
        
        return result
    except Exception as e:
        logging.error(f"Error in calculate_analysis_results: {str(e)}")
        raise

def calculate_long_term_rental_analysis(data):
    try:
        # Gross Monthly Income
        gross_monthly_income = safe_float(data['monthly_rent'])

        # Calculate Operating Expenses
        management = gross_monthly_income * safe_float(data['management_percentage']) / 100
        capex = gross_monthly_income * safe_float(data['capex_percentage']) / 100
        repairs = gross_monthly_income * safe_float(data['repairs_percentage']) / 100
        vacancy = gross_monthly_income * safe_float(data['vacancy_percentage']) / 100
        property_taxes = safe_float(data['property_taxes'])
        insurance = safe_float(data['insurance'])
        hoa_coa_coop = safe_float(data['hoa_coa_coop'])

        # Total Monthly Operating Expenses
        total_monthly_operating_expenses = (management + capex + repairs + vacancy + 
                                         property_taxes + insurance + hoa_coa_coop)

        # Calculate loan payments
        total_monthly_loan_payment = 0
        total_down_payment = 0
        total_closing_costs = 0
        
        if 'loans' in data:
            for loan in data['loans']:
                loan_amount = safe_float(loan['amount'])
                interest_rate = safe_float(loan['interest_rate'])
                term = int(safe_float(loan['term']))
                
                if loan_amount > 0 and term > 0:
                    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, term)
                    total_monthly_loan_payment += monthly_payment
                
                total_down_payment += safe_float(loan['down_payment'])
                total_closing_costs += safe_float(loan['closing_costs'])

        # Calculate Net Monthly Cash Flow
        net_monthly_cash_flow = (gross_monthly_income - 
                               total_monthly_operating_expenses - 
                               total_monthly_loan_payment)

        # Calculate Annual Cash Flow
        annual_cash_flow = net_monthly_cash_flow * 12

        # Calculate total investment and returns
        renovation_costs = safe_float(data['renovation_costs'])
        total_cash_invested = total_down_payment + renovation_costs + total_closing_costs

        # Calculate cash on cash return
        cash_on_cash_return = ((annual_cash_flow / total_cash_invested) * 100 
                             if total_cash_invested > 0 else 0)

        # Store calculated values
        result = {
            'gross_monthly_income': format_currency(gross_monthly_income),
            'net_monthly_cash_flow': format_currency(net_monthly_cash_flow),
            'annual_cash_flow': format_currency(annual_cash_flow),
            'cash_on_cash_return': f"{cash_on_cash_return:.2f}%",
            'total_cash_invested': format_currency(total_cash_invested),
            'operating_expenses': {
                "Management": format_currency(management),
                "CapEx": format_currency(capex),
                "Repairs": format_currency(repairs),
                "Vacancy": format_currency(vacancy),
                "Property Taxes": format_currency(property_taxes),
                "Insurance": format_currency(insurance),
                "HOA/COA/COOP": format_currency(hoa_coa_coop)
            }
        }

        # Include the original data
        result.update(data)
        
        return result

    except Exception as e:
        logging.error(f"Error in calculate_long_term_rental_analysis: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def calculate_brrrr_analysis(data):
    try:
        # Purchase and Renovation
        purchase_price = safe_float(data.get('purchase_price'))
        renovation_costs = safe_float(data.get('renovation_costs'))
        renovation_duration = int(safe_float(data.get('renovation_duration')))
        after_repair_value = safe_float(data.get('after_repair_value'))
        
        # Initial costs
        initial_loan_amount = safe_float(data.get('initial_loan_amount'))
        initial_down_payment = safe_float(data.get('initial_down_payment'))
        initial_closing_costs = safe_float(data.get('initial_closing_costs'))
        
        # Total initial investment before refinance
        total_initial_investment = (initial_down_payment + 
                                  renovation_costs + 
                                  initial_closing_costs)

        # Refinance details
        refinance_loan_amount = safe_float(data.get('refinance_loan_amount'))
        refinance_down_payment = safe_float(data.get('refinance_down_payment'))
        refinance_closing_costs = safe_float(data.get('refinance_closing_costs'))
        
        # Calculate actual cash left in deal after refinance
        total_costs = (purchase_price + renovation_costs + 
                      initial_closing_costs + refinance_closing_costs)
        cash_recouped = refinance_loan_amount - initial_loan_amount
        actual_cash_invested = total_initial_investment - cash_recouped + refinance_closing_costs

        # Income calculations
        monthly_rent = safe_float(data.get('monthly_rent'))

        # Operating expense calculations
        property_taxes = safe_float(data.get('property_taxes'))
        insurance = safe_float(data.get('insurance'))
        
        # Calculate percentage-based expenses
        maintenance_percentage = safe_float(data.get('maintenance_percentage'))
        vacancy_percentage = safe_float(data.get('vacancy_percentage'))
        capex_percentage = safe_float(data.get('capex_percentage'))
        management_percentage = safe_float(data.get('management_percentage'))

        maintenance = monthly_rent * maintenance_percentage / 100
        vacancy = monthly_rent * vacancy_percentage / 100
        capex = monthly_rent * capex_percentage / 100
        management = monthly_rent * management_percentage / 100

        # Organize operating expenses
        operating_expenses = {
            'Property Taxes': property_taxes,
            'Insurance': insurance,
            'Maintenance': maintenance,
            'Vacancy': vacancy,
            'CapEx': capex,
            'Property Management': management
        }

        # Calculate monthly payments
        initial_monthly_payment = calculate_monthly_payment(
            initial_loan_amount, 
            safe_float(data.get('initial_interest_rate')), 
            int(safe_float(data.get('initial_loan_term')))
        )
        
        refinance_monthly_payment = calculate_monthly_payment(
            refinance_loan_amount, 
            safe_float(data.get('refinance_interest_rate')), 
            int(safe_float(data.get('refinance_loan_term')))
        )

        # Calculate total expenses and cash flow
        total_monthly_expenses = (sum(operating_expenses.values()) + 
                                refinance_monthly_payment)
        monthly_cash_flow = monthly_rent - total_monthly_expenses
        annual_cash_flow = monthly_cash_flow * 12

        # Calculate returns
        cash_on_cash_return = ((annual_cash_flow / actual_cash_invested) * 100 
                             if actual_cash_invested > 0 else 0)
        equity_captured = after_repair_value - total_costs
        total_profit = equity_captured + annual_cash_flow
        roi = ((total_profit / actual_cash_invested) * 100 
               if actual_cash_invested > 0 else 0)

        # Format the results
        results = {
            # Basic Information
            'analysis_name': data.get('analysis_name', ''),
            'analysis_type': 'BRRRR',
            'property_address': data.get('property_address', ''),
            'property_type': data.get('property_type', ''),
            'home_square_footage': data.get('home_square_footage', ''),
            'lot_square_footage': data.get('lot_square_footage', ''),
            'year_built': data.get('year_built', ''),
            
            # Purchase and Renovation
            'purchase_price': format_currency(purchase_price),
            'renovation_costs': format_currency(renovation_costs),
            'renovation_duration': renovation_duration,
            'after_repair_value': format_currency(after_repair_value),
            'total_initial_investment': format_currency(total_initial_investment),
            
            # Initial Financing
            'initial_loan_amount': format_currency(initial_loan_amount),
            'initial_down_payment': format_currency(initial_down_payment),
            'initial_interest_rate': f"{safe_float(data.get('initial_interest_rate')):.2f}",
            'initial_loan_term': int(safe_float(data.get('initial_loan_term'))),
            'initial_monthly_payment': format_currency(initial_monthly_payment),
            'initial_closing_costs': format_currency(initial_closing_costs),
            
            # Refinance
            'refinance_loan_amount': format_currency(refinance_loan_amount),
            'refinance_down_payment': format_currency(refinance_down_payment),
            'refinance_interest_rate': f"{safe_float(data.get('refinance_interest_rate')):.2f}",
            'refinance_loan_term': int(safe_float(data.get('refinance_loan_term'))),
            'refinance_monthly_payment': format_currency(refinance_monthly_payment),
            'refinance_closing_costs': format_currency(refinance_closing_costs),
            
            # Operating Income and Expenses
            'monthly_rent': format_currency(monthly_rent),
            'operating_expenses': {k: format_currency(v) for k, v in operating_expenses.items()},
            'total_monthly_expenses': format_currency(total_monthly_expenses),
            'monthly_cash_flow': format_currency(monthly_cash_flow),
            'annual_cash_flow': format_currency(annual_cash_flow),
            
            # Percentage Values
            'maintenance_percentage': f"{maintenance_percentage:.1f}",
            'vacancy_percentage': f"{vacancy_percentage:.1f}",
            'capex_percentage': f"{capex_percentage:.1f}",
            'management_percentage': f"{management_percentage:.1f}",
            
            # Returns and Metrics
            'actual_cash_invested': format_currency(actual_cash_invested),
            'cash_recouped': format_currency(cash_recouped),
            'equity_captured': format_currency(equity_captured),
            'cash_on_cash_return': f"{cash_on_cash_return:.2f}%",
            'roi': f"{roi:.2f}%",
            'total_costs': format_currency(total_costs)
        }

        return results

    except Exception as e:
        logging.error(f"Error in calculate_brrrr_analysis: {str(e)}")
        logging.error(traceback.format_exc())
        raise
        
def calculate_padsplit_expenses(data, monthly_rent):
    """Calculate PadSplit-specific expenses with safe handling"""
    try:
        # Helper function to safely convert to float
        def safe_float(value, default=0):
            try:
                if isinstance(value, str):
                    value = value.replace('$', '').replace(',', '').strip()
                return float(value) if value else default
            except (ValueError, TypeError):
                return default

        # Get platform percentage with safe default
        platform_percentage = safe_float(data.get('padsplit_platform_percentage'), 12)
        
        # Calculate platform fee only if we have income
        platform_fee = (monthly_rent * platform_percentage / 100) if monthly_rent > 0 else 0
        
        # Safely get all expense values
        utilities = safe_float(data.get('utilities'))
        internet = safe_float(data.get('internet'))
        cleaning_costs = safe_float(data.get('cleaning_costs'))
        pest_control = safe_float(data.get('pest_control'))
        landscaping = safe_float(data.get('landscaping'))
        
        # Calculate total PadSplit expenses
        total_padsplit_expenses = (platform_fee + utilities + internet + 
                                 cleaning_costs + pest_control + landscaping)
        
        return {
            'platform_fee': platform_fee,
            'utilities': utilities,
            'internet': internet,
            'cleaning_costs': cleaning_costs,
            'pest_control': pest_control,
            'landscaping': landscaping,
            'total_padsplit_expenses': total_padsplit_expenses
        }
        
    except Exception as e:
        logging.error(f"Error calculating PadSplit expenses: {str(e)}")
        logging.error(f"Input data: {data}")
        logging.error(traceback.format_exc())
        # Return zero values if calculation fails
        return {
            'platform_fee': 0,
            'utilities': 0,
            'internet': 0,
            'cleaning_costs': 0,
            'pest_control': 0,
            'landscaping': 0,
            'total_padsplit_expenses': 0
        }

def calculate_padsplit_ltr_analysis(data):
    try:
        def safe_float(value, default=0):
            try:
                if isinstance(value, str):
                    value = value.replace('$', '').replace(',', '').strip()
                return float(value) if value else default
            except (ValueError, TypeError):
                return default

        # Initial Investment
        purchase_price = safe_float(data.get('purchase_price'))
        after_repair_value = safe_float(data.get('after_repair_value'))  # Note: we collect as after_rehab_value
        cash_to_seller = safe_float(data.get('cash_to_seller'))
        closing_costs = safe_float(data.get('closing_costs'))
        assignment_fee = safe_float(data.get('assignment_fee'))
        marketing_costs = safe_float(data.get('marketing_costs'))
        renovation_costs = safe_float(data.get('renovation_costs'))
        renovation_duration = safe_float(data.get('renovation_duration'))

        # Monthly Income
        monthly_rent = safe_float(data.get('monthly_rent'))

        # Base Operating Expenses
        management_percentage = safe_float(data.get('management_percentage'))
        capex_percentage = safe_float(data.get('capex_percentage'))
        repairs_percentage = safe_float(data.get('repairs_percentage'))
        vacancy_percentage = safe_float(data.get('vacancy_percentage'))
        property_taxes = safe_float(data.get('property_taxes'))
        insurance = safe_float(data.get('insurance'))
        hoa_coa_coop = safe_float(data.get('hoa_coa_coop'))

        # Calculate base operating expenses
        management = monthly_rent * management_percentage / 100
        capex = monthly_rent * capex_percentage / 100
        repairs = monthly_rent * repairs_percentage / 100
        vacancy = monthly_rent * vacancy_percentage / 100

        base_operating_expenses = {
            "Management": management,
            "CapEx": capex,
            "Repairs": repairs,
            "Vacancy": vacancy,
            "Property Taxes": property_taxes,
            "Insurance": insurance,
            "HOA/COA/COOP": hoa_coa_coop
        }

        # PadSplit-specific expenses
        padsplit_platform_percentage = safe_float(data.get('padsplit_platform_percentage'))
        platform_fee = monthly_rent * padsplit_platform_percentage / 100
        utilities = safe_float(data.get('utilities'))
        internet = safe_float(data.get('internet'))
        cleaning_costs = safe_float(data.get('cleaning_costs'))
        pest_control = safe_float(data.get('pest_control'))
        landscaping = safe_float(data.get('landscaping'))

        padsplit_expenses = {
            "Platform Fee": platform_fee,
            "Utilities": utilities,
            "Internet": internet,
            "Cleaning Costs": cleaning_costs,
            "Pest Control": pest_control,
            "Landscaping": landscaping
        }

        # Process loans
        total_monthly_loan_payment = 0
        total_down_payment = 0
        total_closing_costs = 0
        loans = []

        for loan_data in data.get('loans', []):
            loan_amount = safe_float(loan_data.get('amount'))
            interest_rate = safe_float(loan_data.get('interest_rate'))
            term = int(safe_float(loan_data.get('term')))
            down_payment = safe_float(loan_data.get('down_payment'))
            loan_closing_costs = safe_float(loan_data.get('closing_costs'))

            if loan_amount > 0 and term > 0:
                monthly_payment = calculate_monthly_payment(loan_amount, interest_rate, term)
                total_monthly_loan_payment += monthly_payment

            total_down_payment += down_payment
            total_closing_costs += loan_closing_costs

            loans.append({
                'name': loan_data.get('name', ''),
                'amount': loan_amount,
                'down_payment': down_payment,
                'interest_rate': interest_rate,
                'term': term,
                'closing_costs': loan_closing_costs,
                'monthly_payment': monthly_payment if loan_amount > 0 and term > 0 else 0
            })

        # Calculate totals
        total_operating_expenses = sum(base_operating_expenses.values())
        total_padsplit_expenses = sum(padsplit_expenses.values())
        total_expenses = total_operating_expenses + total_padsplit_expenses + total_monthly_loan_payment

        # Calculate cash flows
        monthly_cash_flow = monthly_rent - total_expenses
        annual_cash_flow = monthly_cash_flow * 12

        # Calculate investment metrics
        total_cash_invested = total_down_payment + renovation_costs + total_closing_costs

        # Prepare results with standardized field names
        results = {
            # Basic Information
            'analysis_name': data.get('analysis_name', ''),
            'analysis_type': 'PadSplit LTR',
            'property_address': data.get('property_address', ''),
            'property_type': data.get('property_type', ''),
            'home_square_footage': data.get('home_square_footage', ''),
            'lot_square_footage': data.get('lot_square_footage', ''),
            'year_built': data.get('year_built', ''),

            # Purchase and Investment
            'purchase_price': format_currency(purchase_price),
            'after_repair_value': format_currency(after_repair_value),  # Standardized name
            'cash_to_seller': format_currency(cash_to_seller),
            'closing_costs': format_currency(closing_costs),
            'assignment_fee': format_currency(assignment_fee),
            'marketing_costs': format_currency(marketing_costs),
            'renovation_costs': format_currency(renovation_costs),
            'renovation_duration': renovation_duration,
            'total_cash_invested': format_currency(total_cash_invested),

            # Income
            'monthly_rent': format_currency(monthly_rent),
            'monthly_cash_flow': format_currency(monthly_cash_flow),
            'annual_cash_flow': format_currency(annual_cash_flow),

            # Operating Expenses
            'management_percentage': f"{management_percentage:.1f}",
            'capex_percentage': f"{capex_percentage:.1f}",
            'repairs_percentage': f"{repairs_percentage:.1f}",
            'vacancy_percentage': f"{vacancy_percentage:.1f}",
            'property_taxes': format_currency(property_taxes),
            'insurance': format_currency(insurance),
            'hoa_coa_coop': format_currency(hoa_coa_coop),
            'total_operating_expenses': format_currency(total_operating_expenses),

            # PadSplit Expenses
            'padsplit_platform_percentage': f"{padsplit_platform_percentage:.1f}",
            'utilities': format_currency(utilities),
            'internet': format_currency(internet),
            'cleaning_costs': format_currency(cleaning_costs),
            'pest_control': format_currency(pest_control),
            'landscaping': format_currency(landscaping),
            'total_padsplit_expenses': format_currency(total_padsplit_expenses),

            # Total Expenses
            'total_expenses': format_currency(total_expenses),

            # Returns
            'cash_on_cash_return': f"{(annual_cash_flow / total_cash_invested * 100):.2f}%" if total_cash_invested > 0 else "0.00%",

            # Loan Information
            'loans': loans,
            'total_monthly_loan_payment': format_currency(total_monthly_loan_payment)
        }

        return results

    except Exception as e:
        logging.error(f"Error in calculate_padsplit_ltr_analysis: {str(e)}")
        logging.error(f"Input data: {json.dumps(data, indent=2)}")
        logging.error(traceback.format_exc())
        raise

def calculate_padsplit_brrrr_analysis(data):
    try:
        # Helper function to safely convert numbers
        def safe_float(value, default=0):
            try:
                if isinstance(value, str):
                    value = value.replace('$', '').replace(',', '').strip()
                return float(value) if value else default
            except (ValueError, TypeError):
                return default

        # Purchase and Renovation
        purchase_price = safe_float(data.get('purchase_price'))
        renovation_costs = safe_float(data.get('renovation_costs'))
        renovation_duration = int(safe_float(data.get('renovation_duration')))
        after_repair_value = safe_float(data.get('after_repair_value'))
        total_investment = purchase_price + renovation_costs

        # Initial Financing
        initial_loan_amount = safe_float(data.get('initial_loan_amount'))
        initial_down_payment = safe_float(data.get('initial_down_payment'))
        initial_interest_rate = safe_float(data.get('initial_interest_rate'))
        initial_loan_term = int(safe_float(data.get('initial_loan_term')))
        initial_closing_costs = safe_float(data.get('initial_closing_costs'))
        initial_monthly_payment = calculate_monthly_payment(
            initial_loan_amount, initial_interest_rate, initial_loan_term
        ) if initial_loan_amount > 0 and initial_loan_term > 0 else 0

        # Refinance
        refinance_loan_amount = safe_float(data.get('refinance_loan_amount'))
        refinance_down_payment = safe_float(data.get('refinance_down_payment'))
        refinance_interest_rate = safe_float(data.get('refinance_interest_rate'))
        refinance_loan_term = int(safe_float(data.get('refinance_loan_term')))
        refinance_closing_costs = safe_float(data.get('refinance_closing_costs'))
        refinance_monthly_payment = calculate_monthly_payment(
            refinance_loan_amount, refinance_interest_rate, refinance_loan_term
        ) if refinance_loan_amount > 0 and refinance_loan_term > 0 else 0

        # Rental Income and Base Expenses
        monthly_rent = safe_float(data.get('monthly_rent'))
        property_taxes = safe_float(data.get('property_taxes'))
        insurance = safe_float(data.get('insurance'))
        maintenance_percentage = safe_float(data.get('maintenance_percentage'), 2)
        vacancy_percentage = safe_float(data.get('vacancy_percentage'), 4)
        capex_percentage = safe_float(data.get('capex_percentage'), 2)
        management_percentage = safe_float(data.get('management_percentage'), 8)

        # Calculate base operating expenses
        maintenance = monthly_rent * maintenance_percentage / 100
        vacancy = monthly_rent * vacancy_percentage / 100
        capex = monthly_rent * capex_percentage / 100
        management = monthly_rent * management_percentage / 100

        # PadSplit-specific expenses
        platform_percentage = safe_float(data.get('padsplit_platform_percentage'), 12)
        platform_fee = monthly_rent * platform_percentage / 100
        utilities = safe_float(data.get('utilities'))
        internet = safe_float(data.get('internet'))
        cleaning_costs = safe_float(data.get('cleaning_costs'))
        pest_control = safe_float(data.get('pest_control'))
        landscaping = safe_float(data.get('landscaping'))

        # Organize expenses
        base_operating_expenses = {
            "Management": management,
            "CapEx": capex,
            "Maintenance": maintenance,
            "Vacancy": vacancy,
            "Property Taxes": property_taxes,
            "Insurance": insurance
        }

        padsplit_expenses = {
            "Platform Fee": platform_fee,
            "Utilities": utilities,
            "Internet": internet,
            "Cleaning Costs": cleaning_costs,
            "Pest Control": pest_control,
            "Landscaping": landscaping
        }

        # Calculate totals
        total_operating_expenses = sum(base_operating_expenses.values())
        total_padsplit_expenses = sum(padsplit_expenses.values())
        total_expenses = (total_operating_expenses + total_padsplit_expenses + 
                         refinance_monthly_payment)

        # Calculate cash flows
        monthly_cash_flow = monthly_rent - total_expenses
        annual_cash_flow = monthly_cash_flow * 12

        # Calculate investment metrics
        total_cash_invested = (initial_down_payment + renovation_costs + 
                             initial_closing_costs + refinance_down_payment + 
                             refinance_closing_costs)
        
        equity_captured = after_repair_value - total_investment
        cash_recouped = refinance_loan_amount - initial_loan_amount
        all_in_cost = purchase_price + renovation_costs + initial_closing_costs + refinance_closing_costs

        # Prepare results dictionary
        results = {
            'analysis_name': data.get('analysis_name', ''),
            'analysis_type': 'PadSplit BRRRR',
            'property_address': data.get('property_address', ''),
            'property_type': data.get('property_type', ''),
            'home_square_footage': data.get('home_square_footage', ''),
            'lot_square_footage': data.get('lot_square_footage', ''),
            'year_built': data.get('year_built', ''),
            
            # Purchase and Renovation
            'purchase_price': format_currency(purchase_price),
            'renovation_costs': format_currency(renovation_costs),
            'renovation_duration': renovation_duration,
            'after_repair_value': format_currency(after_repair_value),
            'total_investment': format_currency(total_investment),
            
            # Initial Financing
            'initial_loan_amount': format_currency(initial_loan_amount),
            'initial_down_payment': format_currency(initial_down_payment),
            'initial_interest_rate': f"{initial_interest_rate:.2f}",
            'initial_loan_term': initial_loan_term,
            'initial_monthly_payment': format_currency(initial_monthly_payment),
            'initial_closing_costs': format_currency(initial_closing_costs),
            
            # Refinance
            'refinance_loan_amount': format_currency(refinance_loan_amount),
            'refinance_down_payment': format_currency(refinance_down_payment),
            'refinance_interest_rate': f"{refinance_interest_rate:.2f}",
            'refinance_loan_term': refinance_loan_term,
            'refinance_monthly_payment': format_currency(refinance_monthly_payment),
            'refinance_closing_costs': format_currency(refinance_closing_costs),
            
            # Income
            'monthly_rent': format_currency(monthly_rent),
            
            # Operating Expenses
            'operating_expenses': {k: format_currency(v) for k, v in base_operating_expenses.items()},
            'padsplit_expenses': {k: format_currency(v) for k, v in padsplit_expenses.items()},
            'total_operating_expenses': format_currency(total_operating_expenses),
            'total_padsplit_expenses': format_currency(total_padsplit_expenses),
            'total_expenses': format_currency(total_expenses),
            
            # Cash Flow
            'monthly_cash_flow': format_currency(monthly_cash_flow),
            'annual_cash_flow': format_currency(annual_cash_flow),
            
            # Investment Returns
            'total_cash_invested': format_currency(total_cash_invested),
            'equity_captured': format_currency(equity_captured),
            'cash_recouped': format_currency(cash_recouped),
            'all_in_cost': format_currency(all_in_cost)
        }

        # Calculate returns only if there's an investment
        if total_cash_invested > 0:
            cash_on_cash_return = (annual_cash_flow / total_cash_invested) * 100
            total_profit = equity_captured + annual_cash_flow
            roi = (total_profit / total_cash_invested) * 100
            
            results.update({
                'cash_on_cash_return': f"{cash_on_cash_return:.2f}%",
                'roi': f"{roi:.2f}%"
            })
        else:
            results.update({
                'cash_on_cash_return': "0.00%",
                'roi': "0.00%"
            })

        # Store the percentage values
        results.update({
            'management_percentage': f"{management_percentage:.1f}",
            'maintenance_percentage': f"{maintenance_percentage:.1f}",
            'capex_percentage': f"{capex_percentage:.1f}",
            'vacancy_percentage': f"{vacancy_percentage:.1f}",
            'padsplit_platform_percentage': f"{platform_percentage:.1f}"
        })

        return results

    except Exception as e:
        logging.error(f"Error in calculate_padsplit_brrrr_analysis: {str(e)}")
        logging.error(f"Input data: {data}")
        logging.error(traceback.format_exc())
        raise

def calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_months):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** loan_term_months) / ((1 + monthly_interest_rate) ** loan_term_months - 1)
    return monthly_payment

@analyses_bp.route('/get_analysis/<analysis_id>', methods=['GET'])
@login_required
def get_analysis(analysis_id):
    try:
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        analysis_file = None
        for filename in os.listdir(analyses_dir):
            if filename.startswith(f"{analysis_id}_") and filename.endswith(f"_{current_user.id}.json"):
                analysis_file = filename
                break

        if not analysis_file:
            return jsonify({"success": False, "message": "Analysis not found"}), 404

        filepath = os.path.join(analyses_dir, analysis_file)
        with open(filepath, 'r') as f:
            analysis_data = json.load(f)

        return jsonify({"success": True, "analysis": analysis_data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@analyses_bp.route('/view_analysis/<analysis_id>', methods=['GET'])
@login_required
def view_analysis(analysis_id):
    try:
        analysis = get_analysis(analysis_id)
        if not analysis:
            flash_message('Analysis not found', 'error')
            return redirect(url_for('analyses.view_edit_analysis'))
            
        return render_template('analyses/view_analysis.html', analysis=analysis)
        
    except Exception as e:
        logging.error(f"Error viewing analysis: {str(e)}")
        flash_message('Error loading analysis', 'error')
        return redirect(url_for('analyses.view_edit_analysis'))

@analyses_bp.route('/view_edit_analysis')
@login_required
def view_edit_analysis():
    try:
        page = request.args.get('page', 1, type=int)
        analyses_per_page = 10
        
        analyses, total_pages = get_paginated_analyses(page, analyses_per_page)
        
        return render_template('analyses/view_edit_analysis.html', 
                             analyses=analyses, 
                             current_page=page, 
                             total_pages=total_pages,
                             max=max,  # Pass max function to template
                             min=min)  # Pass min function to template
    except Exception as e:
        logging.error(f"Error in view_edit_analysis: {str(e)}")
        logging.error(traceback.format_exc())
        flash_message('Error loading analyses', 'error')
        # Change to correct dashboard endpoint
        return redirect(url_for('dashboards.dashboards'))  # Updated endpoint

def get_paginated_analyses(page, per_page):
    """Get paginated list of analyses for the current user."""
    try:
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        if not os.path.exists(analyses_dir):
            return [], 0

        all_analyses = []
        for filename in os.listdir(analyses_dir):
            if filename.endswith(f"_{current_user.id}.json"):
                with open(os.path.join(analyses_dir, filename), 'r') as f:
                    analysis_data = json.load(f)
                    # Extract ID from filename
                    analysis_id = filename.split('_')[0]
                    analysis_data['id'] = analysis_id
                    # Get creation date from file if not in data
                    if 'created_at' not in analysis_data:
                        timestamp = os.path.getctime(os.path.join(analyses_dir, filename))
                        analysis_data['created_at'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                    all_analyses.append(analysis_data)

        # Sort analyses by creation date, newest first
        all_analyses.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        # Calculate pagination
        total_analyses = len(all_analyses)
        total_pages = max((total_analyses + per_page - 1) // per_page, 1)
        
        # Adjust page number if out of bounds
        page = min(max(page, 1), total_pages)
        
        # Get the analyses for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_analyses)
        
        return all_analyses[start_idx:end_idx], total_pages
    except Exception as e:
        logging.error(f"Error in get_paginated_analyses: {str(e)}")
        return [], 0

class DynamicFrameDocument(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        BaseDocTemplate.__init__(self, filename, **kwargs)
        self.top_height = 1.5*inch  # Set a default height
        self._calc_frames()

    def handle_flowables(self, flowables):
        frame = self.frame
        for flowable in flowables:
            if isinstance(flowable, Table) and not hasattr(self, 'measured_top_height'):
                # Measure the height of the logo and title table
                w, h = flowable.wrap(self.width, self.height)
                self.top_height = h + 0.25*inch  # Add some padding
                self.measured_top_height = True
                self._calc_frames()
            try:
                frame = frame.add(flowable, self.canv, trySplit=self.allowSplitting)
            except:
                if not frame.allow_split:
                    raise
                flowable = flowable.splitOn(frame, self.canv)
                if not flowable:
                    raise
                frame = frame.split(flowable[0], self.canv)
                self.afterFlowable(flowable[0])
                flowables = [flowable[1]] + flowables[1:]
            if not frame:
                frame = self.handle_nextPageTemplate(flowables)
                self.handle_frameEnd()

    def _calc_frames(self):
        page_height = self.height
        page_width = self.width
        top_margin = self.topMargin
        bottom_margin = self.bottomMargin
        left_margin = self.leftMargin
        right_margin = self.rightMargin

        # Full width frame for logo and title
        full_frame = Frame(left_margin, page_height - top_margin - self.top_height, 
                           page_width - left_margin - right_margin, self.top_height, 
                           id='full')
        
        # Two column frames for the rest of the content
        column_height = page_height - top_margin - bottom_margin - self.top_height
        column_width = (page_width - left_margin - right_margin - 12) / 2  # 12 is the gutter width
        
        left_frame = Frame(left_margin, bottom_margin, column_width, column_height, id='col1')
        right_frame = Frame(left_margin + column_width + 12, bottom_margin, column_width, column_height, id='col2')
        
        self.addPageTemplates([
            PageTemplate(id='FirstPage', frames=[full_frame, left_frame, right_frame]),
            PageTemplate(id='TwoColumn', frames=[left_frame, right_frame])
        ])

@analyses_bp.route('/update_analysis', methods=['POST'])
@login_required
def update_analysis():
    try:
        analysis_data = request.json
        logging.info(f"Received update analysis data: {json.dumps(analysis_data, indent=2)}")

        analysis_id = analysis_data.get('id')
        if not analysis_id:
            return jsonify({"success": False, "message": "Analysis ID is required"}), 400

        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        analysis_file = None
        for filename in os.listdir(analyses_dir):
            if filename.startswith(f"{analysis_id}_") and filename.endswith(f"_{current_user.id}.json"):
                analysis_file = filename
                break

        if not analysis_file:
            return jsonify({"success": False, "message": "Analysis not found"}), 404

        filepath = os.path.join(analyses_dir, analysis_file)

        # Update the analysis data
        updated_data = calculate_analysis_results(analysis_data)

        with open(filepath, 'w') as f:
            json.dump(updated_data, f)

        logging.info(f"Analysis updated successfully: {analysis_id}")
        return jsonify({"success": True, "message": "Analysis updated successfully", "analysis": updated_data})
    except Exception as e:
        logging.error(f"Error updating analysis: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500

@analyses_bp.route('/generate_pdf/<analysis_id>', methods=['GET'])
@login_required
def generate_pdf(analysis_id):
    try:
        current_app.logger.info(f"Starting PDF generation for analysis {analysis_id}")
        
        # Get analysis data
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        analysis_file = None
        
        # Find the correct analysis file
        for filename in os.listdir(analyses_dir):
            if filename.startswith(f"{analysis_id}_") and filename.endswith(f"_{current_user.id}.json"):
                analysis_file = filename
                break

        if not analysis_file:
            current_app.logger.error(f"Analysis file not found for ID: {analysis_id}")
            return jsonify({'error': 'Analysis not found'}), 404

        filepath = os.path.join(analyses_dir, analysis_file)
        
        try:
            # Read and parse the JSON file
            with open(filepath, 'r') as f:
                try:
                    analysis_data = json.load(f)
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"JSON decode error: {str(e)}")
                    return jsonify({'error': f'Invalid analysis data: {str(e)}'}), 500

            # Validate the analysis data
            if not isinstance(analysis_data, dict):
                current_app.logger.error("Analysis data is not a dictionary")
                return jsonify({'error': 'Invalid analysis data format'}), 500

            # Create metrics calculator
            calculator = LenderMetricsCalculator(analysis_data)
            
            # Create PDF buffer
            buffer = BytesIO()
            
            # Generate report
            try:
                generate_lender_report(analysis_data, calculator, buffer)
            except Exception as e:
                current_app.logger.error(f"Error in report generation: {str(e)}")
                current_app.logger.exception("Full traceback:")
                return jsonify({'error': f'Error generating report: {str(e)}'}), 500
            
            # Prepare response
            buffer.seek(0)
            filename = f"{analysis_data.get('analysis_name', 'analysis')}_report.pdf"
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )

        except IOError as e:
            current_app.logger.error(f"File read error: {str(e)}")
            return jsonify({'error': 'Error reading analysis file'}), 500
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {str(e)}")
            current_app.logger.exception("Full traceback:")
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

    except Exception as e:
        current_app.logger.error(f"Global error in generate_pdf: {str(e)}")
        current_app.logger.exception("Full traceback:")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
        
def generate_brrrr_report(metrics, styles):
    """Generate BRRRR-specific report sections"""
    story = []
    
    # Purchase and Renovation
    purchase_data = [
        ["Purchase Price", metrics.get('purchase_price', '$0.00')],
        ["Renovation Costs", metrics.get('renovation_costs', '$0.00')],
        ["After Repair Value (ARV)", metrics.get('after_repair_value', '$0.00')],
        ["Total Initial Investment", metrics.get('total_initial_investment', '$0.00')],
        ["All-in Cost", metrics.get('total_costs', '$0.00')]
    ]
    story.append(Paragraph("Purchase and Renovation", styles))
    story.append(create_table(purchase_data))
    story.append(Spacer(1, 0.25*inch))

    # Income and Operating Expenses
    income_expense_data = [
        ["Monthly Rent", metrics.get('monthly_rent', '$0.00')],
        ["Property Taxes", metrics.get('property_taxes', '$0.00')],
        ["Insurance", metrics.get('insurance', '$0.00')],
        ["CapEx", metrics.get('capex', '$0.00')],
        ["Maintenance", metrics.get('maintenance', '$0.00')],
        ["Vacancy", metrics.get('vacancy', '$0.00')],
        ["Property Management", metrics.get('management', '$0.00')],
        ["Total Monthly Expenses", metrics.get('total_monthly_expenses', '$0.00')],
        ["Monthly Cash Flow", metrics.get('monthly_cash_flow', '$0.00')],
        ["Annual Cash Flow", metrics.get('annual_cash_flow', '$0.00')]
    ]
    story.append(Paragraph("Income and Expenses", styles))
    story.append(create_table(income_expense_data))
    story.append(Spacer(1, 0.25*inch))

    # Financing Details
    financing_data = [
        ["Initial Loan Amount", metrics.get('initial_loan_amount', '$0.00')],
        ["Initial Monthly Payment", metrics.get('initial_monthly_payment', '$0.00')],
        ["Initial Interest Rate", metrics.get('initial_interest_rate', '0.00') + '%'],
        ["Initial Down Payment", metrics.get('initial_down_payment', '$0.00')],
        ["Initial Closing Costs", metrics.get('initial_closing_costs', '$0.00')],
        ["Refinance Loan Amount", metrics.get('refinance_loan_amount', '$0.00')],
        ["Refinance Monthly Payment", metrics.get('refinance_monthly_payment', '$0.00')],
        ["Refinance Interest Rate", metrics.get('refinance_interest_rate', '0.00') + '%'],
        ["Refinance Down Payment", metrics.get('refinance_down_payment', '$0.00')],
        ["Refinance Closing Costs", metrics.get('refinance_closing_costs', '$0.00')]
    ]
    story.append(Paragraph("Financing Details", styles))
    story.append(create_table(financing_data))
    story.append(Spacer(1, 0.25*inch))

    # Investment Returns
    returns_data = [
        ["Actual Cash Invested", metrics.get('actual_cash_invested', '$0.00')],
        ["Cash Recouped in Refinance", metrics.get('cash_recouped', '$0.00')],
        ["Equity Captured", metrics.get('equity_captured', '$0.00')],
        ["Cash on Cash Return", metrics.get('cash_on_cash_return', '0.00%')],
        ["Return on Investment (ROI)", metrics.get('roi', '0.00%')]
    ]
    story.append(Paragraph("Investment Returns", styles))
    story.append(create_table(returns_data))
    
    return story

def generate_long_term_rental_report(data, styles):
    story = []

    subtitle_style = styles.get('Subtitle', styles['Heading2'])  # Use Heading2 as fallback

    # Left Column Content
    # Key Performance Indicators
    story.append(Paragraph("Key Performance Indicators", subtitle_style))
    kpi_data = [
        ["Gross Monthly Income", f"${data.get('gross_monthly_income', 'N/A')}"],
        ["Net Monthly Cash Flow", f"${data.get('net_monthly_cash_flow', 'N/A')}"],
        ["Cash-on-Cash Return", f"{data.get('cash_on_cash_return', 'N/A')}"]
    ]
    story.append(create_table(kpi_data))
    story.append(Spacer(1, 0.25*inch))

    # Operating Expenses
    story.append(Paragraph("Operating Expenses", subtitle_style))
    expense_data = [[k, f"${v}"] for k, v in data.get('operating_expenses', {}).items()]
    story.append(create_table(expense_data))
    story.append(Spacer(1, 0.25*inch))

    # Renovation and Holding Costs
    story.append(Paragraph("Renovation and Holding Costs", subtitle_style))
    renovation_data = [
        ["Renovation Costs", f"${data.get('renovation_costs', 'N/A')}"],
        ["Holding Costs", f"${data.get('holding_costs', 'N/A')}"]
    ]
    story.append(create_table(renovation_data))
    story.append(Spacer(1, 0.25*inch))

    # Move to the right column
    story.append(FrameBreak())

    # Right Column Content
    # Loan Information
    story.append(Paragraph("Loan Information", subtitle_style))
    for i, loan in enumerate(data.get('loans', [])):
        if i > 0:
            story.append(Spacer(1, 0.15*inch))  # Add some space between loans
        loan_data = [
            ["Loan Name", loan.get('name', 'N/A')],
            ["Loan Amount", f"${loan.get('amount', 'N/A')}"],
            ["Down Payment", f"${loan.get('down_payment', 'N/A')}"],
            ["Monthly Payment", f"${loan.get('monthly_payment', 'N/A')}"],
            ["Interest Rate", f"{loan.get('interest_rate', 'N/A')}%"],
            ["Loan Term", f"{loan.get('term', 'N/A')} months"],
            ["Closing Costs", f"${loan.get('closing_costs', 'N/A')}"]
        ]
        story.append(create_table(loan_data))

    return story

def generate_padsplit_ltr_report(story, analysis, styles):
    """Generate PDF report sections for PadSplit LTR analysis"""
    # Property Information
    story.append(Paragraph("Property Information", styles['Subtitle']))
    property_data = [
        ["Address", analysis.get('property_address', 'N/A')],
        ["Property Type", analysis.get('property_type', 'N/A')],
        ["Home Square Footage", analysis.get('home_square_footage', 'N/A')],
        ["Lot Square Footage", analysis.get('lot_square_footage', 'N/A')],
        ["Year Built", analysis.get('year_built', 'N/A')]
    ]
    story.append(create_table(property_data))
    story.append(Spacer(1, 0.25*inch))

    # Purchase Details
    story.append(Paragraph("Purchase Details", styles['Subtitle']))
    purchase_data = [
        ["Purchase Price", analysis.get('purchase_price', 'N/A')],
        ["After Repair Value", analysis.get('after_repair_value', 'N/A')],
        ["Cash to Seller", analysis.get('cash_to_seller', 'N/A')],
        ["Closing Costs", analysis.get('closing_costs', 'N/A')],
        ["Assignment Fee", analysis.get('assignment_fee', 'N/A')],
        ["Marketing Costs", analysis.get('marketing_costs', 'N/A')],
        ["Renovation Costs", analysis.get('renovation_costs', 'N/A')],
        ["Renovation Duration", f"{analysis.get('renovation_duration', 'N/A')} months"]
    ]
    story.append(create_table(purchase_data))
    story.append(Spacer(1, 0.25*inch))

    # Move to next column
    story.append(FrameBreak())

    # Income and Returns
    story.append(Paragraph("Income and Returns", styles['Subtitle']))
    returns_data = [
        ["Monthly Income", analysis.get('monthly_rent', 'N/A')],
        ["Monthly Cash Flow", analysis.get('monthly_cash_flow', 'N/A')],
        ["Annual Cash Flow", analysis.get('annual_cash_flow', 'N/A')],
        ["Cash-on-Cash Return", analysis.get('cash_on_cash_return', 'N/A')],
        ["Total Cash Invested", analysis.get('total_cash_invested', 'N/A')]
    ]
    story.append(create_table(returns_data))
    story.append(Spacer(1, 0.25*inch))

    # Operating Expenses
    story.append(Paragraph("Operating Expenses", styles['Subtitle']))
    expense_data = [
        ["Management", f"{analysis.get('management_percentage', 'N/A')}%"],
        ["CapEx", f"{analysis.get('capex_percentage', 'N/A')}%"],
        ["Repairs", f"{analysis.get('repairs_percentage', 'N/A')}%"],
        ["Vacancy", f"{analysis.get('vacancy_percentage', 'N/A')}%"],
        ["Property Taxes", analysis.get('property_taxes', 'N/A')],
        ["Insurance", analysis.get('insurance', 'N/A')],
        ["HOA/COA/COOP", analysis.get('hoa_coa_coop', 'N/A')],
        ["Total Operating Expenses", analysis.get('total_operating_expenses', 'N/A')]
    ]
    story.append(create_table(expense_data))
    story.append(Spacer(1, 0.25*inch))

    # Move to next column
    story.append(FrameBreak())

    # PadSplit Specific Expenses
    story.append(Paragraph("PadSplit Expenses", styles['Subtitle']))
    padsplit_data = [
        ["Platform Fee", f"{analysis.get('padsplit_platform_percentage', 'N/A')}%"],
        ["Utilities", analysis.get('utilities', 'N/A')],
        ["Internet", analysis.get('internet', 'N/A')],
        ["Cleaning Costs", analysis.get('cleaning_costs', 'N/A')],
        ["Pest Control", analysis.get('pest_control', 'N/A')],
        ["Landscaping", analysis.get('landscaping', 'N/A')],
        ["Total PadSplit Expenses", analysis.get('total_padsplit_expenses', 'N/A')]
    ]
    story.append(create_table(padsplit_data))
    story.append(Spacer(1, 0.25*inch))

    # Loan Information
    if analysis.get('loans'):
        story.append(Paragraph("Loan Information", styles['Subtitle']))
        for i, loan in enumerate(analysis['loans'], 1):
            loan_data = [
                [f"Loan {i} - {loan.get('name', 'N/A')}", ""],
                ["Amount", loan.get('amount', 'N/A')],
                ["Down Payment", loan.get('down_payment', 'N/A')],
                ["Interest Rate", f"{loan.get('interest_rate', 'N/A')}%"],
                ["Term", f"{loan.get('term', 'N/A')} months"],
                ["Closing Costs", loan.get('closing_costs', 'N/A')]
            ]
            story.append(create_table(loan_data))
            story.append(Spacer(1, 0.15*inch))

def generate_padsplit_brrrr_report(story, analysis, styles):
    """Generate PDF report sections for PadSplit BRRRR analysis"""
    # Property Information
    story.append(Paragraph("Property Information", styles['Subtitle']))
    property_data = [
        ["Address", analysis.get('property_address', 'N/A')],
        ["Property Type", analysis.get('property_type', 'N/A')],
        ["Home Square Footage", analysis.get('home_square_footage', 'N/A')],
        ["Lot Square Footage", analysis.get('lot_square_footage', 'N/A')],
        ["Year Built", analysis.get('year_built', 'N/A')]
    ]
    story.append(create_table(property_data))
    story.append(Spacer(1, 0.25*inch))

    # Purchase and Renovation
    story.append(Paragraph("Purchase and Renovation", styles['Subtitle']))
    purchase_data = [
        ["Purchase Price", analysis.get('purchase_price', 'N/A')],
        ["Renovation Costs", analysis.get('renovation_costs', 'N/A')],
        ["Renovation Duration", f"{analysis.get('renovation_duration', 'N/A')} months"],
        ["After Repair Value", analysis.get('after_repair_value', 'N/A')],
        ["Total Investment", analysis.get('total_investment', 'N/A')]
    ]
    story.append(create_table(purchase_data))
    story.append(Spacer(1, 0.25*inch))

    # Move to next column
    story.append(FrameBreak())

    # Financing Details
    story.append(Paragraph("Initial Financing", styles['Subtitle']))
    initial_financing_data = [
        ["Initial Loan Amount", analysis.get('initial_loan_amount', 'N/A')],
        ["Initial Down Payment", analysis.get('initial_down_payment', 'N/A')],
        ["Initial Interest Rate", f"{analysis.get('initial_interest_rate', 'N/A')}%"],
        ["Initial Loan Term", f"{analysis.get('initial_loan_term', 'N/A')} months"],
        ["Initial Monthly Payment", analysis.get('initial_monthly_payment', 'N/A')],
        ["Initial Closing Costs", analysis.get('initial_closing_costs', 'N/A')]
    ]
    story.append(create_table(initial_financing_data))
    story.append(Spacer(1, 0.25*inch))

    # Refinance Details
    story.append(Paragraph("Refinance Details", styles['Subtitle']))
    refinance_data = [
        ["Refinance Loan Amount", analysis.get('refinance_loan_amount', 'N/A')],
        ["Refinance Down Payment", analysis.get('refinance_down_payment', 'N/A')],
        ["Refinance Interest Rate", f"{analysis.get('refinance_interest_rate', 'N/A')}%"],
        ["Refinance Loan Term", f"{analysis.get('refinance_loan_term', 'N/A')} months"],
        ["Refinance Monthly Payment", analysis.get('refinance_monthly_payment', 'N/A')],
        ["Refinance Closing Costs", analysis.get('refinance_closing_costs', 'N/A')]
    ]
    story.append(create_table(refinance_data))
    story.append(Spacer(1, 0.25*inch))

    # Move to next column
    story.append(FrameBreak())

    # Income and Returns
    story.append(Paragraph("Income and Returns", styles['Subtitle']))
    returns_data = [
        ["Monthly Rent", analysis.get('monthly_rent', 'N/A')],
        ["Monthly Cash Flow", analysis.get('monthly_cash_flow', 'N/A')],
        ["Annual Cash Flow", analysis.get('annual_cash_flow', 'N/A')],
        ["Cash-on-Cash Return", analysis.get('cash_on_cash_return', 'N/A')],
        ["ROI", analysis.get('roi', 'N/A')],
        ["Total Cash Invested", analysis.get('total_cash_invested', 'N/A')],
        ["Equity Captured", analysis.get('equity_captured', 'N/A')],
        ["Cash Recouped", analysis.get('cash_recouped', 'N/A')]
    ]
    story.append(create_table(returns_data))
    story.append(Spacer(1, 0.25*inch))

    # PadSplit Specific Expenses
    story.append(Paragraph("PadSplit Expenses", styles['Subtitle']))
    padsplit_data = [
        ["Platform Fee", f"{analysis.get('padsplit_platform_percentage', 'N/A')}%"],
        ["Utilities", analysis.get('utilities', 'N/A')],
        ["Internet", analysis.get('internet', 'N/A')],
        ["Cleaning Costs", analysis.get('cleaning_costs', 'N/A')],
        ["Pest Control", analysis.get('pest_control', 'N/A')],
        ["Landscaping", analysis.get('landscaping', 'N/A')],
        ["Total PadSplit Expenses", analysis.get('total_padsplit_expenses', 'N/A')]
    ]
    story.append(create_table(padsplit_data))

def create_table(data):
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    return table