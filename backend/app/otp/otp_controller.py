"""
OTP controller — maps between HTTP request/response and the service layer.
Controller functions:
  - Parse and validate incoming request data
  - Call the appropriate service function
  - Return a Flask response (success or error)
"""

import logging

import re
from flask import request as flask_request

from app.controllers.activity_controller import log_activity
from app.models.user import User
from app.otp.otp_service import create_otp_record, reset_password, verify_otp
from app.otp.rate_limiter import limiter
from app.utils.responses import error_response, success_response

logger = logging.getLogger(__name__)


def _client_ip():
    """Extract client IP from request headers."""
    forwarded = flask_request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return flask_request.remote_addr or "unknown"


def handle_forgot_password(request_data):
    """
    POST /api/auth/forgot-password
    Body: { email }
    Response: { success, message }

    1. Validate email format
    2. IP-based rate limiting (brute-force protection)
    3. Look up user by email
    4. If user found, check OTP cooldown, generate OTP, hash it, send email
    5. Audit trail for all outcomes
    6. Return success (always — prevents email enumeration)
    """
    if not request_data or "email" not in request_data:
        return error_response("Email is required", 400)

    email = request_data["email"].strip().lower()

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return error_response("Invalid email format", 400)

    ip = _client_ip()
    rate_key = f"forgot_pw:{ip}"
    rate_max = 5
    rate_window = 60

    if not limiter.is_allowed(rate_key, rate_max, rate_window):
        remaining = limiter.remaining(rate_key, rate_max, rate_window)
        logger.warning("Rate limit hit for IP %s — %d remaining", ip, remaining)
        return error_response("Too many requests. Please try again later.", 429)

    user = User.query.filter_by(email=email).first()

    if user:
        result = create_otp_record(user.id, email)
        if result is None:
            logger.warning("OTP cooldown active for %s", email)
        else:
            log_activity(user.id, "request", "otp", details=f"OTP sent to {email}")
            logger.info("Forgot-password flow initiated for %s", email)
    else:
        logger.info("Forgot-password requested for unknown email %s", email)

    return success_response(message="OTP sent successfully")


def handle_verify_otp(request_data):
    """
    POST /api/auth/verify-otp
    Body: { email, otp }
    Response: { success, message }

    1. Validate email + OTP format
    2. Look up user by email
    3. Call service to verify OTP (hash, expiry, attempts, already-used)
    4. Audit trail for success and failure
    5. Return 200 on success, 400 with descriptive error on failure
    """
    if not request_data or "email" not in request_data or "otp" not in request_data:
        return error_response("Email and OTP are required", 400)

    email = request_data["email"].strip().lower()
    otp = request_data["otp"].strip()

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return error_response("Invalid email format", 400)

    if not otp.isdigit() or len(otp) != 6:
        return error_response("OTP must be a 6-digit number", 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response("Invalid email or OTP", 400)

    record, error = verify_otp(user.id, otp)
    if not record:
        log_activity(user.id, "verify_failed", "otp", details=f"OTP verification failed: {error}")
        logger.warning("OTP verification failed for %s: %s", email, error)
        return error_response(error or "Verification failed", 400)

    log_activity(user.id, "verify", "otp", record.id, details="OTP verified successfully")
    logger.info("OTP verified successfully for %s", email)
    return success_response(message="OTP verified successfully")


def handle_reset_password(request_data):
    """
    POST /api/auth/reset-password
    Body: { email, otp, new_password }
    Response: { success, message }

    1. Validate email, OTP, new_password format
    2. Look up user by email
    3. Call service: re-verify OTP hash, hash new password, update DB,
       delete OTP record, update password_changed_at (invalidates all JWTs)
    4. Audit trail for success and failure
    5. Return success or error
    """
    if not request_data or not all(k in request_data for k in ("email", "otp", "new_password")):
        return error_response("Email, OTP, and new password are required", 400)

    email = request_data["email"].strip().lower()
    otp = request_data["otp"].strip()
    new_password = request_data["new_password"]

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return error_response("Invalid email format", 400)

    if not otp.isdigit() or len(otp) != 6:
        return error_response("OTP must be a 6-digit number", 400)

    if len(new_password) < 8:
        return error_response("Password must be at least 8 characters", 400)

    user = User.query.filter_by(email=email).first()
    if not user:
        return error_response("Invalid email or OTP", 400)

    record, error = reset_password(user.id, otp, new_password)
    if not record:
        log_activity(user.id, "reset_failed", "otp", details=f"Password reset failed: {error}")
        logger.warning("Password reset failed for %s: %s", email, error)
        return error_response(error or "Password reset failed", 400)

    log_activity(user.id, "reset", "password", details="Password reset completed")
    logger.info("Password reset completed for %s", email)
    return success_response(message="Password reset successfully")
