from datetime import datetime
from typing import Dict, Optional, Any
import logging
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates PDF reports from analysis data using flat structure."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            spaceBefore=12,
            spaceAfter=6
        ))
        
    def generate_report(self, data: Dict) -> BytesIO:
        """Generate a PDF report from analysis data."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build story (content) for the PDF
        story = []
        
        # Add header
        story.extend(self._create_header(data))
        
        # Add property details
        story.extend(self._create_property_section(data))
        
        # Add financial overview
        story.extend(self._create_financial_section(data))
        
        # Add loan details
        story.extend(self._create_loan_section(data))
        
        # Add operating expenses
        story.extend(self._create_expenses_section(data))
        
        # Add type-specific details
        if 'BRRRR' in data.get('analysis_type', ''):
            story.extend(self._create_brrrr_section(data))
            
        if 'PadSplit' in data.get('analysis_type', ''):
            story.extend(self._create_padsplit_section(data))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _create_header(self, data: Dict) -> list:
        """Create report header section."""
        elements = []
        
        # Title
        title = Paragraph(
            f"{data.get('analysis_name', 'Analysis Report')}",
            self.styles['Title']
        )
        elements.append(title)
        
        # Subtitle with analysis type and date
        subtitle = Paragraph(
            f"Type: {data.get('analysis_type', 'Unknown')} | "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            self.styles['Italic']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 12))
        
        return elements

    def _create_property_section(self, data: Dict) -> list:
        """Create property details section."""
        elements = []
        
        elements.append(Paragraph("Property Details", self.styles['SectionHeader']))
        
        # Create property details table
        property_data = [
            ["Address:", data.get('property_address', 'N/A')],
            ["Square Footage:", str(data.get('square_footage', 'N/A'))],
            ["Lot Size:", str(data.get('lot_size', 'N/A'))],
            ["Year Built:", str(data.get('year_built', 'N/A'))],
            ["Purchase Price:", f"${data.get('purchase_price', 0):,.2f}"],
            ["After Repair Value:", f"${data.get('after_repair_value', 0):,.2f}"],
            ["Renovation Costs:", f"${data.get('renovation_costs', 0):,.2f}"]
        ]
        
        table = Table(property_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        return elements

    def _create_financial_section(self, data: Dict) -> list:
        """Create financial overview section."""
        elements = []
        
        elements.append(Paragraph("Financial Overview", self.styles['SectionHeader']))
        
        # Monthly income and expenses
        monthly_rent = float(data.get('monthly_rent', 0))
        total_expenses = self._calculate_total_expenses(data)
        loan_payments = self._calculate_total_loan_payments(data)
        monthly_cash_flow = monthly_rent - total_expenses - loan_payments
        
        financial_data = [
            ["Monthly Rent:", f"${monthly_rent:,.2f}"],
            ["Operating Expenses:", f"${total_expenses:,.2f}"],
            ["Loan Payments:", f"${loan_payments:,.2f}"],
            ["Monthly Cash Flow:", f"${monthly_cash_flow:,.2f}"],
            ["Annual Cash Flow:", f"${monthly_cash_flow * 12:,.2f}"]
        ]
        
        table = Table(financial_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 12))
        
        return elements

    def _create_loan_section(self, data: Dict) -> list:
        """Create loan details section."""
        elements = []
        
        elements.append(Paragraph("Loan Details", self.styles['SectionHeader']))
        
        # Handle regular loans
        for i in range(1, 4):
            prefix = f'loan{i}_loan'
            if data.get(f'{prefix}_amount'):
                loan_data = [
                    [f"Loan {i} Details"],
                    ["Amount:", f"${data.get(f'{prefix}_amount', 0):,.2f}"],
                    ["Interest Rate:", f"{data.get(f'{prefix}_loan_interest_rate', 0)}%"],
                    ["Term:", f"{data.get(f'{prefix}_loan_term', 0)} months"],
                    ["Down Payment:", f"${data.get(f'{prefix}_loan_down_payment', 0):,.2f}"],
                    ["Closing Costs:", f"${data.get(f'{prefix}_loan_closing_costs', 0):,.2f}"]
                ]
                
                table = Table(loan_data, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('SPAN', (0, 0), (-1, 0)),
                    ('PADDING', (0, 0), (-1, -1), 6)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 12))
        
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

def generate_report(data: Dict) -> BytesIO:
    """
    Generate a PDF report from analysis data.
    
    Args:
        data: Dictionary containing analysis data in flat structure
        
    Returns:
        BytesIO buffer containing the generated PDF
    """
    try:
        return _generator.generate_report(data)
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise RuntimeError(f"Failed to generate report: {str(e)}")