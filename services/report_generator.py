from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
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
from datetime import datetime

# Set up module-level logger
logger = logging.getLogger(__name__)

class BaseReport:
    """Base class for all report types with common functionality."""
    
    def __init__(self, data: Dict, buffer: BytesIO, landscape_mode: bool = False):
        self.data = data
        self.buffer = buffer
        self.landscape_mode = landscape_mode
        self.styles = self._create_styles()
        self.pagesize = landscape(letter) if landscape_mode else letter
        # Calculate margins based on orientation
        self.margins = {
            'left': 0.75*inch,
            'right': 0.75*inch,
            'top': 0.75*inch,
            'bottom': 0.75*inch
        }

    def _create_styles(self) -> Dict:
        """Create standardized styles for the report"""
        styles = getSampleStyleSheet()
        
        # Base styles for all reports
        styles.add(ParagraphStyle(
            'Header',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#000080'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            'SubTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#000080'),
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
        
    def format_currency(self, value: Union[str, float, int, None]) -> str:
        """Format currency values consistently"""
        try:
            if value is None:
                return "$0.00"
            if isinstance(value, str):
                value = float(value.replace('$', '').replace(',', ''))
            return f"${value:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"
            
    def format_percentage(self, value: Union[str, float, int, None]) -> str:
        """Format percentage values consistently"""
        try:
            if value is None:
                return "0.00%"
            if isinstance(value, str):
                value = float(value.replace('%', ''))
            return f"{value:.2f}%"
        except (ValueError, TypeError):
            return "0.00%"

    def _create_header(self) -> Table:
        """Create standard header with logo and title"""
        try:
            # Get logo path
            static_folder = current_app.static_folder
            logo_path = os.path.join(static_folder, 'images', 'logo-blue.png')

            title = self._get_report_title()
            date = datetime.now().strftime("%Y-%m-%d")

            if not os.path.exists(logo_path):
                logger.warning(f"Logo file not found at {logo_path}")
                header_table = Table([
                    [Paragraph(title, self.styles['Header'])],
                    [Paragraph(date, self.styles['SubTitle'])]
                ], colWidths=[10*inch])
            else:
                img = Image(logo_path, width=1.0*inch, height=1.0*inch)
                header_table = Table([
                    [img, Paragraph(title, self.styles['Header'])],
                    [None, Paragraph(date, self.styles['SubTitle'])]
                ], colWidths=[1.5*inch, 8.5*inch])

            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ('SPAN', (0, 0), (0, -1))
            ]))

            return header_table

        except Exception as e:
            logger.error(f"Error creating header: {str(e)}")
            return Paragraph("Report", self.styles['Header'])

    def _create_table(self, title: str, data: List[Tuple[str, Union[str, float, int]]], 
                     color_numbers: bool = True, column_widths: List[float] = None) -> Table:
        """Create consistently styled table with optional number coloring"""
        if column_widths is None:
            column_widths = [3*inch, 2*inch]

        # Create header row
        table_data = [[Paragraph(title, self.styles['TableHeader']), '']]
        
        # Add data rows
        for label, value in data:
            # Format and color code the value if needed
            if isinstance(value, (int, float)) or (isinstance(value, str) and 
                                                 any(c.isdigit() for c in value)):
                try:
                    # Clean and convert the value
                    if isinstance(value, str):
                        cleaned = value.replace('$', '').replace(',', '').replace('%', '')
                        num_value = float(cleaned)
                    else:
                        num_value = float(value)
                        
                    # Format based on presence of % symbol
                    if isinstance(value, str) and '%' in value:
                        formatted = self.format_percentage(num_value)
                    else:
                        formatted = self.format_currency(num_value)
                        
                    # Add color tags if requested
                    if color_numbers and num_value != 0:
                        color = 'green' if num_value > 0 else 'red'
                        value_cell = f'<font color="{color}">{formatted}</font>'
                    else:
                        value_cell = formatted
                except (ValueError, TypeError):
                    value_cell = str(value)
            else:
                value_cell = str(value)
                
            table_data.append([
                Paragraph(str(label), self.styles['Normal']),
                Paragraph(value_cell, self.styles['Normal'])
            ])
        
        # Create table with specified styling
        table = Table(table_data, colWidths=column_widths)
        
        style = [
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#000080')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]
        
        # Add alternating row colors
        for i in range(1, len(table_data), 2):
            style.append(('BACKGROUND', (0, i), (1, i), colors.lightgrey))
            
        table.setStyle(TableStyle(style))
        return table

    def _create_transaction_table(self, title: str, transactions: List[Dict]) -> Table:
        """Create a transaction table with consistent styling"""
        # Table headers
        headers = ['Date', 'Description', 'Income/Expense', 'Category', 'Amount']
        data = [headers]
        
        # Column widths for landscape mode
        col_widths = [1.5*inch, 4*inch, 1.5*inch, 2*inch, 1.5*inch]
        
        # Add transaction rows
        for t in transactions:
            amount = float(t['amount'].replace('$', '').replace(',', ''))
            if t['type'] == 'expense':
                amount = -amount
            
            data.append([
                t['date'],
                t['description'],
                t['type'].title(),
                t['category'],
                self.format_currency(amount)
            ])
        
        # Create and style table
        table = Table(data, colWidths=col_widths)
        
        style = [
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            
            # Body style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),  # Right-align amounts
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Center-align dates
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (1, 1), (1, -1), True),
        ]
        
        # Add row colors and amount colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgrey))
            
            # Color amounts
            amount = float(data[i][-1].replace('$', '').replace(',', ''))
            if amount < 0:
                style.append(('TEXTCOLOR', (-1, i), (-1, i), colors.red))
            else:
                style.append(('TEXTCOLOR', (-1, i), (-1, i), colors.green))
        
        table.setStyle(TableStyle(style))
        return table

    def _add_page_number(self, canvas, doc):
        """Add page number to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(self.pagesize[0] - 0.5*inch, 0.25*inch, text)
        canvas.restoreState()

    def _get_report_title(self) -> str:
        """Override this to provide specific report title"""
        raise NotImplementedError("Each report type must implement _get_report_title")

    def _add_content(self, story: List) -> None:
        """Override this to add report-specific content"""
        raise NotImplementedError("Each report type must implement _add_content")

    def generate(self) -> None:
        """Generate the report with consistent layout"""
        doc = BaseDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            rightMargin=self.margins['right'],
            leftMargin=self.margins['left'],
            topMargin=self.margins['top'],
            bottomMargin=self.margins['bottom']
        )
        
        # Calculate frame dimensions
        content_width = doc.width / 2 - 0.125*inch  # Half width minus half of quarter-inch gap
        header_height = 1.25*inch
        
        # Create frames
        header_frame = Frame(
            doc.leftMargin,
            doc.height - header_height,
            doc.width,
            header_height,
            id='header'
        )
        
        # Create two column frames
        left_frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            content_width,
            doc.height - header_height - 0.5*inch,
            id='left'
        )
        
        right_frame = Frame(
            doc.leftMargin + content_width + 0.25*inch,  # Add quarter-inch gap
            doc.bottomMargin,
            content_width,
            doc.height - header_height - 0.5*inch,
            id='right'
        )
        
        # Create template
        template = PageTemplate(
            id='normal',
            frames=[header_frame, left_frame, right_frame],
            onPage=self._add_page_number
        )
        doc.addPageTemplates([template])
        
        # Build story
        story = []
        self._add_content(story)
        
        # Build document
        doc.build(story)

class AnalysisReport(BaseReport):
    """Report generator for analysis reports"""

    def __init__(self, data: Dict, buffer: BytesIO):
        # Analysis reports in portrait mode with half-inch margins
        super().__init__(data, buffer, landscape_mode=False)
        self.margins = {
            'left': 0.5*inch,
            'right': 0.5*inch,
            'top': 0.5*inch,
            'bottom': 0.5*inch
        }

    def _create_header(self) -> Table:
        """Create header with logo and analysis details"""
        try:
            # Get logo path
            static_folder = current_app.static_folder
            logo_path = os.path.join(static_folder, 'images', 'logo-blue.png')
            
            # Prepare header text
            analysis_name = self.data.get('analysis_name', 'Untitled Analysis')
            analysis_type = self.data.get('analysis_type', 'Analysis')
            header_text = f"{analysis_name}<br/>{analysis_type}"

            if not os.path.exists(logo_path):
                logger.warning(f"Logo file not found at {logo_path}")
                return Paragraph(header_text, self.styles['Header'])

            # Create logo image with specified size
            logo = Image(logo_path, width=0.75*inch, height=0.75*inch)
            
            # Create header table
            header_table = Table([
                [logo, Paragraph(header_text, self.styles['Header'])]
            ], colWidths=[1*inch, 6.5*inch])  # Adjusted for half-inch margins on letter paper

            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),     # Logo alignment
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),     # Text alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # Vertical center alignment
                ('LEFTPADDING', (1, 0), (1, 0), 12),   # Space between logo and text
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            return header_table

        except Exception as e:
            logger.error(f"Error creating header: {str(e)}")
            return Paragraph("Report", self.styles['Header'])

    def _create_loan_details_table_ltr(self, loans: List[Dict], col_widths: List[float] = None) -> List:
        """Create tables for LTR loan details with headers."""
        if not col_widths:
            col_widths = [1.75*inch, 1.25*inch]
        
        tables = []
        for loan in loans:
            # Create loan data
            loan_data = [
                ("Amount", loan.get('amount')),
                ("Interest Rate", loan.get('interest_rate')),
                ("Term", f"{loan.get('term_months', 0)} months"),
                ("Down Payment", loan.get('down_payment')),
                ("Closing Costs", loan.get('closing_costs'))
            ]
            
            # Create table with loan name as header
            loan_table = self._create_table(loan.get('name', 'Unnamed Loan'), loan_data, column_widths=col_widths)
            tables.append(loan_table)
            tables.append(Spacer(1, 0.25*inch))
            
        return tables

    def _add_content(self, story: List) -> None:
        """Add report content based on analysis type."""
        # Add header and common elements to left column
        story.append(self._create_header())
        story.append(Spacer(1, 0.25*inch))
        story.append(FrameBreak())  # Move to left column

        col_widths = [1.75*inch, 1.25*inch]

        # Purchase Details and Income & Returns in left column
        purchase_data = [
            ("Purchase Price", self.data.get('purchase_price')),
            ("After Repair Value", self.data.get('after_repair_value')),
            ("Renovation Costs", self.data.get('renovation_costs')),
            ("Renovation Duration", f"{self.data.get('renovation_duration', 0)} months")
        ]
        story.append(self._create_table("Purchase Details", purchase_data, column_widths=col_widths))
        story.append(Spacer(1, 0.25*inch))

        returns_data = [
            ("Monthly Rent", self.data.get('monthly_rent')),
            ("Monthly Cash Flow", self.data.get('monthly_cash_flow')),
            ("Annual Cash Flow", self.data.get('annual_cash_flow')),
            ("Cash on Cash Return", self.data.get('cash_on_cash_return'))
        ]
        story.append(self._create_table("Income & Returns", returns_data, column_widths=col_widths))

        # Move to right column for loan details
        story.append(FrameBreak())

        analysis_type = self.data.get('analysis_type', '')

        if 'BRRRR' in analysis_type:
            # Initial Loan Details
            initial_loan_data = [
                ("Initial Loan Amount", self.data.get('initial_loan_amount')),
                ("Interest Rate", self.data.get('initial_interest_rate')),
                ("Monthly Payment", self.data.get('initial_monthly_payment')),
                ("Loan Term", f"{self.data.get('initial_loan_term', 0)} months"),
                ("Down Payment", self.data.get('initial_down_payment')),
                ("Closing Costs", self.data.get('initial_closing_costs'))
            ]
            story.append(self._create_table("Initial Loan Details", initial_loan_data, column_widths=col_widths))
            story.append(Spacer(1, 0.25*inch))

            # Refinance Details
            refinance_data = [
                ("Refinance Loan Amount", self.data.get('refinance_loan_amount')),
                ("Interest Rate", self.data.get('refinance_interest_rate')),
                ("Monthly Payment", self.data.get('refinance_monthly_payment')),
                ("Loan Term", f"{self.data.get('refinance_loan_term', 0)} months"),
                ("Down Payment", self.data.get('refinance_down_payment')),
                ("Closing Costs", self.data.get('refinance_closing_costs'))
            ]
            story.append(self._create_table("Refinance Details", refinance_data, column_widths=col_widths))

            # Investment Summary below loan details
            story.append(Spacer(1, 0.25*inch))
            investment_data = [
                ("Total Project Costs", self.data.get('total_project_costs')),
                ("Total Cash Invested", self.data.get('total_cash_invested')),
                ("Cash Recouped", self.data.get('cash_recouped')),
                ("Equity Captured", self.data.get('equity_captured'))
            ]
            story.append(self._create_table("Investment Summary", investment_data, column_widths=col_widths))

        elif 'LTR' in analysis_type and self.data.get('loans'):
            # Add individual loan tables
            loan_tables = self._create_loan_details_table_ltr(self.data['loans'], col_widths)
            story.extend(loan_tables)

    def _create_table(self, title: str, data: List[Tuple[str, str]], column_widths: List[float]) -> Table:
        """Create a formatted table with consistent styling"""
        # Create table with data
        table_data = [[Paragraph(title, self.styles['TableHeader']), '']]
        
        for label, value in data:
            if isinstance(value, (int, float)) or (isinstance(value, str) and 
                                                 any(c.isdigit() for c in value)):
                try:
                    if isinstance(value, str):
                        cleaned = value.replace('$', '').replace(',', '').replace('%', '')
                        num_value = float(cleaned)
                    else:
                        num_value = float(value)
                        
                    if isinstance(value, str) and '%' in value:
                        formatted = self.format_percentage(num_value)
                    else:
                        formatted = self.format_currency(num_value)
                    
                    if num_value != 0:
                        color = 'green' if num_value > 0 else 'red'
                        value_cell = f'<font color="{color}">{formatted}</font>'
                    else:
                        value_cell = formatted
                except (ValueError, TypeError):
                    value_cell = str(value)
            else:
                value_cell = str(value)
                
            table_data.append([
                Paragraph(str(label), self.styles['Normal']),
                Paragraph(value_cell, self.styles['Normal'])
            ])
        
        # Create and style table
        table = Table(table_data, colWidths=column_widths)
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('SPAN', (0, 0), (-1, 0)),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        return table

class TransactionReport(BaseReport):
    """Report generator for transaction reports"""
    
    def __init__(self, data: Dict, buffer: BytesIO):
        # Set landscape_mode=True for transaction reports
        super().__init__(data, buffer, landscape_mode=True)
        self.margins = {
            'left': 1*inch,
            'right': 1*inch,
            'top': 0.75*inch,
            'bottom': 0.75*inch
        }
        self.transactions_by_property = self._group_transactions()
    
    def _get_report_title(self) -> str:
        """Get report title based on number of properties"""
        if len(self.transactions_by_property) == 1:
            property_name = next(iter(self.transactions_by_property.keys()))
            return f"Transactions for {', '.join(property_name.split(',')[:2])}"
        return "Portfolio Transactions"

    def _create_header(self) -> Table:
        """Create header with logo and report title"""
        try:
            static_folder = current_app.static_folder
            logo_path = os.path.join(static_folder, 'images', 'logo-blue.png')
            
            # Get title and date range
            title = self._get_report_title()
            date_str = datetime.now().strftime("%Y-%m-%d")
            date_range = ""
            if 'start_date' in self.data and 'end_date' in self.data:
                date_range = f"\n{self.data['start_date']} to {self.data['end_date']}"
            else:
                date_range = f"\nAll Transactions as of {date_str}"

            if not os.path.exists(logo_path):
                logger.warning(f"Logo file not found at {logo_path}")
                header_table = Table([
                    [Paragraph(title + date_range, self.styles['Header'])]
                ], colWidths=[10*inch])
            else:
                img = Image(logo_path, width=1.0*inch, height=1.0*inch)
                header_table = Table([
                    [img, Paragraph(title + date_range, self.styles['Header'])]
                ], colWidths=[1.5*inch, 8.5*inch])

            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0)
            ]))

            return header_table

        except Exception as e:
            logger.error(f"Error creating header: {str(e)}")
            return Paragraph(self._get_report_title(), self.styles['Header'])
            
    def _add_content(self, story: List) -> None:
        """Add report content in the exact format from the samples"""
        # Add header
        story.append(self._create_header())
        story.append(Spacer(1, 0.25*inch))

        # Add grand total summary for multiple properties
        if len(self.transactions_by_property) > 1:
            grand_total = self._calculate_grand_total()
            summary_data = [
                ("Total Income", grand_total['total_income']),
                ("Total Expenses", grand_total['total_expenses']),
                ("Net Income", grand_total['net_income'])
            ]
            story.append(self._create_table(
                "Grand Total Summary",
                summary_data,
                column_widths=[3*inch, 2*inch]
            ))
            story.append(Spacer(1, 0.2*inch))

        # Process each property
        for property_id, transactions in self.transactions_by_property.items():
            # Property header with in-line truncation
            story.append(Paragraph(f"Property: {', '.join(property_id.split(',')[:2])}", self.styles['SectionHeader']))
            
            # Property summary
            summary = self._calculate_property_summary(transactions)
            summary_data = [
                ("Total Income", summary['total_income']),
                ("Total Expenses", summary['total_expenses']),
                ("Net Income", summary['net_income'])
            ]
            story.append(self._create_table(
                "Property Summary",
                summary_data,
                column_widths=[3*inch, 2*inch]
            ))
            story.append(Spacer(1, 0.2*inch))

            # Sort transactions by date (newest first)
            transactions.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

            # Create transaction table
            story.append(self._create_transaction_table("Transactions", transactions))

            # Add page break between properties (except last)
            if property_id != list(self.transactions_by_property.keys())[-1]:
                story.append(PageBreak())

    def _calculate_property_summary(self, transactions: List[Dict]) -> Dict:
        """Calculate summary totals for a property"""
        total_income = sum(
            float(t['amount'].replace('$', '').replace(',', ''))
            for t in transactions if t['type'].lower() == 'income'
        )
        total_expenses = sum(
            float(t['amount'].replace('$', '').replace(',', ''))
            for t in transactions if t['type'].lower() == 'expense'
        )
        return {
            'total_income': total_income,
            'total_expenses': -total_expenses,  # Make expenses negative
            'net_income': total_income - total_expenses
        }

    def _calculate_grand_total(self) -> Dict:
        """Calculate totals across all properties"""
        total_income = 0
        total_expenses = 0
        
        for transactions in self.transactions_by_property.values():
            summary = self._calculate_property_summary(transactions)
            total_income += summary['total_income']
            total_expenses += summary['total_expenses']
            
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': total_income + total_expenses  # Expenses are already negative
        }

    def _group_transactions(self) -> Dict[str, List[Dict]]:
        """Group transactions by property"""
        grouped = {}
        for transaction in self.data.get('transactions', []):
            property_id = transaction.get('property_id', 'Unknown Property')
            if property_id not in grouped:
                grouped[property_id] = []
            grouped[property_id].append(transaction)
        return grouped

    def generate(self) -> None:
        """Override generate method to use SimpleDocTemplate for transaction reports"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            rightMargin=self.margins['right'],
            leftMargin=self.margins['left'],
            topMargin=self.margins['top'],
            bottomMargin=self.margins['bottom']
        )
        
        story = []
        self._add_content(story)
        doc.build(story, onFirstPage=self._add_page_number, onLaterPages=self._add_page_number)
    
def generate_report(data: Dict, report_type: str = 'analysis') -> BytesIO:
    """Generate appropriate PDF report based on type"""
    buffer = BytesIO()
    
    if report_type == 'transaction':
        # Extract date range from the view data if present
        transactions_data = {
            'transactions': data,
            'start_date': data[0].get('date_filter_start') if data else None,
            'end_date': data[0].get('date_filter_end') if data else None
        }
        report = TransactionReport(transactions_data, buffer)
    else:  # Default to analysis report
        report = AnalysisReport(data, buffer)
        
    report.generate()
    buffer.seek(0)
    return buffer