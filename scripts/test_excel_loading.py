#!/usr/bin/env python3
"""
Test script to verify Excel file loading functionality.

This script tests the registration repository's ability to load data
directly from the Excel file.
"""

from app.repositories.registration_repository import RegistrationRepository
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Change to backend directory for relative paths to work
os.chdir(backend_dir)


def test_excel_loading():
    """Test loading registration data from Excel file."""

    print("=" * 60)
    print("Testing Excel File Loading")
    print("=" * 60)

    # Path to Excel file
    excel_path = "data/vortex26_registrations.xlsx"

    print(f"\n1. Loading data from: {excel_path}")

    try:
        # Initialize repository with Excel file
        repo = RegistrationRepository(excel_path)

        print(f"✓ Successfully loaded Excel file")

        # Get participant count
        count = repo.get_participant_count()
        print(f"\n2. Total participants loaded: {count}")

        # Test email lookup
        if count > 0:
            # Get first participant
            all_participants = repo.get_all_participants()
            first_participant = all_participants[0]

            print(f"\n3. Testing email lookup...")
            print(f"   Looking up: {first_participant.email}")

            # Test case-insensitive lookup
            result = repo.find_by_email(first_participant.email.upper())

            if result:
                print(f"✓ Email lookup successful (case-insensitive)")
                print(f"\n4. Sample participant data:")
                print(f"   Name: {result.name}")
                print(f"   Email: {result.email}")
                print(f"   Phone: {result.phone}")
                print(f"   College: {result.college}")
                print(f"   City: {result.city}")

                # Display events if available
                if result.events:
                    print(f"   Events: {', '.join(result.events)}")

                # Display workshops if available
                if result.workshops:
                    print(f"   Workshops: {', '.join(result.workshops)}")
            else:
                print("✗ Email lookup failed")

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

        return True

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure the Excel file exists at the specified path.")
        return False

    except Exception as e:
        print(f"\n✗ Error loading Excel file: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_excel_loading()
    sys.exit(0 if success else 1)
