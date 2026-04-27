import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"

_counter = 0

def unique_user():
    global _counter
    _counter += 1
    username = f"testuser{_counter}"
    email = f"testuser{_counter}@example.com"
    password = "SecurePass123"
    return username, email, password

# POSITIVE TESTS

def test_register_success(page: Page):
    username, email, password = unique_user()
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirm-password", password)
    page.click("#register-btn")
    msg = page.locator("#message")
    expect(msg).to_be_visible(timeout=5000)
    expect(msg).to_have_class(re.compile("success"))
    expect(msg).to_contain_text("Registration successful")

def test_login_success(page: Page):
    username, email, password = unique_user()
    page.request.post(f"{BASE_URL}/users/register", data={
        "username": username,
        "email": email,
        "password": password,
    })
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#login-btn")
    msg = page.locator("#message")
    expect(msg).to_be_visible(timeout=5000)
    expect(msg).to_have_class(re.compile("success"))
    expect(msg).to_contain_text("Login successful")

def test_login_token_stored(page: Page):
    username, email, password = unique_user()
    page.request.post(f"{BASE_URL}/users/register", data={
        "username": username,
        "email": email,
        "password": password,
    })
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", username)
    page.fill("#password", password)
    page.click("#login-btn")
    expect(page.locator("#message")).to_contain_text("Login successful", timeout=5000)
    token = page.evaluate("() => localStorage.getItem('access_token')")
    assert token is not None and len(token) > 0

# NEGATIVE TESTS

def test_register_short_password(page: Page):
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", "validuser")
    page.fill("#email", "valid@example.com")
    page.fill("#password", "123")
    page.fill("#confirm-password", "123")
    page.click("#register-btn")
    error = page.locator("#password-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("at least 8 characters")

def test_register_invalid_email(page: Page):
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", "validuser")
    page.fill("#email", "not-an-email")
    page.fill("#password", "SecurePass123")
    page.fill("#confirm-password", "SecurePass123")
    page.click("#register-btn")
    error = page.locator("#email-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("valid email")

def test_register_password_mismatch(page: Page):
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", "validuser")
    page.fill("#email", "valid@example.com")
    page.fill("#password", "SecurePass123")
    page.fill("#confirm-password", "DifferentPass")
    page.click("#register-btn")
    error = page.locator("#confirm-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("do not match")

def test_register_short_username(page: Page):
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", "ab")
    page.fill("#email", "valid@example.com")
    page.fill("#password", "SecurePass123")
    page.fill("#confirm-password", "SecurePass123")
    page.click("#register-btn")
    error = page.locator("#username-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("at least 3 characters")

def test_login_wrong_password(page: Page):
    username, email, password = unique_user()
    page.request.post(f"{BASE_URL}/users/register", data={
        "username": username,
        "email": email,
        "password": password,
    })
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", username)
    page.fill("#password", "WrongPassword999")
    page.click("#login-btn")
    msg = page.locator("#message")
    expect(msg).to_be_visible(timeout=5000)
    expect(msg).to_have_class(re.compile("error"))
    expect(msg).to_contain_text("Invalid")

def test_login_nonexistent_user(page: Page):
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", "noSuchUser999")
    page.fill("#password", "SomePassword123")
    page.click("#login-btn")
    msg = page.locator("#message")
    expect(msg).to_be_visible(timeout=5000)
    expect(msg).to_have_class(re.compile("error"))
    expect(msg).to_contain_text("Invalid")
