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
        """Create page template with header and two columns."""
        # Header frame at top of page
        header_frame = Frame(
            doc.leftMargin,
            doc.height - 0.75*inch,
            doc.width,
            1*inch,
            id='header',
            showBoundary=0
        )

        # Left column for property and loan details
        left_column = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            (doc.width/2) - 6,
            doc.height - 1.5*inch,
            id='left',
            showBoundary=0
        )

        # Right column for financial overview and operating expenses
        right_column = Frame(
            doc.leftMargin + (doc.width/2) + 6,
            doc.bottomMargin,
            (doc.width/2) - 6,
            doc.height - 1.5*inch,
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

            # Add header
            story.extend(self._create_header(data, doc))

            # Left column content
            story.extend(self._create_property_section(data))
            story.extend(self._create_loan_section(data))
            # Add notes section in left column
            story.extend(self._create_notes_section(data))

            # Force switch to right column
            story.append(FrameBreak())

            # Right column content
            story.extend(self._create_financial_section(data))
            story.extend(self._create_expenses_section(data))

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
            ["Renovation Costs:", f"${data.get('renovation_costs', 0):,.2f}"],
            ["Bedrooms:", str(data.get('bedrooms', 0))],
            ["Bathrooms:", f"{data.get('bathrooms', 0):.1f}"]
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
        """Create financial overview section for PDF report."""
        elements = []
        metrics = data.get('calculated_metrics', {})
        
        elements.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
        
        if 'BRRRR' in data.get('analysis_type', ''):
            # BRRRR logic remains unchanged
            purchase_data = [
                ["Purchase Overview", ""],
                ["Purchase Price:", f"${data.get('purchase_price', 0):,.2f}"],
                ["Renovation Costs:", f"${data.get('renovation_costs', 0):,.2f}"],
                ["After Repair Value:", f"${data.get('after_repair_value', 0):,.2f}"],
                ["Equity Captured:", metrics.get('equity_captured', '$0.00')],
                ["Cash Recouped:", metrics.get('cash_recouped', '$0.00')],
                ["Total Project Costs:", metrics.get('total_project_costs', '$0.00')]
            ]
            elements.append(self._create_metrics_table(purchase_data))
            elements.append(Spacer(1, 0.1*inch))
            
            # Rest of BRRRR logic...
            
        else:  # LTR Analysis
            has_balloon = data.get('has_balloon_payment') or (
                data.get('balloon_refinance_loan_amount', 0) > 0 and
                data.get('balloon_due_date') and
                data.get('balloon_refinance_ltv_percentage', 0) > 0
            )
            
            if has_balloon:
                # Pre-Balloon Overview
                pre_balloon_data = [
                    ["Pre-Balloon Financial Overview", ""],
                    ["Monthly Rent:", f"${data.get('monthly_rent', 0):,.2f}"],
                    ["Monthly Cash Flow:", metrics.get('pre_balloon_monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('pre_balloon_annual_cash_flow', '$0.00')],
                    ["Cash on Cash Return:", metrics.get('cash_on_cash_return', '0%')],
                    ["Total Cash Invested:", metrics.get('total_cash_invested', '$0.00')],
                    ["Balloon Due Date:", datetime.fromisoformat(data['balloon_due_date']).strftime('%Y-%m-%d')]
                ]
                elements.append(self._create_metrics_table(pre_balloon_data))
                elements.append(Spacer(1, 0.1*inch))
                
                # Pre-Balloon Operating Expenses
                pre_balloon_expenses = [
                    ["Pre-Balloon Operating Expenses", ""],
                    ["Property Taxes:", f"${data.get('property_taxes', 0):,.2f}"],
                    ["Insurance:", f"${data.get('insurance', 0):,.2f}"],
                    ["HOA/COA/COOP:", f"${data.get('hoa_coa_coop', 0):,.2f}"],
                    ["Management:", f"({data.get('management_fee_percentage', 0)}%) ${data.get('monthly_rent', 0) * data.get('management_fee_percentage', 0) / 100:,.2f}"],
                    ["CapEx:", f"({data.get('capex_percentage', 0)}%) ${data.get('monthly_rent', 0) * data.get('capex_percentage', 0) / 100:,.2f}"],
                    ["Vacancy:", f"({data.get('vacancy_percentage', 0)}%) ${data.get('monthly_rent', 0) * data.get('vacancy_percentage', 0) / 100:,.2f}"],
                    ["Repairs:", f"({data.get('repairs_percentage', 0)}%) ${data.get('monthly_rent', 0) * data.get('repairs_percentage', 0) / 100:,.2f}"]
                ]
                elements.append(self._create_metrics_table(pre_balloon_expenses))
                elements.append(Spacer(1, 0.1*inch))
                
                # Post-Balloon Overview
                post_balloon_data = [
                    ["Post-Balloon Financial Overview", ""],
                    ["Monthly Rent (with 2.5% annual increase):", metrics.get('post_balloon_monthly_rent', '$0.00')],
                    ["Monthly Cash Flow:", metrics.get('post_balloon_monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('post_balloon_annual_cash_flow', '$0.00')],
                    ["Post-Balloon Cash-on-Cash Return:", metrics.get('post_balloon_cash_on_cash_return', '0%')],
                    ["Refinance Amount:", f"${data.get('balloon_refinance_loan_amount', 0):,.2f}"],
                    ["Refinance LTV:", f"{data.get('balloon_refinance_ltv_percentage', 0)}%"],
                    ["Monthly Payment Change:", metrics.get('monthly_payment_difference', '$0.00')],
                    ["Refinance Costs:", metrics.get('balloon_refinance_costs', '$0.00')]
                ]
                elements.append(self._create_metrics_table(post_balloon_data))
                elements.append(Spacer(1, 0.1*inch))
                
                # Post-Balloon Operating Expenses
                post_balloon_expenses = [
                    ["Post-Balloon Operating Expenses", ""],
                    ["Property Taxes (with 2.5% annual increase):", metrics.get('post_balloon_property_taxes', '$0.00')],
                    ["Insurance (with 2.5% annual increase):", metrics.get('post_balloon_insurance', '$0.00')],
                    ["HOA/COA/COOP:", f"${data.get('hoa_coa_coop', 0):,.2f}"],
                    ["Management:", metrics.get('post_balloon_management_fee', '$0.00')],
                    ["CapEx:", metrics.get('post_balloon_capex', '$0.00')],
                    ["Vacancy:", metrics.get('post_balloon_vacancy', '$0.00')],
                    ["Repairs:", metrics.get('post_balloon_repairs', '$0.00')]
                ]
                elements.append(self._create_metrics_table(post_balloon_expenses))
                
            else:
                # Standard Overview for non-balloon loans
                financial_data = [
                    ["Financial Overview", ""],
                    ["Monthly Rent:", f"${data.get('monthly_rent', 0):,.2f}"],
                    ["Monthly Cash Flow:", metrics.get('monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('annual_cash_flow', '$0.00')],
                    ["Cash on Cash Return:", metrics.get('cash_on_cash_return', '0%')],
                    ["Total Cash Invested:", metrics.get('total_cash_invested', '$0.00')]
                ]
                elements.append(self._create_metrics_table(financial_data))
                
                # Regular Operating Expenses will be added by _create_expenses_section
        
        elements.append(Spacer(1, 6))
        return elements

    def _create_loan_section(self, data: Dict) -> list:
        """Create loan details section for PDF report."""
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
                ["Monthly Payment:", metrics.get('initial_loan_payment', '$0.00')],
                ["Down Payment:", f"${data.get('initial_loan_down_payment', 0):,.2f}"],
                ["Closing Costs:", f"${data.get('initial_loan_closing_costs', 0):,.2f}"]
            ]
            elements.append(self._create_metrics_table(initial_loan_data))
            elements.append(Spacer(1, 6))
            
            # Refinance Loan
            refinance_loan_data = [
                ["Refinance Loan", ""],
                ["Amount:", f"${data.get('refinance_loan_amount', 0):,.2f}"],
                ["Interest Rate:", f"{data.get('refinance_loan_interest_rate', 0)}%"],
                ["Term:", f"{data.get('refinance_loan_term', 0)} months"],
                ["Monthly Payment:", metrics.get('refinance_loan_payment', '$0.00')],
                ["Down Payment:", f"${data.get('refinance_loan_down_payment', 0):,.2f}"],
                ["Closing Costs:", f"${data.get('refinance_loan_closing_costs', 0):,.2f}"]
            ]
            elements.append(self._create_metrics_table(refinance_loan_data))
            
        else:  # Regular loans
            for i in range(1, 4):
                prefix = f'loan{i}'
                amount = data.get(f'{prefix}_loan_amount', 0)
                if amount > 0:
                    # Get the appropriate payment metric based on loan number
                    payment = metrics.get('pre_balloon_monthly_payment' if i == 1 else f'{prefix}_loan_payment', '$0.00')
                    
                    loan_data = [
                        [data.get(f'{prefix}_loan_name', '') or f"Loan {i}", ""],
                        ["Amount:", f"${amount:,.2f}"],
                        ["Interest Rate:", f"{data.get(f'{prefix}_loan_interest_rate', 0)}%"],
                        ["Term:", f"{data.get(f'{prefix}_loan_term', 0)} months"],
                        ["Monthly Payment:", payment],
                        ["Down Payment:", f"${data.get(f'{prefix}_loan_down_payment', 0):,.2f}"],
                        ["Closing Costs:", f"${data.get(f'{prefix}_loan_closing_costs', 0):,.2f}"]
                    ]
                    elements.append(self._create_metrics_table(loan_data))
                    elements.append(Spacer(1, 6))
        
        return elements
    
    def _create_notes_section(self, data: Dict) -> list:
        """Create notes section for the report."""
        elements = []
        
        if notes := data.get('notes'):
            elements.append(Spacer(1, 0.2*inch))  # Add some space before Notes section
            elements.append(Paragraph("Notes", self.styles['SectionHeader']))
            
            # Create a style for notes text with better formatting
            notes_style = ParagraphStyle(
                'NotesStyle',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=self.BRAND_NAVY,
                spaceAfter=12,
                leftIndent=12,
                rightIndent=12,
                firstLineIndent=0,
                leading=14  # Line height
            )
            
            # Add notes text, replacing newlines with <br/> tags
            formatted_notes = notes.replace('\n', '<br/>')
            elements.append(Paragraph(formatted_notes, notes_style))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements

    def _create_expenses_section(self, data: Dict) -> list:
        """Create operating expenses section for PDF report."""
        elements = []
        has_balloon = data.get('has_balloon_payment') or (
            data.get('balloon_refinance_loan_amount', 0) > 0 and
            data.get('balloon_due_date') and
            data.get('balloon_refinance_ltv_percentage', 0) > 0
        )
        
        # Only create the expenses section for non-balloon loans
        # (Balloon loan expenses are handled in _create_financial_section)
        if not has_balloon:
            elements.append(Paragraph("Operating Expenses", self.styles['SectionHeader']))
            
            # Calculate percentages for display
            monthly_rent = float(data.get('monthly_rent', 0))
            management_dollars = monthly_rent * (float(data.get('management_fee_percentage', 0)) / 100)
            capex_dollars = monthly_rent * (float(data.get('capex_percentage', 0)) / 100)
            vacancy_dollars = monthly_rent * (float(data.get('vacancy_percentage', 0)) / 100)
            repairs_dollars = monthly_rent * (float(data.get('repairs_percentage', 0)) / 100)
            
            # Fixed expenses
            expense_data = [
                ["Property Taxes:", f"${data.get('property_taxes', 0):,.2f}"],
                ["Insurance:", f"${data.get('insurance', 0):,.2f}"],
                ["HOA/COA/COOP:", f"${data.get('hoa_coa_coop', 0):,.2f}"],
                ["Management:", f"({data.get('management_fee_percentage', 0)}%) ${management_dollars:,.2f}"],
                ["CapEx:", f"({data.get('capex_percentage', 0)}%) ${capex_dollars:,.2f}"],
                ["Vacancy:", f"({data.get('vacancy_percentage', 0)}%) ${vacancy_dollars:,.2f}"],
                ["Repairs:", f"({data.get('repairs_percentage', 0)}%) ${repairs_dollars:,.2f}"]
            ]
            
            # Add PadSplit-specific expenses if applicable
            if 'PadSplit' in data.get('analysis_type', ''):
                platform_dollars = monthly_rent * (float(data.get('padsplit_platform_percentage', 0)) / 100)
                padsplit_data = [
                    ["Platform Fee:", f"({data.get('padsplit_platform_percentage', 0)}%) ${platform_dollars:,.2f}"],
                    ["Utilities:", f"${data.get('utilities', 0):,.2f}"],
                    ["Internet:", f"${data.get('internet', 0):,.2f}"],
                    ["Cleaning:", f"${data.get('cleaning', 0):,.2f}"],
                    ["Pest Control:", f"${data.get('pest_control', 0):,.2f}"],
                    ["Landscaping:", f"${data.get('landscaping', 0):,.2f}"]
                ]
                expense_data.extend(padsplit_data)
            
            elements.append(self._create_metrics_table(expense_data))
            elements.append(Spacer(1, 6))
        
        return elements

    def _create_metrics_table(self, data: List[List[str]]) -> Table:
        """Helper method to create consistently styled metrics tables."""
        return Table(
            data,
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
    
# Create a singleton instance
_generator = ReportGenerator()

def generate_report(data: Dict, report_type: str = 'analysis') -> BytesIO:
    """Generate a PDF report from analysis data."""
    try:
        return _generator.generate_report(data, report_type)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise RuntimeError(f"Failed to generate report: {str(e)}")