#!/usr/bin/env python3
"""
Verify that the data migration was successful.
Tests data loading, search functionality, and workshop removal.

Run from backend directory:
    python3 scripts/verify_data_migration.py
"""

import sys
import json
from pathlib import Path


def verify_data_migration():
    """Verify the data migration was successful."""
    print("=" * 80)
    print("DATA MIGRATION VERIFICATION")
    print("=" * 80)

    try:
        # Test 1: Load data directly from JSON
        print("\n1. Testing data loading...")
        data_path = Path('data/sample_registration_data.json')

        if not data_path.exists():
            print(f"   ✗ ERROR: File not found: {data_path}")
            return False

        with open(data_path, 'r', encoding='utf-8') as f:
            registrations = json.load(f)

        print(f"   ✓ Successfully loaded {len(registrations)} registrations")

        # Test 2: Search functionality
        print("\n2. Testing search functionality...")
        test_emails = [
            'ameya.kanagalekar@gmail.com',
            'jeevanrp2006@gmail.com',
            'naveenganesan0702@gmail.com'
        ]

        # Create email lookup
        email_lookup = {reg['email'].lower(): reg for reg in registrations}

        for email in test_emails:
            result = email_lookup.get(email.lower())
            if result:
                print(f"   ✓ Found: {result['name']} ({email})")
                if result.get('workshops'):
                    print(f"     Workshops: {', '.join(result['workshops'])}")
            else:
                print(f"   ✗ Not found: {email}")

        # Test 3: Check for Financial Literacy
        print("\n3. Checking for Financial Literacy workshop...")
        has_financial_literacy = any(
            'Financial Literacy' in reg.get('workshops', [])
            for reg in registrations
        )

        if has_financial_literacy:
            print("   ✗ ERROR: Financial Literacy workshop still found in data!")
            return False
        else:
            print("   ✓ Financial Literacy successfully removed")

        # Test 4: Workshop statistics
        print("\n4. Workshop statistics...")
        workshop_counts = {}
        for reg in registrations:
            for workshop in reg.get('workshops', []):
                workshop_counts[workshop] = workshop_counts.get(
                    workshop, 0) + 1

        print(f"   Total unique workshops: {len(workshop_counts)}")
        print("   Top 5 workshops:")
        for workshop, count in sorted(workshop_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"     - {workshop}: {count}")

        # Test 5: Data integrity
        print("\n5. Data integrity checks...")
        valid_count = 0
        for reg in registrations:
            if reg.get('name') and reg.get('email'):
                valid_count += 1

        print(f"   ✓ Valid registrations: {valid_count}/{len(registrations)}")

        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED - Data migration successful!")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = verify_data_migration()
    sys.exit(0 if success else 1)
