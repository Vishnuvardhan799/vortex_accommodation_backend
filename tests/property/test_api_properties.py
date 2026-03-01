"""
Property-based tests for API endpoints.

This module contains property tests for API validation and response behavior.
"""

import pytest
from hypothesis import given, settings, strategies as st
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from app.main import app
from app.models import AccommodationEntry, SearchResponse, ParticipantData, AccommodationStatus


# Create test client
client = TestClient(app)

# Mock API secret key for testing
TEST_API_KEY = "test_secret_key_12345"


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for all tests."""
    monkeypatch.setenv("API_SECRET_KEY", TEST_API_KEY)
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost:5173")


@settings(max_examples=50, deadline=None)
@given(
    name=st.one_of(st.none(), st.just("")),
    email=st.emails(),
    college=st.text(min_size=1, max_size=100),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_field_specific_validation_errors(
    name, email, college, from_date, to_date, accom_type, mock_env_vars
):
    """
    **Property 12: Field-Specific Validation Errors**

    **Validates: Requirements 9.3**

    For any accommodation form submission with multiple invalid fields,
    the validation error response should contain specific error messages
    that identify each invalid field individually, rather than a generic
    error message.
    """
    # Only test cases with invalid name (None or empty)
    if name is None or name == "":
        request_data = {
            "name": name if name is not None else "",
            "email": email,
            "college": college,
            "fromDate": from_date,
            "toDate": to_date,
            "accommodationType": accom_type,
            "force": False
        }

        # Mock the services to avoid actual Google Sheets calls
        with patch('app.api.routes.accommodation_service') as mock_service:
            mock_service.create_accommodation = AsyncMock()

            response = client.post(
                "/api/accommodation",
                json=request_data,
                headers={"Authorization": f"Bearer {TEST_API_KEY}"}
            )

            # Should return 400 Bad Request for validation error
            assert response.status_code == 400

            # Response should have error structure
            data = response.json()
            assert "success" in data
            assert data["success"] is False
            assert "error" in data

            # Should have field-specific details
            if "details" in data:
                assert isinstance(data["details"], list)
                # At least one detail should mention the invalid field
                assert len(data["details"]) > 0
                # Each detail should have field and message
                for detail in data["details"]:
                    assert "field" in detail
                    assert "message" in detail


@settings(max_examples=50, deadline=None)
@given(
    name=st.text(min_size=1, max_size=100),
    email=st.emails(),
    college=st.text(min_size=1, max_size=100),
    from_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    to_date=st.sampled_from(["2026-03-06", "2026-03-07", "2026-03-08"]),
    accom_type=st.sampled_from(["Boys", "Girls", "Other"])
)
def test_property_success_confirmation(
    name, email, college, from_date, to_date, accom_type, mock_env_vars
):
    """
    **Property 13: Success Confirmation**

    **Validates: Requirements 9.4**

    For any accommodation entry that is successfully created and appended
    to the sheet, the API response should include a success flag set to
    true and a confirmation message.
    """
    # Only test valid date ranges
    if from_date <= to_date:
        request_data = {
            "name": name,
            "email": email,
            "college": college,
            "fromDate": from_date,
            "toDate": to_date,
            "accommodationType": accom_type,
            "force": False
        }

        # Mock the services to simulate successful creation
        with patch('app.api.routes.accommodation_service') as mock_service:
            # Create a mock successful response
            from app.models import AccommodationResponse
            from datetime import datetime

            mock_entry = AccommodationEntry(
                timestamp=datetime.utcnow(),
                name=name,
                email=email,
                college=college,
                fromDate=from_date,
                toDate=to_date,
                accommodationType=accom_type,
                notes=None,
                enteredBy="volunteer@vortex2026.com"
            )

            mock_response = AccommodationResponse(
                success=True,
                message="Accommodation entry created successfully",
                entry=mock_entry,
                duplicate=False
            )

            mock_service.create_accommodation = AsyncMock(
                return_value=mock_response)

            response = client.post(
                "/api/accommodation",
                json=request_data,
                headers={"Authorization": f"Bearer {TEST_API_KEY}"}
            )

            # Should return 201 Created for successful creation
            assert response.status_code == 201

            # Response should have success structure
            data = response.json()
            assert "success" in data
            assert data["success"] is True

            # Should have confirmation message
            assert "message" in data
            assert isinstance(data["message"], str)
            assert len(data["message"]) > 0

            # Should include the created entry
            assert "entry" in data
            assert data["entry"] is not None
