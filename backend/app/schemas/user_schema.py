"""
User schemas — Marshmallow serialization and validation for auth payloads.
Each schema validates a specific request type and strips unknown fields.
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re


# ─── Registration ────────────────────────────────────────────────────────────

class RegisterSchema(Schema):
    """Validates POST /api/auth/register"""

    username = fields.String(
        required=True,
        validate=[
            validate.Length(min=3, max=80, error="Username must be 3-80 characters"),
            validate.Regexp(
                r"^[a-zA-Z0-9_]+$",
                error="Username can only contain letters, numbers, and underscores",
            ),
        ],
    )
    email = fields.Email(required=True, error_messages={"invalid": "Invalid email address"})
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=128, error="Password must be 8-128 characters"),
        load_only=True,
    )
    full_name = fields.String(
        validate=validate.Length(max=150), load_default=None
    )
    currency = fields.String(
        validate=validate.Length(equal=3, error="Currency must be a 3-letter code"),
        load_default="INR",
    )

    @validates("password")
    def validate_password_strength(self, value, **kwargs):
        """Enforce at least one uppercase, one lowercase, and one digit."""
        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValidationError("Password must contain at least one digit")


# ─── Login ───────────────────────────────────────────────────────────────────

class LoginSchema(Schema):
    """Validates POST /api/auth/login — accepts email OR username."""

    login = fields.String(
        required=True,
        error_messages={"required": "Email or username is required"},
    )
    password = fields.String(
        required=True,
        load_only=True,
        error_messages={"required": "Password is required"},
    )


# ─── Profile Update ─────────────────────────────────────────────────────────

class UpdateProfileSchema(Schema):
    """Validates PUT /api/auth/profile"""

    full_name = fields.String(validate=validate.Length(max=150))
    currency = fields.String(
        validate=validate.Length(equal=3, error="Currency must be a 3-letter code")
    )
    email = fields.Email(error_messages={"invalid": "Invalid email address"})
    username = fields.String(
        validate=[
            validate.Length(min=3, max=80, error="Username must be 3-80 characters"),
            validate.Regexp(
                r"^[a-zA-Z0-9_]+$",
                error="Username can only contain letters, numbers, and underscores",
            ),
        ],
    )


# ─── Change Password ────────────────────────────────────────────────────────

class ChangePasswordSchema(Schema):
    """Validates PUT /api/auth/change-password"""

    current_password = fields.String(
        required=True, load_only=True,
        error_messages={"required": "Current password is required"},
    )
    new_password = fields.String(
        required=True, load_only=True,
        validate=validate.Length(min=8, max=128, error="Password must be 8-128 characters"),
    )

    @validates("new_password")
    def validate_new_password_strength(self, value, **kwargs):
        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValidationError("Password must contain at least one digit")


# ─── Forgot / Reset Password ────────────────────────────────────────────────

class ForgotPasswordSchema(Schema):
    """Validates POST /api/auth/forgot-password"""

    email = fields.Email(
        required=True, error_messages={"invalid": "Invalid email address"}
    )


class ResetPasswordSchema(Schema):
    """Validates POST /api/auth/reset-password"""

    token = fields.String(required=True, error_messages={"required": "Reset token is required"})
    new_password = fields.String(
        required=True, load_only=True,
        validate=validate.Length(min=8, max=128, error="Password must be 8-128 characters"),
    )

    @validates("new_password")
    def validate_new_password_strength(self, value, **kwargs):
        if not re.search(r"[A-Z]", value):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValidationError("Password must contain at least one digit")


# ─── Response Schema (for serializing user data) ────────────────────────────

class UserResponseSchema(Schema):
    """Serializes user data for API responses — never exposes password_hash."""

    id = fields.Integer(dump_only=True)
    username = fields.String(dump_only=True)
    email = fields.String(dump_only=True)
    full_name = fields.String(dump_only=True)
    currency = fields.String(dump_only=True)
    avatar = fields.String(dump_only=True, allow_none=True)
    created_at = fields.DateTime(dump_only=True, format="iso")
    updated_at = fields.DateTime(dump_only=True, format="iso")
