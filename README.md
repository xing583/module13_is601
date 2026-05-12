# IS601 Final Project: User Profile & Password Change

## Overview

A FastAPI application with JWT-based authentication, full BREAD calculations dashboard, and a new **User Profile & Password Change** feature added as the Final Project. Built incrementally from Modules 10-14, this application demonstrates production-ready patterns for security, testing, CI/CD, and progressive frontend enhancement.

## Final Project Feature: User Profile & Password Change

### What's New

- **Profile Page (`/profile`)**: View and update username and email, plus securely change password
- **Innovation - Password Strength Meter**: Real-time, color-coded strength feedback (Weak/Medium/Strong) as the user types
- **Innovation - Total Calculations Display**: Profile page surfaces the user's lifetime calculation count
- **Security - Forced Re-login**: After a successful password change, the client clears its JWT and redirects to the login page so the new credential is verified end-to-end
- **Toast Notifications**: Modern slide-up green/red toasts replace browser `alert()` for all user feedback

### Three New API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/me` | Returns the current user's profile (username, email, member-since date, total calculation count) |
| PUT | `/users/me` | Update the current user's username and/or email (409 on conflict) |
| POST | `/users/me/password` | Change password after verifying the old password |

### Security Design

- **JWT Bearer authentication** required on all `/users/me*` endpoints
- **bcrypt** password hashing (never store plaintext)
- **Old-password verification** before any password change
- **Pydantic validators** enforce 8+ chars, uppercase, lowercase, and digit on new passwords
- **Client + server matching** of `new_password` and `confirm_password`
- **Forced re-login** after password change invalidates the in-flight client session

## Original Application Features

### API Endpoints (from earlier modules)

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

### Front-End Pages

- `/login` — Login page with client-side validation
- `/register` — Registration page with client-side validation
- `/calculations-page` — Calculations BREAD dashboard
- `/profile` — **NEW** Profile & Password Change page (Final Project)

## How to Run Locally

### Option 1: Docker Compose (recommended)

```bash
docker compose up -d
```

App available at http://localhost:8000

### Option 2: Without Docker

```bash
docker compose up -d db
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### URLs

- Login: http://localhost:8000/login
- Register: http://localhost:8000/register
- Calculations: http://localhost:8000/calculations-page
- **Profile (new)**: http://localhost:8000/profile
- Swagger UI: http://localhost:8000/docs

## How to Run Tests

The project uses a three-layer testing strategy.

### Unit Tests (25 tests — Pydantic schema validation)

```bash
docker compose exec app pytest tests/test_unit.py -v
```

### Integration Tests (15 tests — full HTTP request/response)

```bash
docker compose exec app pytest tests/test_integration.py -v
```

> **Note:** Integration tests drop and recreate all database tables on each run. After running them locally, restart the app service so the schema is rebuilt:
> ```bash
> docker compose restart app
> ```

### Playwright E2E Tests (21 tests — real Chromium browser)

```bash
# Install browsers and system dependencies (first time only)
docker compose exec --user root app playwright install --with-deps chromium

# Run E2E tests
docker compose exec app pytest tests/test_e2e.py -v
```

### Run All Tests at Once

```bash
docker compose exec app pytest -v
```

## CI/CD Pipeline

GitHub Actions automatically runs the full pipeline on every push to `main`:

1. **Run unit tests** — fast Pydantic schema verification
2. **Run integration tests** — verifies routes against a PostgreSQL service container
3. **Install Playwright browsers** — `playwright install --with-deps chromium`
4. **Start FastAPI server** — uvicorn with a `/health` check before E2E begins
5. **Run Playwright E2E tests** — full user-flow validation in headless Chromium
6. **Deploy** — on success, builds and pushes a Docker image to Docker Hub

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml) for the full configuration.

## Docker Hub

The Docker image is automatically published on every passing `main` build:

https://hub.docker.com/r/xing583/module13-is601

```bash
docker pull xing583/module13-is601:latest
docker run -p 8000:8000 xing583/module13-is601:latest
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline definition
├── app/
│   ├── calculator.py            # Calculation business logic
│   ├── database.py              # SQLAlchemy engine + session factory
│   ├── models.py                # User and Calculation ORM models
│   └── schemas.py               # Pydantic schemas (incl. UserUpdate, PasswordChange, UserProfile)
├── static/
│   ├── login.html               # Login page
│   ├── register.html            # Registration page
│   ├── calculations.html        # BREAD dashboard
│   └── profile.html             # Final Project: profile & password change UI
├── tests/
│   ├── conftest.py              # Playwright browser launch fixtures
│   ├── test_unit.py             # 25 Pydantic schema unit tests
│   ├── test_integration.py      # 15 FastAPI route integration tests
│   └── test_e2e.py              # 21 Playwright end-to-end tests
├── Dockerfile
├── docker-compose.yml
├── main.py                      # FastAPI application, all routes, JWT dependency
├── pytest.ini
├── README.md
├── reflection.md
└── requirements.txt
```

## Reflection

See [`reflection.md`](reflection.md) for a detailed reflection covering the Final Project design decisions, security choices, testing strategy, CI/CD lessons, and challenges encountered.
