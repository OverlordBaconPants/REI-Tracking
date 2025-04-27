"""
KPI comparison report generator module for the REI-Tracker application.

This module provides functionality for generating KPI comparison reports in PDF format,
comparing planned vs. actual metrics for properties.
"""

import io
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, ListFlowable, ListItem, Flowable
)

from src.config import current_config
from src.services.property_financial_service import PropertyFinancialService

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


class KPIComparisonReportGenerator:
    """
    Service for generating KPI comparison reports in PDF format.
    
    This class provides methods for creating reports that compare planned vs. actual
    metrics for properties, with customizable date ranges and visualizations.
    """
    
    def __init__(self):
        """Initialize the KPI comparison report generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.property_financial_service = PropertyFinancialService()
    
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
        
        # Subheading style
        self.styles.add(
            ParagraphStyle(
                name='CustomSubheading',
                parent=self.styles['Heading3'],
                fontName=BRAND_CONFIG['fonts']['primary'],
                fontSize=12,
                textColor=brand_colors['secondary'],
                spaceAfter=8
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
        
        # Favorable metric style
        self.styles.add(
            ParagraphStyle(
                name='FavorableMetric',
                parent=self.styles['Normal'],
                fontName=BRAND_CONFIG['fonts']['secondary'],
                fontSize=10,
                textColor=brand_colors['success'],
                spaceAfter=3
            )
        )
        
        # Unfavorable metric style
        self.styles.add(
            ParagraphStyle(
                name='UnfavorableMetric',
                parent=self.styles['Normal'],
                fontName=BRAND_CONFIG['fonts']['secondary'],
                fontSize=10,
                textColor=brand_colors['danger'],
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
        property_id: str,
        user_id: str,
        output_buffer: io.BytesIO,
        analysis_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Generate a KPI comparison report.
        
        Args:
            property_id: ID of the property
            user_id: ID of the user requesting the report
            output_buffer: Buffer to write the PDF to
            analysis_id: Optional ID of the specific analysis to compare against
            start_date: Optional start date for filtering transactions (YYYY-MM-DD)
            end_date: Optional end date for filtering transactions (YYYY-MM-DD)
            metadata: Optional report metadata
        """
        try:
            # Get comparison data
            comparison_data = self.property_financial_service.compare_actual_to_projected(
                property_id, 
                user_id,
                analysis_id=analysis_id
            )
            
            # Create document
            doc = SimpleDocTemplate(
                output_buffer,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )
            
            # Create story (content)
            story = []
            
            # Add title and metadata
            self._add_title_section(story, comparison_data, metadata)
            
            # Add property details section
            self._add_property_details_section(story, comparison_data)
            
            # Add performance summary section
            self._add_performance_summary_section(story, comparison_data)
            
            # Add KPI comparison section
            self._add_kpi_comparison_section(story, comparison_data)
            
            # Add visualizations
            self._add_visualizations_section(story, comparison_data)
            
            # Build document with page decorations
            doc.build(story, onFirstPage=self._add_page_decorations, onLaterPages=self._add_page_decorations)
            
        except Exception as e:
            logger.error(f"Error generating KPI comparison report: {str(e)}")
            raise
    
    def _add_title_section(self, story: List, comparison_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add title section to the report.
        
        Args:
            story: ReportLab story to add content to
            comparison_data: Comparison data
            metadata: Optional report metadata
        """
        # Add title
        title = "KPI Comparison Report"
        story.append(Paragraph(title, self.styles["CustomTitle"]))
        
        # Add property address
        address = comparison_data.get("address", "")
        if address:
            story.append(Paragraph(f"Property: {address}", self.styles["CustomNormal"]))
        
        # Add metadata
        if metadata:
            date_range = metadata.get("date_range", "All Dates")
            story.append(Paragraph(f"Date Range: {date_range}", self.styles["CustomNormal"]))
            
            if "generated_by" in metadata:
                story.append(Paragraph(f"Generated By: {metadata['generated_by']}", self.styles["CustomNormal"]))
        
        # Add generation date
        story.append(Paragraph(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}", self.styles["CustomNormal"]))
        story.append(Spacer(1, 0.2*inch))
    
    def _add_property_details_section(self, story: List, comparison_data: Dict[str, Any]) -> None:
        """
        Add property details section to the report.
        
        Args:
            story: ReportLab story to add content to
            comparison_data: Comparison data
        """
        # Add section header
        story.append(Paragraph("Property Details", self.styles["CustomHeading"]))
        
        # Extract property details
        property_id = comparison_data.get("property_id", "")
        address = comparison_data.get("address", "")
        
        # Get analysis details
        analysis_details = comparison_data.get("analysis_details", {})
        analysis_name = analysis_details.get("name", "N/A")
        analysis_type = analysis_details.get("type", "N/A")
        
        # Create property details table
        data = [
            ["Property ID:", property_id],
            ["Address:", address],
            ["Analysis Name:", analysis_name],
            ["Analysis Type:", analysis_type]
        ]
        
        # Create table
        table = Table(data, colWidths=[1.5*inch, 5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), BRAND_CONFIG['colors']['table_header']),
            ('TEXTCOLOR', (0, 0), (0, -1), BRAND_CONFIG['colors']['text_dark']),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), BRAND_CONFIG['fonts']['primary']),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, BRAND_CONFIG['colors']['border']),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_performance_summary_section(self, story: List, comparison_data: Dict[str, Any]) -> None:
        """
        Add performance summary section to the report.
        
        Args:
            story: ReportLab story to add content to
            comparison_data: Comparison data
        """
        # Add section header
        story.append(Paragraph("Performance Summary", self.styles["CustomHeading"]))
        
        # Extract overall performance data
        comparison = comparison_data.get("comparison", {})
        overall = comparison.get("overall", {})
        
        performance_score = overall.get("performance_score", 0)
        metrics_better = overall.get("metrics_better_than_projected", 0)
        total_metrics = overall.get("total_metrics_compared", 0)
        is_better = overall.get("is_better_than_projected", False)
        
        # Create performance summary text
        if is_better:
            summary_text = f"The property is performing better than projected overall, with {metrics_better} out of {total_metrics} metrics exceeding projections ({performance_score:.1f}% performance score)."
            story.append(Paragraph(summary_text, self.styles["FavorableMetric"]))
        else:
            summary_text = f"The property is performing below projections overall, with only {metrics_better} out of {total_metrics} metrics exceeding projections ({performance_score:.1f}% performance score)."
            story.append(Paragraph(summary_text, self.styles["UnfavorableMetric"]))
        
        story.append(Spacer(1, 0.2*inch))
    
    def _add_kpi_comparison_section(self, story: List, comparison_data: Dict[str, Any]) -> None:
        """
        Add KPI comparison section to the report.
        
        Args:
            story: ReportLab story to add content to
            comparison_data: Comparison data
        """
        # Add section header
        story.append(Paragraph("KPI Comparison", self.styles["CustomHeading"]))
        
        # Extract metrics data
        actual_metrics = comparison_data.get("actual_metrics", {})
        projected_metrics = comparison_data.get("projected_metrics", {})
        comparison = comparison_data.get("comparison", {})
        
        # Create KPI comparison table
        table_data = [
            ["Metric", "Projected", "Actual", "Variance", "Status"]
        ]
        
        # Add income row
        income_comparison = comparison.get("income", {})
        monthly_income_projected = projected_metrics.get("total_income", {}).get("monthly", "0")
        monthly_income_actual = actual_metrics.get("total_income", {}).get("monthly", "0")
        income_variance = income_comparison.get("monthly_variance", "0")
        income_variance_pct = income_comparison.get("monthly_variance_percentage", "0")
        income_favorable = income_comparison.get("is_better_than_projected", False)
        
        income_status = "FAVORABLE" if income_favorable else "UNFAVORABLE"
        income_status_color = BRAND_CONFIG['colors']['success'] if income_favorable else BRAND_CONFIG['colors']['danger']
        
        table_data.append([
            "Monthly Income",
            f"${self._format_decimal(monthly_income_projected)}",
            f"${self._format_decimal(monthly_income_actual)}",
            f"${self._format_decimal(income_variance)} ({self._format_decimal(income_variance_pct)}%)",
            income_status
        ])
        
        # Add expenses row
        expenses_comparison = comparison.get("expenses", {})
        monthly_expenses_projected = projected_metrics.get("total_expenses", {}).get("monthly", "0")
        monthly_expenses_actual = actual_metrics.get("total_expenses", {}).get("monthly", "0")
        expenses_variance = expenses_comparison.get("monthly_variance", "0")
        expenses_variance_pct = expenses_comparison.get("monthly_variance_percentage", "0")
        expenses_favorable = expenses_comparison.get("is_better_than_projected", False)
        
        expenses_status = "FAVORABLE" if expenses_favorable else "UNFAVORABLE"
        expenses_status_color = BRAND_CONFIG['colors']['success'] if expenses_favorable else BRAND_CONFIG['colors']['danger']
        
        table_data.append([
            "Monthly Expenses",
            f"${self._format_decimal(monthly_expenses_projected)}",
            f"${self._format_decimal(monthly_expenses_actual)}",
            f"${self._format_decimal(expenses_variance)} ({self._format_decimal(expenses_variance_pct)}%)",
            expenses_status
        ])
        
        # Add NOI row
        noi_comparison = comparison.get("noi", {})
        monthly_noi_projected = projected_metrics.get("net_operating_income", {}).get("monthly", "0")
        monthly_noi_actual = actual_metrics.get("net_operating_income", {}).get("monthly", "0")
        noi_variance = noi_comparison.get("monthly_variance", "0")
        noi_variance_pct = noi_comparison.get("monthly_variance_percentage", "0")
        noi_favorable = noi_comparison.get("is_better_than_projected", False)
        
        noi_status = "FAVORABLE" if noi_favorable else "UNFAVORABLE"
        noi_status_color = BRAND_CONFIG['colors']['success'] if noi_favorable else BRAND_CONFIG['colors']['danger']
        
        table_data.append([
            "Monthly NOI",
            f"${self._format_decimal(monthly_noi_projected)}",
            f"${self._format_decimal(monthly_noi_actual)}",
            f"${self._format_decimal(noi_variance)} ({self._format_decimal(noi_variance_pct)}%)",
            noi_status
        ])
        
        # Add cash flow row
        cash_flow_comparison = comparison.get("cash_flow", {})
        monthly_cash_flow_projected = projected_metrics.get("cash_flow", {}).get("monthly", "0")
        monthly_cash_flow_actual = actual_metrics.get("cash_flow", {}).get("monthly", "0")
        cash_flow_variance = cash_flow_comparison.get("monthly_variance", "0")
        cash_flow_variance_pct = cash_flow_comparison.get("monthly_variance_percentage", "0")
        cash_flow_favorable = cash_flow_comparison.get("is_better_than_projected", False)
        
        cash_flow_status = "FAVORABLE" if cash_flow_favorable else "UNFAVORABLE"
        cash_flow_status_color = BRAND_CONFIG['colors']['success'] if cash_flow_favorable else BRAND_CONFIG['colors']['danger']
        
        table_data.append([
            "Monthly Cash Flow",
            f"${self._format_decimal(monthly_cash_flow_projected)}",
            f"${self._format_decimal(monthly_cash_flow_actual)}",
            f"${self._format_decimal(cash_flow_variance)} ({self._format_decimal(cash_flow_variance_pct)}%)",
            cash_flow_status
        ])
        
        # Add cap rate row if available
        if "cap_rate" in comparison:
            cap_rate_comparison = comparison.get("cap_rate", {})
            cap_rate_projected = projected_metrics.get("cap_rate", "0")
            cap_rate_actual = actual_metrics.get("cap_rate", "0")
            cap_rate_variance = cap_rate_comparison.get("variance", "0")
            cap_rate_variance_pct = cap_rate_comparison.get("variance_percentage", "0")
            cap_rate_favorable = cap_rate_comparison.get("is_better_than_projected", False)
            
            cap_rate_status = "FAVORABLE" if cap_rate_favorable else "UNFAVORABLE"
            cap_rate_status_color = BRAND_CONFIG['colors']['success'] if cap_rate_favorable else BRAND_CONFIG['colors']['danger']
            
            table_data.append([
                "Cap Rate",
                f"{self._format_decimal(cap_rate_projected)}%",
                f"{self._format_decimal(cap_rate_actual)}%",
                f"{self._format_decimal(cap_rate_variance)}% ({self._format_decimal(cap_rate_variance_pct)}%)",
                cap_rate_status
            ])
        
        # Add cash on cash return row if available
        if "cash_on_cash_return" in comparison:
            coc_comparison = comparison.get("cash_on_cash_return", {})
            coc_projected = projected_metrics.get("cash_on_cash_return", "0")
            coc_actual = actual_metrics.get("cash_on_cash_return", "0")
            coc_variance = coc_comparison.get("variance", "0")
            coc_variance_pct = coc_comparison.get("variance_percentage", "0")
            coc_favorable = coc_comparison.get("is_better_than_projected", False)
            
            coc_status = "FAVORABLE" if coc_favorable else "UNFAVORABLE"
            coc_status_color = BRAND_CONFIG['colors']['success'] if coc_favorable else BRAND_CONFIG['colors']['danger']
            
            table_data.append([
                "Cash on Cash Return",
                f"{self._format_decimal(coc_projected)}%",
                f"{self._format_decimal(coc_actual)}%",
                f"{self._format_decimal(coc_variance)}% ({self._format_decimal(coc_variance_pct)}%)",
                coc_status
            ])
        
        # Add DSCR row if available
        if "debt_service_coverage_ratio" in comparison:
            dscr_comparison = comparison.get("debt_service_coverage_ratio", {})
            dscr_projected = projected_metrics.get("debt_service_coverage_ratio", "0")
            dscr_actual = actual_metrics.get("debt_service_coverage_ratio", "0")
            dscr_variance = dscr_comparison.get("variance", "0")
            dscr_variance_pct = dscr_comparison.get("variance_percentage", "0")
            dscr_favorable = dscr_comparison.get("is_better_than_projected", False)
            
            dscr_status = "FAVORABLE" if dscr_favorable else "UNFAVORABLE"
            dscr_status_color = BRAND_CONFIG['colors']['success'] if dscr_favorable else BRAND_CONFIG['colors']['danger']
            
            table_data.append([
                "DSCR",
                f"{self._format_decimal(dscr_projected)}",
                f"{self._format_decimal(dscr_actual)}",
                f"{self._format_decimal(dscr_variance)} ({self._format_decimal(dscr_variance_pct)}%)",
                dscr_status
            ])
        
        # Create table
        col_widths = [1.5*inch, 1.2*inch, 1.2*inch, 1.8*inch, 1.3*inch]
        table = Table(table_data, colWidths=col_widths)
        
        # Style the table
        table_style = [
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_CONFIG['colors']['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), BRAND_CONFIG['fonts']['primary']),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data style
            ('FONTNAME', (0, 1), (-1, -1), BRAND_CONFIG['fonts']['secondary']),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (3, -1), 'RIGHT'),  # Right-align numeric columns
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Center status column
            
            # Grid style
            ('GRID', (0, 0), (-1, -1), 0.5, BRAND_CONFIG['colors']['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BRAND_CONFIG['colors']['table_row_alt']]),
        ]
        
        # Add status colors
        status_colors = [
            (income_status_color, 1),
            (expenses_status_color, 2),
            (noi_status_color, 3),
            (cash_flow_status_color, 4)
        ]
        
        row_index = 5
        if "cap_rate" in comparison:
            status_colors.append((cap_rate_status_color, row_index))
            row_index += 1
        
        if "cash_on_cash_return" in comparison:
            status_colors.append((coc_status_color, row_index))
            row_index += 1
        
        if "debt_service_coverage_ratio" in comparison:
            status_colors.append((dscr_status_color, row_index))
        
        for color, row in status_colors:
            table_style.append(('TEXTCOLOR', (4, row), (4, row), color))
            table_style.append(('FONTNAME', (4, row), (4, row), BRAND_CONFIG['fonts']['primary']))
        
        table.setStyle(TableStyle(table_style))
        
        story.append(table)
        story.append(Spacer(1, 0.1*inch))
        
        # Add note about favorable/unfavorable
        note_text = "Note: 'FAVORABLE' indicates the actual performance is better than projected. For expenses, lower actual values are favorable."
        story.append(Paragraph(note_text, self.styles["SmallText"]))
        story.append(Spacer(1, 0.2*inch))
    
    def _add_visualizations_section(self, story: List, comparison_data: Dict[str, Any]) -> None:
        """
        Add visualizations section to the report.
        
        Args:
            story: ReportLab story to add content to
            comparison_data: Comparison data
        """
        # Add section header
        story.append(Paragraph("Performance Visualizations", self.styles["CustomHeading"]))
        
        # Create income/expense comparison chart
        income_expense_chart = self._create_income_expense_comparison_chart(comparison_data)
        story.append(Image(income_expense_chart, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.1*inch))
        
        # Create cash flow comparison chart
        cash_flow_chart = self._create_cash_flow_comparison_chart(comparison_data)
        story.append(Image(cash_flow_chart, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.1*inch))
        
        # Create metrics comparison chart
        metrics_chart = self._create_metrics_comparison_chart(comparison_data)
        story.append(Image(metrics_chart, width=6*inch, height=3*inch))
        story.append(Spacer(1, 0.2*inch))
    
    def _format_decimal(self, value) -> str:
        """
        Format a decimal value to two decimal places.
        
        Args:
            value: Value to format
            
        Returns:
            Formatted string
        """
        try:
            # Handle string values
            if isinstance(value, str):
                # Remove currency symbols and commas
                value = value.replace('$', '').replace(',', '').replace('%', '')
                value = float(value)
            
            # Handle Decimal objects
            if isinstance(value, Decimal):
                value = float(value)
                
            # Format to two decimal places
            return f"{value:.2f}"
        except (ValueError, TypeError):
            return "0.00"
    
    def _create_income_expense_comparison_chart(self, comparison_data: Dict[str, Any]) -> io.BytesIO:
        """
        Create a bar chart comparing projected vs. actual income and expenses.
        
        Args:
            comparison_data: Comparison data
            
        Returns:
            BytesIO buffer containing the chart image
        """
        buffer = io.BytesIO()
        brand_colors = BRAND_CONFIG['colors']
        
        # Extract data
        actual_metrics = comparison_data.get("actual_metrics", {})
        projected_metrics = comparison_data.get("projected_metrics", {})
        
        # Get income and expense values
        monthly_income_projected = float(self._format_decimal(projected_metrics.get("total_income", {}).get("monthly", "0")))
        monthly_income_actual = float(self._format_decimal(actual_metrics.get("total_income", {}).get("monthly", "0")))
        monthly_expenses_projected = float(self._format_decimal(projected_metrics.get("total_expenses", {}).get("monthly", "0")))
        monthly_expenses_actual = float(self._format_decimal(actual_metrics.get("total_expenses", {}).get("monthly", "0")))
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Set background color
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#F9FBFF')
        
        # Set up bar positions
        bar_width = 0.35
        x = [0, 1]  # Positions for income and expenses
        
        # Create bars
        projected_bars = ax.bar(
            [p - bar_width/2 for p in x], 
            [monthly_income_projected, monthly_expenses_projected], 
            bar_width, 
            label='Projected',
            color=brand_colors['tertiary'],
            edgecolor='white',
            linewidth=1
        )
        
        actual_bars = ax.bar(
            [p + bar_width/2 for p in x], 
            [monthly_income_actual, monthly_expenses_actual], 
            bar_width, 
            label='Actual',
            color=brand_colors['primary'],
            edgecolor='white',
            linewidth=1
        )
        
        # Add labels and title
        ax.set_xlabel('Category', fontsize=10, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=10, fontweight='bold')
        ax.set_title('Income vs. Expenses: Projected vs. Actual', fontsize=12, fontweight='bold')
        
        # Set x-axis ticks
        ax.set_xticks(x)
        ax.set_xticklabels(['Income', 'Expenses'])
        
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
        
        add_labels(projected_bars)
        add_labels(actual_bars)
        
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _create_cash_flow_comparison_chart(self, comparison_data: Dict[str, Any]) -> io.BytesIO:
        """
        Create a bar chart comparing projected vs. actual cash flow.
        
        Args:
            comparison_data: Comparison data
            
        Returns:
            BytesIO buffer containing the chart image
        """
        buffer = io.BytesIO()
        brand_colors = BRAND_CONFIG['colors']
        
        # Extract data
        actual_metrics = comparison_data.get("actual_metrics", {})
        projected_metrics = comparison_data.get("projected_metrics", {})
        
        # Get cash flow values
        monthly_cash_flow_projected = float(self._format_decimal(projected_metrics.get("cash_flow", {}).get("monthly", "0")))
        monthly_cash_flow_actual = float(self._format_decimal(actual_metrics.get("cash_flow", {}).get("monthly", "0")))
        monthly_noi_projected = float(self._format_decimal(projected_metrics.get("net_operating_income", {}).get("monthly", "0")))
        monthly_noi_actual = float(self._format_decimal(actual_metrics.get("net_operating_income", {}).get("monthly", "0")))
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Set background color
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#F9FBFF')
        
        # Set up bar positions
        bar_width = 0.35
        x = [0, 1]  # Positions for NOI and Cash Flow
        
        # Create bars
        projected_bars = ax.bar(
            [p - bar_width/2 for p in x], 
            [monthly_noi_projected, monthly_cash_flow_projected], 
            bar_width, 
            label='Projected',
            color=brand_colors['tertiary'],
            edgecolor='white',
            linewidth=1
        )
        
        actual_bars = ax.bar(
            [p + bar_width/2 for p in x], 
            [monthly_noi_actual, monthly_cash_flow_actual], 
            bar_width, 
            label='Actual',
            color=brand_colors['primary'],
            edgecolor='white',
            linewidth=1
        )
        
        # Add labels and title
        ax.set_xlabel('Metric', fontsize=10, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=10, fontweight='bold')
        ax.set_title('NOI and Cash Flow: Projected vs. Actual', fontsize=12, fontweight='bold')
        
        # Set x-axis ticks
        ax.set_xticks(x)
        ax.set_xticklabels(['Net Operating Income', 'Cash Flow'])
        
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
        
        add_labels(projected_bars)
        add_labels(actual_bars)
        
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _create_metrics_comparison_chart(self, comparison_data: Dict[str, Any]) -> io.BytesIO:
        """
        Create a bar chart comparing projected vs. actual investment metrics.
        
        Args:
            comparison_data: Comparison data
            
        Returns:
            BytesIO buffer containing the chart image
        """
        buffer = io.BytesIO()
        brand_colors = BRAND_CONFIG['colors']
        
        # Extract data
        actual_metrics = comparison_data.get("actual_metrics", {})
        projected_metrics = comparison_data.get("projected_metrics", {})
        comparison = comparison_data.get("comparison", {})
        
        # Determine which metrics are available
        metrics = []
        metric_values_projected = []
        metric_values_actual = []
        metric_labels = []
        
        # Check for cap rate
        if "cap_rate" in comparison:
            metrics.append("cap_rate")
            metric_labels.append("Cap Rate")
            metric_values_projected.append(float(self._format_decimal(projected_metrics.get("cap_rate", "0"))))
            metric_values_actual.append(float(self._format_decimal(actual_metrics.get("cap_rate", "0"))))
        
        # Check for cash on cash return
        if "cash_on_cash_return" in comparison:
            metrics.append("cash_on_cash_return")
            metric_labels.append("Cash on Cash Return")
            metric_values_projected.append(float(self._format_decimal(projected_metrics.get("cash_on_cash_return", "0"))))
            metric_values_actual.append(float(self._format_decimal(actual_metrics.get("cash_on_cash_return", "0"))))
        
        # Check for DSCR
        if "debt_service_coverage_ratio" in comparison:
            metrics.append("debt_service_coverage_ratio")
            metric_labels.append("DSCR")
            metric_values_projected.append(float(self._format_decimal(projected_metrics.get("debt_service_coverage_ratio", "0"))))
            metric_values_actual.append(float(self._format_decimal(actual_metrics.get("debt_service_coverage_ratio", "0"))))
        
        # If no metrics are available, return an empty chart
        if not metrics:
            # Create a simple error message chart
            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            ax.text(0.5, 0.5, "No investment metrics available for comparison", 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=ax.transAxes, 
                fontsize=12,
                color=brand_colors['text_dark'])
            ax.axis('off')
            plt.savefig(buffer, format='png', dpi=100)
            plt.close(fig)
            
            buffer.seek(0)
            return buffer
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
        
        # Set background color
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#F9FBFF')
        
        # Set up bar positions
        bar_width = 0.35
        x = list(range(len(metrics)))
        
        # Create bars
        projected_bars = ax.bar(
            [p - bar_width/2 for p in x], 
            metric_values_projected, 
            bar_width, 
            label='Projected',
            color=brand_colors['tertiary'],
            edgecolor='white',
            linewidth=1
        )
        
        actual_bars = ax.bar(
            [p + bar_width/2 for p in x], 
            metric_values_actual, 
            bar_width, 
            label='Actual',
            color=brand_colors['primary'],
            edgecolor='white',
            linewidth=1
        )
        
        # Add labels and title
        ax.set_xlabel('Metric', fontsize=10, fontweight='bold')
        ax.set_ylabel('Value', fontsize=10, fontweight='bold')
        ax.set_title('Investment Metrics: Projected vs. Actual', fontsize=12, fontweight='bold')
        
        # Set x-axis ticks
        ax.set_xticks(x)
        ax.set_xticklabels(metric_labels)
        
        # Format y-axis as percentage for metrics
        def percentage_formatter(x, pos):
            return f'{x:.1f}%' if "DSCR" not in metric_labels else f'{x:.2f}'
        
        ax.yaxis.set_major_formatter(FuncFormatter(percentage_formatter))
        
        # Add grid
        ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.3)
        
        # Add legend
        ax.legend()
        
        # Add value labels on bars
        def add_labels(bars):
            for bar in bars:
                height = bar.get_height()
                if "DSCR" in metric_labels:
                    label = f'{height:.2f}'
                else:
                    label = f'{height:.1f}%'
                ax.annotate(
                    label,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', 
                    va='bottom',
                    fontsize=8
                )
        
        add_labels(projected_bars)
        add_labels(actual_bars)
        
        plt.tight_layout()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        buffer.seek(0)
        return buffer
