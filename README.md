# Vortex 2026 Accommodation System - Backend

FastAPI backend service for the Vortex 2026 Accommodation & Registration Check System.

A lightweight, high-performance API for managing participant registration and accommodation data during Vortex 2026 (March 6-8, NIT Trichy).

## Features

- Fast participant search by email (sub-second response)
- Real-time accommodation management via Google Sheets
- Event and workshop registration tracking
- Valediction token tracking with roll number search
  - Search counters (existing, non-existing, duplicate) auto-tracked in Google Sheet
  - Row highlighting in green when token is marked as given
- Duplicate detection with confirmation workflow
- Rate limiting (100 requests/minute per IP)
- API key authentication
- Comprehensive error handling
- CORS support for frontend integration
- Health check endpoint for monitoring

## Tech Stack

- FastAPI (Python 3.11+) with async/await
- Uvicorn ASGI server
- Pydantic v2 for validation
- Google Sheets API (gspread, google-auth)
- slowapi for rate limiting
- pytest + hypothesis for testing

## Prerequisites

- Python 3.11 or higher
- Google Cloud service account with Sheets API access
- Virtual environment (recommended)

## Installation

1. **Create and activate virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment variables:**

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Required environment variables:

- `GOOGLE_CREDENTIALS_JSON`: Google service account credentials (JSON string)
- `SHEET_NAME`: Name of the Google Sheet for accommodation data
- `API_SECRET_KEY`: Secret key for API authentication
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins
- `REGISTRATION_DATA_PATH`: Path to registration data JSON file

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # Application entry point, middleware
│   ├── config.py               # Environment variable validation
│   ├── exceptions.py           # Custom exception classes
│   ├── middleware.py           # Authentication middleware
│   ├── utils.py                # Shared utilities
│   ├── api/
│   │   └── routes.py           # API endpoint definitions
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   ├── services/               # Business logic layer
│   │   ├── search_service.py
│   │   ├── accommodation_service.py
│   │   ├── event_service.py
│   │   ├── workshop_service.py
│   │   ├── valediction_service.py
│   │   └── validation_service.py
│   └── repositories/           # Data access layer
│       ├── registration_repository.py
│       └── sheets_repository.py
├── tests/
│   ├── unit/                   # Unit tests
│   ├── property/               # Property-based tests (hypothesis)
│   └── integration/            # Integration tests
├── data/                       # Registration data (JSON)
├── docs/                       # API and deployment documentation
├── scripts/                    # Setup utilities
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## API Endpoints

| Method | Endpoint                      | Description                       | Auth Required |
| ------ | ----------------------------- | --------------------------------- | ------------- |
| GET    | `/api/health`                 | Health check                      | No            |
| POST   | `/api/search`                 | Search participant by email       | Yes           |
| POST   | `/api/accommodation`          | Add accommodation entry           | Yes           |
| POST   | `/api/events/register`        | Register for events               | Yes           |
| POST   | `/api/workshops/register`     | Register for workshops            | Yes           |
| POST   | `/api/valediction/search`     | Search valediction by roll number | Yes           |
| POST   | `/api/valediction/mark-token` | Mark valediction token as given   | Yes           |

All authenticated endpoints require a Bearer token in the Authorization header.

## Testing

The project uses a dual testing approach:

- Unit tests for specific examples and edge cases
- Property-based tests for universal properties across random inputs

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit              # Unit tests only
pytest tests/property          # Property-based tests only
pytest tests/integration       # Integration tests only

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_search_service.py
```

## Development

### Code Quality Tools

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type check
mypy app/
```

## Google Sheets Setup

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create a service account
4. Download the service account credentials JSON
5. Share your Google Sheet with the service account email
6. Set the credentials in the `GOOGLE_CREDENTIALS_JSON` environment variable

## Environment Variables Reference

| Variable                  | Description                            | Required | Default     |
| ------------------------- | -------------------------------------- | -------- | ----------- |
| `GOOGLE_CREDENTIALS_JSON` | Google service account credentials     | Yes      | -           |
| `API_SECRET_KEY`          | Secret key for API authentication      | Yes      | -           |
| `ALLOWED_ORIGINS`         | CORS allowed origins (comma-separated) | Yes      | -           |
| `REGISTRATION_DATA_PATH`  | Path to registration data JSON         | Yes      | -           |
| `ACCOMMODATION_SHEET_ID`  | Google Sheet ID for accommodation      | Yes      | -           |
| `EVENTS_SHEET_ID`         | Google Sheet ID for events             | Yes      | -           |
| `WORKSHOPS_SHEET_ID`      | Google Sheet ID for workshops          | Yes      | -           |
| `VALEDICTION_SHEET_ID`    | Google Sheet ID for valediction        | Yes      | -           |
| `ENVIRONMENT`             | Environment (development/production)   | No       | development |
| `LOG_LEVEL`               | Logging level                          | No       | INFO        |

## Performance Targets

- Search response: <1 second
- Accommodation creation: <2 seconds
- Concurrent users: 50+
- Participant records: 10,000+

## Troubleshooting

### Common Issues

1. **Google Sheets API errors**
   - Verify service account has access to the sheet
   - Check that `GOOGLE_CREDENTIALS_JSON` is valid JSON
   - Ensure Sheets API is enabled in Google Cloud Console

2. **CORS errors**
   - Add your frontend URL to `ALLOWED_ORIGINS`
   - Ensure URLs don't have trailing slashes

3. **Rate limiting**
   - Default: 100 requests/minute per IP
   - Adjust in `app/main.py` if needed

4. **Import errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

## Additional Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Google Sheets Setup Guide](docs/GOOGLE_SHEETS_SETUP.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)

## License

Internal use only - Vortex 2026 Event

## Deployment

### Docker Deployment

Build the Docker image:

```bash
docker build -t vortex-2026-backend .
```

Run the container:

```bash
docker run -p 8000:8000 \
  -e GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}' \
  -e SHEET_NAME="Vortex 2026 Accommodation" \
  -e API_SECRET_KEY="your-secret-key" \
  -e ALLOWED_ORIGINS="https://your-frontend.vercel.app" \
  -e REGISTRATION_DATA_PATH="data/registration_data.json" \
  -v $(pwd)/data:/app/data \
  vortex-2026-backend
```

### Render Deployment

1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically detect `render.yaml`
4. Set the following environment variables in Render dashboard:
   - `GOOGLE_CREDENTIALS_JSON` - Your service account credentials
   - `SHEET_NAME` - Your Google Sheet name
   - `ALLOWED_ORIGINS` - Your frontend URL
5. Deploy!

Render will automatically:

- Install dependencies
- Start the application with 4 workers
- Set up health checks
- Enable auto-deploy on git push

### Railway Deployment

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize project: `railway init`
4. Set environment variables:

```bash
railway variables set GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}'
railway variables set SHEET_NAME="Vortex 2026 Accommodation"
railway variables set API_SECRET_KEY="your-secret-key"
railway variables set ALLOWED_ORIGINS="https://your-frontend.vercel.app"
railway variables set REGISTRATION_DATA_PATH="data/registration_data.json"
railway variables set ENVIRONMENT="production"
```

5. Deploy: `railway up`

Railway will automatically:

- Detect Python and install dependencies
- Use the configuration from `railway.json`
- Set up health checks
- Provide a public URL

### Environment Variables for Production

Ensure these are set in your deployment platform:

- `GOOGLE_CREDENTIALS_JSON` - Full service account JSON (keep secure!)
- `SHEET_NAME` - Name of your Google Sheet
- `API_SECRET_KEY` - Strong random key (use a password generator)
- `ALLOWED_ORIGINS` - Your frontend URL(s), comma-separated
- `REGISTRATION_DATA_PATH` - Path to registration data file
- `ENVIRONMENT` - Set to "production"
- `LOG_LEVEL` - Set to "INFO" or "WARNING" for production

### Post-Deployment Checklist

- [ ] Verify health check endpoint: `https://your-api.com/api/health`
- [ ] Test search endpoint with a sample email
- [ ] Verify Google Sheets integration is working
- [ ] Check logs for any errors
- [ ] Test CORS with your frontend domain
- [ ] Verify rate limiting is working
- [ ] Monitor response times and errors
