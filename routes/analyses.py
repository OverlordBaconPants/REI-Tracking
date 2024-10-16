from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import uuid
import os
import traceback
import json
import logging
import locale
from config import Config
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, FrameBreak, PageTemplate, Image, NextPageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import BaseDocTemplate

analyses_bp = Blueprint('analyses', __name__)

# Set the locale to handle comma formatting
locale.setlocale(locale.LC_ALL, '')

def format_currency(value):
    return locale.format_string("%.2f", value, grouping=True)

@analyses_bp.route('/create_analysis', methods=['GET', 'POST'])
@login_required
def create_analysis():
    if request.method == 'POST':
        try:
            analysis_data = request.json
            logging.info(f"Received analysis data: {json.dumps(analysis_data, indent=2)}")

            analysis_type = analysis_data.get('analysis_type', 'Long-Term Rental')
            logging.info(f"Analysis type: {analysis_type}")

            # Check for required fields based on analysis type
            if analysis_type == 'BRRRR':
                required_fields = ['analysis_name', 'purchase_price', 'renovation_costs', 'renovation_duration', 'after_repair_value',
                                   'initial_loan_amount', 'initial_interest_rate', 'initial_loan_term', 'initial_closing_costs',
                                   'refinance_loan_amount', 'refinance_interest_rate', 'refinance_loan_term', 'refinance_closing_costs',
                                   'monthly_rent', 'property_taxes', 'insurance', 'maintenance_percentage',
                                   'vacancy_percentage', 'capex_percentage', 'management_percentage']
            else:
                required_fields = ['analysis_name', 'monthly_income', 'management_percentage', 'capex_percentage', 
                                   'repairs_percentage', 'vacancy_percentage', 'property_taxes', 'insurance', 
                                   'hoa_coa_coop', 'renovation_costs', 'renovation_duration', 'hoa_coa_coop']

            for field in required_fields:
                if field not in analysis_data:
                    return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400

            analysis_data['user_id'] = current_user.id

            analysis_data = calculate_analysis_results(analysis_data)

            # Generate a unique ID for the analysis
            analysis_id = str(uuid.uuid4())
            analysis_data['id'] = analysis_id

            analysis_name = secure_filename(analysis_data['analysis_name'])
            
            filename = f"{analysis_id}_{current_user.id}.json"
            filepath = os.path.join(Config.DATA_DIR, 'analyses', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(analysis_data, f)
            
            return jsonify({"success": True, "message": "Analysis created successfully!", "analysis": analysis_data})
        except Exception as e:
            logging.error(f"Error creating analysis: {str(e)}")
            return jsonify({"success": False, "message": f"An error occurred: {str(e)}"}), 500
    
    return render_template('analyses/create_analysis.html')

def calculate_analysis_results(data):
    try:
        logging.info(f"Entering calculate_analysis_results with data: {json.dumps(data, indent=2)}")
        
        analysis_type = data.get('analysis_type', 'Long-Term Rental')
        logging.info(f"Analysis type in calculate_analysis_results: {analysis_type}")
        
        # Ensure analysis_name is preserved
        analysis_name = data.get('analysis_name')
        logging.info(f"Analysis name: {analysis_name}")
        
        if analysis_type == 'BRRRR':
            result = calculate_brrrr_analysis(data)
        else:
            result = calculate_long_term_rental_analysis(data)
        
        # Ensure analysis_name is added back to the result
        result['analysis_name'] = analysis_name
        
        logging.info(f"Exiting calculate_analysis_results with result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logging.error(f"Error in calculate_analysis_results: {str(e)}")
        logging.error(traceback.format_exc())
        raise

def calculate_long_term_rental_analysis(data):
    try:
        # Gross Monthly Income
        data['gross_monthly_income'] = float(data['monthly_income'])

        # Operating Expenses
        data['operating_expenses'] = {
            "Management": data['gross_monthly_income'] * float(data['management_percentage']) / 100,
            "CapEx": data['gross_monthly_income'] * float(data['capex_percentage']) / 100,
            "Repairs": data['gross_monthly_income'] * float(data['repairs_percentage']) / 100,
            "Vacancy": data['gross_monthly_income'] * float(data['vacancy_percentage']) / 100,
            "Property Taxes": float(data['property_taxes']),
            "Insurance": float(data['insurance']),
            "HOA/COA/COOP": float(data['hoa_coa_coop'])
        }

        # Total Monthly Operating Expenses
        total_monthly_operating_expenses = sum(data['operating_expenses'].values())

        # Calculate total monthly loan payments, down payments, and closing costs
        total_monthly_loan_payment = 0
        total_down_payment = 0
        total_closing_costs = 0
        if 'loans' in data:
            for loan in data['loans']:
                loan['monthly_payment'] = calculate_monthly_payment(
                    float(loan['amount']), 
                    float(loan['interest_rate']), 
                    int(loan['term'])
                )
                total_monthly_loan_payment += loan['monthly_payment']
                total_down_payment += float(loan['down_payment'])
                total_closing_costs += float(loan['closing_costs'])

        # Calculate holding costs
        monthly_holding_costs = (total_monthly_loan_payment + 
                                 float(data['property_taxes']) + 
                                 float(data['insurance']) + 
                                 float(data['hoa_coa_coop']))
        data['holding_costs'] = monthly_holding_costs * float(data['renovation_duration'])

        # Net Monthly Cash Flow
        data['net_monthly_cash_flow'] = data['gross_monthly_income'] - total_monthly_operating_expenses - total_monthly_loan_payment

        # Cash-on-Cash Return
        total_cash_invested = total_down_payment + total_closing_costs + float(data['renovation_costs'])
        annual_cash_flow = data['net_monthly_cash_flow'] * 12
        data['cash_on_cash_return'] = (annual_cash_flow / total_cash_invested) * 100 if total_cash_invested > 0 else 0

        # Renovation Costs
        data['renovation_costs'] = float(data['renovation_costs'])

        # Summary variables
        data['total_down_payment'] = total_down_payment
        data['total_closing_costs'] = total_closing_costs
        data['total_cash_invested'] = total_cash_invested

        # Format currency values
        data['gross_monthly_income'] = format_currency(data['gross_monthly_income'])
        data['net_monthly_cash_flow'] = format_currency(data['net_monthly_cash_flow'])
        data['holding_costs'] = format_currency(data['holding_costs'])
        data['renovation_costs'] = format_currency(data['renovation_costs'])
        data['total_down_payment'] = format_currency(data['total_down_payment'])
        data['total_closing_costs'] = format_currency(data['total_closing_costs'])
        data['total_cash_invested'] = format_currency(data['total_cash_invested'])

        for expense, value in data['operating_expenses'].items():
            data['operating_expenses'][expense] = format_currency(value)

        for loan in data['loans']:
            loan['amount'] = format_currency(float(loan['amount']))
            loan['down_payment'] = format_currency(float(loan['down_payment']))
            loan['monthly_payment'] = format_currency(loan['monthly_payment'])
            loan['closing_costs'] = format_currency(float(loan['closing_costs']))

        # Format percentages
        data['cash_on_cash_return'] = f"{data['cash_on_cash_return']:.2f}%"

        return data
    except Exception as e:
        logging.error(f"Error in calculate_long_term_rental_analysis: {str(e)}")
        raise

def calculate_brrrr_analysis(data):
    try:
        # Purchase and Renovation
        purchase_price = float(data['purchase_price'])
        renovation_costs = float(data['renovation_costs'])
        after_repair_value = float(data['after_repair_value'])
        total_investment = purchase_price + renovation_costs

        # Initial Financing
        initial_loan_amount = float(data['initial_loan_amount'])
        initial_down_payment = float(data['initial_down_payment'])
        initial_interest_rate = float(data['initial_interest_rate'])
        initial_loan_term = int(data['initial_loan_term'])
        initial_closing_costs = float(data['initial_closing_costs'])

        # Refinance
        refinance_loan_amount = float(data['refinance_loan_amount'])
        refinance_down_payment = float(data['refinance_down_payment'])
        refinance_interest_rate = float(data['refinance_interest_rate'])
        refinance_loan_term = int(data['refinance_loan_term'])
        refinance_closing_costs = float(data['refinance_closing_costs'])

        # Rental Income and Expenses
        monthly_rent = float(data['monthly_rent'])
        property_taxes = float(data['property_taxes'])
        insurance = float(data['insurance'])
        maintenance = monthly_rent * float(data['maintenance_percentage']) / 100
        vacancy = monthly_rent * float(data['vacancy_percentage']) / 100
        capex = monthly_rent * float(data['capex_percentage']) / 100
        management = monthly_rent * float(data['management_percentage']) / 100

        # Calculate monthly payments
        initial_monthly_payment = calculate_monthly_payment(initial_loan_amount, initial_interest_rate, initial_loan_term)
        refinance_monthly_payment = calculate_monthly_payment(refinance_loan_amount, refinance_interest_rate, refinance_loan_term)

        # Calculate cash flow
        total_expenses = property_taxes + insurance + maintenance + vacancy + capex + management + refinance_monthly_payment
        monthly_cash_flow = monthly_rent - total_expenses
        annual_cash_flow = monthly_cash_flow * 12

        # Calculate total cash invested
        total_cash_invested = initial_down_payment + renovation_costs + initial_closing_costs + refinance_down_payment + refinance_closing_costs

        # Calculate cash-on-cash return
        cash_on_cash_return = (annual_cash_flow / total_cash_invested) * 100 if total_cash_invested > 0 else 0

        # Calculate equity captured
        equity_captured = after_repair_value - total_investment

        # Calculate ROI
        total_profit = equity_captured + annual_cash_flow
        roi = (total_profit / total_cash_invested) * 100 if total_cash_invested > 0 else 0

        # Calculate cash recouped
        cash_recouped = refinance_loan_amount - initial_loan_amount

        # Calculate all-in cost
        all_in_cost = purchase_price + renovation_costs + initial_closing_costs + refinance_closing_costs

        # Prepare results
        results = {
            'analysis_name': data.get('analysis_name'),
            'analysis_type': 'BRRRR',
            'purchase_price': format_currency(purchase_price),
            'renovation_costs': format_currency(renovation_costs),
            'after_repair_value': format_currency(after_repair_value),
            'total_investment': format_currency(total_investment),
            'initial_loan_amount': format_currency(initial_loan_amount),
            'initial_down_payment': format_currency(initial_down_payment),
            'initial_monthly_payment': format_currency(initial_monthly_payment),
            'refinance_loan_amount': format_currency(refinance_loan_amount),
            'refinance_down_payment': format_currency(refinance_down_payment),
            'refinance_monthly_payment': format_currency(refinance_monthly_payment),
            'monthly_rent': format_currency(monthly_rent),
            'total_expenses': format_currency(total_expenses),
            'monthly_cash_flow': format_currency(monthly_cash_flow),
            'annual_cash_flow': format_currency(annual_cash_flow),
            'total_cash_invested': format_currency(total_cash_invested),
            'cash_on_cash_return': f"{cash_on_cash_return:.2f}%",
            'equity_captured': format_currency(equity_captured),
            'roi': f"{roi:.2f}%",
            'cash_recouped': format_currency(cash_recouped),
            'all_in_cost': format_currency(all_in_cost)
        }

        return results
    except Exception as e:
        logging.error(f"Error in calculate_brrrr_analysis: {str(e)}")
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

@analyses_bp.route('/view_edit_analysis')
@login_required
def view_edit_analysis():
    # Get all analyses for the current user
    analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
    user_analyses = []
    
    if os.path.exists(analyses_dir):
        for filename in os.listdir(analyses_dir):
            if filename.endswith(f"_{current_user.id}.json"):
                with open(os.path.join(analyses_dir, filename), 'r') as f:
                    analysis_data = json.load(f)
                    user_analyses.append(analysis_data)
    
    return render_template('analyses/view_edit_analysis.html', analyses=user_analyses)

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
        logging.info(f"Starting PDF generation for analysis_id: {analysis_id}")
        
        # Find the correct analysis file
        analyses_dir = os.path.join(Config.DATA_DIR, 'analyses')
        analysis_file = None
        for filename in os.listdir(analyses_dir):
            if filename.startswith(f"{analysis_id}_") and filename.endswith(f"_{current_user.id}.json"):
                analysis_file = filename
                break
        
        if not analysis_file:
            logging.error(f"Analysis file not found for analysis_id: {analysis_id}")
            return jsonify({"success": False, "message": "Analysis not found"}), 404

        filepath = os.path.join(analyses_dir, analysis_file)
        logging.info(f"Analysis file found: {filepath}")
        
        with open(filepath, 'r') as f:
            analysis_data = json.load(f)
        logging.info(f"Analysis data loaded successfully: {json.dumps(analysis_data, indent=2)}")

        # Create a PDF
        buffer = BytesIO()
        doc = DynamicFrameDocument(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=18)
        
        story = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=1))
        styles.add(ParagraphStyle(
            name='Subtitle',
            parent=styles['Heading2'],
            fontSize=14,
            leading=16,
            alignment=TA_LEFT
        ))
        title_style = ParagraphStyle(name='Title', parent=styles['Heading1'], alignment=1)
        normal_style = styles['Normal']
        
        # Add logo and title
        logo_path = os.path.join(Config.BASE_DIR, 'static', 'images', 'logo.png')
        if not os.path.exists(logo_path):
            logging.error(f"Logo file not found at {logo_path}")
            raise FileNotFoundError(f"Logo file not found at {logo_path}")
        
        logo = Image(logo_path, width=0.8*inch, height=0.8*inch)  # Slightly reduced size
        title = f"Analysis Report: {analysis_data.get('analysis_name', 'N/A')} ({analysis_data.get('analysis_type', 'N/A')})"
        title_paragraph = Paragraph(title, title_style)
        
        # Create a table for logo and title with adjusted widths
        available_width = doc.width
        logo_width = 1*inch  # Width allocated for logo column
        title_width = available_width - logo_width  # Remaining width for title
        
        title_table = Table([[logo, title_paragraph]], colWidths=[logo_width, title_width])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(title_table)
        story.append(Spacer(1, 0.25*inch))

        logging.info("Logo and title added to story")

        # Switch to two-column layout
        story.append(NextPageTemplate('TwoColumn'))
        story.append(FrameBreak())

        # Generate the report based on analysis type
        analysis_type = analysis_data.get('analysis_type', 'N/A')
        logging.info(f"Generating report for analysis type: {analysis_type}")
        if analysis_type == 'BRRRR':
            story.extend(generate_brrrr_report(analysis_data, styles))
        elif analysis_type == 'Long-Term Rental':
            story.extend(generate_long_term_rental_report(analysis_data, styles))
        else:
            logging.error(f"Unsupported analysis type: {analysis_type}")
            raise ValueError(f"Unsupported analysis type: {analysis_type}")

        logging.info("Content generation completed")

        logging.info("Building PDF")
        doc.build(story)
        logging.info("PDF built successfully")
        
        buffer.seek(0)
        logging.info("Sending PDF file")
        return send_file(buffer, as_attachment=True, download_name=f"{analysis_data.get('analysis_name', 'analysis')}_report.pdf", mimetype='application/pdf')
    
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"success": False, "message": f"An error occurred while generating the PDF: {str(e)}"}), 500

def generate_brrrr_report(data, styles):
    story = []
    
    # Create a centered style for sub-headers
    centered_style = ParagraphStyle(
        'Centered',
        parent=styles['Heading3'],
        alignment=TA_CENTER,
        spaceAfter=12
    )

    # Left Column
    story.append(Paragraph("Purchase and Renovation", styles['Heading2']))
    purchase_data = [
        ["Purchase Price", f"${data.get('purchase_price', 'N/A')}"],
        ["Renovation Costs", f"${data.get('renovation_costs', 'N/A')}"],
        ["Total Investment", f"${data.get('total_investment', 'N/A')}"],
        ["After Repair Value (ARV)", f"${data.get('after_repair_value', 'N/A')}"],
        ["All-in Cost", f"${data.get('all_in_cost', 'N/A')}"]
    ]
    story.append(create_table(purchase_data))
    story.append(Spacer(1, 0.25*inch))

    story.append(Paragraph("Initial Financing", styles['Heading2']))
    initial_financing_data = [
        ["Initial Loan Amount", f"${data.get('initial_loan_amount', 'N/A')}"],
        ["Initial Down Payment", f"${data.get('initial_down_payment', 'N/A')}"],
        ["Initial Monthly Payment", f"${data.get('initial_monthly_payment', 'N/A')}"]
    ]
    story.append(create_table(initial_financing_data))
    story.append(Spacer(1, 0.25*inch))

    story.append(Paragraph("Refinance", styles['Heading2']))
    refinance_data = [
        ["Refinance Loan Amount", f"${data.get('refinance_loan_amount', 'N/A')}"],
        ["Refinance Down Payment", f"${data.get('refinance_down_payment', 'N/A')}"],
        ["Refinance Monthly Payment", f"${data.get('refinance_monthly_payment', 'N/A')}"]
    ]
    story.append(create_table(refinance_data))
    story.append(Spacer(1, 0.25*inch))

    # Add a FrameBreak to move to the second column
    story.append(FrameBreak())

    # Right Column
    story.append(Paragraph("Income and Expenses", styles['Heading2']))
    income_expense_data = [
        ["Monthly Rent", f"${data.get('monthly_rent', 'N/A')}"],
        ["Total Monthly Expenses", f"${data.get('total_expenses', 'N/A')}"],
        ["Monthly Cash Flow", f"${data.get('monthly_cash_flow', 'N/A')}"],
        ["Annual Cash Flow", f"${data.get('annual_cash_flow', 'N/A')}"]
    ]
    story.append(create_table(income_expense_data))
    story.append(Spacer(1, 0.25*inch))

    story.append(Paragraph("Investment Returns", styles['Heading2']))
    returns_data = [
        ["Total Cash Invested", f"${data.get('total_cash_invested', 'N/A')}"],
        ["Cash-on-Cash Return", data.get('cash_on_cash_return', 'N/A')],
        ["Return on Investment (ROI)", data.get('roi', 'N/A')],
        ["Equity Captured", f"${data.get('equity_captured', 'N/A')}"],
        ["Cash Recouped", f"${data.get('cash_recouped', 'N/A')}"]
    ]
    story.append(create_table(returns_data))
    story.append(Spacer(1, 0.25*inch))

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