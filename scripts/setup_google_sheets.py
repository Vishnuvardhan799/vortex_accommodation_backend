#!/usr/bin/env python3
"""
Google Sheets Setup Script for Vortex 2026 Accommodation System

This script initializes a Google Sheet with the proper headers and formatting
for the accommodation data.

Validates: Requirements 5.1, 5.2, 5.3

Usage:
    python scripts/setup_google_sheets.py

Prerequisites:
    - Google Cloud project with Sheets API enabled
    - Service account credentials JSON file
    - GOOGLE_CREDENTIALS_JSON and SHEET_NAME environment variables set
"""

import os
import sys
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()


def load_credentials():
    """Load Google service account credentials from environment."""
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        print("❌ Error: GOOGLE_CREDENTIALS_JSON environment variable not set")
        print("Please set this variable in your .env file")
        sys.exit(1)

    try:
        creds_dict = json.loads(creds_json)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in GOOGLE_CREDENTIALS_JSON: {e}")
        sys.exit(1)

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials = Credentials.from_service_account_info(
        creds_dict, scopes=scopes)
    return credentials


def get_or_create_sheet(client, sheet_name):
    """Get existing sheet or create a new one."""
    try:
        # Try to open existing sheet
        sheet = client.open(sheet_name)
        print(f"✓ Found existing sheet: {sheet_name}")
        return sheet, False
    except gspread.exceptions.SpreadsheetNotFound:
        # Create new sheet
        print(f"Creating new sheet: {sheet_name}")
        sheet = client.create(sheet_name)
        print(f"✓ Created new sheet: {sheet_name}")
        return sheet, True


def setup_headers(worksheet):
    """Set up the header row with proper column names."""
    headers = [
        "Timestamp",
        "Name",
        "Email",
        "College",
        "From Date",
        "To Date",
        "Accommodation Type",
        "Notes",
        "Entered By"
    ]

    # Set headers in first row
    worksheet.update('A1:I1', [headers])
    print("✓ Headers configured")

    return headers


def format_sheet(worksheet):
    """Apply formatting to the sheet."""
    # Freeze header row
    worksheet.freeze(rows=1)
    print("✓ Header row frozen")

    # Format header row (bold, background color)
    worksheet.format('A1:I1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
        'horizontalAlignment': 'CENTER'
    })
    print("✓ Header formatting applied")

    # Set column widths
    worksheet.set_column_width('A', 180)  # Timestamp
    worksheet.set_column_width('B', 200)  # Name
    worksheet.set_column_width('C', 250)  # Email
    worksheet.set_column_width('D', 250)  # College
    worksheet.set_column_width('E', 120)  # From Date
    worksheet.set_column_width('F', 120)  # To Date
    worksheet.set_column_width('G', 150)  # Accommodation Type
    worksheet.set_column_width('H', 300)  # Notes
    worksheet.set_column_width('I', 200)  # Entered By
    print("✓ Column widths set")

    # Add data validation for Accommodation Type column (G)
    # This will be applied to rows 2-1000
    worksheet.add_validation('G2:G1000', {
        'condition': {
            'type': 'ONE_OF_LIST',
            'values': [
                {'userEnteredValue': 'Boys'},
                {'userEnteredValue': 'Girls'},
                {'userEnteredValue': 'Other'}
            ]
        },
        'strict': True,
        'showCustomUi': True
    })
    print("✓ Data validation added for Accommodation Type")

    # Add conditional formatting to highlight duplicate emails
    worksheet.add_conditional_formatting('C2:C1000', {
        'condition': {
            'type': 'CUSTOM_FORMULA',
            'values': [{'userEnteredValue': '=COUNTIF($C$2:$C$1000,C2)>1'}]
        },
        'format': {
            'backgroundColor': {'red': 1.0, 'green': 0.9, 'blue': 0.4}
        }
    })
    print("✓ Conditional formatting added for duplicate emails")


def share_sheet(sheet, service_account_email):
    """Share the sheet with instructions."""
    print("\n" + "="*70)
    print("IMPORTANT: Sheet Sharing Instructions")
    print("="*70)
    print(
        f"\nThe sheet has been created with service account: {service_account_email}")
    print("\nTo allow volunteers to view the sheet (optional):")
    print(f"1. Open the sheet: {sheet.url}")
    print("2. Click 'Share' button")
    print("3. Add volunteer email addresses with 'Viewer' or 'Editor' access")
    print("\nNote: The backend API will access the sheet using the service account.")
    print("Volunteers don't need direct access unless you want them to view it manually.")
    print("="*70 + "\n")


def add_sample_data(worksheet):
    """Add a sample row to demonstrate the format."""
    sample_row = [
        "2026-03-06T10:00:00Z",
        "Sample Participant",
        "sample@example.com",
        "Sample College",
        "2026-03-06",
        "2026-03-08",
        "Boys",
        "This is a sample entry - you can delete this row",
        "admin@vortex2026.com"
    ]

    worksheet.append_row(sample_row)
    print("✓ Sample data row added (you can delete this later)")


def main():
    """Main setup function."""
    print("\n" + "="*70)
    print("Vortex 2026 Accommodation System - Google Sheets Setup")
    print("="*70 + "\n")

    # Get sheet name from environment
    sheet_name = os.getenv("SHEET_NAME")
    if not sheet_name:
        print("❌ Error: SHEET_NAME environment variable not set")
        print("Please set this variable in your .env file")
        sys.exit(1)

    print(f"Sheet name: {sheet_name}\n")

    # Load credentials
    print("Loading credentials...")
    credentials = load_credentials()
    print("✓ Credentials loaded\n")

    # Initialize gspread client
    print("Connecting to Google Sheets API...")
    client = gspread.authorize(credentials)
    print("✓ Connected to Google Sheets API\n")

    # Get or create sheet
    print("Setting up sheet...")
    sheet, is_new = get_or_create_sheet(client, sheet_name)

    # Get the first worksheet
    worksheet = sheet.sheet1

    if is_new:
        # Set up headers
        print("\nConfiguring headers...")
        setup_headers(worksheet)

        # Apply formatting
        print("\nApplying formatting...")
        format_sheet(worksheet)

        # Add sample data
        print("\nAdding sample data...")
        add_sample_data(worksheet)
    else:
        print("\n⚠️  Sheet already exists. Checking configuration...")
        response = input(
            "Do you want to reconfigure the sheet? This will overwrite existing headers. (yes/no): ")
        if response.lower() in ['yes', 'y']:
            print("\nReconfiguring sheet...")
            setup_headers(worksheet)
            format_sheet(worksheet)
            print("✓ Sheet reconfigured")
        else:
            print("Skipping reconfiguration")

    # Get service account email
    service_account_email = credentials.service_account_email

    # Print sharing instructions
    share_sheet(sheet, service_account_email)

    # Print success message
    print("✅ Setup complete!\n")
    print(f"Sheet URL: {sheet.url}")
    print(f"Sheet ID: {sheet.id}")
    print("\nYou can now start the backend application.")
    print("The API will automatically connect to this sheet.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
