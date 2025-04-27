"""
Test module for transaction report generator.

This module contains tests for the transaction report generator.
"""

import io
import os
import pytest
import zipfile
from unittest.mock import patch, MagicMock, call, ANY
from decimal import Decimal
from datetime import datetime

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image, PageBreak

from src.services.transaction_report_generator import TransactionReportGenerator


@pytest.fixture
def report_generator():
    """Create a transaction report generator for testing."""
    return TransactionReportGenerator()


@pytest.fixture
def mock_transactions():
    """Create mock transactions for testing."""
    return [
        {
            "id": "test-transaction-1",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Maintenance",
            "description": "Test transaction 1",
            "amount": "100.00",
            "date": "2025-01-01",
            "collector_payer": "Test User"
        },
        {
            "id": "test-transaction-2",
            "property_id": "456 Oak Ave",
            "type": "income",
            "category": "Rent",
            "description": "Test transaction 2",
            "amount": "1000.00",
            "date": "2025-01-15",
            "collector_payer": "Tenant"
        },
        {
            "id": "test-transaction-3",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Utilities",
            "description": "Test transaction 3",
            "amount": "50.00",
            "date": "2025-01-20",
            "collector_payer": "Test User",
            "reimbursement": {
                "date_shared": "2025-01-25",
                "share_description": "Split with partners",
                "reimbursement_status": "completed"
            }
        }
    ]


@pytest.fixture
def mock_transactions_with_docs():
    """Create mock transactions with documentation for testing."""
    return [
        {
            "id": "test-transaction-1",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Maintenance",
            "description": "Test transaction 1",
            "amount": "100.00",
            "date": "2025-01-01",
            "collector_payer": "Test User",
            "documentation_file": "test_doc_1.pdf"
        },
        {
            "id": "test-transaction-2",
            "property_id": "456 Oak Ave",
            "type": "income",
            "category": "Rent",
            "description": "Test transaction 2",
            "amount": "1000.00",
            "date": "2025-01-15",
            "collector_payer": "Tenant"
        },
        {
            "id": "test-transaction-3",
            "property_id": "123 Main St",
            "type": "expense",
            "category": "Utilities",
            "description": "Test transaction 3",
            "amount": "50.00",
            "date": "2025-01-20",
            "collector_payer": "Test User",
            "documentation_file": "test_doc_3.pdf",
            "reimbursement": {
                "date_shared": "2025-01-25",
                "share_description": "Split with partners",
                "reimbursement_status": "completed"
            }
        }
    ]


@pytest.fixture
def mock_metadata():
    """Create mock metadata for testing."""
    return {
        "title": "Test Transaction Report",
        "property_name": "All Properties",
        "date_range": "2025-01-01 to 2025-01-31",
        "generated_by": "Test User"
    }


class TestTransactionReportGenerator:
    """Test class for transaction report generator."""

    def test_init(self, report_generator):
        """Test initialization."""
        assert report_generator.styles is not None
        assert "CustomTitle" in report_generator.styles
        assert "CustomHeading" in report_generator.styles
        assert "CustomNormal" in report_generator.styles
        assert "TableHeader" in report_generator.styles

    @patch("src.services.transaction_report_generator.SimpleDocTemplate")
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._add_title_section")
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._process_summary_data")
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._add_summary_section")
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._add_financial_visualizations")
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._add_transactions_table")
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._add_documentation_references")
    def test_generate(
        self, mock_add_docs, mock_add_table, mock_add_viz, mock_add_summary, 
        mock_process_summary, mock_add_title, mock_doc_class, 
        report_generator, mock_transactions, mock_metadata
    ):
        """Test generating a report."""
        # Mock SimpleDocTemplate
        mock_doc = mock_doc_class.return_value
        
        # Mock _process_summary_data
        mock_summary_data = {
            "total_income": Decimal("1000.00"),
            "total_expense": Decimal("150.00"),
            "net_amount": Decimal("850.00"),
            "income_by_category": {"Rent": Decimal("1000.00")},
            "expense_by_category": {
                "Maintenance": Decimal("100.00"),
                "Utilities": Decimal("50.00")
            },
            "property_summary": {
                "123 Main St": {
                    "income": Decimal("0.00"),
                    "expense": Decimal("150.00"),
                    "net": Decimal("-150.00")
                },
                "456 Oak Ave": {
                    "income": Decimal("1000.00"),
                    "expense": Decimal("0.00"),
                    "net": Decimal("1000.00")
                }
            }
        }
        mock_process_summary.return_value = mock_summary_data
        
        # Create buffer
        buffer = io.BytesIO()
        
        # Call the method
        report_generator.generate(mock_transactions, buffer, mock_metadata)
        
        # Verify methods were called
        mock_doc_class.assert_called_once()
        mock_add_title.assert_called_once()
        mock_process_summary.assert_called_once_with(mock_transactions)
        mock_add_summary.assert_called_once()
        mock_add_viz.assert_called_once_with(ANY, mock_summary_data)
        mock_add_table.assert_called_once()
        mock_add_docs.assert_called_once()
        mock_doc.build.assert_called_once()

    def test_process_summary_data(self, report_generator, mock_transactions):
        """Test processing summary data."""
        # Call the method
        result = report_generator._process_summary_data(mock_transactions)
        
        # Check result
        assert result["total_income"] == Decimal("1000.00")
        assert result["total_expense"] == Decimal("150.00")
        assert result["net_amount"] == Decimal("850.00")
        
        # Check income by category
        assert "Rent" in result["income_by_category"]
        assert result["income_by_category"]["Rent"] == Decimal("1000.00")
        
        # Check expense by category
        assert "Maintenance" in result["expense_by_category"]
        assert result["expense_by_category"]["Maintenance"] == Decimal("100.00")
        assert "Utilities" in result["expense_by_category"]
        assert result["expense_by_category"]["Utilities"] == Decimal("50.00")
        
        # Check property summary
        assert "123 Main St" in result["property_summary"]
        assert "456 Oak Ave" in result["property_summary"]
        
        assert result["property_summary"]["123 Main St"]["income"] == Decimal("0.00")
        assert result["property_summary"]["123 Main St"]["expense"] == Decimal("150.00")
        assert result["property_summary"]["123 Main St"]["net"] == Decimal("-150.00")
        
        assert result["property_summary"]["456 Oak Ave"]["income"] == Decimal("1000.00")
        assert result["property_summary"]["456 Oak Ave"]["expense"] == Decimal("0.00")
        assert result["property_summary"]["456 Oak Ave"]["net"] == Decimal("1000.00")

    @patch("src.services.transaction_report_generator.Paragraph")
    @patch("src.services.transaction_report_generator.Spacer")
    def test_add_title_section(self, mock_spacer, mock_paragraph, report_generator, mock_metadata):
        """Test adding title section."""
        # Create story
        story = []
        
        # Call the method
        report_generator._add_title_section(story, mock_metadata)
        
        # Check result
        assert len(story) == 3  # Title, metadata, spacer
        
        # Verify Paragraph was called
        assert mock_paragraph.call_count == 2
        mock_paragraph.assert_any_call("Test Transaction Report", report_generator.styles["CustomTitle"])
        
        # Verify Spacer was called
        assert mock_spacer.call_count == 1

    @patch("src.services.transaction_report_generator.Paragraph")
    @patch("src.services.transaction_report_generator.Spacer")
    @patch("src.services.transaction_report_generator.Table")
    def test_add_summary_section(
        self, mock_table, mock_spacer, mock_paragraph, report_generator
    ):
        """Test adding summary section."""
        # Create story
        story = []
        
        # Create summary data
        summary_data = {
            "total_income": Decimal("1000.00"),
            "total_expense": Decimal("150.00"),
            "net_amount": Decimal("850.00"),
            "income_by_category": {"Rent": Decimal("1000.00")},
            "expense_by_category": {
                "Maintenance": Decimal("100.00"),
                "Utilities": Decimal("50.00")
            },
            "property_summary": {
                "123 Main St": {
                    "income": Decimal("0.00"),
                    "expense": Decimal("150.00"),
                    "net": Decimal("-150.00")
                },
                "456 Oak Ave": {
                    "income": Decimal("1000.00"),
                    "expense": Decimal("0.00"),
                    "net": Decimal("1000.00")
                }
            }
        }
        
        # Mock Table
        mock_table_instance = mock_table.return_value
        
        # Call the method
        report_generator._add_summary_section(story, summary_data)
        
        # Check result
        assert len(story) > 0
        
        # Verify Paragraph was called
        mock_paragraph.assert_any_call("Financial Summary", report_generator.styles["CustomHeading"])
        mock_paragraph.assert_any_call("Property Summary", report_generator.styles["CustomHeading"])
        mock_paragraph.assert_any_call("Category Breakdown", report_generator.styles["CustomHeading"])
        
        # Verify Table was called
        assert mock_table.call_count >= 3  # Overall table, property table, category tables
        
        # Verify Spacer was called
        assert mock_spacer.call_count >= 3

    @patch("src.services.transaction_report_generator.Paragraph")
    @patch("src.services.transaction_report_generator.Table")
    def test_add_transactions_table(
        self, mock_table, mock_paragraph, report_generator, mock_transactions
    ):
        """Test adding transactions table."""
        # Create story
        story = []
        
        # Mock Table
        mock_table_instance = mock_table.return_value
        
        # Call the method
        report_generator._add_transactions_table(story, mock_transactions)
        
        # Check result
        assert len(story) > 0
        
        # Verify Paragraph was called
        mock_paragraph.assert_called_once_with(
            "Transaction Details", report_generator.styles["CustomHeading"]
        )
        
        # Verify Table was called
        mock_table.assert_called_once()
        
        # Check table data
        table_data = mock_table.call_args[0][0]
        assert len(table_data) == 4  # Header + 3 transactions
        assert table_data[0] == [
            "Date", "Property", "Type", "Category", 
            "Description", "Amount", "Collector/Payer", "Status"
        ]
    
    @patch("src.services.transaction_report_generator.Paragraph")
    @patch("src.services.transaction_report_generator.Image")
    def test_add_financial_visualizations(
        self, mock_image, mock_paragraph, report_generator
    ):
        """Test adding financial visualizations."""
        # Create story and mock data
        story = []
        summary_data = {
            "total_income": Decimal("1000.00"),
            "total_expense": Decimal("150.00"),
            "net_amount": Decimal("850.00"),
            "income_by_category": {"Rent": Decimal("1000.00")},
            "expense_by_category": {
                "Maintenance": Decimal("100.00"),
                "Utilities": Decimal("50.00")
            },
            "property_summary": {
                "123 Main St": {
                    "income": Decimal("0.00"),
                    "expense": Decimal("150.00"),
                    "net": Decimal("-150.00")
                },
                "456 Oak Ave": {
                    "income": Decimal("1000.00"),
                    "expense": Decimal("0.00"),
                    "net": Decimal("1000.00")
                }
            }
        }
        
        # Mock chart creation methods
        with patch.object(report_generator, '_create_income_expense_pie_chart') as mock_pie_chart, \
             patch.object(report_generator, '_create_category_breakdown_chart') as mock_category_chart, \
             patch.object(report_generator, '_create_property_comparison_chart') as mock_property_chart:
            
            # Set up mock return values
            mock_pie_chart.return_value = io.BytesIO(b"pie chart data")
            mock_category_chart.return_value = io.BytesIO(b"category chart data")
            mock_property_chart.return_value = io.BytesIO(b"property chart data")
            
            # Call the method
            report_generator._add_financial_visualizations(story, summary_data)
            
            # Verify methods were called
            mock_paragraph.assert_called_with("Financial Visualizations", report_generator.styles["CustomHeading"])
            mock_pie_chart.assert_called_once_with(summary_data)
            mock_category_chart.assert_called_once_with(summary_data)
            mock_property_chart.assert_called_once_with(summary_data)
            
            # Verify Image was called for each chart
            assert mock_image.call_count == 3
    
    def test_create_income_expense_pie_chart(self, report_generator):
        """Test creating income expense pie chart."""
        # Create mock data
        summary_data = {
            "total_income": Decimal("1000.00"),
            "total_expense": Decimal("150.00")
        }
        
        # Call the method
        with patch("matplotlib.pyplot.savefig") as mock_savefig:
            result = report_generator._create_income_expense_pie_chart(summary_data)
            
            # Verify savefig was called
            mock_savefig.assert_called_once()
            
            # Verify result is a BytesIO object
            assert isinstance(result, io.BytesIO)
    
    def test_create_category_breakdown_chart(self, report_generator):
        """Test creating category breakdown chart."""
        # Create mock data
        summary_data = {
            "income_by_category": {"Rent": Decimal("1000.00")},
            "expense_by_category": {
                "Maintenance": Decimal("100.00"),
                "Utilities": Decimal("50.00")
            }
        }
        
        # Call the method
        with patch("matplotlib.pyplot.savefig") as mock_savefig:
            result = report_generator._create_category_breakdown_chart(summary_data)
            
            # Verify savefig was called
            mock_savefig.assert_called_once()
            
            # Verify result is a BytesIO object
            assert isinstance(result, io.BytesIO)
    
    def test_create_property_comparison_chart(self, report_generator):
        """Test creating property comparison chart."""
        # Create mock data
        summary_data = {
            "property_summary": {
                "123 Main St": {
                    "income": Decimal("0.00"),
                    "expense": Decimal("150.00"),
                    "net": Decimal("-150.00")
                },
                "456 Oak Ave": {
                    "income": Decimal("1000.00"),
                    "expense": Decimal("0.00"),
                    "net": Decimal("1000.00")
                }
            }
        }
        
        # Call the method
        with patch("matplotlib.pyplot.savefig") as mock_savefig:
            result = report_generator._create_property_comparison_chart(summary_data)
            
            # Verify savefig was called
            mock_savefig.assert_called_once()
            
            # Verify result is a BytesIO object
            assert isinstance(result, io.BytesIO)
    
    @patch("src.services.transaction_report_generator.Paragraph")
    @patch("src.services.transaction_report_generator.PageBreak")
    @patch("src.services.transaction_report_generator.Table")
    def test_add_documentation_references(
        self, mock_table, mock_page_break, mock_paragraph, report_generator, mock_transactions_with_docs
    ):
        """Test adding documentation references."""
        # Create story
        story = []
        
        # Call the method
        report_generator._add_documentation_references(story, mock_transactions_with_docs)
        
        # Check result
        assert len(story) > 0
        
        # Verify PageBreak was called
        mock_page_break.assert_called_once()
        
        # Verify Paragraph was called for heading
        mock_paragraph.assert_any_call(
            "Transaction Documentation", report_generator.styles["CustomHeading"]
        )
        
        # Verify Table was called
        mock_table.assert_called_once()
        
        # Check table data
        table_data = mock_table.call_args[0][0]
        assert len(table_data) == 3  # Header + 2 transactions with docs
        assert table_data[0] == [
            "Date", "Property", "Description", "Amount", "Documentation"
        ]
    
    def test_add_documentation_references_no_docs(self, report_generator, mock_transactions):
        """Test adding documentation references when no docs exist."""
        # Create story
        story = []
        
        # Call the method
        report_generator._add_documentation_references(story, mock_transactions)
        
        # Check result - should not add anything
        assert len(story) == 0
    
    @patch("zipfile.ZipFile")
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._generate_zip_readme")
    def test_generate_zip_archive(
        self, mock_generate_readme, mock_zipfile, report_generator, mock_transactions_with_docs
    ):
        """Test generating ZIP archive."""
        # Mock file service
        report_generator.file_service = MagicMock()
        report_generator.file_service.get_file_path.return_value = "/path/to/file.pdf"
        
        # Mock readme content
        mock_generate_readme.return_value = "README content"
        
        # Create mock ZipFile instance
        mock_zip = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip
        
        # Create buffer
        buffer = io.BytesIO()
        
        # Call the method
        report_generator.generate_zip_archive(mock_transactions_with_docs, buffer)
        
        # Verify ZipFile was created
        mock_zipfile.assert_called_once_with(buffer, 'w', zipfile.ZIP_DEFLATED)
        
        # Verify readme was added
        mock_zip.writestr.assert_called_once_with('README.txt', 'README content')
        
        # Verify files were added
        assert mock_zip.write.call_count == 2  # Two transactions with docs
    
    def test_generate_zip_readme(self, report_generator, mock_transactions_with_docs):
        """Test generating ZIP readme."""
        # Call the method
        result = report_generator._generate_zip_readme(mock_transactions_with_docs)
        
        # Verify result is a string
        assert isinstance(result, str)
        
        # Verify content
        assert "TRANSACTION DOCUMENTATION ARCHIVE" in result
        assert "Total transactions: 3" in result
        assert "Transactions with documentation: 2" in result
        assert "Date: 2025-01-01" in result
        assert "Property: 123 Main St" in result
        assert "Documentation: test_doc_1.pdf" in result
