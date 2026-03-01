"""
WorkshopService for the Vortex 2026 Registration System.

This module provides the service layer for creating and managing
workshop registrations with validation and duplicate detection.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from app.models.schemas import WorkshopRegistrationRequest, WorkshopRegistrationResponse
from app.repositories.sheets_repository import SheetsRepository
from app.services.validation_service import ValidationService


logger = logging.getLogger(__name__)


class WorkshopService:
    """
    Service for handling workshop registration with validation.
    """

    def __init__(self, sheets_repo: SheetsRepository, validator: ValidationService):
        """
        Initialize WorkshopService with required dependencies.

        Args:
            sheets_repo: Repository for Google Sheets operations
            validator: Service for input validation
        """
        self.sheets_repo = sheets_repo
        self.validator = validator

    async def create_workshop_registration(
        self,
        data: WorkshopRegistrationRequest,
        volunteer_email: str
    ) -> WorkshopRegistrationResponse:
        """
        Create new workshop registration with duplicate checking.

        Args:
            data: WorkshopRegistrationRequest containing entry data
            volunteer_email: Email of the volunteer creating the entry

        Returns:
            WorkshopRegistrationResponse indicating success or duplicate warning

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
                "workshopNames": data.workshopNames
            }
            self.validator.validate_workshop_data(data_dict)
            logger.debug(
                f"Validation passed for workshop registration: {data.email}")

            # Check for duplicates - block if email already registered
            existing = await self.sheets_repo.find_workshop_registration(data.email)
            if existing:
                logger.info(
                    f"Email already registered for workshops: {data.email}")
                return WorkshopRegistrationResponse(
                    success=False,
                    message="This email is already registered for workshops",
                    duplicate=True,
                    existingEntry={
                        "name": existing.get('Name'),
                        "workshopNames": existing.get('Workshop Names')
                    }
                )

            # Prepare entry with automatic field population
            entry = self._prepare_entry(data, volunteer_email)

            # Append to Google Sheets
            await self.sheets_repo.append_workshop_registration(entry)

            logger.info(
                f"Successfully created workshop registration for: {data.email}")

            return WorkshopRegistrationResponse(
                success=True,
                message="Workshop registration created successfully",
                entry=entry,
                duplicate=False
            )

        except Exception as e:
            logger.error(
                f"Error creating workshop registration for {data.email}: {e}")
            raise

    def _prepare_entry(
        self,
        data: WorkshopRegistrationRequest,
        volunteer_email: str
    ) -> Dict[str, Any]:
        """
        Prepare workshop registration entry with automatic field population.

        Args:
            data: WorkshopRegistrationRequest containing user-provided data
            volunteer_email: Email of the volunteer creating the entry

        Returns:
            Dict with all fields populated
        """
        entry = {
            'timestamp': datetime.utcnow(),
            'name': data.name,
            'email': data.email,
            'phone': data.phone,
            'workshopNames': data.workshopNames,
            'paymentStatus': data.paymentStatus,
            'notes': data.notes or '',
            'enteredBy': volunteer_email
        }

        logger.debug(
            f"Prepared workshop entry with timestamp={entry['timestamp']}, enteredBy={entry['enteredBy']}")

        return entry
