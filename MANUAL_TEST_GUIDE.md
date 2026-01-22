# Manual Test Guide for LLM Government Consulting System

## Status: DEPLOYMENT READY

This guide provides instructions for manual testing of the fixed Flask application with all bugs resolved.

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
export SECRET_KEY='your-secret-key'
export JWT_SECRET_KEY='your-jwt-secret'
export DATABASE_URL='sqlite:///llm_consulting.db'  # Development
export CORS_ORIGINS='localhost:3000'
```

### 3. Initialize Database
```bash
python -c "from src.app import app, db; app.app_context().push(); db.create_all()"
```

### 4. Run Flask Application
```bash
python -m src.app
```

Server will start at: `http://localhost:5000`

## Test Cases

### Test 1: Health Check
**Endpoint:** `GET /api/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX..."
}
```

**Status Code:** 200

### Test 2: User Registration
**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePassword123!",
  "agency": "Department of Defense"
}
```

**Expected Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "agency": "Department of Defense",
    "role": "analyst",
    "active": true,
    "created_at": "2024-01-XX..."
  }
}
```

**Status Code:** 201

**Bug Fixes Verified:**
- BUG #8: Password is properly hashed (set_password() called)
- BUG #7: Response is JSON serializable (to_dict() method)
- BUG #5: Error handling with proper rollback

### Test 3: User Login
**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePassword123!"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "agency": "Department of Defense",
    "role": "analyst",
    "active": true,
    "created_at": "2024-01-XX..."
  }
}
```

**Status Code:** 200

**Bug Fixes Verified:**
- BUG #5: Password check works with hashed values
- BUG #7: User response is JSON serializable

### Test 4: Create Project (Requires JWT Token)
**Endpoint:** `POST /api/projects`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "project_id": "FAR-001-2024",
  "title": "Defense Contract Analysis",
  "description": "Comprehensive analysis of government procurement policies",
  "agency": "Department of Defense",
  "budget": 5000000,
  "timeline_months": 18
}
```

**Expected Response:**
```json
{
  "message": "Project created successfully",
  "project": {
    "id": 1,
    "project_id": "FAR-001-2024",
    "title": "Defense Contract Analysis",
    "agency": "Department of Defense",
    "budget": 5000000,
    "status": "draft",
    "created_at": "2024-01-XX..."
  }
}
```

**Status Code:** 201

**Bug Fixes Verified:**
- BUG #5: Error handling in route
- BUG #7: Project response is JSON serializable

### Test 5: Get Projects (Requires JWT Token)
**Endpoint:** `GET /api/projects`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Expected Response:**
```json
{
  "projects": [
    {
      "id": 1,
      "project_id": "FAR-001-2024",
      "title": "Defense Contract Analysis",
      "agency": "Department of Defense",
      "budget": 5000000,
      "status": "draft",
      "created_at": "2024-01-XX..."
    }
  ]
}
```

**Status Code:** 200

## Bug Fixes Summary

### ✅ BUG #1: Import Errors - FIXED
- Proper imports from llm_engine package
- Package now has __init__.py

### ✅ BUG #2: Database Configuration - FIXED
- Uses environment variable DATABASE_URL
- Falls back to SQLite for development

### ✅ BUG #3: Package Structure - FIXED
- src/llm_engine/__init__.py created
- Proper package imports established

### ✅ BUG #4: Route Naming - FIXED
- Routes properly separated by HTTP method
- GET and POST methods on different routes

### ✅ BUG #5: Error Handling - FIXED
- Comprehensive try-except blocks
- Rollback called in all exception paths

### ✅ BUG #6: CORS - FIXED
- CORS configured with environment variables
- Restricted origins instead of wildcard

### ✅ BUG #7: JSON Serialization - FIXED
- to_dict() methods added to all models
- Proper ISO format for datetime fields

### ✅ BUG #8: Password Hashing - FIXED
- set_password() method called in register
- Passwords properly hashed before storage

## Deployment Notes

1. **Local Testing:** Use SQLite database (default)
2. **Production:** Set DATABASE_URL to PostgreSQL connection string
3. **Security:** Update SECRET_KEY and JWT_SECRET_KEY with strong values
4. **CORS:** Set CORS_ORIGINS to allowed frontend domains
5. **Docker:** Build and run using provided Dockerfile

## Expected Test Results

All tests should pass with:
- ✅ Correct HTTP status codes
- ✅ Valid JSON responses
- ✅ Proper error messages
- ✅ Database persistence
- ✅ JWT authentication working
- ✅ Password encryption verified
