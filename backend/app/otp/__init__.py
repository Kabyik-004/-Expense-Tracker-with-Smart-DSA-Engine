"""
OTP module for password reset via email verification.
Architecture:

  otp_routes.py      ← Blueprint with HTTP endpoints
       ↓
  otp_controller.py  ← Request parsing, response formatting
       ↓
  otp_service.py     ← Business logic (generate, verify, invalidate)
       ↓
  otp_utils.py       ← Pure helpers (generate OTP, hash, expiry)
"""

from app.otp.otp_routes import otp_bp

__all__ = ["otp_bp"]
