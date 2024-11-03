from flask import current_app
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
import os
from config import Config

# Set up module-level logger
logger = logging.getLogger(__name__)

def safe_float(value, default=0.0):
    """Safely convert string or numeric value to float."""
    try:
        if isinstance(value, str):
            # Remove currency symbols and commas
            value = value.replace('$', '').replace(',', '').strip()
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

def format_currency(value):
    """Format a number as currency."""
    try:
        if isinstance(value, str):
            value = safe_float(value)
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def create_table(data):
    """Create a formatted table for the PDF report"""
    table = Table(data, colWidths=[250, 250])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT')  # Right-align the values
    ])
    table.setStyle(style)
    return table

class LenderMetricsCalculator:
    """Calculate metrics relevant for private lender analysis reports"""
    
    def __init__(self, analysis_data):
        self.data = analysis_data
        self.current_market_rate = 7.5  # Could be fetched from an API

    def get_metric(self, key, default=0.0):
        """Get a metric value with safe float conversion."""
        value = self.data.get(key, default)
        if isinstance(value, (str, int, float)):
            return safe_float(value, default)
        return default

    def clean_number(self, value):
        """Clean numeric strings by removing currency symbols and commas"""
        if isinstance(value, str):
            # Remove currency symbols, commas, and whitespace
            cleaned = value.replace('$', '').replace(',', '').replace(' ', '')
            return float(cleaned or 0)
        return float(value or 0)
        
    def calculate_security_metrics(self):
        """Calculate loan security and collateral metrics"""
        loan_amount = self.clean_number(self.data.get('initial_loan_amount', 0))
        current_value = self.clean_number(self.data.get('purchase_price', 0))
        arv = self.clean_number(self.data.get('after_repair_value', 0))
        noi = self.calculate_net_operating_income()
        
        return {
            'loan_to_value': (loan_amount / current_value * 100) if current_value > 0 else 0,
            'loan_to_arv': (loan_amount / arv * 100) if arv > 0 else 0,
            'dscr': self.calculate_dscr(),
            'equity_cushion': arv - loan_amount,
            'equity_percentage': ((arv - loan_amount) / arv * 100) if arv > 0 else 0
        }
    
    def calculate_dscr(self):
        """Calculate Debt Service Coverage Ratio"""
        annual_noi = self.calculate_net_operating_income() * 12
        annual_debt_service = self.calculate_annual_debt_service()
        
        return annual_noi / annual_debt_service if annual_debt_service > 0 else 0
    
    def calculate_net_operating_income(self):
        """Calculate monthly Net Operating Income"""
        monthly_rent = self.clean_number(self.data.get('monthly_rent', 0))
        
        # Calculate operating expenses
        expenses = {
            'management': monthly_rent * self.clean_number(self.data.get('management_percentage', 0)) / 100,
            'maintenance': monthly_rent * self.clean_number(self.data.get('maintenance_percentage', 0)) / 100,
            'vacancy': monthly_rent * self.clean_number(self.data.get('vacancy_percentage', 0)) / 100,
            'property_taxes': self.clean_number(self.data.get('property_taxes', 0)),
            'insurance': self.clean_number(self.data.get('insurance', 0))
        }
        
        total_expenses = sum(expenses.values())
        return monthly_rent - total_expenses
    
    def calculate_annual_debt_service(self):
        """Calculate total annual debt payments"""
        monthly_payment = 0
        if self.data.get('loans'):
            for loan in self.data['loans']:
                monthly_payment += float(loan.get('monthly_payment', 0))
        return monthly_payment * 12
    
    def calculate_exit_metrics(self):
        """Calculate exit strategy metrics"""
        arv = self.clean_number(self.data.get('after_repair_value', 0))
        total_investment = self.clean_number(self.data.get('total_investment', 0))
        monthly_rent = self.clean_number(self.data.get('monthly_rent', 0))
        
        conventional_ltv_75 = arv * 0.75
        conventional_payment = self.calculate_monthly_payment(
            conventional_ltv_75, 
            self.current_market_rate, 
            360  # 30-year term
        )
        
        return {
            'refinance_potential': {
                'conventional_ltv_75': conventional_ltv_75,
                'conventional_ltv_80': arv * 0.80,
                'estimated_payment': conventional_payment
            },
            'sale_potential': {
                'profit_at_arv': arv - total_investment,
                'profit_margin': ((arv - total_investment) / total_investment * 100) if total_investment > 0 else 0,
                'estimated_dom': 45  # Could be fetched from market data
            },
            'rental_metrics': {
                'gross_rent_multiplier': arv / (monthly_rent * 12) if monthly_rent > 0 else 0,
                'cap_rate': (self.calculate_net_operating_income() * 12 / arv * 100) if arv > 0 else 0
            }
        }
    
    def calculate_cost_breakdown(self):
        """Calculate detailed cost breakdown"""
        renovation_costs = self.clean_number(self.data.get('renovation_costs', 0))
        renovation_duration = int(self.clean_number(self.data.get('renovation_duration', 0)))
        
        return {
            'acquisition_costs': {
                'purchase_price': self.clean_number(self.data.get('purchase_price', 0)),
                'closing_costs': self.clean_number(self.data.get('closing_costs', 0)),
                'title_insurance': self.clean_number(self.data.get('title_insurance', 0)),
                'legal_fees': self.clean_number(self.data.get('legal_fees', 0))
            },
            'renovation_costs': {
                'total_budget': renovation_costs,
                'contingency': renovation_costs * 0.10
            },
            'holding_costs': {
                'property_taxes': self.clean_number(self.data.get('property_taxes', 0)) * renovation_duration,
                'insurance': self.clean_number(self.data.get('insurance', 0)) * renovation_duration,
                'utilities': self.clean_number(self.data.get('utilities', 0)) * renovation_duration,
                'loan_payments': self.calculate_holding_period_payments(renovation_duration)
            }
        }
    
    def calculate_holding_period_payments(self, duration):
        """Calculate total loan payments during holding period"""
        monthly_payment = 0
        if self.data.get('loans'):
            for loan in self.data['loans']:
                monthly_payment += float(loan.get('monthly_payment', 0))
        return monthly_payment * duration
    
    @staticmethod
    def calculate_monthly_payment(loan_amount, interest_rate, term):
        """Calculate monthly loan payment"""
        monthly_rate = interest_rate / 12 / 100
        if monthly_rate == 0:
            return loan_amount / term
        return loan_amount * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)

def calculate_metrics(self):
    """
    Calculate all metrics for the analysis with safe float handling.
    Returns a dictionary of calculated metrics.
    """
    # Basic property metrics
    purchase_price = self.get_metric('purchase_price')
    after_repair_value = self.get_metric('after_repair_value')
    renovation_costs = self.get_metric('renovation_costs')
    total_investment = purchase_price + renovation_costs

    # Income metrics
    monthly_rent = self.get_metric('monthly_rent')
    annual_rent = monthly_rent * 12

    # Get operating expenses
    operating_expenses = self.data.get('operating_expenses', {})
    total_monthly_expenses = sum(safe_float(v) for v in operating_expenses.values())
    total_annual_expenses = total_monthly_expenses * 12

    # Calculate cash flows
    monthly_cash_flow = self.get_metric('monthly_cash_flow')
    annual_cash_flow = monthly_cash_flow * 12

    # Investment metrics
    total_cash_invested = self.get_metric('total_cash_invested')
    
    # Calculate returns
    cash_on_cash_return = (annual_cash_flow / total_cash_invested * 100) if total_cash_invested > 0 else 0
    
    # BRRRR-specific calculations
    if self.data.get('analysis_type') in ['BRRRR', 'PadSplit BRRRR']:
        initial_loan_amount = self.get_metric('initial_loan_amount')
        initial_monthly_payment = self.get_metric('initial_monthly_payment')
        refinance_loan_amount = self.get_metric('refinance_loan_amount')
        refinance_monthly_payment = self.get_metric('refinance_monthly_payment')
        equity_captured = after_repair_value - total_investment
        cash_recouped = refinance_loan_amount - initial_loan_amount
        total_profit = equity_captured + annual_cash_flow
        roi = (total_profit / total_cash_invested * 100) if total_cash_invested > 0 else 0
        
        return {
            'purchase_price': purchase_price,
            'after_repair_value': after_repair_value,
            'renovation_costs': renovation_costs,
            'total_investment': total_investment,
            'monthly_rent': monthly_rent,
            'annual_rent': annual_rent,
            'total_monthly_expenses': total_monthly_expenses,
            'total_annual_expenses': total_annual_expenses,
            'monthly_cash_flow': monthly_cash_flow,
            'annual_cash_flow': annual_cash_flow,
            'total_cash_invested': total_cash_invested,
            'cash_on_cash_return': cash_on_cash_return,
            'initial_loan_amount': initial_loan_amount,
            'initial_monthly_payment': initial_monthly_payment,
            'refinance_loan_amount': refinance_loan_amount,
            'refinance_monthly_payment': refinance_monthly_payment,
            'equity_captured': equity_captured,
            'cash_recouped': cash_recouped,
            'total_profit': total_profit,
            'roi': roi
        }
    
    # PadSplit-specific calculations
    elif self.data.get('analysis_type') in ['PadSplit LTR']:
        padsplit_expenses = self.data.get('padsplit_expenses', {})
        total_padsplit_expenses = sum(safe_float(v) for v in padsplit_expenses.values())
        
        return {
            'purchase_price': purchase_price,
            'after_repair_value': after_repair_value,
            'renovation_costs': renovation_costs,
            'total_investment': total_investment,
            'monthly_rent': monthly_rent,
            'annual_rent': annual_rent,
            'total_monthly_expenses': total_monthly_expenses,
            'total_annual_expenses': total_annual_expenses,
            'total_padsplit_expenses': total_padsplit_expenses,
            'monthly_cash_flow': monthly_cash_flow,
            'annual_cash_flow': annual_cash_flow,
            'total_cash_invested': total_cash_invested,
            'cash_on_cash_return': cash_on_cash_return
        }
    
    # Long-term rental calculations (default)
    else:
        return {
            'purchase_price': purchase_price,
            'after_repair_value': after_repair_value,
            'renovation_costs': renovation_costs,
            'total_investment': total_investment,
            'monthly_rent': monthly_rent,
            'annual_rent': annual_rent,
            'total_monthly_expenses': total_monthly_expenses,
            'total_annual_expenses': total_annual_expenses,
            'monthly_cash_flow': monthly_cash_flow,
            'annual_cash_flow': annual_cash_flow,
            'total_cash_invested': total_cash_invested,
            'cash_on_cash_return': cash_on_cash_return,
            'operating_expense_ratio': (total_annual_expenses / annual_rent * 100) if annual_rent > 0 else 0,
            'debt_service_coverage_ratio': self.calculate_dscr()
        }

def calculate_dscr(self):
    """Calculate Debt Service Coverage Ratio."""
    try:
        annual_noi = self.get_metric('annual_cash_flow')
        
        # Get total annual debt service from all loans
        total_annual_debt_service = 0
        loans = self.data.get('loans', [])
        
        for loan in loans:
            monthly_payment = safe_float(loan.get('monthly_payment', 0))
            total_annual_debt_service += monthly_payment * 12
        
        if total_annual_debt_service > 0:
            return annual_noi / total_annual_debt_service
        return 0
        
    except Exception as e:
        logging.error(f"Error calculating DSCR: {str(e)}")
        return 0

def generate_lender_report(analysis_data, calculator, buffer):
    """Generate a PDF report for the analysis."""
    try:
        current_app.logger.info("Starting PDF generation")
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        # Create the story for the document
        story = []

        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Investment Analysis Report: {analysis_data.get('analysis_name', 'Untitled')}", title_style))

        # Add property information
        property_info = [
            ["Property Address", analysis_data.get('property_address', 'N/A')],
            ["Analysis Type", analysis_data.get('analysis_type', 'N/A')],
            ["Property Type", analysis_data.get('property_type', 'N/A')],
            ["Square Footage", analysis_data.get('home_square_footage', 'N/A')],
            ["Year Built", analysis_data.get('year_built', 'N/A')]
        ]
        story.append(Paragraph("Property Information", ParagraphStyle('Heading2')))
        story.append(create_table(property_info))
        story.append(Spacer(1, 0.25*inch))

        # Generate analysis-specific content
        if analysis_data.get('analysis_type') == 'BRRRR':
            story.extend(generate_brrrr_report(analysis_data, ParagraphStyle('Heading2')))
        else:
            # Handle other analysis types
            purchase_data = [
                ["Purchase Price", analysis_data.get('purchase_price', 'N/A')],
                ["After Repair Value", analysis_data.get('after_repair_value', 'N/A')],
                ["Total Investment", analysis_data.get('total_investment', 'N/A')]
            ]
            story.append(Paragraph("Purchase Details", ParagraphStyle('Heading2')))
            story.append(create_table(purchase_data))
            story.append(Spacer(1, 0.25*inch))

            income_data = [
                ["Monthly Rent", analysis_data.get('monthly_rent', 'N/A')],
                ["Monthly Cash Flow", analysis_data.get('monthly_cash_flow', 'N/A')],
                ["Annual Cash Flow", analysis_data.get('annual_cash_flow', 'N/A')]
            ]
            story.append(Paragraph("Income Details", ParagraphStyle('Heading2')))
            story.append(create_table(income_data))
            story.append(Spacer(1, 0.25*inch))

        # Build the document
        doc.build(story)
        current_app.logger.info("PDF generation completed successfully")
        return buffer

    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {str(e)}")
        current_app.logger.exception("Full traceback:")
        raise

def generate_brrrr_report(analysis_data, styles):
    """Generate BRRRR-specific report sections"""
    story = []
    
    # Purchase and Renovation
    purchase_data = [
        ["Purchase Price", analysis_data.get('purchase_price', 'N/A')],
        ["Renovation Costs", analysis_data.get('renovation_costs', 'N/A')],
        ["After Repair Value (ARV)", analysis_data.get('after_repair_value', 'N/A')],
        ["Total Initial Investment", analysis_data.get('total_initial_investment', 'N/A')]
    ]
    story.append(Paragraph("Purchase and Renovation", styles))
    story.append(create_table(purchase_data))
    story.append(Spacer(1, 0.25*inch))

    # Income and Operating Expenses
    income_expense_data = [
        ["Monthly Rent", analysis_data.get('monthly_rent', 'N/A')],
        ["Property Taxes", analysis_data.get('property_taxes', 'N/A')],
        ["Insurance", analysis_data.get('insurance', 'N/A')],
        ["CapEx", analysis_data.get('capex', 'N/A')],
        ["Maintenance", analysis_data.get('maintenance', 'N/A')],
        ["Vacancy", analysis_data.get('vacancy', 'N/A')],
        ["Property Management", analysis_data.get('management', 'N/A')],
        ["Total Monthly Expenses", analysis_data.get('total_monthly_expenses', 'N/A')],
        ["Monthly Cash Flow", analysis_data.get('monthly_cash_flow', 'N/A')],
        ["Annual Cash Flow", analysis_data.get('annual_cash_flow', 'N/A')]
    ]
    story.append(Paragraph("Income and Expenses", styles))
    story.append(create_table(income_expense_data))
    story.append(Spacer(1, 0.25*inch))

    # Financing Details
    financing_data = [
        ["Initial Loan Amount", analysis_data.get('initial_loan_amount', 'N/A')],
        ["Initial Monthly Payment", analysis_data.get('initial_monthly_payment', 'N/A')],
        ["Initial Interest Rate", analysis_data.get('initial_interest_rate', '0.00') + '%'],
        ["Initial Down Payment", analysis_data.get('initial_down_payment', 'N/A')],
        ["Initial Closing Costs", analysis_data.get('initial_closing_costs', 'N/A')],
        ["Refinance Loan Amount", analysis_data.get('refinance_loan_amount', 'N/A')],
        ["Refinance Monthly Payment", analysis_data.get('refinance_monthly_payment', 'N/A')],
        ["Refinance Interest Rate", analysis_data.get('refinance_interest_rate', '0.00') + '%'],
        ["Refinance Down Payment", analysis_data.get('refinance_down_payment', 'N/A')],
        ["Refinance Closing Costs", analysis_data.get('refinance_closing_costs', 'N/A')]
    ]
    story.append(Paragraph("Financing Details", styles))
    story.append(create_table(financing_data))
    story.append(Spacer(1, 0.25*inch))

    # Investment Returns
    returns_data = [
        ["Actual Cash Invested", analysis_data.get('actual_cash_invested', 'N/A')],
        ["Cash Recouped in Refinance", analysis_data.get('cash_recouped', 'N/A')],
        ["Equity Captured", analysis_data.get('equity_captured', 'N/A')],
        ["Cash on Cash Return", analysis_data.get('cash_on_cash_return', '0.00%')],
        ["Return on Investment (ROI)", analysis_data.get('roi', '0.00%')]
    ]
    story.append(Paragraph("Investment Returns", styles))
    story.append(create_table(returns_data))
    
    return story
