"""
Shared fixtures and configuration for all test files.
"""

import pytest
from app.otp.rate_limiter import limiter


@pytest.fixture(autouse=True)
def clear_limiter():
    """Clear the global rate limiter before every test to prevent cross-test
    bleed of rate-limit counters (all tests share IP 127.0.0.1)."""
    limiter.clear_all()
