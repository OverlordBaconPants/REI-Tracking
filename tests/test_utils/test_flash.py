import pytest
from unittest.mock import patch, call
from utils.flash import flash_message, flash_success, flash_error, flash_warning, flash_info


class TestFlash:
    """Test suite for the flash utility functions."""

    @patch('utils.flash.flash')
    def test_flash_message_with_valid_input(self, mock_flash):
        """Test flash_message with valid input."""
        # Test with default category
        flash_message("Test message")
        mock_flash.assert_called_once_with("Test message", "info")
        mock_flash.reset_mock()

        # Test with success category
        flash_message("Success message", "success")
        mock_flash.assert_called_once_with("Success message", "success")
        mock_flash.reset_mock()

        # Test with error category
        flash_message("Error message", "error")
        mock_flash.assert_called_once_with("Error message", "error")
        mock_flash.reset_mock()

        # Test with warning category
        flash_message("Warning message", "warning")
        mock_flash.assert_called_once_with("Warning message", "warning")
        mock_flash.reset_mock()

        # Test with danger category (maps to error)
        flash_message("Danger message", "danger")
        mock_flash.assert_called_once_with("Danger message", "error")
        mock_flash.reset_mock()

        # Test with message category (maps to info)
        flash_message("Message", "message")
        mock_flash.assert_called_once_with("Message", "info")
        mock_flash.reset_mock()

    @patch('utils.flash.flash')
    def test_flash_message_with_uppercase_category(self, mock_flash):
        """Test flash_message with uppercase category."""
        flash_message("Test message", "SUCCESS")
        mock_flash.assert_called_once_with("Test message", "success")
        mock_flash.reset_mock()

        flash_message("Test message", "ERROR")
        mock_flash.assert_called_once_with("Test message", "error")
        mock_flash.reset_mock()

        flash_message("Test message", "WARNING")
        mock_flash.assert_called_once_with("Test message", "warning")
        mock_flash.reset_mock()

        flash_message("Test message", "INFO")
        mock_flash.assert_called_once_with("Test message", "info")

    @patch('utils.flash.flash')
    def test_flash_message_with_unknown_category(self, mock_flash):
        """Test flash_message with unknown category."""
        flash_message("Test message", "unknown")
        mock_flash.assert_called_once_with("Test message", "info")

    @patch('utils.flash.flash')
    def test_flash_message_with_non_string_category(self, mock_flash):
        """Test flash_message with non-string category."""
        flash_message("Test message", 123)
        mock_flash.assert_called_once_with("Test message", "info")

    @patch('utils.flash.flash')
    def test_flash_message_with_empty_message(self, mock_flash):
        """Test flash_message with empty message."""
        flash_message("")
        mock_flash.assert_not_called()

    @patch('utils.flash.flash')
    def test_flash_message_with_none_message(self, mock_flash):
        """Test flash_message with None message."""
        flash_message(None)
        mock_flash.assert_not_called()

    @patch('utils.flash.flash')
    def test_flash_message_with_non_string_message(self, mock_flash):
        """Test flash_message with non-string message."""
        flash_message(123)
        mock_flash.assert_called_once_with("123", "info")

    @patch('utils.flash.flash')
    def test_flash_message_exception_handling(self, mock_flash):
        """Test flash_message exception handling."""
        # Set up the mock to raise an exception on first call, then return normally
        mock_flash.side_effect = [Exception("Test exception"), None]
        flash_message("Test message")
        # Verify both calls were made
        assert mock_flash.call_count == 2
        mock_flash.assert_has_calls([
            call("Test message", "info"),
            call("Test exception", "error")
        ])

    @patch('utils.flash.flash_message')
    def test_flash_success(self, mock_flash_message):
        """Test flash_success function."""
        flash_success("Success message")
        mock_flash_message.assert_called_once_with("Success message", "success")

    @patch('utils.flash.flash_message')
    def test_flash_error(self, mock_flash_message):
        """Test flash_error function."""
        flash_error("Error message")
        mock_flash_message.assert_called_once_with("Error message", "error")

    @patch('utils.flash.flash_message')
    def test_flash_warning(self, mock_flash_message):
        """Test flash_warning function."""
        flash_warning("Warning message")
        mock_flash_message.assert_called_once_with("Warning message", "warning")

    @patch('utils.flash.flash_message')
    def test_flash_info(self, mock_flash_message):
        """Test flash_info function."""
        flash_info("Info message")
        mock_flash_message.assert_called_once_with("Info message", "info")
