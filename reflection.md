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

1. WSL browser dependencies: Playwright's Chromium failed to launch in WSL due to missing system libraries (libgbm1, libnss3, libgtk). Resolved by installing required packages with apt-get.
2. Test isolation: Shared database state caused test failures. Solved by resetting the database between runs and filtering calculations by user_id.
3. Inline editing UX: Transforming table cells into input fields required careful DOM manipulation in JavaScript to maintain a smooth user experience.

## Conclusion

Module 14 reinforced the value of incremental development. Having a stable back-end API from earlier modules made adding the front-end straightforward. The BREAD pattern provided clear structure for both API design and UI implementation, and comprehensive E2E testing ensures all operations work reliably.
