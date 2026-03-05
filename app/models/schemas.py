"""
Pydantic models for the Vortex 2026 Accommodation & Registration Check System.

This module defines all data models used for request/response validation,
data serialization, and business logic throughout the application.
"""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class AccommodationEntry(BaseModel):
    """
    Model representing an accommodation entry in the Google Sheet.

    Validates:
    - Email format (Requirements 3.4)
    - Date format and range (Requirements 3.3)
    - Required fields (Requirements 3.2)
    - Automatic timestamp and enteredBy fields (Requirements 3.5, 3.6)
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15,
                       pattern=r'^\+?[0-9\s\-\(\)]+$')
    college: str = Field(min_length=1, max_length=200)
    fromDate: str = Field(pattern=r'^2026-03-(06|07|08)$')
    toDate: str = Field(pattern=r'^2026-03-(07|08)$')
    accommodationType: Literal['Boys', 'Girls', 'Other']
    paymentStatus: Literal['Paid', 'Pending',
                           'Waived'] = Field(default='Pending')
    notes: Optional[str] = Field(default=None, max_length=500)
    enteredBy: str  # Volunteer email

    @field_validator('toDate')
    @classmethod
    def validate_date_range(cls, v: str, info) -> str:
        """
        Validate that toDate is greater than or equal to fromDate.

        Validates: Requirements 3.3
        """
        from_date = info.data.get('fromDate')
        if from_date and v < from_date:
            raise ValueError('toDate must be >= fromDate')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "timestamp": "2026-03-06T10:30:00Z",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+91 9876543210",
                "college": "NIT Trichy",
                "fromDate": "2026-03-06",
                "toDate": "2026-03-08",
                "accommodationType": "Boys",
                "paymentStatus": "Paid",
                "notes": "Late arrival",
                "enteredBy": "volunteer@example.com"
            }
        }
    }


class RegistrationData(BaseModel):
    """
    Model representing participant registration data.

    Contains information about a participant's event and workshop registrations.
    Validates: Requirements 1.2
    """
    name: str
    email: EmailStr
    phone: Optional[str] = None
    college: str
    events: List[str] = Field(default_factory=list)
    workshops: List[str] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "college": "NIT Trichy",
                "events": ["Tech Talk", "Hackathon"],
                "workshops": ["AI Workshop", "Web Dev Workshop"]
            }
        }
    }


class SearchRequest(BaseModel):
    """
    Model for participant search requests.

    Validates: Requirements 1.5
    """
    email: EmailStr

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "participant@example.com"
            }
        }
    }


class AccommodationStatus(BaseModel):
    """
    Model representing accommodation status for a participant.

    Used in search responses to indicate accommodation details.
    Validates: Requirements 1.3
    """
    hasAccommodation: bool
    fromDate: Optional[str] = None
    toDate: Optional[str] = None
    type: Optional[str] = None
    notes: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "hasAccommodation": True,
                "fromDate": "2026-03-06",
                "toDate": "2026-03-08",
                "type": "Boys",
                "notes": "Late arrival"
            }
        }
    }


class ParticipantData(BaseModel):
    """
    Model representing complete participant information.

    Combines registration data with accommodation status.
    Validates: Requirements 1.2, 1.3
    """
    name: str
    email: str
    phone: Optional[str] = None
    college: str
    events: List[str] = Field(default_factory=list)
    workshops: List[str] = Field(default_factory=list)
    accommodation: Optional[AccommodationStatus] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "college": "NIT Trichy",
                "events": ["Tech Talk", "Hackathon"],
                "workshops": ["AI Workshop"],
                "accommodation": {
                    "hasAccommodation": True,
                    "fromDate": "2026-03-06",
                    "toDate": "2026-03-08",
                    "type": "Boys"
                }
            }
        }
    }


class SearchResponse(BaseModel):
    """
    Model for participant search responses.

    Validates: Requirements 1.2, 1.3, 1.4
    """
    found: bool
    participant: Optional[ParticipantData] = None
    message: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "found": True,
                    "participant": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "college": "NIT Trichy",
                        "events": ["Tech Talk"],
                        "workshops": ["AI Workshop"],
                        "accommodation": {
                            "hasAccommodation": True,
                            "fromDate": "2026-03-06",
                            "toDate": "2026-03-08",
                            "type": "Boys"
                        }
                    }
                },
                {
                    "found": False,
                    "message": "No participant found with this email"
                }
            ]
        }
    }


class AccommodationRequest(BaseModel):
    """
    Model for accommodation creation requests.

    Validates:
    - Required fields (Requirements 3.2)
    - Email format (Requirements 3.4)
    - Date format and range (Requirements 3.3)
    - Accommodation type (Requirements 6.3)
    """
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15,
                       pattern=r'^\+?[0-9\s\-\(\)]+$')
    college: str = Field(min_length=1, max_length=200)
    fromDate: str = Field(pattern=r'^2026-03-(06|07|08)$')
    toDate: str = Field(pattern=r'^2026-03-(07|08)$')
    accommodationType: Literal['Boys', 'Girls', 'Other']
    paymentStatus: Literal['Paid', 'Pending',
                           'Waived'] = Field(default='Pending')
    notes: Optional[str] = Field(default=None, max_length=500)
    force: bool = Field(default=False)

    @field_validator('toDate')
    @classmethod
    def validate_date_range(cls, v: str, info) -> str:
        """
        Validate that toDate is greater than or equal to fromDate.

        Validates: Requirements 3.3
        """
        from_date = info.data.get('fromDate')
        if from_date and v < from_date:
            raise ValueError('toDate must be >= fromDate')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "participant@example.com",
                "phone": "+91 9876543210",
                "college": "NIT Trichy",
                "fromDate": "2026-03-06",
                "toDate": "2026-03-08",
                "accommodationType": "Boys",
                "paymentStatus": "Paid",
                "notes": "Late arrival",
                "force": False
            }
        }
    }


class AccommodationResponse(BaseModel):
    """
    Model for accommodation creation responses.

    Validates: Requirements 3.1, 4.1, 9.4
    """
    success: bool
    message: str
    entry: Optional[AccommodationEntry] = None
    duplicate: bool = Field(default=False)
    existingEntry: Optional[dict] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Accommodation entry created successfully",
                    "entry": {
                        "timestamp": "2026-03-06T10:30:00Z",
                        "name": "John Doe",
                        "email": "participant@example.com",
                        "college": "NIT Trichy",
                        "fromDate": "2026-03-06",
                        "toDate": "2026-03-08",
                        "accommodationType": "Boys",
                        "paymentStatus": "Paid",
                        "notes": "Late arrival",
                        "enteredBy": "volunteer@example.com"
                    },
                    "duplicate": False
                },
                {
                    "success": False,
                    "message": "An accommodation entry already exists for this email",
                    "duplicate": True,
                    "existingEntry": {
                        "name": "John Doe",
                        "fromDate": "2026-03-06",
                        "toDate": "2026-03-07"
                    }
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """
    Model for health check responses.

    Validates: Requirements 5.2
    """
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: dict

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2026-03-06T10:30:00Z",
                "services": {
                    "googleSheets": "connected",
                    "registrationData": "loaded"
                }
            }
        }
    }


class EventRegistrationRequest(BaseModel):
    """
    Model for event registration requests.
    """
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15,
                       pattern=r'^\+?[0-9\s\-\(\)]+$')
    eventNames: List[str] = Field(min_items=1, max_items=20)
    teamName: Optional[str] = Field(default=None, max_length=200)
    paymentStatus: Literal['Paid', 'Pending',
                           'Waived'] = Field(default='Pending')
    notes: Optional[str] = Field(default=None, max_length=500)
    force: bool = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "participant@example.com",
                "phone": "+91 9876543210",
                "eventNames": ["Tech Talk", "Hackathon"],
                "teamName": "Team Alpha",
                "paymentStatus": "Paid",
                "notes": "First time participant",
                "force": False
            }
        }
    }


class EventRegistrationResponse(BaseModel):
    """
    Model for event registration responses.
    """
    success: bool
    message: str
    entry: Optional[dict] = None
    duplicate: bool = Field(default=False)
    existingEntry: Optional[dict] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Event registration created successfully",
                "duplicate": False
            }
        }
    }


class WorkshopRegistrationRequest(BaseModel):
    """
    Model for workshop registration requests.
    """
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=15,
                       pattern=r'^\+?[0-9\s\-\(\)]+$')
    workshopNames: List[str] = Field(min_items=1, max_items=20)
    paymentStatus: Literal['Paid', 'Pending',
                           'Waived'] = Field(default='Pending')
    notes: Optional[str] = Field(default=None, max_length=500)
    force: bool = Field(default=False)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "participant@example.com",
                "phone": "+91 9876543210",
                "workshopNames": ["AI Workshop", "Web Dev Workshop"],
                "paymentStatus": "Paid",
                "notes": "Interested in advanced topics",
                "force": False
            }
        }
    }


class WorkshopRegistrationResponse(BaseModel):
    """
    Model for workshop registration responses.
    """
    success: bool
    message: str
    entry: Optional[dict] = None
    duplicate: bool = Field(default=False)
    existingEntry: Optional[dict] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Workshop registration created successfully",
                "duplicate": False
            }
        }
    }
