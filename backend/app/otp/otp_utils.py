"""
OTP utilities — pure helper functions for OTP generation, hashing, and expiry.
These functions have no database or request dependencies.
"""

import secrets
from datetime import datetime, timedelta, timezone

import bcrypt


def generate_otp(length=6):
    """
    Generate a cryptographically secure numeric OTP of the given length.
    Returns the OTP as a string.
    """
    return str(secrets.randbelow(10**length)).zfill(length)


def hash_otp(otp):
    """
    Hash the OTP using bcrypt before storing in the database.
    Returns the hashed string.
    """
    return bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_otp(otp, otp_hash):
    """
    Verify a plain-text OTP against a stored bcrypt hash.
    Returns True if the OTP matches, False otherwise.
    """
    return bcrypt.checkpw(otp.encode("utf-8"), otp_hash.encode("utf-8"))


def get_otp_expiry(minutes=5):
    """
    Return a UTC datetime representing the OTP expiry time.
    Default is 5 minutes from now.
    """
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def is_otp_expired(expires_at):
    """
    Check whether the given expiry datetime is in the past.
    Returns True if expired, False otherwise.
    """
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= expires_at


def max_attempts():
    """
    Return the maximum number of failed verification attempts allowed
    before the OTP record is invalidated.
    """
    return 5
