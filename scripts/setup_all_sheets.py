#!/usr/bin/env python3
"""
Google Sheets Setup Script for Vortex 2026 - All Three Sheets

This script initializes all three Google Sheets (Accommodation, Events, Workshops)
with proper headers and formatting.

Usage:
    python scripts/setup_all_sheets.py
"""

import os
import sys
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()


def load_credentials():
    """Load Google service account credentials from environment."""
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        print("❌ Error: GOOGLE_CREDENTIALS_JSON environment variable not set")
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


def setup_accommodation_sheet(client, sheet_id):
    """Set up accommodation sheet."""
    print("\n" + "="*70)
    print("Setting up ACCOMMODATION sheet")
    print("="*70)

    try:
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.sheet1
        print(f"✓ Opened sheet: {sheet.title}")
    except Exception as e:
        print(f"❌ Error opening accommodation sheet: {e}")
        return False

    headers = [
        "Timestamp", "Name", "Email", "Phone", "College",
        "From Date", "To Date", "Accommodation Type", "Notes", "Entered By"
    ]

    worksheet.clear()
    worksheet.update(values=[headers], range_name='A1')
    print("✓ Headers configured")

    worksheet.freeze(rows=1)
    worksheet.format('A1:J1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.8},
        'horizontalAlignment': 'CENTER'
    })
    print("✓ Formatting applied")
    print(f"✓ Accommodation sheet ready: {sheet.url}")
    return True


def setup_events_sheet(client, sheet_id):
    """Set up events sheet."""
    print("\n" + "="*70)
    print("Setting up EVENTS sheet")
    print("="*70)

    try:
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.sheet1
        print(f"✓ Opened sheet: {sheet.title}")
    except Exception as e:
        print(f"❌ Error opening events sheet: {e}")
        return False

    headers = [
        "Timestamp", "Name", "Email", "Phone", "Event Names",
        "Team Name", "Payment Status", "Notes", "Entered By"
    ]

    worksheet.clear()
    worksheet.update(values=[headers], range_name='A1')
    print("✓ Headers configured")

    worksheet.freeze(rows=1)
    worksheet.format('A1:I1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.9, 'green': 0.6, 'blue': 0.2},
        'horizontalAlignment': 'CENTER'
    })
    print("✓ Formatting applied")
    print(f"✓ Events sheet ready: {sheet.url}")
    return True


def setup_workshops_sheet(client, sheet_id):
    """Set up workshops sheet."""
    print("\n" + "="*70)
    print("Setting up WORKSHOPS sheet")
    print("="*70)

    try:
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.sheet1
        print(f"✓ Opened sheet: {sheet.title}")
    except Exception as e:
        print(f"❌ Error opening workshops sheet: {e}")
        return False

    headers = [
        "Timestamp", "Name", "Email", "Phone", "Workshop Names",
        "Payment Status", "Notes", "Entered By"
    ]

    worksheet.clear()
    worksheet.update(values=[headers], range_name='A1')
    print("✓ Headers configured")

    worksheet.freeze(rows=1)
    worksheet.format('A1:H1', {
        'textFormat': {'bold': True},
        'backgroundColor': {'red': 0.4, 'green': 0.8, 'blue': 0.4},
        'horizontalAlignment': 'CENTER'
    })
    print("✓ Formatting applied")
    print(f"✓ Workshops sheet ready: {sheet.url}")
    return True


def main():
    """Main setup function."""
    print("\n" + "="*70)
    print("Vortex 2026 - Google Sheets Setup (All Three Sheets)")
    print("="*70 + "\n")

    accommodation_sheet_id = os.getenv("ACCOMMODATION_SHEET_ID")
    events_sheet_id = os.getenv("EVENTS_SHEET_ID")
    workshops_sheet_id = os.getenv("WORKSHOPS_SHEET_ID")

    if not accommodation_sheet_id:
        print("❌ Error: ACCOMMODATION_SHEET_ID not set")
        sys.exit(1)
    if not events_sheet_id:
        print("❌ Error: EVENTS_SHEET_ID not set")
        sys.exit(1)
    if not workshops_sheet_id:
        print("❌ Error: WORKSHOPS_SHEET_ID not set")
        sys.exit(1)

    print("Sheet IDs found:")
    print(f"  - Accommodation: {accommodation_sheet_id}")
    print(f"  - Events: {events_sheet_id}")
    print(f"  - Workshops: {workshops_sheet_id}\n")

    print("Loading credentials...")
    credentials = load_credentials()
    print("✓ Credentials loaded\n")

    print("Connecting to Google Sheets API...")
    client = gspread.authorize(credentials)
    print("✓ Connected to Google Sheets API\n")

    success_count = 0

    if setup_accommodation_sheet(client, accommodation_sheet_id):
        success_count += 1

    if setup_events_sheet(client, events_sheet_id):
        success_count += 1

    if setup_workshops_sheet(client, workshops_sheet_id):
        success_count += 1

    print("\n" + "="*70)
    print("SETUP SUMMARY")
    print("="*70)
    print(f"Successfully configured: {success_count}/3 sheets")

    if success_count == 3:
        print("\n✅ All sheets are ready!")
        print("\nYou can now start the backend application.")
        print("The API will automatically connect to these sheets.\n")
    else:
        print("\n⚠️  Some sheets failed to configure. Please check the errors above.\n")
        sys.exit(1)


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
