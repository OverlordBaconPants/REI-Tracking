from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
                              Image, PageBreak, KeepTogether)
from reportlab.platypus.flowables import Flowable
from datetime import datetime
import logging
import os
import traceback

class RoundedTableFlowable(Flowable):
    """Wraps a table in a flowable with rounded corners."""
    
    def __init__(self, table, corner_radius=8, padding=2):
        Flowable.__init__(self)
        self.table = table
        self.corner_radius = corner_radius
        self.padding = padding
        self.width, self.height = table.wrap(0, 0)
        self.width += padding * 2
        self.height += padding * 2
    
    def draw(self):
        # Save canvas state
        self.canv.saveState()
        
        # Set colors
        bg_color = BRAND_CONFIG['colors']['background']
        border_color = BRAND_CONFIG['colors']['border']
        
        # Draw rounded rectangle background
        self.canv.setFillColor(bg_color)
        self.canv.setStrokeColor(border_color)
        self.canv.setLineWidth(0.5)
        self.canv.roundRect(0, 0, self.width, self.height, self.corner_radius, fill=1, stroke=1)
        
        # Draw the table with offset to account for padding
        self.canv.translate(self.padding, self.padding)
        self.table.canv = self.canv
        self.table.draw()
        
        # Restore canvas state
        self.canv.restoreState()
    
    def wrap(self, availWidth, availHeight):
        # Account for padding in the dimensions while ensuring we don't exceed page dimensions
        available_content_width = availWidth - self.padding * 2
        available_content_height = availHeight - self.padding * 2
        
        # Wrap the table to the available content area
        width, height = self.table.wrap(available_content_width, available_content_height)
        
        # Ensure we don't exceed the available space
        if width > available_content_width:
            width = available_content_width
        if height > available_content_height:
            height = available_content_height
            
        self.width = width + self.padding * 2
        self.height = height + self.padding * 2
        return self.width, self.height

# Brand configuration matching report_generator.py
BRAND_CONFIG = {
    'colors': {
        'primary': '#0047AB',       # Navy blue primary color
        'secondary': '#0056b3',     # Slightly lighter blue for accents
        'tertiary': '#4285F4',      # Light blue for highlights
        'text_dark': '#333333',     # Dark text
        'text_light': '#666666',    # Light text
        'background': '#FFFFFF',    # White background
        'success': '#51A351',       # Green for positive indicators
        'warning': '#F89406',       # Orange for warnings
        'danger': '#BD362F',        # Red for negative indicators
        'neutral': '#F5F7FA',       # Lighter gray for backgrounds
        'border': '#E0E5EB',        # Border color
        'table_row_alt': '#F0F3F7', # Alternating table row background color
        'table_header': '#E8ECEF',  # Table header background color
        'border_light': '#E0E5EB'   # Light border color for tables
    },
    'fonts': {
        'primary': 'Helvetica-Bold',  # Built-in ReportLab font for headings
        'secondary': 'Helvetica',     # Built-in ReportLab font for body text
    },
    'logo_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo-blue.png')
}

class TransactionReportGenerator:
    """Handles generation of transaction-specific PDF reports with enhanced styling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.styles = self._create_styles()

    def _create_styles(self):
        """Create paragraph and table styles."""
        styles = getSampleStyleSheet()
        colors = BRAND_CONFIG['colors']
        
        # Add custom styles
        styles.add(ParagraphStyle(
            name='BrandNormal',
            parent=styles['Normal'],
            fontName=BRAND_CONFIG['fonts']['secondary'],
            fontSize=8,
            textColor=colors['text_dark'],
            spaceAfter=4,
            wordWrap='CJK'
        ))

        styles.add(ParagraphStyle(
            name='BrandHeading1',
            parent=styles['Heading1'],
            fontName=BRAND_CONFIG['fonts']['primary'],
            fontSize=16,
            textColor=colors['primary'],
            spaceAfter=12,
            alignment=0,  # Left aligned
            wordWrap='CJK'
        ))
        
        styles.add(ParagraphStyle(
            name='BrandHeading3',
            parent=styles['Heading3'],
            fontName=BRAND_CONFIG['fonts']['primary'],
            fontSize=10,
            textColor=colors['primary'],
            spaceBefore=6,
            spaceAfter=4,
            alignment=0,  # Left aligned
            wordWrap='CJK'
        ))
        
        styles.add(ParagraphStyle(
            name='BrandSmall',
            parent=styles['Normal'],
            fontName=BRAND_CONFIG['fonts']['secondary'],
            fontSize=7,
            textColor=colors['text_light'],
            spaceAfter=4,
            wordWrap='CJK'
        ))
        
        styles.add(ParagraphStyle(
            name='TableHeader',
            parent=styles['Normal'],
            fontName=BRAND_CONFIG['fonts']['primary'],
            fontSize=9,
            textColor=colors['background'],
            alignment=1,  # Center aligned
            wordWrap='CJK'
        ))
        
        styles.add(ParagraphStyle(
            name='EnhancedTitle',
            parent=styles['Heading1'],
            fontName=BRAND_CONFIG['fonts']['primary'],
            fontSize=16,
            leading=20,
            textColor=colors['primary'],
            alignment=0,  # Left aligned
            spaceBefore=0,
            spaceAfter=2
        ))
        
        styles.add(ParagraphStyle(
            name='EnhancedSubtitle',
            parent=styles['Normal'],
            fontName=BRAND_CONFIG['fonts']['secondary'],
            fontSize=9,
            leading=11,
            textColor=colors['text_light'],
            alignment=0,  # Left aligned
            spaceBefore=0,
            spaceAfter=0
        ))
        
        styles.add(ParagraphStyle(
            name='TableContent',
            parent=styles['BrandNormal'],
            fontSize=8,
            leading=10,
            wordWrap='CJK'
        ))
        
        styles.add(ParagraphStyle(
            name='TableCell',
            parent=styles['TableContent'],
            alignment=0  # Left aligned
        ))
        
        styles.add(ParagraphStyle(
            name='TableCellRight',
            parent=styles['TableContent'],
            alignment=2  # Right aligned
        ))
        
        styles.add(ParagraphStyle(
            name='MetadataEntry',
            parent=styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_light'],
            spaceAfter=1
        ))
        
        return styles

    def _add_page_decorations(self, canvas, doc):
        """Add page number, footer line, and logo (first page only)."""
        canvas.saveState()
        colors = BRAND_CONFIG['colors']
        
        # Draw the footer with page number
        canvas.setFont(BRAND_CONFIG['fonts']['primary'], 8)
        canvas.setFillColor(colors['text_light'])
        canvas.drawRightString(
            doc.pagesize[0] - 0.5*inch,
            0.25*inch,
            f"Page {doc.page}"
        )
        
        # Add a thin footer line
        canvas.setStrokeColor(colors['primary'])
        canvas.setLineWidth(0.5)
        canvas.line(
            doc.leftMargin, 
            0.45*inch, 
            doc.pagesize[0] - doc.rightMargin, 
            0.45*inch
        )
        
        # Draw actual logo only on first page
        if doc.page == 1:
            logo_path = BRAND_CONFIG['logo_path']
            logo_height = 0.75*inch
            
            try:
                if os.path.exists(logo_path):
                    # Use actual logo from file with transparent background
                    canvas.drawImage(
                        logo_path,
                        doc.pagesize[0] - doc.rightMargin - 1.5*inch,
                        doc.pagesize[1] - doc.topMargin - logo_height,
                        width=1.5*inch,
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # This makes white background transparent
                    )
                else:
                    self.logger.warning(f"Logo file not found at {logo_path}")
            except Exception as e:
                self.logger.error(f"Error adding logo: {str(e)}")
        
        canvas.restoreState()

    def _truncate_address(self, address):
        """Truncate address to show only house number, street, and city"""
        if not address or address == 'All Properties':
            return address
        parts = address.split(',')
        return ', '.join(parts[:2]).strip() if len(parts) >= 2 else parts[0].strip()

    def generate(self, transactions, buffer, metadata=None):
        """Generate a PDF report of transactions"""
        try:
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            story = self._build_story(transactions, metadata)
            doc.build(story, onFirstPage=self._add_page_decorations, onLaterPages=self._add_page_decorations)
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating PDF report: {str(e)}")
            self.logger.error(f"Stack trace: {traceback.format_exc()}")
            raise

    def _build_story(self, transactions, metadata):
        """Build the content (story) for the PDF"""
        story = []

        # Create header with title
        header_elements = self._create_header(metadata)
        story.extend(header_elements)
        
        story.append(Spacer(1, 0.2*inch))
        
        # Add summary section
        if metadata:
            property_id = metadata.get('property')
            if property_id and property_id != 'All Properties':
                story.extend(self._create_property_summary(transactions))
            else:
                story.extend(self._create_grand_summary(transactions))
                # Add page break after the grand summary table
                story.append(PageBreak())
        
        # Add transactions section
        property_id = metadata.get('property') if metadata else None
        
        if property_id and property_id != 'All Properties':
            # Sort transactions by date in descending order
            sorted_transactions = sorted(
                transactions,
                key=lambda x: x.get('date', ''),
                reverse=True
            )
            
            # Single property report - just add transactions table
            story.extend(self._create_transactions_table(sorted_transactions))
        else:
            # All properties report
            # Group transactions by property
            sorted_transactions = sorted(
                transactions,
                key=lambda x: (x.get('property_id', ''), x.get('date', '')),
                reverse=True
            )
            
            grouped_transactions = {}
            for t in sorted_transactions:
                property_id = t.get('property_id', '')
                if not property_id:
                    continue
                
                if property_id not in grouped_transactions:
                    grouped_transactions[property_id] = []
                
                grouped_transactions[property_id].append(t)
            
            # Create a section for each property
            first_property = True
            for property_id, property_transactions in grouped_transactions.items():
                # Add page break before each property (except the first one)
                if not first_property:
                    story.append(PageBreak())
                else:
                    first_property = False
                    
                # Create property section
                property_section = []
                
                # Add property header
                truncated_address = self._truncate_address(property_id)
                property_section.append(Paragraph(truncated_address, self.styles['BrandHeading3']))
                property_section.append(Spacer(1, 0.05*inch))
                
                # Add property transaction summary
                property_section.extend(self._create_property_summary(property_transactions))
                property_section.append(Spacer(1, 0.1*inch))
                
                # Add property transactions
                property_section.extend(self._create_transactions_table(property_transactions))
                
                # Add the entire property section to the story
                story.extend(property_section)

        return story

    def _create_header(self, metadata):
        """Create report header with title, date and metadata."""
        elements = []
        
        # Title
        title = "Transaction Report"
        elements.append(Paragraph(title, self.styles['EnhancedTitle']))
        
        # Subtitle with date
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Add property info if available
        subtitle = current_date
        if metadata and metadata.get('property'):
            property_name = self._truncate_address(metadata['property'])
            if property_name != 'All Properties':
                subtitle = f"{property_name} | {current_date}"
            else:
                subtitle = f"All Properties | {current_date}"
                
        elements.append(Paragraph(subtitle, self.styles['EnhancedSubtitle']))
        
        # Add metadata as small text if available
        if metadata:
            elements.append(Spacer(1, 0.1*inch))
            
            metadata_text = []
            if metadata.get('user'):
                metadata_text.append(Paragraph(f"Generated by: {metadata['user']}", 
                                           self.styles['MetadataEntry']))
            if metadata.get('date_range'):
                metadata_text.append(Paragraph(f"Date Range: {metadata['date_range']}", 
                                           self.styles['MetadataEntry']))
            
            for entry in metadata_text:
                elements.append(entry)
        
        return elements

    def _create_grand_summary(self, transactions):
        """Create the grand summary table for all properties"""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Property Summary", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Group transactions by property
        property_summaries = {}
        
        for t in transactions:
            property_id = t.get('property_id')
            if not property_id:
                continue
                
            if property_id not in property_summaries:
                property_summaries[property_id] = {'income': 0, 'expense': 0}
            
            amount = self._parse_amount(t['amount'])
            if t.get('type', '').lower() == 'income':
                property_summaries[property_id]['income'] += amount
            else:
                property_summaries[property_id]['expense'] += amount

        # Create table data with styled cells
        header_style = ParagraphStyle(
            name='SummaryHeader',
            parent=self.styles['TableHeader'],
            fontSize=8,
            textColor=colors['background'],
            alignment=1  # Center aligned
        )
        
        label_style = ParagraphStyle(
            name='SummaryLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='SummaryValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            alignment=2  # Right aligned
        )
        
        table_data = [
            [
                Paragraph("Property", header_style),
                Paragraph("Total Income", header_style),
                Paragraph("Total Expenses", header_style),
                Paragraph("Net Amount", header_style)
            ]
        ]
        
        total_income = 0
        total_expenses = 0
        
        # Sort properties by name
        sorted_properties = sorted(property_summaries.items(), key=lambda x: x[0])
        
        for property_id, summary in sorted_properties:
            truncated_address = self._truncate_address(property_id)
            net = summary['income'] - summary['expense']
            
            row = [
                Paragraph(truncated_address, label_style),
                Paragraph(f"${summary['income']:,.2f}", value_style),
                Paragraph(f"${summary['expense']:,.2f}", value_style),
                Paragraph(f"${net:,.2f}", value_style)
            ]
            
            table_data.append(row)
            total_income += summary['income']
            total_expenses += summary['expense']
        
        # Add totals row
        net_total = total_income - total_expenses
        total_row = [
            Paragraph("TOTAL", label_style),
            Paragraph(f"${total_income:,.2f}", value_style),
            Paragraph(f"${total_expenses:,.2f}", value_style),
            Paragraph(f"${net_total:,.2f}", value_style)
        ]
        table_data.append(total_row)

        # Calculate column widths
        table_width = 7.0*inch
        col_widths = [3.0*inch, 1.33*inch, 1.33*inch, 1.34*inch]
        
        # Create alternating row colors
        row_styles = []
        for i in range(1, len(table_data)-1):  # Skip header and total rows
            if i % 2 == 1:  # Alternate rows
                row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
        
        # Create and style the table
        summary_table = Table(
            table_data,
            colWidths=col_widths,
            style=TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors['primary']),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid and borders
                ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors['border']),  # Thicker line above total
                
                # Totals row styling
                ('BACKGROUND', (0, -1), (-1, -1), colors['neutral']),
                ('FONTNAME', (0, -1), (-1, -1), BRAND_CONFIG['fonts']['primary']),
                
                # Cell padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ] + row_styles)
        )
        
        # Apply table border 
        summary_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors['border']),
        ]))
        
        # For large property sets, use normal table without rounded corners
        if len(sorted_properties) < 15:  # Only use rounded corners for smaller tables
            # Wrap the table in a RoundedTableFlowable
            rounded_summary_table = RoundedTableFlowable(summary_table, corner_radius=8, padding=2)
            elements.append(rounded_summary_table)
        else:
            # Use standard table for large datasets to avoid overflow errors
            elements.append(summary_table)
            
        # Add a spacer after the summary table for better separation
        elements.append(Spacer(1, 0.1*inch))
        
        return elements

    def _create_property_summary(self, transactions):
        """Create financial summary for a specific property."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Financial Summary", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Calculate totals
        total_income = sum(self._parse_amount(t['amount']) 
                         for t in transactions if t.get('type', '').lower() == 'income')
        total_expenses = sum(self._parse_amount(t['amount']) 
                           for t in transactions if t.get('type', '').lower() == 'expense')
        net_amount = total_income - total_expenses
        
        # Define styles for table cells
        label_style = ParagraphStyle(
            name='FinancialLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='FinancialValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        net_style = ParagraphStyle(
            name='NetAmount',
            parent=value_style,
            fontName=BRAND_CONFIG['fonts']['primary'],
            textColor=colors['primary'] if net_amount >= 0 else colors['danger']
        )
        
        # Create summary data
        summary_data = [
            [Paragraph("Total Income:", label_style),
             Paragraph(f"${total_income:,.2f}", value_style)],
            [Paragraph("Total Expenses:", label_style),
             Paragraph(f"${total_expenses:,.2f}", value_style)],
            [Paragraph("Net Amount:", label_style),
             Paragraph(f"${net_amount:,.2f}", net_style)]
        ]
        
        # Calculate optimal column widths
        col1_width = 1.4*inch
        col2_width = 1.4*inch
        
        # Create and style the table
        summary_table = Table(
            summary_data,
            colWidths=[col1_width, col2_width],
            style=TableStyle([
                # Label styling - left column
                ('BACKGROUND', (0, 0), (0, -1), colors['table_header']),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                
                # Value styling - right column
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                
                # Grid and borders
                ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors['border']),  # Thicker line above net
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Net row styling
                ('BACKGROUND', (0, -1), (-1, -1), colors['neutral']),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ])
        )
        
        # Apply table border
        summary_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors['border']),
        ]))
        
        # Wrap small tables in RoundedTableFlowable
        rounded_summary_table = RoundedTableFlowable(summary_table, corner_radius=8, padding=2)
        elements.append(rounded_summary_table)
        
        # Add a spacer after the summary table for better separation
        elements.append(Spacer(1, 0.1*inch))
        
        return elements

    def _create_transactions_table(self, transactions):
        """Create the transactions table with enhanced styling."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Force more space before the section header to prevent overlap with preceding content
        elements.append(Spacer(1, 0.3*inch))  # Increased from 0.15 to 0.3
        
        # Use a larger, more prominent header that's less likely to be occluded
        header = Paragraph("<b>Transaction Details</b>", self.styles['BrandHeading3'])
        elements.append(header)
        elements.append(Spacer(1, 0.15*inch))  # Increased from 0.1 to 0.15
        
        # Define column headers
        columns = [
            'Date',
            'Type',
            'Category',
            'Description',
            'Amount',
            'Payer/<br/>Collector',
            'Status',
            'Notes'
        ]
        
        # Create header style
        header_style = ParagraphStyle(
            name='TransactionHeader',
            parent=self.styles['TableHeader'],
            fontSize=8,
            textColor=colors['background'],
            alignment=1  # Center aligned
        )
        
        # Create cell styles
        cell_style = ParagraphStyle(
            name='TransactionCell',
            parent=self.styles['TableCell'],
            fontSize=7,
            leading=9
        )
        
        amount_income_style = ParagraphStyle(
            name='AmountIncome',
            parent=cell_style,
            textColor=colors['success'],
            alignment=2  # Right aligned
        )
        
        amount_expense_style = ParagraphStyle(
            name='AmountExpense',
            parent=cell_style,
            textColor=colors['danger'],
            alignment=2  # Right aligned
        )
        
        # Build table data with styled headers
        table_data = [
            [Paragraph(col, header_style) for col in columns]
        ]
        
        # Add data rows with styled cells
        for t in transactions:
            amount_value = t.get('amount', '0')
            amount = self._parse_amount(amount_value)
            amount_str = f"${amount:,.2f}"
            
            is_income = t.get('type', '').lower() == 'income'
            amount_style = amount_income_style if is_income else amount_expense_style
            
            row = [
                Paragraph(t.get('date', ''), cell_style),
                Paragraph(t.get('type', ''), cell_style),
                Paragraph(t.get('category', ''), cell_style),
                Paragraph(t.get('description', ''), cell_style),
                Paragraph(amount_str, amount_style),
                Paragraph(t.get('collector_payer', ''), cell_style),
                Paragraph(t.get('reimbursement', {}).get('reimbursement_status', ''), cell_style),
                Paragraph(t.get('notes', ''), cell_style)
            ]
            
            table_data.append(row)
        
        # Calculate column widths (total: 7 inches)
        col_widths = [
            0.7*inch,   # Date
            0.6*inch,   # Type
            0.8*inch,   # Category
            1.2*inch,   # Description (reduced from 1.3)
            0.7*inch,   # Amount
            0.7*inch,   # Collector/Payer (reduced from 0.8)
            0.6*inch,   # Status
            1.2*inch    # Notes (reduced from 1.5)
        ]
        
        # Create alternating row colors
        row_styles = []
        for i in range(1, len(table_data)):
            if i % 2 == 1:  # Alternate rows
                row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
        
        # For large transaction sets, use normal table without rounded corners
        use_rounded = len(table_data) < 25  # Only use rounded corners for smaller tables
        
        # Create table with repeating header
        transactions_table = Table(
            table_data,
            colWidths=col_widths,
            repeatRows=1,
            style=TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors['primary']),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid and borders
                ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors['border']),  # Thicker line below header
                
                # Cell padding
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Reduced from 4
                ('RIGHTPADDING', (0, 0), (-1, -1), 3), # Reduced from 4
            ] + row_styles)
        )
        
        # Apply table border 
        transactions_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors['border']),
        ]))
        
        # Create table content list
        table_content = []
        if use_rounded:
            # Wrap the table in a RoundedTableFlowable
            rounded_transactions_table = RoundedTableFlowable(transactions_table, corner_radius=8, padding=2)
            table_content.append(rounded_transactions_table)
        else:
            # Use standard table for large datasets to avoid overflow errors
            table_content.append(transactions_table)
        
        # Add note about transaction count
        if transactions:
            count_text = f"Total transactions: {len(transactions)}"
            table_content.append(Spacer(1, 0.05*inch))
            table_content.append(Paragraph(count_text, self.styles['BrandSmall']))
        
        # Add the table content
        elements.extend(table_content)
        
        return elements

    def _parse_amount(self, amount_str):
        """Parse amount from string format"""
        if isinstance(amount_str, str):
            # Remove '$' and ',' then convert to float
            return float(amount_str.replace('$', '').replace(',', ''))
        return float(amount_str)