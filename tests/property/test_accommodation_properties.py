"""
Property-based tests for AccommodationService.

Tests universal properties that should hold for all valid inputs.
Uses Hypothesis for property-based testing.
"""

import pytest
from hypothesis import given, settings, assume
import hypothesis.strategies as st
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from app.models import AccommodationRequest
from app.services.accommodation_service import AccommodationService
from app.services.validation_service import ValidationService


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
    notes=st.one_of(st.none(), st.text(max_size=500)),
    volunteer_email=st.emails()
)
@pytest.mark.asyncio
async def test_property_automatic_field_population(
    name, email, college, from_date, to_date, accom_type, notes, volunteer_email
):
    """
    Property 8: Automatic Field Population

    **Validates: Requirements 3.5, 3.6**

    For any accommodation entry successfully created, the stored entry should
    contain both a timestamp field (not present in the original request) and
    an enteredBy field (populated from the authenticated volunteer), regardless
    of whether these fields were included in the request.
    """
    # Only test valid date ranges
    assume(from_date <= to_date)

    # Arrange: Create mock repositories
    sheets_repo = MagicMock()
    validator = ValidationService()

    # Mock sheets repository to not find duplicates
    sheets_repo.find_accommodation = AsyncMock(return_value=None)
    sheets_repo.append_accommodation = AsyncMock()

    # Create service
    accom_service = AccommodationService(sheets_repo, validator)

    # Create request (without timestamp and enteredBy)
    request = AccommodationRequest(
        name=name,
        email=email,
        college=college,
        fromDate=from_date,
        toDate=to_date,
        accommodationType=accom_type,
        notes=notes,
        force=False
    )

    # Record time before creation
    time_before = datetime.utcnow()

    # Act: Create accommodation entry
    result = await accom_service.create_accommodation(
        request,
        volunteer_email,
        force=False
    )

    # Record time after creation
    time_after = datetime.utcnow()

    # Assert: Entry should be created successfully
    assert result.success is True, "Entry creation should succeed"
    assert result.entry is not None, "Entry should be present in response"

    # Verify automatic timestamp field population
    assert result.entry.timestamp is not None, \
        "Timestamp should be automatically populated"
    assert isinstance(result.entry.timestamp, datetime), \
        "Timestamp should be a datetime object"
    assert time_before <= result.entry.timestamp <= time_after, \
        "Timestamp should be within the creation time window"

    # Verify automatic enteredBy field population
    assert result.entry.enteredBy is not None, \
        "enteredBy should be automatically populated"
    assert result.entry.enteredBy == volunteer_email, \
        f"enteredBy should be set to volunteer email: {volunteer_email}"

    # Verify user-provided fields are preserved
    assert result.entry.name == name
    assert result.entry.email == email
    assert result.entry.college == college
    assert result.entry.fromDate == from_date
    assert result.entry.toDate == to_date
    assert result.entry.accommodationType == accom_type
    assert result.entry.notes == notes


@settings(max_examples=100, deadline=None)
@given(
    name=st.text(min_size=1, max_size=100),
    email=st.emails(),
    college=st.text(min_size=1, max_size=100),
    from_date=valid_dates,
    to_date=valid_dates,
    accom_type=accommodation_types,
    volunteer_email=st.emails()
)
@pytest.mark.asyncio
async def test_property_duplicate_detection(
    name, email, college, from_date, to_date, accom_type, volunteer_email
):
    """
    Property 9: Duplicate Detection

    **Validates: Requirements 4.1**

    For any email address that already has an accommodation entry in the sheet,
    attempting to create a new accommodation entry with the same email (without
    force flag) should return a duplicate warning response instead of creating
    the entry.
    """
    # Only test valid date ranges
    assume(from_date <= to_date)

    # Arrange: Create mock repositories
    sheets_repo = MagicMock()
    validator = ValidationService()

    # Mock existing accommodation entry
    existing_entry = {
        'Email': email,
        'Name': 'Existing User',
        'From Date': '2026-03-06',
        'To Date': '2026-03-07',
        'Accommodation Type': 'Boys'
    }
    sheets_repo.find_accommodation = AsyncMock(return_value=existing_entry)
    sheets_repo.append_accommodation = AsyncMock()

    # Create service
    accom_service = AccommodationService(sheets_repo, validator)

    # Create request
    request = AccommodationRequest(
        name=name,
        email=email,
        college=college,
        fromDate=from_date,
        toDate=to_date,
        accommodationType=accom_type,
        notes=None,
        force=False
    )

    # Act: Attempt to create duplicate entry
    result = await accom_service.create_accommodation(
        request,
        volunteer_email,
        force=False
    )

    # Assert: Should return duplicate warning
    assert result.success is False, \
        "Creation should fail when duplicate exists"
    assert result.duplicate is True, \
        "duplicate flag should be True"
    assert result.existingEntry is not None, \
        "Existing entry information should be provided"
    assert "already exists" in result.message.lower(), \
        "Message should indicate duplicate exists"

    # Verify append was NOT called
    sheets_repo.append_accommodation.assert_not_called()


@settings(max_examples=100, deadline=None)
@given(
    name=st.text(min_size=1, max_size=100),
    email=st.emails(),
    college=st.text(min_size=1, max_size=100),
    from_date=valid_dates,
    to_date=valid_dates,
    accom_type=accommodation_types,
    volunteer_email=st.emails()
)
@pytest.mark.asyncio
async def test_property_force_flag_override(
    name, email, college, from_date, to_date, accom_type, volunteer_email
):
    """
    Property 10: Force Flag Override

    **Validates: Requirements 4.3**

    For any email address that already has an accommodation entry, submitting
    a new accommodation entry with force=true should successfully create and
    append the new entry to the sheet, resulting in multiple entries for the
    same email.
    """
    # Only test valid date ranges
    assume(from_date <= to_date)

    # Arrange: Create mock repositories
    sheets_repo = MagicMock()
    validator = ValidationService()

    # Mock existing accommodation entry
    existing_entry = {
        'Email': email,
        'Name': 'Existing User',
        'From Date': '2026-03-06',
        'To Date': '2026-03-07',
        'Accommodation Type': 'Boys'
    }
    sheets_repo.find_accommodation = AsyncMock(return_value=existing_entry)
    sheets_repo.append_accommodation = AsyncMock()

    # Create service
    accom_service = AccommodationService(sheets_repo, validator)

    # Create request with force=True
    request = AccommodationRequest(
        name=name,
        email=email,
        college=college,
        fromDate=from_date,
        toDate=to_date,
        accommodationType=accom_type,
        notes=None,
        force=True
    )

    # Act: Create entry with force flag
    result = await accom_service.create_accommodation(
        request,
        volunteer_email,
        force=True
    )

    # Assert: Entry should be created successfully despite duplicate
    assert result.success is True, \
        "Creation should succeed with force=True even when duplicate exists"
    assert result.duplicate is False, \
        "duplicate flag should be False when force is used"
    assert result.entry is not None, \
        "Entry should be present in response"

    # Verify append WAS called
    sheets_repo.append_accommodation.assert_called_once()

    # Verify the entry has correct data
    assert result.entry.email == email
    assert result.entry.name == name
    assert result.entry.enteredBy == volunteer_email
