# 🛡️ Error Handling & Crash Prevention Guide

## Overview

This guide provides comprehensive strategies to prevent crashes, handle errors gracefully, and maintain system stability in the LLM_PEXPERIMENT application.

---

## 1. Flask-Migrate Setup (Critical)

### Problem
Missing `flask_migrate` module causes startup failures with:
```
ModuleNotFoundError: No module named 'flask_migrate'
```

### Solution
Ensure `Flask-Migrate==4.0.5` is in `requirements.txt`:

```bash
# requirements.txt
Flask-Migrate==4.0.5
alembic==1.12.0
```

### Verification
```bash
pip install -r requirements.txt
python -c "from flask_migrate import Migrate; print('✓ Flask-Migrate loaded')"
```

---

## 2. Environment Variables Configuration

### Essential Variables

```env
# .env file
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secure-random-key
DATABASE_URL=postgresql://user:password@localhost/llm_experiment
OPENAI_API_KEY=sk-...
LOG_LEVEL=INFO
MAX_WORKERS=4
```

### Validation
- ✅ Never commit `.env` file (add to `.gitignore`)
- ✅ Use strong SECRET_KEY (minimum 32 characters)
- ✅ Validate all URLs and API keys before deployment

---

## 3. Error Logging Strategy

### Python Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler with rotation
file_handler = RotatingFileHandler(
    'app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General informational messages
- `WARNING`: Warning messages for recoverable issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical failures requiring immediate attention

---

## 4. Try-Except Error Handling

### Flask Route Protection

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/endpoint')
def protected_endpoint():
    try:
        # Your code here
        result = perform_operation()
        return jsonify({'status': 'success', 'data': result}), 200
    
    except ValueError as e:
        logger.warning(f'Invalid input: {str(e)}')
        return jsonify({'error': 'Invalid input'}), 400
    
    except DatabaseError as e:
        logger.error(f'Database error: {str(e)}')
        return jsonify({'error': 'Database unavailable'}), 500
    
    except Exception as e:
        logger.critical(f'Unexpected error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
```

---

## 5. Input Validation

### Validate All Inputs

```python
from marshmallow import Schema, fields, ValidationError

class RequestSchema(Schema):
    query = fields.Str(required=True, validate=lambda x: len(x) > 0)
    limit = fields.Int(required=False, validate=lambda x: 0 < x <= 100)

def validate_request(data):
    schema = RequestSchema()
    try:
        result = schema.load(data)
        return result, None
    except ValidationError as err:
        return None, err.messages
```

---

## 6. Database Connection Handling

### Connection Pooling

```python
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True   # Verify connection before use
)

@event.listens_for(engine, 'connect')
def receive_connect(dbapi_conn, connection_record):
    """Enable foreign keys for SQLite"""
    cursor = dbapi_conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
```

### Transaction Management

```python
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

def safe_database_operation(operation_func):
    session = Session()
    try:
        result = operation_func(session)
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        logger.error(f'Database operation failed: {str(e)}')
        raise
    finally:
        session.close()
```

---

## 7. Health Check Endpoints

### Implement Health Monitoring

```python
@app.route('/api/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check external services
        check_openai_api()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }), 200
    
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

---

## 8. Rate Limiting

### Prevent Overload

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=['200 per day', '50 per hour']
)

@app.route('/api/endpoint')
@limiter.limit('10 per minute')
def rate_limited_endpoint():
    # Your endpoint logic
    pass
```

---

## 9. Common Crashes & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| Missing Dependencies | ImportError | `pip install -r requirements.txt` |
| Database Connection | psycopg2.OperationalError | Check DATABASE_URL, verify PostgreSQL is running |
| API Rate Limit | 429 Too Many Requests | Implement exponential backoff, reduce request frequency |
| Memory Leak | Memory usage increases over time | Profile with memory_profiler, check for circular references |
| Timeout | Request hangs indefinitely | Set connection timeouts, optimize queries |
| CORS Issues | 403 Forbidden from browser | Configure CORS headers properly |

---

## 10. Deployment Checklist

- ✅ All dependencies in `requirements.txt`
- ✅ Environment variables configured
- ✅ Database migrations applied
- ✅ Logging configured
- ✅ Health check endpoint working
- ✅ Rate limiting enabled
- ✅ Error handlers registered
- ✅ HTTPS enabled
- ✅ Security headers configured
- ✅ Monitoring alerts set up

---

## 11. Debugging Tips

### Local Development
```bash
# Enable Flask debug mode
FLASK_ENV=development FLASK_DEBUG=True python wsgi.py

# View detailed error pages
# Available at http://localhost:5000 with stack traces
```

### Production Debugging
```bash
# Check logs
tail -f app.log

# Monitor performance
watch -n 1 'ps aux | grep python'

# Use Render dashboard
# https://dashboard.render.com/web/srv-d5qsq7koud1c73ecti20/logs
```

---

## 12. Support Resources

- 📖 [Flask Documentation](https://flask.palletsprojects.com/)
- 📖 [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- 📖 [OpenAI API Documentation](https://platform.openai.com/docs)
- 💬 [GitHub Issues](https://github.com/ayushjhaa1187-spec/LLM_PEXPERIMENT/issues)
- 🆘 [Email Support](mailto:ayushjhaa1187@gmail.com)

---

**Last Updated**: January 25, 2026  
**Maintained By**: Ayush Kumar Jha
