# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 1. Application Won't Start

#### Problem: `ModuleNotFoundError: No module named 'flask_migrate'`

**Cause**: Missing Flask-Migrate dependency

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from flask_migrate import Migrate; print('✓ OK')"

# Restart the application
python wsgi.py
```

---

### 2. Database Connection Errors

#### Problem: `psycopg2.OperationalError: could not connect to server`

**Cause**: Database not running or incorrect connection URL

**Solution**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL if stopped
sudo systemctl start postgresql

# Verify DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
psql "$DATABASE_URL" -c "SELECT 1"
```

---

### 3. Port Already in Use

#### Problem: `OSError: [Errno 48] Address already in use`

**Cause**: Port 5000 is already occupied

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or use different port
FLASK_ENV=development python wsgi.py --port 5001
```

---

### 4. Deployment Issues on Render

#### Problem: 502 Bad Gateway Error

**Cause**: Application crashed during startup

**Solution**:
1. Check Render logs: https://dashboard.render.com/web/srv-d5qsq7koud1c73ecti20/logs
2. Verify all dependencies are in `requirements.txt`
3. Check environment variables in Render settings
4. Redeploy with `Manual Deploy` → `Deploy latest commit`

---

### 5. Environment Variables Not Loading

#### Problem: `KeyError: 'OPENAI_API_KEY'`

**Cause**: .env file not loaded or variables not set

**Solution**:
```python
# Ensure python-dotenv is installed
pip install python-dotenv

# Load .env in app initialization
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

---

### 6. API Rate Limiting

#### Problem: `429 Too Many Requests`

**Cause**: Exceeded API rate limits

**Solution**:
```python
# Implement exponential backoff
import time
from functools import wraps

def retry_with_backoff(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except RateLimitError:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        raise
    return wrapper
```

---

### 7. CORS Issues

#### Problem: `No 'Access-Control-Allow-Origin' header`

**Cause**: CORS not configured properly

**Solution**:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE"]
    }
})
```

---

### 8. Memory Leaks

#### Problem: Memory usage increases continuously

**Cause**: Unclosed database connections or circular references

**Solution**:
```bash
# Monitor memory usage
memory_profiler monitor_app.py

# Check for memory leaks
python -m memory_profiler -m pytest
```

---

### 9. Timeout Errors

#### Problem: `TimeoutError: Request timed out after 30s`

**Cause**: Slow queries or external service delays

**Solution**:
```python
# Increase timeout
import requests

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=10,
    max_retries=requests.packages.urllib3.util.retry.Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.get(url, timeout=60)
```

---

### 10. Health Check Failures

#### Problem: `/api/health` returns 503

**Cause**: Service dependencies are unavailable

**Solution**:
```bash
# Check all dependencies
curl -s https://llm-pexperiment.onrender.com/api/health | jq .

# Check individual services
# Database
psql "$DATABASE_URL" -c "SELECT 1"

# OpenAI API
python -c "import openai; print(openai.__version__)"

# Redis (if used)
redis-cli ping
```

---

## Performance Issues

### Slow API Response

**Check query performance**:
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    logger.info(f"Start Query: {statement}")

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    logger.info(f"Query Complete!Total Time: {total_time}s")
```

---

## Testing Endpoints

### Test API locally
```bash
# Home endpoint
curl http://localhost:5000/

# Health check
curl http://localhost:5000/api/health | jq .

# Full-flight endpoint
curl http://localhost:5000/api/full-flight | jq .
```

### Test live deployment
```bash
# Home endpoint
curl https://llm-pexperiment.onrender.com/

# Health check
curl https://llm-pexperiment.onrender.com/api/health | jq .

# Full-flight endpoint
curl https://llm-pexperiment.onrender.com/api/full-flight | jq .
```

---

## Getting Help

1. **Check logs**:
   - Local: `tail -f app.log`
   - Render: https://dashboard.render.com/web/srv-d5qsq7koud1c73ecti20/logs

2. **Review documentation**:
   - [ERROR_HANDLING.md](ERROR_HANDLING.md) - Crash prevention
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [README.md](README.md) - Project overview

3. **Report issues**:
   - 🐛 [GitHub Issues](https://github.com/ayushjhaa1187-spec/LLM_PEXPERIMENT/issues)
   - 💬 [GitHub Discussions](https://github.com/ayushjhaa1187-spec/LLM_PEXPERIMENT/discussions)
   - 📧 [Email Support](mailto:ayushjhaa1187@gmail.com)

---

**Last Updated**: January 25, 2026  
**Maintained By**: Ayush Kumar Jha
