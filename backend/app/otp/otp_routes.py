"""
OTP routes — HTTP endpoints for the password-reset OTP flow.
All routes are registered under the /api/auth blueprint.

Endpoints:
  POST /api/auth/forgot-password → Submit email, receive OTP
  POST /api/auth/verify-otp      → Verify OTP
  POST /api/auth/reset-password  → Set new password after OTP verification
"""

from flask import Blueprint, request

from app.otp.otp_controller import (
    handle_forgot_password,
    handle_reset_password,
    handle_verify_otp,
)

otp_bp = Blueprint("otp", __name__)


@otp_bp.route("/forgot-password", methods=["POST"])
def forgot_password_route():
    """
    POST /api/auth/forgot-password
    Body: { email }
    """
    return handle_forgot_password(request.get_json())


@otp_bp.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    """
    POST /api/auth/verify-otp
    Body: { email, otp }
    """
    return handle_verify_otp(request.get_json())


@otp_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    """
    POST /api/auth/reset-password
    Body: { email, otp, new_password }
    """
    return handle_reset_password(request.get_json())
