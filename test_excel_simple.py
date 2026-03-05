#!/usr/bin/env python3
"""
Simple test script to verify Excel file loading.
Run from backend directory: python test_excel_simple.py
"""

import pandas as pd
from pathlib import Path


def test_excel_loading():
    """Test loading Excel file directly."""

    print("=" * 60)
    print("Testing Excel File Loading")
    print("=" * 60)

    # Path to Excel file
    excel_path = "data/vortex26_registrations.xlsx"

    print(f"\n1. Checking if file exists: {excel_path}")

    if not Path(excel_path).exists():
        print(f"✗ File not found: {excel_path}")
        print(f"\nCurrent directory: {Path.cwd()}")
        print("\nTry using absolute path in .env:")
        print("REGISTRATION_DATA_PATH=/Users/vishnu/Desktop/Vortex/backend/data/vortex26_registrations.xlsx")
        return False

    print(f"✓ File exists")

    try:
        print(f"\n2. Loading Excel file...")
        df = pd.read_excel(excel_path, engine='openpyxl')

        print(f"✓ Successfully loaded Excel file")
        print(f"\n3. File statistics:")
        print(f"   Total rows: {len(df)}")
        print(f"   Total columns: {len(df.columns)}")
        print(f"   Columns: {', '.join(df.columns.tolist())}")

        # Check for required columns
        required_cols = ['name', 'email', 'phone', 'college', 'city']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(
                f"\n⚠ Warning: Missing required columns: {', '.join(missing_cols)}")
        else:
            print(f"\n✓ All required columns present")

        # Show sample data
        if len(df) > 0:
            print(f"\n4. Sample data (first row):")
            first_row = df.iloc[0]
            for col in df.columns:
                value = first_row[col]
                if pd.notna(value):
                    print(f"   {col}: {value}")

        print("\n" + "=" * 60)
        print("✓ Excel file is valid and ready to use!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Error loading Excel file: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = test_excel_loading()
    sys.exit(0 if success else 1)
