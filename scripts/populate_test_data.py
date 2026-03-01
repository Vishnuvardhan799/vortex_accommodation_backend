#!/usr/bin/env python3
"""
Script to populate Google Sheets with sample accommodation data for testing.

This script adds realistic test data to the accommodation sheet, including:
- Participants with accommodation (matching registration data)
- Various accommodation types (Boys, Girls, Other)
- Different date ranges
- Some with notes
"""

from app.models.schemas import AccommodationEntry
from app.repositories.sheets_repository import SheetsRepository
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# Sample accommodation data matching participants from registration data
SAMPLE_ACCOMMODATIONS = [
    {
        "name": "Aarav Sharma",
        "email": "aarav.sharma@nitt.edu",
        "phone": "+91 9876543210",
        "college": "NIT Trichy",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Boys",
        "notes": "Early arrival",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Priya Patel",
        "email": "priya.patel@iitm.ac.in",
        "phone": "+91 9876543211",
        "college": "IIT Madras",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Girls",
        "notes": None,
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Rahul Kumar",
        "email": "rahul.kumar@vit.ac.in",
        "phone": "+91 9876543212",
        "college": "VIT Vellore",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-07",
        "accommodationType": "Boys",
        "notes": "Leaving early",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Ananya Reddy",
        "email": "ananya.reddy@bits-pilani.ac.in",
        "phone": "+91 9876543213",
        "college": "BITS Pilani",
        "fromDate": "2026-03-07",
        "toDate": "2026-03-08",
        "accommodationType": "Girls",
        "notes": "Late arrival",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Arjun Nair",
        "email": "arjun.nair@nitk.edu.in",
        "phone": "+91 9876543214",
        "college": "NIT Karnataka",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Boys",
        "notes": None,
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Sneha Iyer",
        "email": "sneha.iyer@annauniv.edu",
        "phone": "+91 9876543215",
        "college": "Anna University",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Girls",
        "notes": "Vegetarian food preference",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Vikram Singh",
        "email": "vikram.singh@dtu.ac.in",
        "phone": "+91 9876543216",
        "college": "Delhi Technological University",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Boys",
        "notes": None,
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Divya Menon",
        "email": "divya.menon@nitt.edu",
        "phone": "+91 9876543217",
        "college": "NIT Trichy",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Girls",
        "notes": "Local student",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Karthik Krishnan",
        "email": "karthik.k@psgtech.ac.in",
        "phone": "+91 9876543218",
        "college": "PSG College of Technology",
        "fromDate": "2026-03-07",
        "toDate": "2026-03-08",
        "accommodationType": "Boys",
        "notes": "Arriving on Day 2",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Meera Desai",
        "email": "meera.desai@manipal.edu",
        "phone": "+91 9876543219",
        "college": "Manipal Institute of Technology",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-07",
        "accommodationType": "Girls",
        "notes": None,
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Rohan Gupta",
        "email": "rohan.gupta@iitkgp.ac.in",
        "phone": "+91 9876543220",
        "college": "IIT Kharagpur",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Boys",
        "notes": "Team leader for hackathon",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Aisha Khan",
        "email": "aisha.khan@jadavpur.edu.in",
        "phone": "+91 9876543221",
        "college": "Jadavpur University",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Girls",
        "notes": None,
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Siddharth Rao",
        "email": "siddharth.rao@srm.edu.in",
        "phone": "+91 9876543222",
        "college": "SRM Institute of Science and Technology",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Boys",
        "notes": "Robotics team member",
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Kavya Pillai",
        "email": "kavya.pillai@cusat.ac.in",
        "phone": "+91 9876543223",
        "college": "Cochin University of Science and Technology",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Girls",
        "notes": None,
        "enteredBy": "volunteer@nitt.edu"
    },
    {
        "name": "Aditya Verma",
        "email": "aditya.verma@nitw.ac.in",
        "phone": "+91 9876543224",
        "college": "NIT Warangal",
        "fromDate": "2026-03-06",
        "toDate": "2026-03-08",
        "accommodationType": "Boys",
        "notes": "Special dietary requirements",
        "enteredBy": "volunteer@nitt.edu"
    }
]


async def populate_test_data():
    """Populate Google Sheets with sample accommodation data."""
    print("🚀 Starting test data population...")
    print(f"📊 Will add {len(SAMPLE_ACCOMMODATIONS)} accommodation entries\n")

    try:
        # Initialize repository
        repo = SheetsRepository()

        # Verify connection
        print("🔌 Verifying Google Sheets connection...")
        if not repo.verify_connection():
            print("❌ Failed to connect to Google Sheets")
            return False
        print("✅ Connected successfully\n")

        # Add each accommodation entry
        success_count = 0
        for i, data in enumerate(SAMPLE_ACCOMMODATIONS, 1):
            try:
                # Create entry with current timestamp
                entry = AccommodationEntry(
                    timestamp=datetime.utcnow(),
                    **data
                )

                # Append to sheet
                await repo.append_accommodation(entry)
                print(
                    f"✅ [{i}/{len(SAMPLE_ACCOMMODATIONS)}] Added: {data['name']} ({data['email']})")
                success_count += 1

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

            except Exception as e:
                print(
                    f"❌ [{i}/{len(SAMPLE_ACCOMMODATIONS)}] Failed to add {data['name']}: {str(e)}")

        print(
            f"\n🎉 Completed! Successfully added {success_count}/{len(SAMPLE_ACCOMMODATIONS)} entries")
        return True

    except Exception as e:
        print(f"❌ Error during population: {str(e)}")
        return False


if __name__ == "__main__":
    success = asyncio.run(populate_test_data())
    sys.exit(0 if success else 1)
