from datetime import datetime
from typing import Dict, Optional, Any, List, Union
import os
import logging
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.platypus import Frame, PageTemplate, FrameBreak
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_RIGHT, TA_LEFT, TA_CENTER

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates PDF reports with refined layout."""
    
    # Define brand colors
    BRAND_NAVY = HexColor('#1a3d5c')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='HeaderText',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.BRAND_NAVY,
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=self.BRAND_NAVY,
            spaceBefore=6,
            spaceAfter=3
        ))
        
    def _create_page_template(self, doc):
        """Create page template with header area and two columns."""
        # Header frame at top of page
        header_frame = Frame(
            doc.leftMargin,
            doc.height - 0.75*inch,  # Move header up slightly
            doc.width,
            1*inch,
            id='header',
            showBoundary=0
        )
        
        # Two columns below header
        left_column = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            (doc.width/2) - 6,  # Subtract 6 points for gutter
            doc.height - 1.5*inch,  # Leave room for header plus small gap
            id='left',
            showBoundary=0
        )
        
        right_column = Frame(
            doc.leftMargin + (doc.width/2) + 6,  # Add 6 points for gutter
            doc.bottomMargin,
            (doc.width/2) - 6,
            doc.height - 2*inch,  # Same height as left column
            id='right',
            showBoundary=0
        )
        
        return PageTemplate(
            id='TwoColumn',
            frames=[header_frame, left_column, right_column],
            onPage=self._add_page_number
        )
        
    def _add_page_number(self, canvas, doc):
        """Add page number to each page."""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(
            doc.pagesize[0] - 0.5*inch,
            0.25*inch,
            f"Page {doc.page}"
        )
        canvas.restoreState()
        
    def generate_report(self, data: Dict, report_type: str = 'analysis') -> BytesIO:
        """Generate a PDF report with continuous flow layout."""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Add page template
            doc.addPageTemplates([self._create_page_template(doc)])
            
            # Build story (content) for the PDF
            story = []
            
            # Add header with logo
            story.extend(self._create_header(data, doc))
            
            # Left column content
            story.extend(self._create_property_section(data))
            story.extend(self._create_loan_section(data))
            
            # Force column break
            story.append(FrameBreak())
            
            # Right column content
            story.extend(self._create_financial_section(data))
            story.extend(self._create_expenses_section(data))
            
            # Add BRRRR section if applicable
            if 'BRRRR' in data.get('analysis_type', ''):
                story.extend(self._create_brrrr_section(data))
            
            # Build the PDF
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def _create_header(self, data: Dict, doc: SimpleDocTemplate) -> list:
        """Create report header with analysis type and date."""
        elements = []
        
        # Create header text with analysis type and date
        header_text = data.get('analysis_name', '')
        subheader_text = (
            f"{data.get('analysis_type', 'Analysis')} | "
            f"Generated: {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        logo_path = os.path.join('static', 'images', 'logo-blue.png')
        if os.path.exists(logo_path):
            img = Image(logo_path, width=0.75*inch, height=0.75*inch)
            
            # Create header table
            header_elements = [
                [
                    Paragraph(header_text, self.styles['HeaderText']),
                    img
                ],
                [
                    Paragraph(subheader_text, self.styles['HeaderText']),
                    ''  # Empty cell under logo
                ]
            ]
            
            header_table = Table(
                header_elements,
                colWidths=[doc.width - 1*inch, 0.75*inch],
                style=TableStyle([
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('SPAN', (1, 0), (1, 1))  # Make logo span both rows
                ])
            )
            elements.append(header_table)
            elements.append(Spacer(1, 0.1*inch))  # Minimal gap after header
            
        return elements

    def _create_property_section(self, data: Dict) -> list:
        """Create compact property details section."""
        elements = []
        
        elements.append(Paragraph("Property Details", self.styles['SectionHeader']))
        
        # Create property details with minimal widths
        property_data = [
            ["Purchase Price:", f"${data.get('purchase_price', 0):,.2f}"],
            ["After Repair Value:", f"${data.get('after_repair_value', 0):,.2f}"],
            ["Renovation Costs:", f"${data.get('renovation_costs', 0):,.2f}"]
        ]
        
        table = Table(
            property_data,
            colWidths=[1.2*inch, 2.3*inch],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.BRAND_NAVY),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT')
            ])
        )
        
        elements.append(table)
        elements.append(Spacer(1, 6))
        
        return elements

    def _create_financial_section(self, data: Dict) -> list:
        """Create compact financial overview section."""
        elements = []
        
        elements.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
        
        metrics = data.get('calculated_metrics', {})
        financial_data = [
            ["Monthly Rent:", f"${data.get('monthly_rent', 0):,.2f}"],
            ["Monthly Cash Flow:", metrics.get('monthly_cash_flow', '$0.00')],
            ["Annual Cash Flow:", metrics.get('annual_cash_flow', '$0.00')],
            ["Cash on Cash Return:", metrics.get('cash_on_cash_return', '0%')],
            ["Total Cash Invested:", metrics.get('total_cash_invested', '$0.00')]
        ]
        
        if 'BRRRR' in data.get('analysis_type', ''):
            financial_data.extend([
                ["Equity Captured:", metrics.get('equity_captured', '$0.00')],
                ["Cash Recouped:", metrics.get('cash_recouped', '$0.00')]
            ])
        
        table = Table(
            financial_data,
            colWidths=[1.2*inch, 2.3*inch],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.BRAND_NAVY),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT')
            ])
        )
        
        elements.append(table)
        elements.append(Spacer(1, 6))
        
        return elements

    def _create_loan_section(self, data: Dict) -> list:
        """Create compact loan details section."""
        elements = []
        
        elements.append(Paragraph("Loan Details", self.styles['SectionHeader']))
        metrics = data.get('calculated_metrics', {})
        
        if 'BRRRR' in data.get('analysis_type', ''):
            # Initial Loan
            initial_loan_data = [
                ["Initial Loan", ""],
                ["Amount:", f"${data.get('initial_loan_amount', 0):,.2f}"],
                ["Interest Rate:", f"{data.get('initial_loan_interest_rate', 0)}%"],
                ["Term:", f"{data.get('initial_loan_term', 0)} months"],
                ["Payment:", metrics.get('initial_loan_payment', '$0.00')],
                ["Down Payment:", f"${data.get('initial_loan_down_payment', 0):,.2f}"],
                ["Closing Costs:", f"${data.get('initial_loan_closing_costs', 0):,.2f}"]
            ]
            
            table = Table(
                initial_loan_data,
                colWidths=[1.2*inch, 2.3*inch],
                style=TableStyle([
                    ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                    ('SPAN', (0, 0), (1, 0)),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_NAVY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_NAVY),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT')
                ])
            )
            elements.append(table)
            elements.append(Spacer(1, 6))
            
            # Refinance Loan
            refinance_loan_data = [
                ["Refinance Loan", ""],
                ["Amount:", f"${data.get('refinance_loan_amount', 0):,.2f}"],
                ["Interest Rate:", f"{data.get('refinance_loan_interest_rate', 0)}%"],
                ["Term:", f"{data.get('refinance_loan_term', 0)} months"],
                ["Payment:", metrics.get('refinance_loan_payment', '$0.00')],
                ["Down Payment:", f"${data.get('refinance_loan_down_payment', 0):,.2f}"],
                ["Closing Costs:", f"${data.get('refinance_loan_closing_costs', 0):,.2f}"]
            ]
            
            table = Table(
                refinance_loan_data,
                colWidths=[1.2*inch, 2.3*inch],
                style=TableStyle([
                    ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                    ('SPAN', (0, 0), (1, 0)),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_NAVY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_NAVY),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('PADDING', (0, 0), (-1, -1), 4),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT')
                ])
            )
            elements.append(table)
            
        else:
            # Regular loans
            for i in range(1, 4):
                prefix = f'loan{i}'
                amount = data.get(f'{prefix}_loan_amount', 0)
                if amount > 0:
                    loan_data = [
                        [f"Loan {i}", ""],
                        ["Amount:", f"${amount:,.2f}"],
                        ["Interest Rate:", f"{data.get(f'{prefix}_loan_interest_rate', 0)}%"],
                        ["Term:", f"{data.get(f'{prefix}_loan_term', 0)} months"],
                        ["Payment:", metrics.get(f'{prefix}_loan_payment', '$0.00')],
                        ["Down Payment:", f"${data.get(f'{prefix}_loan_down_payment', 0):,.2f}"],
                        ["Closing Costs:", f"${data.get(f'{prefix}_loan_closing_costs', 0):,.2f}"]
                    ]
                    
                    table = Table(
                        loan_data,
                        colWidths=[1.2*inch, 2.3*inch],
                        style=TableStyle([
                            ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
                            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                            ('SPAN', (0, 0), (1, 0)),
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                            ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_NAVY),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_NAVY),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('PADDING', (0, 0), (-1, -1), 4),
                            ('ALIGN', (1, 1), (1, -1), 'RIGHT')
                        ])
                    )
                    elements.append(table)
                    elements.append(Spacer(1, 6))
        
        return elements

    def _create_expenses_section(self, data: Dict) -> list:
        """Create compact operating expenses section."""
        elements = []
        
        elements.append(Paragraph("Operating Expenses", self.styles['SectionHeader']))
        
        # Fixed expenses
        expense_data = [
            ["Property Taxes:", f"${data.get('property_taxes', 0):,.2f}"],
            ["Insurance:", f"${data.get('insurance', 0):,.2f}"],
            ["HOA/COA/COOP:", f"${data.get('hoa_coa_coop', 0):,.2f}"],
            ["Management:", f"{data.get('management_fee_percentage', 0)}%"],
            ["CapEx:", f"{data.get('capex_percentage', 0)}%"],
            ["Vacancy:", f"{data.get('vacancy_percentage', 0)}%"],
            ["Repairs:", f"{data.get('repairs_percentage', 0)}%"]
        ]
        
        # Add PadSplit-specific expenses if applicable
        if 'PadSplit' in data.get('analysis_type', ''):
            expense_data.extend([
                ["Platform Fee:", f"{data.get('padsplit_platform_percentage', 0)}%"],
                ["Utilities:", f"${data.get('utilities', 0):,.2f}"],
                ["Internet:", f"${data.get('internet', 0):,.2f}"],
                ["Cleaning:", f"${data.get('cleaning', 0):,.2f}"],
                ["Pest Control:", f"${data.get('pest_control', 0):,.2f}"],
                ["Landscaping:", f"${data.get('landscaping', 0):,.2f}"]
            ])
        
        table = Table(
            expense_data,
            colWidths=[1.2*inch, 2.3*inch],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.BRAND_NAVY),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT')
            ])
        )
        
        elements.append(table)
        elements.append(Spacer(1, 6))
        
        return elements

    def _create_brrrr_section(self, data: Dict) -> list:
        """Create compact BRRRR strategy section."""
        elements = []
        metrics = data.get('calculated_metrics', {})
        
        elements.append(Paragraph("BRRRR Strategy Details", self.styles['SectionHeader']))
        
        brrrr_data = [
            ["Purchase Price:", f"${data.get('purchase_price', 0):,.2f}"],
            ["Renovation Costs:", f"${data.get('renovation_costs', 0):,.2f}"],
            ["After Repair Value:", f"${data.get('after_repair_value', 0):,.2f}"],
            ["Equity Captured:", metrics.get('equity_captured', '$0.00')],
            ["Cash Recouped:", metrics.get('cash_recouped', '$0.00')],
            ["Total Project Costs:", metrics.get('total_project_costs', '$0.00')]
        ]
        
        table = Table(
            brrrr_data,
            colWidths=[1.2*inch, 2.3*inch],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.BRAND_NAVY),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT')
            ])
        )
        
        elements.append(table)
        elements.append(Spacer(1, 6))
        
        return elements

    def _create_padsplit_section(self, data: Dict) -> list:
        """Create compact PadSplit section."""
        elements = []
        
        elements.append(Paragraph("PadSplit Details", self.styles['SectionHeader']))
        
        padsplit_data = [
            ["Platform Fee:", f"{data.get('padsplit_platform_percentage', 0)}%"],
            ["Utilities:", f"${data.get('utilities', 0):,.2f}"],
            ["Internet:", f"${data.get('internet', 0):,.2f}"],
            ["Cleaning:", f"${data.get('cleaning', 0):,.2f}"],
            ["Pest Control:", f"${data.get('pest_control', 0):,.2f}"],
            ["Landscaping:", f"${data.get('landscaping', 0):,.2f}"]
        ]
        
        table = Table(
            padsplit_data,
            colWidths=[1.2*inch, 2.3*inch],
            style=TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.BRAND_NAVY),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT')
            ])
        )
        
        elements.append(table)
        elements.append(Spacer(1, 6))
        
        return elements

    def _calculate_total_expenses(self, data: Dict) -> float:
        """Calculate total monthly operating expenses."""
        expenses = sum([
            float(data.get('property_taxes', 0)),
            float(data.get('insurance', 0)),
            float(data.get('hoa_coa_coop', 0))
        ])
        
        # Add percentage-based expenses
        monthly_rent = float(data.get('monthly_rent', 0))
        for field in ['management_fee_percentage', 'capex_percentage', 
                     'vacancy_percentage', 'repairs_percentage']:
            percentage = float(data.get(field, 0)) / 100
            expenses += monthly_rent * percentage
        
        # Add PadSplit-specific expenses
        if 'PadSplit' in data.get('analysis_type', ''):
            padsplit_expenses = sum([
                float(data.get('utilities', 0)),
                float(data.get('internet', 0)),
                float(data.get('cleaning', 0)),
                float(data.get('pest_control', 0)),
                float(data.get('landscaping', 0))
            ])
            padsplit_percentage = float(data.get('padsplit_platform_percentage', 0)) / 100
            expenses += padsplit_expenses + (monthly_rent * padsplit_percentage)
        
        return expenses

    def _calculate_total_loan_payments(self, data: Dict) -> float:
        """Calculate total monthly loan payments."""
        total_payment = 0.0
        
        # Calculate regular loan payments
        for i in range(1, 4):
            prefix = f'loan{i}_loan'
            if data.get(f'{prefix}_amount'):
                total_payment += self._calculate_loan_payment(
                    amount=float(data.get(f'{prefix}_amount', 0)),
                    rate=float(data.get(f'{prefix}_loan_interest_rate', 0)),
                    term=int(data.get(f'{prefix}_loan_term', 0))
                )
        
        # Add BRRRR-specific loans if applicable
        if 'BRRRR' in data.get('analysis_type', ''):
            # Initial loan
            if data.get('initial_loan_amount'):
                total_payment += self._calculate_loan_payment(
                    amount=float(data.get('initial_loan_amount', 0)),
                    rate=float(data.get('initial_loan_interest_rate', 0)),
                    term=int(data.get('initial_loan_term', 0)),
                    is_interest_only=True
                )
            
            # Refinance loan
            if data.get('refinance_loan_amount'):
                total_payment += self._calculate_loan_payment(
                    amount=float(data.get('refinance_loan_amount', 0)),
                    rate=float(data.get('refinance_loan_interest_rate', 0)),
                    term=int(data.get('refinance_loan_term', 0))
                )
        
        return total_payment

    def _calculate_loan_payment(self, amount: float, rate: float, 
                              term: int, is_interest_only: bool = False) -> float:
        """Calculate monthly loan payment."""
        if amount == 0 or term == 0:
            return 0.0
            
        if is_interest_only:
            return amount * (rate / 1200)
            
        monthly_rate = rate / 1200
        if monthly_rate == 0:
            return amount / term
            
        factor = (1 + monthly_rate) ** term
        return amount * monthly_rate * factor / (factor - 1)
    
# Create a singleton instance
_generator = ReportGenerator()

def generate_report(data: Dict, report_type: str = 'analysis') -> BytesIO:
    """Generate a PDF report from analysis data."""
    try:
        return _generator.generate_report(data, report_type)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise RuntimeError(f"Failed to generate report: {str(e)}")