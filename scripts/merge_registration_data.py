#!/usr/bin/env python3
"""
Merge new Excel registration data with existing JSON data.
Updates existing users with new Events/Workshops/Internship and adds new users.
"""

import pandas as pd
import json
from pathlib import Path


def merge_registration_data():
    """Merge new Excel data with existing JSON data."""

    # Paths
    excel_path = Path("data/vortex26_registrations.xlsx")
    json_path = Path("data/registration_data.json")
    backup_path = Path("data/registration_data_backup.json")

    print(f"Merging {excel_path} with {json_path}...")

    try:
        # Backup existing JSON
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            print(f"✓ Backup created: {backup_path}")
        else:
            existing_data = []

        # Create lookup by email for existing data
        existing_by_email = {record['email'].lower(
        ): record for record in existing_data if record.get('email')}

        # Read new Excel file
        df = pd.read_excel(excel_path, engine='openpyxl')

        # Normalize column names
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

        # Replace NaN with None
        df = df.replace({pd.NA: None, pd.NaT: None})
        df = df.where(pd.notna(df), None)
        new_data = df.to_dict('records')

        # Clean up the new data
        for record in new_data:
            if record.get('phone') is not None:
                try:
                    record['phone'] = str(int(record['phone']))
                except (ValueError, TypeError):
                    record['phone'] = None

            # Convert events and workshops to lists
            for field in ['events', 'workshops']:
                value = record.get(field)
                if value is None or value == '':
                    record[field] = []
                elif isinstance(value, str):
                    record[field] = [item.strip()
                                     for item in value.split(',') if item.strip()]
                else:
                    record[field] = []

            # Ensure college is a string
            if record.get('college') is None:
                record['college'] = ''

        # Merge logic
        updated_count = 0
        new_count = 0
        merged_data = []

        for new_record in new_data:
            email = new_record.get('email')
            if not email:
                continue

            email_lower = email.lower()

            if email_lower in existing_by_email:
                # Update existing record
                existing_record = existing_by_email[email_lower]

                # Merge events (union of both lists)
                existing_events = set(existing_record.get('events', []))
                new_events = set(new_record.get('events', []))
                merged_events = sorted(list(existing_events | new_events))

                # Merge workshops (union of both lists)
                existing_workshops = set(existing_record.get('workshops', []))
                new_workshops = set(new_record.get('workshops', []))
                merged_workshops = sorted(
                    list(existing_workshops | new_workshops))

                # Update internship if new data has it
                new_internship = new_record.get('summer_internship')
                if new_internship and new_internship != 'No':
                    existing_record['summer_internship'] = new_internship

                # Check if anything changed
                if (merged_events != sorted(existing_record.get('events', [])) or
                    merged_workshops != sorted(existing_record.get('workshops', [])) or
                        new_internship and new_internship != existing_record.get('summer_internship')):
                    updated_count += 1

                # Update the record
                existing_record['events'] = merged_events
                existing_record['workshops'] = merged_workshops

                merged_data.append(existing_record)
                # Remove from lookup so we don't add it again
                del existing_by_email[email_lower]
            else:
                # New user
                merged_data.append(new_record)
                new_count += 1

        # Add remaining existing users that weren't in the new data
        for remaining_record in existing_by_email.values():
            merged_data.append(remaining_record)

        # Sort by ID if available
        merged_data.sort(key=lambda x: x.get('id', 0) or 0)

        # Write merged data to JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Successfully merged data:")
        print(f"  - Total records: {len(merged_data)}")
        print(f"  - Updated existing users: {updated_count}")
        print(f"  - New users added: {new_count}")
        print(
            f"  - Unchanged users: {len(merged_data) - updated_count - new_count}")
        print(f"✓ JSON file updated: {json_path}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    success = merge_registration_data()
    sys.exit(0 if success else 1)
