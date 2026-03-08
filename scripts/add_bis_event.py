#!/usr/bin/env python3
"""
Script to add BIS event to participants
"""
import json
import csv
from pathlib import Path

# BIS event participants data
bis_event_data = """Jeevan R P	jeevanrp2006@gmail.com	8072406233	Achariya College Engineering Technology
Hari Kumar A	harikumar3868@gmail.com	8525059820	NIT Trichy
Thumbalam Mithun	thumbalammithun@gmail.com	8008869393	Ni trichy
Mohammad Tabish Ayman	tabishayman1538@gmail.com	7330856405	NITT
Karthikeyan TS	keyashqa@gmail.com	9445816403	National Institute of Technology Tiruchirappalli
Gnanaraj S	krishdeveloper2006@gmail.com	6380973585	AAA College of Engineering and Technology
Ram manideep	rammanideep998@gmail.com	6305249787	Nit Trichy
Sivaranjani	aranjanisiva8@gmail.com	9025270016	K.Ramakrishnan college of technology
Madhan Kumar S	madhanshankar2006@gmail.com	9345043376	Anna University Regional Campus Tirunelveli
Saravanan M	saravananm2119@gmail.com	9842820025	Achariya college of engineering technology
Pirrr Ateee	deviljsjunior@gmail.com	9360877548	nitt
Ragipalyam Ananda Swaroop	anandaswaroop2005@gmail.com	8815774884	NITT
Prateek Yadav	prateek.ydv.nitt@gmail.com	9938360804	NIT TRICHY
Abhishek Kumar	ak62002190@gmail.com	8252409305	NIT Tiruchirappalli
Mohammed Aasif	aasifibrahim04@gmail.com	7305948488	National Institute of Technology Tiruchirappalli
Kumari Sneha	kumarisneha0905@gmail.com	8544237626	NIT Trichy"""


def parse_bis_data():
    """Parse the BIS participant data"""
    entries = []
    for line in bis_event_data.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 4:
            entries.append({
                'name': parts[0].strip(),
                'email': parts[1].strip().lower(),
                'phone': parts[2].strip(),
                'college': parts[3].strip()
            })
    return entries


def load_csv_data():
    """Load CSV data to check for existing workshops/events"""
    csv_path = Path('backend/data/user_details_report.csv')
    csv_data = {}
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row['Email'].strip().lower()
                csv_data[email] = {
                    'workshops': [w.strip() for w in row['Workshops'].split(',') if w.strip()],
                    'events': [e.strip() for e in row['Events'].split(',') if e.strip()],
                    'year': row['Year'].strip() if row['Year'].strip() else None,
                    'gender': row['Gender'].strip() if row['Gender'].strip() else None,
                    'summer_internship': row['Summer Internship'].strip() if row['Summer Internship'].strip() else 'No'
                }
    except Exception as e:
        print(f"Warning: Could not load CSV data: {e}")
    return csv_data


def main():
    print("Loading existing registration data...")
    json_path = Path('backend/data/registration_data.json')

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Load CSV data
    csv_data = load_csv_data()

    # Parse BIS participants
    bis_participants = parse_bis_data()

    # Create email lookup
    email_to_entry = {entry['email'].lower(): entry for entry in data}

    # Get next ID for new entries
    next_id = max(entry['id'] for entry in data) + 1

    added_event_count = 0
    added_participant_count = 0
    not_found = []
    already_has = []

    print(f"\nProcessing {len(bis_participants)} BIS event participants...")

    for participant in bis_participants:
        email = participant['email']

        if email in email_to_entry:
            entry = email_to_entry[email]

            # Check if already has the BIS event
            if 'BIS' in str(entry.get('events', [])):
                already_has.append(participant['name'])
            else:
                # Add the BIS event
                if 'events' not in entry:
                    entry['events'] = []
                entry['events'].append('BIS')
                added_event_count += 1
                print(
                    f"  ✓ Added BIS event to: {participant['name']} ({email})")
        else:
            # Add new participant with BIS event
            new_record = {
                'id': next_id,
                'name': participant['name'],
                'email': email,
                'phone': participant['phone'] if participant['phone'] else None,
                'college': participant['college'],
                'year': None,
                'gender': None,
                'summer_internship': 'No',
                'workshops': [],
                'events': ['BIS'],
                'city': ''
            }

            # Check CSV for additional data
            if email in csv_data:
                csv_info = csv_data[email]
                new_record['workshops'] = csv_info['workshops']
                # Add existing events from CSV
                for event in csv_info['events']:
                    if event and event not in new_record['events']:
                        new_record['events'].append(event)
                new_record['year'] = csv_info['year']
                new_record['gender'] = csv_info['gender']
                new_record['summer_internship'] = csv_info['summer_internship']

            data.append(new_record)
            email_to_entry[email] = new_record
            next_id += 1
            added_participant_count += 1
            print(
                f"  + Added new participant: {participant['name']} ({email})")

    # Save updated data
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n{'='*70}")
    print(f"✓ Added 'BIS' event to {added_event_count} existing participants")
    print(f"✓ Added {added_participant_count} new participants with BIS event")
    print(f"✓ {len(already_has)} participants already had the BIS event")

    if already_has:
        print(f"\nParticipants who already had BIS event:")
        for name in already_has:
            print(f"  - {name}")

    print(f"\n✓ Total records: {len(data)}")
    print(f"✓ Saved to {json_path}")


if __name__ == '__main__':
    main()
