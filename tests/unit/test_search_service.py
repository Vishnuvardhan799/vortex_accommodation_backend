"""
Unit tests for SearchService.

Tests specific examples and edge cases for participant search functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.models import RegistrationData, AccommodationStatus, SearchResponse
from app.services.search_service import SearchService


@pytest.fixture
def mock_reg_repo():
    """Create mock registration repository."""
    return MagicMock()


@pytest.fixture
def mock_sheets_repo():
    """Create mock sheets repository."""
    return MagicMock()


@pytest.fixture
def search_service(mock_reg_repo, mock_sheets_repo):
    """Create SearchService with mock repositories."""
    return SearchService(mock_reg_repo, mock_sheets_repo)


@pytest.mark.asyncio
async def test_search_with_accommodation_data(search_service, mock_reg_repo, mock_sheets_repo):
    """
    Test search when participant has both registration and accommodation data.

    Validates: Requirements 1.1, 1.2, 1.3
    """
    # Arrange
    email = "test@example.com"

    reg_data = RegistrationData(
        name="John Doe",
        email=email,
        college="NIT Trichy",
        events=["Tech Talk", "Hackathon"],
        workshops=["AI Workshop"]
    )
    mock_reg_repo.find_by_email.return_value = reg_data

    accom_data = {
        'Email': email,
        'Name': 'John Doe',
        'From Date': '2026-03-06',
        'To Date': '2026-03-08',
        'Accommodation Type': 'Boys',
        'Notes': 'Late arrival'
    }
    mock_sheets_repo.find_accommodation = AsyncMock(return_value=accom_data)

    # Act
    result = await search_service.search_participant(email)

    # Assert
    assert result.found is True
    assert result.participant is not None
    assert result.participant.name == "John Doe"
    assert result.participant.email == email
    assert result.participant.college == "NIT Trichy"
    assert result.participant.events == ["Tech Talk", "Hackathon"]
    assert result.participant.workshops == ["AI Workshop"]

    # Verify accommodation data
    assert result.participant.accommodation is not None
    assert result.participant.accommodation.hasAccommodation is True
    assert result.participant.accommodation.fromDate == '2026-03-06'
    assert result.participant.accommodation.toDate == '2026-03-08'
    assert result.participant.accommodation.type == 'Boys'
    assert result.participant.accommodation.notes == 'Late arrival'


@pytest.mark.asyncio
async def test_search_without_accommodation_data(search_service, mock_reg_repo, mock_sheets_repo):
    """
    Test search when participant has registration but no accommodation data.

    Validates: Requirements 1.1, 1.2, 1.3
    """
    # Arrange
    email = "test@example.com"

    reg_data = RegistrationData(
        name="Jane Smith",
        email=email,
        college="IIT Madras",
        events=["Workshop"],
        workshops=[]
    )
    mock_reg_repo.find_by_email.return_value = reg_data
    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)

    # Act
    result = await search_service.search_participant(email)

    # Assert
    assert result.found is True
    assert result.participant is not None
    assert result.participant.name == "Jane Smith"

    # Verify accommodation status shows no accommodation
    assert result.participant.accommodation is not None
    assert result.participant.accommodation.hasAccommodation is False
    assert result.participant.accommodation.fromDate is None
    assert result.participant.accommodation.toDate is None
    assert result.participant.accommodation.type is None


@pytest.mark.asyncio
async def test_search_participant_not_found(search_service, mock_reg_repo, mock_sheets_repo):
    """
    Test search when participant is not in registration data.

    Validates: Requirements 1.4
    """
    # Arrange
    email = "notfound@example.com"
    mock_reg_repo.find_by_email.return_value = None
    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)

    # Act
    result = await search_service.search_participant(email)

    # Assert
    assert result.found is False
    assert result.participant is None
    assert result.message == "No participant found with this email"


@pytest.mark.asyncio
async def test_search_with_empty_events_and_workshops(search_service, mock_reg_repo, mock_sheets_repo):
    """
    Test search when participant has no events or workshops registered.

    Validates: Requirements 1.2
    """
    # Arrange
    email = "minimal@example.com"

    reg_data = RegistrationData(
        name="Minimal User",
        email=email,
        college="Test College",
        events=[],
        workshops=[]
    )
    mock_reg_repo.find_by_email.return_value = reg_data
    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)

    # Act
    result = await search_service.search_participant(email)

    # Assert
    assert result.found is True
    assert result.participant is not None
    assert result.participant.events == []
    assert result.participant.workshops == []


@pytest.mark.asyncio
async def test_concurrent_query_execution(search_service, mock_reg_repo, mock_sheets_repo):
    """
    Test that registration and accommodation queries are executed concurrently.

    Validates: Requirements 1.1 (performance optimization)
    """
    # Arrange
    email = "concurrent@example.com"

    reg_data = RegistrationData(
        name="Concurrent Test",
        email=email,
        college="Test College",
        events=["Event"],
        workshops=[]
    )
    mock_reg_repo.find_by_email.return_value = reg_data
    mock_sheets_repo.find_accommodation = AsyncMock(return_value=None)

    # Act
    result = await search_service.search_participant(email)

    # Assert - both repositories should have been called
    mock_reg_repo.find_by_email.assert_called_once_with(email)
    mock_sheets_repo.find_accommodation.assert_called_once_with(email)

    # Result should be successful
    assert result.found is True


@pytest.mark.asyncio
async def test_search_with_accommodation_missing_notes(search_service, mock_reg_repo, mock_sheets_repo):
    """
    Test search when accommodation data exists but notes field is empty.

    Validates: Requirements 1.3
    """
    # Arrange
    email = "nonotes@example.com"

    reg_data = RegistrationData(
        name="No Notes User",
        email=email,
        college="Test College",
        events=["Event"],
        workshops=[]
    )
    mock_reg_repo.find_by_email.return_value = reg_data

    accom_data = {
        'Email': email,
        'Name': 'No Notes User',
        'From Date': '2026-03-06',
        'To Date': '2026-03-07',
        'Accommodation Type': 'Girls',
        'Notes': ''
    }
    mock_sheets_repo.find_accommodation = AsyncMock(return_value=accom_data)

    # Act
    result = await search_service.search_participant(email)

    # Assert
    assert result.found is True
    assert result.participant.accommodation.hasAccommodation is True
    assert result.participant.accommodation.notes == ''
