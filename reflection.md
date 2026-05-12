# Module 13 Reflection

## Key Experiences

In this module, I extended my FastAPI application with JWT-based authentication and built front-end pages for user login and registration.

## JWT Authentication

Implementing JWT tokens using `python-jose` was straightforward. JWT provides stateless authentication - the server signs a token containing the user identity, and the client stores this token in localStorage for future authenticated requests.

## Front-End Development

Building the login and registration HTML pages helped me understand the importance of client-side validation as a first line of defense. While server-side validation via Pydantic is essential for security, client-side checks improve user experience by providing immediate feedback.

## Playwright E2E Testing

Writing Playwright tests was valuable. The tests simulate real user interactions - filling forms, clicking buttons, and verifying UI feedback. I wrote both positive tests (successful registration and login) and negative tests (short passwords, invalid emails, wrong credentials).

## CI/CD Integration

Integrating Playwright into GitHub Actions required additional setup: installing browser dependencies, starting the FastAPI server in the background, and running tests against the live server.

## Challenges

1. Server startup timing: Playwright tests need the server running before they execute. Solved with a sleep delay and health check in CI.
2. Unique test data: Each test needs unique usernames to avoid conflicts. Used a counter-based helper function.
3. Client-server validation alignment: Ensuring client-side rules match server-side Pydantic validators.

## Conclusion

Module 13 reinforced incremental development. By building on the back-end foundation from Modules 10-12, I focused on authentication UX and end-to-end testing, resulting in a more robust application.


# Module 14 Reflection

## Key Experiences

In this module, I completed the BREAD (Browse, Read, Edit, Add, Delete) front-end functionality for calculations, building on the JWT authentication and back-end API routes developed in Modules 12 and 13.

## BREAD Front-End Implementation

I created a Calculations Dashboard page (`calculations.html`) that provides a complete interface for managing calculations. Users can add new calculations through a form, view all their records in a table, edit entries inline by clicking the Edit button, and delete records with confirmation dialogs. The page automatically redirects unauthenticated users to the login page.

## User-Scoped Data Filtering

A key technical decision was modifying the GET /calculations endpoint to accept an optional `user_id` parameter. This ensures each user only sees their own calculations, which is essential for data privacy and also solved test isolation issues where Playwright tests were seeing leftover data from previous test runs.

## Playwright E2E Testing

I extended the test suite from 9 to 16 tests. The new tests cover all BREAD operations: adding a calculation and verifying it appears in the table, browsing multiple calculations, editing values and confirming updates, and deleting records. Negative tests check for empty operands, divide-by-zero validation, and unauthorized access to the calculations page.

## CI/CD Integration

The GitHub Actions pipeline continues to run all tests automatically and deploys the Docker image to Docker Hub upon success. No changes were needed to the CI/CD workflow since Playwright was already configured in Module 13.

## Challenges

1. WSL browser dependencies: Playwright's Chromium failed to launch in WSL due to missing system libraries. Resolved by installing required packages with apt-get.
2. Test isolation: Shared database state caused test failures. Solved by resetting the database between runs and filtering calculations by user_id.
3. Inline editing UX: Transforming table cells into input fields required careful DOM manipulation in JavaScript to maintain a smooth user experience.

## Conclusion

Module 14 reinforced the value of incremental development. Having a stable back-end API from earlier modules made adding the front-end straightforward. The BREAD pattern provided clear structure for both API design and UI implementation, and comprehensive E2E testing ensures all operations work reliably.


# IS601 Final Project Reflection: User Profile & Password Change

## Key Experiences

The Final Project asked me to extend the IS601 calculator application with a substantial new feature of my own choosing. I selected **User Profile & Password Change** because it sits at the intersection of three areas the course emphasizes: security (authenticated endpoints, password hashing, credential rotation), testing across three layers (unit, integration, end-to-end), and progressive front-end enhancement. The work touched every layer of the application, from new Pydantic validators down to a real-time JavaScript password strength meter.

## Security as a First-Class Concern

The most interesting design decision was how to handle the password change flow. A naive implementation would simply update the hash and return success. Instead, I made three security-driven choices:

1. **Verify the old password before allowing a change.** Without this, anyone who steals an active JWT can take over the account. The new `POST /users/me/password` endpoint refuses any request whose `old_password` does not match the stored bcrypt hash, returning 401.
2. **Enforce strong-password rules at the Pydantic layer.** The `PasswordChange` schema rejects new passwords missing uppercase, lowercase, or digit characters with a 422 before they ever touch the database. The same rules are mirrored client-side so the user sees feedback immediately.
3. **Force re-login on success.** After the server hashes the new password, the client clears `localStorage` and redirects to `/login`. This means the user must demonstrate they actually have the new credential, which closes the gap where a leaked old session token could continue working.

## Three-Layer Testing Strategy

I extended the test suite with a clear separation of concerns across three layers:

- **Unit tests (25 total)**: Validate the new `UserUpdate`, `PasswordChange`, and `UserProfile` Pydantic schemas in isolation — no database, no HTTP. These run in under two seconds and catch validation logic bugs immediately.
- **Integration tests (15 total)**: Use FastAPI's `TestClient` to exercise the three new `/users/me*` endpoints end-to-end through the routing layer. Tests cover the happy path, 401 (missing or invalid token), 409 (username conflict), and 422 (weak password, mismatched confirmation).
- **E2E tests (21 total, 5 new)**: Drive a real Chromium browser via Playwright to verify the profile page renders correctly after login, the toast notification fires on save, the password strength meter updates in real time, and an unauthenticated visit to `/profile` redirects to `/login`.

Each layer caught different bugs during development. Unit tests caught a missed validator on `confirm_password`. Integration tests caught an off-by-one in the routing order (FastAPI was trying to interpret `me` as an integer user ID until I reordered the routes). E2E tests caught a real UX issue where the password-strength wrapper failed to hide when the field was empty.

## Innovation Features

Two additions transformed the page from a functional form into something that feels like a real product:

- **Real-time password strength meter**: A color-coded bar (red/yellow/green) updates as the user types in the new-password field, scoring length and character classes from 0 to 6. This is implemented entirely in client-side JavaScript with no extra request to the server.
- **Total Calculations stat**: The `/users/me` response includes `total_calculations`, surfaced on the profile page as a lifetime usage indicator. It required a single SQLAlchemy `count()` query on the back end and a single element on the front end, but it changes how the page reads and demonstrates that the API can expose derived data beyond raw model fields.

## CI/CD Lessons

The most painful debugging session of this project happened in CI rather than in application code. After pushing my E2E tests, the entire pipeline turned red on a step that had previously been green — the unit tests were failing with "Playwright browser executable not found." The root cause was that I had added an `autouse=True` Playwright fixture in `tests/conftest.py`, which was loaded by every test in the `tests/` directory, including the pure unit tests, which were now trying to launch a browser they did not need and did not have installed yet at that step. Scoping the fixture so it only activates for tests that explicitly request the `page` fixture fixed the pipeline. The lesson: pytest's `conftest.py` is wider in scope than I had assumed, and `autouse=True` should be reserved for fixtures that genuinely apply to everything below it.

## Challenges

1. **FastAPI route ordering**: `/users/me` had to be declared before `/users/{user_id}`, otherwise FastAPI tried to parse `me` as an integer and returned 422.
2. **Test isolation vs. dev database**: Integration tests drop and recreate tables on each run but share a PostgreSQL instance with the dev environment. After running the tests, the dev login would 500 because the `users` table no longer existed. The quick fix is `docker compose restart app`, which re-runs `Base.metadata.create_all`. The proper fix — a dedicated test database — is on my list for a future cleanup.
3. **Chrome in a Docker container**: Running Playwright inside the `app` container required `--no-sandbox` and `--disable-dev-shm-usage` flags plus a system-package install. CI handles this automatically via `playwright install --with-deps`, but local containers require a manual one-time install.
4. **Conftest fixture scope**: The `autouse=True` bug described above cost the most CI iterations and was the most instructive mistake of the project.

## Conclusion

The Final Project pulled together everything from the semester into a single feature: SQLAlchemy models, Pydantic validators, FastAPI dependencies, JWT auth, a real HTML/CSS/JS front end, three layers of automated tests, GitHub Actions CI, and Docker Hub deployment. The most valuable takeaway was the realization that I could now design a feature with security and testability built in from the first commit, rather than bolted on at the end.
