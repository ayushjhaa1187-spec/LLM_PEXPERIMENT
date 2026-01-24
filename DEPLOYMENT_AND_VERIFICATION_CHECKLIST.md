# DEPLOYMENT AND VERIFICATION CHECKLIST
## LLM Government Consulting Prototype - Production Readiness Guide

**Date**: January 24, 2026  
**Status**: Ready for Deployment Phase  
**Target**: All systems operational by Feb 15, 2026  

---

## PRE-DEPLOYMENT VERIFICATION (DO FIRST)

### 1. Code Quality Checks
```bash
# Static Analysis
pylint src/
flake8 src/
pytest --cov=src src/tests/

# Expected Results:
# ✅ No critical linting errors
# ✅ Code coverage > 85%
# ✅ All tests passing
```

### 2. Security Scan
```bash
# Dependency Security
safety check
bandit -r src/

# Expected Results:
# ✅ No known vulnerabilities
# ✅ No hardcoded secrets
# ✅ All dependencies up-to-date
```

### 3. Configuration Validation
```bash
# Environment Setup
[] Copy .env.example to .env
[] Set DATABASE_URL (PostgreSQL)
[] Set LLM_API_KEY (OpenAI/Anthropic)
[] Set JWT_SECRET_KEY
[] Set CORS_ORIGINS
[] Set REDIS_URL (for caching)

# Verification
python -c "from src.app import app; print('Flask app initialized OK')"
python -c "from src.llm_engine import MultiAgentRAGSystem; print('RAG system initialized OK')"
```

### 4. Database Migration
```bash
# Create Database Schema
flask db upgrade
alembic upgrade head

# Verify Tables
python -c "from src.app import db; db.create_all(); print(db.engine.table_names())"

# Expected Tables:
# ✅ users
# ✅ projects
# ✅ analyses
# ✅ documents
# ✅ audit_logs
```

### 5. LLM Integration Test
```python
# Test LLM Connection
from src.llm_engine import MultiAgentRAGSystem

system = MultiAgentRAGSystem()
result = system.execute_pipeline({
    'project_id': 'TEST_001',
    'agency': 'DoD',
    'budget': 2500000,
    'description': 'Test project'
})

assert result['pipeline_status'] == 'completed'
assert 'agent_outputs' in result
print(f"✅ LLM pipeline test PASSED")
```

---

## LOCAL DEPLOYMENT TEST

### Step 1: Start Backend
```bash
cd /path/to/LLM_PEXPERIMENT
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

python src/main.py
# Expected: "Running on http://0.0.0.0:5000"
```

### Step 2: Verify API Endpoints
```bash
# Health Check
curl http://localhost:5000/api/health
# Expected: {"status": "healthy", "timestamp": "..."}

# User Registration
curl -X POST http://localhost:5000/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "SecurePassword@123",
    "agency": "DoD"
  }'
# Expected: {"message": "User registered successfully", "user": {...}}

# User Login
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "test_user", "password": "SecurePassword@123"}'
# Expected: {"access_token": "eyJ0eXAi...", "user": {...}}
```

### Step 3: Test Core Workflows
```bash
# Set JWT token from login response
TOKEN="eyJ0eXAi..."

# Create Project
curl -X POST http://localhost:5000/api/projects \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_id": "PROJ_001",
    "title": "FAR Compliance Analysis",
    "agency": "DoD",
    "budget": 2500000,
    "timeline_months": 12
  }'

# Run Policy Analysis
curl -X POST http://localhost:5000/api/analyze/policy/1 \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json"

# Run Cost Analysis
curl -X POST http://localhost:5000/api/analyze/cost/1 \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json"
```

### Step 4: Verify Output Accuracy
```python
# Check Results Match Expected Ranges
assert result['total_base_cost'] > 0
assert result['total_potential_savings'] > 0
assert 0 <= result['average_confidence'] <= 1.0
assert result['savings_percentage'] > 30  # Should be 60-80%
assert result['estimated_payback_months'] < 6  # Should be 1-6 months

print("✅ All cost calculations within expected ranges")
```

---

## DOCKER DEPLOYMENT

### Build & Run Containerized App
```bash
# Build Docker Image
docker build -t llm-gov-consulting:latest .

# Run Container
docker run -d \\
  -p 5000:5000 \\
  -e DATABASE_URL="postgresql://user:pass@host:5432/llm_db" \\
  -e LLM_API_KEY="sk-..." \\
  -e JWT_SECRET_KEY="your-secret" \\
  -e CORS_ORIGINS="localhost:3000,your-domain.com" \\
  --name llm-app \\
  llm-gov-consulting:latest

# Check Logs
docker logs -f llm-app

# Test from Host
curl http://localhost:5000/api/health
```

### Docker Compose (Full Stack)
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/llm_db
      REDIS_URL: redis://cache:6379/0
    depends_on:
      - postgres
      - cache
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: securepass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  cache:
    image: redis:7-alpine

volumes:
  postgres_data:
```

```bash
docker-compose up -d
docker-compose logs -f backend
```

---

## INTEGRATION WITH PROVIDED DEVELOPMENT GUIDE

### Critical Solutions from PDF
Your attached Development Guide provides:

1. **Multi-Agent Pipeline (LangGraph)**
   - Replace complex orchestration with LangGraph
   - ~5 days saved in development
   - Integrated in `src/llm_engine/`

2. **Document Processing (Unstructured.io)**
   - Handles PDF/DOCX/images with OCR
   - 95% success vs current 60%
   - Implementation: `src/document_processor.py`

3. **Vector Search Improvements**
   - Smart chunking with metadata
   - RecursiveCharacterTextSplitter with overlap
   - Section-aware splitting for regulations

4. **Citation Verification**
   - Structured output schema with citations
   - Hallucination detection
   - Confidence scoring (LOW/MEDIUM/HIGH)

5. **Performance Optimization**
   - Semantic caching: 30s → 3s
   - Parallel vector search
   - Embedding cache

6. **Error Recovery**
   - Fallback mechanisms for each agent
   - Graceful degradation
   - Retry with exponential backoff

---

## DEPLOYMENT VERIFICATION MATRIX

| Component | Local Test | Docker Test | Production | Status |
|-----------|-----------|------------|------------|--------|
| Backend API | curl tests | docker exec | AWS/Cloud | Pending |
| Database | SQLite works | PostgreSQL | PostgreSQL | Pending |
| LLM Integration | OpenAI test | API key set | Production API | Pending |
| Document Processing | PDF upload | Container | Full stack | Pending |
| Authentication | JWT login | Token auth | OAuth2 ready | Pending |
| Error Handling | Try-catch | Fallback logic | Monitoring | Pending |
| Performance | <100ms API | <200ms container | <500ms cloud | Pending |
| Security | No secrets hardcoded | Env variables | Vault integration | Pending |

---

## GO/NO-GO DECISION CHECKLIST

### Must Pass (Blocking)
```
[] All 18 bugs fixed and tested
[] Unit test coverage > 90%
[] No critical security vulnerabilities
[] Cost calculations within ±5% accuracy
[] API response time < 5 seconds
[] All auth flows working (register, login, JWT)
[] Error handling for all edge cases
[] Database migrations successful
[] LLM API integration confirmed
[] Docker image builds successfully
```

### Should Pass (Non-Blocking)
```
[] Performance profiling shows no bottlenecks
[] Load testing: 10 concurrent users OK
[] CI/CD pipeline passing
[] Documentation complete
[] Example queries working correctly
[] Cost comparison calculator accurate
[] Audit logging functioning
[] Error recovery tested
```

### Nice-to-Have (Optional)
```
[] Frontend dashboard deployed
[] Analytics tracking working
[] Daily compliance check scheduled
[] Document versioning implemented
[] Multi-document comparison feature
[] Advanced access control rules
```

---

## PRODUCTION MONITORING SETUP

### Logging
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=5)
handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

### Metrics to Track
```
[] API response times (p50, p95, p99)
[] Error rate (target <1%)
[] Cost calculation accuracy
[] Citation verification success rate
[] Database query times
[] LLM API latency
[] Cache hit rate (target >80%)
[] User engagement
```

### Alerting Thresholds
```
CRITICAL:
- API down (0 responses)
- Cost calc error >10%
- Citation hallucination >5%

WARNING:
- API latency >5s
- Error rate >2%
- Database slow query
- LLM API timeout
```

---

## ROLLBACK PROCEDURES

### Code Rollback
```bash
git log --oneline | head
git revert [commit-hash]
git push
```

### Database Rollback
```bash
alembic downgrade -1  # Go back 1 version
alembic downgrade base  # Go back to start
```

### Docker Rollback
```bash
docker images | grep llm-gov
docker run -d ... llm-gov-consulting:previous-tag
```

---

## FINAL READINESS SIGN-OFF

**Pre-Deployment Checklist Owner**: [Name]  
**Date**: [Date]  
**Sign-Off**: _______________

✅ All code quality checks passed  
✅ Security scan complete  
✅ Database migrations verified  
✅ API endpoints tested  
✅ LLM integration confirmed  
✅ Docker image built  
✅ Monitoring configured  
✅ Rollback procedures documented  

**Status**: READY FOR DEPLOYMENT
