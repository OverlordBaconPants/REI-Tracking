"""
Test module for bulk transaction import functionality.

This module contains tests for the bulk transaction import functionality.
"""

import os
import pytest
import pandas as pd
import json
from unittest.mock import patch, MagicMock, mock_open
from decimal import Decimal
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


class TestBulkTransactionImport:
    """Test class for bulk transaction import functionality."""

    def test_process_import_file_success(self, import_service, mock_csv_data):
        """Test successful processing of an import file."""
        # Create a mock DataFrame
        df = pd.read_csv(StringIO(mock_csv_data))
        
        # Mock dependencies
        with patch.object(import_service, 'read_file', return_value=df):
            with patch.object(import_service, '_validate_column_mapping'):
                with patch.object(import_service, 'get_accessible_properties', return_value=[
                    MagicMock(id="123 Main St"),
                    MagicMock(id="456 Oak Ave")
                ]):
                    with patch.object(import_service, 'can_manage_property', return_value=True):
                        with patch.object(import_service, 'is_duplicate_transaction', return_value=False):
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
                            assert "skipped_details" in result
                            assert "modifications" in result
                            assert "preview_data" in result
                            
                            # Check values
                            assert result["total_rows"] == 3
                            assert result["processed_rows"] == 3
                            assert result["imported_count"] == 3
                            assert result["skipped_rows"] == 0
                            
                            # Check that create was called for each row
                            assert import_service.transaction_repo.create.call_count == 3

    def test_process_import_file_with_duplicate(self, import_service, mock_csv_data):
        """Test processing an import file with a duplicate transaction."""
        # Create a mock DataFrame
        df = pd.read_csv(StringIO(mock_csv_data))
        
        # Mock dependencies
        with patch.object(import_service, 'read_file', return_value=df):
            with patch.object(import_service, '_validate_column_mapping'):
                with patch.object(import_service, 'get_accessible_properties', return_value=[
                    MagicMock(id="123 Main St"),
                    MagicMock(id="456 Oak Ave")
                ]):
                    with patch.object(import_service, 'can_manage_property', return_value=True):
                        # Mock is_duplicate_transaction to return True for the first row
                        def is_duplicate_side_effect(transaction):
                            return transaction.property_id == "123 Main St" and transaction.date == "2025-01-01"
                        
                        with patch.object(import_service, 'is_duplicate_transaction', side_effect=is_duplicate_side_effect):
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
                            
                            # Check values
                            assert result["total_rows"] == 3
                            assert result["processed_rows"] == 2
                            assert result["imported_count"] == 2
                            assert result["skipped_rows"] == 1
                            assert result["skipped_details"]["duplicate"] == 1
                            
                            # Check that create was called for each non-duplicate row
                            assert import_service.transaction_repo.create.call_count == 2

    def test_process_import_file_with_unmatched_property(self, import_service, mock_csv_data):
        """Test processing an import file with an unmatched property."""
        # Create a mock DataFrame
        df = pd.read_csv(StringIO(mock_csv_data))
        
        # Mock dependencies
        with patch.object(import_service, 'read_file', return_value=df):
            with patch.object(import_service, '_validate_column_mapping'):
                # Return only one property, so the second row will have an unmatched property
                with patch.object(import_service, 'get_accessible_properties', return_value=[
                    MagicMock(id="123 Main St")
                ]):
                    with patch.object(import_service, 'can_manage_property', return_value=True):
                        with patch.object(import_service, 'is_duplicate_transaction', return_value=False):
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
                            
                            # Check values
                            assert result["total_rows"] == 3
                            assert result["processed_rows"] == 2
                            assert result["imported_count"] == 2
                            assert result["skipped_rows"] == 1
                            assert result["skipped_details"]["unmatched_property"] == 1
                            
                            # Check that create was called for each matched property row
                            assert import_service.transaction_repo.create.call_count == 2

    def test_process_import_file_with_permission_denied(self, import_service, mock_csv_data):
        """Test processing an import file with permission denied for a property."""
        # Create a mock DataFrame
        df = pd.read_csv(StringIO(mock_csv_data))
        
        # Mock dependencies
        with patch.object(import_service, 'read_file', return_value=df):
            with patch.object(import_service, '_validate_column_mapping'):
                with patch.object(import_service, 'get_accessible_properties', return_value=[
                    MagicMock(id="123 Main St"),
                    MagicMock(id="456 Oak Ave")
                ]):
                    # Allow management only for 123 Main St
                    def can_manage_side_effect(user_id, property_id):
                        return property_id == "123 Main St"
                    
                    with patch.object(import_service, 'can_manage_property', side_effect=can_manage_side_effect):
                        with patch.object(import_service, 'is_duplicate_transaction', return_value=False):
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
                            
                            # Check values
                            assert result["total_rows"] == 3
                            assert result["processed_rows"] == 2
                            assert result["imported_count"] == 2
                            assert result["skipped_rows"] == 1
                            assert result["skipped_details"]["permission_denied"] == 1
                            
                            # Check that create was called for each permitted property row
                            assert import_service.transaction_repo.create.call_count == 2

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
            # Missing date
            "category": "Category",
            "description": "Description",
            "collector_payer": "Collector/Payer"
        }
        
        # Create file columns
        file_columns = ["Property", "Date", "Amount", "Category", "Description", "Collector/Payer"]
        
        # Call the method - should raise an exception
        with pytest.raises(ValueError) as excinfo:
            import_service._validate_column_mapping(column_mapping, file_columns)
        
        assert "date" in str(excinfo.value)

    def test_validate_column_mapping_invalid_column(self, import_service):
        """Test validating a column mapping with invalid column."""
        # Create column mapping with invalid column
        column_mapping = {
            "property_id": "Property",
            "amount": "Amount",
            "date": "Invalid Column",
            "category": "Category",
            "description": "Description",
            "collector_payer": "Collector/Payer"
        }
        
        # Create file columns
        file_columns = ["Property", "Date", "Amount", "Category", "Description", "Collector/Payer"]
        
        # Call the method - should raise an exception
        with pytest.raises(ValueError) as excinfo:
            import_service._validate_column_mapping(column_mapping, file_columns)
        
        assert "Invalid Column" in str(excinfo.value)

    def test_clean_category(self, import_service):
        """Test cleaning category values."""
        # Test with valid category
        assert import_service._clean_category("Maintenance", "expense") == "Maintenance"
        
        # Test with empty category for income
        assert import_service._clean_category("", "income") == "Other Income"
        
        # Test with empty category for expense
        assert import_service._clean_category("", "expense") == "Other Expense"
        
        # Test with None category for income
        assert import_service._clean_category(None, "income") == "Other Income"

    def test_clean_description(self, import_service):
        """Test cleaning description values."""
        # Test with valid description
        assert import_service._clean_description("Test description") == "Test description"
        
        # Test with empty description
        assert import_service._clean_description("") == "Imported transaction"
        
        # Test with None description
        assert import_service._clean_description(None) == "Imported transaction"
        
        # Test with long description
        long_desc = "x" * 600
        cleaned_desc = import_service._clean_description(long_desc)
        assert len(cleaned_desc) <= 500
        assert cleaned_desc.endswith("...")

    def test_clean_collector_payer(self, import_service):
        """Test cleaning collector/payer values."""
        # Test with valid collector/payer
        assert import_service._clean_collector_payer("John Doe") == "John Doe"
        
        # Test with empty collector/payer
        assert import_service._clean_collector_payer("") == "Unknown"
        
        # Test with None collector/payer
        assert import_service._clean_collector_payer(None) == "Unknown"
