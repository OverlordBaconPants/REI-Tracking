from datetime import datetime, timedelta
import os
import logging
import traceback
from io import BytesIO
import json
import math
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
                               Frame, PageTemplate, NextPageTemplate, FrameBreak, PageBreak, Flowable)
from reportlab.graphics.shapes import Drawing, Circle, String, Rect
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects
from matplotlib.ticker import FuncFormatter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Brand configuration
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

class KPICardFlowable(Flowable):
    """A flowable that draws a KPI card with value, target, and favorable/unfavorable indicator."""
    
    def __init__(self, title, value, target, is_favorable, width=2*inch, height=0.9*inch):
        Flowable.__init__(self)
        self.title = title
        self.value = value
        self.target = target
        self.is_favorable = is_favorable
        self.width = width
        self.height = height
        
    def draw(self):
        """Draw the KPI card with styling."""
        colors = BRAND_CONFIG['colors']
        
        # Draw card background with rounded corners
        self.canv.setFillColor(colors['neutral'])
        self.canv.setStrokeColor(colors['border_light'])
        self.canv.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=1)
        
        # Draw title
        self.canv.setFont(BRAND_CONFIG['fonts']['primary'], 9)
        self.canv.setFillColor(colors['primary'])
        self.canv.drawCentredString(self.width/2, self.height-14, self.title)
        
        # Draw value
        self.canv.setFont(BRAND_CONFIG['fonts']['primary'], 16)
        self.canv.setFillColor(colors['text_dark'])
        self.canv.drawCentredString(self.width/2, self.height/2, self.value)
        
        # Draw target
        self.canv.setFont(BRAND_CONFIG['fonts']['secondary'], 7)
        self.canv.setFillColor(colors['text_light'])
        self.canv.drawCentredString(self.width/2, 24, f"Target: {self.target}")
        
        # Draw status line
        status_color = colors['success'] if self.is_favorable else colors['danger']
        self.canv.setStrokeColor(status_color)
        self.canv.setLineWidth(1.5)
        self.canv.line(5, 18, self.width-5, 18)
        
        # Draw status text
        status_text = "FAVORABLE" if self.is_favorable else "UNFAVORABLE"
        self.canv.setFont(BRAND_CONFIG['fonts']['secondary'], 7)
        self.canv.setFillColor(status_color)
        self.canv.drawCentredString(self.width/2, 8, status_text)
    
    def wrap(self, availWidth, availHeight):
        """Return the size this flowable will take up."""
        return (self.width, self.height)

class ChartGenerator:
    """Generate charts for the report."""
    
    def create_amortization_chart(self, data):
        """Create an enhanced amortization chart showing balance, principal and interest."""
        buffer = BytesIO()
        colors = BRAND_CONFIG['colors']
        
        try:
            # Extract the schedule data
            schedule = data.get('total_schedule', [])
            if not schedule:
                raise ValueError("No amortization schedule data available")
                
            # Extract data for plotting
            months = [entry.get('month', i+1) for i, entry in enumerate(schedule)]
            balances = [entry.get('ending_balance', 0) for entry in schedule]
            
            # Calculate cumulative principal and interest
            cumulative_principal = []
            cumulative_interest = []
            principal_sum = 0
            interest_sum = 0
            
            for entry in schedule:
                principal_sum += entry.get('principal_payment', 0)
                interest_sum += entry.get('interest_payment', 0)
                cumulative_principal.append(principal_sum)
                cumulative_interest.append(interest_sum)
            
            # Determine if we have balloon data
            has_balloon = data.get('balloon_data') is not None
            balloon_month = None
            if has_balloon and data.get('balloon_data'):
                balloon_month = data['balloon_data'].get('months_to_balloon')
            
            # Create figure with improved size for legend
            fig, ax = plt.subplots(figsize=(5, 3.5), dpi=100)
            
            # Set background color
            fig.patch.set_facecolor('#FFFFFF')
            ax.set_facecolor('#F9FBFF')
            
            # Plot loan balance line
            ax.plot(months, balances, 
                color=colors['primary'], 
                linewidth=2,
                label='Loan Balance',
                solid_capstyle='round')
            
            # Plot cumulative principal line
            ax.plot(months, cumulative_principal, 
                color=colors['success'], 
                linewidth=2,
                label='Principal Paid',
                solid_capstyle='round')
            
            # Plot cumulative interest line
            ax.plot(months, cumulative_interest, 
                color=colors['danger'], 
                linewidth=2,
                label='Interest Paid',
                solid_capstyle='round')
            
            # Add balloon marker if applicable
            if has_balloon and balloon_month:
                ax.axvline(x=balloon_month, 
                        linestyle='--', 
                        color=colors['warning'], 
                        linewidth=1.5,
                        alpha=0.7,
                        label='Balloon Due')
            
            # Formatting
            ax.set_xlabel('Month', fontsize=9, fontweight='bold')
            ax.set_ylabel('Amount ($)', fontsize=9, fontweight='bold')
            ax.set_title('Loan Amortization Schedule', fontsize=10, fontweight='bold', pad=10)
            
            # Format y-axis as currency
            def currency_formatter(x, pos):
                if x >= 1000:
                    return f'${x/1000:.0f}K'
                return f'${x:.0f}'
            
            ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
            
            # Set y-axis to start at 0
            ax.set_ylim(bottom=0)
            
            # Add grid
            ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.3)
            
            # Add legend with better positioning
            ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
                    frameon=True, framealpha=0.9, fontsize=8, ncol=4)
            
            plt.tight_layout()
            plt.subplots_adjust(bottom=0.25)  # Add extra space for the legend
            
            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating amortization chart: {str(e)}")
            
            # Create a simple error message chart
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.text(0.5, 0.5, "Error generating chart", 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=ax.transAxes, 
                fontsize=10,
                color=colors['danger'])
            ax.axis('off')
            plt.savefig(buffer, format='png', dpi=100)
            plt.close(fig)
            
            buffer.seek(0)
            return buffer

# Main function to generate report that matches the original signature
def generate_report(data, report_type='analysis'):
    """Generate a PDF report from analysis data."""
    try:
        # Create report generator
        generator = PropertyReportGenerator(data)
        
        # Generate report
        return generator.generate()
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise RuntimeError(f"Failed to generate report: {str(e)}")

class PropertyReportGenerator:
    """Generate property analysis reports."""
    
    def __init__(self, data):
        """Initialize with property data."""
        self.data = data
        self.buffer = BytesIO()
        
        # Create document with proper margins
        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Create styles
        self.styles = self._create_styles()
        
        # Initialize chart generator
        self.chart_gen = ChartGenerator()
    
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
        
        return styles
    
    def _get_short_address(self, full_address):
        """Extract street address and city from full address."""
        if full_address and ',' in full_address:
            parts = full_address.split(',')
            if len(parts) >= 2:
                # Keep only the street address and city
                return f"{parts[0]}, {parts[1].strip()}"
        return full_address
    
    def create_header(self):
        """Create the header with address and logo."""
        elements = []
        
        # Get address and format title
        full_address = self.data.get('address', 'Property Analysis')
        title = self._get_short_address(full_address)
            
        # Create a subtitle
        analysis_type = self.data.get('analysis_type', '')
        current_date = datetime.now().strftime('%B %d, %Y')
        subtitle = f"{analysis_type} | {current_date}"
        
        # Create elements for header with proper spacing
        elements.append(Paragraph(title, self.styles['EnhancedTitle']))
        elements.append(Paragraph(subtitle, self.styles['EnhancedSubtitle']))
        
        return elements
    
    def create_property_details(self):
        """Create property details table."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Property Details", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Define styles for table cells
        label_style = ParagraphStyle(
            name='TableLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='TableValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        # Property fields
        property_fields = [
            ('property_type', 'Property Type'),
            ('square_footage', 'Square Footage'),
            ('lot_size', 'Lot Size'),
            ('year_built', 'Year Built'),
            ('bedrooms', 'Bedrooms'),
            ('bathrooms', 'Bathrooms')
        ]
        
        # Build table data
        table_data = []
        for key, label in property_fields:
            if key in self.data and self.data[key]:
                value = self.data[key]
                
                # Format values for better display
                if key in ['square_footage', 'lot_size']:
                    if isinstance(value, (int, float)):
                        value = f"{int(value):,} sq ft"
                elif key == 'bedrooms':
                    if isinstance(value, (int, float)):
                        value = f"{int(value)} BR"
                elif key == 'bathrooms':
                    if isinstance(value, (int, float)):
                        value = f"{float(value):.1f} BA"
                
                table_data.append([
                    Paragraph(label + ":", label_style),
                    Paragraph(str(value), value_style)
                ])
        
        # Create and style the table
        if table_data:
            # Calculate optimal column widths
            col1_width = min(1.5*inch, self.doc.width * 0.45 * 0.6)
            col2_width = (self.doc.width * 0.45) - col1_width
            
            # Create alternating row colors
            row_styles = []
            for i in range(len(table_data)):
                if i % 2 == 1:  # Alternate rows
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
            
            property_table = Table(
                table_data,
                colWidths=[col1_width, col2_width],
                style=TableStyle([
                    # Label styling - left column
                    ('BACKGROUND', (0, 0), (0, -1), colors['table_header']),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    
                    # Value styling - right column
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    
                    # Grid and borders
                    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Padding for breathing room
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ] + row_styles)
            )
            
            # Apply table border
            property_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
            ]))
            
            elements.append(property_table)
        else:
            # No data available
            elements.append(Paragraph("No property details available", self.styles['BrandNormal']))
        
        return elements
    
    def create_kpi_dashboard(self):
        """Create KPI dashboard with card metrics."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Key Performance Indicators", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Calculate KPI metrics from data
        kpi_data = self._calculate_kpi_metrics()
        
        # Define KPI cards layout
        card_width = (self.doc.width - 0.5*inch) / 3  # Divide available width into 3 columns with some spacing
        
        # First row of KPIs (3 cards)
        row1_cards = [
            ('Cash-on-Cash', 
             kpi_data.get('cash_on_cash', '0%'), 
             kpi_data.get('cash_on_cash_target', '≥ 10.0%'),
             kpi_data.get('cash_on_cash_favorable', False)),
            
            ('Cap Rate', 
             kpi_data.get('cap_rate', '0%'), 
             kpi_data.get('cap_rate_target', '6.0% - 12.0%'),
             kpi_data.get('cap_rate_favorable', False)),
             
            ('NOI', 
             kpi_data.get('noi', '$0'), 
             kpi_data.get('noi_target', '≥ $800'),
             kpi_data.get('noi_favorable', False))
        ]
        
        # Create first row of KPI cards
        row1_data = []
        for title, value, target, is_favorable in row1_cards:
            kpi_card = KPICardFlowable(title, value, target, is_favorable, width=card_width-0.1*inch)
            row1_data.append(kpi_card)
            
        row1_table = Table([row1_data], colWidths=[card_width-0.1*inch]*3, 
                         style=TableStyle([
                             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 5),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                         ]))
        
        elements.append(row1_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Second row of KPIs (2 cards)
        row2_cards = [
            ('DSCR', 
             kpi_data.get('dscr', '0'), 
             kpi_data.get('dscr_target', '≥ 1.25'),
             kpi_data.get('dscr_favorable', False)),
            
            ('Expense Ratio', 
             kpi_data.get('expense_ratio', '0%'), 
             kpi_data.get('expense_ratio_target', '≤ 40.0%'),
             kpi_data.get('expense_ratio_favorable', False))
        ]
        
        # Create second row of KPI cards
        row2_data = []
        for title, value, target, is_favorable in row2_cards:
            kpi_card = KPICardFlowable(title, value, target, is_favorable, width=card_width-0.1*inch)
            row2_data.append(kpi_card)
        
        # Add empty cell to maintain 3-column layout
        row2_data.append("")
            
        row2_table = Table([row2_data], colWidths=[card_width-0.1*inch]*3, 
                         style=TableStyle([
                             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                             ('LEFTPADDING', (0, 0), (-1, -1), 5),
                             ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                         ]))
        
        elements.append(row2_table)
        
        # Add explanation note
        elements.append(Spacer(1, 0.05*inch))
        note_text = (
            "KPIs evaluate investment aspects with target thresholds. 'Favorable' means the metric meets or exceeds its target."
        )
        elements.append(Paragraph(note_text, self.styles['BrandSmall']))
        
        return elements
    
    def create_amortization_section(self):
        """Create loan amortization section with chart."""
        elements = []
        
        # Add section header
        elements.append(Paragraph("Loan Amortization", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Generate amortization data
        amortization_data = self._calculate_amortization_data()
        
        # Generate chart if we have data
        if amortization_data.get('total_schedule'):
            # Create chart
            chart_buffer = self.chart_gen.create_amortization_chart(amortization_data)
            elements.append(Image(chart_buffer, width=4*inch, height=3*inch))
            
            # Add brief explanation
            if self._has_balloon_payment():
                explanation = "The vertical line indicates balloon due date."
            else:
                explanation = "Shows loan balance over time."
            elements.append(Paragraph(explanation, self.styles['BrandSmall']))
        else:
            # No data available
            elements.append(Paragraph("No loan amortization data available", self.styles['BrandNormal']))
        
        return elements
    
    def _add_page_decorations(self, canvas, doc):
        """Add page number, footer line, and logo (first page only)."""
        canvas.saveState()
        
        # Draw the footer with page number
        canvas.setFont(BRAND_CONFIG['fonts']['primary'], 8)
        canvas.setFillColor(BRAND_CONFIG['colors']['text_light'])
        canvas.drawRightString(
            doc.pagesize[0] - 0.5*inch,
            0.25*inch,
            f"Page {doc.page}"
        )
        
        # Add a thin footer line
        canvas.setStrokeColor(BRAND_CONFIG['colors']['primary'])
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
            logo_height = 1*inch  # Increased from 0.5 to 1 inch
            
            try:
                if os.path.exists(logo_path):
                    # Use actual logo from file with transparent background
                    canvas.drawImage(
                        logo_path,
                        doc.pagesize[0] - doc.rightMargin - 2.0*inch,  # Moved left to accommodate larger logo
                        doc.pagesize[1] - doc.topMargin - logo_height,
                        width=2.0*inch,  # Increased from 1.5 to 2.0 inch
                        height=logo_height,
                        preserveAspectRatio=True,
                        mask='auto'  # This makes white background transparent
                    )
                else:
                    # Placeholder if logo not found
                    logger.warning(f"Logo file not found at {logo_path}, using placeholder.")
                    # Code for placeholder logo...
            except Exception as e:
                logger.error(f"Error adding logo: {str(e)}")
        
        canvas.restoreState()
    
    def generate(self):
        """Generate the complete report with all sections."""
        try:
            story = []
            
            # Section 1: Header and property details
            story.extend(self.create_header())
            story.append(Spacer(1, 0.2*inch))
            story.extend(self.create_property_details())
            story.append(Spacer(1, 0.3*inch))
            
            # Section 2: KPI Dashboard and Amortization Chart
            story.extend(self.create_kpi_dashboard())
            story.append(Spacer(1, 0.3*inch))
            story.extend(self.create_amortization_section())
            story.append(Spacer(1, 0.3*inch))
            
            # Section 3: Long-Term Performance Projections
            story.extend(self.create_projections_section())
            story.append(Spacer(1, 0.3*inch))
            
            # Sections 4-6: Purchase Details and Financial Overviews
            if self._has_balloon_payment():
                # Single column for Purchase Details
                story.extend(self.create_purchase_details_section())
                story.append(Spacer(1, 0.3*inch))
                
                # Two-column Balloon Comparison
                story.extend(self.create_balloon_sections())
            else:
                # Two-column layout - Purchase Details and Financial Overview
                purchase_details = self.create_purchase_details_section()
                financial_overview = self.create_financial_overview_section()
                
                col_width = self.doc.width / 2 - 0.1*inch
                two_col_data = [[purchase_details, financial_overview]]
                
                two_col_table = Table(
                    two_col_data,
                    colWidths=[col_width, col_width],
                    style=TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('TOPPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                    ])
                )
                
                story.append(two_col_table)
            
            # Add page break before next section
            story.append(PageBreak())
            
            # Section 7: Loan Details and Operating Expenses
            story.extend(self.create_loans_and_expenses_section())
            
            # Check if we have comps data to add
            if self.data.get('comps_data') and self.data['comps_data'].get('comparables'):
                # Add page break before comps section
                story.append(PageBreak())
                
                # Section 8: Property Comparables
                story.extend(self.create_property_comps_section())
            
            # Build the document
            self.doc.build(story, onFirstPage=self._add_page_decorations, onLaterPages=self._add_page_decorations)
            self.buffer.seek(0)
            return self.buffer
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            logger.error(f"Stack trace: {traceback.format_exc()}")
            raise RuntimeError(f"Failed to generate report: {str(e)}")
    
    def _calculate_kpi_metrics(self):
        """Calculate KPI metrics from data."""
        kpi_data = {}
        
        # Get calculated metrics if available
        calculated_metrics = self.data.get('calculated_metrics', {})
        
        # Cash on Cash Return
        cash_on_cash = self._parse_percentage(calculated_metrics.get('cash_on_cash_return', '0%'))
        kpi_data['cash_on_cash'] = f"{cash_on_cash:.1f}%"
        kpi_data['cash_on_cash_target'] = '≥ 10.0%'
        kpi_data['cash_on_cash_favorable'] = cash_on_cash >= 10.0
        
        # Net Operating Income (NOI)
        noi_monthly = self._calculate_noi()
        kpi_data['noi'] = f"${noi_monthly:.2f}"
        kpi_data['noi_target'] = '≥ $800.00'
        kpi_data['noi_favorable'] = noi_monthly >= 800
        
        # Cap Rate
        purchase_price = self._parse_currency(self.data.get('purchase_price', 0))
        if purchase_price > 0:
            cap_rate = (noi_monthly * 12 / purchase_price) * 100
            kpi_data['cap_rate'] = f"{cap_rate:.1f}%"
            kpi_data['cap_rate_target'] = '6.0% - 12.0%'
            kpi_data['cap_rate_favorable'] = 6.0 <= cap_rate <= 12.0
        
        # Debt Service Coverage Ratio (DSCR)
        monthly_loan_payment = 0
        for prefix in ['loan1', 'loan2', 'loan3']:
            payment_str = calculated_metrics.get(f'{prefix}_loan_payment', '0')
            monthly_loan_payment += self._parse_currency(payment_str)
        
        if monthly_loan_payment > 0:
            dscr = noi_monthly / monthly_loan_payment
            kpi_data['dscr'] = f"{dscr:.2f}"
            kpi_data['dscr_target'] = '≥ 1.25'
            kpi_data['dscr_favorable'] = dscr >= 1.25
        
        # Operating Expense Ratio
        monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
        if monthly_rent > 0:
            total_expenses = self._calculate_total_expenses(monthly_rent)
            expense_ratio = (total_expenses / monthly_rent) * 100
            kpi_data['expense_ratio'] = f"{expense_ratio:.1f}%"
            kpi_data['expense_ratio_target'] = '≤ 40.0%'
            kpi_data['expense_ratio_favorable'] = expense_ratio <= 40.0
        
        return kpi_data
    
    def _calculate_noi(self):
        """Calculate Net Operating Income."""
        # Get monthly rent
        monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
        
        # Calculate expenses (excluding debt service)
        total_expenses = self._calculate_total_expenses(monthly_rent)
        
        # NOI = Rent - Expenses (excluding debt service)
        noi = monthly_rent - total_expenses
        
        return noi
    
    def _calculate_total_expenses(self, monthly_rent):
        """Calculate total monthly operating expenses."""
        # Fixed expenses
        fixed_expenses = sum([
            self._parse_currency(self.data.get('property_taxes', 0)),
            self._parse_currency(self.data.get('insurance', 0)),
            self._parse_currency(self.data.get('hoa_coa_coop', 0))
        ])
        
        # Percentage-based expenses
        pct_expenses = sum([
            monthly_rent * self._parse_percentage(self.data.get('management_fee_percentage', 0)) / 100,
            monthly_rent * self._parse_percentage(self.data.get('capex_percentage', 0)) / 100,
            monthly_rent * self._parse_percentage(self.data.get('vacancy_percentage', 0)) / 100,
            monthly_rent * self._parse_percentage(self.data.get('repairs_percentage', 0)) / 100
        ])
        
        # Add PadSplit-specific expenses if applicable
        padsplit_expenses = 0
        if 'PadSplit' in self.data.get('analysis_type', ''):
            padsplit_expenses = sum([
                self._parse_currency(self.data.get('utilities', 0)),
                self._parse_currency(self.data.get('internet', 0)),
                self._parse_currency(self.data.get('cleaning', 0)),
                self._parse_currency(self.data.get('pest_control', 0)),
                self._parse_currency(self.data.get('landscaping', 0)),
                monthly_rent * self._parse_percentage(self.data.get('padsplit_platform_percentage', 0)) / 100
            ])
        
        return fixed_expenses + pct_expenses + padsplit_expenses
    
    def _calculate_amortization_data(self):
        """Calculate amortization schedule data."""
        # Check if this has a balloon payment
        has_balloon = self._has_balloon_payment()
        
        if has_balloon:
            return self._calculate_balloon_amortization()
        else:
            return self._calculate_standard_amortization()
    
    def _has_balloon_payment(self):
        """Check if this analysis has balloon payment."""
        has_balloon = self.data.get('has_balloon_payment', False)
        if not has_balloon:
            return False
            
        # Additional validation for balloon payment values
        balloon_amount = self._parse_currency(self.data.get('balloon_refinance_loan_amount', 0))
        return bool(has_balloon and balloon_amount > 0 and self.data.get('balloon_due_date'))
    
    def _calculate_standard_amortization(self):
        """Calculate standard amortization schedule for loans."""
        schedules = []
        
        for i in range(1, 4):
            prefix = f'loan{i}'
            amount = self._parse_currency(self.data.get(f'{prefix}_loan_amount', 0))
            if amount > 0:
                interest_rate = self._parse_percentage(self.data.get(f'{prefix}_loan_interest_rate', 0)) / 100 / 12
                term_months = int(self.data.get(f'{prefix}_loan_term', 0) or 0)
                is_interest_only = self.data.get(f'{prefix}_interest_only', False)
                
                if term_months > 0:
                    schedule = self._calculate_loan_schedule(
                        principal=amount,
                        interest_rate=interest_rate,
                        term_months=term_months,
                        is_interest_only=is_interest_only,
                        label=f"Loan {i}"
                    )
                    
                    schedules.append(schedule)
        
        # Combine schedules if multiple loans
        if len(schedules) > 1:
            max_length = max(len(schedule['schedule']) for schedule in schedules)
            
            total_schedule = []
            for month in range(max_length):
                month_data = {
                    'month': month + 1,
                    'date': datetime.now() + timedelta(days=30 * month),
                    'principal_payment': 0,
                    'interest_payment': 0,
                    'total_payment': 0,
                    'ending_balance': 0,
                    'period': 'standard'
                }
                
                for schedule in schedules:
                    if month < len(schedule['schedule']):
                        month_entry = schedule['schedule'][month]
                        month_data['principal_payment'] += month_entry['principal_payment']
                        month_data['interest_payment'] += month_entry['interest_payment']
                        month_data['total_payment'] += month_entry['total_payment']
                        month_data['ending_balance'] += month_entry['ending_balance']
                
                total_schedule.append(month_data)
        elif len(schedules) == 1:
            # Use the single schedule directly
            total_schedule = schedules[0]['schedule']
            for entry in total_schedule:
                entry['period'] = 'standard'
        else:
            total_schedule = []
        
        return {
            'loans': schedules,
            'balloon_data': None,
            'total_schedule': total_schedule
        }
    
    def _calculate_balloon_amortization(self):
        """Calculate amortization schedule for balloon payment scenario."""
        # Calculate pre-balloon amortization
        balloon_date = None
        balloon_date_str = self.data.get('balloon_due_date', '')
        
        try:
            if 'T' in balloon_date_str:
                balloon_date = datetime.fromisoformat(balloon_date_str.replace('Z', '+00:00'))
            else:
                balloon_date = datetime.strptime(balloon_date_str, '%Y-%m-%d')
                
            today = datetime.now()
            months_to_balloon = max(1, (balloon_date.year - today.year) * 12 + (balloon_date.month - today.month))
        except (ValueError, TypeError):
            # Default to 60 months if date parsing fails
            months_to_balloon = 60
            balloon_date = today + timedelta(days=30 * 60)
        
        # Setup balloon data
        balloon_data = {
            'balloon_date': balloon_date,
            'months_to_balloon': months_to_balloon
        }
        
        # Process pre-balloon loans
        pre_balloon_schedules = []
        total_pre_balloon_balance = 0
        
        for i in range(1, 4):
            prefix = f'loan{i}'
            amount = self._parse_currency(self.data.get(f'{prefix}_loan_amount', 0))
            if amount > 0:
                interest_rate = self._parse_percentage(self.data.get(f'{prefix}_loan_interest_rate', 0)) / 100 / 12
                term_months = int(self.data.get(f'{prefix}_loan_term', 0) or 0)
                is_interest_only = self.data.get(f'{prefix}_interest_only', False)
                
                if term_months > 0:
                    # Calculate schedule
                    schedule = self._calculate_loan_schedule(
                        principal=amount,
                        interest_rate=interest_rate,
                        term_months=term_months,
                        months_to_calculate=months_to_balloon,
                        is_interest_only=is_interest_only,
                        label=f"Loan {i}"
                    )
                    
                    pre_balloon_schedules.append(schedule)
                    if schedule['schedule'] and len(schedule['schedule']) > 0:
                        total_pre_balloon_balance += schedule['schedule'][-1]['ending_balance']
        
        # Calculate post-balloon refinance
        refinance_amount = self._parse_currency(self.data.get('balloon_refinance_loan_amount', 0))
        refinance_rate = self._parse_percentage(self.data.get('balloon_refinance_loan_interest_rate', 0)) / 100 / 12
        refinance_term = int(self.data.get('balloon_refinance_loan_term', 0) or 0)
        
        post_balloon_schedule = None
        if refinance_amount > 0 and refinance_term > 0:
            post_balloon_schedule = self._calculate_loan_schedule(
                principal=refinance_amount,
                interest_rate=refinance_rate,
                term_months=refinance_term,
                start_date=balloon_date,
                label="Refinance Loan"
            )
        
        # Combine schedules
        total_schedule = []
        
        # Add pre-balloon months
        if pre_balloon_schedules:
            for month in range(months_to_balloon):
                month_data = {
                    'month': month + 1,
                    'date': datetime.now() + timedelta(days=30 * month),
                    'principal_payment': 0,
                    'interest_payment': 0,
                    'total_payment': 0,
                    'ending_balance': 0,
                    'period': 'pre-balloon'
                }
                
                for schedule in pre_balloon_schedules:
                    if month < len(schedule['schedule']):
                        month_entry = schedule['schedule'][month]
                        month_data['principal_payment'] += month_entry['principal_payment']
                        month_data['interest_payment'] += month_entry['interest_payment']
                        month_data['total_payment'] += month_entry['total_payment']
                        month_data['ending_balance'] += month_entry['ending_balance']
                
                total_schedule.append(month_data)
        
        # Add post-balloon months
        if post_balloon_schedule:
            for i, month_entry in enumerate(post_balloon_schedule['schedule']):
                modified_entry = month_entry.copy()
                modified_entry['month'] = months_to_balloon + i + 1
                modified_entry['period'] = 'post-balloon'
                total_schedule.append(modified_entry)
        
        return {
            'loans': pre_balloon_schedules + ([post_balloon_schedule] if post_balloon_schedule else []),
            'balloon_data': balloon_data,
            'total_schedule': total_schedule
        }
    
    def _calculate_loan_schedule(self, principal, interest_rate, term_months, 
                              months_to_calculate=None, is_interest_only=False,
                              start_date=None, label="Loan"):
        """Calculate amortization schedule for a single loan."""
        if months_to_calculate is None:
            months_to_calculate = term_months
            
        if start_date is None:
            start_date = datetime.now()
        
        # Calculate monthly payment
        if is_interest_only:
            monthly_payment = principal * interest_rate
        elif interest_rate > 0:
            monthly_payment = principal * (interest_rate * (1 + interest_rate) ** term_months) / ((1 + interest_rate) ** term_months - 1)
        else:
            # Simple principal-only payment for 0% loans
            monthly_payment = principal / term_months
            
        schedule = []
        remaining_balance = principal
        
        for month in range(1, min(months_to_calculate + 1, term_months + 1)):
            if is_interest_only:
                interest = remaining_balance * interest_rate
                principal_payment = 0  # No principal payment for interest-only
                
                # If it's the last month, pay off the entire principal
                if month == term_months:
                    principal_payment = remaining_balance
            else:
                interest = remaining_balance * interest_rate
                principal_payment = monthly_payment - interest
            
            # Handle edge cases for very small remaining amounts
            if remaining_balance < principal_payment:
                principal_payment = remaining_balance
                
            remaining_balance -= principal_payment
            
            # Calculate payment date
            payment_date = start_date + timedelta(days=30 * (month - 1))
            
            month_data = {
                'month': month,
                'date': payment_date,
                'principal_payment': principal_payment,
                'interest_payment': interest,
                'total_payment': principal_payment + interest,
                'ending_balance': remaining_balance
            }
            
            schedule.append(month_data)
            
            # Stop if balance is paid off
            if remaining_balance <= 0:
                break
        
        return {
            'label': label,
            'principal': principal,
            'interest_rate': interest_rate * 12 * 100,  # Convert back to annual percentage
            'term_months': term_months,
            'monthly_payment': monthly_payment,
            'is_interest_only': is_interest_only,
            'schedule': schedule
        }
    
    def _parse_currency(self, value):
        """Parse currency value to float."""
        if value is None:
            return 0.0
            
        try:
            if isinstance(value, str):
                # Remove currency symbols and commas - fixed string syntax
                value = value.replace('$', '').replace(',', '')
            return float(value)
        except (ValueError, TypeError):
            return 0.0
        
    def _parse_percentage(self, value):
        """Parse percentage value to float."""
        if value is None:
            return 0.0
            
        try:
            if isinstance(value, str):
                value = value.replace('%', '')
            return float(value)
        except (ValueError, TypeError):
            return 0.0
        
    def create_projections_section(self):
        
        """Create long-term performance projections section."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Long-Term Performance Projections", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Calculate projections data
        projections_data = self._calculate_projections_data()
        
        # Create table with projection data
        if projections_data.get('metrics') and projections_data.get('timeframes'):
            table_data = self._create_projections_table_data(projections_data)
            
            # Calculate column widths
            table_width = self.doc.width * 0.95
            first_col_width = table_width * 0.25
            other_col_width = (table_width - first_col_width) / len(projections_data['timeframes'])
            col_widths = [first_col_width] + [other_col_width] * len(projections_data['timeframes'])
            
            # Create alternating row colors
            row_styles = []
            for i in range(1, len(table_data)):  # Skip header row
                if i % 2 == 1:  # Alternate rows
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
            
            # Create table with styling
            projections_table = Table(
                table_data,
                colWidths=col_widths,
                style=TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors['primary']),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors['background']),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # First column styling
                    ('BACKGROUND', (0, 1), (0, -1), colors['table_header']),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    
                    # Values styling
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    
                    # Grid and borders
                    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Padding
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ] + row_styles)
            )
            
            elements.append(projections_table)
            
            # Add explanation note
            elements.append(Spacer(1, 0.06*inch))
            note_text = (
                "These projections assume 2.5% annual rent and expense growth, "
                "3% property appreciation rate, and include both principal reduction "
                "and property appreciation in the equity calculations."
            )
            elements.append(Paragraph(note_text, self.styles['BrandSmall']))
        else:
            # No data available
            elements.append(Paragraph("No projections data available", self.styles['BrandNormal']))
        
        return elements

    def _create_projections_table_data(self, projections_data):
        """Create table data for projections."""
        timeframes = projections_data['timeframes']
        metrics = projections_data['metrics']
        
        # Create header row
        header_style = ParagraphStyle(
            name='ProjectionHeader',
            parent=self.styles['TableHeader'],
            fontSize=8,
            textColor=BRAND_CONFIG['colors']['background'],
            alignment=1  # Center aligned
        )
        
        metric_style = ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=BRAND_CONFIG['colors']['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='MetricValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=BRAND_CONFIG['colors']['text_dark'],
            alignment=2  # Right aligned
        )
        
        # Create header row
        table_data = [
            [Paragraph("Metric", header_style)] + 
            [Paragraph(f"Year {year}", header_style) for year in timeframes]
        ]
        
        # Define metrics to display
        metric_display = [
            ('monthly_cash_flow', 'Monthly Cash Flow', 'currency'),
            ('noi', 'Net Operating Income', 'currency'),
            ('cash_on_cash', 'Cash-on-Cash Return', 'percentage'),
            ('cap_rate', 'Cap Rate', 'percentage'),
            ('equity_earned', 'Equity Earned', 'currency')
        ]
        
        # Add rows for each metric
        for metric_key, metric_name, format_type in metric_display:
            if metric_key in metrics:
                row = [Paragraph(metric_name, metric_style)]
                
                # Add value for each timeframe
                for i, year in enumerate(timeframes):
                    value = metrics[metric_key][i]
                    
                    # Format based on type
                    if format_type == 'currency':
                        formatted_value = f"${value:,.2f}"
                    else:  # percentage
                        formatted_value = f"{value:.1f}%"
                    
                    row.append(Paragraph(formatted_value, value_style))
                    
                table_data.append(row)
        
        return table_data

    def _calculate_projections_data(self):
        """Calculate projection data for future years."""
        timeframes = [1, 3, 5, 10]  # Years to project
        
        # Initialize metrics dictionary
        metrics = {
            'monthly_cash_flow': [],
            'noi': [],
            'cash_on_cash': [],
            'cap_rate': [],
            'equity_earned': []
        }
        
        # Starting values
        purchase_price = self._parse_currency(self.data.get('purchase_price', 0))
        monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
        monthly_expenses = self._calculate_total_expenses(monthly_rent)
        
        # Get loan information for principal reduction calculation
        amortization_data = self._calculate_amortization_data()
        
        # Annual growth rates
        rent_growth_rate = 0.025  # 2.5% annual rent growth
        expense_growth_rate = 0.025  # 2.5% annual expense growth
        appreciation_rate = 0.03  # 3% annual property appreciation
        
        # Calculate metrics for each timeframe
        for year in timeframes:
            # Apply growth rates
            projected_monthly_rent = monthly_rent * (1 + rent_growth_rate) ** year
            projected_monthly_expenses = monthly_expenses * (1 + expense_growth_rate) ** year
            
            # Calculate NOI
            projected_noi = projected_monthly_rent - projected_monthly_expenses
            metrics['noi'].append(projected_noi)
            
            # Calculate property value with appreciation
            projected_property_value = purchase_price * (1 + appreciation_rate) ** year
            
            # Calculate loan balances and equity
            loan_balance = self._get_loan_balance_at_year(amortization_data, year)
            equity = projected_property_value - loan_balance
            metrics['equity_earned'].append(equity)
            
            # Calculate monthly cash flow
            monthly_loan_payment = self._get_loan_payment_at_year(amortization_data, year)
            projected_monthly_cash_flow = projected_noi - monthly_loan_payment
            metrics['monthly_cash_flow'].append(projected_monthly_cash_flow)
            
            # Calculate cap rate
            if projected_property_value > 0:
                projected_cap_rate = (projected_noi * 12 / projected_property_value) * 100
            else:
                projected_cap_rate = 0
            metrics['cap_rate'].append(projected_cap_rate)
            
            # Calculate cash-on-cash return
            total_investment = self._calculate_total_investment()
            if total_investment > 0:
                projected_cash_on_cash = (projected_monthly_cash_flow * 12 / total_investment) * 100
            else:
                projected_cash_on_cash = 0
            metrics['cash_on_cash'].append(projected_cash_on_cash)
        
        return {
            'timeframes': timeframes,
            'metrics': metrics
        }

    def _get_loan_balance_at_year(self, amortization_data, years):
        """Get the remaining loan balance at a specific year."""
        schedule = amortization_data.get('total_schedule', [])
        if not schedule:
            return 0
            
        target_month = years * 12
        
        # Find the closest month in the schedule
        for i in range(len(schedule) - 1, -1, -1):
            if schedule[i]['month'] <= target_month:
                return schedule[i]['ending_balance']
        
        return 0

    def _get_loan_payment_at_year(self, amortization_data, years):
        """Get the monthly loan payment at a specific year."""
        schedule = amortization_data.get('total_schedule', [])
        if not schedule:
            return 0
            
        target_month = years * 12
        
        # Find the closest month in the schedule
        for i in range(len(schedule) - 1, -1, -1):
            if schedule[i]['month'] <= target_month:
                return schedule[i]['total_payment']
        
        return 0

    def _calculate_total_investment(self):
        """Calculate total cash invested in the property."""
        # Sum up down payments from all loans
        down_payment_total = 0
        for i in range(1, 4):
            prefix = f'loan{i}'
            down_payment_total += self._parse_currency(self.data.get(f'{prefix}_loan_down_payment', 0))
        
        # Add closing costs
        closing_costs = self._parse_currency(self.data.get('closing_costs', 0))
        
        # Add renovation costs
        renovation_costs = self._parse_currency(self.data.get('renovation_costs', 0))
        
        # Add other costs like furnishings (for PadSplit)
        furnishing_costs = self._parse_currency(self.data.get('furnishing_costs', 0))
        
        return down_payment_total + closing_costs + renovation_costs + furnishing_costs
    
    def create_purchase_details_section(self):
        """Create purchase details section with pricing and costs."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Purchase Details", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Define styles for table cells
        label_style = ParagraphStyle(
            name='PurchaseLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='PurchaseValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        # Define purchase fields based on analysis type
        purchase_fields = []
        
        # For Lease Option, include specific fields
        if self.data.get('analysis_type') == 'Lease Option':
            purchase_fields = [
                ('purchase_price', 'Purchase Price'),
                ('strike_price', 'Strike Price'),
                ('option_consideration_fee', 'Option Fee'),
                ('option_term_months', 'Option Term'),
                ('monthly_rent_credit_percentage', 'Monthly Rent Credit %'),
                ('rent_credit_cap', 'Rent Credit Cap')
            ]
        else:
            # For other analysis types, include standard fields
            purchase_fields = [
                ('purchase_price', 'Purchase Price'),
                ('after_repair_value', 'After Repair Value'),
                ('renovation_costs', 'Renovation Costs'),
                ('renovation_duration', 'Renovation Duration'),
                ('cash_to_seller', 'Cash to Seller'),
                ('closing_costs', 'Closing Costs'),
                ('assignment_fee', 'Assignment Fee'),
                ('marketing_costs', 'Marketing Costs')
            ]
            
            # Add PadSplit-specific field
            if 'PadSplit' in self.data.get('analysis_type', ''):
                purchase_fields.append(('furnishing_costs', 'Furnishing Costs'))
        
        # Build table data
        table_data = []
        for key, label in purchase_fields:
            if key in self.data and self.data[key]:
                value = self.data[key]
                
                # Format values for better display
                if key in ['purchase_price', 'after_repair_value', 'renovation_costs', 
                        'cash_to_seller', 'closing_costs', 'assignment_fee', 
                        'marketing_costs', 'furnishing_costs', 'strike_price',
                        'option_consideration_fee', 'rent_credit_cap']:
                    if isinstance(value, (int, float)):
                        value = f"${value:,.2f}"
                # Format renovation duration
                elif key == 'renovation_duration':
                    if isinstance(value, (int, float)) and value > 0:
                        value = f"{int(value)} month{'s' if int(value) != 1 else ''}"
                # Format option term
                elif key == 'option_term_months':
                    if isinstance(value, (int, float)) and value > 0:
                        value = f"{int(value)} month{'s' if int(value) != 1 else ''}"
                # Format rent credit percentage
                elif key == 'monthly_rent_credit_percentage':
                    if isinstance(value, (int, float)):
                        value = f"{value}%"
                
                table_data.append([
                    Paragraph(label + ":", label_style),
                    Paragraph(str(value), value_style)
                ])
        
        # Create and style the table
        if table_data:
            # Calculate optimal column widths
            col1_width = min(1.6*inch, self.doc.width * 0.45 * 0.6)
            col2_width = (self.doc.width * 0.45) - col1_width
            
            # Create alternating row colors
            row_styles = []
            for i in range(len(table_data)):
                if i % 2 == 1:  # Alternate rows
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
            
            purchase_table = Table(
                table_data,
                colWidths=[col1_width, col2_width],
                style=TableStyle([
                    # Label styling - left column
                    ('BACKGROUND', (0, 0), (0, -1), colors['table_header']),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    
                    # Value styling - right column
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    
                    # Grid and borders
                    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Padding for breathing room
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ] + row_styles)
            )
            
            # Apply table border
            purchase_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
            ]))
            
            elements.append(purchase_table)
        else:
            # No data available
            elements.append(Paragraph("No purchase details available", self.styles['BrandNormal']))
        
        return elements
    
    def create_financial_overview_section(self):
        """Create financial overview section."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Financial Overview", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
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
        
        # Define financial fields based on analysis type
        financial_fields = []
        
        if self.data.get('analysis_type') == 'Lease Option':
            financial_fields = [
                ('monthly_rent', 'Monthly Rent'),
                ('monthly_cash_flow', 'Monthly Cash Flow'),
                ('annual_cash_flow', 'Annual Cash Flow'),
                ('total_rent_credits', 'Total Rent Credits'),
                ('effective_purchase_price', 'Effective Purchase Price'),
                ('cash_on_cash_return', 'Cash on Cash Return'),
                ('breakeven_months', 'Breakeven Months')
            ]
        else:
            financial_fields = [
                ('monthly_rent', 'Monthly Rent'),
                ('monthly_cash_flow', 'Monthly Cash Flow'),
                ('annual_cash_flow', 'Annual Cash Flow'),
                ('cash_on_cash_return', 'Cash on Cash Return'),
                ('roi', 'ROI'),
                ('total_cash_invested', 'Total Cash Invested')
            ]
        
        # Build table data
        table_data = []
        
        # Get calculated metrics
        calculated_metrics = self.data.get('calculated_metrics', {})
        
        for key, label in financial_fields:
            value = None
            
            # Get value from calculated metrics if available
            if key in calculated_metrics:
                value = calculated_metrics[key]
            # Calculate some values if not already available
            elif key == 'monthly_cash_flow':
                noi = self._calculate_noi()
                monthly_loan_payment = self._calculate_total_loan_payment()
                value = f"${noi - monthly_loan_payment:.2f}"
            elif key == 'annual_cash_flow':
                if 'monthly_cash_flow' in calculated_metrics:
                    monthly = self._parse_currency(calculated_metrics['monthly_cash_flow'])
                    value = f"${monthly * 12:.2f}"
            elif key == 'total_cash_invested':
                total = self._calculate_total_investment()
                value = f"${total:.2f}"
            # Use direct values for some fields
            elif key == 'monthly_rent':
                value = f"${self._parse_currency(self.data.get('monthly_rent', 0)):.2f}"
            elif key == 'total_rent_credits' and not value:
                # Calculate for Lease Option if not provided
                monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
                credit_pct = self._parse_percentage(self.data.get('monthly_rent_credit_percentage', 0)) / 100
                term = int(self.data.get('option_term_months', 0))
                cap = self._parse_currency(self.data.get('rent_credit_cap', 0))
                
                total_credits = min(monthly_rent * credit_pct * term, cap)
                value = f"${total_credits:.2f}"
            elif key == 'effective_purchase_price' and not value:
                # Calculate for Lease Option if not provided
                strike_price = self._parse_currency(self.data.get('strike_price', 0))
                
                # Get total rent credits (from above calculation)
                monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
                credit_pct = self._parse_percentage(self.data.get('monthly_rent_credit_percentage', 0)) / 100
                term = int(self.data.get('option_term_months', 0))
                cap = self._parse_currency(self.data.get('rent_credit_cap', 0))
                
                total_credits = min(monthly_rent * credit_pct * term, cap)
                
                value = f"${strike_price - total_credits:.2f}"
            
            if value:
                table_data.append([
                    Paragraph(label + ":", label_style),
                    Paragraph(str(value), value_style)
                ])
        
        # Create and style the table
        if table_data:
            # Calculate column widths
            col1_width = min(1.6*inch, self.doc.width * 0.45 * 0.6)
            col2_width = (self.doc.width * 0.45) - col1_width
            
            # Create alternating row colors
            row_styles = []
            for i in range(len(table_data)):
                if i % 2 == 1:  # Alternate rows
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
            
            financial_table = Table(
                table_data,
                colWidths=[col1_width, col2_width],
                style=TableStyle([
                    # Label styling - left column
                    ('BACKGROUND', (0, 0), (0, -1), colors['table_header']),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    
                    # Value styling - right column
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    
                    # Grid and borders
                    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Padding
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ] + row_styles)
            )
            
            # Apply table border
            financial_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
            ]))
            
            elements.append(financial_table)
        else:
            # No data available
            elements.append(Paragraph("No financial overview available", self.styles['BrandNormal']))
        
        return elements
    
    def _calculate_total_loan_payment(self):
        """Calculate total monthly loan payment across all loans."""
        # Get calculated metrics
        calculated_metrics = self.data.get('calculated_metrics', {})
        
        # For BRRRR, use refinance loan payment or initial loan payment
        if 'BRRRR' in self.data.get('analysis_type', ''):
            if 'refinance_loan_payment' in calculated_metrics:
                return self._parse_currency(calculated_metrics['refinance_loan_payment'])
            elif 'initial_loan_payment' in calculated_metrics:
                return self._parse_currency(calculated_metrics['initial_loan_payment'])
        
        # For standard loans, sum all loan payments
        total_payment = 0
        for i in range(1, 4):
            payment_key = f'loan{i}_loan_payment'
            if payment_key in calculated_metrics:
                total_payment += self._parse_currency(calculated_metrics[payment_key])
        
        return total_payment
    
    def create_balloon_sections(self):
        """Create pre/post balloon payment financial overviews."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Create two sections for balloon payment comparison
        pre_balloon = self.create_balloon_financial_section('pre_balloon', "Pre-Balloon Financial Overview")
        post_balloon = self.create_balloon_financial_section('post_balloon', "Post-Balloon Financial Overview")
        
        # Create a two-column layout with pre-balloon and post-balloon sections
        col_width = self.doc.width / 2 - 0.1*inch
        two_col_data = [[pre_balloon, post_balloon]]
        
        two_col_table = Table(
            two_col_data,
            colWidths=[col_width, col_width],
            style=TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        
        elements.append(two_col_table)
        return elements

    def create_balloon_financial_section(self, section_type, title):
        """Create financial overview for balloon payment scenarios."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph(title, self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Define styles for table cells
        label_style = ParagraphStyle(
            name=f'{section_type}Label',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name=f'{section_type}Value',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        # Define financial fields based on section type
        if section_type == 'pre_balloon':
            financial_fields = [
                ('monthly_rent', 'Monthly Rent'),
                ('monthly_cash_flow', 'Monthly Cash Flow'),
                ('annual_cash_flow', 'Annual Cash Flow'),
                ('cash_on_cash_return', 'Cash on Cash Return'),
                ('balloon_due_date', 'Balloon Due Date')
            ]
        else:  # post_balloon
            financial_fields = [
                ('monthly_rent', 'Monthly Rent'),
                ('monthly_cash_flow', 'Monthly Cash Flow'),
                ('annual_cash_flow', 'Annual Cash Flow'),
                ('cash_on_cash_return', 'Cash-on-Cash Return'),
                ('refinance_amount', 'Refinance Amount'),
                ('refinance_ltv', 'Refinance LTV'),
                ('monthly_payment_change', 'Monthly Payment Change')
            ]
        
        # Build table data
        table_data = []
        calculated_metrics = self.data.get('calculated_metrics', {})
        
        # Get prefix-based metrics
        for key, label in financial_fields:
            value = None
            metric_key = f"{section_type}_{key}" if key not in ['balloon_due_date', 'refinance_amount', 'refinance_ltv'] else key
                
            # Get value from calculated metrics if available
            if metric_key in calculated_metrics:
                value = calculated_metrics[metric_key]
            # Special case handling
            elif key == 'balloon_due_date':
                value = self.data.get('balloon_due_date', '')
                if 'T' in value:
                    # Format ISO date
                    try:
                        date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        value = date_obj.strftime('%B %d, %Y')
                    except (ValueError, TypeError):
                        pass
            elif key == 'refinance_amount':
                value = f"${self._parse_currency(self.data.get('balloon_refinance_loan_amount', 0)):,.2f}"
            elif key == 'refinance_ltv':
                value = f"{self._parse_percentage(self.data.get('balloon_refinance_ltv_percentage', 0)):.1f}%"
            elif key == 'monthly_rent':
                # For post-balloon, apply rent growth
                if section_type == 'post_balloon':
                    balloon_date = self.data.get('balloon_due_date', '')
                    today = datetime.now()
                    years_to_balloon = 0
                    
                    try:
                        if 'T' in balloon_date:
                            balloon_date = datetime.fromisoformat(balloon_date.replace('Z', '+00:00'))
                        else:
                            balloon_date = datetime.strptime(balloon_date, '%Y-%m-%d')
                        
                        years_to_balloon = max(0, (balloon_date.year - today.year) + 
                                            (balloon_date.month - today.month) / 12)
                    except (ValueError, TypeError):
                        years_to_balloon = 8  # Default if parsing fails
                    
                    # Apply 2.5% annual rent growth
                    monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
                    grown_rent = monthly_rent * (1.025 ** years_to_balloon)
                    value = f"${grown_rent:.2f}"
                else:
                    value = f"${self._parse_currency(self.data.get('monthly_rent', 0)):.2f}"
            
            if value:
                table_data.append([
                    Paragraph(label + ":", label_style),
                    Paragraph(str(value), value_style)
                ])
        
        # Create and style the table
        if table_data:
            # Calculate column widths
            col1_width = min(1.6*inch, (self.doc.width/2 - 0.2*inch) * 0.6)
            col2_width = (self.doc.width/2 - 0.2*inch) - col1_width
            
            # Create alternating row colors
            row_styles = []
            for i in range(len(table_data)):
                if i % 2 == 1:  # Alternate rows
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
            
            financial_table = Table(
                table_data,
                colWidths=[col1_width, col2_width],
                style=TableStyle([
                    # Label styling - left column
                    ('BACKGROUND', (0, 0), (0, -1), colors['table_header']),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    
                    # Value styling - right column
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    
                    # Grid and borders
                    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Padding
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ] + row_styles)
            )
            
            # Apply table border
            financial_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
            ]))
            
            elements.append(financial_table)
        else:
            # No data available
            elements.append(Paragraph(f"No {section_type} financial data available", self.styles['BrandNormal']))
        
        return elements
    
    def create_loans_and_expenses_section(self):
        """Create two-column section with loan details and operating expenses."""
        elements = []
        
        # Create loan details and operating expenses
        loan_details = self.create_loan_details_section()
        operating_expenses = self.create_operating_expenses_section()
        
        # Create two-column layout
        col_width = self.doc.width / 2 - 0.1*inch
        two_col_data = [[loan_details, operating_expenses]]
        
        two_col_table = Table(
            two_col_data,
            colWidths=[col_width, col_width],
            style=TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ])
        )
        
        elements.append(two_col_table)
        return elements

    def create_loan_details_section(self):
        """Create loan details section."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Loan Details", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Create loan tables based on analysis type
        if 'BRRRR' in self.data.get('analysis_type', ''):
            # BRRRR: Show initial and refinance loans
            elements.append(self._create_loan_table("Initial Hard Money Loan", 
                                                prefix='initial',
                                                special_styling='hard_money'))
            elements.append(Spacer(1, 0.2*inch))
            elements.append(self._create_loan_table("Refinance Loan", 
                                                prefix='refinance',
                                                special_styling='refinance'))
        elif self._has_balloon_payment():
            # Balloon payment: Show loans with balloon and refinance details
            # Pre-balloon loans
            for i in range(1, 4):
                prefix = f'loan{i}'
                if self._has_loan(prefix):
                    loan_name = self.data.get(f'{prefix}_loan_name', '') or f"Loan {i}"
                    elements.append(self._create_loan_table(f"{loan_name} (Pre-Balloon)", 
                                                        prefix=prefix,
                                                        special_styling='balloon_pre'))
                    elements.append(Spacer(1, 0.1*inch))
            
            # Add balloon summary
            elements.append(self._create_balloon_summary())
            elements.append(Spacer(1, 0.1*inch))
            
            # Add refinance details
            elements.append(self._create_balloon_refinance_table())
        else:
            # Standard loans: Show each loan
            for i in range(1, 4):
                prefix = f'loan{i}'
                if self._has_loan(prefix):
                    loan_name = self.data.get(f'{prefix}_loan_name', '') or f"Loan {i}"
                    elements.append(self._create_loan_table(loan_name, prefix=prefix))
                    if i < 3 and self._has_loan(f'loan{i+1}'):
                        elements.append(Spacer(1, 0.1*inch))
        
        return elements

    def create_operating_expenses_section(self):
        """Create operating expenses section."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Operating Expenses", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Define styles for table cells
        label_style = ParagraphStyle(
            name='ExpenseLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='ExpenseValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        category_style = ParagraphStyle(
            name='ExpenseCategory',
            parent=self.styles['BrandNormal'],
            fontSize=7,
            textColor=colors['text_light'],
            fontName=BRAND_CONFIG['fonts']['primary'],
            alignment=0  # Left aligned
        )
        
        # Organize expenses by category
        fixed_expenses = []
        percentage_expenses = []
        padsplit_expenses = []
        
        # Fixed expenses
        for key, label in [
            ('property_taxes', 'Property Taxes'),
            ('insurance', 'Insurance'),
            ('hoa_coa_coop', 'HOA/COA/COOP')
        ]:
            if key in self.data and self.data[key]:
                value = f"${self._parse_currency(self.data[key]):.2f}"
                fixed_expenses.append([
                    Paragraph(label + ":", label_style),
                    Paragraph(value, value_style)
                ])
        
        # PadSplit specific expenses
        if 'PadSplit' in self.data.get('analysis_type', ''):
            for key, label in [
                ('utilities', 'Utilities'),
                ('internet', 'Internet'),
                ('cleaning', 'Cleaning'),
                ('pest_control', 'Pest Control'),
                ('landscaping', 'Landscaping')
            ]:
                if key in self.data and self.data[key]:
                    value = f"${self._parse_currency(self.data[key]):.2f}"
                    padsplit_expenses.append([
                        Paragraph(label + ":", label_style),
                        Paragraph(value, value_style)
                    ])
            
            # Add platform fee
            platform_pct = self._parse_percentage(self.data.get('padsplit_platform_percentage', 0))
            if platform_pct > 0:
                monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
                platform_fee = monthly_rent * platform_pct / 100
                padsplit_expenses.append([
                    Paragraph("Platform Fee:", label_style),
                    Paragraph(f"({platform_pct:.1f}%) ${platform_fee:.2f}", value_style)
                ])
        
        # Percentage-based expenses
        monthly_rent = self._parse_currency(self.data.get('monthly_rent', 0))
        
        for key, label, pct_key in [
            ('management_fee', 'Management', 'management_fee_percentage'),
            ('capex', 'CapEx', 'capex_percentage'),
            ('vacancy', 'Vacancy', 'vacancy_percentage'),
            ('repairs', 'Repairs', 'repairs_percentage')
        ]:
            pct = self._parse_percentage(self.data.get(pct_key, 0))
            if pct > 0:
                amount = monthly_rent * pct / 100
                percentage_expenses.append([
                    Paragraph(label + ":", label_style),
                    Paragraph(f"({pct:.1f}%) ${amount:.2f}", value_style)
                ])
        
        # Combine all expenses with category headers
        table_data = []
        
        # Fixed expenses
        if fixed_expenses:
            table_data.extend(fixed_expenses)
        
        # PadSplit expenses
        if padsplit_expenses:
            if fixed_expenses:  # Add separator if needed
                table_data.append([
                    Paragraph("PadSplit Expenses:", category_style),
                    Paragraph("", value_style)
                ])
            table_data.extend(padsplit_expenses)
        
        # Percentage expenses
        if percentage_expenses:
            if fixed_expenses or padsplit_expenses:  # Add separator if needed
                table_data.append([
                    Paragraph("Variable Expenses:", category_style),
                    Paragraph("", value_style)
                ])
            table_data.extend(percentage_expenses)
        
        # Create and style the table
        if table_data:
            # Calculate column widths
            col1_width = min(1.6*inch, (self.doc.width/2 - 0.2*inch) * 0.6)
            col2_width = (self.doc.width/2 - 0.2*inch) - col1_width
            
            # Create alternating row colors and style category headers
            row_styles = []
            category_styles = []
            
            for i, row in enumerate(table_data):
                if i % 2 == 1 and not (isinstance(row[0], Paragraph) and "Expenses:" in row[0].text):
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
                
                if isinstance(row[0], Paragraph) and "Expenses:" in row[0].text:
                    category_styles.append(('LINEABOVE', (0, i), (-1, i), 0.5, colors['border_light']))
                    category_styles.append(('BACKGROUND', (0, i), (0, i), colors['table_header']))
            
            expenses_table = Table(
                table_data,
                colWidths=[col1_width, col2_width],
                style=TableStyle([
                    # Label styling - left column
                    ('BACKGROUND', (0, 0), (0, -1), colors['table_header']),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    
                    # Value styling - right column
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    
                    # Grid and borders
                    ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Padding
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ] + row_styles + category_styles)
            )
            
            # Apply table border
            expenses_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
            ]))
            
            elements.append(expenses_table)
        else:
            # No data available
            elements.append(Paragraph("No operating expenses available", self.styles['BrandNormal']))
        
        return elements
    
    def _has_loan(self, prefix):
        """Check if a loan with the given prefix exists and has a non-zero amount."""
        amount = self._parse_currency(self.data.get(f'{prefix}_loan_amount', 0))
        return amount > 0

    def _create_loan_table(self, title, prefix, special_styling=None):
        """Create a loan details table with appropriate styling."""
        colors = BRAND_CONFIG['colors']
        
        # Determine header color based on loan type
        header_color = colors['primary']
        if special_styling == 'hard_money':
            header_color = colors['warning']
        elif special_styling == 'refinance':
            header_color = colors['success']
        elif special_styling == 'balloon_pre':
            header_color = colors['tertiary']
        
        # Define styles
        header_style = ParagraphStyle(
            name='LoanHeader',
            parent=self.styles['TableHeader'],
            fontSize=9,
            textColor=colors['background'],
            alignment=1  # Center aligned
        )
        
        label_style = ParagraphStyle(
            name='LoanLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='LoanValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        value_bold_style = ParagraphStyle(
            name='LoanValueBold',
            parent=value_style,
            fontName=BRAND_CONFIG['fonts']['primary']
        )
        
        # Create table data
        table_data = [
            [Paragraph(title, header_style)]
        ]
        
        # Check if we have loan amount
        amount = self._parse_currency(self.data.get(f'{prefix}_loan_amount', 0))
        if amount <= 0:
            return Paragraph(f"No data for {title}", self.styles['BrandNormal'])
        
        # Add loan details
        table_data.extend([
            [Paragraph("Amount:", label_style),
            Paragraph(f"${amount:,.2f}", value_bold_style)],
            
            [Paragraph("Interest Rate:", label_style),
            Paragraph(f"{self._parse_percentage(self.data.get(f'{prefix}_loan_interest_rate', 0)):.2f}%", value_style)],
            
            [Paragraph("Term:", label_style),
            Paragraph(f"{int(self.data.get(f'{prefix}_loan_term', 0))} months", value_style)],
            
            [Paragraph("Monthly Payment:", label_style),
            Paragraph(self.data.get('calculated_metrics', {}).get(f'{prefix}_loan_payment', '$0.00'), value_bold_style)]
        ])
        
        # Add interest only flag
        is_interest_only = self.data.get(f'{prefix}_interest_only', False)
        interest_style = value_bold_style if is_interest_only else value_style
        table_data.append([
            Paragraph("Interest Only:", label_style),
            Paragraph("Yes" if is_interest_only else "No", interest_style)
        ])
        
        # Add down payment and closing costs
        table_data.extend([
            [Paragraph("Down Payment:", label_style),
            Paragraph(f"${self._parse_currency(self.data.get(f'{prefix}_loan_down_payment', 0)):,.2f}", value_style)],
            
            [Paragraph("Closing Costs:", label_style),
            Paragraph(f"${self._parse_currency(self.data.get(f'{prefix}_loan_closing_costs', 0)):,.2f}", value_style)]
        ])
        
        # Calculate column widths
        col1_width = min(1.6*inch, (self.doc.width/2 - 0.2*inch) * 0.6)
        col2_width = (self.doc.width/2 - 0.2*inch) - col1_width
        
        # Create alternating row colors
        row_styles = []
        for i in range(1, len(table_data)):  # Skip header row
            if i % 2 == 1:  # Alternate rows
                row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
        
        # Create table with styling
        loan_table = Table(
            table_data,
            colWidths=[col1_width, col2_width],
            style=TableStyle([
                # Header styling
                ('SPAN', (0, 0), (1, 0)),  # Span header across columns
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Center header
                ('BACKGROUND', (0, 0), (1, 0), header_color),  # Custom header background
                ('TEXTCOLOR', (0, 0), (1, 0), colors['background']),  # Header text color
                
                # Content styling
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align labels
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Right align values
                ('BACKGROUND', (0, 1), (0, -1), colors['table_header']),  # Label background
                
                # Grid and borders
                ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ] + row_styles)
        )
        
        # Apply table border
        loan_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
        ]))
        
        return loan_table

    def _create_balloon_summary(self):
        """Create a balloon payment summary table."""
        colors = BRAND_CONFIG['colors']
        
        # Define styles
        header_style = ParagraphStyle(
            name='BalloonHeader',
            parent=self.styles['TableHeader'],
            fontSize=9,
            textColor=colors['background'],
            alignment=1  # Center aligned
        )
        
        label_style = ParagraphStyle(
            name='BalloonLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='BalloonValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        # Calculate total monthly payment
        total_payment = 0
        for i in range(1, 4):
            prefix = f'loan{i}'
            if self._has_loan(prefix):
                payment_str = self.data.get('calculated_metrics', {}).get(f'{prefix}_loan_payment', '0')
                total_payment += self._parse_currency(payment_str)
        
        # Create data for balloon summary
        table_data = [
            [Paragraph("Balloon Payment Summary", header_style)],
            [Paragraph("Total Monthly Payment:", label_style),
            Paragraph(f"${total_payment:,.2f}", value_style)],
            [Paragraph("Balloon Due Date:", label_style),
            Paragraph(self.data.get('balloon_due_date', 'N/A'), value_style)]
        ]
        
        # Calculate column widths
        col1_width = min(1.6*inch, (self.doc.width/2 - 0.2*inch) * 0.6)
        col2_width = (self.doc.width/2 - 0.2*inch) - col1_width
        
        # Create table with styling
        balloon_table = Table(
            table_data,
            colWidths=[col1_width, col2_width],
            style=TableStyle([
                # Header styling
                ('SPAN', (0, 0), (1, 0)),  # Span header across columns
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Center header
                ('BACKGROUND', (0, 0), (1, 0), colors['warning']),  # Warning color for balloon
                ('TEXTCOLOR', (0, 0), (1, 0), colors['background']),  # Header text color
                
                # Content styling
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align labels
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Right align values
                ('BACKGROUND', (0, 1), (0, -1), colors['table_header']),  # Label background
                
                # Highlight due date
                ('BACKGROUND', (0, 2), (0, 2), colors['table_header']),
                
                # Grid and borders
                ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ])
        )
        
        # Apply table border
        balloon_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
        ]))
        
        return balloon_table

    def _create_balloon_refinance_table(self):
        """Create a refinance details table for balloon payment."""
        colors = BRAND_CONFIG['colors']
        
        # Define styles
        header_style = ParagraphStyle(
            name='RefinanceHeader',
            parent=self.styles['TableHeader'],
            fontSize=9,
            textColor=colors['background'],
            alignment=1  # Center aligned
        )
        
        label_style = ParagraphStyle(
            name='RefinanceLabel',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=0  # Left aligned
        )
        
        value_style = ParagraphStyle(
            name='RefinanceValue',
            parent=self.styles['BrandNormal'],
            fontSize=8,
            textColor=colors['text_dark'],
            alignment=2  # Right aligned
        )
        
        value_bold_style = ParagraphStyle(
            name='RefinanceValueBold',
            parent=value_style,
            fontName=BRAND_CONFIG['fonts']['primary']
        )
        
        # Create data for refinance details
        table_data = [
            [Paragraph("Balloon Refinance Details", header_style)],
            [Paragraph("Refinance Amount:", label_style),
            Paragraph(f"${self._parse_currency(self.data.get('balloon_refinance_loan_amount', 0)):,.2f}", value_bold_style)],
            [Paragraph("Interest Rate:", label_style),
            Paragraph(f"{self._parse_percentage(self.data.get('balloon_refinance_loan_interest_rate', 0)):.2f}%", value_style)],
            [Paragraph("Term:", label_style),
            Paragraph(f"{int(self.data.get('balloon_refinance_loan_term', 0))} months", value_style)],
            [Paragraph("Monthly Payment:", label_style),
            Paragraph(self.data.get('calculated_metrics', {}).get('post_balloon_monthly_payment', '$0.00'), value_bold_style)],
            [Paragraph("LTV Percentage:", label_style),
            Paragraph(f"{self._parse_percentage(self.data.get('balloon_refinance_ltv_percentage', 0)):.1f}%", value_style)],
            [Paragraph("Down Payment:", label_style),
            Paragraph(f"${self._parse_currency(self.data.get('balloon_refinance_loan_down_payment', 0)):,.2f}", value_style)],
            [Paragraph("Closing Costs:", label_style),
            Paragraph(f"${self._parse_currency(self.data.get('balloon_refinance_loan_closing_costs', 0)):,.2f}", value_style)]
        ]
        
        # Calculate column widths
        col1_width = min(1.6*inch, (self.doc.width/2 - 0.2*inch) * 0.6)
        col2_width = (self.doc.width/2 - 0.2*inch) - col1_width
        
        # Create alternating row colors
        row_styles = []
        for i in range(1, len(table_data)):  # Skip header row
            if i % 2 == 1:  # Alternate rows
                row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
        
        # Create table with styling
        refinance_table = Table(
            table_data,
            colWidths=[col1_width, col2_width],
            style=TableStyle([
                # Header styling
                ('SPAN', (0, 0), (1, 0)),  # Span header across columns
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Center header
                ('BACKGROUND', (0, 0), (1, 0), colors['success']),  # Success color for refinance
                ('TEXTCOLOR', (0, 0), (1, 0), colors['background']),  # Header text color
                
                # Content styling
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align labels
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Right align values
                ('BACKGROUND', (0, 1), (0, -1), colors['table_header']),  # Label background
                
                # Grid and borders
                ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors['border_light']),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ] + row_styles)
        )
        
        # Apply table border
        refinance_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors['border_light']),
        ]))
        
        return refinance_table

    def create_property_comps_section(self):
        """Create property comps section with comparable properties."""
        elements = []
        colors = BRAND_CONFIG['colors']
        
        # Add section header
        elements.append(Paragraph("Property Comparables", self.styles['BrandHeading3']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Get comps data
        comps_data = self.data.get('comps_data', {})
        comparables = comps_data.get('comparables', [])
        
        if comparables and len(comparables) > 0:
            # Create summary of comps estimates
            estimated_value = comps_data.get('estimated_value', 0)
            value_range_low = comps_data.get('value_range_low', 0)
            value_range_high = comps_data.get('value_range_high', 0)
            
            summary_style = ParagraphStyle(
                name='CompsSummary',
                parent=self.styles['BrandNormal'],
                fontSize=9,
                textColor=colors['text_dark'],
                alignment=0  # Left aligned
            )
            
            value_style = ParagraphStyle(
                name='CompsValue',
                parent=self.styles['BrandNormal'],
                fontSize=9,
                textColor=colors['primary'],
                fontName=BRAND_CONFIG['fonts']['primary'],
                alignment=0  # Left aligned
            )
            
            # Add estimated value and range
            elements.append(Paragraph(f"Estimated Value: <b>${estimated_value:,}</b>", summary_style))
            elements.append(Paragraph(f"Value Range: ${value_range_low:,} - ${value_range_high:,}", summary_style))
            elements.append(Spacer(1, 0.1*inch))
            
            # Create comparables table
            table_data = []
            
            # Create header row
            header_style = ParagraphStyle(
                name='CompsHeader',
                parent=self.styles['TableHeader'],
                fontSize=8,
                textColor=colors['background'],
                alignment=1  # Center aligned
            )
            
            # Define columns
            headers = [
                'Address',
                'Price',
                'Bed/Bath',
                'Sq Ft',
                'Year',
                'Distance',
                'Date Sold'
            ]
            
            # Add header row
            table_data.append([Paragraph(h, header_style) for h in headers])
            
            # Cell styles
            cell_style = ParagraphStyle(
                name='CompsCell',
                parent=self.styles['BrandNormal'],
                fontSize=7,
                textColor=colors['text_dark'],
                alignment=0  # Left aligned
            )
            
            price_style = ParagraphStyle(
                name='CompsPrice',
                parent=cell_style,
                alignment=2  # Right aligned
            )
            
            numeric_style = ParagraphStyle(
                name='CompsNumeric',
                parent=cell_style,
                alignment=1  # Center aligned
            )
            
            # Add data rows - limit to 10 comps max to fit on page
            max_comps = min(len(comparables), 10)
            for i in range(max_comps):
                comp = comparables[i]
                
                # Format address - keep it short to fit in table
                address = comp.get('formattedAddress', '')
                short_address = self._get_short_address(address)
                
                # Format date
                listed_date = comp.get('listedDate', '')
                date_display = ''
                if listed_date:
                    try:
                        if 'T' in listed_date:
                            date_obj = datetime.fromisoformat(listed_date.replace('Z', '+00:00'))
                            date_display = date_obj.strftime('%m/%d/%Y')
                        else:
                            date_obj = datetime.strptime(listed_date, '%Y-%m-%d')
                            date_display = date_obj.strftime('%m/%d/%Y')
                    except (ValueError, TypeError):
                        date_display = listed_date
                
                # Add row
                table_data.append([
                    Paragraph(short_address, cell_style),
                    Paragraph(f"${comp.get('price', 0):,}", price_style),
                    Paragraph(f"{comp.get('bedrooms', 0)}/{comp.get('bathrooms', 0)}", numeric_style),
                    Paragraph(f"{comp.get('squareFootage', 0):,}", numeric_style),
                    Paragraph(f"{comp.get('yearBuilt', '')}", numeric_style),
                    Paragraph(f"{comp.get('distance', 0):.1f} mi", numeric_style),
                    Paragraph(date_display, numeric_style)
                ])
            
            # Calculate column widths based on content
            table_width = self.doc.width
            col_widths = [
                table_width * 0.30,  # Address
                table_width * 0.15,  # Price
                table_width * 0.10,  # Bed/Bath
                table_width * 0.10,  # Sq Ft
                table_width * 0.10,  # Year
                table_width * 0.10,  # Distance
                table_width * 0.15   # Date Sold
            ]
            
            # Create alternating row colors
            row_styles = []
            for i in range(1, len(table_data)):  # Skip header row
                if i % 2 == 1:  # Alternate rows
                    row_styles.append(('BACKGROUND', (0, i), (-1, i), colors['table_row_alt']))
            
            # Create table with styling
            comps_table = Table(
                table_data,
                colWidths=col_widths,
                style=TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors['primary']),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors['background']),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    
                    # Content styling
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),     # Left align address
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),    # Right align price
                    ('ALIGN', (2, 1), (-1, -1), 'CENTER'),  # Center everything else
                    
                    # Grid and borders
                    ('GRID', (0, 0), (-1, -1), 0.25, colors['border_light']),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Padding for breathing room
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ] + row_styles)
            )
            
            elements.append(comps_table)
            
            # Add note about comps
            elements.append(Spacer(1, 0.05*inch))
            note_text = (
                f"Based on {len(comparables)} comparable properties within the area. "
                f"Last updated: {comps_data.get('last_run', 'N/A')}"
            )
            elements.append(Paragraph(note_text, self.styles['BrandSmall']))
            
        else:
            # No comps available
            elements.append(Paragraph("No comparable properties available. Run comps in the application to include them in this report.", 
                                    self.styles['BrandNormal']))
        
        return elements