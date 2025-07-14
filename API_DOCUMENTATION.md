# Secure File Sharing System - API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication Endpoints

### 1.1 Client User Signup
**POST** `/auth/signup`

**Description:** Register a new client user with email verification

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "client@example.com",
  "username": "clientuser",
  "password": "password123",
  "user_type": "client"
}
```

**Response (200):**
```json
{
  "message": "User created successfully. Please check your email for verification.",
  "user_id": 1
}
```

**Response (400):**
```json
{
  "detail": "Only client users can sign up through this endpoint"
}
```

---

### 1.2 User Login
**POST** `/auth/login`

**Description:** Authenticate user and get JWT token

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (401):**
```json
{
  "detail": "Incorrect email or password"
}
```

---

### 1.3 Email Verification
**GET** `/auth/verify-email`

**Description:** Verify user email address

**Query Parameters:**
- `email`: User's email address
- `token`: Verification token (sent via email)

**URL Example:**
```
GET /auth/verify-email?email=client@example.com&token=abc123def456
```

**Response (200):**
```json
{
  "message": "Email verified successfully"
}
```

**Response (400):**
```json
{
  "detail": "Invalid verification token"
}
```

---

### 1.4 Create Ops User (Development)
**POST** `/auth/create-ops-user`

**Description:** Create an Ops user (for development/testing)

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "ops@example.com",
  "username": "opsuser",
  "password": "password123",
  "user_type": "ops"
}
```

**Response (200):**
```json
{
  "message": "Ops user created successfully",
  "user_id": 2
}
```

---

## 2. File Management Endpoints

### 2.1 Upload File (Ops Users Only)
**POST** `/files/upload`

**Description:** Upload a file (only .pptx, .docx, .xlsx allowed)

**Headers:**
```
Authorization: Bearer <ops_user_token>
Content-Type: multipart/form-data
```

**Body:**
```
Form Data:
- file: [Select file] (pptx, docx, or xlsx)
```

**Response (200):**
```json
{
  "message": "File uploaded successfully. File ID: 1"
}
```

**Response (400):**
```json
{
  "detail": "Only .pptx, .docx, .xlsx files are allowed"
}
```

**Response (401):**
```json
{
  "detail": "Access denied. Ops user required."
}
```

---

### 2.2 List Files (Client Users Only)
**GET** `/files/list`

**Description:** Get list of all uploaded files

**Headers:**
```
Authorization: Bearer <client_user_token>
```

**Response (200):**
```json
{
  "files": [
    {
      "id": 1,
      "filename": "abc123.docx",
      "original_filename": "document.docx",
      "file_size": 1024,
      "file_type": ".docx",
      "uploader_id": 2,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

**Response (401):**
```json
{
  "detail": "Access denied. Client user required."
}
```

---

### 2.3 Get Download Link (Client Users Only)
**GET** `/files/download/{file_id}`

**Description:** Get secure download link for a specific file

**Headers:**
```
Authorization: Bearer <client_user_token>
```

**Path Parameters:**
- `file_id`: Integer ID of the file

**Response (200):**
```json
{
  "download_link": "http://localhost:8000/files/download-file/abc123def456ghi789",
  "message": "success"
}
```

**Response (404):**
```json
{
  "detail": "File not found"
}
```

---

### 2.4 Download File (Using Secure Token)
**GET** `/files/download-file/{token}`

**Description:** Download file using secure token (no authentication required)

**Path Parameters:**
- `token`: Secure download token

**Response (200):**
```
Binary file content with headers:
Content-Disposition: attachment; filename=document.docx
Content-Type: application/octet-stream
```

**Response (400):**
```json
{
  "detail": "Invalid or expired download token"
}
```

---

## 3. Error Responses

### Common Error Codes

**400 Bad Request:**
```json
{
  "detail": "Error description"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Invalid authorization header"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## 4. Postman Collection Setup

### Environment Variables
Create a Postman environment with these variables:

```
base_url: http://localhost:8000
ops_token: (will be set after login)
client_token: (will be set after login)
file_id: (will be set after upload)
download_token: (will be set after getting download link)
```

### Collection Structure
```
Secure File Sharing System
├── Authentication
│   ├── Create Ops User
│   ├── Client Signup
│   ├── Login (Ops)
│   ├── Login (Client)
│   └── Verify Email
├── File Management
│   ├── Upload File
│   ├── List Files
│   ├── Get Download Link
│   └── Download File
└── Tests
    ├── Test Unauthorized Access
    └── Test Invalid File Types
```

### Test Scripts

**For Login endpoints (set token automatically):**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.access_token) {
        pm.environment.set("ops_token", response.access_token);
        // or pm.environment.set("client_token", response.access_token);
    }
}
```

**For Upload File (set file_id automatically):**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.text();
    const match = response.match(/File ID: (\d+)/);
    if (match) {
        pm.environment.set("file_id", match[1]);
    }
}
```

**For Get Download Link (set download_token automatically):**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.download_link) {
        const token = response.download_link.split('/').pop();
        pm.environment.set("download_token", token);
    }
}
```

---

## 5. Workflow Examples

### Complete Client Workflow
1. **Client Signup** → Get user_id
2. **Verify Email** → Use token from console/email
3. **Client Login** → Get client_token
4. **List Files** → View available files
5. **Get Download Link** → Get secure download URL
6. **Download File** → Download using secure token

### Complete Ops Workflow
1. **Create Ops User** → Get user_id
2. **Ops Login** → Get ops_token
3. **Upload File** → Upload .pptx/.docx/.xlsx file
4. **List Files** → Verify upload (if you have client access)

### Testing Security
1. Try accessing Ops endpoints with Client token
2. Try accessing Client endpoints with Ops token
3. Try accessing protected endpoints without token
4. Try uploading invalid file types
5. Try using expired download tokens

---

## 6. File Requirements

### Allowed File Types
- `.pptx` (PowerPoint)
- `.docx` (Word)
- `.xlsx` (Excel)

### File Size Limit
- Maximum: 10MB (10,485,760 bytes)

### File Storage
- Files are stored in the `uploads/` directory
- Original filenames are preserved in database
- Unique filenames are generated for storage

---

## 7. Security Features

### JWT Tokens
- Tokens expire after 30 minutes (configurable)
- Tokens contain user email and user type
- Tokens are required for all protected endpoints

### Download Security
- Each download generates a unique, time-limited token
- Tokens expire after 1 hour
- Tokens can only be used once
- Only Client users can generate download links

### Role-Based Access
- **Ops Users**: Can upload files only
- **Client Users**: Can list and download files only
- **Unauthenticated**: Can only download using valid tokens

### Email Verification
- Client users must verify email before login
- Ops users are automatically verified
- Verification tokens expire after 24 hours 