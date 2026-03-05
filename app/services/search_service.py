"""
SearchService for the Vortex 2026 Accommodation System.

This module provides the service layer for searching participants across
registration data and accommodation records.

Validates: Requirements 1.1, 1.2, 1.3, 1.4
"""

import asyncio
import logging
from typing import Optional

from app.models import (
    AccommodationStatus,
    ParticipantData,
    RegistrationData,
    SearchResponse,
)
from app.repositories.registration_repository import RegistrationRepository
from app.repositories.sheets_repository import SheetsRepository


logger = logging.getLogger(__name__)


class SearchService:
    """
    Service for coordinating participant search across data sources.

    This service queries both the registration repository and the sheets
    repository concurrently, then merges the results into a unified
    participant data response.

    Validates: Requirements 1.1, 1.2, 1.3, 1.4
    """

    def __init__(
        self,
        reg_repo: RegistrationRepository,
        sheets_repo: SheetsRepository
    ):
        """
        Initialize SearchService with required repositories.

        Args:
            reg_repo: Repository for registration data access
            sheets_repo: Repository for accommodation data access
        """
        self.reg_repo = reg_repo
        self.sheets_repo = sheets_repo

    async def search_participant(self, email: str) -> SearchResponse:
        """
        Search for participant across registration data and accommodation sheet.

        Queries both data sources concurrently using asyncio.gather for
        optimal performance. Returns combined participant information.

        Args:
            email: Email address to search for

        Returns:
            SearchResponse containing participant data if found, or not found message

        Validates: Requirements 1.1, 1.2, 1.3, 1.4
        """
        try:
            # Query registration data and accommodation sheet concurrently
            reg_data, accom_data = await asyncio.gather(
                self._get_registration_data(email),
                self.sheets_repo.find_accommodation(email)
            )

            # If participant not found in registration data
            if reg_data is None:
                logger.info(f"No participant found for email: {email}")
                return SearchResponse(
                    found=False,
                    message="No participant found with this email"
                )

            # Merge registration and accommodation data
            participant = self._merge_participant_data(reg_data, accom_data)

            logger.info(f"Successfully found participant: {email}")
            return SearchResponse(
                found=True,
                participant=participant
            )

        except Exception as e:
            logger.error(f"Error searching for participant {email}: {e}")
            raise

    async def _get_registration_data(self, email: str) -> Optional[RegistrationData]:
        """
        Get registration data for email.

        Wraps synchronous repository call in async context.

        Args:
            email: Email address to search for

        Returns:
            RegistrationData if found, None otherwise
        """
        # Registration repository is synchronous, but we wrap it for consistency
        return self.reg_repo.find_by_email(email)

    def _merge_participant_data(
        self,
        reg_data: RegistrationData,
        accom_data: Optional[dict]
    ) -> ParticipantData:
        """
        Merge registration data with accommodation data.

        Combines participant registration information with their accommodation
        status into a unified ParticipantData object.

        Args:
            reg_data: Registration data from registration repository
            accom_data: Accommodation data from sheets repository (or None)

        Returns:
            ParticipantData with merged information

        Validates: Requirements 1.2, 1.3
        """
        # Build accommodation status if accommodation data exists
        accommodation = None
        if accom_data:
            accommodation = AccommodationStatus(
                hasAccommodation=True,
                fromDate=accom_data.get('From Date'),
                toDate=accom_data.get('To Date'),
                type=accom_data.get('Accommodation Type'),
                notes=accom_data.get('Notes')
            )
        else:
            accommodation = AccommodationStatus(
                hasAccommodation=False
            )

        # Create unified participant data
        participant = ParticipantData(
            name=reg_data.name,
            email=reg_data.email,
            phone=reg_data.phone,
            college=reg_data.college,
            events=reg_data.events,
            workshops=reg_data.workshops,
            accommodation=accommodation
        )

        return participant
