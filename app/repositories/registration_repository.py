"""
Registration Repository for the Vortex 2026 Accommodation System.

This module provides data access for participant registration data.
It loads registration data from a JSON or Excel file and provides fast O(1) email lookups
using an in-memory index.

Validates: Requirements 1.1, 1.2
"""

import json
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
from app.models import RegistrationData


class RegistrationRepository:
    """
    Repository for managing participant registration data.

    This class loads registration data from a JSON file at initialization
    and builds an in-memory email index for O(1) lookup performance.

    Attributes:
        data_path: Path to the registration data JSON file
        data: List of all registration records
        email_index: Dictionary mapping email addresses to registration data
    """

    def __init__(self, data_path: str):
        """
        Initialize the repository and load registration data.

        Args:
            data_path: Path to the JSON or Excel file containing registration data

        Raises:
            FileNotFoundError: If the data file does not exist
            json.JSONDecodeError: If the JSON data file is not valid
            ValueError: If the data file format is invalid
        """
        self.data_path = Path(data_path)
        self.data = self._load_registration_data()
        self.email_index = self._build_email_index()

    def _load_registration_data(self) -> list:
        """
        Load registration data from JSON or Excel file.

        Supports both .json and .xlsx file formats. Excel files are expected
        to have data in the first sheet with column headers in the first row.

        Returns:
            List of registration records as dictionaries

        Raises:
            FileNotFoundError: If the data file does not exist
            json.JSONDecodeError: If the JSON data file is not valid
            ValueError: If the file format is unsupported or data is invalid
        """
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Registration data file not found: {self.data_path}"
            )

        file_extension = self.data_path.suffix.lower()

        if file_extension == '.json':
            return self._load_from_json()
        elif file_extension in ['.xlsx', '.xls']:
            return self._load_from_excel()
        else:
            raise ValueError(
                f"Unsupported file format: {file_extension}. "
                "Supported formats: .json, .xlsx, .xls"
            )

    def _load_from_json(self) -> list:
        """
        Load registration data from JSON file.

        Returns:
            List of registration records as dictionaries

        Raises:
            json.JSONDecodeError: If the JSON file is not valid
            ValueError: If the data format is invalid
        """
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(
                "Registration data must be a JSON array of participant objects"
            )

        return data

    def _load_from_excel(self) -> list:
        """
        Load registration data from Excel file.

        Reads the first sheet of the Excel file and converts it to a list
        of dictionaries. Column headers are expected in the first row.
        Automatically normalizes column names to lowercase.

        Returns:
            List of registration records as dictionaries

        Raises:
            ValueError: If the Excel file cannot be read or is empty
        """
        try:
            # Read Excel file (first sheet by default)
            df = pd.read_excel(self.data_path, engine='openpyxl')

            # Check if DataFrame is empty
            if df.empty:
                raise ValueError(
                    f"Excel file is empty: {self.data_path}"
                )

            # Normalize column names to lowercase for consistency
            df.columns = df.columns.str.lower().str.strip()

            # Handle common column name variations
            column_mapping = {
                'year': 'year',  # Keep as is
                'gender': 'gender',  # Keep as is
                'summer internship': 'summer_internship',  # Normalize spaces
                '#': 'id',  # Map # to id
            }

            # Apply column name mapping
            df = df.rename(columns=column_mapping)

            # Add city column if missing (use empty string as default)
            if 'city' not in df.columns:
                df['city'] = ''

            # Convert DataFrame to list of dictionaries
            # Replace NaN values with None for proper JSON serialization
            data = df.where(pd.notna(df), None).to_dict('records')

            print(
                f"Loaded {len(data)} records from Excel file: {self.data_path}")

            return data

        except Exception as e:
            raise ValueError(
                f"Failed to load Excel file {self.data_path}: {str(e)}"
            )

    def _build_email_index(self) -> Dict[str, RegistrationData]:
        """
        Build in-memory index for O(1) email lookups.

        Creates a dictionary mapping lowercase email addresses to RegistrationData
        objects. Email addresses are normalized to lowercase for case-insensitive
        lookups.

        Returns:
            Dictionary mapping email addresses to RegistrationData objects

        Raises:
            ValueError: If a participant record is missing required fields
        """
        index = {}

        for participant in self.data:
            try:
                # Validate and parse participant data using Pydantic model
                reg_data = RegistrationData(**participant)

                # Store with lowercase email for case-insensitive lookup
                email_key = reg_data.email.lower()
                index[email_key] = reg_data

            except Exception as e:
                # Log warning but continue processing other records
                print(f"Warning: Skipping invalid participant record: {e}")
                continue

        return index

    def find_by_email(self, email: str) -> Optional[RegistrationData]:
        """
        Find participant registration by email address.

        Uses the in-memory email index for O(1) lookup performance.
        Email lookup is case-insensitive.

        Args:
            email: Email address to search for

        Returns:
            RegistrationData object if found, None otherwise

        Validates: Requirements 1.1, 1.2
        """
        # Normalize email to lowercase for case-insensitive lookup
        email_key = email.lower().strip()
        return self.email_index.get(email_key)

    def get_all_participants(self) -> list[RegistrationData]:
        """
        Get all participant registration records.

        Returns:
            List of all RegistrationData objects
        """
        return list(self.email_index.values())

    def get_participant_count(self) -> int:
        """
        Get the total number of registered participants.

        Returns:
            Count of participants in the registration dataset
        """
        return len(self.email_index)

    def is_loaded(self) -> bool:
        """
        Check if registration data is loaded.

        Returns:
            True if data is loaded, False otherwise
        """
        return self.data is not None and len(self.email_index) > 0
