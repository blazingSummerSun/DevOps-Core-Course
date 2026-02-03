# DevOps Info Service

## Overview

DevOps Info Service is a lightweight HTTP service that exposes runtime, system, and application information. The service is suitable for containerization, health monitoring, and deployment in orchestration platforms such as Kubernetes.

The application provides:

* Service metadata (name, version, framework)
* System information (OS, architecture, CPU count, Python version)
* Runtime information (uptime, current time)
* Health check endpoint for monitoring

---

## Prerequisites

* Python **3.10+** (recommended: 3.12 or newer)
* pip (Python package manager)
* Virtual environment support (`venv`)

To check the Python version:

```bash
python3 --version
```

---

## Installation

Clone the repository and navigate to the project directory:

```bash
cd app_python
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Run with default configuration:

```bash
python3 app.py
```

Run with custom configuration:

```bash
PORT=8080 python3 app.py
HOST=127.0.0.1 PORT=3000 python3 app.py
```

By default, the service will be available at:

```
http://localhost:5000
```

---

## API Endpoints

### GET /

Returns service, system, runtime, and request information.

Example:

```bash
curl http://localhost:5000/
```

### GET /health

Health check endpoint for monitoring and readiness probes.

Example:

```bash
curl http://localhost:5000/health
```

---

## Configuration

The application can be configured using environment variables.

| Variable | Description         | Default |
| -------- | ------------------- | ------- |
| HOST     | Server bind address | 0.0.0.0 |
| PORT     | Server port         | 5000    |
| DEBUG    | Enable debug mode   | False   |

Example:

```bash
DEBUG=true PORT=8080 python3 app.py
```

---

## Notes

* This project follows Python best practices and PEP 8 style guidelines.
* Dependencies are pinned for reproducibility.
* The `/health` endpoint is suitable for Kubernetes liveness and readiness probes.
