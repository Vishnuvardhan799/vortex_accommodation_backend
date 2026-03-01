"""
Property-based tests for Google Sheets integration.

Tests universal properties that should hold for all inputs related to
Google Sheets operations, particularly row structure and data integrity.
"""

import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from datetime import datetime

from app.models.schemas import AccommodationEntry
from app.repositories.sheets_repository import SheetsRepository


@settings(max_examples=100)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"]),
    notes=st.one_of(st.none(), st.text(max_size=500)),
    entered_by=st.emails()
)
def test_property_11_sheet_row_structure(
    name, email, college, from_date, to_date, accom_type, notes, entered_by
):
    """
    **Validates: Requirements 5.3**

    Property 11: Sheet Row Structure

    For any accommodation entry appended to the Google Sheet, the resulting row
    should contain exactly 9 columns in order: Timestamp, Name, Email, College,
    From Date, To Date, Accommodation Type, Notes, Entered By.

    This test validates that the _entry_to_row method in SheetsRepository
    correctly converts an AccommodationEntry to a row with the proper structure.
    """
    # Only test valid cases where date range is valid
    if from_date <= to_date:
        # Arrange: Create an AccommodationEntry
        entry = AccommodationEntry(
            name=name,
            email=email,
            college=college,
            fromDate=from_date,
            toDate=to_date,
            accommodationType=accom_type,
            notes=notes,
            enteredBy=entered_by
        )

        # Create a SheetsRepository instance (we'll use the _entry_to_row method)
        # Note: We don't need actual Google Sheets connection for this test
        # We're testing the data transformation logic only
        repo = SheetsRepository.__new__(SheetsRepository)

        # Act: Convert entry to row format
        row = repo._entry_to_row(entry)

        # Assert: Row should have exactly 9 columns
        assert len(row) == 9, f"Expected 9 columns, got {len(row)}"

        # Assert: Verify column order and content
        # Column 0: Timestamp (ISO format string)
        assert isinstance(row[0], str), "Timestamp should be a string"
        assert row[0] == entry.timestamp.isoformat(
        ), "Timestamp should match entry timestamp"

        # Column 1: Name
        assert row[1] == name, "Name should match entry name"

        # Column 2: Email
        assert row[2] == email, "Email should match entry email"

        # Column 3: College
        assert row[3] == college, "College should match entry college"

        # Column 4: From Date
        assert row[4] == from_date, "From Date should match entry fromDate"

        # Column 5: To Date
        assert row[5] == to_date, "To Date should match entry toDate"

        # Column 6: Accommodation Type
        assert row[6] == accom_type, "Accommodation Type should match entry accommodationType"

        # Column 7: Notes (empty string if None)
        expected_notes = notes if notes is not None else ""
        assert row[7] == expected_notes, "Notes should match entry notes or be empty string"

        # Column 8: Entered By
        assert row[8] == entered_by, "Entered By should match entry enteredBy"


@settings(max_examples=50)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"]),
    entered_by=st.emails()
)
def test_property_11_sheet_row_structure_without_notes(
    name, email, college, from_date, to_date, accom_type, entered_by
):
    """
    **Validates: Requirements 5.3**

    Property 11: Sheet Row Structure (Notes Optional)

    For any accommodation entry without notes, the resulting row should still
    contain exactly 9 columns with an empty string for the notes field.

    This test specifically validates the handling of optional notes field.
    """
    # Only test valid cases where date range is valid
    if from_date <= to_date:
        # Arrange: Create an AccommodationEntry without notes
        entry = AccommodationEntry(
            name=name,
            email=email,
            college=college,
            fromDate=from_date,
            toDate=to_date,
            accommodationType=accom_type,
            notes=None,  # Explicitly set notes to None
            enteredBy=entered_by
        )

        # Create a SheetsRepository instance
        repo = SheetsRepository.__new__(SheetsRepository)

        # Act: Convert entry to row format
        row = repo._entry_to_row(entry)

        # Assert: Row should have exactly 9 columns
        assert len(row) == 9, f"Expected 9 columns, got {len(row)}"

        # Assert: Notes field (column 7) should be empty string, not None
        assert row[7] == "", "Notes should be empty string when None"
        assert row[7] is not None, "Notes should not be None in row"


@settings(max_examples=50)
@given(
    name=st.text(min_size=1, max_size=200),
    email=st.emails(),
    college=st.text(min_size=1, max_size=200),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"]),
    entered_by=st.emails()
)
def test_property_11_sheet_row_column_order(
    name, email, college, from_date, to_date, accom_type, entered_by
):
    """
    **Validates: Requirements 5.3**

    Property 11: Sheet Row Structure (Column Order)

    For any accommodation entry, the columns must be in the exact order specified:
    Timestamp, Name, Email, College, From Date, To Date, Accommodation Type, Notes, Entered By.

    This test validates that the column order is strictly maintained.
    """
    # Only test valid cases where date range is valid
    if from_date <= to_date:
        # Arrange: Create an AccommodationEntry
        entry = AccommodationEntry(
            name=name,
            email=email,
            college=college,
            fromDate=from_date,
            toDate=to_date,
            accommodationType=accom_type,
            notes="Test notes",
            enteredBy=entered_by
        )

        # Create a SheetsRepository instance
        repo = SheetsRepository.__new__(SheetsRepository)

        # Act: Convert entry to row format
        row = repo._entry_to_row(entry)

        # Assert: Verify exact column positions
        # This ensures the order is maintained regardless of how the entry is created
        column_names = [
            "Timestamp",
            "Name",
            "Email",
            "College",
            "From Date",
            "To Date",
            "Accommodation Type",
            "Notes",
            "Entered By"
        ]

        # Verify we have the expected number of columns
        assert len(row) == len(column_names), \
            f"Expected {len(column_names)} columns, got {len(row)}"

        # Verify each column contains the expected data type and value
        # Column 0: Timestamp - should be ISO format string
        assert isinstance(row[0], str) and 'T' in row[0], \
            f"Column 0 (Timestamp) should be ISO format string, got {type(row[0])}"

        # Column 1: Name - should be string
        assert isinstance(row[1], str) and row[1] == name, \
            f"Column 1 (Name) should be string matching entry name"

        # Column 2: Email - should be string
        assert isinstance(row[2], str) and '@' in row[2], \
            f"Column 2 (Email) should be valid email string"

        # Column 3: College - should be string
        assert isinstance(row[3], str) and row[3] == college, \
            f"Column 3 (College) should be string matching entry college"

        # Column 4: From Date - should be date string
        assert isinstance(row[4], str) and row[4] in ["2026-03-06", "2026-03-07", "2026-03-08"], \
            f"Column 4 (From Date) should be valid date string"

        # Column 5: To Date - should be date string
        assert isinstance(row[5], str) and row[5] in ["2026-03-06", "2026-03-07", "2026-03-08"], \
            f"Column 5 (To Date) should be valid date string"

        # Column 6: Accommodation Type - should be one of the valid types
        assert row[6] in ["Boys", "Girls", "Other"], \
            f"Column 6 (Accommodation Type) should be Boys, Girls, or Other"

        # Column 7: Notes - should be string (empty or with content)
        assert isinstance(row[7], str), \
            f"Column 7 (Notes) should be string"

        # Column 8: Entered By - should be string (email)
        assert isinstance(row[8], str) and '@' in row[8], \
            f"Column 8 (Entered By) should be valid email string"
