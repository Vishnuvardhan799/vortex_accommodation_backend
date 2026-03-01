# API Documentation

Comprehensive API documentation for the Vortex 2026 Accommodation & Registration Check System.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-api-domain.com`

## Authentication

All API endpoints (except `/` and `/api/health`) require authentication using a Bearer token.

### Authentication Header

```
Authorization: Bearer <your-api-secret-key>
```

The API secret key must match the `API_SECRET_KEY` configured in the backend environment variables.

### Example Request

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"email": "participant@example.com"}'
```

## Rate Limiting

Rate limits are applied per IP address:

- **Search endpoint**: 30 requests per minute
- **Accommodation endpoint**: 20 requests per minute
- **Health check**: No limit

When rate limit is exceeded, the API returns:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

**HTTP Status**: `429 Too Many Requests`

## Endpoints

### 1. Root Endpoint

Get API information.

**Endpoint**: `GET /`

**Authentication**: Not required

**Response**:

```json
{
  "message": "Vortex 2026 Accommodation System API",
  "version": "1.0.0",
  "status": "running"
}
```

**Status Code**: `200 OK`

---

### 2. Health Check

Check the health status of the API and its dependencies.

**Endpoint**: `GET /api/health`

**Authentication**: Not required

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-06T10:30:00Z",
  "services": {
    "googleSheets": "connected",
    "registrationData": "loaded"
  }
}
```

**Status Codes**:

- `200 OK` - All services healthy
- `503 Service Unavailable` - One or more services unavailable

**Service Status Values**:

- `connected` - Service is operational
- `disconnected` - Service is not available
- `loaded` - Data is loaded successfully
- `error` - Service encountered an error

---

### 3. Search Participant

Search for a participant by email address.

**Endpoint**: `POST /api/search`

**Authentication**: Required

**Rate Limit**: 30 requests/minute

**Request Body**:

```json
{
  "email": "participant@example.com"
}
```

**Request Schema**:

| Field | Type   | Required | Description         |
| ----- | ------ | -------- | ------------------- |
| email | string | Yes      | Valid email address |

**Success Response** (Participant Found):

```json
{
  "found": true,
  "participant": {
    "name": "John Doe",
    "email": "participant@example.com",
    "college": "NIT Trichy",
    "events": ["Tech Talk: AI in 2026", "Hackathon"],
    "workshops": ["Machine Learning Basics", "Web Development with React"],
    "accommodation": {
      "hasAccommodation": true,
      "fromDate": "2026-03-06",
      "toDate": "2026-03-08",
      "type": "Boys"
    }
  }
}
```

**Success Response** (Participant Not Found):

```json
{
  "found": false,
  "message": "No participant found with this email"
}
```

**Response Schema**:

| Field                                      | Type        | Description                       |
| ------------------------------------------ | ----------- | --------------------------------- |
| found                                      | boolean     | Whether participant was found     |
| participant                                | object      | Participant details (if found)    |
| participant.name                           | string      | Full name                         |
| participant.email                          | string      | Email address                     |
| participant.college                        | string      | College/institution name          |
| participant.events                         | array       | List of registered events         |
| participant.workshops                      | array       | List of registered workshops      |
| participant.accommodation                  | object/null | Accommodation details (if exists) |
| participant.accommodation.hasAccommodation | boolean     | Accommodation status              |
| participant.accommodation.fromDate         | string      | Start date (YYYY-MM-DD)           |
| participant.accommodation.toDate           | string      | End date (YYYY-MM-DD)             |
| participant.accommodation.type             | string      | Boys/Girls/Other                  |
| message                                    | string      | Message (if not found)            |

**Status Codes**:

- `200 OK` - Request successful (participant found or not found)
- `400 Bad Request` - Invalid email format
- `401 Unauthorized` - Missing or invalid authentication token
- `429 Too Many Requests` - Rate limit exceeded
- `503 Service Unavailable` - Google Sheets API error

**Error Response Examples**:

Invalid email format:

```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    {
      "field": "email",
      "message": "value is not a valid email address"
    }
  ]
}
```

---

### 4. Add Accommodation Entry

Create a new accommodation entry.

**Endpoint**: `POST /api/accommodation`

**Authentication**: Required

**Rate Limit**: 20 requests/minute

**Request Body**:

```json
{
  "name": "John Doe",
  "email": "participant@example.com",
  "college": "NIT Trichy",
  "fromDate": "2026-03-06",
  "toDate": "2026-03-08",
  "accommodationType": "Boys",
  "notes": "Late arrival",
  "force": false
}
```

**Request Schema**:

| Field             | Type    | Required | Description              | Validation                    |
| ----------------- | ------- | -------- | ------------------------ | ----------------------------- |
| name              | string  | Yes      | Participant full name    | 1-200 characters              |
| email             | string  | Yes      | Participant email        | Valid email format            |
| college           | string  | Yes      | College/institution      | 1-200 characters              |
| fromDate          | string  | Yes      | Start date               | 2026-03-06/07/08              |
| toDate            | string  | Yes      | End date                 | 2026-03-06/07/08, >= fromDate |
| accommodationType | string  | Yes      | Accommodation type       | Boys/Girls/Other              |
| notes             | string  | No       | Additional notes         | Max 500 characters            |
| force             | boolean | No       | Override duplicate check | Default: false                |

**Success Response**:

```json
{
  "success": true,
  "message": "Accommodation entry created successfully",
  "entry": {
    "timestamp": "2026-03-06T10:30:00Z",
    "name": "John Doe",
    "email": "participant@example.com",
    "college": "NIT Trichy",
    "fromDate": "2026-03-06",
    "toDate": "2026-03-08",
    "accommodationType": "Boys",
    "notes": "Late arrival",
    "enteredBy": "volunteer@example.com"
  }
}
```

**Duplicate Warning Response**:

```json
{
  "success": false,
  "duplicate": true,
  "message": "An accommodation entry already exists for this email",
  "existingEntry": {
    "name": "John Doe",
    "email": "participant@example.com",
    "fromDate": "2026-03-06",
    "toDate": "2026-03-07",
    "accommodationType": "Boys"
  }
}
```

**Status Codes**:

- `201 Created` - Entry created successfully
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing or invalid authentication token
- `409 Conflict` - Duplicate entry (when force=false)
- `429 Too Many Requests` - Rate limit exceeded
- `503 Service Unavailable` - Google Sheets API error

**Error Response Examples**:

Validation errors:

```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    {
      "field": "fromDate",
      "message": "Invalid date format"
    },
    {
      "field": "toDate",
      "message": "toDate must be >= fromDate"
    }
  ]
}
```

Date range error:

```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    {
      "field": "toDate",
      "message": "toDate must be greater than or equal to fromDate"
    }
  ]
}
```

---

## Error Handling

### Error Response Format

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error type",
  "message": "Human-readable error message",
  "details": [
    {
      "field": "field_name",
      "message": "Field-specific error message"
    }
  ]
}
```

### HTTP Status Codes

| Code | Description           | When Used                                    |
| ---- | --------------------- | -------------------------------------------- |
| 200  | OK                    | Successful request                           |
| 201  | Created               | Resource created successfully                |
| 400  | Bad Request           | Invalid input data                           |
| 401  | Unauthorized          | Missing or invalid authentication            |
| 409  | Conflict              | Duplicate entry detected                     |
| 429  | Too Many Requests     | Rate limit exceeded                          |
| 500  | Internal Server Error | Unexpected server error                      |
| 503  | Service Unavailable   | External service (Google Sheets) unavailable |

### Common Error Types

#### 1. Validation Errors (400)

Returned when request data fails validation.

```json
{
  "success": false,
  "error": "Validation failed",
  "details": [
    {
      "field": "email",
      "message": "value is not a valid email address"
    }
  ]
}
```

#### 2. Authentication Errors (401)

Returned when authentication token is missing or invalid.

```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Invalid authentication token"
}
```

#### 3. Duplicate Entry Errors (409)

Returned when attempting to create a duplicate accommodation entry.

```json
{
  "success": false,
  "duplicate": true,
  "message": "An accommodation entry already exists for this email",
  "existingEntry": { ... }
}
```

#### 4. Rate Limit Errors (429)

Returned when rate limit is exceeded.

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

#### 5. Service Unavailable Errors (503)

Returned when Google Sheets API is unavailable.

```json
{
  "success": false,
  "error": "Service temporarily unavailable",
  "message": "Unable to access accommodation data. Please try again in a moment."
}
```

---

## Data Models

### ParticipantData

```typescript
{
  name: string;              // Full name
  email: string;             // Email address
  college: string;           // College/institution
  events: string[];          // List of registered events
  workshops: string[];       // List of registered workshops
  accommodation: {           // Accommodation details (nullable)
    hasAccommodation: boolean;
    fromDate: string;        // YYYY-MM-DD
    toDate: string;          // YYYY-MM-DD
    type: string;            // Boys/Girls/Other
  } | null;
}
```

### AccommodationEntry

```typescript
{
  timestamp: string;         // ISO 8601 datetime
  name: string;              // Full name (1-200 chars)
  email: string;             // Valid email
  college: string;           // College name (1-200 chars)
  fromDate: string;          // YYYY-MM-DD (2026-03-06/07/08)
  toDate: string;            // YYYY-MM-DD (2026-03-06/07/08)
  accommodationType: string; // Boys/Girls/Other
  notes?: string;            // Optional (max 500 chars)
  enteredBy: string;         // Volunteer email
}
```

---

## Usage Examples

### Example 1: Search for a Participant

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "aarav.sharma@nitt.edu"
  }'
```

**Response**:

```json
{
  "found": true,
  "participant": {
    "name": "Aarav Sharma",
    "email": "aarav.sharma@nitt.edu",
    "college": "NIT Trichy",
    "events": ["Tech Talk: AI in 2026", "Hackathon", "Robotics Competition"],
    "workshops": ["Machine Learning Basics", "Web Development with React"],
    "accommodation": {
      "hasAccommodation": true,
      "fromDate": "2026-03-06",
      "toDate": "2026-03-08",
      "type": "Boys"
    }
  }
}
```

### Example 2: Add Accommodation Entry

```bash
curl -X POST http://localhost:8000/api/accommodation \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Patel",
    "email": "priya.patel@iitm.ac.in",
    "college": "IIT Madras",
    "fromDate": "2026-03-07",
    "toDate": "2026-03-08",
    "accommodationType": "Girls",
    "notes": "Arriving on March 7 morning"
  }'
```

**Response**:

```json
{
  "success": true,
  "message": "Accommodation entry created successfully",
  "entry": {
    "timestamp": "2026-03-06T14:30:00Z",
    "name": "Priya Patel",
    "email": "priya.patel@iitm.ac.in",
    "college": "IIT Madras",
    "fromDate": "2026-03-07",
    "toDate": "2026-03-08",
    "accommodationType": "Girls",
    "notes": "Arriving on March 7 morning",
    "enteredBy": "volunteer@vortex.com"
  }
}
```

### Example 3: Handle Duplicate Entry

First attempt (without force):

```bash
curl -X POST http://localhost:8000/api/accommodation \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Patel",
    "email": "priya.patel@iitm.ac.in",
    "college": "IIT Madras",
    "fromDate": "2026-03-06",
    "toDate": "2026-03-08",
    "accommodationType": "Girls"
  }'
```

**Response** (409 Conflict):

```json
{
  "success": false,
  "duplicate": true,
  "message": "An accommodation entry already exists for this email",
  "existingEntry": {
    "name": "Priya Patel",
    "fromDate": "2026-03-07",
    "toDate": "2026-03-08",
    "accommodationType": "Girls"
  }
}
```

Second attempt (with force=true):

```bash
curl -X POST http://localhost:8000/api/accommodation \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Priya Patel",
    "email": "priya.patel@iitm.ac.in",
    "college": "IIT Madras",
    "fromDate": "2026-03-06",
    "toDate": "2026-03-08",
    "accommodationType": "Girls",
    "force": true
  }'
```

**Response** (201 Created):

```json
{
  "success": true,
  "message": "Accommodation entry created successfully",
  "entry": { ... }
}
```

### Example 4: Check API Health

```bash
curl http://localhost:8000/api/health
```

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-06T10:30:00Z",
  "services": {
    "googleSheets": "connected",
    "registrationData": "loaded"
  }
}
```

---

## Interactive API Documentation

The API provides interactive documentation through Swagger UI and ReDoc:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API explorer
  - Try out endpoints directly
  - View request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - Clean, readable documentation
  - Detailed schema information
  - Code examples

---

## Client Libraries

### JavaScript/TypeScript (Axios)

```typescript
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
  headers: {
    Authorization: `Bearer ${API_SECRET_KEY}`,
    "Content-Type": "application/json",
  },
});

// Search participant
const searchParticipant = async (email: string) => {
  const response = await api.post("/api/search", { email });
  return response.data;
};

// Add accommodation
const addAccommodation = async (data: AccommodationData) => {
  const response = await api.post("/api/accommodation", data);
  return response.data;
};
```

### Python (requests)

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-secret-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Search participant
def search_participant(email):
    response = requests.post(
        f"{API_URL}/api/search",
        json={"email": email},
        headers=headers
    )
    return response.json()

# Add accommodation
def add_accommodation(data):
    response = requests.post(
        f"{API_URL}/api/accommodation",
        json=data,
        headers=headers
    )
    return response.json()
```

---

## Best Practices

1. **Always include authentication header** for protected endpoints
2. **Handle rate limits gracefully** - implement exponential backoff
3. **Validate input on client side** before sending to API
4. **Handle all error cases** - don't assume success
5. **Use HTTPS in production** - never send credentials over HTTP
6. **Cache responses when appropriate** - reduce API calls
7. **Implement timeout handling** - don't wait indefinitely
8. **Log errors for debugging** - but don't log sensitive data

---

## Support

For API issues or questions:

1. Check this documentation
2. Review the interactive docs at `/docs`
3. Check the backend logs for detailed error messages
4. Contact the technical team

---

## Changelog

### Version 1.0.0 (2026-03-01)

- Initial API release
- Search participant endpoint
- Add accommodation endpoint
- Health check endpoint
- Authentication and rate limiting
- Comprehensive error handling
