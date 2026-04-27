# Module 13: JWT Login/Registration with Client-Side Validation & Playwright E2E

## Overview

A FastAPI application with JWT-based authentication (login & registration), front-end HTML pages with client-side validation, and Playwright end-to-end tests.

## What's New in Module 13

- **JWT Authentication**: Login and register endpoints return JWT tokens
- **Front-End Pages**: `login.html` and `register.html` with client-side validation
- **Playwright E2E Tests**: 9 tests covering positive and negative scenarios

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/register` | Register a new user, returns JWT token |
| POST | `/users/login` | Login with credentials, returns JWT token |
| GET | `/users/{user_id}` | Get user by ID |
| GET | `/calculations` | Browse all calculations |
| GET | `/calculations/{id}` | Read a single calculation |
| POST | `/calculations` | Add a new calculation |
| PUT | `/calculations/{id}` | Edit an existing calculation |
| DELETE | `/calculations/{id}` | Delete a calculation |

## How to Run Locally

```bash
docker-compose up -d db
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- Login page: http://localhost:8000/login
- Register page: http://localhost:8000/register
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
