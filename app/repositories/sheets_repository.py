"""
SheetsRepository for Google Sheets integration.

This module provides the repository layer for interacting with Google Sheets
to store and retrieve accommodation, event, and workshop entries.

Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
"""

import json
import logging
import os
import time
from typing import Optional, Dict, Any, Literal
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, SpreadsheetNotFound

from app.models import AccommodationEntry


logger = logging.getLogger(__name__)

SheetType = Literal['accommodation', 'events', 'workshops', 'valediction']


class SheetsAPIError(Exception):
    """Custom exception for Google Sheets API errors."""

    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        super().__init__(
            f"Google Sheets API error during {operation}: {str(original_error)}")


class SheetsRepository:
    """
    Repository for Google Sheets operations across multiple sheets.

    Implements:
    - Service account authentication (Requirement 5.1)
    - Connection pooling for gspread client (Requirement 5.5)
    - Caching with 60s TTL (Requirement 5.2)
    - Error handling for Google Sheets API errors (Requirement 5.4)
    - Multi-sheet support for accommodation, events, and workshops
    """

    # Class-level client for connection pooling
    _client: Optional[gspread.Client] = None
    _client_initialized: bool = False

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        accommodation_sheet_id: Optional[str] = None,
        events_sheet_id: Optional[str] = None,
        workshops_sheet_id: Optional[str] = None,
        valediction_sheet_id: Optional[str] = None
    ):
        """
        Initialize SheetsRepository with Google Sheets credentials.

        Args:
            credentials_path: Path to service account JSON or JSON string
            accommodation_sheet_id: ID of the accommodation Google Sheet
            events_sheet_id: ID of the events Google Sheet
            workshops_sheet_id: ID of the workshops Google Sheet
            valediction_sheet_id: ID of the valediction Google Sheet

        Raises:
            ValueError: If required environment variables are missing
            SheetsAPIError: If sheet access fails
        """
        # Load configuration from environment if not provided
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_CREDENTIALS_JSON")
        self.accommodation_sheet_id = accommodation_sheet_id or os.getenv(
            "ACCOMMODATION_SHEET_ID")
        self.events_sheet_id = events_sheet_id or os.getenv("EVENTS_SHEET_ID")
        self.workshops_sheet_id = workshops_sheet_id or os.getenv(
            "WORKSHOPS_SHEET_ID")
        self.valediction_sheet_id = valediction_sheet_id or os.getenv(
            "VALEDICTION_SHEET_ID")

        if not self.credentials_path:
            raise ValueError(
                "GOOGLE_CREDENTIALS_JSON environment variable not set")
        if not self.accommodation_sheet_id:
            raise ValueError(
                "ACCOMMODATION_SHEET_ID environment variable not set")
        if not self.events_sheet_id:
            raise ValueError("EVENTS_SHEET_ID environment variable not set")
        if not self.workshops_sheet_id:
            raise ValueError("WORKSHOPS_SHEET_ID environment variable not set")
        if not self.valediction_sheet_id:
            raise ValueError(
                "VALEDICTION_SHEET_ID environment variable not set")

        # Initialize client (with connection pooling)
        self.client = self._get_or_create_client()

        # Open all sheets
        self.sheets: Dict[SheetType, Any] = {}
        self._open_sheets()

        # Cache for each sheet type
        self._caches: Dict[SheetType, Optional[list]] = {
            'accommodation': None,
            'events': None,
            'workshops': None,
            'valediction': None
        }
        self._cache_timestamps: Dict[SheetType, Optional[float]] = {
            'accommodation': None,
            'events': None,
            'workshops': None,
            'valediction': None
        }
        self._cache_ttl: int = 60  # 60 seconds TTL

    def _open_sheets(self) -> None:
        """
        Open all three Google Sheets.

        Raises:
            SheetsAPIError: If sheet access fails
        """
        sheet_configs = {
            'accommodation': self.accommodation_sheet_id,
            'events': self.events_sheet_id,
            'workshops': self.workshops_sheet_id,
            'valediction': self.valediction_sheet_id
        }

        for sheet_type, sheet_id in sheet_configs.items():
            try:
                spreadsheet = self.client.open_by_key(sheet_id)
                self.sheets[sheet_type] = spreadsheet.sheet1
                logger.info(
                    f"Successfully connected to {sheet_type} sheet: {sheet_id}")
            except SpreadsheetNotFound:
                logger.error(
                    f"{sheet_type.capitalize()} spreadsheet not found: {sheet_id}")
                raise SheetsAPIError(
                    "sheet_access", SpreadsheetNotFound(sheet_id))
            except Exception as e:
                logger.error(f"Failed to open {sheet_type} spreadsheet: {e}")
                raise SheetsAPIError("sheet_access", e)

    def _get_or_create_client(self) -> gspread.Client:
        """
        Get or create gspread client with connection pooling.

        Returns:
            gspread.Client: Authenticated gspread client

        Raises:
            SheetsAPIError: If authentication fails
        """
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
            if self.credentials_path.strip().startswith('{'):
                creds_dict = json.loads(self.credentials_path)
                credentials = Credentials.from_service_account_info(
                    creds_dict, scopes=scopes)
            else:
                credentials = Credentials.from_service_account_file(
                    self.credentials_path, scopes=scopes
                )
            return credentials
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in credentials: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load credentials: {e}")

    def _is_cache_stale(self, sheet_type: SheetType) -> bool:
        """
        Check if the cache is stale for a specific sheet type.

        Args:
            sheet_type: Type of sheet to check

        Returns:
            bool: True if cache is stale or doesn't exist
        """
        cache = self._caches.get(sheet_type)
        timestamp = self._cache_timestamps.get(sheet_type)

        if cache is None or timestamp is None:
            return True

        elapsed = time.time() - timestamp
        return elapsed > self._cache_ttl

    def _refresh_cache(self, sheet_type: SheetType) -> None:
        """
        Refresh the cache for a specific sheet type.

        Args:
            sheet_type: Type of sheet to refresh

        Raises:
            SheetsAPIError: If reading from sheet fails
        """
        try:
            sheet = self.sheets[sheet_type]
            self._caches[sheet_type] = sheet.get_all_records()
            self._cache_timestamps[sheet_type] = time.time()
            logger.debug(
                f"{sheet_type.capitalize()} cache refreshed with {len(self._caches[sheet_type])} records")
        except APIError as e:
            logger.error(
                f"Google Sheets API error while refreshing {sheet_type} cache: {e}")
            raise SheetsAPIError("get_all_records", e)
        except Exception as e:
            logger.error(
                f"Unexpected error while refreshing {sheet_type} cache: {e}")
            raise SheetsAPIError("get_all_records", e)

    async def find_accommodation(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find accommodation entry by email with caching.

        Args:
            email: Email address to search for

        Returns:
            Optional[Dict[str, Any]]: Accommodation entry if found, None otherwise

        Raises:
            SheetsAPIError: If reading from sheet fails
        """
        return await self._find_entry('accommodation', email)

    async def find_event_registration(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find event registration by email with caching.

        Args:
            email: Email address to search for

        Returns:
            Optional[Dict[str, Any]]: Event registration if found, None otherwise

        Raises:
            SheetsAPIError: If reading from sheet fails
        """
        return await self._find_entry('events', email)

    async def find_workshop_registration(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find workshop registration by email with caching.

        Args:
            email: Email address to search for

        Returns:
            Optional[Dict[str, Any]]: Workshop registration if found, None otherwise

        Raises:
            SheetsAPIError: If reading from sheet fails
        """
        return await self._find_entry('workshops', email)

    async def _find_entry(self, sheet_type: SheetType, email: str) -> Optional[Dict[str, Any]]:
        """
        Generic method to find entry by email in any sheet type.

        Args:
            sheet_type: Type of sheet to search
            email: Email address to search for

        Returns:
            Optional[Dict[str, Any]]: Entry if found, None otherwise
        """
        if self._is_cache_stale(sheet_type):
            self._refresh_cache(sheet_type)

        email_lower = email.lower()
        cache = self._caches[sheet_type]

        for record in cache:
            if record.get('Email', '').lower() == email_lower:
                logger.debug(f"Found {sheet_type} entry for email: {email}")
                return record

        logger.debug(f"No {sheet_type} entry found for email: {email}")
        return None

    async def append_accommodation(self, entry: AccommodationEntry) -> None:
        """
        Append new accommodation entry to the sheet.

        Args:
            entry: AccommodationEntry to append

        Raises:
            SheetsAPIError: If appending to sheet fails
        """
        row = self._accommodation_entry_to_row(entry)
        await self._append_row('accommodation', row)
        logger.info(
            f"Successfully appended accommodation entry for: {entry.email}")

    async def append_event_registration(self, entry: Dict[str, Any]) -> None:
        """
        Append new event registration to the sheet.

        Args:
            entry: Event registration data

        Raises:
            SheetsAPIError: If appending to sheet fails
        """
        row = self._event_entry_to_row(entry)
        await self._append_row('events', row)
        logger.info(
            f"Successfully appended event registration for: {entry['email']}")

    async def append_workshop_registration(self, entry: Dict[str, Any]) -> None:
        """
        Append new workshop registration to the sheet.

        Args:
            entry: Workshop registration data

        Raises:
            SheetsAPIError: If appending to sheet fails
        """
        row = self._workshop_entry_to_row(entry)
        await self._append_row('workshops', row)
        logger.info(
            f"Successfully appended workshop registration for: {entry['email']}")

    async def _append_row(self, sheet_type: SheetType, row: list) -> None:
        """
        Generic method to append a row to any sheet type.

        Args:
            sheet_type: Type of sheet to append to
            row: Row data to append

        Raises:
            SheetsAPIError: If appending to sheet fails
        """
        try:
            sheet = self.sheets[sheet_type]
            sheet.append_row(row)

            # Invalidate cache
            self._caches[sheet_type] = None
            self._cache_timestamps[sheet_type] = None

        except APIError as e:
            logger.error(
                f"Google Sheets API error while appending to {sheet_type}: {e}")
            raise SheetsAPIError("append_row", e)
        except Exception as e:
            logger.error(
                f"Unexpected error while appending to {sheet_type}: {e}")
            raise SheetsAPIError("append_row", e)

    def _accommodation_entry_to_row(self, entry: AccommodationEntry) -> list:
        """
        Convert AccommodationEntry to sheet row format.

        Row: [Timestamp, Name, Email, Phone, College, From Date, To Date, Type, Payment Status, Notes, Entered By]
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
            entry.paymentStatus,
            entry.notes or "",
            entry.enteredBy
        ]

    def _event_entry_to_row(self, entry: Dict[str, Any]) -> list:
        """
        Convert event registration to sheet row format.

        Row: [Timestamp, Name, Email, Phone, Event Names, Team Name, Payment Status, Notes, Entered By]
        """
        # Join event names with comma separator
        event_names_str = ", ".join(entry['eventNames']) if isinstance(
            entry['eventNames'], list) else str(entry['eventNames'])

        return [
            entry['timestamp'].isoformat(),
            entry['name'],
            entry['email'],
            entry['phone'],
            event_names_str,
            entry.get('teamName', ''),
            entry.get('paymentStatus', 'Pending'),
            entry.get('notes', ''),
            entry['enteredBy']
        ]

    def _workshop_entry_to_row(self, entry: Dict[str, Any]) -> list:
        """
        Convert workshop registration to sheet row format.

        Row: [Timestamp, Name, Email, Phone, Workshop Names, Payment Status, Notes, Entered By]
        """
        # Join workshop names with comma separator
        workshop_names_str = ", ".join(entry['workshopNames']) if isinstance(
            entry['workshopNames'], list) else str(entry['workshopNames'])

        return [
            entry['timestamp'].isoformat(),
            entry['name'],
            entry['email'],
            entry['phone'],
            workshop_names_str,
            entry.get('paymentStatus', 'Pending'),
            entry.get('notes', ''),
            entry['enteredBy']
        ]

    async def find_valediction_by_roll(self, roll_number: str) -> Optional[Dict[str, Any]]:
        """
        Find valediction participant by roll number.

        Args:
            roll_number: 9-digit roll number to search for

        Returns:
            Optional[Dict[str, Any]]: Participant record if found, None otherwise
        """
        if self._is_cache_stale('valediction'):
            self._refresh_cache('valediction')

        cache = self._caches['valediction']
        for record in cache:
            # Match against 'Roll Number' column (handle both str and int)
            sheet_roll = str(record.get('Roll Number', '')).strip()
            if sheet_roll == roll_number.strip():
                logger.debug(
                    f"Found valediction entry for roll: {roll_number}")
                return record

        logger.debug(f"No valediction entry found for roll: {roll_number}")
        return None

    async def mark_valediction_token(self, roll_number: str, given_by: str) -> bool:
        """
        Mark a valediction token as given in the Google Sheet.

        Finds the row by roll number and updates the 'Token Given', 'Given By',
        and 'Given At' columns. Auto-creates these columns if they don't exist.

        Args:
            roll_number: 9-digit roll number
            given_by: Volunteer identifier who gave the token

        Returns:
            True if successfully updated

        Raises:
            SheetsAPIError: If updating the sheet fails
        """
        try:
            sheet = self.sheets['valediction']
            all_values = sheet.get_all_values()

            if not all_values:
                raise SheetsAPIError("mark_token", Exception("Sheet is empty"))

            headers = all_values[0]
            header_lower = [h.strip().lower() for h in headers]

            # Find Roll Number column
            roll_col = None
            for idx, h in enumerate(header_lower):
                if h == 'roll number':
                    roll_col = idx
                    break

            if roll_col is None:
                raise SheetsAPIError("mark_token", Exception(
                    "'Roll Number' column not found"))

            # Find or create Token Given, Given By, Given At columns
            token_col = None
            given_by_col = None
            given_at_col = None

            for idx, h in enumerate(header_lower):
                if h == 'token given':
                    token_col = idx
                elif h == 'given by':
                    given_by_col = idx
                elif h == 'given at':
                    given_at_col = idx

            # Add missing columns as new headers
            next_col = len(headers)
            new_headers = []
            if token_col is None:
                token_col = next_col
                new_headers.append((next_col, 'Token Given'))
                next_col += 1
            if given_by_col is None:
                given_by_col = next_col
                new_headers.append((next_col, 'Given By'))
                next_col += 1
            if given_at_col is None:
                given_at_col = next_col
                new_headers.append((next_col, 'Given At'))
                next_col += 1

            for col_idx, header_name in new_headers:
                cell = gspread.utils.rowcol_to_a1(1, col_idx + 1)
                sheet.update(cell, [[header_name]])

            # Find the row with matching roll number
            target_row = None
            for row_idx, row in enumerate(all_values[1:], start=2):
                if len(row) > roll_col and str(row[roll_col]).strip() == roll_number.strip():
                    target_row = row_idx
                    break

            if target_row is None:
                raise SheetsAPIError("mark_token", Exception(
                    f"Roll number {roll_number} not found"))

            # Update the cells
            timestamp = datetime.utcnow().isoformat()

            token_cell = gspread.utils.rowcol_to_a1(target_row, token_col + 1)
            sheet.update(token_cell, [['Yes']])

            given_by_cell = gspread.utils.rowcol_to_a1(
                target_row, given_by_col + 1)
            sheet.update(given_by_cell, [[given_by]])

            given_at_cell = gspread.utils.rowcol_to_a1(
                target_row, given_at_col + 1)
            sheet.update(given_at_cell, [[timestamp]])

            # Highlight the entire row for this participant in green
            green_format = {
                "backgroundColor": {
                    "red": 0.85,
                    "green": 0.95,
                    "blue": 0.85,
                }
            }
            last_col_letter = gspread.utils.rowcol_to_a1(
                1, len(headers)).rstrip('0123456789')
            row_range = f"A{target_row}:{last_col_letter}{target_row}"
            sheet.format(row_range, green_format)

            # Invalidate cache
            self._caches['valediction'] = None
            self._cache_timestamps['valediction'] = None

            logger.info(f"Successfully marked token for roll: {roll_number}")
            return True

        except APIError as e:
            logger.error(f"Google Sheets API error while marking token: {e}")
            raise SheetsAPIError("mark_token", e)
        except SheetsAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error while marking token: {e}")
            raise SheetsAPIError("mark_token", e)

    def verify_connection(self) -> bool:
        """
        Verify connection to all Google Sheets.

        Returns:
            bool: True if all connections are successful
        """
        try:
            for sheet_type, sheet in self.sheets.items():
                _ = sheet.title
            return True
        except Exception as e:
            logger.error(f"Failed to verify Google Sheets connection: {e}")
            return False

    async def check_connection(self) -> bool:
        """
        Async wrapper for verify_connection.

        Returns:
            bool: True if connection is successful
        """
        return self.verify_connection()

    # --- Valediction Search Counters (row 420-422, below 415 data entries) ---
    COUNTER_ROW_EXISTING = 420
    COUNTER_ROW_NON_EXISTING = 421
    COUNTER_ROW_DUPLICATE = 422

    async def _ensure_search_counters(self) -> None:
        """Set up counter labels and initial values if not already present."""
        sheet = self.sheets['valediction']
        label_cell = f"A{self.COUNTER_ROW_EXISTING}"
        current = sheet.acell(label_cell).value
        if current == "Existing Searches":
            return  # already set up

        sheet.update(label_cell, [["Existing Searches"]])
        sheet.update(f"B{self.COUNTER_ROW_EXISTING}", [[0]])
        sheet.update(f"A{self.COUNTER_ROW_NON_EXISTING}",
                     [["Non-Existing Searches"]])
        sheet.update(f"B{self.COUNTER_ROW_NON_EXISTING}", [[0]])
        sheet.update(f"A{self.COUNTER_ROW_DUPLICATE}",
                     [["Duplicate Searches (Token Already Given)"]])
        sheet.update(f"B{self.COUNTER_ROW_DUPLICATE}", [[0]])

        # Bold the labels
        bold_fmt = {"textFormat": {"bold": True}}
        sheet.format(
            f"A{self.COUNTER_ROW_EXISTING}:A{self.COUNTER_ROW_DUPLICATE}", bold_fmt)
        logger.info("Initialized valediction search counters")

    async def increment_search_counter(self, found: bool, duplicate: bool = False) -> None:
        """Increment the existing, non-existing, or duplicate search counter by 1."""
        try:
            await self._ensure_search_counters()
            sheet = self.sheets['valediction']
            if duplicate:
                row = self.COUNTER_ROW_DUPLICATE
            elif found:
                row = self.COUNTER_ROW_EXISTING
            else:
                row = self.COUNTER_ROW_NON_EXISTING
            cell = f"B{row}"
            current = sheet.acell(cell).value
            count = int(current) if current and current.isdigit() else 0
            sheet.update(cell, [[count + 1]])
        except Exception as e:
            # Don't let counter failures break the search flow
            logger.warning(f"Failed to update search counter: {e}")
