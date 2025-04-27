"""
Transaction report generator module for the REI-Tracker application.

This module provides functionality for generating transaction reports in PDF format
and creating ZIP archives of transaction documentation.
"""

import io
import os
import logging
import zipfile
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, ListFlowable, ListItem, Flowable
)

from src.config import current_config
from src.services.file_service import FileService

# Set up logger
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
    }
}


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


class TransactionReportGenerator:
    """
    Service for generating transaction reports in PDF format and creating
    ZIP archives of transaction documentation.
    
    This class provides methods for creating summary and detailed transaction
    reports with customizable formatting, visualizations, and documentation references.
    """
    
    def __init__(self):
        """Initialize the transaction report generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.file_service = FileService()
    
    def _setup_custom_styles(self):
        """Set up custom styles for the report."""
        brand_colors = BRAND_CONFIG['colors']
        
        # Title style
        self.styles.add(
            ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Title'],
                fontName=BRAND_CONFIG['fonts']['primary'],
                fontSize=16,
                textColor=brand_colors['primary'],
                spaceAfter=12
            )
        )
        
        # Heading style
        self.styles.add(
            ParagraphStyle(
                name='CustomHeading',
                parent=self.styles['Heading2'],
                fontName=BRAND_CONFIG['fonts']['primary'],
                fontSize=14,
                textColor=brand_colors['primary'],
                spaceAfter=10
            )
        )
        
        # Normal text style
        self.styles.add(
            ParagraphStyle(
                name='CustomNormal',
                parent=self.styles['Normal'],
                fontName=BRAND_CONFIG['fonts']['secondary'],
                fontSize=10,
                textColor=brand_colors['text_dark'],
                spaceAfter=6
            )
        )
        
        # Table header style
        self.styles.add(
            ParagraphStyle(
                name='TableHeader',
                parent=self.styles['Normal'],
                fontName=BRAND_CONFIG['fonts']['primary'],
                fontSize=10,
                alignment=1,  # Center alignment
                textColor=colors.white  # Using reportlab.lib.colors directly
            )
        )
        
        # Small text style
        self.styles.add(
            ParagraphStyle(
                name='SmallText',
                parent=self.styles['Normal'],
                fontName=BRAND_CONFIG['fonts']['secondary'],
                fontSize=8,
                textColor=brand_colors['text_light'],
                spaceAfter=3
            )
        )
        
        # Document reference style
        self.styles.add(
            ParagraphStyle(
                name='DocumentReference',
                parent=self.styles['Normal'],
                fontName=BRAND_CONFIG['fonts']['secondary'],
                fontSize=9,
                textColor=brand_colors['tertiary'],
                spaceAfter=3
            )
        )
    
    def _add_page_decorations(self, canvas, doc):
        """Add page number, footer line, and logo (first page only)."""
        canvas.saveState()
        brand_colors = BRAND_CONFIG['colors']
        
        # Draw the footer with page number
        canvas.setFont(BRAND_CONFIG['fonts']['primary'], 8)
        canvas.setFillColor(brand_colors['text_light'])
        canvas.drawRightString(
            doc.pagesize[0] - 0.5*inch,
            0.25*inch,
            f"Page {doc.page}"
        )
        
        # Add a thin footer line
        canvas.setStrokeColor(brand_colors['primary'])
        canvas.setLineWidth(0.5)
        canvas.line(
            doc.leftMargin, 
            0.45*inch, 
            doc.pagesize[0] - doc.rightMargin, 
            0.45*inch
        )
        
        # Draw logo only on first page
        if doc.page == 1:
            try:
                logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'logo.png')
                if os.path.exists(logo_path):
                    canvas.drawImage(
                        logo_path,
                        doc.pagesize[0] - doc.rightMargin - 1.5*inch,
                        doc.pagesize[1] - doc.topMargin - 0.75*inch,
                        width=1.5*inch,
                        height=0.75*inch,
                        preserveAspectRatio=True,
                        mask='auto'  # This makes white background transparent
                    )
            except Exception as e:
                logger.warning(f"Could not add logo to report: {str(e)}")
        
        canvas.restoreState()
    
    def generate(
        self, 
        transactions: List[Dict[str, Any]], 
        output_buffer: io.BytesIO,
        metadata: Dict[str, Any]
    ) -> None:
        """
        Generate a transaction report.
        
        Args:
            transactions: List of transactions to include in the report
            output_buffer: Buffer to write the PDF to
            metadata: Report metadata (title, date range, property, etc.)
        """
        try:
            # Create document
            doc = SimpleDocTemplate(
                output_buffer,
                pagesize=landscape(letter),
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Create story (content)
            story = []
            
            # Add title and metadata
            self._add_title_section(story, metadata)
            
            # Add summary section with visualizations
            summary_data = self._process_summary_data(transactions)
            self._add_summary_section(story, summary_data)
            
            # Add financial visualizations
            self._add_financial_visualizations(story, summary_data)
            
            # Add transactions table
            self._add_transactions_table(story, transactions)
            
            # Add documentation references if any transactions have documentation
            self._add_documentation_references(story, transactions)
            
            # Build document with page decorations
            doc.build(story, onFirstPage=self._add_page_decorations, onLaterPages=self._add_page_decorations)
            
        except Exception as e:
            logger.error(f"Error generating transaction report: {str(e)}")
            raise
    
    def _add_title_section(self, story: List, metadata: Dict[str, Any]) -> None:
        """
        Add title section to the report.
        
        Args:
            story: ReportLab story to add content to
            metadata: Report metadata
        """
        # Add title
        title = metadata.get("title", "Transaction Report")
        story.append(Paragraph(title, self.styles["CustomTitle"]))
        
        # Add metadata
        property_name = metadata.get("property_name", "All Properties")
        date_range = metadata.get("date_range", "All Dates")
        
        metadata_text = f"Property: {property_name}<br/>Date Range: {date_range}"
        if "generated_by" in metadata:
            metadata_text += f"<br/>Generated By: {metadata['generated_by']}"
        
        metadata_text += f"<br/>Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        story.append(Paragraph(metadata_text, self.styles["CustomNormal"]))
        story.append(Spacer(1, 0.2*inch))
    
    def _process_summary_data(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process transaction data to create summary information.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Dictionary with summary data
        """
        # Initialize summary data
        summary = {
            "total_income": Decimal("0.00"),
            "total_expense": Decimal("0.00"),
            "net_amount": Decimal("0.00"),
            "income_by_category": {},
            "expense_by_category": {},
            "property_summary": {}
        }
        
        # Process each transaction
        for transaction in transactions:
            amount = Decimal(str(transaction["amount"]))
            category = transaction["category"]
            property_id = transaction["property_id"]
            transaction_type = transaction["type"]
            
            # Update totals
            if transaction_type == "income":
                summary["total_income"] += amount
                
                # Update income by category
                if category not in summary["income_by_category"]:
                    summary["income_by_category"][category] = Decimal("0.00")
                summary["income_by_category"][category] += amount
                
            else:  # expense
                summary["total_expense"] += amount
                
                # Update expense by category
                if category not in summary["expense_by_category"]:
                    summary["expense_by_category"][category] = Decimal("0.00")
                summary["expense_by_category"][category] += amount
            
            # Update property summary
            if property_id not in summary["property_summary"]:
                summary["property_summary"][property_id] = {
                    "income": Decimal("0.00"),
                    "expense": Decimal("0.00"),
                    "net": Decimal("0.00")
                }
            
            if transaction_type == "income":
                summary["property_summary"][property_id]["income"] += amount
            else:
                summary["property_summary"][property_id]["expense"] += amount
            
            summary["property_summary"][property_id]["net"] = (
                summary["property_summary"][property_id]["income"] - 
                summary["property_summary"][property_id]["expense"]
            )
        
        # Calculate net amount
        summary["net_amount"] = summary["total_income"] - summary["total_expense"]
        
        return summary
    
    def _add_summary_section(self, story: List, summary_data: Dict[str, Any]) -> None:
        """
        Add summary section to the report.
        
        Args:
            story: ReportLab story to add content to
            summary_data: Summary data
        """
        # Add summary heading
        story.append(Paragraph("Financial Summary", self.styles["CustomHeading"]))
        
        # Add overall summary
        total_income = f"${summary_data['total_income']:.2f}"
        total_expense = f"${summary_data['total_expense']:.2f}"
        net_amount = f"${summary_data['net_amount']:.2f}"
        
        overall_data = [
            ["Total Income", "Total Expense", "Net Amount"],
            [total_income, total_expense, net_amount]
        ]
        
        overall_table = Table(overall_data, colWidths=[2*inch, 2*inch, 2*inch])
        overall_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(overall_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add property summary if multiple properties
        if len(summary_data["property_summary"]) > 1:
            story.append(Paragraph("Property Summary", self.styles["CustomHeading"]))
            
            # Create property summary table
            property_data = [["Property", "Income", "Expense", "Net"]]
            
            for property_id, values in summary_data["property_summary"].items():
                property_data.append([
                    property_id,
                    f"${values['income']:.2f}",
                    f"${values['expense']:.2f}",
                    f"${values['net']:.2f}"
                ])
            
            property_table = Table(property_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            property_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            story.append(property_table)
            story.append(Spacer(1, 0.2*inch))
        
        # Add category breakdowns
        story.append(Paragraph("Category Breakdown", self.styles["CustomHeading"]))
        
        # Create category tables
        income_data = [["Income Category", "Amount"]]
        for category, amount in sorted(
            summary_data["income_by_category"].items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            income_data.append([category, f"${amount:.2f}"])
        
        expense_data = [["Expense Category", "Amount"]]
        for category, amount in sorted(
            summary_data["expense_by_category"].items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            expense_data.append([category, f"${amount:.2f}"])
        
        # Create tables side by side
        income_table = Table(income_data, colWidths=[2.5*inch, 1.5*inch])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        expense_table = Table(expense_data, colWidths=[2.5*inch, 1.5*inch])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        category_tables = Table([[income_table, expense_table]], colWidths=[4.5*inch, 4.5*inch])
        category_tables.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(category_tables)
        story.append(Spacer(1, 0.3*inch))
    
    def _add_transactions_table(self, story: List, transactions: List[Dict[str, Any]]) -> None:
        """
        Add transactions table to the report.
        
        Args:
            story: ReportLab story to add content to
            transactions: List of transactions
        """
        # Add transactions heading
        story.append(Paragraph("Transaction Details", self.styles["CustomHeading"]))
        
        # Define table headers
        headers = [
            "Date", "Property", "Type", "Category", 
            "Description", "Amount", "Collector/Payer", "Status"
        ]
        
        # Create table data
        data = [headers]
        
        # Add transaction rows
        for transaction in sorted(transactions, key=lambda x: x["date"]):
            # Format amount with currency symbol
            amount = f"${float(transaction['amount']):.2f}"
            
            # Determine status
            if transaction.get("reimbursement"):
                status = transaction["reimbursement"].get("reimbursement_status", "pending")
                status = status.replace("_", " ").title()
            else:
                status = "N/A"
            
            # Add row
            data.append([
                transaction["date"],
                transaction["property_id"],
                transaction["type"].title(),
                transaction["category"],
                transaction["description"],
                amount,
                transaction["collector_payer"],
                status
            ])
        
        # Create table
        col_widths = [0.8*inch, 2*inch, 0.8*inch, 1.2*inch, 2.5*inch, 0.8*inch, 1.2*inch, 0.8*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data style
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),  # Amount column right-aligned
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Date column centered
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Type column centered
            ('ALIGN', (7, 1), (7, -1), 'CENTER'),  # Status column centered
            
            # Grid style
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        # Add table to story
        story.append(table)
    
    def _add_financial_visualizations(self, story: List, summary_data: Dict[str, Any]) -> None:
        """
        Add financial visualizations to the report.
        
        Args:
            story: ReportLab story to add content to
            summary_data: Summary data
        """
        # Add visualizations heading
        story.append(Paragraph("Financial Visualizations", self.styles["CustomHeading"]))
        
        # Create income/expense pie chart
        if summary_data["total_income"] > 0 or summary_data["total_expense"] > 0:
            pie_chart_buffer = self._create_income_expense_pie_chart(summary_data)
            story.append(Image(pie_chart_buffer, width=4*inch, height=3*inch))
            story.append(Spacer(1, 0.1*inch))
        
        # Create category breakdown chart if we have categories
        if summary_data["income_by_category"] or summary_data["expense_by_category"]:
            category_chart_buffer = self._create_category_breakdown_chart(summary_data)
            story.append(Image(category_chart_buffer, width=6*inch, height=3*inch))
            story.append(Spacer(1, 0.1*inch))
        
        # Create property comparison chart if we have multiple properties
        if len(summary_data["property_summary"]) > 1:
            property_chart_buffer = self._create_property_comparison_chart(summary_data)
            story.append(Image(property_chart_buffer, width=6*inch, height=3*inch))
        
        story.append(Spacer(1, 0.3*inch))
    
    def _create_income_expense_pie_chart(self, summary_data: Dict[str, Any]) -> io.BytesIO:
        """
        Create a pie chart showing income vs. expense.
        
        Args:
            summary_data: Summary data
            
        Returns:
            BytesIO buffer containing the chart image
        """
        buffer = io.BytesIO()
        brand_colors = BRAND_CONFIG['colors']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        
        # Set background color
        fig.patch.set_facecolor('#FFFFFF')
        
        # Data for pie chart
        labels = ['Income', 'Expense']
        sizes = [float(summary_data['total_income']), float(summary_data['total_expense'])]
        
        # Skip empty values
        data = [(label, size) for label, size in zip(labels, sizes) if size > 0]
        if data:
            labels, sizes = zip(*data)
        else:
            labels, sizes = ['No Data'], [1]
        
        # Colors for pie chart
        pie_colors = [brand_colors['success'], brand_colors['danger']]
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=90,
            colors=pie_colors,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
        )
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Set title
        ax.set_title('Income vs. Expense', fontsize=12, fontweight='bold')
        
        # Style text
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
            autotext.set_color('white')
        
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _create_category_breakdown_chart(self, summary_data: Dict[str, Any]) -> io.BytesIO:
        """
        Create a bar chart showing category breakdown.
        
        Args:
            summary_data: Summary data
            
        Returns:
            BytesIO buffer containing the chart image
        """
        buffer = io.BytesIO()
        brand_colors = BRAND_CONFIG['colors']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        
        # Set background color
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#F9FBFF')
        
        # Prepare data for income categories
        income_categories = []
        income_amounts = []
        
        for category, amount in sorted(
            summary_data["income_by_category"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]:  # Limit to top 5 categories
            income_categories.append(category)
            income_amounts.append(float(amount))
        
        # Prepare data for expense categories
        expense_categories = []
        expense_amounts = []
        
        for category, amount in sorted(
            summary_data["expense_by_category"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]:  # Limit to top 5 categories
            expense_categories.append(category)
            expense_amounts.append(float(amount))
        
        # Set positions for bars
        bar_width = 0.35
        x_income = range(len(income_categories))
        x_expense = [x + len(income_categories) + 1 for x in range(len(expense_categories))]
        
        # Create bars
        income_bars = ax.bar(
            x_income, 
            income_amounts, 
            bar_width, 
            label='Income', 
            color=brand_colors['success'],
            edgecolor='white',
            linewidth=1
        )
        
        expense_bars = ax.bar(
            x_expense, 
            expense_amounts, 
            bar_width, 
            label='Expense', 
            color=brand_colors['danger'],
            edgecolor='white',
            linewidth=1
        )
        
        # Add labels and title
        ax.set_xlabel('Category', fontsize=10, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=10, fontweight='bold')
        ax.set_title('Top Categories by Amount', fontsize=12, fontweight='bold')
        
        # Set x-axis ticks
        ax.set_xticks(list(x_income) + list(x_expense))
        ax.set_xticklabels(income_categories + expense_categories, rotation=45, ha='right')
        
        # Format y-axis as currency
        def currency_formatter(x, pos):
            return f'${x:,.0f}'
        
        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        
        # Add grid
        ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.3)
        
        # Add legend
        ax.legend()
        
        # Add value labels on bars
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f'${height:,.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', 
                    va='bottom',
                    fontsize=8
                )
        
        add_labels(income_bars)
        add_labels(expense_bars)
        
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _create_property_comparison_chart(self, summary_data: Dict[str, Any]) -> io.BytesIO:
        """
        Create a bar chart comparing properties.
        
        Args:
            summary_data: Summary data
            
        Returns:
            BytesIO buffer containing the chart image
        """
        buffer = io.BytesIO()
        brand_colors = BRAND_CONFIG['colors']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
        
        # Set background color
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#F9FBFF')
        
        # Prepare data
        properties = []
        net_amounts = []
        income_amounts = []
        expense_amounts = []
        
        for property_id, values in sorted(
            summary_data["property_summary"].items(),
            key=lambda x: x[1]["net"],
            reverse=True
        ):
            # Truncate property name if too long
            if len(property_id) > 15:
                property_name = property_id[:12] + "..."
            else:
                property_name = property_id
                
            properties.append(property_name)
            net_amounts.append(float(values["net"]))
            income_amounts.append(float(values["income"]))
            expense_amounts.append(float(values["expense"]))
        
        # Set positions for bars
        x = range(len(properties))
        bar_width = 0.25
        
        # Create bars
        income_bars = ax.bar(
            [i - bar_width for i in x], 
            income_amounts, 
            bar_width, 
            label='Income', 
            color=brand_colors['success'],
            edgecolor='white',
            linewidth=1
        )
        
        expense_bars = ax.bar(
            x, 
            expense_amounts, 
            bar_width, 
            label='Expense', 
            color=brand_colors['danger'],
            edgecolor='white',
            linewidth=1
        )
        
        net_bars = ax.bar(
            [i + bar_width for i in x], 
            net_amounts, 
            bar_width, 
            label='Net', 
            color=brand_colors['primary'],
            edgecolor='white',
            linewidth=1
        )
        
        # Add labels and title
        ax.set_xlabel('Property', fontsize=10, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=10, fontweight='bold')
        ax.set_title('Property Financial Comparison', fontsize=12, fontweight='bold')
        
        # Set x-axis ticks
        ax.set_xticks(x)
        ax.set_xticklabels(properties, rotation=45, ha='right')
        
        # Format y-axis as currency
        def currency_formatter(x, pos):
            return f'${x:,.0f}'
        
        ax.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        
        # Add grid
        ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.3)
        
        # Add legend
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _add_documentation_references(self, story: List, transactions: List[Dict[str, Any]]) -> None:
        """
        Add documentation references to the report.
        
        Args:
            story: ReportLab story to add content to
            transactions: List of transactions
        """
        # Filter transactions with documentation
        transactions_with_docs = [t for t in transactions if t.get("documentation_file")]
        
        if not transactions_with_docs:
            return
        
        # Add documentation heading
        story.append(PageBreak())
        story.append(Paragraph("Transaction Documentation", self.styles["CustomHeading"]))
        story.append(Spacer(1, 0.1*inch))
        
        # Add explanation
        story.append(Paragraph(
            "The following transactions have associated documentation files. "
            "These files can be accessed through the system or included in the ZIP archive.",
            self.styles["CustomNormal"]
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Create documentation table
        data = [["Date", "Property", "Description", "Amount", "Documentation"]]
        
        for transaction in sorted(transactions_with_docs, key=lambda x: x["date"]):
            # Format amount with currency symbol
            amount = f"${float(transaction['amount']):.2f}"
            
            # Get documentation filename
            doc_file = transaction.get("documentation_file", "")
            
            # Add row
            data.append([
                transaction["date"],
                transaction["property_id"],
                transaction["description"],
                amount,
                doc_file
            ])
        
        # Create table
        col_widths = [1*inch, 2*inch, 3*inch, 1*inch, 3*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_CONFIG['colors']['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), BRAND_CONFIG['fonts']['primary']),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data style
            ('FONTNAME', (0, 1), (-1, -1), BRAND_CONFIG['fonts']['secondary']),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Amount column right-aligned
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Date column centered
            
            # Grid style
            ('GRID', (0, 0), (-1, -1), 0.5, BRAND_CONFIG['colors']['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_CONFIG['colors']['table_row_alt']]),
        ]))
        
        # Add table to story
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Add note about ZIP archive
        story.append(Paragraph(
            "Note: A separate ZIP archive can be generated containing all documentation files for these transactions.",
            self.styles["SmallText"]
        ))
    
    def generate_zip_archive(
        self, 
        transactions: List[Dict[str, Any]], 
        output_buffer: io.BytesIO
    ) -> None:
        """
        Generate a ZIP archive with transaction documentation.
        
        Args:
            transactions: List of transactions with documentation
            output_buffer: Buffer to write the ZIP archive to
            
        Returns:
            None. The output_buffer will contain the ZIP archive data.
        """
        try:
            # Create ZIP file
            with zipfile.ZipFile(output_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add README file with summary information
                readme_content = self._generate_zip_readme(transactions)
                zip_file.writestr('README.txt', readme_content)
                
                # Add transaction documentation files
                added_files = []
                
                for transaction in transactions:
                    doc_file = transaction.get("documentation_file")
                    if not doc_file:
                        continue
                    
                    try:
                        # Get file path
                        file_path = self.file_service.get_file_path(doc_file)
                        
                        # Create a directory structure based on property and date
                        property_id = transaction["property_id"].replace(" ", "_")
                        date = transaction["date"]
                        
                        # Create a unique filename in case of duplicates
                        base_filename = os.path.basename(file_path)
                        filename = f"{date}_{transaction['id']}_{base_filename}"
                        
                        # Add file to ZIP
                        archive_path = f"{property_id}/{filename}"
                        
                        # Check for duplicate filenames
                        if archive_path in added_files:
                            # Add a counter to make the filename unique
                            counter = 1
                            while f"{archive_path}_{counter}" in added_files:
                                counter += 1
                            archive_path = f"{archive_path}_{counter}"
                        
                        # Add file to ZIP
                        zip_file.write(file_path, archive_path)
                        added_files.append(archive_path)
                        
                    except FileNotFoundError:
                        logger.warning(f"Documentation file not found: {doc_file}")
                    except Exception as e:
                        logger.error(f"Error adding file to ZIP: {str(e)}")
            
            # Reset buffer position
            output_buffer.seek(0)
            
        except Exception as e:
            logger.error(f"Error generating ZIP archive: {str(e)}")
            raise
    
    def _generate_zip_readme(self, transactions: List[Dict[str, Any]]) -> str:
        """
        Generate README content for the ZIP archive.
        
        Args:
            transactions: List of transactions
            
        Returns:
            README content as string
        """
        # Filter transactions with documentation
        transactions_with_docs = [t for t in transactions if t.get("documentation_file")]
        
        # Generate content
        content = "TRANSACTION DOCUMENTATION ARCHIVE\n"
        content += "==============================\n\n"
        content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        content += f"Total transactions: {len(transactions)}\n"
        content += f"Transactions with documentation: {len(transactions_with_docs)}\n\n"
        
        # Add transaction details
        content += "TRANSACTION DETAILS\n"
        content += "------------------\n\n"
        
        for transaction in sorted(transactions_with_docs, key=lambda x: x["date"]):
            content += f"Date: {transaction['date']}\n"
            content += f"Property: {transaction['property_id']}\n"
            content += f"Type: {transaction['type']}\n"
            content += f"Category: {transaction['category']}\n"
            content += f"Description: {transaction['description']}\n"
            content += f"Amount: ${float(transaction['amount']):.2f}\n"
            content += f"Documentation: {transaction.get('documentation_file', 'None')}\n"
            content += "\n"
        
        return content
