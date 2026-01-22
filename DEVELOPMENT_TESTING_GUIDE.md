# Development Testing Guide - LLM Government Consulting System
## For SMB & Mid-Cap Businesses - Budget-Friendly Alternative to Deloitte & Big 4

---

## 🎯 Project Vision
**Objective:** Create an affordable, autonomous audit and compliance reporting system for small-to-medium businesses (SMBs) and mid-cap companies who cannot afford expensive Deloitte, EY, or KPMG consulting services.

**Value Proposition:**
- **Cost:** 90% cheaper than traditional big audits
- **Speed:** Automated document processing and analysis
- **Accessibility:** Cloud-based, easy to use
- **Compliance:** FAR (Federal Acquisition Regulation) compliant
- **Intelligence:** AI-powered insights and recommendations

---

## 📋 Development Environment Checklist

### ✅ Prerequisites
- Python 3.8+
- PostgreSQL or SQLite
- Flask 2.3+
- SQLAlchemy ORM
- JWT authentication
- CORS enabled for frontend

### ✅ All Dependencies Installed
```bash
pip install -r requirements.txt
```

---

## 🔐 Authentication Features Verification

### 1. User Registration & Password Hashing
**Test Objective:** Verify passwords are securely hashed

```bash
CURL Command:
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "smb_user_001",
    "email": "owner@businessname.com",
    "password": "SecurePassword@123",
    "agency": "ABC Manufacturing Inc."
  }'
```

**Expected Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "smb_user_001",
    "email": "owner@businessname.com",
    "agency": "ABC Manufacturing Inc.",
    "role": "analyst",
    "active": true,
    "created_at": "2026-01-22T18:00:00"
  }
}
```

**Verification Points:**
- ✅ Password stored as hash (NOT plaintext)
- ✅ User created successfully
- ✅ Role defaults to 'analyst'
- ✅ Account active by default

### 2. User Login & JWT Token Generation
**Test Objective:** Verify JWT authentication works

```bash
CURL Command:
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "smb_user_001",
    "password": "SecurePassword@123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "smb_user_001",
    "email": "owner@businessname.com",
    "agency": "ABC Manufacturing Inc.",
    "role": "analyst",
    "active": true
  }
}
```

**Verification Points:**
- ✅ JWT token generated
- ✅ Token valid for 24 hours
- ✅ User data returned
- ✅ Last login timestamp updated

---

## 📁 Database Integration Testing

### 3. Database Connection Verification
**Test Objective:** Ensure database properly configured and connected

**SQLite (Development):**
```bash
ls -la llm_consulting.db  # Database file created
```

**Database Structure:**
- **users table:** Stores SMB user accounts
- **projects table:** Stores audit/compliance projects
- **analyses table:** Stores analysis results and reports
- **Relationships:** Proper foreign keys, cascading deletes

### 4. Project Creation (Requires JWT Token)
**Test Objective:** Verify project data persistence

```bash
CURL Command:
curl -X POST http://localhost:5000/api/projects \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "ABC-2024-001",
    "title": "Annual Government Compliance Audit",
    "description": "Full FAR compliance review for ABC Manufacturing",
    "agency": "ABC Manufacturing Inc.",
    "budget": 500000,
    "timeline_months": 6
  }'
```

**Expected Response (201 Created):**
```json
{
  "message": "Project created successfully",
  "project": {
    "id": 1,
    "project_id": "ABC-2024-001",
    "title": "Annual Government Compliance Audit",
    "agency": "ABC Manufacturing Inc.",
    "budget": 500000,
    "status": "draft",
    "created_at": "2026-01-22T18:00:00"
  }
}
```

**Database Verification:**
- ✅ Project stored in database
- ✅ User association maintained
- ✅ Status defaults to 'draft'
- ✅ Timestamps recorded

### 5. Document Upload Integration
**Test Objective:** Verify document storage mechanism

**Planned Features:**
- PDF upload and storage
- Document versioning
- Audit trail for all uploads
- Secure storage with encryption

**Future Implementation:**
```python
# Document storage endpoint
@app.route('/api/projects/<int:project_id>/documents', methods=['POST'])
@jwt_required()
def upload_document(project_id):
    # Validates file type (PDF, Excel, Word)
    # Stores with encryption
    # Creates audit log entry
    # Returns document metadata
    pass
```

---

## 🌐 Web Interface Testing (Frontend Integration)

### Frontend URL Endpoints
- **Login:** `http://localhost:3000/login`
- **Dashboard:** `http://localhost:3000/dashboard`
- **Projects:** `http://localhost:3000/projects`
- **New Project:** `http://localhost:3000/projects/new`
- **Reports:** `http://localhost:3000/reports`

### Required Frontend Components
1. **Login Form** → Calls `/api/auth/login` → Stores JWT
2. **Project List** → Calls `/api/projects` (GET)
3. **Create Project** → Calls `/api/projects` (POST)
4. **Document Upload** → Calls `/api/projects/{id}/documents` (POST)
5. **Analysis Viewer** → Calls `/api/analyze/policy/{project_id}` (POST)
6. **Report Generation** → Calls `/api/analyze/cost/{project_id}` (POST)

---

## 🧪 Continuous Integration Testing

### GitHub Actions Pipeline
**File:** `.github/workflows/deploy.yml`

**Test Stages:**
1. **Unit Tests** - Test individual functions
2. **Integration Tests** - Test database interactions
3. **Authentication Tests** - Verify JWT flows
4. **API Tests** - Validate all endpoints
5. **Build Tests** - Docker image creation

### Manual Testing Checklist

#### Authentication Tests
- [ ] Register new user
- [ ] Login with correct credentials
- [ ] Login fails with wrong password
- [ ] JWT token validates
- [ ] Token expires after 24 hours
- [ ] Logout clears session

#### Database Tests
- [ ] User data persists
- [ ] Projects created successfully
- [ ] Project relationships maintained
- [ ] Cascading deletes work
- [ ] Transactions rollback on error

#### API Tests
- [ ] Health endpoint returns 200
- [ ] Protected routes require JWT
- [ ] Invalid tokens rejected (401)
- [ ] Missing data returns 400
- [ ] Database errors return 500
- [ ] CORS headers present

#### Security Tests
- [ ] Passwords hashed (not plaintext)
- [ ] SQL injection prevented (SQLAlchemy)
- [ ] XSS protection via JSON
- [ ] CSRF tokens for state changes
- [ ] Rate limiting implemented

---

## 💼 Business Metrics Dashboard

### For SMB/Mid-Cap Business Owners

**Cost Savings Analysis:**
- Traditional Big 4 Audit: $50,000 - $200,000
- This System: $5,000 - $15,000/year
- **Savings: 75-90%**

**Time Savings:**
- Manual audit collection: 40-60 hours
- Automated system: 2-4 hours
- **Time saved: 95%**

**Key Metrics Tracked:**
- Compliance score (0-100)
- Risk areas identified
- Cost optimization opportunities
- Recommendations implemented
- Document processing time

---

## 📊 System Architecture Verification

### Current Stack
- **Backend:** Python Flask + SQLAlchemy
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Authentication:** JWT tokens
- **API:** RESTful endpoints
- **Deployment:** Docker + GitHub Actions

### Feature Status
- ✅ User authentication
- ✅ Project management
- ✅ Database integration
- ✅ API endpoints
- ✅ Error handling
- ✅ CORS support
- 🔄 Document upload (in development)
- 🔄 AI analysis (in development)
- 🔄 Report generation (in development)

---

## 🚀 Deployment Steps for Production

### Step 1: Set Environment Variables
```bash
export SECRET_KEY='your-production-secret'
export JWT_SECRET_KEY='your-jwt-secret'
export DATABASE_URL='postgresql://user:pass@host:5432/llm_db'
export CORS_ORIGINS='yourdomain.com,app.yourdomain.com'
export FLASK_ENV='production'
```

### Step 2: Build Docker Image
```bash
docker build -t llm-consulting:latest .
```

### Step 3: Run Docker Container
```bash
docker run -d \
  -e SECRET_KEY='your-secret' \
  -e DATABASE_URL='postgresql://...' \
  -p 5000:5000 \
  llm-consulting:latest
```

### Step 4: Verify Deployment
```bash
curl http://localhost:5000/api/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

---

## 📝 Documentation References

1. **MANUAL_TEST_GUIDE.md** - Detailed API test cases
2. **TESTING_AND_BUG_REPORT.md** - All bugs and fixes
3. **PROTOTYPE_NOTES.md** - Architecture details
4. **README.md** - Project overview

---

## 💡 Next Steps

1. **Frontend Development**
   - React/Vue.js UI
   - User dashboard
   - Document upload interface
   - Report viewing

2. **AI Integration**
   - Connect LLM models
   - Document analysis
   - Compliance recommendations
   - Risk assessment

3. **Business Features**
   - Subscription plans
   - Multi-user teams
   - Role-based access
   - Audit history

4. **Compliance**
   - SOC 2 certification
   - GDPR compliance
   - Data encryption
   - Backup & recovery

---

## 🎓 Developer Quick Reference

**Start Development Server:**
```bash
python -m src.app
```

**Database Reset:**
```bash
rm llm_consulting.db
python -c "from src.app import app, db; app.app_context().push(); db.create_all()"
```

**View All Routes:**
```bash
python -c "from src.app import app; [print(rule) for rule in app.url_map.iter_rules()]"
```

---

**Status:** ✅ Development Environment Ready for Testing
**Last Updated:** January 22, 2026
**Version:** 1.0.0
