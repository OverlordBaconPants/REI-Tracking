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
        
    def _safe_number(self, value: Any, decimals: int = 1) -> float:
        """Safely convert a value to a number, returning 0 if conversion fails."""
        try:
            # Return 0 for None or empty values
            if value is None or value == '':
                return 0.0
                
            # Handle string values
            if isinstance(value, str):
                # Remove currency symbols and commas
                clean_value = value.replace('$', '').replace(',', '').replace('%', '').strip()
                if not clean_value:  # If empty after cleaning
                    return 0.0
                return round(float(clean_value), decimals)
                
            # Handle numeric values
            return round(float(value), decimals)
            
        except (TypeError, ValueError) as e:
            logger.warning(f"Failed to convert value to number: {value}, type: {type(value)}, error: {str(e)}")
            return 0.0

    def _check_balloon_payment(self, data: Dict) -> bool:
        """Safely check if balloon payment is enabled and valid."""
        logger.debug(f"Checking balloon payment with data: {data}")
        
        try:
            # First, check if balloon payment is explicitly disabled
            has_balloon = data.get('has_balloon_payment', False)
            if not has_balloon:
                logger.debug("Balloon payment explicitly disabled")
                return False
                
            # Check all required balloon fields have valid non-zero values
            loan_amount = self._safe_number(data.get('balloon_refinance_loan_amount', 0))
            logger.debug(f"Balloon loan amount: {loan_amount}")
            
            ltv_percentage = self._safe_number(data.get('balloon_refinance_ltv_percentage', 0))
            logger.debug(f"Balloon LTV percentage: {ltv_percentage}")
            
            due_date = data.get('balloon_due_date')
            logger.debug(f"Balloon due date: {due_date}")
            
            # Verify all required values are present and valid
            if not all([
                loan_amount > 0,
                ltv_percentage > 0,
                due_date and isinstance(due_date, str)
            ]):
                logger.debug("Missing or invalid balloon payment values")
                return False
                
            # Verify date format
            try:
                datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError) as e:
                logger.debug(f"Invalid balloon due date format: {e}")
                return False
                
            logger.debug("All balloon payment checks passed")
            return True
            
        except Exception as e:
            logger.error(f"Error checking balloon payment: {e}")
            return False
    
    def generate_report(self, data: Dict, report_type: str = 'analysis') -> BytesIO:
        """Generate a PDF report from analysis data with lease option support."""
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
            
            # Initialize story (content) for the PDF
            story = []
            
            # Add header
            story.extend(self._create_header(data, doc))
            
            if data.get('analysis_type') == 'Lease Option':
                # Left column content
                story.extend(self._create_property_section(data))
                story.extend(self._create_lease_option_details(data))
                story.extend(self._create_loan_section(data))
                story.extend(self._create_notes_section(data))
                
                # Force switch to right column
                story.append(FrameBreak())
                
                # Right column content - financial overview and expenses
                story.extend(self._create_financial_section(data))
                story.extend(self._create_expenses_section(data))
            else:
                # Standard report layout for other analysis types
                story.extend(self._create_property_section(data))
                story.extend(self._create_loan_section(data))
                story.extend(self._create_notes_section(data))
                story.append(FrameBreak())
                story.extend(self._create_financial_section(data))
                story.extend(self._create_expenses_section(data))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise RuntimeError(f"Failed to generate report: {str(e)}")

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
        """Create property details section with lease option support."""
        elements = []
        
        elements.append(Paragraph("Property Details", self.styles['SectionHeader']))
        
        if data.get('analysis_type') == 'Lease Option':
            property_data = [
                ["Purchase Price:", f"${self._safe_number(data.get('purchase_price'), 2):,.2f}"],
                ["Square Footage:", f"{data.get('square_footage', 0):,}"],
                ["Lot Size:", f"{data.get('lot_size', 0):,}"],
                ["Year Built:", str(data.get('year_built', 'N/A'))],
                ["Bedrooms:", str(data.get('bedrooms', 0))],
                ["Bathrooms:", f"{data.get('bathrooms', 0):.1f}"]
            ]
        else:
            # Standard property details
            property_data = [
                ["Purchase Price:", f"${self._safe_number(data.get('purchase_price'), 2):,.2f}"],
                ["After Repair Value:", f"${self._safe_number(data.get('after_repair_value'), 2):,.2f}"],
                ["Renovation Costs:", f"${self._safe_number(data.get('renovation_costs'), 2):,.2f}"],
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
        """Create financial overview section with support for all analysis types."""
        try:
            elements = []
            metrics = data.get('calculated_metrics', {})
            analysis_type = data.get('analysis_type')

            # Handle Lease Option analysis
            if analysis_type == 'Lease Option':
                elements.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
                
                # Calculate monthly rent credit
                monthly_rent = self._safe_number(data.get('monthly_rent', 0))
                credit_percentage = self._safe_number(data.get('monthly_rent_credit_percentage', 0))
                monthly_credit = (monthly_rent * credit_percentage) / 100
                
                financial_data = [
                    ["Financial Overview", ""],
                    ["Monthly Rent:", f"${self._safe_number(data.get('monthly_rent'), 2):,.2f}"],
                    ["Monthly Cash Flow:", metrics.get('monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('annual_cash_flow', '$0.00')],
                    ["Monthly Rent Credit:", f"${monthly_credit:,.2f}"],
                    ["Rent Credit Percentage:", f"{credit_percentage:.1f}%"],
                    ["Option Fee ROI (Annual):", metrics.get('option_roi', '0%')],
                    ["Cash on Cash Return:", metrics.get('cash_on_cash_return', '0%')],
                    ["Months to Break Even:", metrics.get('breakeven_months', 'N/A')]
                ]
                
                elements.append(self._create_metrics_table(financial_data))
                
            # Handle analyses with balloon payments
            elif self._check_balloon_payment(data):
                # Pre-Balloon Overview
                elements.append(Paragraph("Pre-Balloon Financial Overview", self.styles['SectionHeader']))
                pre_balloon_data = [
                    ["Pre-Balloon Financial Overview", ""],
                    ["Monthly Rent:", f"${self._safe_number(data.get('monthly_rent'), 2):,.2f}"],
                    ["Monthly Cash Flow:", metrics.get('pre_balloon_monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('pre_balloon_annual_cash_flow', '$0.00')],
                    ["Cash on Cash Return:", metrics.get('cash_on_cash_return', '0%')],
                    ["Balloon Due Date:", datetime.fromisoformat(data['balloon_due_date']).strftime('%Y-%m-%d')]
                ]
                elements.append(self._create_metrics_table(pre_balloon_data))
                elements.append(Spacer(1, 0.2*inch))

                # Post-Balloon Overview
                elements.append(Paragraph("Post-Balloon Financial Overview", self.styles['SectionHeader']))
                post_balloon_data = [
                    ["Post-Balloon Financial Overview", ""],
                    ["Monthly Rent:", metrics.get('post_balloon_monthly_rent', '$0.00')],
                    ["Monthly Cash Flow:", metrics.get('post_balloon_monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('post_balloon_annual_cash_flow', '$0.00')],
                    ["Cash-on-Cash Return:", metrics.get('post_balloon_cash_on_cash_return', '0%')],
                    ["Refinance Amount:", f"${self._safe_number(data.get('balloon_refinance_loan_amount'), 2):,.2f}"],
                    ["Refinance LTV:", f"{self._safe_number(data.get('balloon_refinance_ltv_percentage'))}%"],
                    ["Monthly Payment Change:", metrics.get('monthly_payment_difference', '$0.00')]
                ]
                elements.append(self._create_metrics_table(post_balloon_data))
                
            # Handle BRRRR analysis
            elif 'BRRRR' in analysis_type:
                elements.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
                financial_data = [
                    ["Financial Overview", ""],
                    ["Monthly Rent:", f"${self._safe_number(data.get('monthly_rent'), 2):,.2f}"],
                    ["Monthly Cash Flow:", metrics.get('monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('annual_cash_flow', '$0.00')],
                    ["Cash on Cash Return:", metrics.get('cash_on_cash_return', '0%')],
                    ["ROI:", metrics.get('roi', '0%')],
                    ["Equity Captured:", metrics.get('equity_captured', '$0.00')],
                    ["Cash Recouped:", metrics.get('cash_recouped', '$0.00')]
                ]
                elements.append(self._create_metrics_table(financial_data))
                
            # Handle standard LTR analysis
            else:
                elements.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
                financial_data = [
                    ["Financial Overview", ""],
                    ["Monthly Rent:", f"${self._safe_number(data.get('monthly_rent'), 2):,.2f}"],
                    ["Monthly Cash Flow:", metrics.get('monthly_cash_flow', '$0.00')],
                    ["Annual Cash Flow:", metrics.get('annual_cash_flow', '$0.00')],
                    ["Cash on Cash Return:", metrics.get('cash_on_cash_return', '0%')],
                    ["ROI:", metrics.get('roi', '0%')]
                ]
                elements.append(self._create_metrics_table(financial_data))

            # Add total investment details for all types except balloon payment
            if not self._check_balloon_payment(data):
                total_investment = self._safe_number(metrics.get('total_cash_invested', 0))
                if total_investment > 0:
                    investment_data = [
                        ["Investment Overview", ""],
                        ["Total Cash Invested:", f"${total_investment:,.2f}"]
                    ]
                    elements.append(Spacer(1, 0.2*inch))
                    elements.append(self._create_metrics_table(investment_data))

            return elements
            
        except Exception as e:
            logger.error(f"Error creating financial section: {str(e)}")
            logger.error(traceback.format_exc())
            return [Paragraph(f"Error creating financial section: {str(e)}", self.styles['Normal'])]

    def _create_loan_section(self, data: Dict) -> list:
        """Create loan details section with balloon payment support."""
        try:
            elements = []
            elements.append(Paragraph("Loan Details", self.styles['SectionHeader']))
            metrics = data.get('calculated_metrics', {})

            # Check for balloon payment
            has_balloon = bool(data.get('has_balloon_payment')) and all([
                self._safe_number(data.get('balloon_refinance_loan_amount')) > 0,
                data.get('balloon_due_date'),
                self._safe_number(data.get('balloon_refinance_ltv_percentage')) > 0
            ])

            if has_balloon:
                # Pre-Balloon Loan Details
                loan_data = [
                    ["Initial Loan (Pre-Balloon)", ""],
                    ["Amount:", f"${self._safe_number(data.get('loan1_loan_amount'), 2):,.2f}"],
                    ["Interest Rate:", f"{self._safe_number(data.get('loan1_loan_interest_rate'))}%"],
                    ["Term:", f"{data.get('loan1_loan_term', 0)} months"],
                    ["Monthly Payment:", metrics.get('pre_balloon_monthly_payment', '$0.00')],
                    ["Interest Only:", "Yes" if data.get('loan1_interest_only') else "No"],
                    ["Down Payment:", f"${self._safe_number(data.get('loan1_loan_down_payment'), 2):,.2f}"],
                    ["Closing Costs:", f"${self._safe_number(data.get('loan1_loan_closing_costs'), 2):,.2f}"]
                ]
                elements.append(self._create_metrics_table(loan_data))
                elements.append(Spacer(1, 0.2*inch))

                # Balloon Refinance Details
                refinance_data = [
                    ["Balloon Refinance Details", ""],
                    ["Refinance Amount:", f"${self._safe_number(data.get('balloon_refinance_loan_amount'), 2):,.2f}"],
                    ["Interest Rate:", f"{self._safe_number(data.get('balloon_refinance_loan_interest_rate'))}%"],
                    ["Term:", f"{data.get('balloon_refinance_loan_term', 0)} months"],
                    ["Monthly Payment:", metrics.get('post_balloon_monthly_payment', '$0.00')],
                    ["LTV Percentage:", f"{self._safe_number(data.get('balloon_refinance_ltv_percentage'))}%"],
                    ["Down Payment:", f"${self._safe_number(data.get('balloon_refinance_loan_down_payment'), 2):,.2f}"],
                    ["Closing Costs:", f"${self._safe_number(data.get('balloon_refinance_loan_closing_costs'), 2):,.2f}"]
                ]
                elements.append(self._create_metrics_table(refinance_data))

            else:
                # Regular loans
                for i in range(1, 4):
                    prefix = f'loan{i}'
                    amount = self._safe_number(data.get(f'{prefix}_loan_amount'))
                    if amount > 0:
                        loan_data = [
                            [data.get(f'{prefix}_loan_name', '') or f"Loan {i}", ""],
                            ["Amount:", f"${amount:,.2f}"],
                            ["Interest Rate:", f"{self._safe_number(data.get(f'{prefix}_loan_interest_rate'))}%"],
                            ["Term:", f"{data.get(f'{prefix}_loan_term', 0)} months"],
                            ["Monthly Payment:", metrics.get(f'{prefix}_loan_payment', '$0.00')],
                            ["Interest Only:", "Yes" if data.get(f'{prefix}_interest_only') else "No"],
                            ["Down Payment:", f"${self._safe_number(data.get(f'{prefix}_loan_down_payment'), 2):,.2f}"],
                            ["Closing Costs:", f"${self._safe_number(data.get(f'{prefix}_loan_closing_costs'), 2):,.2f}"]
                        ]
                        elements.append(self._create_metrics_table(loan_data))
                        elements.append(Spacer(1, 0.2*inch))

            return elements

        except Exception as e:
            logger.error(f"Error creating loan section: {str(e)}")
            return [Paragraph(f"Error creating loan section: {str(e)}", self.styles['Normal'])]

    def _create_lease_option_details(self, data: Dict) -> list:
        """Create lease option specific details section."""
        elements = []
        elements.append(Paragraph("Option Details", self.styles['SectionHeader']))
        
        # Format option details
        option_data = [
            ["Option Details", ""],
            ["Option Fee:", f"${self._safe_number(data.get('option_consideration_fee'), 2):,.2f}"],
            ["Option Term:", f"{data.get('option_term_months', 0)} months"],
            ["Strike Price:", f"${self._safe_number(data.get('strike_price'), 2):,.2f}"],
            ["Monthly Rent Credit:", f"{self._safe_number(data.get('monthly_rent_credit_percentage'))}%"],
            ["Rent Credit Cap:", f"${self._safe_number(data.get('rent_credit_cap'), 2):,.2f}"]
        ]
        
        # Calculate total potential credits
        monthly_rent = self._safe_number(data.get('monthly_rent', 0))
        monthly_credit_pct = self._safe_number(data.get('monthly_rent_credit_percentage', 0)) / 100
        term_months = int(data.get('option_term_months', 0))
        total_potential = monthly_rent * monthly_credit_pct * term_months
        credit_cap = self._safe_number(data.get('rent_credit_cap', 0))
        total_credits = min(total_potential, credit_cap)
        
        option_data.append(["Total Potential Credits:", f"${total_credits:,.2f}"])
        
        elements.append(self._create_metrics_table(option_data))
        elements.append(Spacer(1, 0.2*inch))
        
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
        """Create operating expenses section with safe value handling."""
        try:
            elements = []
            has_balloon = self._check_balloon_payment(data)
            
            if not has_balloon:
                elements.append(Paragraph("Operating Expenses", self.styles['SectionHeader']))
                monthly_rent = self._safe_number(data.get('monthly_rent'))
                
                # Basic expenses
                expense_data = [
                    ["Property Taxes:", f"${self._safe_number(data.get('property_taxes'), 2):,.2f}"],
                    ["Insurance:", f"${self._safe_number(data.get('insurance'), 2):,.2f}"],
                    ["HOA/COA/COOP:", f"${self._safe_number(data.get('hoa_coa_coop'), 2):,.2f}"]
                ]
                
                # Percentage-based expenses
                for field, label in {
                    'management_fee_percentage': 'Management',
                    'capex_percentage': 'CapEx',
                    'vacancy_percentage': 'Vacancy',
                    'repairs_percentage': 'Repairs'
                }.items():
                    percentage = self._safe_number(data.get(field))
                    amount = (monthly_rent * percentage) / 100
                    expense_data.append([
                        f"{label}:", 
                        f"({percentage:.1f}%) ${amount:,.2f}"
                    ])
                
                elements.append(self._create_metrics_table(expense_data))
                elements.append(Spacer(1, 6))
            
            return elements
            
        except Exception as e:
            logger.error(f"Error in _create_expenses_section: {str(e)}")
            return [Paragraph("Error generating expenses section", self.styles['Normal'])]

    def _create_metrics_table(self, data: List[List[str]], include_header: bool = True) -> Table:
        """Helper method to create consistently styled metrics tables."""
        try:
            # Make sure we have valid data
            if not data or not isinstance(data, list):
                logger.error("Invalid data for metrics table")
                return Table([["No data available"]], colWidths=[4*inch])
                
            # Create table style
            style = [
                ('GRID', (0, 1), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.BRAND_NAVY),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (1, 1), (1, -1), 'RIGHT')
            ]
            
            # Add header styling if included
            if include_header and len(data) > 0:
                style.extend([
                    ('SPAN', (0, 0), (1, 0)),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_NAVY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)
                ])
                
            return Table(
                data,
                colWidths=[1.2*inch, 2.3*inch],
                style=TableStyle(style)
            )
            
        except Exception as e:
            logger.error(f"Error creating metrics table: {e}")
            return Table([["Error creating table"]], colWidths=[4*inch])
    
def generate_report(data: Dict, report_type: str = 'analysis') -> BytesIO:
    """Generate a PDF report from analysis data."""
    try:
        generator = ReportGenerator()
        return generator.generate_report(data, report_type)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise RuntimeError(f"Failed to generate report: {str(e)}")