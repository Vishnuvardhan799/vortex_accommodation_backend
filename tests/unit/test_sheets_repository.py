"""
Unit tests for SheetsRepository.

Tests specific functionality including:
- Error handling for API failures
- Caching behavior with TTL
- Mock gspread client for isolated testing

Validates: Requirements 5.4
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime
import time

from gspread.exceptions import APIError, SpreadsheetNotFound

from app.models.schemas import AccommodationEntry
from app.repositories.sheets_repository import SheetsRepository, SheetsAPIError


@pytest.fixture
def mock_credentials():
    """Mock Google service account credentials."""
    with patch('app.repositories.sheets_repository.Credentials') as mock_creds:
        mock_creds.from_service_account_info.return_value = Mock()
        mock_creds.from_service_account_file.return_value = Mock()
        yield mock_creds


@pytest.fixture
def mock_gspread():
    """Mock gspread client and sheet."""
    with patch('app.repositories.sheets_repository.gspread') as mock_gs:
        # Create mock client
        mock_client = Mock()
        mock_gs.authorize.return_value = mock_client

        # Create mock spreadsheet and sheet
        mock_spreadsheet = Mock()
        mock_sheet = Mock()
        mock_sheet.title = "Test Sheet"
        mock_spreadsheet.sheet1 = mock_sheet
        mock_client.open.return_value = mock_spreadsheet

        yield {
            'gspread': mock_gs,
            'client': mock_client,
            'spreadsheet': mock_spreadsheet,
            'sheet': mock_sheet
        }


@pytest.fixture
def sample_accommodation_entry():
    """Create a sample AccommodationEntry for testing."""
    return AccommodationEntry(
        name="John Doe",
        email="john.doe@example.com",
        college="NIT Trichy",
        fromDate="2026-03-06",
        toDate="2026-03-08",
        accommodationType="Boys",
        notes="Test notes",
        enteredBy="volunteer@example.com"
    )


@pytest.fixture
def sheets_repo(mock_credentials, mock_gspread):
    """Create a SheetsRepository instance with mocked dependencies."""
    # Reset class-level client state before each test
    SheetsRepository._client = None
    SheetsRepository._client_initialized = False

    with patch.dict('os.environ', {
        'GOOGLE_CREDENTIALS_JSON': '{"type": "service_account", "project_id": "test"}',
        'SHEET_NAME': 'Test Accommodation Sheet'
    }):
        repo = SheetsRepository()
        return repo


class TestSheetsRepositoryInitialization:
    """Test SheetsRepository initialization and configuration."""

    def test_initialization_with_environment_variables(self, mock_credentials, mock_gspread):
        """Test successful initialization using environment variables."""
        # Reset class-level state
        SheetsRepository._client = None
        SheetsRepository._client_initialized = False

        with patch.dict('os.environ', {
            'GOOGLE_CREDENTIALS_JSON': '{"type": "service_account"}',
            'SHEET_NAME': 'Test Sheet'
        }):
            repo = SheetsRepository()

            assert repo.sheet_name == 'Test Sheet'
            assert repo.client is not None
            assert repo.sheet is not None

    def test_initialization_missing_credentials_env_var(self, mock_credentials, mock_gspread):
        """Test initialization fails when GOOGLE_CREDENTIALS_JSON is missing."""
        # Reset class-level state
        SheetsRepository._client = None
        SheetsRepository._client_initialized = False

        with patch.dict('os.environ', {'SHEET_NAME': 'Test Sheet'}, clear=True):
            with pytest.raises(ValueError, match="GOOGLE_CREDENTIALS_JSON"):
                SheetsRepository()

    def test_initialization_missing_sheet_name_env_var(self, mock_credentials, mock_gspread):
        """Test initialization fails when SHEET_NAME is missing."""
        # Reset class-level state
        SheetsRepository._client = None
        SheetsRepository._client_initialized = False

        with patch.dict('os.environ', {
            'GOOGLE_CREDENTIALS_JSON': '{"type": "service_account"}'
        }, clear=True):
            with pytest.raises(ValueError, match="SHEET_NAME"):
                SheetsRepository()

    def test_initialization_spreadsheet_not_found(self, mock_credentials, mock_gspread):
        """Test initialization fails gracefully when spreadsheet is not found."""
        # Reset class-level state
        SheetsRepository._client = None
        SheetsRepository._client_initialized = False

        # Configure mock to raise SpreadsheetNotFound
        mock_gspread['client'].open.side_effect = SpreadsheetNotFound(
            "Sheet not found")

        with patch.dict('os.environ', {
            'GOOGLE_CREDENTIALS_JSON': '{"type": "service_account"}',
            'SHEET_NAME': 'Nonexistent Sheet'
        }):
            with pytest.raises(SheetsAPIError) as exc_info:
                SheetsRepository()

            assert exc_info.value.operation == "sheet_access"
            assert isinstance(exc_info.value.original_error,
                              SpreadsheetNotFound)


class TestSheetsRepositoryCaching:
    """Test caching behavior with 60-second TTL."""

    @pytest.mark.asyncio
    async def test_cache_is_populated_on_first_find(self, sheets_repo, mock_gspread):
        """Test that cache is populated on first find_accommodation call."""
        # Configure mock to return sample data
        mock_records = [
            {'Email': 'test@example.com', 'Name': 'Test User'},
            {'Email': 'another@example.com', 'Name': 'Another User'}
        ]
        mock_gspread['sheet'].get_all_records.return_value = mock_records

        # First call should populate cache
        result = await sheets_repo.find_accommodation('test@example.com')

        assert result is not None
        assert result['Email'] == 'test@example.com'
        assert sheets_repo._cache is not None
        assert len(sheets_repo._cache) == 2
        mock_gspread['sheet'].get_all_records.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_is_reused_within_ttl(self, sheets_repo, mock_gspread):
        """Test that cache is reused for subsequent calls within TTL."""
        # Configure mock to return sample data
        mock_records = [
            {'Email': 'test@example.com', 'Name': 'Test User'}
        ]
        mock_gspread['sheet'].get_all_records.return_value = mock_records

        # First call populates cache
        await sheets_repo.find_accommodation('test@example.com')

        # Second call should use cache (no additional API call)
        result = await sheets_repo.find_accommodation('test@example.com')

        assert result is not None
        # get_all_records should only be called once
        assert mock_gspread['sheet'].get_all_records.call_count == 1

    @pytest.mark.asyncio
    async def test_cache_is_refreshed_after_ttl_expires(self, sheets_repo, mock_gspread):
        """Test that cache is refreshed after TTL expires."""
        # Configure mock to return sample data
        mock_records = [
            {'Email': 'test@example.com', 'Name': 'Test User'}
        ]
        mock_gspread['sheet'].get_all_records.return_value = mock_records

        # First call populates cache
        await sheets_repo.find_accommodation('test@example.com')

        # Simulate TTL expiration by manipulating cache timestamp
        sheets_repo._cache_timestamp = time.time() - 61  # 61 seconds ago

        # Second call should refresh cache
        result = await sheets_repo.find_accommodation('test@example.com')

        assert result is not None
        # get_all_records should be called twice (initial + refresh)
        assert mock_gspread['sheet'].get_all_records.call_count == 2

    @pytest.mark.asyncio
    async def test_cache_is_invalidated_after_append(self, sheets_repo, mock_gspread, sample_accommodation_entry):
        """Test that cache is invalidated after appending new entry."""
        # Configure mock to return sample data
        mock_records = [
            {'Email': 'existing@example.com', 'Name': 'Existing User'}
        ]
        mock_gspread['sheet'].get_all_records.return_value = mock_records

        # Populate cache
        await sheets_repo.find_accommodation('existing@example.com')
        assert sheets_repo._cache is not None

        # Append new entry
        await sheets_repo.append_accommodation(sample_accommodation_entry)

        # Cache should be invalidated
        assert sheets_repo._cache is None
        assert sheets_repo._cache_timestamp is None

    @pytest.mark.asyncio
    async def test_find_accommodation_case_insensitive(self, sheets_repo, mock_gspread):
        """Test that find_accommodation performs case-insensitive email search."""
        # Configure mock with mixed case email
        mock_records = [
            {'Email': 'Test@Example.COM', 'Name': 'Test User'}
        ]
        mock_gspread['sheet'].get_all_records.return_value = mock_records

        # Search with lowercase email
        result = await sheets_repo.find_accommodation('test@example.com')

        assert result is not None
        assert result['Email'] == 'Test@Example.COM'

    @pytest.mark.asyncio
    async def test_find_accommodation_returns_none_when_not_found(self, sheets_repo, mock_gspread):
        """Test that find_accommodation returns None when email is not found."""
        # Configure mock with empty records
        mock_gspread['sheet'].get_all_records.return_value = []

        result = await sheets_repo.find_accommodation('nonexistent@example.com')

        assert result is None


class TestSheetsRepositoryErrorHandling:
    """Test error handling for API failures."""

    @pytest.mark.asyncio
    async def test_find_accommodation_handles_api_error(self, sheets_repo, mock_gspread):
        """Test that find_accommodation handles Google Sheets API errors."""
        # Configure mock to raise APIError
        mock_gspread['sheet'].get_all_records.side_effect = APIError(
            "API Error")

        with pytest.raises(SheetsAPIError) as exc_info:
            await sheets_repo.find_accommodation('test@example.com')

        assert exc_info.value.operation == "get_all_records"
        assert isinstance(exc_info.value.original_error, APIError)

    @pytest.mark.asyncio
    async def test_find_accommodation_handles_unexpected_error(self, sheets_repo, mock_gspread):
        """Test that find_accommodation handles unexpected errors."""
        # Configure mock to raise unexpected error
        mock_gspread['sheet'].get_all_records.side_effect = Exception(
            "Unexpected error")

        with pytest.raises(SheetsAPIError) as exc_info:
            await sheets_repo.find_accommodation('test@example.com')

        assert exc_info.value.operation == "get_all_records"
        assert "Unexpected error" in str(exc_info.value.original_error)

    @pytest.mark.asyncio
    async def test_append_accommodation_handles_api_error(self, sheets_repo, mock_gspread, sample_accommodation_entry):
        """Test that append_accommodation handles Google Sheets API errors."""
        # Configure mock to raise APIError
        mock_gspread['sheet'].append_row.side_effect = APIError("API Error")

        with pytest.raises(SheetsAPIError) as exc_info:
            await sheets_repo.append_accommodation(sample_accommodation_entry)

        assert exc_info.value.operation == "append_row"
        assert isinstance(exc_info.value.original_error, APIError)

    @pytest.mark.asyncio
    async def test_append_accommodation_handles_unexpected_error(self, sheets_repo, mock_gspread, sample_accommodation_entry):
        """Test that append_accommodation handles unexpected errors."""
        # Configure mock to raise unexpected error
        mock_gspread['sheet'].append_row.side_effect = Exception(
            "Unexpected error")

        with pytest.raises(SheetsAPIError) as exc_info:
            await sheets_repo.append_accommodation(sample_accommodation_entry)

        assert exc_info.value.operation == "append_row"
        assert "Unexpected error" in str(exc_info.value.original_error)

    def test_authentication_error_during_client_initialization(self, mock_credentials):
        """Test that authentication errors are properly handled during client initialization."""
        # Reset class-level state
        SheetsRepository._client = None
        SheetsRepository._client_initialized = False

        with patch('app.repositories.sheets_repository.gspread') as mock_gs:
            # Configure mock to raise error during authorization
            mock_gs.authorize.side_effect = Exception("Authentication failed")

            with patch.dict('os.environ', {
                'GOOGLE_CREDENTIALS_JSON': '{"type": "service_account"}',
                'SHEET_NAME': 'Test Sheet'
            }):
                with pytest.raises(SheetsAPIError) as exc_info:
                    SheetsRepository()

                assert exc_info.value.operation == "authentication"
                assert "Authentication failed" in str(
                    exc_info.value.original_error)


class TestSheetsRepositoryAppendAccommodation:
    """Test append_accommodation functionality."""

    @pytest.mark.asyncio
    async def test_append_accommodation_success(self, sheets_repo, mock_gspread, sample_accommodation_entry):
        """Test successful accommodation entry append."""
        # Append entry
        await sheets_repo.append_accommodation(sample_accommodation_entry)

        # Verify append_row was called
        mock_gspread['sheet'].append_row.assert_called_once()

        # Verify the row data
        call_args = mock_gspread['sheet'].append_row.call_args[0][0]
        assert len(call_args) == 9
        assert call_args[1] == "John Doe"
        assert call_args[2] == "john.doe@example.com"
        assert call_args[3] == "NIT Trichy"

    @pytest.mark.asyncio
    async def test_append_accommodation_with_none_notes(self, sheets_repo, mock_gspread):
        """Test appending accommodation entry with None notes."""
        entry = AccommodationEntry(
            name="Jane Doe",
            email="jane@example.com",
            college="Test College",
            fromDate="2026-03-06",
            toDate="2026-03-07",
            accommodationType="Girls",
            notes=None,
            enteredBy="volunteer@example.com"
        )

        await sheets_repo.append_accommodation(entry)

        # Verify notes field is empty string, not None
        call_args = mock_gspread['sheet'].append_row.call_args[0][0]
        assert call_args[7] == ""  # Notes field should be empty string


class TestSheetsRepositoryVerifyConnection:
    """Test verify_connection health check functionality."""

    def test_verify_connection_success(self, sheets_repo, mock_gspread):
        """Test successful connection verification."""
        result = sheets_repo.verify_connection()

        assert result is True

    def test_verify_connection_failure(self, sheets_repo, mock_gspread):
        """Test connection verification failure."""
        # Configure mock to raise error when accessing title
        type(mock_gspread['sheet']).title = PropertyMock(
            side_effect=Exception("Connection failed"))

        result = sheets_repo.verify_connection()

        assert result is False


class TestSheetsRepositoryConnectionPooling:
    """Test connection pooling behavior."""

    def test_client_is_reused_across_instances(self, mock_credentials, mock_gspread):
        """Test that gspread client is reused across multiple SheetsRepository instances."""
        # Reset class-level state
        SheetsRepository._client = None
        SheetsRepository._client_initialized = False

        with patch.dict('os.environ', {
            'GOOGLE_CREDENTIALS_JSON': '{"type": "service_account"}',
            'SHEET_NAME': 'Test Sheet'
        }):
            # Create first instance
            repo1 = SheetsRepository()

            # Create second instance
            repo2 = SheetsRepository()

            # Both should use the same client
            assert repo1.client is repo2.client

            # gspread.authorize should only be called once
            assert mock_gspread['gspread'].authorize.call_count == 1
