"""
API routes for the Vortex 2026 Accommodation System.

This module defines all API endpoints for the application.
"""

from app.config import get_config
import os
from fastapi import APIRouter, Depends, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime

from app.models.schemas import (
    SearchRequest,
    SearchResponse,
    AccommodationRequest,
    AccommodationResponse,
    EventRegistrationRequest,
    EventRegistrationResponse,
    WorkshopRegistrationRequest,
    WorkshopRegistrationResponse,
    HealthResponse
)
from app.middleware import verify_token
from app.services.search_service import SearchService
from app.services.accommodation_service import AccommodationService
from app.services.event_service import EventService
from app.services.workshop_service import WorkshopService
from app.repositories.registration_repository import RegistrationRepository
from app.repositories.sheets_repository import SheetsRepository
from app.services.validation_service import ValidationService

# Create router
router = APIRouter(prefix="/api", tags=["api"])

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize repositories and services

config = get_config()

# Initialize repositories
registration_repo = RegistrationRepository(config.registration_data_path)
sheets_repo = SheetsRepository(
    credentials_path=config.google_credentials_json,
    accommodation_sheet_id=config.accommodation_sheet_id,
    events_sheet_id=config.events_sheet_id,
    workshops_sheet_id=config.workshops_sheet_id
)

# Initialize services
validation_service = ValidationService()
search_service = SearchService(registration_repo, sheets_repo)
accommodation_service = AccommodationService(sheets_repo, validation_service)
event_service = EventService(sheets_repo, validation_service)
workshop_service = WorkshopService(sheets_repo, validation_service)


@router.post("/search", response_model=SearchResponse)
@limiter.limit("30/minute")
async def search_participant(
    request: Request,
    search_req: SearchRequest,
    token: str = Depends(verify_token)
):
    """
    Search for participant by email address.

    Rate limit: 30 requests per minute per IP

    Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 7.2
    """
    result = await search_service.search_participant(search_req.email)
    return result


@router.post("/accommodation", response_model=AccommodationResponse)
@limiter.limit("20/minute")
async def add_accommodation(
    request: Request,
    response: Response,
    accom_req: AccommodationRequest,
    token: str = Depends(verify_token)
):
    """
    Add new accommodation entry.

    Rate limit: 20 requests per minute per IP

    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 7.2
    """
    # For now, use a placeholder volunteer email
    # In production, this would come from the authenticated user
    volunteer_email = "volunteer@vortex2026.com"

    result = await accommodation_service.create_accommodation(
        data=accom_req,
        volunteer_email=volunteer_email
    )

    # Return 409 for duplicates, 201 for success
    response.status_code = 409 if result.duplicate else 201
    return result


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring.

    Validates: Requirements 5.2
    """
    services_status = {
        "api": "running"
    }

    # Check Google Sheets connectivity
    try:
        if sheets_repo and sheets_repo.verify_connection():
            services_status["googleSheets"] = "connected"
        else:
            services_status["googleSheets"] = "disconnected"
    except Exception:
        services_status["googleSheets"] = "error"

    # Check registration data
    try:
        if registration_repo and registration_repo.get_participant_count() > 0:
            services_status["registrationData"] = "loaded"
        else:
            services_status["registrationData"] = "not_loaded"
    except Exception:
        services_status["registrationData"] = "error"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services=services_status
    )


@router.post("/events/register", response_model=EventRegistrationResponse)
@limiter.limit("20/minute")
async def register_event(
    request: Request,
    response: Response,
    event_req: EventRegistrationRequest,
    token: str = Depends(verify_token)
):
    """
    Register participant for an event.

    Rate limit: 20 requests per minute per IP
    """
    volunteer_email = "volunteer@vortex2026.com"

    result = await event_service.create_event_registration(
        data=event_req,
        volunteer_email=volunteer_email
    )

    # Return 409 for duplicates, 201 for success
    response.status_code = 409 if result.duplicate else 201
    return result


@router.post("/workshops/register", response_model=WorkshopRegistrationResponse)
@limiter.limit("20/minute")
async def register_workshop(
    request: Request,
    response: Response,
    workshop_req: WorkshopRegistrationRequest,
    token: str = Depends(verify_token)
):
    """
    Register participant for a workshop.

    Rate limit: 20 requests per minute per IP
    """
    volunteer_email = "volunteer@vortex2026.com"

    result = await workshop_service.create_workshop_registration(
        data=workshop_req,
        volunteer_email=volunteer_email
    )

    # Return 409 for duplicates, 201 for success
    response.status_code = 409 if result.duplicate else 201
    return result
