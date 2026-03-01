"""
Unit tests for AccommodationService.

Tests specific examples and edge cases for accommodation entry creation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.models import AccommodationRequest, AccommodationEntry
from app.services.accommodation_service import AccommodationService
from app.services.validation_service import ValidationService, ValidationError


@pytest.fixture
def mock_sheets_repo():
    """Create mock sheets repository."""
    return MagicMock()


@pytest.fixture
def validator():
    """Create real validation service."""
    return ValidationService()


@pytest.fixture
def accommodation_service(mock_sheets_repo, validator):
    """Create AccommodationService with mock repository."""
    return AccommodationService(mock_sheets_repo, validator)


@pytest.mark.asyncio
async def test_create_accommodation_success(accommodation_service, mock_sheets_repo):
    """
    Test successful accommodation entry creation.

    Validates: Requirements 3.1, 3.2, 3.5, 3.6
    """
    # Arrange
    request = AccommodationRequest(
        name="John Doe",
        email="john@example.com",
        college="NIT Trichy",
        fromDate="2026-03-06",
        toDate="2026-03-08",
        accommodationType="Boys",
        notes="Late arrival",
        force=False
    )
    volunteer_email = "volunteer@example.com"

    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)
    mock_sheets_repo.append_accommodation = AsyncMock()

    # Act
    result = await accommodation_service.create_accommodation(
        request,
        volunteer_email,
        force=False
    )

    # Assert
    assert result.success is True
    assert result.message == "Accommodation entry created successfully"
    assert result.duplicate is False
    assert result.entry is not None

    # Verify automatic fields
    assert result.entry.timestamp is not None
    assert isinstance(result.entry.timestamp, datetime)
    assert result.entry.enteredBy == volunteer_email

    # Verify user fields
    assert result.entry.name == "John Doe"
    assert result.entry.email == "john@example.com"
    assert result.entry.college == "NIT Trichy"
    assert result.entry.fromDate == "2026-03-06"
    assert result.entry.toDate == "2026-03-08"
    assert result.entry.accommodationType == "Boys"
    assert result.entry.notes == "Late arrival"

    # Verify append was called
    mock_sheets_repo.append_accommodation.assert_called_once()


@pytest.mark.asyncio
async def test_create_accommodation_duplicate_warning(accommodation_service, mock_sheets_repo):
    """
    Test duplicate warning when entry already exists.

    Validates: Requirements 4.1
    """
    # Arrange
    request = AccommodationRequest(
        name="Jane Smith",
        email="jane@example.com",
        college="IIT Madras",
        fromDate="2026-03-07",
        toDate="2026-03-08",
        accommodationType="Girls",
        notes=None,
        force=False
    )
    volunteer_email = "volunteer@example.com"

    existing_entry = {
        'Email': 'jane@example.com',
        'Name': 'Jane Smith',
        'From Date': '2026-03-06',
        'To Date': '2026-03-07',
        'Accommodation Type': 'Girls'
    }
    mock_sheets_repo.find_accommodation = AsyncMock(
        return_value=existing_entry)
    mock_sheets_repo.append_accommodation = AsyncMock()

    # Act
    result = await accommodation_service.create_accommodation(
        request,
        volunteer_email,
        force=False
    )

    # Assert
    assert result.success is False
    assert result.duplicate is True
    assert "already exists" in result.message
    assert result.existingEntry is not None
    assert result.existingEntry['name'] == 'Jane Smith'
    assert result.existingEntry['fromDate'] == '2026-03-06'

    # Verify append was NOT called
    mock_sheets_repo.append_accommodation.assert_not_called()


@pytest.mark.asyncio
async def test_create_accommodation_force_override(accommodation_service, mock_sheets_repo):
    """
    Test force flag bypasses duplicate check.

    Validates: Requirements 4.2, 4.3
    """
    # Arrange
    request = AccommodationRequest(
        name="Bob Wilson",
        email="bob@example.com",
        college="Test College",
        fromDate="2026-03-06",
        toDate="2026-03-08",
        accommodationType="Boys",
        notes=None,
        force=True
    )
    volunteer_email = "volunteer@example.com"

    existing_entry = {
        'Email': 'bob@example.com',
        'Name': 'Bob Wilson',
        'From Date': '2026-03-06',
        'To Date': '2026-03-07',
        'Accommodation Type': 'Boys'
    }
    mock_sheets_repo.find_accommodation = AsyncMock(
        return_value=existing_entry)
    mock_sheets_repo.append_accommodation = AsyncMock()

    # Act
    result = await accommodation_service.create_accommodation(
        request,
        volunteer_email,
        force=True
    )

    # Assert
    assert result.success is True
    assert result.duplicate is False
    assert result.entry is not None

    # Verify append WAS called despite duplicate
    mock_sheets_repo.append_accommodation.assert_called_once()


@pytest.mark.asyncio
async def test_create_accommodation_validation_error(accommodation_service, mock_sheets_repo):
    """
    Test validation error handling.

    Validates: Requirements 3.3
    """
    # Arrange - invalid date range (from > to)
    request = AccommodationRequest(
        name="Invalid User",
        email="invalid@example.com",
        college="Test College",
        fromDate="2026-03-08",
        toDate="2026-03-06",  # Invalid: before fromDate
        accommodationType="Boys",
        notes=None,
        force=False
    )
    volunteer_email = "volunteer@example.com"

    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)
    mock_sheets_repo.append_accommodation = AsyncMock()

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        await accommodation_service.create_accommodation(
            request,
            volunteer_email,
            force=False
        )

    # Verify error is about date range
    assert "date" in str(exc_info.value).lower()

    # Verify append was NOT called
    mock_sheets_repo.append_accommodation.assert_not_called()


@pytest.mark.asyncio
async def test_create_accommodation_with_empty_notes(accommodation_service, mock_sheets_repo):
    """
    Test accommodation creation with empty notes field.

    Validates: Requirements 3.2
    """
    # Arrange
    request = AccommodationRequest(
        name="No Notes User",
        email="nonotes@example.com",
        college="Test College",
        fromDate="2026-03-06",
        toDate="2026-03-07",
        accommodationType="Other",
        notes=None,
        force=False
    )
    volunteer_email = "volunteer@example.com"

    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)
    mock_sheets_repo.append_accommodation = AsyncMock()

    # Act
    result = await accommodation_service.create_accommodation(
        request,
        volunteer_email,
        force=False
    )

    # Assert
    assert result.success is True
    assert result.entry.notes is None


@pytest.mark.asyncio
async def test_create_accommodation_same_day_dates(accommodation_service, mock_sheets_repo):
    """
    Test accommodation creation with same from and to dates.

    Validates: Requirements 3.3
    """
    # Arrange
    request = AccommodationRequest(
        name="Same Day User",
        email="sameday@example.com",
        college="Test College",
        fromDate="2026-03-07",
        toDate="2026-03-07",  # Same as fromDate
        accommodationType="Girls",
        notes=None,
        force=False
    )
    volunteer_email = "volunteer@example.com"

    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)
    mock_sheets_repo.append_accommodation = AsyncMock()

    # Act
    result = await accommodation_service.create_accommodation(
        request,
        volunteer_email,
        force=False
    )

    # Assert - should succeed (from <= to is valid)
    assert result.success is True
    assert result.entry.fromDate == "2026-03-07"
    assert result.entry.toDate == "2026-03-07"


@pytest.mark.asyncio
async def test_duplicate_warning_response_structure(accommodation_service, mock_sheets_repo):
    """
    Test that duplicate warning response has correct structure.

    Validates: Requirements 4.1
    """
    # Arrange
    request = AccommodationRequest(
        name="Test User",
        email="test@example.com",
        college="Test College",
        fromDate="2026-03-06",
        toDate="2026-03-08",
        accommodationType="Boys",
        notes=None,
        force=False
    )
    volunteer_email = "volunteer@example.com"

    existing_entry = {
        'Email': 'test@example.com',
        'Name': 'Existing Name',
        'From Date': '2026-03-06',
        'To Date': '2026-03-07',
        'Accommodation Type': 'Boys'
    }
    mock_sheets_repo.find_accommodation = AsyncMock(
        return_value=existing_entry)

    # Act
    result = await accommodation_service.create_accommodation(
        request,
        volunteer_email,
        force=False
    )

    # Assert - verify response structure
    assert result.success is False
    assert result.duplicate is True
    assert result.message is not None
    assert result.existingEntry is not None

    # Verify existingEntry contains required fields
    assert 'name' in result.existingEntry
    assert 'fromDate' in result.existingEntry
    assert 'toDate' in result.existingEntry
    assert 'accommodationType' in result.existingEntry
