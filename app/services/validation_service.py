"""
Validation Service for the Vortex 2026 Accommodation System.

This module provides centralized validation logic for accommodation data,
including email format validation, date validation, and required field checks.

Validates: Requirements 1.5, 3.2, 3.3, 3.4
"""

import re
from typing import Any, Dict, List
from pydantic import EmailStr, ValidationError as PydanticValidationError


class ValidationError(Exception):
    """
    Custom exception for validation failures.

    Raised when input data fails validation checks.
    """

    def __init__(self, field: str, message: str):
        """
        Initialize validation error.

        Args:
            field: The field that failed validation
            message: Description of the validation failure
        """
        self.field = field
        self.message = message
        super().__init__(f"Validation error on {field}: {message}")


class ValidationService:
    """
    Service for validating accommodation and registration data.

    Provides methods for validating email formats, date ranges,
    accommodation types, and required fields.

    Validates: Requirements 1.5, 3.2, 3.3, 3.4
    """

    # Valid dates for Vortex 2026 event
    VALID_DATES = ["2026-03-06", "2026-03-07", "2026-03-08"]

    # Valid accommodation types
    VALID_TYPES = ["Boys", "Girls", "Other"]

    # Email validation regex pattern
    EMAIL_REGEX = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'

    def validate_email(self, email: str) -> None:
        """
        Validate email format.

        Checks that the email matches the expected format pattern:
        - Contains @ symbol
        - Has domain name
        - Has top-level domain

        Args:
            email: Email address to validate

        Raises:
            ValidationError: If email format is invalid

        Validates: Requirements 1.5, 3.4
        """
        if not email or not isinstance(email, str):
            raise ValidationError(
                "email", "Email is required and must be a string")

        email = email.strip()

        if not email:
            raise ValidationError("email", "Email cannot be empty")

        if not re.match(self.EMAIL_REGEX, email):
            raise ValidationError(
                "email",
                "Invalid email format. Email must contain @ symbol, domain, and TLD"
            )

    def validate_dates(self, from_date: str, to_date: str) -> None:
        """
        Validate accommodation date range.

        Checks that:
        - Both dates are in the valid date list (March 6-8, 2026)
        - from_date is less than or equal to to_date

        Args:
            from_date: Accommodation start date (YYYY-MM-DD format)
            to_date: Accommodation end date (YYYY-MM-DD format)

        Raises:
            ValidationError: If dates are invalid or out of range

        Validates: Requirements 3.3
        """
        # Validate from_date
        if not from_date or not isinstance(from_date, str):
            raise ValidationError(
                "fromDate", "From date is required and must be a string")

        if from_date not in self.VALID_DATES:
            raise ValidationError(
                "fromDate",
                f"Invalid from_date: {from_date}. Must be one of {', '.join(self.VALID_DATES)}"
            )

        # Validate to_date
        if not to_date or not isinstance(to_date, str):
            raise ValidationError(
                "toDate", "To date is required and must be a string")

        if to_date not in self.VALID_DATES:
            raise ValidationError(
                "toDate",
                f"Invalid to_date: {to_date}. Must be one of {', '.join(self.VALID_DATES)}"
            )

        # Validate date range
        if from_date > to_date:
            raise ValidationError(
                "dateRange",
                f"from_date ({from_date}) must be less than or equal to to_date ({to_date})"
            )

    def validate_accommodation_type(self, accommodation_type: str) -> None:
        """
        Validate accommodation type.

        Checks that the accommodation type is one of the valid options:
        Boys, Girls, or Other.

        Args:
            accommodation_type: Type of accommodation

        Raises:
            ValidationError: If accommodation type is invalid

        Validates: Requirements 3.2
        """
        if not accommodation_type or not isinstance(accommodation_type, str):
            raise ValidationError(
                "accommodationType",
                "Accommodation type is required and must be a string"
            )

        if accommodation_type not in self.VALID_TYPES:
            raise ValidationError(
                "accommodationType",
                f"Invalid accommodation type: {accommodation_type}. Must be one of {', '.join(self.VALID_TYPES)}"
            )

    def validate_required_fields(self, data: Dict[str, Any]) -> None:
        """
        Validate that all required fields are present and non-empty.

        Required fields for accommodation entry:
        - name
        - email
        - college
        - fromDate
        - toDate
        - accommodationType

        Args:
            data: Dictionary containing accommodation data

        Raises:
            ValidationError: If any required field is missing or empty

        Validates: Requirements 3.2
        """
        required_fields = [
            "name",
            "email",
            "college",
            "fromDate",
            "toDate",
            "accommodationType"
        ]

        for field in required_fields:
            if field not in data:
                raise ValidationError(
                    field, f"Required field '{field}' is missing")

            value = data[field]

            # Check for None or empty string
            if value is None:
                raise ValidationError(
                    field, f"Required field '{field}' cannot be None")

            if isinstance(value, str) and not value.strip():
                raise ValidationError(
                    field, f"Required field '{field}' cannot be empty")

    def validate_text_field(self, field_name: str, value: str, min_length: int = 1, max_length: int = 200) -> None:
        """
        Validate a text field for length constraints.

        Args:
            field_name: Name of the field being validated
            value: Text value to validate
            min_length: Minimum allowed length (default: 1)
            max_length: Maximum allowed length (default: 200)

        Raises:
            ValidationError: If text length is invalid
        """
        if not value or not isinstance(value, str):
            raise ValidationError(
                field_name, f"{field_name} must be a non-empty string")

        value = value.strip()

        if len(value) < min_length:
            raise ValidationError(
                field_name,
                f"{field_name} must be at least {min_length} character(s) long"
            )

        if len(value) > max_length:
            raise ValidationError(
                field_name,
                f"{field_name} must not exceed {max_length} characters"
            )

    def validate_accommodation_data(self, data: Dict[str, Any]) -> None:
        """
        Validate complete accommodation form data.

        Performs comprehensive validation including:
        - Required fields check
        - Email format validation
        - Date range validation
        - Accommodation type validation
        - Text field length validation

        Args:
            data: Dictionary containing accommodation data

        Raises:
            ValidationError: If any validation check fails

        Validates: Requirements 1.5, 3.2, 3.3, 3.4
        """
        # Validate required fields are present
        self.validate_required_fields(data)

        # Validate email format
        self.validate_email(data["email"])

        # Validate dates
        self.validate_dates(data["fromDate"], data["toDate"])

        # Validate accommodation type
        self.validate_accommodation_type(data["accommodationType"])

        # Validate text fields
        self.validate_text_field(
            "name", data["name"], min_length=1, max_length=200)
        self.validate_text_field(
            "college", data["college"], min_length=1, max_length=200)

        # Validate optional notes field if present
        if "notes" in data and data["notes"] is not None:
            if isinstance(data["notes"], str) and len(data["notes"]) > 500:
                raise ValidationError(
                    "notes", "Notes must not exceed 500 characters")

    def validate_event_data(self, data: Dict[str, Any]) -> None:
        """
        Validate complete event registration data.

        Args:
            data: Dictionary containing event registration data

        Raises:
            ValidationError: If any validation check fails
        """
        # Required fields for event registration
        required_fields = ["name", "email", "phone", "eventNames"]

        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(
                    field, f"Required field '{field}' is missing or empty")

        # Validate email format
        self.validate_email(data["email"])

        # Validate text fields
        self.validate_text_field(
            "name", data["name"], min_length=1, max_length=200)

        # Validate eventNames is a list with at least one item
        if not isinstance(data["eventNames"], list) or len(data["eventNames"]) == 0:
            raise ValidationError(
                "eventNames", "At least one event must be selected")

        for event_name in data["eventNames"]:
            self.validate_text_field(
                "eventName", event_name, min_length=1, max_length=200)

    def validate_workshop_data(self, data: Dict[str, Any]) -> None:
        """
        Validate complete workshop registration data.

        Args:
            data: Dictionary containing workshop registration data

        Raises:
            ValidationError: If any validation check fails
        """
        # Required fields for workshop registration
        required_fields = ["name", "email", "phone", "workshopNames"]

        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(
                    field, f"Required field '{field}' is missing or empty")

        # Validate email format
        self.validate_email(data["email"])

        # Validate text fields
        self.validate_text_field(
            "name", data["name"], min_length=1, max_length=200)

        # Validate workshopNames is a list with at least one item
        if not isinstance(data["workshopNames"], list) or len(data["workshopNames"]) == 0:
            raise ValidationError(
                "workshopNames", "At least one workshop must be selected")

        for workshop_name in data["workshopNames"]:
            self.validate_text_field(
                "workshopName", workshop_name, min_length=1, max_length=200)
