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
