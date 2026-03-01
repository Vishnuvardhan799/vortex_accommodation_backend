# Google Sheets Setup Guide

This guide walks you through setting up Google Sheets integration for the Vortex 2026 Accommodation System.

## Overview

The system uses Google Sheets as the data store for accommodation entries. The backend connects to Google Sheets using a service account for authentication.

## Prerequisites

- Google account
- Access to Google Cloud Console
- Basic understanding of Google Cloud Platform

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter project details:
   - **Project name**: `vortex-2026-accommodation`
   - **Organization**: (optional)
5. Click "Create"
6. Wait for the project to be created (takes a few seconds)

## Step 2: Enable Google Sheets API

1. In the Google Cloud Console, ensure your project is selected
2. Go to "APIs & Services" > "Library"
3. Search for "Google Sheets API"
4. Click on "Google Sheets API"
5. Click "Enable"
6. Wait for the API to be enabled

## Step 3: Create a Service Account

A service account is a special type of account used by applications (not humans) to access Google APIs.

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - **Service account name**: `vortex-accommodation-service`
   - **Service account ID**: (auto-generated)
   - **Description**: `Service account for Vortex 2026 accommodation system`
4. Click "Create and Continue"
5. Grant access (optional, can skip):
   - **Role**: (leave empty for now)
   - Click "Continue"
6. Grant users access (optional, can skip):
   - Click "Done"

## Step 4: Create Service Account Key

1. In the "Credentials" page, find your service account in the list
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create new key"
5. Select "JSON" as the key type
6. Click "Create"
7. A JSON file will be downloaded to your computer
8. **IMPORTANT**: Keep this file secure! It contains credentials to access your Google Sheets

## Step 5: Configure Environment Variables

1. Open the downloaded JSON file
2. Copy the entire contents
3. In your backend `.env` file, set the `GOOGLE_CREDENTIALS_JSON` variable:

```bash
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project-id",...}
```

**Note**: The entire JSON should be on one line, or you can use a tool to minify it.

Alternatively, you can store the JSON file and reference its path:

```bash
GOOGLE_CREDENTIALS_PATH=/path/to/service-account-key.json
```

4. Set the sheet name:

```bash
SHEET_NAME=Vortex 2026 Accommodation
```

## Step 6: Create and Configure Google Sheet

### Option A: Use the Setup Script (Recommended)

Run the provided setup script:

```bash
cd backend
python scripts/setup_google_sheets.py
```

The script will:

- Create a new Google Sheet (or use existing one)
- Set up proper headers
- Apply formatting and data validation
- Add conditional formatting for duplicate detection
- Provide the sheet URL

### Option B: Manual Setup

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it: `Vortex 2026 Accommodation`
4. Set up the header row (Row 1) with these columns:

| A         | B    | C     | D       | E         | F       | G                  | H     | I          |
| --------- | ---- | ----- | ------- | --------- | ------- | ------------------ | ----- | ---------- |
| Timestamp | Name | Email | College | From Date | To Date | Accommodation Type | Notes | Entered By |

5. Format the header row:
   - Make it bold
   - Add a background color
   - Freeze the row (View > Freeze > 1 row)

6. Add data validation for "Accommodation Type" column (G):
   - Select cells G2:G1000
   - Data > Data validation
   - Criteria: List of items
   - Items: `Boys, Girls, Other`
   - Check "Reject input"
   - Save

## Step 7: Share Sheet with Service Account

**CRITICAL STEP**: You must share the Google Sheet with your service account email.

1. Open your Google Sheet
2. Click the "Share" button (top right)
3. In the "Add people and groups" field, enter your service account email
   - Find this in the JSON file: `client_email` field
   - Example: `vortex-accommodation-service@your-project.iam.gserviceaccount.com`
4. Set permission level: **Editor**
5. Uncheck "Notify people" (service accounts don't receive emails)
6. Click "Share"

**Without this step, the backend will not be able to access the sheet!**

## Step 8: Test the Connection

1. Start the backend application:

```bash
cd backend
uvicorn app.main:app --reload
```

2. Check the health endpoint:

```bash
curl http://localhost:8000/api/health
```

You should see:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-06T10:00:00Z",
  "services": {
    "googleSheets": "connected",
    "registrationData": "loaded"
  }
}
```

If `googleSheets` shows "connected", you're all set!

## Troubleshooting

### Error: "Spreadsheet not found"

**Cause**: The sheet hasn't been shared with the service account.

**Solution**: Follow Step 7 to share the sheet with your service account email.

### Error: "Invalid credentials"

**Cause**: The service account JSON is malformed or incorrect.

**Solution**:

- Verify the JSON is valid (use a JSON validator)
- Ensure the entire JSON is in the environment variable
- Try downloading a new key from Google Cloud Console

### Error: "Permission denied"

**Cause**: The service account doesn't have permission to access the sheet.

**Solution**:

- Ensure the sheet is shared with the service account email
- Verify the service account has "Editor" permission
- Check that the Google Sheets API is enabled in your project

### Error: "API not enabled"

**Cause**: Google Sheets API is not enabled for your project.

**Solution**: Follow Step 2 to enable the Google Sheets API.

## Security Best Practices

1. **Never commit credentials to version control**
   - Add `.env` to `.gitignore`
   - Never share the service account JSON file publicly

2. **Use environment variables**
   - Store credentials in environment variables or secret management systems
   - Don't hardcode credentials in your code

3. **Limit service account permissions**
   - Only grant the minimum required permissions
   - Use separate service accounts for different environments (dev, prod)

4. **Rotate keys regularly**
   - Create new service account keys periodically
   - Delete old keys after rotation

5. **Monitor access**
   - Check Google Cloud Console for unusual activity
   - Review sheet access logs regularly

## Production Deployment

For production deployments:

1. **Use secret management**:
   - Render: Use environment variables in dashboard
   - Railway: Use `railway variables set`
   - Vercel: Use environment variables in project settings
   - AWS: Use AWS Secrets Manager
   - Azure: Use Azure Key Vault

2. **Separate environments**:
   - Use different Google Sheets for dev/staging/production
   - Use different service accounts for each environment

3. **Backup your data**:
   - Regularly export the Google Sheet
   - Set up automated backups
   - Keep backups in a secure location

## Additional Resources

- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Service Account Documentation](https://cloud.google.com/iam/docs/service-accounts)
- [gspread Library Documentation](https://docs.gspread.org/)
- [Google Cloud Console](https://console.cloud.google.com/)

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the backend logs for detailed error messages
3. Verify all environment variables are set correctly
4. Ensure the Google Sheets API is enabled
5. Confirm the sheet is shared with the service account

## Sheet Structure Reference

The accommodation sheet has the following columns:

| Column             | Type     | Description                    | Required | Validation         |
| ------------------ | -------- | ------------------------------ | -------- | ------------------ |
| Timestamp          | DateTime | Auto-generated entry timestamp | Yes      | ISO 8601 format    |
| Name               | String   | Participant full name          | Yes      | 1-200 characters   |
| Email              | String   | Participant email              | Yes      | Valid email format |
| College            | String   | College/institution name       | Yes      | 1-200 characters   |
| From Date          | Date     | Accommodation start date       | Yes      | 2026-03-06/07/08   |
| To Date            | Date     | Accommodation end date         | Yes      | 2026-03-06/07/08   |
| Accommodation Type | Enum     | Type of accommodation          | Yes      | Boys/Girls/Other   |
| Notes              | String   | Additional information         | No       | Max 500 characters |
| Entered By         | String   | Volunteer email                | Yes      | Valid email format |

## Example Sheet

Here's what a properly configured sheet looks like:

| Timestamp            | Name       | Email            | College    | From Date  | To Date    | Accommodation Type | Notes        | Entered By           |
| -------------------- | ---------- | ---------------- | ---------- | ---------- | ---------- | ------------------ | ------------ | -------------------- |
| 2026-03-06T10:30:00Z | John Doe   | john@example.com | NIT Trichy | 2026-03-06 | 2026-03-08 | Boys               | Late arrival | volunteer@vortex.com |
| 2026-03-06T11:15:00Z | Jane Smith | jane@example.com | IIT Madras | 2026-03-07 | 2026-03-08 | Girls              | -            | volunteer@vortex.com |
