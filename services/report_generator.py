from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, 
                               TableStyle, Image, BaseDocTemplate, PageTemplate, 
                               Frame, FrameBreak, PageBreak, KeepTogether)
from typing import Dict, List, Optional, Union
from io import BytesIO
from flask import current_app
import logging
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Base class for generating PDF reports from structured data."""
    
    def __init__(self, data: Dict, buffer: BytesIO, landscape_mode: bool = False):
        self.data = data
        self.buffer = buffer
        self.landscape_mode = landscape_mode
        self.styles = self._create_styles()
        self.pagesize = landscape(letter) if landscape_mode else letter
        self.margins = {
            'left': 0.75*inch,
            'right': 0.75*inch,
            'top': 0.75*inch,
            'bottom': 0.75*inch
        }

    def _create_styles(self) -> Dict:
        """Create standardized styles for the report"""
        styles = getSampleStyleSheet()
        
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
            alignment=TA_LEFT
        ))
        
        return styles

    def _create_header(self) -> Table:
        """Create report header with logo and title."""
        try:
            logo_path = os.path.join(current_app.static_folder, 'images', 'logo-blue.png')
            
            if 'analysis_name' in self.data:
                # Analysis report header
                title = self.data.get('analysis_name', 'Analysis Report')
                subtitle = f"{self.data.get('analysis_type', 'Analysis')}"
                date = self.data.get('generated_date', datetime.now().strftime("%Y-%m-%d"))
            else:
                # Transaction report header
                title = "Transaction Report"
                subtitle = f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
                date = self.data.get('date_range', 'All Time')

            if not os.path.exists(logo_path):
                logger.warning(f"Logo file not found at {logo_path}")
                header_data = [
                    [Paragraph(title, self.styles['Header'])],
                    [Paragraph(f"{subtitle}<br/>{date}", self.styles['SubTitle'])]
                ]
                header_table = Table(header_data, colWidths=[7*inch])
            else:
                img = Image(logo_path, width=0.75*inch, height=0.75*inch)
                header_data = [
                    [img, Paragraph(title, self.styles['Header'])],
                    [None, Paragraph(f"{subtitle}<br/>{date}", self.styles['SubTitle'])]
                ]
                header_table = Table(header_data, colWidths=[1*inch, 6*inch])

            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('SPAN', (0, 0), (0, 1))
            ]))

            return header_table
        except Exception as e:
            logger.error(f"Error creating header: {str(e)}")
            return Paragraph("Report", self.styles['Header'])

    def _create_table(self, title: str, data: List[tuple[str, str]], column_widths: Optional[List[float]] = None) -> Table:
        """Create a formatted table with data."""
        if not column_widths:
            column_widths = [3*inch, 2*inch]

        table_data = [[Paragraph(title, self.styles['TableHeader']), '']]
        
        for label, value in data:
            table_data.append([
                Paragraph(str(label), self.styles['Normal']),
                Paragraph(str(value), self.styles['Normal'])
            ])
        
        table = Table(table_data, colWidths=column_widths)
        
        style = [
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('SPAN', (0, 0), (1, 0)),
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#000080')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]
        
        for i in range(1, len(table_data), 2):
            style.append(('BACKGROUND', (0, i), (1, i), colors.lightgrey))
            
        table.setStyle(TableStyle(style))
        return table

    def _create_transaction_table(self, title: str, transactions: List[Dict]) -> Table:
        """Create transaction table for transaction reports."""
        headers = ['Date', 'Description', 'Type', 'Category', 'Amount']
        data = [headers]
        
        col_widths = [1.5*inch, 4*inch, 1.5*inch, 2*inch, 1.5*inch]
        
        for t in transactions:
            data.append([
                t['date'],
                t['description'],
                t['type'].title(),
                t['category'],
                t['amount']
            ])
        
        table = Table(data, colWidths=col_widths)
        
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000080')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]
        
        table.setStyle(TableStyle(style))
        return table

    def _add_content(self, story: List) -> None:
        """Add report content based on report type."""
        story.append(self._create_header())
        story.append(Spacer(1, 0.25*inch))

        if 'sections' in self.data:
            # Analysis report content
            col_width = (self.pagesize[0] - sum(self.margins.values())) / 2 - 0.125*inch
            
            for i, section in enumerate(self.data['sections']):
                table = self._create_table(
                    section['title'],
                    section['data'],
                    column_widths=[col_width * 0.6, col_width * 0.4]
                )
                story.append(table)
                
                if i < len(self.data['sections']) - 1:
                    story.append(Spacer(1, 0.25*inch))
                
                if i % 2 == 1 and i < len(self.data['sections']) - 1:
                    story.append(FrameBreak())
        else:
            # Transaction report content
            if 'transactions' in self.data:
                for property_id, transactions in self.data['transactions'].items():
                    story.append(self._create_transaction_table(
                        f"Transactions - {property_id}",
                        transactions
                    ))
                    story.append(Spacer(1, 0.25*inch))

    def _add_page_number(self, canvas, doc):
        """Add page number to each page."""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(
            self.pagesize[0] - self.margins['right'],
            self.margins['bottom'] / 2,
            text
        )
        canvas.restoreState()

    def generate(self) -> None:
        """Generate the complete report."""
        doc = BaseDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            rightMargin=self.margins['right'],
            leftMargin=self.margins['left'],
            topMargin=self.margins['top'],
            bottomMargin=self.margins['bottom']
        )
        
        header_height = 1.25*inch
        content_width = doc.width / 2 - 0.125*inch
        content_height = doc.height - header_height - 0.5*inch
        
        header_frame = Frame(
            doc.leftMargin,
            doc.height - header_height,
            doc.width,
            header_height,
            id='header'
        )
        
        left_frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            content_width,
            content_height,
            id='left'
        )
        
        right_frame = Frame(
            doc.leftMargin + content_width + 0.25*inch,
            doc.bottomMargin,
            content_width,
            content_height,
            id='right'
        )
        
        template = PageTemplate(
            id='normal',
            frames=[header_frame, left_frame, right_frame],
            onPage=self._add_page_number
        )
        doc.addPageTemplates([template])
        
        story = []
        self._add_content(story)
        doc.build(story)

def generate_report(data: Dict, report_type: str = 'analysis') -> BytesIO:
    """Generate appropriate PDF report based on type."""
    buffer = BytesIO()
    is_landscape = report_type == 'transaction'
    report = ReportGenerator(data, buffer, landscape_mode=is_landscape)
    report.generate()
    buffer.seek(0)
    return buffer