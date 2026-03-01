"""
Unit tests for error handling.

This module tests custom exceptions, exception handlers, and retry logic.
Validates: Requirements 9.1, 9.2, 9.3
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.exceptions import (
    AccommodationSystemError,
    DuplicateEntryError,
    SheetsAPIError,
    ValidationError
)
from app.utils import retry_with_backoff
from app.main import (
    validation_exception_handler,
    duplicate_entry_exception_handler,
    sheets_api_exception_handler,
    custom_validation_exception_handler,
    general_exception_handler
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_accommodation_system_error_base(self):
        """Test base exception class."""
        error = AccommodationSystemError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_duplicate_entry_error(self):
        """
        Test DuplicateEntryError exception.

        Validates: Requirements 4.1, 9.2
        """
        existing_entry = {
            "name": "John Doe",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-07"
        }

        error = DuplicateEntryError("test@example.com", existing_entry)

        assert error.email == "test@example.com"
        assert error.existing_entry == existing_entry
        assert "test@example.com" in str(error)
        assert isinstance(error, AccommodationSystemError)

    def test_sheets_api_error(self):
        """
        Test SheetsAPIError exception.

        Validates: Requirements 5.4, 9.2
        """
        original_error = Exception("API connection failed")
        error = SheetsAPIError("append_row", original_error)

        assert error.operation == "append_row"
        assert error.original_error == original_error
        assert "append_row" in str(error)
        assert isinstance(error, AccommodationSystemError)

    def test_validation_error(self):
        """
        Test ValidationError exception.

        Validates: Requirements 9.3
        """
        error = ValidationError("email", "Invalid email format")

        assert error.field == "email"
        assert error.message == "Invalid email format"
        assert "email" in str(error)
        assert "Invalid email format" in str(error)
        assert isinstance(error, AccommodationSystemError)


class TestExceptionHandlers:
    """Test exception handler functions."""

    @pytest.mark.asyncio
    async def test_validation_exception_handler(self):
        """
        Test validation exception handler.

        Validates: Requirements 9.3
        """
        # Create mock request
        request = Mock(spec=Request)
        request.url.path = "/api/accommodation"

        # Create mock validation error
        from pydantic_core import ValidationError as CoreValidationError

        # Create a simple validation error
        exc = RequestValidationError([
            {
                "loc": ("body", "email"),
                "msg": "Invalid email format",
                "type": "value_error"
            },
            {
                "loc": ("body", "name"),
                "msg": "Field required",
                "type": "missing"
            }
        ])

        # Call handler
        response = await validation_exception_handler(request, exc)

        # Verify response
        assert response.status_code == 400
        body = response.body.decode()
        assert "success" in body
        assert "false" in body.lower()
        assert "details" in body

    @pytest.mark.asyncio
    async def test_duplicate_entry_exception_handler(self):
        """
        Test duplicate entry exception handler.

        Validates: Requirements 4.1, 9.2
        """
        # Create mock request
        request = Mock(spec=Request)

        # Create duplicate entry error
        existing_entry = {
            "name": "John Doe",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-07"
        }
        exc = DuplicateEntryError("test@example.com", existing_entry)

        # Call handler
        response = await duplicate_entry_exception_handler(request, exc)

        # Verify response
        assert response.status_code == 409
        body = response.body.decode()
        assert "success" in body
        assert "false" in body.lower()
        assert "duplicate" in body
        assert "true" in body.lower()

    @pytest.mark.asyncio
    async def test_sheets_api_exception_handler(self):
        """
        Test Sheets API exception handler.

        Validates: Requirements 5.4, 9.2
        """
        # Create mock request
        request = Mock(spec=Request)

        # Create Sheets API error
        original_error = Exception("Connection timeout")
        exc = SheetsAPIError("append_row", original_error)

        # Call handler
        response = await sheets_api_exception_handler(request, exc)

        # Verify response
        assert response.status_code == 503
        body = response.body.decode()
        assert "success" in body
        assert "false" in body.lower()
        assert "unavailable" in body.lower()

    @pytest.mark.asyncio
    async def test_custom_validation_exception_handler(self):
        """
        Test custom validation exception handler.

        Validates: Requirements 9.3
        """
        # Create mock request
        request = Mock(spec=Request)

        # Create validation error
        exc = ValidationError("fromDate", "Date must be in valid range")

        # Call handler
        response = await custom_validation_exception_handler(request, exc)

        # Verify response
        assert response.status_code == 400
        body = response.body.decode()
        assert "success" in body
        assert "false" in body.lower()
        assert "details" in body

    @pytest.mark.asyncio
    async def test_general_exception_handler(self):
        """
        Test general exception handler.

        Validates: Requirements 9.1
        """
        # Create mock request
        request = Mock(spec=Request)
        request.url.path = "/api/test"

        # Create generic exception
        exc = Exception("Unexpected error occurred")

        # Call handler
        response = await general_exception_handler(request, exc)

        # Verify response
        assert response.status_code == 500
        body = response.body.decode()
        assert "success" in body
        assert "false" in body.lower()
        assert "error" in body
        # Should not leak implementation details
        assert "Unexpected error occurred" not in body


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """
        Test successful execution on first attempt.

        Validates: Requirements 5.4
        """
        # Create mock function that succeeds
        mock_func = AsyncMock(return_value="success")

        # Call retry logic
        result = await retry_with_backoff(mock_func, max_attempts=3)

        # Verify
        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_success_after_failures(self):
        """
        Test successful execution after retries.

        Validates: Requirements 5.4
        """
        # Create mock function that fails twice then succeeds
        mock_func = AsyncMock(
            side_effect=[
                SheetsAPIError("test", Exception("Fail 1")),
                SheetsAPIError("test", Exception("Fail 2")),
                "success"
            ]
        )

        # Call retry logic
        result = await retry_with_backoff(
            mock_func,
            max_attempts=3,
            initial_delay=0.01,  # Short delay for testing
            backoff_factor=2.0
        )

        # Verify
        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """
        Test retry exhaustion after max attempts.

        Validates: Requirements 5.4
        """
        # Create mock function that always fails
        mock_func = AsyncMock(
            side_effect=SheetsAPIError("test", Exception("Always fails"))
        )

        # Call retry logic and expect exception
        with pytest.raises(SheetsAPIError):
            await retry_with_backoff(
                mock_func,
                max_attempts=3,
                initial_delay=0.01,
                backoff_factor=2.0
            )

        # Verify all attempts were made
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_non_retryable_error(self):
        """
        Test that non-retryable errors are not retried.

        Validates: Requirements 5.4
        """
        # Create mock function that raises non-retryable error
        mock_func = AsyncMock(side_effect=ValueError("Invalid input"))

        # Call retry logic and expect immediate exception
        with pytest.raises(ValueError):
            await retry_with_backoff(
                mock_func,
                max_attempts=3,
                initial_delay=0.01
            )

        # Verify only one attempt was made
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_exponential_backoff(self):
        """
        Test exponential backoff timing.

        Validates: Requirements 5.4
        """
        import time

        # Create mock function that fails twice
        mock_func = AsyncMock(
            side_effect=[
                SheetsAPIError("test", Exception("Fail 1")),
                SheetsAPIError("test", Exception("Fail 2")),
                "success"
            ]
        )

        # Call retry logic with measurable delays
        start_time = time.time()
        result = await retry_with_backoff(
            mock_func,
            max_attempts=3,
            initial_delay=0.1,
            backoff_factor=2.0
        )
        elapsed_time = time.time() - start_time

        # Verify result
        assert result == "success"

        # Verify exponential backoff occurred
        # First retry: 0.1s, Second retry: 0.2s = Total ~0.3s minimum
        assert elapsed_time >= 0.3
        assert mock_func.call_count == 3


class TestErrorResponseFormats:
    """Test error response formats."""

    def test_validation_error_response_format(self):
        """
        Test validation error response has correct format.

        Validates: Requirements 9.3
        """
        error = ValidationError("email", "Invalid format")

        # Verify error attributes
        assert hasattr(error, 'field')
        assert hasattr(error, 'message')
        assert error.field == "email"
        assert error.message == "Invalid format"

    def test_duplicate_error_response_format(self):
        """
        Test duplicate error response has correct format.

        Validates: Requirements 4.1, 9.2
        """
        existing_entry = {
            "name": "Test User",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-07"
        }
        error = DuplicateEntryError("test@example.com", existing_entry)

        # Verify error attributes
        assert hasattr(error, 'email')
        assert hasattr(error, 'existing_entry')
        assert error.email == "test@example.com"
        assert error.existing_entry == existing_entry

    def test_sheets_error_response_format(self):
        """
        Test Sheets API error response has correct format.

        Validates: Requirements 5.4, 9.2
        """
        original = Exception("Connection failed")
        error = SheetsAPIError("append_row", original)

        # Verify error attributes
        assert hasattr(error, 'operation')
        assert hasattr(error, 'original_error')
        assert error.operation == "append_row"
        assert error.original_error == original
