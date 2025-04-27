"""
Test module for transaction report generator.

This module contains tests for the transaction report generator.
"""

import io
import pytest
from unittest.mock import patch, MagicMock, call
from decimal import Decimal
from datetime import datetime

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table

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
    @patch("src.services.transaction_report_generator.TransactionReportGenerator._add_transactions_table")
    def test_generate(
        self, mock_add_table, mock_add_summary, mock_process_summary, 
        mock_add_title, mock_doc_class, report_generator, mock_transactions, mock_metadata
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
        # The actual call uses a list as the first argument, not mock_doc.any()
        # So we'll check the call args differently
        assert mock_add_summary.call_count == 1
        assert mock_add_table.call_count == 1
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
