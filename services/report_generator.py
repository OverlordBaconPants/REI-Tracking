from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                               TableStyle, Image, BaseDocTemplate, PageTemplate, 
                               Frame, FrameBreak, PageBreak)
import os
from typing import Dict, List, Tuple, Union
from io import BytesIO
from flask import current_app
import logging

# Set up module-level logger
logger = logging.getLogger(__name__)

def safe_float(value: Union[str, float, int, None], default: float = 0.0) -> float:
    """Safely convert value to float, handling various formats."""
    try:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value.replace('$', '').replace(',', '').strip() or default)
        return default
    except (ValueError, TypeError):
        return default

class BasePropertyReport:
    """Base class for generating property analysis reports"""
    
    def __init__(self, analysis_data: Dict, buffer: BytesIO):
        self.data = analysis_data
        self.buffer = buffer
        self.styles = self._create_styles()

    @staticmethod    
    def format_currency(value: Union[str, float, int]) -> str:
        """Format currency values consistently as $X,XXX.XX"""
        try:
            if isinstance(value, str):
                value = float(value.replace('$', '').replace(',', ''))
            return f"${value:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
            
    @staticmethod
    def format_percentage(value: Union[str, float, int]) -> str:
        """Format percentage values consistently as XX.XX%"""
        try:
            if isinstance(value, str):
                value = float(value.replace('%', ''))
            return f"{value:.2f}%"
        except (ValueError, TypeError):
            return "0.00%"
        
    def _create_styles(self) -> Dict:
        """Create standardized styles for the report"""
        styles = getSampleStyleSheet()
        
        # Add custom styles based on CSS
        styles.add(ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000080'),  # Navy blue from CSS
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            'SubTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#000080'),  # Navy blue from CSS
            spaceAfter=10,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#000080'),
            spaceBefore=15,
            spaceAfter=10,
            alignment=TA_LEFT
        ))
        
        styles.add(ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_LEFT,
            backColor=colors.HexColor('#000080')
        ))
        
        return styles
        
    def _get_truncated_address(self, address_data) -> str:
        """Safely get truncated address from either string or list format."""
        try:
            if isinstance(address_data, list):
                return ', '.join(address_data[:2]).strip()
            elif isinstance(address_data, str):
                parts = address_data.split(',')
                return ', '.join(parts[:2]).strip()
            else:
                logger.warning(f"Unexpected address format: {type(address_data)}")
                return "Unknown Address"
        except Exception as e:
            logger.error(f"Error processing address: {str(e)}")
            return "Unknown Address"

    def _create_header(self, story: List) -> None:
        """Add report header with logo and title"""
        try:
            # Get the static folder path from Flask app and correct logo path
            static_folder = current_app.static_folder
            logo_path = os.path.join(static_folder, 'images', 'logo-blue.png')
            
            # Get truncated address and analysis type
            truncated_address = self._get_truncated_address(self.data.get('property_address', 'Unknown Address'))
            analysis_type = self.data.get('analysis_type', 'Property Analysis')
            
            if not os.path.exists(logo_path):
                logger.warning(f"Logo file not found at {logo_path}")
                header_table = Table([
                    [Paragraph("Property Analysis Report", self.styles['Header'])],
                    [Paragraph(truncated_address, self.styles['SubTitle'])],
                    [Paragraph(analysis_type, self.styles['SubTitle'])]
                ], colWidths=[7*inch], rowHeights=[18, 13, 13])  # Reduced row heights
            else:
                img = Image(logo_path, width=1.0*inch, height=1.0*inch)  # Slightly smaller logo
                header_table = Table([
                    [img, Paragraph("Property Analysis Report", self.styles['Header'])],
                    [None, Paragraph(truncated_address, self.styles['SubTitle'])],
                    [None, Paragraph(analysis_type, self.styles['SubTitle'])]
                ], colWidths=[1.5*inch, 5.5*inch], rowHeights=[18, 13, 13])  # Reduced row heights
            
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('SPAN', (0, 0), (0, -1)),  # Logo spans all rows
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            story.append(header_table)
            story.append(Spacer(1, 0.25*inch))  # Reduced spacing after header
            
        except Exception as e:
            logger.error(f"Error creating header: {str(e)}")
            story.append(Paragraph("Property Analysis Report", self.styles['Header']))
            story.append(Spacer(1, 0.25*inch))

    def _create_section(self, title: str, data: List[Tuple[str, str]], 
                       story: List, color_rows: bool = True) -> None:
        """Create a formatted section with title and data"""
        story.append(Paragraph(title, self.styles['SectionHeader']))
        
        # Calculate optimal column widths
        label_width = 2*inch
        value_width = 1.5*inch
        
        # Format table data
        table_data = [[Paragraph(str(key), self.styles['Normal']), 
                      Paragraph(str(value), self.styles['Normal'])] 
                     for key, value in data]
        
        t = Table(table_data, colWidths=[label_width, value_width])
        style = [
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]
        
        if color_rows:
            for i in range(len(table_data)):
                if i % 2 == 0:
                    style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
                    
        t.setStyle(TableStyle(style))
        story.append(t)
        story.append(Spacer(1, 0.2*inch))

    def generate(self) -> None:
        """Generate the complete report"""
        doc = BaseDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=1*inch,
            leftMargin=1*inch,
            topMargin=0.5*inch,  # Reduced top margin
            bottomMargin=1*inch
        )
        
        # Calculate frame dimensions
        content_width = doc.width
        
        # Create header frame (full width, reduced height)
        header_frame = Frame(
            doc.leftMargin,
            doc.height - 1*inch,  # Reduced space for header
            content_width,
            1.25*inch,  # Reduced header height
            id='header',
            showBoundary=0
        )
        
        # Calculate column widths with buffer
        col_width = (content_width - 1*inch) / 2  # 1 inch between columns
        
        # Create content frames (two columns)
        left_frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            col_width,
            doc.height - 2.25*inch,  # Adjusted for reduced header space
            id='left',
            showBoundary=0
        )
        
        right_frame = Frame(
            doc.leftMargin + col_width + 1*inch,
            doc.bottomMargin,
            col_width,
            doc.height - 2.25*inch,  # Adjusted for reduced header space
            id='right',
            showBoundary=0
        )
        
        def header_footer(canvas, doc):
            """Keep track of page numbers"""
            canvas.saveState()
            canvas.setFont('Helvetica', 9)
            page_num = canvas.getPageNumber()
            text = "Page %s" % page_num
            canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, doc.bottomMargin - 20, text)
            canvas.restoreState()
        
        # Create page template with all frames
        template = PageTemplate(
            id='ThreeFrames',
            frames=[header_frame, left_frame, right_frame],
            onPage=header_footer
        )
        doc.addPageTemplates([template])
        
        # Build the story
        story = []
        
        # Add header
        self._create_header(story)
        story.append(FrameBreak())
        
        # Create content and manage sections
        content_story = []
        self._add_content(content_story)
        
        # Group content into sections
        current_section = []
        for flowable in content_story:
            # Check specifically for FrameBreak since that's what we use to mark section breaks
            if flowable.__class__.__name__ == 'FrameBreak':
                # When we hit a break, add the accumulated section
                if current_section:
                    story.extend(current_section)
                    story.append(FrameBreak())
                    current_section = []
            else:
                current_section.append(flowable)

        # Add any remaining content
        if current_section:
            story.extend(current_section)
        
        # Build the document
        doc.build(story)
        
    def _add_content(self) -> None:
        """Each analysis type should override this method to add its specific content"""
        raise NotImplementedError("Each analysis type must implement _add_content")
    
class BRRRRReport(BasePropertyReport):
    """Report generator for BRRRR analyses"""
    
    def _add_content(self, story: List) -> None:
        # Key Performance Indicators
        kpi_data = [
            ("Purchase Price", self._format_currency(self.data.get('purchase_price', 0))),
            ("After Repair Value", self._format_currency(self.data.get('after_repair_value', 0))),
            ("Equity Captured", self._format_currency(self.data.get('equity_captured', 0))),
            ("Cash-on-Cash Return", self._format_percentage(self.data.get('cash_on_cash_return', 0))),
            ("Return on Investment", self._format_percentage(self.data.get('roi', 0))),
            ("Maximum Allowable Offer", self._format_currency(self.data.get('maximum_allowable_offer', 0)))
        ]
        self._create_section("Key Performance Indicators", kpi_data, story)

        # Monthly Income
        income_data = [
            ("Monthly Rent", self._format_currency(self.data.get('monthly_rent', 0))),
            ("Net Monthly Cash Flow", self._format_currency(self.data.get('monthly_cash_flow', 0))),
            ("Annual Cash Flow", self._format_currency(self.data.get('annual_cash_flow', 0)))
        ]
        self._create_section("Monthly Income", income_data, story)

        # Purchase and Renovation
        reno_data = [
            ("Purchase Price", self._format_currency(self.data.get('purchase_price', 0))),
            ("Renovation Costs", self._format_currency(self.data.get('renovation_costs', 0))),
            ("Renovation Duration", f"{self.data.get('renovation_duration', 0)} months"),
            ("Total Investment", self._format_currency(self.data.get('total_investment', 0)))
        ]
        self._create_section("Purchase and Renovation", reno_data, story)

        # Move to right column
        story.append(FrameBreak())

        # Operating Expenses
        operating_expenses = self.data.get('operating_expenses', {})
        expense_data = [
            (name, self._format_currency(amount)) 
            for name, amount in operating_expenses.items()
        ]
        expense_data.append(("Total Monthly Expenses", 
                           self._format_currency(self.data.get('total_monthly_expenses', 0))))
        self._create_section("Operating Expenses", expense_data, story)

        # Initial Financing
        initial_financing_data = [
            ("Initial Loan Amount", self._format_currency(self.data.get('initial_loan_amount', 0))),
            ("Initial Down Payment", self._format_currency(self.data.get('initial_down_payment', 0))),
            ("Initial Interest Rate", self._format_percentage(self.data.get('initial_interest_rate', 0))),
            ("Initial Loan Term", f"{self.data.get('initial_loan_term', 0)} months"),
            ("Initial Monthly Payment", self._format_currency(self.data.get('initial_monthly_payment', 0))),
            ("Initial Closing Costs", self._format_currency(self.data.get('initial_closing_costs', 0)))
        ]
        self._create_section("Initial Financing", initial_financing_data, story)

        # Refinance Details
        refinance_data = [
            ("Refinance Loan Amount", self._format_currency(self.data.get('refinance_loan_amount', 0))),
            ("Refinance Down Payment", self._format_currency(self.data.get('refinance_down_payment', 0))),
            ("Refinance Interest Rate", self._format_percentage(self.data.get('refinance_interest_rate', 0))),
            ("Refinance Loan Term", f"{self.data.get('refinance_loan_term', 0)} months"),
            ("Refinance Monthly Payment", self._format_currency(self.data.get('refinance_monthly_payment', 0))),
            ("Refinance Closing Costs", self._format_currency(self.data.get('refinance_closing_costs', 0))),
            ("Cash Recouped", self._format_currency(self.data.get('cash_recouped', 0)))
        ]
        self._create_section("Refinance Details", refinance_data, story)

class PadSplitLTRReport(BasePropertyReport):
    """Report generator for PadSplit LTR analyses"""
    
    def _add_content(self, story: List) -> None:
        # Key Performance Indicators
        kpi_data = [
            ("Purchase Price", self._format_currency(self.data.get('purchase_price', 0))),
            ("After Repair Value", self._format_currency(self.data.get('after_repair_value', 0))),
            ("Cash-on-Cash Return", self._format_percentage(self.data.get('cash_on_cash_return', 0))),
            ("Maximum Allowable Offer", self._format_currency(self.data.get('maximum_allowable_offer', 0))),
            ("Total Investment", self._format_currency(self.data.get('total_investment', 0))),
            ("Total Cash Invested", self._format_currency(self.data.get('total_cash_invested', 0)))
        ]
        self._create_section("Key Performance Indicators", kpi_data, story)

        # Monthly Income
        income_data = [
            ("Monthly Rent", self._format_currency(self.data.get('monthly_rent', 0))),
            ("Net Monthly Cash Flow", self._format_currency(self.data.get('monthly_cash_flow', 0))),
            ("Annual Cash Flow", self._format_currency(self.data.get('annual_cash_flow', 0)))
        ]
        self._create_section("Monthly Income", income_data, story)

        # Purchase Details
        purchase_data = [
            ("Purchase Price", self._format_currency(self.data.get('purchase_price', 0))),
            ("Cash to Seller", self._format_currency(self.data.get('cash_to_seller', 0))),
            ("Closing Costs", self._format_currency(self.data.get('closing_costs', 0))),
            ("Assignment Fee", self._format_currency(self.data.get('assignment_fee', 0))),
            ("Marketing Costs", self._format_currency(self.data.get('marketing_costs', 0))),
            ("Renovation Costs", self._format_currency(self.data.get('renovation_costs', 0))),
            ("Renovation Duration", f"{self.data.get('renovation_duration', 0)} months")
        ]
        self._create_section("Purchase Details", purchase_data, story)

        # Move to right column
        story.append(FrameBreak())

        # Operating Expenses
        operating_expenses = self.data.get('operating_expenses', {})
        expense_data = [
            (name, self._format_currency(amount)) 
            for name, amount in operating_expenses.items()
        ]
        expense_data.append(("Total Operating Expenses", 
                           self._format_currency(self.data.get('total_operating_expenses', 0))))
        self._create_section("Operating Expenses", expense_data, story)

        # PadSplit Specific Expenses
        padsplit_expenses = {
            "Platform Fee": self._format_currency(self.data.get('monthly_rent', 0) * 
                          float(self.data.get('padsplit_platform_percentage', 0)) / 100),
            "Utilities": self._format_currency(self.data.get('utilities', 0)),
            "Internet": self._format_currency(self.data.get('internet', 0)),
            "Cleaning Costs": self._format_currency(self.data.get('cleaning_costs', 0)),
            "Pest Control": self._format_currency(self.data.get('pest_control', 0)),
            "Landscaping": self._format_currency(self.data.get('landscaping', 0))
        }
        padsplit_expense_data = [
            (name, amount) for name, amount in padsplit_expenses.items()
        ]
        padsplit_expense_data.append(("Total PadSplit Expenses", 
                                    self._format_currency(self.data.get('total_padsplit_expenses', 0))))
        self._create_section("PadSplit Expenses", padsplit_expense_data, story)

        # Financing Details (if any loans exist)
        if self.data.get('loans'):
            loan_data = []
            for i, loan in enumerate(self.data['loans'], 1):
                loan_data.extend([
                    (f"Loan {i} - {loan.get('name', 'Unnamed')}", ""),
                    (f"Amount", self._format_currency(loan.get('amount', 0))),
                    (f"Down Payment", self._format_currency(loan.get('down_payment', 0))),
                    (f"Interest Rate", self._format_percentage(loan.get('interest_rate', 0))),
                    (f"Term", f"{loan.get('term', 0)} months"),
                    (f"Monthly Payment", self._format_currency(loan.get('monthly_payment', 0))),
                    (f"Closing Costs", self._format_currency(loan.get('closing_costs', 0)))
                ])
            self._create_section("Financing Details", loan_data, story)

class LenderReport(BasePropertyReport):
    """Report generator for lender analyses"""
    
    def _add_content(self, story: List) -> None:
        # Security Metrics
        security_metrics = self.data.get('security_metrics', {})
        security_data = [
            ("Loan to Value", self.format_percentage(security_metrics.get('loan_to_value', 0))),
            ("Loan to ARV", self.format_percentage(security_metrics.get('loan_to_arv', 0))),
            ("DSCR", f"{security_metrics.get('dscr', 0):.2f}"),
            ("Equity Cushion", self.format_currency(security_metrics.get('equity_cushion', 0))),
            ("Equity Percentage", self.format_percentage(security_metrics.get('equity_percentage', 0)))
        ]
        self._create_section("Security Metrics", security_data, story)

        # Exit Strategy Metrics
        exit_metrics = self.data.get('exit_metrics', {})
        refinance_potential = exit_metrics.get('refinance_potential', {})
        sale_potential = exit_metrics.get('sale_potential', {})
        rental_metrics = exit_metrics.get('rental_metrics', {})

        refinance_data = [
            ("Conventional 75% LTV", self.format_currency(refinance_potential.get('conventional_ltv_75', 0))),
            ("Conventional 80% LTV", self.format_currency(refinance_potential.get('conventional_ltv_80', 0))),
            ("Estimated Payment", self.format_currency(refinance_potential.get('estimated_payment', 0)))
        ]
        self._create_section("Refinance Potential", refinance_data, story)

        sale_data = [
            ("Profit at ARV", self.format_currency(sale_potential.get('profit_at_arv', 0))),
            ("Profit Margin", self.format_percentage(sale_potential.get('profit_margin', 0))),
            ("Estimated DOM", f"{sale_potential.get('estimated_dom', 0)} days")
        ]
        self._create_section("Sale Potential", sale_data, story)

        # Move to right column
        story.append(FrameBreak())

        rental_data = [
            ("Gross Rent Multiplier", f"{rental_metrics.get('gross_rent_multiplier', 0):.2f}"),
            ("Cap Rate", self.format_percentage(rental_metrics.get('cap_rate', 0)))
        ]
        self._create_section("Rental Metrics", rental_data, story)

        # Cost Breakdown
        cost_breakdown = self.data.get('cost_breakdown', {})
        acquisition_costs = cost_breakdown.get('acquisition_costs', {})
        renovation_costs = cost_breakdown.get('renovation_costs', {})
        holding_costs = cost_breakdown.get('holding_costs', {})

        acquisition_data = [
            ("Purchase Price", self.format_currency(acquisition_costs.get('purchase_price', 0))),
            ("Closing Costs", self.format_currency(acquisition_costs.get('closing_costs', 0))),
            ("Title Insurance", self.format_currency(acquisition_costs.get('title_insurance', 0))),
            ("Legal Fees", self.format_currency(acquisition_costs.get('legal_fees', 0)))
        ]
        self._create_section("Acquisition Costs", acquisition_data, story)

        renovation_data = [
            ("Total Budget", self.format_currency(renovation_costs.get('total_budget', 0))),
            ("Contingency", self.format_currency(renovation_costs.get('contingency', 0)))
        ]
        self._create_section("Renovation Costs", renovation_data, story)

        holding_data = [
            ("Property Taxes", self.format_currency(holding_costs.get('property_taxes', 0))),
            ("Insurance", self.format_currency(holding_costs.get('insurance', 0))),
            ("Utilities", self.format_currency(holding_costs.get('utilities', 0))),
            ("Loan Payments", self.format_currency(holding_costs.get('loan_payments', 0)))
        ]
        self._create_section("Holding Costs", holding_data, story)

def generate_lender_report(analysis_data: Dict, calculator: 'LenderMetricsCalculator', buffer: BytesIO) -> BytesIO:
    """Generate a PDF report for lender analysis."""
    try:
        # Calculate all metrics
        security_metrics = calculator.calculate_security_metrics()
        exit_metrics = calculator.calculate_exit_metrics()
        cost_breakdown = calculator.calculate_cost_breakdown()

        # Combine all data
        report_data = {
            'property_address': analysis_data.get('property_address', 'Unknown Address'),
            'analysis_type': analysis_data.get('analysis_type', 'Unknown'),
            'security_metrics': security_metrics,
            'exit_metrics': exit_metrics,
            'cost_breakdown': cost_breakdown
        }

        # Generate report
        report = LenderReport(report_data, buffer)
        report.generate()
        
        return buffer

    except Exception as e:
        logger.error(f"Error generating lender report: {str(e)}")
        raise

class MAOCalculator:
    """Calculate Maximum Allowable Offer based on investment strategy."""
    
    def __init__(self, analysis_data):
        self.data = analysis_data
        self.analysis_type = analysis_data.get('analysis_type')
        
    def clean_number(self, value, default=0.0):
        """Clean numeric values from currency strings."""
        if isinstance(value, str):
            return float(value.replace('$', '').replace(',', '').strip() or default)
        return float(value or default)
        
    def calculate_holding_costs(self, duration_months):
        """Calculate total holding costs during renovation."""
        monthly_costs = sum([
            self.clean_number(self.data.get('property_taxes', 0)),
            self.clean_number(self.data.get('insurance', 0)),
            self.clean_number(self.data.get('utilities', 0))
        ])
        
        # Calculate monthly loan payments during renovation
        if self.analysis_type == 'BRRRR':
            monthly_loan = self.clean_number(self.data.get('initial_monthly_payment', 0))
        else:
            monthly_loan = sum(
                self.clean_number(loan.get('monthly_payment', 0)) 
                for loan in self.data.get('loans', [])
            )
            
        total_monthly_costs = monthly_costs + monthly_loan
        return total_monthly_costs * duration_months
        
    def calculate_mao(self):
        """Calculate Maximum Allowable Offer based on strategy."""
        try:
            arv = self.clean_number(self.data.get('after_repair_value', 0))
            renovation_costs = self.clean_number(self.data.get('renovation_costs', 0))
            renovation_duration = int(self.clean_number(self.data.get('renovation_duration', 0)))
            holding_costs = self.calculate_holding_costs(renovation_duration)
            
            if self.analysis_type == 'BRRRR':
                return self.calculate_brrrr_mao(arv, renovation_costs, holding_costs)
            else:
                return self.calculate_ltr_mao(arv, renovation_costs, holding_costs)
                
        except Exception as e:
            logger.error(f"Error calculating MAO: {str(e)}")
            return 0
            
    def calculate_brrrr_mao(self, arv, renovation_costs, holding_costs):
        """Calculate MAO for BRRRR strategy."""
        # Get refinance parameters
        refinance_ltv = self.clean_number(self.data.get('refinance_ltv_percentage', 75)) / 100
        max_cash_left = self.clean_number(self.data.get('max_cash_left', 10000))
        refinance_closing_costs = self.clean_number(self.data.get('refinance_closing_costs', 0))
        purchase_closing_costs = self.clean_number(self.data.get('initial_closing_costs', 0))
        
        # Calculate maximum loan amount after refinance
        max_refinance_amount = arv * refinance_ltv
        
        # Working backwards:
        # max_refinance_amount = total_costs - max_cash_left
        # where total_costs = purchase_price + renovation_costs + holding_costs + closing_costs
        mao = (max_refinance_amount - max_cash_left - renovation_costs - 
               holding_costs - purchase_closing_costs - refinance_closing_costs)
               
        self.calculation_breakdown = {
            'arv': arv,
            'refinance_ltv': refinance_ltv,
            'max_refinance_amount': max_refinance_amount,
            'renovation_costs': renovation_costs,
            'holding_costs': holding_costs,
            'purchase_closing_costs': purchase_closing_costs,
            'refinance_closing_costs': refinance_closing_costs,
            'max_cash_left': max_cash_left
        }
        
        return max(0, mao)
        
    def calculate_ltr_mao(self, arv, renovation_costs, holding_costs):
        """Calculate MAO for Long-Term Rental strategy."""
        entry_fee_cap = self.clean_number(self.data.get('entry_fee_cap_percentage', 15)) / 100
        closing_costs = self.clean_number(self.data.get('closing_costs', 0))
        
        # Maximum allowable entry fee
        max_entry_fee = arv * entry_fee_cap
        
        # Entry fee includes down payment, closing costs, renovation costs, and holding costs
        # If using financing, account for down payment percentage
        down_payment_percentage = 0
        if self.data.get('loans'):
            loan = self.data['loans'][0]  # Consider primary loan
            loan_amount = self.clean_number(loan.get('amount', 0))
            down_payment = self.clean_number(loan.get('down_payment', 0))
            if loan_amount > 0:
                down_payment_percentage = down_payment / (loan_amount + down_payment)
        
        # Working backwards:
        # max_entry_fee = (purchase_price * down_payment_percentage) + closing_costs + renovation_costs + holding_costs
        if down_payment_percentage > 0:
            mao = (max_entry_fee - closing_costs - renovation_costs - holding_costs) / down_payment_percentage
        else:
            mao = max_entry_fee - closing_costs - renovation_costs - holding_costs
            
        self.calculation_breakdown = {
            'arv': arv,
            'entry_fee_cap': entry_fee_cap,
            'max_entry_fee': max_entry_fee,
            'down_payment_percentage': down_payment_percentage,
            'renovation_costs': renovation_costs,
            'holding_costs': holding_costs,
            'closing_costs': closing_costs
        }
        
        return max(0, mao)
        
    def get_calculation_breakdown(self):
        """Get formatted breakdown of MAO calculation."""
        if not hasattr(self, 'calculation_breakdown'):
            return "Calculation breakdown not available"
            
        if self.analysis_type == 'BRRRR':
            return (
                f"ARV: ${self.calculation_breakdown['arv']:,.2f}\n"
                f"Refinance LTV: {self.calculation_breakdown['refinance_ltv']*100:.1f}%\n"
                f"Max Refinance Amount: ${self.calculation_breakdown['max_refinance_amount']:,.2f}\n"
                f"Renovation Costs: ${self.calculation_breakdown['renovation_costs']:,.2f}\n"
                f"Holding Costs: ${self.calculation_breakdown['holding_costs']:,.2f}\n"
                f"Purchase Closing Costs: ${self.calculation_breakdown['purchase_closing_costs']:,.2f}\n"
                f"Refinance Closing Costs: ${self.calculation_breakdown['refinance_closing_costs']:,.2f}\n"
                f"Max Cash Left in Deal: ${self.calculation_breakdown['max_cash_left']:,.2f}"
            )
        else:
            return (
                f"ARV: ${self.calculation_breakdown['arv']:,.2f}\n"
                f"Entry Fee Cap: {self.calculation_breakdown['entry_fee_cap']*100:.1f}%\n"
                f"Max Entry Fee: ${self.calculation_breakdown['max_entry_fee']:,.2f}\n"
                f"Down Payment: {self.calculation_breakdown['down_payment_percentage']*100:.1f}%\n"
                f"Renovation Costs: ${self.calculation_breakdown['renovation_costs']:,.2f}\n"
                f"Holding Costs: ${self.calculation_breakdown['holding_costs']:,.2f}\n"
                f"Closing Costs: ${self.calculation_breakdown['closing_costs']:,.2f}"
            )
        
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