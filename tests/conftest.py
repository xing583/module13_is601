"""
pytest configuration for Playwright E2E tests.

Provides Docker-friendly browser launch flags. Only applies when
tests use the `page` fixture (i.e., Playwright tests).
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
