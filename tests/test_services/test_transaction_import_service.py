"""
Test module for transaction import service.

This module contains tests for the transaction import service.
"""

import os
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock, mock_open
from decimal import Decimal
from pathlib import Path
from io import StringIO

from src.services.transaction_import_service import TransactionImportService
from src.models.transaction import Transaction


@pytest.fixture
def import_service():
    """Create a transaction import service for testing."""
    return TransactionImportService()


@pytest.fixture
def mock_csv_data():
    """Create mock CSV data for testing."""
    return (
        "Property,Date,Amount,Category,Description,Collector/Payer\n"
        "123 Main St,2025-01-01,100.00,Maintenance,Test expense,John Doe\n"
        "456 Oak Ave,2025-01-15,-1000.00,Rent,Test income,Jane Smith\n"
        "123 Main St,2025-01-20,50.00,Utilities,Test expense 2,John Doe\n"
    )


@pytest.fixture
def mock_properties():
    """Create mock properties for testing."""
    return [
        MagicMock(id="123 Main St"),
        MagicMock(id="456 Oak Ave")
    ]


class TestTransactionImportService:
    """Test class for transaction import service."""

    def test_read_file_csv(self, import_service):
        """Test reading a CSV file."""
        # Create a simple test for the read_file method
        # We'll just verify it doesn't raise an exception with our test path
        try:
            # Override the empty check for testing
            with patch.object(import_service, 'read_file', wraps=import_service.read_file) as wrapped_read:
                # Create a mock DataFrame
                mock_df = pd.DataFrame({
                    'Property': ['123 Main St', '456 Oak Ave'],
                    'Date': ['2025-01-01', '2025-01-15'],
                    'Amount': [100.00, -1000.00],
                    'Category': ['Maintenance', 'Rent'],
                    'Description': ['Test expense', 'Test income'],
                    'Collector/Payer': ['John Doe', 'Jane Smith']
                })
                
                # Mock pandas.read_csv to return our DataFrame
                with patch('pandas.read_csv', return_value=mock_df):
                    # Call the method
                    result = import_service.read_file("/path/to/file.csv", "file.csv")
                    
                    # Check result
                    assert isinstance(result, pd.DataFrame)
                    assert len(result) == 2
        except Exception as e:
            pytest.fail(f"read_file raised an exception: {str(e)}")

    @patch("pandas.read_excel")
    def test_read_file_excel(self, mock_read_excel, import_service, mock_csv_data):
        """Test reading an Excel file."""
        # Mock pandas read_excel
        mock_df = pd.read_csv(StringIO(mock_csv_data))
        mock_read_excel.return_value = mock_df
        
        # Call the method
        result = import_service.read_file("/path/to/file.xlsx", "file.xlsx")
        
        # Check result
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        
        # Verify pandas was called
        mock_read_excel.assert_called_once()

    def test_validate_column_mapping_valid(self, import_service):
        """Test validating a valid column mapping."""
        # Create column mapping
        column_mapping = {
            "property_id": "Property",
            "amount": "Amount",
            "date": "Date",
            "category": "Category",
            "description": "Description",
            "collector_payer": "Collector/Payer"
        }
        
        # Create file columns
        file_columns = ["Property", "Date", "Amount", "Category", "Description", "Collector/Payer"]
        
        # Call the method - should not raise an exception
        import_service._validate_column_mapping(column_mapping, file_columns)

    def test_validate_column_mapping_missing_required(self, import_service):
        """Test validating a column mapping with missing required fields."""
        # Create column mapping with missing required field
        column_mapping = {
            "property_id": "Property",
            "amount": "Amount",
            "date": "Date",
            "category": "Category",
            "description": "Description"
            # Missing collector_payer
        }
        
        # Create file columns
        file_columns = ["Property", "Date", "Amount", "Category", "Description", "Collector/Payer"]
        
        # Call the method - should raise an exception
        with pytest.raises(ValueError) as excinfo:
            import_service._validate_column_mapping(column_mapping, file_columns)
        
        assert "collector_payer" in str(excinfo.value)

    def test_validate_column_mapping_invalid_column(self, import_service):
        """Test validating a column mapping with invalid column."""
        # Create column mapping with invalid column
        column_mapping = {
            "property_id": "Property",
            "amount": "Amount",
            "date": "Date",
            "category": "Category",
            "description": "Description",
            "collector_payer": "Invalid Column"
        }
        
        # Create file columns
        file_columns = ["Property", "Date", "Amount", "Category", "Description", "Collector/Payer"]
        
        # Call the method - should raise an exception
        with pytest.raises(ValueError) as excinfo:
            import_service._validate_column_mapping(column_mapping, file_columns)
        
        assert "Invalid Column" in str(excinfo.value)

    def test_match_property_exact(self, import_service, mock_properties):
        """Test matching a property with exact match."""
        # Call the method
        result = import_service._match_property("123 Main St", mock_properties)
        
        # Check result
        assert result == "123 Main St"

    def test_match_property_case_insensitive(self, import_service, mock_properties):
        """Test matching a property with case-insensitive match."""
        # Call the method
        result = import_service._match_property("123 main st", mock_properties)
        
        # Check result
        assert result == "123 Main St"

    def test_match_property_partial(self, import_service, mock_properties):
        """Test matching a property with partial match."""
        # Call the method
        result = import_service._match_property("Main St", mock_properties)
        
        # Check result
        assert result == "123 Main St"

    def test_match_property_no_match(self, import_service, mock_properties):
        """Test matching a property with no match."""
        # Call the method
        result = import_service._match_property("789 Elm St", mock_properties)
        
        # Check result
        assert result is None

    def test_clean_amount_positive(self, import_service):
        """Test cleaning a positive amount."""
        # Call the method
        amount, transaction_type = import_service._clean_amount("100.00")
        
        # Check result
        assert amount == Decimal("100.00")
        assert transaction_type == "income"

    def test_clean_amount_negative(self, import_service):
        """Test cleaning a negative amount."""
        # Call the method
        amount, transaction_type = import_service._clean_amount("-100.00")
        
        # Check result
        assert amount == Decimal("100.00")
        assert transaction_type == "expense"

    def test_clean_amount_with_currency(self, import_service):
        """Test cleaning an amount with currency symbol."""
        # Call the method
        amount, transaction_type = import_service._clean_amount("$100.00")
        
        # Check result
        assert amount == Decimal("100.00")
        assert transaction_type == "income"

    def test_clean_amount_invalid(self, import_service):
        """Test cleaning an invalid amount."""
        # Call the method
        amount, transaction_type = import_service._clean_amount("invalid")
        
        # Check result
        assert amount is None
        assert transaction_type is None

    def test_parse_date_valid(self, import_service):
        """Test parsing a valid date."""
        # Call the method with various formats
        date1 = import_service._parse_date("2025-01-01")
        date2 = import_service._parse_date("01/01/2025")
        date3 = import_service._parse_date("2025/01/01")
        
        # Check results
        assert date1 == "2025-01-01"
        assert date2 == "2025-01-01"
        assert date3 == "2025-01-01"

    def test_parse_date_invalid(self, import_service):
        """Test parsing an invalid date."""
        # Call the method
        date = import_service._parse_date("invalid")
        
        # Check result
        assert date is None

    def test_process_import_file(self, import_service, mock_csv_data):
        """Test processing an import file."""
        # Create a simplified test that doesn't rely on mocking the repository
        
        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'Property': ['123 Main St', '456 Oak Ave'],
            'Date': ['2025-01-01', '2025-01-15'],
            'Amount': [100.00, -1000.00],
            'Category': ['Maintenance', 'Rent'],
            'Description': ['Test expense', 'Test income'],
            'Collector/Payer': ['John Doe', 'Jane Smith']
        })
        
        # Mock dependencies
        with patch.object(import_service, 'read_file', return_value=mock_df):
            with patch.object(import_service, '_validate_column_mapping'):
                with patch.object(import_service, 'get_accessible_properties', return_value=[
                    MagicMock(id="123 Main St"),
                    MagicMock(id="456 Oak Ave")
                ]):
                    with patch.object(import_service, 'can_manage_property', return_value=True):
                        # Mock transaction repository
                        import_service.transaction_repo = MagicMock()
                        import_service.transaction_repo.create = MagicMock()
                        
                        # Create column mapping
                        column_mapping = {
                            "property_id": "Property",
                            "amount": "Amount",
                            "date": "Date",
                            "category": "Category",
                            "description": "Description",
                            "collector_payer": "Collector/Payer"
                        }
                        
                        # Call the method
                        result = import_service.process_import_file(
                            "/path/to/file.csv", 
                            column_mapping, 
                            "file.csv",
                            "test-user"
                        )
                        
                        # Check result structure
                        assert isinstance(result, dict)
                        assert "total_rows" in result
                        assert "processed_rows" in result
                        assert "imported_count" in result
                        assert "skipped_rows" in result

    def test_is_duplicate_transaction(self, import_service):
        """Test checking for duplicate transactions."""
        # Create test transactions
        existing_transaction = Transaction(
            id="test-1",
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Test transaction",
            amount=Decimal("100.00"),
            date="2025-01-01",
            collector_payer="Test User"
        )
        
        # Mock repository directly on the import service
        import_service.transaction_repo = MagicMock()
        import_service.transaction_repo.get_all = MagicMock(return_value=[existing_transaction])
        
        # Create new transaction (duplicate)
        duplicate_transaction = Transaction(
            id="test-2",
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Another description",
            amount=Decimal("100.00"),
            date="2025-01-01",
            collector_payer="Test User"
        )
        
        # Create new transaction (not duplicate)
        non_duplicate_transaction = Transaction(
            id="test-3",
            property_id="123 Main St",
            type="expense",
            category="Maintenance",
            description="Another description",
            amount=Decimal("200.00"),
            date="2025-01-01",
            collector_payer="Test User"
        )
        
        # Call the method
        is_duplicate = import_service.is_duplicate_transaction(duplicate_transaction)
        is_not_duplicate = import_service.is_duplicate_transaction(non_duplicate_transaction)
        
        # Check results
        assert is_duplicate is True
        assert is_not_duplicate is False
