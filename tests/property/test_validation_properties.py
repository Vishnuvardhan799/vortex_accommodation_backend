"""
Property-based tests for validation logic.

Tests universal properties that should hold for all inputs related to
validation of emails, dates, and other form fields.
"""

import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from pydantic import ValidationError

from app.models.schemas import SearchRequest, AccommodationRequest, AccommodationEntry


@settings(max_examples=100)
@given(invalid_email=st.text().filter(lambda s: '@' not in s or '.' not in s))
def test_property_3_email_format_validation_search_request(invalid_email):
    """
    **Validates: Requirements 1.5, 3.4**

    Property 3: Email Format Validation

    For any string that does not match the email format pattern (contains @ symbol,
    has domain, has TLD), submitting it as a search query should result in a
    validation error response.

    This test validates that SearchRequest properly rejects invalid email formats.
    """
    # Act & Assert: Invalid email should raise validation error
    with pytest.raises(ValidationError) as exc_info:
        SearchRequest(email=invalid_email)

    # Verify the error is related to email validation
    error_str = str(exc_info.value).lower()
    assert "email" in error_str or "value_error" in error_str


@settings(max_examples=100)
@given(invalid_email=st.text().filter(lambda s: '@' not in s or '.' not in s))
def test_property_3_email_format_validation_accommodation_request(invalid_email):
    """
    **Validates: Requirements 1.5, 3.4**

    Property 3: Email Format Validation

    For any string that does not match the email format pattern (contains @ symbol,
    has domain, has TLD), submitting it in an accommodation form should result in a
    validation error response.

    This test validates that AccommodationRequest properly rejects invalid email formats.
    """
    # Act & Assert: Invalid email should raise validation error
    with pytest.raises(ValidationError) as exc_info:
        AccommodationRequest(
            name="Test User",
            email=invalid_email,
            college="Test College",
            fromDate="2026-03-06",
            toDate="2026-03-08",
            accommodationType="Boys"
        )

    # Verify the error is related to email validation
    error_str = str(exc_info.value).lower()
    assert "email" in error_str or "value_error" in error_str


@settings(max_examples=100)
@given(valid_email=st.emails())
def test_property_3_valid_email_acceptance_search_request(valid_email):
    """
    **Validates: Requirements 1.5, 3.4**

    Property 3: Email Format Validation (Inverse Property)

    For any string that matches the email format pattern, submitting it as a
    search query should NOT result in a validation error.

    This test validates that SearchRequest accepts valid email formats.
    """
    # Act: Valid email should not raise validation error
    try:
        request = SearchRequest(email=valid_email)
        # Assert: Email should be stored correctly
        assert request.email == valid_email
    except ValidationError:
        pytest.fail(f"Valid email {valid_email} was rejected")


@settings(max_examples=100)
@given(
    valid_email=st.emails(),
    name=st.text(min_size=1, max_size=200),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_3_valid_email_acceptance_accommodation_request(
    valid_email, name, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 1.5, 3.4**

    Property 3: Email Format Validation (Inverse Property)

    For any string that matches the email format pattern, submitting it in an
    accommodation form should NOT result in a validation error (assuming other
    fields are valid).

    This test validates that AccommodationRequest accepts valid email formats.
    """
    # Only test cases where date range is valid
    if from_date <= to_date:
        # Act: Valid email should not raise validation error
        try:
            request = AccommodationRequest(
                name=name,
                email=valid_email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type
            )
            # Assert: Email should be stored correctly
            assert request.email == valid_email
        except ValidationError as e:
            # If validation fails, it should not be due to email format
            error_str = str(e).lower()
            if "email" in error_str:
                pytest.fail(f"Valid email {valid_email} was rejected: {e}")


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_7_date_range_validation_accommodation_request(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.3**

    Property 7: Date Range Validation

    For any accommodation form submission where the fromDate is chronologically
    after the toDate, the system should reject the submission with a validation
    error indicating invalid date range.

    This test validates that AccommodationRequest properly rejects invalid date ranges.
    """
    # Only test invalid cases where from_date > to_date
    if from_date > to_date:
        # Act & Assert: Invalid date range should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            AccommodationRequest(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type
            )

        # Verify the error is related to date validation
        error_str = str(exc_info.value).lower()
        assert "date" in error_str or "todate" in error_str


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_7_date_range_validation_accommodation_entry(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.3**

    Property 7: Date Range Validation

    For any accommodation entry where the fromDate is chronologically after the
    toDate, the system should reject the entry with a validation error indicating
    invalid date range.

    This test validates that AccommodationEntry properly rejects invalid date ranges.
    """
    # Only test invalid cases where from_date > to_date
    if from_date > to_date:
        # Act & Assert: Invalid date range should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            AccommodationEntry(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type,
                enteredBy="volunteer@example.com"
            )

        # Verify the error is related to date validation
        error_str = str(exc_info.value).lower()
        assert "date" in error_str or "todate" in error_str


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_7_valid_date_range_acceptance_accommodation_request(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.3**

    Property 7: Date Range Validation (Inverse Property)

    For any accommodation form submission where the fromDate is less than or equal
    to the toDate, the system should accept the date range without validation error.

    This test validates that AccommodationRequest accepts valid date ranges.
    """
    # Only test valid cases where from_date <= to_date
    if from_date <= to_date:
        # Act: Valid date range should not raise validation error
        try:
            request = AccommodationRequest(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type
            )
            # Assert: Dates should be stored correctly
            assert request.fromDate == from_date
            assert request.toDate == to_date
        except ValidationError as e:
            # If validation fails, it should not be due to date range
            error_str = str(e).lower()
            if "date" in error_str or "todate" in error_str:
                pytest.fail(
                    f"Valid date range {from_date} to {to_date} was rejected: {e}")


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_7_valid_date_range_acceptance_accommodation_entry(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.3**

    Property 7: Date Range Validation (Inverse Property)

    For any accommodation entry where the fromDate is less than or equal to the
    toDate, the system should accept the date range without validation error.

    This test validates that AccommodationEntry accepts valid date ranges.
    """
    # Only test valid cases where from_date <= to_date
    if from_date <= to_date:
        # Act: Valid date range should not raise validation error
        try:
            entry = AccommodationEntry(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type,
                enteredBy="volunteer@example.com"
            )
            # Assert: Dates should be stored correctly
            assert entry.fromDate == from_date
            assert entry.toDate == to_date
        except ValidationError as e:
            # If validation fails, it should not be due to date range
            error_str = str(e).lower()
            if "date" in error_str or "todate" in error_str:
                pytest.fail(
                    f"Valid date range {from_date} to {to_date} was rejected: {e}")


@settings(max_examples=100)
@given(
    name=st.one_of(st.none(), st.just(""), st.text(min_size=1, max_size=200)),
    email=st.one_of(st.none(), st.just(""), st.emails()),
    college=st.one_of(st.none(), st.just(
        ""), st.text(min_size=1, max_size=200)),
    from_date=st.one_of(st.none(), st.just(""), st.sampled_from(
        ["2026-03-06", "2026-03-07", "2026-03-08"])),
    to_date=st.one_of(st.none(), st.just(""), st.sampled_from(
        ["2026-03-06", "2026-03-07", "2026-03-08"])),
    accom_type=st.one_of(st.none(), st.just(
        ""), st.sampled_from(["Boys", "Girls", "Other"]))
)
def test_property_6_required_fields_validation_accommodation_request(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.2**

    Property 6: Required Fields Validation

    For any accommodation form submission where one or more required fields
    (name, email, fromDate, toDate, accommodationType) are missing or empty,
    the system should reject the submission with a validation error.

    This test validates that AccommodationRequest properly rejects submissions
    with missing or empty required fields.
    """
    # Check if any required field is missing or empty
    has_missing_or_empty = (
        name is None or name == "" or
        email is None or email == "" or
        college is None or college == "" or
        from_date is None or from_date == "" or
        to_date is None or to_date == "" or
        accom_type is None or accom_type == ""
    )

    if has_missing_or_empty:
        # Act & Assert: Missing or empty required fields should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            AccommodationRequest(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type
            )

        # Verify that a validation error was raised
        assert exc_info.value is not None


@settings(max_examples=100)
@given(
    name=st.one_of(st.none(), st.just(""), st.text(min_size=1, max_size=200)),
    email=st.one_of(st.none(), st.just(""), st.emails()),
    college=st.one_of(st.none(), st.just(
        ""), st.text(min_size=1, max_size=200)),
    from_date=st.one_of(st.none(), st.just(""), st.sampled_from(
        ["2026-03-06", "2026-03-07", "2026-03-08"])),
    to_date=st.one_of(st.none(), st.just(""), st.sampled_from(
        ["2026-03-06", "2026-03-07", "2026-03-08"])),
    accom_type=st.one_of(st.none(), st.just(
        ""), st.sampled_from(["Boys", "Girls", "Other"]))
)
def test_property_6_required_fields_validation_accommodation_entry(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.2**

    Property 6: Required Fields Validation

    For any accommodation entry where one or more required fields
    (name, email, fromDate, toDate, accommodationType) are missing or empty,
    the system should reject the entry with a validation error.

    This test validates that AccommodationEntry properly rejects entries
    with missing or empty required fields.
    """
    # Check if any required field is missing or empty
    has_missing_or_empty = (
        name is None or name == "" or
        email is None or email == "" or
        college is None or college == "" or
        from_date is None or from_date == "" or
        to_date is None or to_date == "" or
        accom_type is None or accom_type == ""
    )

    if has_missing_or_empty:
        # Act & Assert: Missing or empty required fields should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            AccommodationEntry(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type,
                enteredBy="volunteer@example.com"
            )

        # Verify that a validation error was raised
        assert exc_info.value is not None


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_6_all_required_fields_present_accommodation_request(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.2**

    Property 6: Required Fields Validation (Inverse Property)

    For any accommodation form submission where all required fields
    (name, email, fromDate, toDate, accommodationType) are present and non-empty,
    the system should accept the submission without validation error related to
    missing fields.

    This test validates that AccommodationRequest accepts submissions with all
    required fields present.
    """
    # Only test valid cases where date range is valid
    if from_date <= to_date:
        # Act: All required fields present should not raise validation error
        try:
            request = AccommodationRequest(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type
            )
            # Assert: All fields should be stored correctly
            assert request.name == name
            assert request.email == email
            assert request.college == college
            assert request.fromDate == from_date
            assert request.toDate == to_date
            assert request.accommodationType == accom_type
        except ValidationError as e:
            # If validation fails, it should not be due to missing required fields
            error_str = str(e).lower()
            # Check that error is not about required fields
            if "required" in error_str or "missing" in error_str or "none" in error_str:
                pytest.fail(
                    f"Valid submission with all required fields was rejected: {e}")


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_6_all_required_fields_present_accommodation_entry(
    name, email, college, from_date, to_date, accom_type
):
    """
    **Validates: Requirements 3.2**

    Property 6: Required Fields Validation (Inverse Property)

    For any accommodation entry where all required fields
    (name, email, fromDate, toDate, accommodationType, enteredBy) are present
    and non-empty, the system should accept the entry without validation error
    related to missing fields.

    This test validates that AccommodationEntry accepts entries with all
    required fields present.
    """
    # Only test valid cases where date range is valid
    if from_date <= to_date:
        # Act: All required fields present should not raise validation error
        try:
            entry = AccommodationEntry(
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type,
                enteredBy="volunteer@example.com"
            )
            # Assert: All fields should be stored correctly
            assert entry.name == name
            assert entry.email == email
            assert entry.college == college
            assert entry.fromDate == from_date
            assert entry.toDate == to_date
            assert entry.accommodationType == accom_type
            assert entry.enteredBy == "volunteer@example.com"
        except ValidationError as e:
            # If validation fails, it should not be due to missing required fields
            error_str = str(e).lower()
            # Check that error is not about required fields
            if "required" in error_str or "missing" in error_str or "none" in error_str:
                pytest.fail(
                    f"Valid entry with all required fields was rejected: {e}")
