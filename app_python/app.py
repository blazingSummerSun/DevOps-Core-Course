"""
DevOps Info Service
Main application module
"""

import json
import logging
import os
import platform
import socket
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response, g
import threading
from pathlib import Path

import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST


from prometheus_client import Counter, Histogram, Gauge

app = Flask(__name__)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
VISITS_FILE = Path(os.getenv("VISITS_FILE", "/data/visits"))
_visits_lock = threading.Lock()

SERVICE_NAME = "devops-info-service"
SERVICE_VERSION = "1.0.0"
SERVICE_DESCRIPTION = "DevOps course info service"
FRAMEWORK = "Flask"

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
)

def normalize_endpoint():
    if request.url_rule and hasattr(request.url_rule, "rule"):
        return request.url_rule.rule
    return request.path


# JSON Structured Logging
class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Add extra-fields if they provided
        for field in ("method", "path", "status_code", "client_ip",
                      "user_agent", "service"):
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        return json.dumps(log_entry)


# Configure root logger with JSON-format
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logging.root.handlers = []
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

logger.info(
    "Application starting",
    extra={
        "service": SERVICE_NAME,
        "method": "STARTUP",
        "path": "/",
    },
)

# Application start time
start_time = datetime.now()


def get_uptime():
    delta = datetime.now() - start_time
    seconds = int(delta.total_seconds())
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return {"seconds": seconds, "human": f"{hours} hours, {minutes} minutes"}

def _read_visits() -> int:
    try:
        return int(VISITS_FILE.read_text().strip() or "0")
    except FileNotFoundError:
        return 0
    except Exception:
        return 0


def _write_visits(value: int) -> None:
    VISITS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = VISITS_FILE.with_suffix(".tmp")
    tmp.write_text(str(value))
    tmp.replace(VISITS_FILE)


@app.before_request
def log_request():
    http_requests_in_progress.inc()
    request._start_time = time.perf_counter()

    logger.info(
        f"Incoming request: {request.method} {request.path}",
        extra={
            "method": request.method,
            "path": request.path,
            "client_ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", ""),
        },
    )


@app.after_request
def log_response(response):
    # metrics: decrement in-progress
    http_requests_in_progress.dec()

    endpoint = normalize_endpoint()
    method = request.method
    status = str(response.status_code)

    # counter
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

    # histogram
    start = getattr(request, "_start_time", None)
    if start is not None:
        duration = time.perf_counter() - start
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    logger.info(
        f"Response: {request.method} {request.path} -> {response.status_code}",
        extra={
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "client_ip": request.remote_addr,
        },
    )
    return response


# Routes


@app.route("/", methods=["GET"])
def index():
    """Main endpoint - service and system information."""
    devops_info_endpoint_calls.labels(endpoint="/").inc()

    with _visits_lock:
        visits = _read_visits() + 1
        _write_visits(visits)

    t0 = time.perf_counter()
    uptime = get_uptime()

    response = {
        "service": {
            "name": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "description": SERVICE_DESCRIPTION,
            "framework": FRAMEWORK,
        },
        "system": {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_count": os.cpu_count(),
            "python_version": platform.python_version(),
        },
        "runtime": {
            "uptime_seconds": uptime["seconds"],
            "uptime_human": uptime["human"],
            "current_time": datetime.now(timezone.utc).isoformat(),
            "timezone": "UTC",
        },
        "request": {
            "client_ip": request.remote_addr,
            "user_agent": request.headers.get("User-Agent"),
            "method": request.method,
            "path": request.path,
        },
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Service information"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/visits", "method": "GET", "description": "Visits counter"},
        ],
        "visits": {
            "count": visits
        }
    }


    devops_info_system_collection_seconds.observe(time.perf_counter() - t0)
    return jsonify(response)


@app.route("/health", methods=["GET"])
def health():
    devops_info_endpoint_calls.labels(endpoint="/health").inc()
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": get_uptime()["seconds"],
        }
    )

@app.route("/visits", methods=["GET"])
def visits():
    with _visits_lock:
        value = _read_visits()
    return jsonify({"visits": value})


@app.errorhandler(404)
def not_found(error):
    logger.warning(
        "Endpoint not found",
        extra={
            "method": request.method,
            "path": request.path,
            "status_code": 404,
            "client_ip": request.remote_addr,
        },
    )
    return jsonify({"error": "Not Found", "message": "Endpoint does not exist"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(
        "Internal server error",
        extra={
            "method": request.method,
            "path": request.path,
            "status_code": 500,
            "client_ip": request.remote_addr,
        },
    )
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


@app.get("/error")
def error():
    raise Exception("Test error for logging")

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(data, mimetype=CONTENT_TYPE_LATEST)

devops_info_endpoint_calls = Counter(
    "devops_info_endpoint_calls",
    "DevOps Info Service endpoint calls",
    ["endpoint"],
)

devops_info_system_collection_seconds = Histogram(
    "devops_info_system_collection_seconds",
    "Time spent collecting system info for response",
)

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
