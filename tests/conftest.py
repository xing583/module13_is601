"""
pytest configuration for Playwright E2E tests.

Provides Docker-friendly browser launch flags and a slightly higher
default timeout so tests run reliably in both CI and containerized
local environments.
"""

import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Pass extra Chromium flags so the browser launches in containers."""
    return {
        **browser_type_launch_args,
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    }


@pytest.fixture(autouse=True)
def _set_default_timeout(page):
    """Use a 10s default timeout (more reliable than the 5s default)."""
    page.set_default_timeout(10000)
    page.set_default_navigation_timeout(10000)
    yield
