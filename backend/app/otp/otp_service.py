"""
OTP service — business logic layer for the password-reset OTP flow.
All functions are pure service functions; they do not handle HTTP directly.
"""

import logging
from datetime import datetime, timezone

from flask import current_app

from app import db
from app.models.password_reset_otp import PasswordResetOTP
from app.otp.otp_utils import check_otp, generate_otp, get_otp_expiry, hash_otp, is_otp_expired
from app.otp.rate_limiter import limiter

logger = logging.getLogger(__name__)


def _cfg(key, default):
    """Read a config value from Flask app config with a fallback default."""
    try:
        return current_app.config.get(key, default)
    except RuntimeError:
        return default


def delete_expired_otps():
    """Remove all OTP records whose expiry has passed (keeps DB lean)."""
    now = datetime.now(timezone.utc)
    expired = PasswordResetOTP.query.filter(PasswordResetOTP.expires_at <= now).all()
    if expired:
        for record in expired:
            db.session.delete(record)
        db.session.commit()
        logger.info("Cleaned up %d expired OTP record(s)", len(expired))


def send_otp(email, otp):
    """
    Dispatch the OTP to the given email address via SMTP.
    Returns True if delivery succeeded, False otherwise.
    """
    from app.email_service import send_otp_email

    delivered = send_otp_email(email, otp)
    if delivered:
        logger.info("OTP delivered to %s", email)
    else:
        logger.error("OTP delivery failed for %s", email)
    return delivered


def create_otp_record(user_id, email):
    """
    Generate an OTP, hash it, persist a PasswordResetOTP record to the database,
    send the OTP via email, and return the plain-text OTP (for dev fallback).

    Security checks applied:
      1. Cooldown: one OTP per email every OTP_RESEND_COOLDOWN seconds
      2. Invalidates any previous unverified OTPs for this user
      3. Deletes expired OTPs from the database
      4. Configurable expiry window
    """
    cooldown_sec = _cfg("OTP_RESEND_COOLDOWN", 60)

    cooldown_key = f"otp_cooldown:{email}"
    remaining = limiter.get_cooldown(cooldown_key, cooldown_sec)
    if remaining > 0:
        logger.warning("OTP cooldown active for %s — %.0fs remaining", email, remaining)
        return None

    limiter.clear(cooldown_key)
    limiter.is_allowed(cooldown_key, 1, cooldown_sec)

    invalidate_otp(user_id)
    delete_expired_otps()

    otp = generate_otp()
    otp_hash = hash_otp(otp)
    expiry_minutes = _cfg("OTP_EXPIRY_MINUTES", 5)

    record = PasswordResetOTP(
        user_id=user_id,
        email=email,
        otp_hash=otp_hash,
        expires_at=get_otp_expiry(expiry_minutes),
        attempts=0,
        verified=False,
    )
    db.session.add(record)
    db.session.commit()

    delivered = send_otp(email, otp)

    if not delivered:
        logger.info(
            "Dev fallback — OTP for %s: %s (email not configured)",
            email, otp,
        )
    else:
        logger.info(
            "OTP record %d created for user %s — delivered=%s",
            record.id, user_id, delivered,
        )

    return otp


def verify_otp(user_id, otp):
    """
    Validate a plain-text OTP for the given user.

    Checks:
      - An active OTP record exists
      - OTP is not expired
      - OTP has not already been used
      - Attempt limit has not been exceeded
      - OTP hash matches

    On success:
      - Marks the OTP record as verified
      - Returns (record, None)

    On failure:
      - Increments the attempt counter
      - Returns (None, error_message)
    """
    max_attempts = _cfg("OTP_MAX_ATTEMPTS", 5)
    record = get_most_recent_otp(user_id)
    if not record:
        return None, "No active OTP found"

    if is_otp_expired(record.expires_at):
        return None, "OTP has expired"

    if record.verified:
        return None, "This OTP has already been used"

    if record.attempts >= max_attempts:
        return None, "Maximum attempts exceeded"

    if not check_otp(otp, record.otp_hash):
        record.attempts += 1
        db.session.commit()
        remaining = max_attempts - record.attempts
        if remaining <= 0:
            return None, "Maximum attempts exceeded"
        return None, f"Invalid OTP. {remaining} attempt{'s' if remaining != 1 else ''} remaining"

    record.verified = True
    db.session.commit()
    return record, None


def reset_password(user_id, otp, new_password):
    """
    Complete the password reset flow.

    Requires a verified OTP record for the user. Re-verifies the hash,
    updates the password, updates password_changed_at (invalidates all
    existing JWTs), and deletes the OTP record.
    """
    from app.models.user import User

    record = PasswordResetOTP.query.filter(
        PasswordResetOTP.user_id == user_id,
        PasswordResetOTP.verified == True,
    ).order_by(PasswordResetOTP.created_at.desc()).first()

    if not record:
        return None, "No verified OTP found. Please verify your OTP first."

    if is_otp_expired(record.expires_at):
        return None, "OTP has expired. Please request a new one."

    if not check_otp(otp, record.otp_hash):
        return None, "OTP mismatch. Please start the process again."

    user = db.session.get(User, int(user_id))
    if not user:
        return None, "User not found."

    user.set_password(new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    user.reset_token = None
    user.reset_token_expires = None

    db.session.delete(record)
    db.session.commit()

    logger.info("Password reset completed for user %s", user_id)
    return record, None


def invalidate_otp(user_id):
    """
    Mark all active OTP records for the given user as expired/invalid.
    Called before creating a new OTP to enforce "one active OTP" limit.
    """
    now = datetime.now(timezone.utc)
    active_otps = PasswordResetOTP.query.filter(
        PasswordResetOTP.user_id == user_id,
        PasswordResetOTP.verified == False,
        PasswordResetOTP.expires_at > now,
    ).all()

    for record in active_otps:
        record.expires_at = now
    db.session.commit()


def get_most_recent_otp(user_id):
    """
    Retrieve the most recent OTP record for the given user,
    regardless of expiry or verification status.
    """
    return PasswordResetOTP.query.filter_by(
        user_id=user_id,
    ).order_by(PasswordResetOTP.created_at.desc()).first()


def get_active_otp(user_id):
    """
    Retrieve the most recent active (unexpired, unverified) OTP record
    for the given user. Returns None if no active record exists.
    """
    now = datetime.now(timezone.utc)
    return PasswordResetOTP.query.filter(
        PasswordResetOTP.user_id == user_id,
        PasswordResetOTP.verified == False,
        PasswordResetOTP.expires_at > now,
    ).order_by(PasswordResetOTP.created_at.desc()).first()
