"""
ValedictionService for the Vortex 2026 CSE Valediction Token System.

This module provides the service layer for searching valediction participants
by roll number and marking tokens as given.
"""

import logging
from typing import Optional

from app.models.schemas import (
    ValedictionParticipant,
    ValedictionSearchResponse,
    ValedictionMarkTokenResponse,
)
from app.repositories.sheets_repository import SheetsRepository


logger = logging.getLogger(__name__)


class ValedictionService:
    """
    Service for handling CSE Valediction token distribution.
    """

    def __init__(self, sheets_repo: SheetsRepository):
        self.sheets_repo = sheets_repo

    async def search_by_roll(self, roll_number: str) -> ValedictionSearchResponse:
        """
        Search for a valediction participant by roll number.

        Args:
            roll_number: 9-digit roll number

        Returns:
            ValedictionSearchResponse with participant data if found
        """
        try:
            record = await self.sheets_repo.find_valediction_by_roll(roll_number)

            if record is None:
                logger.info(
                    f"No valediction participant found for roll: {roll_number}")
                await self.sheets_repo.increment_search_counter(found=False)
                return ValedictionSearchResponse(
                    found=False,
                    message="No participant found with this roll number"
                )

            participant = self._record_to_participant(record)

            # Check if token already given — count as duplicate search
            is_duplicate = participant.tokenGiven
            logger.info(f"Found valediction participant: {roll_number}")
            await self.sheets_repo.increment_search_counter(found=True, duplicate=is_duplicate)
            return ValedictionSearchResponse(
                found=True,
                participant=participant
            )

        except Exception as e:
            logger.error(
                f"Error searching valediction participant {roll_number}: {e}")
            raise

    async def mark_token_given(self, roll_number: str, volunteer: str = "volunteer@vortex2026.com") -> ValedictionMarkTokenResponse:
        """
        Mark a valediction token as given for a participant.

        Args:
            roll_number: 9-digit roll number
            volunteer: Identifier of the volunteer marking the token

        Returns:
            ValedictionMarkTokenResponse indicating success or already given
        """
        try:
            # First check if participant exists and token status
            record = await self.sheets_repo.find_valediction_by_roll(roll_number)

            if record is None:
                return ValedictionMarkTokenResponse(
                    success=False,
                    message="No participant found with this roll number",
                    alreadyGiven=False
                )

            # Check if token already given
            token_status = str(record.get('Token Given', '')).strip().lower()
            if token_status in ('yes', 'true', '1'):
                participant = self._record_to_participant(record)
                return ValedictionMarkTokenResponse(
                    success=False,
                    message="Token has already been given to this participant",
                    alreadyGiven=True,
                    participant=participant
                )

            # Mark the token
            await self.sheets_repo.mark_valediction_token(roll_number, volunteer)

            # Re-fetch to get updated data
            updated_record = await self.sheets_repo.find_valediction_by_roll(roll_number)
            participant = self._record_to_participant(
                updated_record) if updated_record else None

            logger.info(f"Token marked as given for roll: {roll_number}")
            return ValedictionMarkTokenResponse(
                success=True,
                message="Token marked as given successfully",
                alreadyGiven=False,
                participant=participant
            )

        except Exception as e:
            logger.error(f"Error marking token for {roll_number}: {e}")
            raise

    def _record_to_participant(self, record: dict) -> ValedictionParticipant:
        """Convert a sheet record dict to a ValedictionParticipant model."""
        token_val = str(record.get('Token Given', '')).strip().lower()
        token_given = token_val in ('yes', 'true', '1')

        return ValedictionParticipant(
            rollNumber=str(record.get('Roll Number', '')).strip(),
            name=str(record.get('Name', '')).strip(),
            email=str(record.get('Email Address', '')).strip() or None,
            gender=str(record.get('Gender', '')).strip() or None,
            year=str(record.get('Year', '')).strip() or None,
            foodPreference=str(record.get(
                'Preferred Food choice', '')).strip() or None,
            tokenGiven=token_given,
            givenBy=str(record.get('Given By', '')).strip() or None,
            givenAt=str(record.get('Given At', '')).strip() or None,
        )
