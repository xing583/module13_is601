# Module 14: Complete BREAD Functionality for Calculations

## Overview

A FastAPI application with JWT-based authentication, full BREAD (Browse, Read, Edit, Add, Delete) front-end for calculations, and comprehensive Playwright end-to-end tests. Built incrementally from Modules 10–13.

## What's New in Module 14

- **Calculations Dashboard**: `calculations.html` with full BREAD operations UI
- **User-Scoped Data**: Browse endpoint filters calculations by logged-in user
- **Auto Redirect**: Login/Register success redirects to calculations page
- **Extended E2E Tests**: 16 Playwright tests covering login, register, and all BREAD operations (positive + negative scenarios)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/register` | Register a new user, returns JWT token |
| POST | `/users/login` | Login with credentials, returns JWT token |
| GET | `/users/{user_id}` | Get user by ID |
| GET | `/calculations` | Browse calculations (filterable by user_id) |
| GET | `/calculations/{id}` | Read a single calculation |
| POST | `/calculations` | Add a new calculation |
| PUT | `/calculations/{id}` | Edit an existing calculation |
| DELETE | `/calculations/{id}` | Delete a calculation |

## Front-End Pages

- `/login` — Login page with client-side validation
- `/register` — Registration page with client-side validation
- `/calculations-page` — Calculations BREAD dashboard (requires login)

## How to Run Locally

```bash
docker-compose up -d db
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- Login: http://localhost:8000/login
- Register: http://localhost:8000/register
- Calculations: http://localhost:8000/calculations-page
- Swagger UI: http://localhost:8000/docs

## How to Run Tests

```bash
# Unit tests
pytest tests/test_unit.py -v

# Integration tests
DATABASE_URL=postgresql://user:password@localhost:5432/appdb pytest tests/test_integration.py -v

# Playwright E2E tests
playwright install --with-deps chromium
uvicorn main:app --host 0.0.0.0 --port 8000 &
pytest tests/test_e2e.py -v
```

## CI/CD Pipeline

GitHub Actions automatically:
1. Runs unit tests
2. Runs integration tests
3. Runs Playwright E2E tests
4. Pushes Docker image to Docker Hub on success

## Docker Hub

https://hub.docker.com/r/xing583/module13-is601

```bash
docker pull xing583/module13-is601:latest
docker run -p 8000:8000 xing583/module13-is601:latest
```
