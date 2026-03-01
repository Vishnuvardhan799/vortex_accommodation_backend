"""
AccommodationService for the Vortex 2026 Accommodation System.

This module provides the service layer for creating and managing
accommodation entries with validation and duplicate detection.

Validates: Requirements 3.1, 3.2, 3.5, 3.6, 4.1, 4.2, 4.3
"""

import logging
from datetime import datetime
from typing import Dict, Any

from app.models import AccommodationEntry, AccommodationRequest, AccommodationResponse
from app.repositories.sheets_repository import SheetsRepository
from app.services.validation_service import ValidationService


logger = logging.getLogger(__name__)


class AccommodationService:
    """
    Service for handling accommodation entry creation with validation.

    This service coordinates accommodation entry creation, including:
    - Input validation
    - Duplicate detection
    - Automatic field population (timestamp, enteredBy)
    - Data persistence to Google Sheets

    Validates: Requirements 3.1, 3.2, 3.5, 3.6, 4.1, 4.2, 4.3
    """

    def __init__(
        self,
        sheets_repo: SheetsRepository,
        validator: ValidationService
    ):
        """
        Initialize AccommodationService with required dependencies.

        Args:
            sheets_repo: Repository for Google Sheets operations
            validator: Service for input validation
        """
        self.sheets_repo = sheets_repo
        self.validator = validator

    async def create_accommodation(
        self,
        data: AccommodationRequest,
        volunteer_email: str,
        force: bool = False
    ) -> AccommodationResponse:
        """
        Create new accommodation entry with duplicate checking.

        This method:
        1. Validates input data
        2. Checks for duplicate entries (unless force=True)
        3. Adds timestamp and volunteer email automatically
        4. Appends entry to Google Sheets

        Args:
            data: AccommodationRequest containing entry data
            volunteer_email: Email of the volunteer creating the entry
            force: If True, bypass duplicate check and create anyway

        Returns:
            AccommodationResponse indicating success or duplicate warning

        Raises:
            ValidationError: If input data is invalid
            SheetsAPIError: If Google Sheets operation fails

        Validates: Requirements 3.1, 3.2, 3.5, 3.6, 4.1, 4.2, 4.3
        """
        try:
            # Validate input data
            data_dict = {
                "name": data.name,
                "email": data.email,
                "college": data.college,
                "fromDate": data.fromDate,
                "toDate": data.toDate,
                "accommodationType": data.accommodationType,
                "notes": data.notes
            }
            self.validator.validate_accommodation_data(data_dict)
            logger.debug(
                f"Validation passed for accommodation entry: {data.email}")

            # Check for duplicates (unless force flag is set)
            if not force:
                existing = await self.sheets_repo.find_accommodation(data.email)
                if existing:
                    logger.info(
                        f"Duplicate accommodation entry detected for: {data.email}"
                    )
                    return AccommodationResponse(
                        success=False,
                        message="An accommodation entry already exists for this email",
                        duplicate=True,
                        existingEntry={
                            "name": existing.get('Name'),
                            "fromDate": existing.get('From Date'),
                            "toDate": existing.get('To Date'),
                            "accommodationType": existing.get('Accommodation Type')
                        }
                    )

            # Prepare entry with automatic field population
            entry = self._prepare_entry(data, volunteer_email)

            # Append to Google Sheets
            await self.sheets_repo.append_accommodation(entry)

            logger.info(
                f"Successfully created accommodation entry for: {data.email}"
            )

            return AccommodationResponse(
                success=True,
                message="Accommodation entry created successfully",
                entry=entry,
                duplicate=False
            )

        except Exception as e:
            logger.error(
                f"Error creating accommodation entry for {data.email}: {e}"
            )
            raise

    def _prepare_entry(
        self,
        data: AccommodationRequest,
        volunteer_email: str
    ) -> AccommodationEntry:
        """
        Prepare accommodation entry with automatic field population.

        Automatically adds:
        - timestamp: Current UTC timestamp
        - enteredBy: Volunteer email who created the entry

        Args:
            data: AccommodationRequest containing user-provided data
            volunteer_email: Email of the volunteer creating the entry

        Returns:
            AccommodationEntry with all fields populated

        Validates: Requirements 3.5, 3.6
        """
        entry = AccommodationEntry(
            timestamp=datetime.utcnow(),
            name=data.name,
            email=data.email,
            phone=data.phone,
            college=data.college,
            fromDate=data.fromDate,
            toDate=data.toDate,
            accommodationType=data.accommodationType,
            notes=data.notes,
            enteredBy=volunteer_email
        )

        logger.debug(
            f"Prepared entry with timestamp={entry.timestamp}, "
            f"enteredBy={entry.enteredBy}"
        )

        return entry
