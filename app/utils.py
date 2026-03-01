"""
Utility functions for the Vortex 2026 Accommodation System.

This module provides helper functions including retry logic with exponential backoff.
Validates: Requirements 5.4
"""

import asyncio
import logging
from typing import TypeVar, Callable

from app.exceptions import SheetsAPIError

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
) -> T:
    """
    Retry function with exponential backoff.

    Args:
        func: Async function to retry
        max_attempts: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        backoff_factor: Multiplier for delay after each attempt (default: 2.0)

    Returns:
        Result of the function call

    Raises:
        SheetsAPIError: If all retry attempts fail

    Validates: Requirements 5.4
    """
    delay = initial_delay

    for attempt in range(max_attempts):
        try:
            return await func()
        except SheetsAPIError as e:
            if attempt == max_attempts - 1:
                # Last attempt failed, re-raise
                logger.error(f"All {max_attempts} retry attempts failed")
                raise

            # Log retry attempt
            logger.warning(
                f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                f"Retrying in {delay}s..."
            )

            # Wait before retry
            await asyncio.sleep(delay)
            delay *= backoff_factor
        except Exception as e:
            # Non-retryable error, re-raise immediately
            logger.error(f"Non-retryable error occurred: {e}")
            raise

    raise Exception("Retry logic failed unexpectedly")
