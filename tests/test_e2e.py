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
    token = page.evaluate("() => localStorage.getItem('token')")
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

# ── CALCULATION BREAD TESTS ──

def _register_and_go_to_calcs(page: Page):
    """Helper: register a new user and navigate to calculations page."""
    username, email, password = unique_user()
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirm-password", password)
    page.click("#register-btn")
    page.wait_for_url("**/calculations-page", timeout=10000)
    page.wait_for_timeout(1500)

# ── POSITIVE SCENARIOS ──

def test_add_calculation(page: Page):
    """Add a calculation and verify it appears in the table."""
    _register_and_go_to_calcs(page)
    page.fill("#addA", "10")
    page.select_option("#addOp", "add")
    page.fill("#addB", "5")
    page.click("#addBtn")
    page.wait_for_timeout(2000)
    row = page.locator("#calcTableBody tr").first
    expect(row).to_contain_text("10")
    expect(row).to_contain_text("5")
    expect(row).to_contain_text("15")

def test_browse_calculations(page: Page):
    """Add two calculations and verify both appear."""
    _register_and_go_to_calcs(page)
    page.fill("#addA", "8")
    page.select_option("#addOp", "multiply")
    page.fill("#addB", "3")
    page.click("#addBtn")
    page.wait_for_timeout(2000)
    page.fill("#addA", "20")
    page.select_option("#addOp", "subtract")
    page.fill("#addB", "7")
    page.click("#addBtn")
    page.wait_for_timeout(2000)
    rows = page.locator("#calcTableBody tr")
    expect(rows).to_have_count(2)

def test_edit_calculation(page: Page):
    """Add a calculation, edit it, and verify the update."""
    _register_and_go_to_calcs(page)
    page.fill("#addA", "10")
    page.select_option("#addOp", "add")
    page.fill("#addB", "5")
    page.click("#addBtn")
    page.wait_for_timeout(2000)
    page.locator(".btn-edit").first.click()
    page.wait_for_timeout(1000)
    edit_a = page.locator("[id^='editA-']").first
    edit_a.fill("20")
    page.locator(".btn-save").first.click()
    page.wait_for_timeout(2000)
    row = page.locator("#calcTableBody tr").first
    expect(row).to_contain_text("20")
    expect(row).to_contain_text("25")

def test_delete_calculation(page: Page):
    """Add a calculation, delete it, and verify it's gone."""
    _register_and_go_to_calcs(page)
    page.fill("#addA", "100")
    page.select_option("#addOp", "divide")
    page.fill("#addB", "4")
    page.click("#addBtn")
    page.wait_for_timeout(2000)
    expect(page.locator("#calcTableBody tr")).to_have_count(1)
    page.on("dialog", lambda dialog: dialog.accept())
    page.locator(".btn-delete").first.click()
    page.wait_for_timeout(2000)
    expect(page.locator("#calcTableBody tr")).to_have_count(1)
    expect(page.locator("#calcTableBody")).to_contain_text("No calculations yet")

# ── NEGATIVE SCENARIOS ──

def test_add_empty_operands(page: Page):
    """Try to add with empty fields, expect error message."""
    _register_and_go_to_calcs(page)
    page.click("#addBtn")
    error = page.locator("#addError")
    expect(error).to_contain_text("Please enter both operands")

def test_add_divide_by_zero(page: Page):
    """Try to divide by zero, expect error message."""
    _register_and_go_to_calcs(page)
    page.fill("#addA", "10")
    page.select_option("#addOp", "divide")
    page.fill("#addB", "0")
    page.click("#addBtn")
    error = page.locator("#addError")
    expect(error).to_contain_text("Cannot divide by zero")

def test_unauthorized_access_calculations(page: Page):
    """Access calculations page without login, should redirect to login."""
    page.goto(f"{BASE_URL}/login")
    page.evaluate("() => localStorage.clear()")
    page.goto(f"{BASE_URL}/calculations-page")
    page.wait_for_timeout(2000)
    expect(page).to_have_url(re.compile(r".*/login"))
