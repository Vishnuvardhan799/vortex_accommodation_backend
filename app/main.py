"""
Vortex 2026 Accommodation & Registration Check System - Main Application

This module initializes the FastAPI application and configures middleware.
"""

from app.api.routes import router as api_router
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
from dotenv import load_dotenv

from app.exceptions import DuplicateEntryError, SheetsAPIError, ValidationError
from app.config import validate_config, get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate configuration at startup
# Validates: Requirements 10.4
try:
    validate_config()
    config = get_config()
except Exception as e:
    logger.critical(f"Failed to start application: {e}")
    raise

# Create FastAPI application
app = FastAPI(
    title="Vortex 2026 Accommodation System",
    description="API for managing participant registration and accommodation data",
    version="1.0.0"
)

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Configure GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global Exception Handlers
# Validates: Requirements 9.1, 9.2, 9.3, 9.4

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with detailed field-level messages.

    Validates: Requirements 9.3
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:])  # Skip 'body'
        message = error["msg"]
        errors.append({"field": field, "message": message})

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": "Validation failed",
            "details": errors
        }
    )


@app.exception_handler(DuplicateEntryError)
async def duplicate_entry_exception_handler(request: Request, exc: DuplicateEntryError):
    """
    Handle duplicate accommodation entry errors.

    Validates: Requirements 4.1, 9.2
    """
    logger.info(f"Duplicate entry attempt for email: {exc.email}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "duplicate": True,
            "message": str(exc),
            "existingEntry": exc.existing_entry
        }
    )


@app.exception_handler(SheetsAPIError)
async def sheets_api_exception_handler(request: Request, exc: SheetsAPIError):
    """
    Handle Google Sheets API errors.

    Validates: Requirements 5.4, 9.2
    """
    logger.error(
        f"Sheets API error during {exc.operation}: {exc.original_error}")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "success": False,
            "error": "Service temporarily unavailable",
            "message": "Unable to access accommodation data. Please try again in a moment."
        }
    )


@app.exception_handler(ValidationError)
async def custom_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle custom validation errors.

    Validates: Requirements 9.3
    """
    logger.warning(f"Custom validation error: {exc.field} - {exc.message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": "Validation failed",
            "details": [{"field": exc.field, "message": exc.message}]
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected errors.

    Validates: Requirements 9.1
    """
    # Log the full exception for debugging
    logger.error(
        f"Unexpected error on {request.url.path}: {exc}", exc_info=True)

    # Return generic error to client (don't leak implementation details)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected error occurred. Please try again."
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Vortex 2026 Accommodation System API",
        "version": "1.0.0",
        "status": "running"
    }


# Include API routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
