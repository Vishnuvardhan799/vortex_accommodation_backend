"""
Middleware components for the Vortex 2026 Accommodation System.

This module provides authentication and other middleware functionality.
Validates: Requirements 7.1, 7.4
"""

import os
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Verify authentication token against environment variable.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        The validated token

    Raises:
        HTTPException: If token is invalid or missing

    Validates: Requirements 7.1, 7.4
    """
    expected_token = os.getenv("API_SECRET_KEY")

    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API_SECRET_KEY not set"
        )

    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

    return credentials.credentials
