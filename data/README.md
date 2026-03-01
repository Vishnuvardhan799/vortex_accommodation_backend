# Registration Data

This directory contains the registration data for Vortex 2026 participants.

## Files

### sample_registration_data.json

Sample registration data with 54 participants for testing and development purposes.

**Structure:**

```json
[
  {
    "name": "Participant Name",
    "email": "email@college.edu",
    "college": "College Name",
    "events": ["Event 1", "Event 2"],
    "workshops": ["Workshop 1", "Workshop 2"]
  }
]
```

**Fields:**

- `name` (string, required): Full name of the participant
- `email` (string, required): Email address (must be unique)
- `college` (string, required): College or institution name
- `events` (array of strings): List of events the participant registered for
- `workshops` (array of strings): List of workshops the participant registered for

## Usage

### Development

Set the `REGISTRATION_DATA_PATH` environment variable to point to this file:

```bash
REGISTRATION_DATA_PATH=data/sample_registration_data.json
```

### Production

Replace `sample_registration_data.json` with your actual registration data exported from your registration system.

**Export Format:**

Ensure your registration data follows the same JSON structure as the sample file. You can export from:

- Google Forms (via Google Sheets → Export as JSON)
- Typeform (via API or export)
- Custom registration system (via database export)

**Data Preparation Steps:**

1. Export registration data from your system
2. Convert to JSON format matching the structure above
3. Validate the JSON format (use a JSON validator)
4. Ensure all email addresses are unique
5. Remove any test or duplicate entries
6. Save as `registration_data.json` in this directory
7. Update `REGISTRATION_DATA_PATH` to point to the new file

## Data Privacy

**Important:** Registration data contains personal information (names, emails, colleges).

- Never commit actual participant data to version control
- Use sample data for development and testing only
- Ensure production data is stored securely
- Follow data protection regulations (GDPR, etc.)
- Delete data after the event as per your data retention policy

## Sample Data Statistics

The sample data includes:

- **Total Participants:** 54
- **Colleges Represented:** 50+ institutions across India
- **Events:** 7 different events
- **Workshops:** 10 different workshops
- **Email Domains:** Various educational institutions (.edu, .ac.in)

## Events in Sample Data

1. Tech Talk: AI in 2026
2. Hackathon
3. Robotics Competition
4. Coding Competition
5. Project Expo
6. Tech Quiz
7. Gaming Tournament

## Workshops in Sample Data

1. Machine Learning Basics
2. Web Development with React
3. Cloud Computing with AWS
4. Cybersecurity Fundamentals
5. Data Science with Python
6. Mobile App Development
7. IoT and Smart Devices
8. Blockchain Technology
9. UI/UX Design
10. Digital Marketing

## Updating Registration Data

If you need to add or update participants during the event:

1. Edit the JSON file directly
2. Restart the backend application to reload the data
3. Or implement a hot-reload mechanism if needed

**Note:** The backend loads registration data into memory at startup for fast lookups. Changes to the file require an application restart.
