"""
Unit tests for RegistrationRepository.

Tests specific examples, edge cases, and error handling for the
registration data repository.

Validates: Requirements 1.2
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from app.repositories.registration_repository import RegistrationRepository
from app.models import RegistrationData


class TestRegistrationRepository:
    """Test suite for RegistrationRepository class."""

    def test_load_valid_registration_data(self):
        """Test loading valid registration data from JSON file."""
        # Arrange
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "college": "NIT Trichy",
                "events": ["Event A", "Event B"],
                "workshops": ["Workshop X"]
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "college": "IIT Madras",
                "events": ["Event C"],
                "workshops": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Act
            repo = RegistrationRepository(temp_file)

            # Assert
            assert repo.get_participant_count() == 2
            assert len(repo.email_index) == 2

        finally:
            os.unlink(temp_file)

    def test_find_by_email_existing_participant(self):
        """Test finding an existing participant by email."""
        # Arrange
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "college": "NIT Trichy",
                "events": ["Event A"],
                "workshops": ["Workshop X"]
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            repo = RegistrationRepository(temp_file)

            # Act
            result = repo.find_by_email("john@example.com")

            # Assert
            assert result is not None
            assert result.name == "John Doe"
            assert result.email == "john@example.com"
            assert result.college == "NIT Trichy"
            assert result.events == ["Event A"]
            assert result.workshops == ["Workshop X"]

        finally:
            os.unlink(temp_file)

    def test_find_by_email_nonexistent_participant(self):
        """Test searching for a non-existent participant returns None."""
        # Arrange
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "college": "NIT Trichy",
                "events": [],
                "workshops": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            repo = RegistrationRepository(temp_file)

            # Act
            result = repo.find_by_email("nonexistent@example.com")

            # Assert
            assert result is None

        finally:
            os.unlink(temp_file)

    def test_case_insensitive_email_lookup(self):
        """Test that email lookup is case-insensitive."""
        # Arrange
        test_data = [
            {
                "name": "John Doe",
                "email": "John.Doe@Example.COM",
                "college": "NIT Trichy",
                "events": [],
                "workshops": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            repo = RegistrationRepository(temp_file)

            # Act - search with different case variations
            result_lower = repo.find_by_email("john.doe@example.com")
            result_upper = repo.find_by_email("JOHN.DOE@EXAMPLE.COM")
            result_mixed = repo.find_by_email("John.Doe@Example.COM")

            # Assert - all should find the same participant
            assert result_lower is not None
            assert result_upper is not None
            assert result_mixed is not None
            assert result_lower.name == result_upper.name == result_mixed.name

        finally:
            os.unlink(temp_file)

    def test_email_with_whitespace_trimmed(self):
        """Test that email lookup trims whitespace."""
        # Arrange
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "college": "NIT Trichy",
                "events": [],
                "workshops": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            repo = RegistrationRepository(temp_file)

            # Act - search with whitespace
            result = repo.find_by_email("  john@example.com  ")

            # Assert
            assert result is not None
            assert result.email == "john@example.com"

        finally:
            os.unlink(temp_file)

    def test_empty_dataset(self):
        """Test repository with empty dataset."""
        # Arrange
        test_data = []

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Act
            repo = RegistrationRepository(temp_file)

            # Assert
            assert repo.get_participant_count() == 0
            assert len(repo.email_index) == 0
            assert repo.find_by_email("any@example.com") is None

        finally:
            os.unlink(temp_file)

    def test_participant_with_empty_events_and_workshops(self):
        """Test participant with empty events and workshops lists."""
        # Arrange
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "college": "NIT Trichy",
                "events": [],
                "workshops": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            repo = RegistrationRepository(temp_file)

            # Act
            result = repo.find_by_email("john@example.com")

            # Assert
            assert result is not None
            assert result.events == []
            assert result.workshops == []

        finally:
            os.unlink(temp_file)

    def test_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            RegistrationRepository("/nonexistent/path/to/file.json")

        assert "not found" in str(exc_info.value).lower()

    def test_invalid_json_format(self):
        """Test that JSONDecodeError is raised for invalid JSON."""
        # Arrange - create file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name

        try:
            # Act & Assert
            with pytest.raises(json.JSONDecodeError):
                RegistrationRepository(temp_file)

        finally:
            os.unlink(temp_file)

    def test_invalid_data_format_not_array(self):
        """Test that ValueError is raised when data is not an array."""
        # Arrange - create file with object instead of array
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"name": "John"}, f)
            temp_file = f.name

        try:
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                RegistrationRepository(temp_file)

            assert "array" in str(exc_info.value).lower()

        finally:
            os.unlink(temp_file)

    def test_skip_invalid_participant_records(self):
        """Test that invalid participant records are skipped with warning."""
        # Arrange - mix of valid and invalid records
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "college": "NIT Trichy",
                "events": [],
                "workshops": []
            },
            {
                "name": "Invalid",
                "email": "not-an-email",  # Invalid email format
                "college": "Test College",
                "events": [],
                "workshops": []
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "college": "IIT Madras",
                "events": [],
                "workshops": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            # Act
            repo = RegistrationRepository(temp_file)

            # Assert - only valid records should be loaded
            assert repo.get_participant_count() == 2
            assert repo.find_by_email("john@example.com") is not None
            assert repo.find_by_email("jane@example.com") is not None
            assert repo.find_by_email("not-an-email") is None

        finally:
            os.unlink(temp_file)

    def test_get_all_participants(self):
        """Test retrieving all participants."""
        # Arrange
        test_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "college": "NIT Trichy",
                "events": [],
                "workshops": []
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "college": "IIT Madras",
                "events": [],
                "workshops": []
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            repo = RegistrationRepository(temp_file)

            # Act
            all_participants = repo.get_all_participants()

            # Assert
            assert len(all_participants) == 2
            assert all(isinstance(p, RegistrationData)
                       for p in all_participants)

        finally:
            os.unlink(temp_file)

    def test_email_index_building(self):
        """Test that email index is built correctly for O(1) lookups."""
        # Arrange
        test_data = [
            {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "college": "Test College",
                "events": [],
                "workshops": []
            }
            for i in range(100)
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name

        try:
            repo = RegistrationRepository(temp_file)

            # Act & Assert - verify index contains all emails
            assert len(repo.email_index) == 100

            # Verify random lookups work
            assert repo.find_by_email("user0@example.com") is not None
            assert repo.find_by_email("user50@example.com") is not None
            assert repo.find_by_email("user99@example.com") is not None

        finally:
            os.unlink(temp_file)
