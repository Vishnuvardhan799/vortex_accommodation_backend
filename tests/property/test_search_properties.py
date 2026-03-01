"""
Property-based tests for SearchService.

Tests universal properties that should hold for all valid inputs.
Uses Hypothesis for property-based testing.
"""

import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from unittest.mock import AsyncMock, MagicMock

from app.models import RegistrationData, AccommodationStatus
from app.services.search_service import SearchService


# Strategy for generating valid dates
valid_dates = st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"])

# Strategy for generating accommodation types
accommodation_types = st.sampled_from(["Boys", "Girls", "Other"])


@settings(max_examples=100, deadline=None)
@given(
    name=st.text(min_size=1, max_size=100),
    email=st.emails(),
    college=st.text(min_size=1, max_size=100),
    from_date=valid_dates,
    to_date=valid_dates,
    accom_type=accommodation_types,
    notes=st.one_of(st.none(), st.text(max_size=500))
)
@pytest.mark.asyncio
async def test_property_accommodation_status_in_search(
    name, email, college, from_date, to_date, accom_type, notes
):
    """
    Property 2: Accommodation Status in Search

    **Validates: Requirements 1.3**

    For any participant email that has an accommodation entry, searching by
    that email should return accommodation data containing status, from date,
    and to date fields.
    """
    # Only test valid date ranges
    if from_date > to_date:
        return

    # Arrange: Create mock repositories
    reg_repo = MagicMock()
    sheets_repo = MagicMock()

    # Mock registration data
    reg_data = RegistrationData(
        name=name,
        email=email,
        college=college,
        events=["Event 1"],
        workshops=["Workshop 1"]
    )
    reg_repo.find_by_email.return_value = reg_data

    # Mock accommodation data (exists)
    accom_data = {
        'Email': email,
        'Name': name,
        'From Date': from_date,
        'To Date': to_date,
        'Accommodation Type': accom_type,
        'Notes': notes or ""
    }
    sheets_repo.find_accommodation = AsyncMock(return_value=accom_data)

    # Create service
    search_service = SearchService(reg_repo, sheets_repo)

    # Act: Search for participant
    result = await search_service.search_participant(email)

    # Assert: Accommodation data should be present with all required fields
    assert result.found is True, "Participant should be found"
    assert result.participant is not None, "Participant data should be present"

    # Verify accommodation status is present
    accommodation = result.participant.accommodation
    assert accommodation is not None, "Accommodation status should be present"

    # Verify accommodation has required fields
    assert accommodation.hasAccommodation is True, \
        "hasAccommodation should be True when accommodation exists"
    assert accommodation.fromDate == from_date, \
        f"fromDate should be {from_date}"
    assert accommodation.toDate == to_date, \
        f"toDate should be {to_date}"
    assert accommodation.type == accom_type, \
        f"type should be {accom_type}"
