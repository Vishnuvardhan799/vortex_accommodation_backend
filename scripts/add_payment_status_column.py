"""
Script to add Payment Status column to accommodation sheet and fill existing rows.

This script:
1. Inserts a new "Payment Status" column after "Accommodation Type"
2. Fills all existing rows with "Paid" as the default value
3. Preserves all existing data

Usage:
    python scripts/add_payment_status_column.py
"""

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import gspread
import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_credentials():
    """Load Google service account credentials."""
    load_dotenv()

    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not credentials_json:
        raise ValueError("GOOGLE_CREDENTIALS_JSON not found in environment")

    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    creds_dict = json.loads(credentials_json)
    credentials = Credentials.from_service_account_info(
        creds_dict, scopes=scopes)

    return credentials


def add_payment_status_column():
    """Add Payment Status column and fill existing rows."""

    print("🔄 Loading credentials...")
    credentials = load_credentials()
    client = gspread.authorize(credentials)

    # Get sheet ID from environment
    sheet_id = os.getenv("ACCOMMODATION_SHEET_ID")
    if not sheet_id:
        raise ValueError("ACCOMMODATION_SHEET_ID not found in environment")

    print(f"📊 Opening accommodation sheet: {sheet_id}")
    spreadsheet = client.open_by_key(sheet_id)
    sheet = spreadsheet.sheet1

    # Get current header row
    print("📋 Reading current headers...")
    headers = sheet.row_values(1)
    print(f"Current headers: {headers}")

    # Check if Payment Status already exists
    if "Payment Status" in headers:
        print("⚠️  Payment Status column already exists!")
        response = input(
            "Do you want to fill existing empty cells with 'Paid'? (y/n): ")
        if response.lower() != 'y':
            print("❌ Aborted.")
            return

        # Find Payment Status column index
        payment_col_index = headers.index("Payment Status") + 1

    else:
        # Find the column index where we need to insert (after Accommodation Type)
        if "Accommodation Type" not in headers:
            print("❌ Error: 'Accommodation Type' column not found!")
            return

        accommodation_type_index = headers.index("Accommodation Type") + 1
        insert_col_index = accommodation_type_index + 1

        print(
            f"➕ Inserting 'Payment Status' column at position {insert_col_index}...")

        # Insert a new column after Accommodation Type
        sheet.insert_cols([[]], col=insert_col_index)

        # Add header
        sheet.update_cell(1, insert_col_index, "Payment Status")
        print("✅ Column inserted and header added!")

        payment_col_index = insert_col_index

    # Get all data to find how many rows have data
    print("📊 Reading all data...")
    all_data = sheet.get_all_values()

    # Count rows with data (excluding header)
    data_rows = len([row for row in all_data[1:]
                    if any(cell.strip() for cell in row)])

    if data_rows == 0:
        print("ℹ️  No data rows found. Only header exists.")
        return

    print(f"📝 Found {data_rows} rows with data")

    # Get column letter for Payment Status
    col_letter = gspread.utils.rowcol_to_a1(1, payment_col_index)[0]

    # Check which cells are empty in Payment Status column
    payment_col_values = sheet.col_values(payment_col_index)

    # Fill empty cells with "Paid" (starting from row 2)
    updates = []
    # +2 because row 1 is header and we start from row 2
    for row_num in range(2, data_rows + 2):
        if row_num > len(payment_col_values) or not payment_col_values[row_num - 1].strip():
            cell_address = f"{col_letter}{row_num}"
            updates.append({
                'range': cell_address,
                'values': [['Paid']]
            })

    if updates:
        print(f"💰 Filling {len(updates)} rows with 'Paid'...")
        sheet.batch_update(updates)
        print(f"✅ Successfully filled {len(updates)} rows with 'Paid'!")
    else:
        print("ℹ️  All rows already have payment status values.")

    # Display final result
    print("\n" + "="*60)
    print("✨ Update Complete!")
    print("="*60)
    print(f"📊 Sheet: {spreadsheet.title}")
    print(f"📍 Payment Status column: Column {col_letter}")
    print(f"✅ Total data rows: {data_rows}")
    print(f"💰 Rows filled with 'Paid': {len(updates)}")
    print("\n🎉 Your accommodation sheet is now ready for the new payment status feature!")


if __name__ == "__main__":
    try:
        add_payment_status_column()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
