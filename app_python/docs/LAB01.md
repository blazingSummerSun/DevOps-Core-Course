# LAB01 — DevOps Info Service

## 1. Framework Selection

### Selected Framework: **Flask**

### Justification

* Flask is lightweight and minimal, making it easy to understand and maintain.
* The framework provides full control over application behavior without hidden abstractions.
* Routing as in Ktor-framework which I have experience with

The goal of this lab is to demonstrate DevOps principles rather than complex backend logic, therefore Flask is an optimal choice.

### Framework Comparison

| Framework | Pros                               | Cons                              | 
| --------- | ---------------------------------- | --------------------------------- | 
| Flask     | Simple, lightweight, easy to learn | Limited built-in features         | 
| FastAPI   | Async, auto-generated docs, modern | Higher complexity, async overhead | 
| Django    | Full-featured, ORM, admin panel    | Heavyweight, steep learning curve |

---

## 2. Best Practices Applied

### 2.1 Clean Code Organization

**Practices:**

* Clear and descriptive function names
* Grouped imports according to PEP 8
* Minimal and meaningful comments
* Constants defined at module level

**Example:**

```python
"""
DevOps Info Service
Main application module
"""

import os
import socket
import platform
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request
```

```python
def get_uptime():
    delta = datetime.now() - start_time
    ...

def log_request():
    logger.info(f"Request: {request.method} {request.path}")

@app.route("/", methods=["GET"])
def index():
    """Main endpoint - service and system information."""
    ...
    
@app.route("/health", methods=["GET"])
def health():
    ...
```

**Importance:**
Clean code improves readability, maintainability, and reduces onboarding time for new developers.

---

### 2.2 Error Handling

Custom error handlers were implemented for common HTTP errors.

**Example:**

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'Endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500
```

**Importance:**
Graceful error handling provides consistent API responses and improves client-side debugging.

---

### 2.3 Logging

Application logging is implemented using Python’s built-in `logging` module. Each incoming request is logged.

**Example:**

```python
# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info('Application starting...')

@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}")
```

**Importance:**
Logging is essential for monitoring, debugging, and observability in production environments.

---

### 2.4 Environment-Based Configuration

The application behavior can be configured using environment variables.

**Example:**

```python
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
```

**Importance:**
Environment-based configuration is a core DevOps principle and allows seamless deployment across environments.

---

## 3. API Documentation

### GET /

Returns service, system, runtime, and request information.

**Request:**

```bash
curl http://localhost:5000/
```

**Response (excerpt):**

```json
{
  "endpoints": [
    {
      "description": "Service information",
      "method": "GET",
      "path": "/"
    },
    {
      "description": "Health check",
      "method": "GET",
      "path": "/health"
    }
  ],
  "request": {
    "client_ip": "127.0.0.1",
    "method": "GET",
    "path": "/",
    "user_agent": "curl/7.81.0"
  },
  "runtime": {
    "current_time": "2026-01-28T15:40:35.714395+00:00",
    "timezone": "UTC",
    "uptime_human": "0 hours, 0 minutes",
    "uptime_seconds": 4
  },
  "service": {
    "description": "DevOps course info service",
    "framework": "Flask",
    "name": "devops-info-service",
    "version": "1.0.0"
  },
  "system": {
    "architecture": "x86_64",
    "cpu_count": 4,
    "hostname": "californiawrld",
    "platform": "Linux",
    "platform_version": "#91~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Nov 20 15:20:45 UTC 2",
    "python_version": "3.10.12"
  }
}
```

---

### GET /health

Health check endpoint used for monitoring.

**Request:**

```bash
curl http://localhost:5000/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-01-28T15:43:11.421546+00:00",
  "uptime_seconds": 160
}
```

---

## Testing Commands

Run the application:

```bash
python3 app.py
```

Test endpoints:

```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

Run with custom configuration:

```bash
PORT=8080 python app.py
```

---

## 4. Testing Evidence

The following screenshots are provided in `docs/screenshots/`:

* **01-main-endpoint.png** — main endpoint JSON response
* **02-health-check.png** — health check response
* **03-formatted-output.png** — pretty-printed JSON output

---

## 5. Challenges & Solutions

### Challenge 1: Request Context Errors

**Problem:** Attempted to access request data in each endpoint directly.

**Solution:** Moved request logging into a `before_request` handler provided by Flask.

## 6. GitHub Community
### Discovery & Bookmarking:
1. Star count indicates project popularity and community trust. Starred repos appear in your GitHub profile, showing your interests
2. Learn from others' code and commits. See how experienced developers solve problems