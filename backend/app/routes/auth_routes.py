"""
Auth routes — /api/auth/*
Maps HTTP endpoints to auth controller functions.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.controllers.auth_controller import (
    register_user,
    login_user,
    logout_user,
    refresh_access_token,
    get_user_profile,
    update_user_profile,
    change_user_password,
    upload_user_avatar,
    forgot_password,
    reset_password,
    validate_token,
)
from app.utils.responses import error_response

auth_bp = Blueprint("auth", __name__)


# ─── Public routes ───────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /api/auth/register
    Body: { username, email, password, full_name?, currency? }
    Returns: { user, access_token, refresh_token }
    """
    try:
        return register_user(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { login (email or username), password }
    Returns: { user, access_token, refresh_token }
    """
    try:
        return login_user(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password_route():
    """
    POST /api/auth/forgot-password
    Body: { email }
    Returns: { reset_token } (token returned in response for testing only)
    """
    try:
        return forgot_password(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password_route():
    """
    POST /api/auth/reset-password
    Body: { token, new_password }
    """
    try:
        return reset_password(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


# ─── Protected routes (require valid JWT) ────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    POST /api/auth/logout
    Headers: Authorization: Bearer <access_token>
    """
    return logout_user()


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    POST /api/auth/refresh
    Headers: Authorization: Bearer <refresh_token>
    Returns: { access_token }
    """
    return refresh_access_token()


@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    """
    GET /api/auth/profile
    Headers: Authorization: Bearer <access_token>
    Returns: { user }
    """
    return get_user_profile()


@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    PUT /api/auth/profile
    Headers: Authorization: Bearer <access_token>
    Body: { full_name?, currency?, email?, username? }
    """
    try:
        return update_user_profile(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    """
    PUT /api/auth/change-password
    Headers: Authorization: Bearer <access_token>
    Body: { current_password, new_password }
    """
    try:
        return change_user_password(request.get_json())
    except ValidationError as e:
        return error_response("Validation failed", 400, errors=e.messages)


@auth_bp.route("/avatar", methods=["POST"])
@jwt_required()
def upload_avatar():
    """
    POST /api/auth/avatar
    Headers: Authorization: Bearer <access_token>
    Body: { avatar: "<base64_string>" }
    """
    return upload_user_avatar(request.get_json())


@auth_bp.route("/validate", methods=["GET"])
@jwt_required()
def validate():
    """
    GET /api/auth/validate
    Headers: Authorization: Bearer <access_token>
    Returns: { user, token_expires }
    """
    return validate_token()
