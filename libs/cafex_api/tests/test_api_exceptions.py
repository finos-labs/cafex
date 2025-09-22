"""
Test module for the APIExceptions class in the CAFEX framework.

This module provides comprehensive test coverage for the API exception handling
capabilities in the cafex_api.api_exceptions module.
"""

import pytest
from unittest.mock import patch

from cafex_api.api_exceptions import APIExceptions


class TestAPIExceptions:
    """Test suite for APIExceptions class."""

    @pytest.fixture
    def api_exceptions(self):
        """Fixture to create an APIExceptions instance for tests."""
        return APIExceptions()

    def test_init(self, api_exceptions):
        """Test APIExceptions initialization."""
        assert api_exceptions is not None
        # Verify inheritance from CoreExceptions
        assert hasattr(api_exceptions, 'raise_generic_exception')

    def test_raise_null_response_object(self, api_exceptions):
        """Test raising exception for null response object."""
        # Setup
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Test with default parameters
            api_exceptions.raise_null_response_object()

            # Verify the generic exception was called with the right parameters
            mock_raise.assert_called_once_with(
                message="The response object is null",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True
            )

            mock_raise.reset_mock()

            # Test with custom parameters
            api_exceptions.raise_null_response_object(
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

            # Verify the generic exception was called with custom parameters
            mock_raise.assert_called_once_with(
                message="The response object is null",
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

    def test_raise_null_value(self, api_exceptions):
        """Test raising exception for null value."""
        # Setup
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Test with default parameters
            message = "Test field is null"
            api_exceptions.raise_null_value(message)

            # Verify the generic exception was called with the right parameters
            mock_raise.assert_called_once_with(
                message=message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True
            )

            mock_raise.reset_mock()

            # Test with custom parameters
            api_exceptions.raise_null_value(
                message=message,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

            # Verify the generic exception was called with custom parameters
            mock_raise.assert_called_once_with(
                message=message,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

    def test_raise_invalid_value(self, api_exceptions):
        """Test raising exception for invalid value."""
        # Setup
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Test with default parameters
            message = "Status is invalid"
            api_exceptions.raise_invalid_value(message)

            # Verify the generic exception was called with the right parameters
            mock_raise.assert_called_once_with(
                message=message,
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True
            )

            mock_raise.reset_mock()

            # Test with custom parameters
            api_exceptions.raise_invalid_value(
                message=message,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

            # Verify the generic exception was called with custom parameters
            mock_raise.assert_called_once_with(
                message=message,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

    def test_raise_file_not_found(self, api_exceptions):
        """Test raising exception for file not found."""
        # Setup
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Test with default parameters
            file_path = "path/to/file.json"
            api_exceptions.raise_file_not_found(file_path)

            # Verify the generic exception was called with the right parameters
            mock_raise.assert_called_once_with(
                message=f"The file {file_path} is not found",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True
            )

            mock_raise.reset_mock()

            # Test with custom parameters
            api_exceptions.raise_file_not_found(
                file_path=file_path,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

            # Verify the generic exception was called with custom parameters
            mock_raise.assert_called_once_with(
                message=f"The file {file_path} is not found",
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

    def test_raise_invalid_status_code(self, api_exceptions):
        """Test raising exception for invalid status code."""
        # Setup
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Test with default parameters
            status_code = 404
            expected_code = 200
            api_exceptions.raise_invalid_status_code(status_code, expected_code)

            # Verify the generic exception was called with the right parameters
            mock_raise.assert_called_once_with(
                message=f"Invalid status code. Expected: {expected_code}, Got: {status_code}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True
            )

            mock_raise.reset_mock()

            # Test with custom parameters
            api_exceptions.raise_invalid_status_code(
                status_code=status_code,
                expected_code=expected_code,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

            # Verify the generic exception was called with custom parameters
            mock_raise.assert_called_once_with(
                message=f"Invalid status code. Expected: {expected_code}, Got: {status_code}",
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

    def test_raise_invalid_response_format(self, api_exceptions):
        """Test raising exception for invalid response format."""
        # Setup
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Test with default parameters
            expected_format = "JSON object"
            api_exceptions.raise_invalid_response_format(expected_format)

            # Verify the generic exception was called with the right parameters
            mock_raise.assert_called_once_with(
                message=f"Invalid API response format. Expected: {expected_format}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True
            )

            mock_raise.reset_mock()

            # Test with custom parameters
            api_exceptions.raise_invalid_response_format(
                expected_format=expected_format,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

            # Verify the generic exception was called with custom parameters
            mock_raise.assert_called_once_with(
                message=f"Invalid API response format. Expected: {expected_format}",
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

    def test_raise_missing_required_field(self, api_exceptions):
        """Test raising exception for missing required field."""
        # Setup
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Test with default parameters
            field_name = "user_id"
            api_exceptions.raise_missing_required_field(field_name)

            # Verify the generic exception was called with the right parameters
            mock_raise.assert_called_once_with(
                message=f"Required field missing: {field_name}",
                insert_report=True,
                trim_log=True,
                log_local=True,
                fail_test=True
            )

            mock_raise.reset_mock()

            # Test with custom parameters
            api_exceptions.raise_missing_required_field(
                field_name=field_name,
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

            # Verify the generic exception was called with custom parameters
            mock_raise.assert_called_once_with(
                message=f"Required field missing: {field_name}",
                insert_report=False,
                trim_log=False,
                log_local=False,
                fail_test=False
            )

    def test_integration_with_core_exceptions(self, api_exceptions):
        """Test integration with CoreExceptions."""
        # This test verifies that the API exceptions correctly integrate with the core exceptions
        with patch.object(api_exceptions, 'raise_generic_exception',
                          side_effect=RuntimeError("Test exception")) as mock_raise:
            # Test that the exception is properly propagated
            with pytest.raises(RuntimeError) as exc_info:
                api_exceptions.raise_null_response_object()

            assert "Test exception" in str(exc_info.value)
            mock_raise.assert_called_once()

    def test_exception_chain(self, api_exceptions):
        """Test exception chaining with multiple API exceptions."""
        # This tests chaining multiple API exceptions in sequence
        with patch.object(api_exceptions, 'raise_generic_exception') as mock_raise:
            # Define a test function that raises multiple exceptions
            def test_function():
                if True:  # Just for test flow
                    api_exceptions.raise_null_value("URL is null")
                    api_exceptions.raise_file_not_found("config.json")
                    api_exceptions.raise_invalid_status_code(404, 200)
                return True

            # Call the test function
            test_function()

            # Verify that all exceptions were handled
            assert mock_raise.call_count == 3

            # Verify the correct sequence of calls
            assert mock_raise.call_args_list[0][1]["message"] == "URL is null"
            assert mock_raise.call_args_list[1][1]["message"] == "The file config.json is not found"
            assert mock_raise.call_args_list[2][1]["message"] == "Invalid status code. Expected: 200, Got: 404"
