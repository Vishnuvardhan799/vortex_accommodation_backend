"""
EventService for the Vortex 2026 Registration System.

This module provides the service layer for creating and managing
event registrations with validation and duplicate detection.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from app.models.schemas import EventRegistrationRequest, EventRegistrationResponse
from app.repositories.sheets_repository import SheetsRepository
from app.services.validation_service import ValidationService


logger = logging.getLogger(__name__)


class EventService:
    """
    Service for handling event registration with validation.
    """

    def __init__(self, sheets_repo: SheetsRepository, validator: ValidationService):
        """
        Initialize EventService with required dependencies.

        Args:
            sheets_repo: Repository for Google Sheets operations
            validator: Service for input validation
        """
        self.sheets_repo = sheets_repo
        self.validator = validator

    async def create_event_registration(
        self,
        data: EventRegistrationRequest,
        volunteer_email: str,
        force: bool = False
    ) -> EventRegistrationResponse:
        """
        Create new event registration with duplicate checking.

        Args:
            data: EventRegistrationRequest containing entry data
            volunteer_email: Email of the volunteer creating the entry
            force: If True, bypass duplicate check and create anyway

        Returns:
            EventRegistrationResponse indicating success or duplicate warning

        Raises:
            ValidationError: If input data is invalid
            SheetsAPIError: If Google Sheets operation fails
        """
        try:
            # Validate input data
            data_dict = {
                "name": data.name,
                "email": data.email,
                "phone": data.phone,
                "eventNames": data.eventNames
            }
            self.validator.validate_event_data(data_dict)
            logger.debug(
                f"Validation passed for event registration: {data.email}")

            # Check for duplicates (unless force flag is set)
            if not force:
                existing = await self.sheets_repo.find_event_registration(data.email)
                if existing:
                    logger.info(
                        f"Duplicate event registration detected for: {data.email}")
                    return EventRegistrationResponse(
                        success=False,
                        message="An event registration already exists for this email",
                        duplicate=True,
                        existingEntry={
                            "name": existing.get('Name'),
                            "eventNames": existing.get('Event Names'),
                            "teamName": existing.get('Team Name')
                        }
                    )

            # Prepare entry with automatic field population
            entry = self._prepare_entry(data, volunteer_email)

            # Append to Google Sheets
            await self.sheets_repo.append_event_registration(entry)

            logger.info(
                f"Successfully created event registration for: {data.email}")

            return EventRegistrationResponse(
                success=True,
                message="Event registration created successfully",
                entry=entry,
                duplicate=False
            )

        except Exception as e:
            logger.error(
                f"Error creating event registration for {data.email}: {e}")
            raise

    def _prepare_entry(
        self,
        data: EventRegistrationRequest,
        volunteer_email: str
    ) -> Dict[str, Any]:
        """
        Prepare event registration entry with automatic field population.

        Args:
            data: EventRegistrationRequest containing user-provided data
            volunteer_email: Email of the volunteer creating the entry

        Returns:
            Dict with all fields populated
        """
        entry = {
            'timestamp': datetime.utcnow(),
            'name': data.name,
            'email': data.email,
            'phone': data.phone,
            'eventNames': data.eventNames,
            'teamName': data.teamName or '',
            'paymentStatus': data.paymentStatus,
            'notes': data.notes or '',
            'enteredBy': volunteer_email
        }

        logger.debug(
            f"Prepared event entry with timestamp={entry['timestamp']}, enteredBy={entry['enteredBy']}")

        return entry
