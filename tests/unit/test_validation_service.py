"""
Unit tests for ValidationService.

Tests specific examples, edge cases, and error handling for the
validation service.

Validates: Requirements 1.5, 3.3, 3.4
"""

import pytest
from app.services import ValidationService, ValidationError


class TestValidationService:
    """Test suite for ValidationService class."""

    @pytest.fixture
    def validator(self):
        """Create a ValidationService instance for testing."""
        return ValidationService()

    # Email Validation Tests

    def test_validate_email_valid_format(self, validator):
        """Test that valid email formats pass validation."""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "name+tag@subdomain.example.org",
            "user123@test-domain.com",
            "a@b.c"
        ]

        for email in valid_emails:
            # Should not raise exception
            validator.validate_email(email)

    def test_validate_email_invalid_format_no_at(self, validator):
        """Test that email without @ symbol fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("userexample.com")

        assert exc_info.value.field == "email"
        assert "@" in exc_info.value.message or "format" in exc_info.value.message.lower()

    def test_validate_email_invalid_format_no_domain(self, validator):
        """Test that email without domain fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("user@")

        assert exc_info.value.field == "email"

    def test_validate_email_invalid_format_no_tld(self, validator):
        """Test that email without TLD fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("user@domain")

        assert exc_info.value.field == "email"

    def test_validate_email_empty_string(self, validator):
        """Test that empty email string fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("")

        assert exc_info.value.field == "email"
        assert "empty" in exc_info.value.message.lower()

    def test_validate_email_whitespace_only(self, validator):
        """Test that whitespace-only email fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("   ")

        assert exc_info.value.field == "email"

    def test_validate_email_none(self, validator):
        """Test that None email fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email(None)

        assert exc_info.value.field == "email"

    def test_validate_email_with_spaces(self, validator):
        """Test that email with spaces fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_email("user name@example.com")

        assert exc_info.value.field == "email"

    # Date Validation Tests

    def test_validate_dates_valid_same_day(self, validator):
        """Test that same from and to dates are valid."""
        # Should not raise exception
        validator.validate_dates("2026-03-06", "2026-03-06")
        validator.validate_dates("2026-03-07", "2026-03-07")
        validator.validate_dates("2026-03-08", "2026-03-08")

    def test_validate_dates_valid_range(self, validator):
        """Test that valid date ranges pass validation."""
        valid_ranges = [
            ("2026-03-06", "2026-03-07"),
            ("2026-03-06", "2026-03-08"),
            ("2026-03-07", "2026-03-08")
        ]

        for from_date, to_date in valid_ranges:
            # Should not raise exception
            validator.validate_dates(from_date, to_date)

    def test_validate_dates_invalid_from_date(self, validator):
        """Test that invalid from_date fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("2026-03-05", "2026-03-06")

        assert exc_info.value.field == "fromDate"
        assert "2026-03-05" in exc_info.value.message

    def test_validate_dates_invalid_to_date(self, validator):
        """Test that invalid to_date fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("2026-03-06", "2026-03-09")

        assert exc_info.value.field == "toDate"
        assert "2026-03-09" in exc_info.value.message

    def test_validate_dates_from_after_to(self, validator):
        """Test that from_date > to_date fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("2026-03-08", "2026-03-06")

        assert exc_info.value.field == "dateRange"
        assert "less than or equal" in exc_info.value.message.lower()

    def test_validate_dates_empty_from_date(self, validator):
        """Test that empty from_date fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("", "2026-03-06")

        assert exc_info.value.field == "fromDate"

    def test_validate_dates_empty_to_date(self, validator):
        """Test that empty to_date fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("2026-03-06", "")

        assert exc_info.value.field == "toDate"

    def test_validate_dates_none_from_date(self, validator):
        """Test that None from_date fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates(None, "2026-03-06")

        assert exc_info.value.field == "fromDate"

    def test_validate_dates_none_to_date(self, validator):
        """Test that None to_date fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("2026-03-06", None)

        assert exc_info.value.field == "toDate"

    def test_validate_dates_wrong_year(self, validator):
        """Test that dates from wrong year fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("2025-03-06", "2025-03-07")

        assert exc_info.value.field == "fromDate"

    def test_validate_dates_wrong_month(self, validator):
        """Test that dates from wrong month fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_dates("2026-04-06", "2026-04-07")

        assert exc_info.value.field == "fromDate"

    # Accommodation Type Validation Tests

    def test_validate_accommodation_type_valid(self, validator):
        """Test that valid accommodation types pass validation."""
        valid_types = ["Boys", "Girls", "Other"]

        for acc_type in valid_types:
            # Should not raise exception
            validator.validate_accommodation_type(acc_type)

    def test_validate_accommodation_type_invalid(self, validator):
        """Test that invalid accommodation type fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_type("Mixed")

        assert exc_info.value.field == "accommodationType"
        assert "Mixed" in exc_info.value.message

    def test_validate_accommodation_type_case_sensitive(self, validator):
        """Test that accommodation type validation is case-sensitive."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_type("boys")  # lowercase

        assert exc_info.value.field == "accommodationType"

    def test_validate_accommodation_type_empty(self, validator):
        """Test that empty accommodation type fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_type("")

        assert exc_info.value.field == "accommodationType"

    def test_validate_accommodation_type_none(self, validator):
        """Test that None accommodation type fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_type(None)

        assert exc_info.value.field == "accommodationType"

    # Required Fields Validation Tests

    def test_validate_required_fields_all_present(self, validator):
        """Test that data with all required fields passes validation."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        # Should not raise exception
        validator.validate_required_fields(data)

    def test_validate_required_fields_missing_name(self, validator):
        """Test that missing name field fails validation."""
        data = {
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_required_fields(data)

        assert exc_info.value.field == "name"
        assert "missing" in exc_info.value.message.lower()

    def test_validate_required_fields_missing_email(self, validator):
        """Test that missing email field fails validation."""
        data = {
            "name": "John Doe",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_required_fields(data)

        assert exc_info.value.field == "email"

    def test_validate_required_fields_empty_name(self, validator):
        """Test that empty name field fails validation."""
        data = {
            "name": "",
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_required_fields(data)

        assert exc_info.value.field == "name"
        assert "empty" in exc_info.value.message.lower()

    def test_validate_required_fields_whitespace_only(self, validator):
        """Test that whitespace-only field fails validation."""
        data = {
            "name": "   ",
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_required_fields(data)

        assert exc_info.value.field == "name"

    def test_validate_required_fields_none_value(self, validator):
        """Test that None field value fails validation."""
        data = {
            "name": None,
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_required_fields(data)

        assert exc_info.value.field == "name"
        assert "None" in exc_info.value.message

    # Text Field Validation Tests

    def test_validate_text_field_valid(self, validator):
        """Test that valid text field passes validation."""
        # Should not raise exception
        validator.validate_text_field(
            "name", "John Doe", min_length=1, max_length=200)

    def test_validate_text_field_too_short(self, validator):
        """Test that text field below minimum length fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            validator.validate_text_field(
                "name", "", min_length=1, max_length=200)

        assert exc_info.value.field == "name"

    def test_validate_text_field_too_long(self, validator):
        """Test that text field exceeding maximum length fails validation."""
        long_text = "a" * 201

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_text_field(
                "name", long_text, min_length=1, max_length=200)

        assert exc_info.value.field == "name"
        assert "200" in exc_info.value.message

    def test_validate_text_field_exact_max_length(self, validator):
        """Test that text field at exact maximum length passes validation."""
        text = "a" * 200

        # Should not raise exception
        validator.validate_text_field(
            "name", text, min_length=1, max_length=200)

    # Complete Accommodation Data Validation Tests

    def test_validate_accommodation_data_valid(self, validator):
        """Test that valid accommodation data passes all validations."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys",
            "notes": "Late arrival"
        }

        # Should not raise exception
        validator.validate_accommodation_data(data)

    def test_validate_accommodation_data_without_notes(self, validator):
        """Test that accommodation data without optional notes passes validation."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        # Should not raise exception
        validator.validate_accommodation_data(data)

    def test_validate_accommodation_data_notes_too_long(self, validator):
        """Test that notes exceeding 500 characters fail validation."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys",
            "notes": "a" * 501
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_data(data)

        assert exc_info.value.field == "notes"
        assert "500" in exc_info.value.message

    def test_validate_accommodation_data_invalid_email(self, validator):
        """Test that invalid email in accommodation data fails validation."""
        data = {
            "name": "John Doe",
            "email": "invalid-email",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_data(data)

        assert exc_info.value.field == "email"

    def test_validate_accommodation_data_invalid_date_range(self, validator):
        """Test that invalid date range in accommodation data fails validation."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-08",
            "toDate": "2026-03-06",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_data(data)

        assert exc_info.value.field == "dateRange"

    def test_validate_accommodation_data_name_too_long(self, validator):
        """Test that name exceeding 200 characters fails validation."""
        data = {
            "name": "a" * 201,
            "email": "john@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_data(data)

        assert exc_info.value.field == "name"

    def test_validate_accommodation_data_college_too_long(self, validator):
        """Test that college exceeding 200 characters fails validation."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "college": "a" * 201,
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys"
        }

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_accommodation_data(data)

        assert exc_info.value.field == "college"
