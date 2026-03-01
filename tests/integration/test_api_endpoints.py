"""
Integration tests for API endpoints.

This module contains integration tests for the complete API workflows.
Validates: Requirements 1.1, 3.1, 4.1, 7.2, 7.3
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from app.main import app
from app.models import (
    AccommodationEntry,
    AccommodationResponse,
    SearchResponse,
    ParticipantData,
    AccommodationStatus,
    RegistrationData
)


# Create test client
client = TestClient(app)

# Test API key
TEST_API_KEY = "test_secret_key_12345"


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for all tests."""
    monkeypatch.setenv("API_SECRET_KEY", TEST_API_KEY)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:5173")


@pytest.fixture
def mock_services():
    """Mock the service dependencies."""
    with patch('app.api.routes.search_service') as mock_search, \
            patch('app.api.routes.accommodation_service') as mock_accom, \
            patch('app.api.routes.registration_repo') as mock_reg, \
            patch('app.api.routes.sheets_repo') as mock_sheets:

        # Configure mocks
        mock_search.search_participant = AsyncMock()
        mock_accom.create_accommodation = AsyncMock()
        mock_reg.is_loaded = Mock(return_value=True)
        mock_sheets.check_connection = AsyncMock(return_value=True)

        yield {
            'search': mock_search,
            'accommodation': mock_accom,
            'registration': mock_reg,
            'sheets': mock_sheets
        }


def test_complete_search_workflow(mock_services):
    """
    Test complete search workflow.

    Validates: Requirements 1.1, 7.2
    """
    # Setup mock response
    participant = ParticipantData(
        name="John Doe",
        email="john@example.com",
        college="NIT Trichy",
        events=["Tech Talk"],
        workshops=["AI Workshop"],
        accommodation=AccommodationStatus(
            hasAccommodation=True,
            fromDate="2026-03-06",
            toDate="2026-03-08",
            type="Boys"
        )
    )

    mock_services['search'].search_participant.return_value = SearchResponse(
        found=True,
        participant=participant
    )

    # Make request
    response = client.post(
        "/api/search",
        json={"email": "john@example.com"},
        headers={"Authorization": f"Bearer {TEST_API_KEY}"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["participant"]["name"] == "John Doe"
    assert data["participant"]["email"] == "john@example.com"
    assert data["participant"]["accommodation"]["hasAccommodation"] is True


def test_search_participant_not_found(mock_services):
    """
    Test search when participant is not found.

    Validates: Requirements 1.1, 1.4
    """
    # Setup mock response
    mock_services['search'].search_participant.return_value = SearchResponse(
        found=False,
        message="No participant found with this email"
    )

    # Make request
    response = client.post(
        "/api/search",
        json={"email": "notfound@example.com"},
        headers={"Authorization": f"Bearer {TEST_API_KEY}"}
    )

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is False
    assert "message" in data


def test_complete_add_accommodation_workflow(mock_services):
    """
    Test complete add accommodation workflow.

    Validates: Requirements 3.1, 7.2
    """
    # Setup mock response
    entry = AccommodationEntry(
        timestamp=datetime.utcnow(),
        name="Jane Smith",
        email="jane@example.com",
        college="NIT Trichy",
        fromDate="2026-03-06",
        toDate="2026-03-08",
        accommodationType="Girls",
        notes="Early arrival",
        enteredBy="volunteer@vortex2026.com"
    )

    mock_services['accommodation'].create_accommodation.return_value = AccommodationResponse(
        success=True,
        message="Accommodation entry created successfully",
        entry=entry,
        duplicate=False
    )

    # Make request
    response = client.post(
        "/api/accommodation",
        json={
            "name": "Jane Smith",
            "email": "jane@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Girls",
            "notes": "Early arrival",
            "force": False
        },
        headers={"Authorization": f"Bearer {TEST_API_KEY}"}
    )

    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    assert data["entry"]["name"] == "Jane Smith"


def test_duplicate_handling_workflow(mock_services):
    """
    Test duplicate accommodation entry handling.

    Validates: Requirements 4.1, 7.2
    """
    # Setup mock response for duplicate
    mock_services['accommodation'].create_accommodation.return_value = AccommodationResponse(
        success=False,
        message="An accommodation entry already exists for this email",
        duplicate=True,
        existingEntry={
            "name": "Jane Smith",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-07",
            "accommodationType": "Girls"
        }
    )

    # Make request without force flag
    response = client.post(
        "/api/accommodation",
        json={
            "name": "Jane Smith",
            "email": "jane@example.com",
            "college": "NIT Trichy",
            "fromDate": "2026-03-07",
            "toDate": "2026-03-08",
            "accommodationType": "Girls",
            "force": False
        },
        headers={"Authorization": f"Bearer {TEST_API_KEY}"}
    )

    # Verify duplicate warning response
    assert response.status_code == 201  # Still 201 but with duplicate flag
    data = response.json()
    assert data["success"] is False
    assert data["duplicate"] is True
    assert "existingEntry" in data


def test_authentication_failure():
    """
    Test authentication failure with invalid token.

    Validates: Requirements 7.2
    """
    # Make request with invalid token
    response = client.post(
        "/api/search",
        json={"email": "test@example.com"},
        headers={"Authorization": "Bearer invalid_token"}
    )

    # Verify authentication error
    assert response.status_code == 401


def test_authentication_missing():
    """
    Test authentication failure with missing token.

    Validates: Requirements 7.2
    """
    # Make request without token
    response = client.post(
        "/api/search",
        json={"email": "test@example.com"}
    )

    # Verify authentication error
    assert response.status_code == 403  # FastAPI returns 403 for missing credentials


def test_rate_limiting_behavior(mock_services):
    """
    Test rate limiting on search endpoint.

    Validates: Requirements 7.3

    Note: This is a basic test. Full rate limiting testing would require
    more sophisticated setup with time manipulation.
    """
    # Setup mock response
    mock_services['search'].search_participant.return_value = SearchResponse(
        found=False,
        message="No participant found"
    )

    # Make multiple requests (within rate limit)
    for i in range(5):
        response = client.post(
            "/api/search",
            json={"email": f"test{i}@example.com"},
            headers={"Authorization": f"Bearer {TEST_API_KEY}"}
        )
        # Should succeed within rate limit
        assert response.status_code == 200


def test_validation_error_response():
    """
    Test validation error response format.

    Validates: Requirements 7.3
    """
    # Make request with invalid email format
    response = client.post(
        "/api/search",
        json={"email": "invalid-email"},
        headers={"Authorization": f"Bearer {TEST_API_KEY}"}
    )

    # Verify validation error response
    assert response.status_code == 400
    data = response.json()
    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert "details" in data


def test_health_endpoint(mock_services):
    """
    Test health check endpoint.

    Validates: Requirements 5.2
    """
    # Make request to health endpoint
    response = client.get("/api/health")

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "timestamp" in data


def test_invalid_date_range():
    """
    Test validation for invalid date range.

    Validates: Requirements 3.3, 7.3
    """
    # Make request with fromDate > toDate
    response = client.post(
        "/api/accommodation",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "college": "Test College",
            "fromDate": "2026-03-08",
            "toDate": "2026-03-06",  # Earlier than fromDate
            "accommodationType": "Boys",
            "force": False
        },
        headers={"Authorization": f"Bearer {TEST_API_KEY}"}
    )

    # Verify validation error
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False


def test_missing_required_fields():
    """
    Test validation for missing required fields.

    Validates: Requirements 3.2, 7.3
    """
    # Make request with missing name field
    response = client.post(
        "/api/accommodation",
        json={
            "email": "test@example.com",
            "college": "Test College",
            "fromDate": "2026-03-06",
            "toDate": "2026-03-08",
            "accommodationType": "Boys",
            "force": False
        },
        headers={"Authorization": f"Bearer {TEST_API_KEY}"}
    )

    # Verify validation error
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "details" in data
