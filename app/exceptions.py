"""
Custom exception classes for the Vortex 2026 Accommodation System.

This module defines custom exceptions for error handling throughout the application.
Validates: Requirements 9.1, 9.2, 9.3
"""


class AccommodationSystemError(Exception):
    """Base exception for accommodation system errors."""
    pass


class DuplicateEntryError(AccommodationSystemError):
    """
    Raised when attempting to create duplicate accommodation entry.

    Validates: Requirements 4.1, 9.2
    """

    def __init__(self, email: str, existing_entry: dict):
        self.email = email
        self.existing_entry = existing_entry
        super().__init__(f"Accommodation entry already exists for {email}")


class SheetsAPIError(AccommodationSystemError):
    """
    Raised when Google Sheets API operations fail.

    Validates: Requirements 5.4, 9.2
    """

    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Google Sheets API error during {operation}")


class ValidationError(AccommodationSystemError):
    """
    Raised for custom validation failures.

    Validates: Requirements 9.3
    """

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on {field}: {message}")
