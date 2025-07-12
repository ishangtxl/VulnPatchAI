# VulnPatch AI API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints (except login/register) require authentication using Bearer tokens.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Endpoints

### Authentication

#### POST /auth/login
Login with email and password.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "user"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### POST /auth/logout
Logout current user.

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### Scans

#### POST /scan/upload
Upload and process an Nmap XML scan file.

**Request:**
- Content-Type: multipart/form-data
- Body: file (XML file)

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "filename": "scan_results.xml",
  "original_filename": "scan_results.xml",
  "status": "processing",
  "upload_time": "2024-01-01T12:00:00Z",
  "file_size": 1024000
}
```

#### GET /scan/history
Get scan history for the current user.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records (default: 100)

**Response:**
```json
[
  {
    "id": 1,
    "filename": "scan_results.xml",
    "status": "completed",
    "upload_time": "2024-01-01T12:00:00Z",
    "file_size": 1024000
  }
]
```

#### GET /scan/{scan_id}
Get detailed information about a specific scan.

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "filename": "scan_results.xml",
  "status": "completed",
  "upload_time": "2024-01-01T12:00:00Z",
  "processed_at": "2024-01-01T12:05:00Z",
  "file_size": 1024000,
  "parsed_data": {
    "scan_info": {...},
    "hosts": [...],
    "services": [...],
    "total_hosts": 5,
    "total_services": 12
  }
}
```

#### DELETE /scan/{scan_id}
Delete a scan and all associated data.

**Response:**
```json
{
  "message": "Scan deleted successfully"
}
```

### Vulnerabilities

#### GET /vulnerabilities
Get vulnerabilities with optional filters.

**Query Parameters:**
- `scan_id` (int, optional): Filter by scan ID
- `severity` (string, optional): Filter by severity (Critical, High, Medium, Low)
- `status` (string, optional): Filter by status (open, patched, ignored, false_positive)
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum number of records

**Response:**
```json
[
  {
    "id": 1,
    "scan_id": 1,
    "service_name": "ssh",
    "service_version": "OpenSSH 7.4",
    "port": 22,
    "protocol": "tcp",
    "cve_id": "CVE-2023-1234",
    "cvss_score": 7.5,
    "severity": "High",
    "description": "SSH service vulnerability",
    "recommendation": "Update to latest version",
    "status": "open",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

#### GET /vulnerabilities/{vuln_id}
Get detailed information about a specific vulnerability.

**Response:**
```json
{
  "id": 1,
  "scan_id": 1,
  "service_name": "ssh",
  "service_version": "OpenSSH 7.4",
  "port": 22,
  "protocol": "tcp",
  "cve_id": "CVE-2023-1234",
  "cvss_score": 7.5,
  "severity": "High",
  "description": "SSH service vulnerability",
  "recommendation": "Update to latest version",
  "status": "open",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

#### PATCH /vulnerabilities/{vuln_id}/status
Update vulnerability status.

**Request Body:**
```json
{
  "status": "patched",
  "notes": "Applied security update"
}
```

**Response:**
```json
{
  "id": 1,
  "status": "patched",
  "updated_at": "2024-01-01T13:00:00Z"
}
```

#### POST /vulnerabilities/{vuln_id}/feedback
Add feedback for a vulnerability.

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Very helpful recommendation",
  "feedback_type": "recommendation"
}
```

**Response:**
```json
{
  "message": "Feedback added successfully",
  "feedback_id": 1
}
```

### Dashboard

#### GET /dashboard/metrics
Get dashboard metrics for the current user.

**Response:**
```json
{
  "total_scans": 10,
  "vulnerabilities": {
    "critical": 2,
    "high": 5,
    "medium": 8,
    "low": 3,
    "total": 18
  },
  "patch_completion_rate": 65.5,
  "recent_scans": 3,
  "avg_cvss_score": 6.2
}
```

#### GET /dashboard/trends
Get trend data for charts.

**Query Parameters:**
- `days` (int, optional): Number of days for trend data (default: 30)

**Response:**
```json
{
  "vulnerability_trends": [
    {"date": "2024-01-01", "value": 5},
    {"date": "2024-01-02", "value": 8}
  ],
  "scan_trends": [
    {"date": "2024-01-01", "value": 1},
    {"date": "2024-01-02", "value": 2}
  ],
  "severity_distribution": {
    "Critical": 2,
    "High": 5,
    "Medium": 8,
    "Low": 3
  }
}
```

### Reports

#### POST /reports/generate
Generate a new report.

**Request Body:**
```json
{
  "scan_id": 1,
  "report_type": "executive",
  "format": "html"
}
```

**Response:**
```json
{
  "id": 1,
  "scan_id": 1,
  "user_id": 1,
  "report_type": "executive",
  "title": "Executive Report - scan_results.xml",
  "format": "html",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

#### GET /reports
Get reports for the current user.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum number of records

**Response:**
```json
[
  {
    "id": 1,
    "scan_id": 1,
    "report_type": "executive",
    "title": "Executive Report - scan_results.xml",
    "format": "html",
    "generated_at": "2024-01-01T12:00:00Z"
  }
]
```

#### GET /reports/{report_id}
Get detailed information about a specific report.

**Response:**
```json
{
  "id": 1,
  "scan_id": 1,
  "user_id": 1,
  "report_type": "executive",
  "title": "Executive Report - scan_results.xml",
  "content": "<html>...</html>",
  "format": "html",
  "file_path": "/path/to/report.html",
  "generated_at": "2024-01-01T12:00:00Z"
}
```

#### GET /reports/{report_id}/download
Download report file.

**Response:**
- Content-Type: application/octet-stream
- File download

### AI Assistant

#### POST /ai/query
Ask the AI assistant a question.

**Request Body:**
```json
{
  "query": "What are my most critical vulnerabilities?",
  "context": {
    "scan_id": 1
  }
}
```

**Response:**
```json
{
  "query": "What are my most critical vulnerabilities?",
  "response": "Based on your latest scan, you have 2 critical vulnerabilities...",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST /ai/analyze
Get AI analysis for a scan.

**Request Body:**
```json
{
  "scan_id": 1
}
```

**Response:**
```json
{
  "scan_id": 1,
  "summary": "Your scan identified 18 vulnerabilities across 5 hosts...",
  "key_findings": [
    "2 critical vulnerabilities require immediate attention",
    "SSH service has the most vulnerabilities (5)"
  ],
  "recommendations": [
    "Immediately patch 2 critical vulnerabilities",
    "Schedule patching for 5 high-severity vulnerabilities"
  ],
  "risk_score": 7.2,
  "generated_at": "2024-01-01T12:00:00Z"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API endpoints are rate limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- File upload endpoints: 10 requests per minute
- Other endpoints: 100 requests per minute

## File Upload Limits

- Maximum file size: 10MB
- Supported formats: XML files only
- File types: Nmap XML scan results

## Security

- All communications use HTTPS in production
- Passwords are hashed using bcrypt
- JWT tokens expire after 30 minutes
- Input validation and sanitization on all endpoints
- SQL injection protection through parameterized queries