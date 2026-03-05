#!/usr/bin/env python3
"""
Convert Excel registration data to JSON format.
Run this before deploying to production.
"""

import pandas as pd
import json
from pathlib import Path


def convert_excel_to_json():
    """Convert Excel file to JSON format."""

    # Paths
    excel_path = Path("data/vortex26_registrations.xlsx")
    json_path = Path("data/registration_data.json")

    print(f"Converting {excel_path} to {json_path}...")

    try:
        # Read Excel file
        df = pd.read_excel(excel_path, engine='openpyxl')

        # Normalize column names to lowercase
        df.columns = df.columns.str.lower().str.strip()

        # Handle column name variations
        column_mapping = {
            'year': 'year',
            'gender': 'gender',
            'summer internship': 'summer_internship',
            '#': 'id',
        }
        df = df.rename(columns=column_mapping)

        # Add city column if missing
        if 'city' not in df.columns:
            df['city'] = ''

        # Replace NaN with None and convert to list of dictionaries
        df = df.replace({pd.NA: None, pd.NaT: None})
        df = df.where(pd.notna(df), None)
        data = df.to_dict('records')

        # Clean up the data - convert float phone numbers to strings
        for record in data:
            if record.get('phone') is not None:
                try:
                    # Convert to int first to remove decimal, then to string
                    record['phone'] = str(int(record['phone']))
                except (ValueError, TypeError):
                    record['phone'] = None

            # Convert events and workshops from comma-separated strings to lists
            for field in ['events', 'workshops']:
                value = record.get(field)
                if value is None or value == '':
                    record[field] = []
                elif isinstance(value, str):
                    # Split by comma and strip whitespace
                    record[field] = [item.strip()
                                     for item in value.split(',') if item.strip()]
                else:
                    record[field] = []

            # Ensure college is a string, not None
            if record.get('college') is None:
                record['college'] = ''

        # Write to JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✓ Successfully converted {len(data)} records")
        print(f"✓ JSON file created: {json_path}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = convert_excel_to_json()
    sys.exit(0 if success else 1)
