"""
DevOps Info Service
Main application module
"""

import os
import json
import socket
import platform
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SERVICE_NAME = "devops-info-service"
SERVICE_VERSION = "1.0.0"
SERVICE_DESCRIPTION = "DevOps course info service"
FRAMEWORK = "Flask"


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


@app.before_request
def log_request():
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
        ],
    }

    return jsonify(response)


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": get_uptime()["seconds"],
        }
    )


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

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)