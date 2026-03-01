"""
SheetsRepository for Google Sheets integration.

This module provides the repository layer for interacting with Google Sheets
to store and retrieve accommodation entries.

Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
"""

import json
import logging
import os
import time
from typing import Optional, Dict, Any
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound

from app.models import AccommodationEntry


logger = logging.getLogger(__name__)


class SheetsAPIError(Exception):
    """Custom exception for Google Sheets API errors."""

    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        super().__init__(
            f"Google Sheets API error during {operation}: {str(original_error)}")


class SheetsRepository:
    """
    Repository for Google Sheets operations.

    Implements:
    - Service account authentication (Requirement 5.1)
    - Connection pooling for gspread client (Requirement 5.5)
    - Caching with 60s TTL (Requirement 5.2)
    - Error handling for Google Sheets API errors (Requirement 5.4)
    - Accommodation entry operations (Requirements 5.3)
    """

    # Class-level client for connection pooling
    _client: Optional[gspread.Client] = None
    _client_initialized: bool = False

    def __init__(self, credentials_path: Optional[str] = None, sheet_name: Optional[str] = None, sheet_id: Optional[str] = None):
        """
        Initialize SheetsRepository with Google Sheets credentials.

        Args:
            credentials_path: Path to service account JSON or JSON string
            sheet_name: Name of the Google Sheet to access
            sheet_id: ID of the Google Sheet to access (alternative to sheet_name)

        Raises:
            ValueError: If required environment variables are missing
            SheetsAPIError: If sheet access fails
        """
        # Load configuration from environment if not provided
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_CREDENTIALS_JSON")
        self.sheet_name = sheet_name or os.getenv("SHEET_NAME")
        self.sheet_id = sheet_id or os.getenv("SHEET_ID")

        if not self.credentials_path:
            raise ValueError(
                "GOOGLE_CREDENTIALS_JSON environment variable not set")
        if not self.sheet_name and not self.sheet_id:
            raise ValueError(
                "Either SHEET_NAME or SHEET_ID environment variable must be set")

        # Initialize client (with connection pooling)
        self.client = self._get_or_create_client()

        # Open the sheet (prefer sheet_id if provided)
        try:
            if self.sheet_id:
                self.spreadsheet = self.client.open_by_key(self.sheet_id)
                logger.info(
                    f"Successfully connected to Google Sheet by ID: {self.sheet_id}")
            else:
                self.spreadsheet = self.client.open(self.sheet_name)
                logger.info(
                    f"Successfully connected to Google Sheet: {self.sheet_name}")
            self.sheet = self.spreadsheet.sheet1
        except SpreadsheetNotFound:
            identifier = self.sheet_id if self.sheet_id else self.sheet_name
            logger.error(f"Spreadsheet not found: {identifier}")
            raise SheetsAPIError(
                "sheet_access", SpreadsheetNotFound(identifier))
        except Exception as e:
            logger.error(f"Failed to open spreadsheet: {e}")
            raise SheetsAPIError("sheet_access", e)

        # Cache for accommodation data
        self._cache: Optional[list] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl: int = 60  # 60 seconds TTL

    def _get_or_create_client(self) -> gspread.Client:
        """
        Get or create gspread client with connection pooling.

        Implements connection pooling by reusing the same client instance
        across all SheetsRepository instances.

        Returns:
            gspread.Client: Authenticated gspread client

        Raises:
            SheetsAPIError: If authentication fails
        """
        # Use class-level client for connection pooling
        if not SheetsRepository._client_initialized:
            try:
                credentials = self._load_credentials()
                SheetsRepository._client = gspread.authorize(credentials)
                SheetsRepository._client_initialized = True
                logger.info(
                    "Successfully initialized gspread client with service account")
            except Exception as e:
                logger.error(f"Failed to initialize gspread client: {e}")
                raise SheetsAPIError("authentication", e)

        return SheetsRepository._client

    def _load_credentials(self) -> Credentials:
        """
        Load Google service account credentials.

        Supports both file path and JSON string from environment variable.

        Returns:
            Credentials: Google service account credentials

        Raises:
            ValueError: If credentials format is invalid
        """
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        try:
            # Try to parse as JSON string first (for environment variable)
            if self.credentials_path.strip().startswith('{'):
                creds_dict = json.loads(self.credentials_path)
                credentials = Credentials.from_service_account_info(
                    creds_dict, scopes=scopes)
            else:
                # Treat as file path
                credentials = Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=scopes
                )
            return credentials
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in credentials: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load credentials: {e}")

    def _is_cache_stale(self) -> bool:
        """
        Check if the cache is stale and needs refresh.

        Returns:
            bool: True if cache is stale or doesn't exist
        """
        if self._cache is None or self._cache_timestamp is None:
            return True

        elapsed = time.time() - self._cache_timestamp
        return elapsed > self._cache_ttl

    def _refresh_cache(self) -> None:
        """
        Refresh the accommodation data cache.

        Reads all records from the sheet and updates the cache.

        Raises:
            SheetsAPIError: If reading from sheet fails
        """
        try:
            self._cache = self.sheet.get_all_records()
            self._cache_timestamp = time.time()
            logger.debug(f"Cache refreshed with {len(self._cache)} records")
        except APIError as e:
            logger.error(
                f"Google Sheets API error while refreshing cache: {e}")
            raise SheetsAPIError("get_all_records", e)
        except Exception as e:
            logger.error(f"Unexpected error while refreshing cache: {e}")
            raise SheetsAPIError("get_all_records", e)

    async def find_accommodation(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find accommodation entry by email with caching.

        Implements 60-second TTL caching to reduce API calls.

        Args:
            email: Email address to search for

        Returns:
            Optional[Dict[str, Any]]: Accommodation entry if found, None otherwise

        Raises:
            SheetsAPIError: If reading from sheet fails
        """
        # Refresh cache if stale
        if self._is_cache_stale():
            self._refresh_cache()

        # Search in cached data (case-insensitive)
        email_lower = email.lower()
        for record in self._cache:
            if record.get('Email', '').lower() == email_lower:
                logger.debug(f"Found accommodation for email: {email}")
                return record

        logger.debug(f"No accommodation found for email: {email}")
        return None

    async def append_accommodation(self, entry: AccommodationEntry) -> None:
        """
        Append new accommodation entry to the sheet.

        Converts AccommodationEntry to row format and appends to sheet.
        Invalidates cache after successful append.

        Args:
            entry: AccommodationEntry to append

        Raises:
            SheetsAPIError: If appending to sheet fails
        """
        try:
            # Convert entry to row format
            row = self._entry_to_row(entry)

            # Append to sheet
            self.sheet.append_row(row)
            logger.info(
                f"Successfully appended accommodation entry for: {entry.email}")

            # Invalidate cache to force refresh on next read
            self._cache = None
            self._cache_timestamp = None

        except APIError as e:
            logger.error(f"Google Sheets API error while appending row: {e}")
            raise SheetsAPIError("append_row", e)
        except Exception as e:
            logger.error(
                f"Unexpected error while appending accommodation: {e}")
            raise SheetsAPIError("append_row", e)

    def _entry_to_row(self, entry: AccommodationEntry) -> list:
        """
        Convert AccommodationEntry to sheet row format.

        Row structure (Requirement 5.3):
        [Timestamp, Name, Email, Phone, College, From Date, To Date, Accommodation Type, Notes, Entered By]

        Args:
            entry: AccommodationEntry to convert

        Returns:
            list: Row data in correct column order
        """
        return [
            entry.timestamp.isoformat(),
            entry.name,
            entry.email,
            entry.phone,
            entry.college,
            entry.fromDate,
            entry.toDate,
            entry.accommodationType,
            entry.notes or "",
            entry.enteredBy
        ]

    def verify_connection(self) -> bool:
        """
        Verify connection to Google Sheets.

        Used for health checks (Requirement 5.2).

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to access sheet title
            _ = self.sheet.title
            return True
        except Exception as e:
            logger.error(f"Failed to verify Google Sheets connection: {e}")
            return False

    async def check_connection(self) -> bool:
        """
        Async wrapper for verify_connection.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        return self.verify_connection()
