"""
Auth controller — all authentication business logic.
Routes call these functions; they never touch HTTP directly.
"""

from datetime import datetime, timezone

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
)

from app import db
from app.models.user import User
from app.database import create_default_categories_for_user
from app.schemas.user_schema import (
    RegisterSchema,
    LoginSchema,
    UpdateProfileSchema,
    ChangePasswordSchema,
    UserResponseSchema,
)
from app.utils.responses import success_response, error_response
from app.controllers.activity_controller import log_activity

# ── Schema instances ─────────────────────────────────────────────────────────
register_schema = RegisterSchema()
login_schema = LoginSchema()
update_profile_schema = UpdateProfileSchema()
change_password_schema = ChangePasswordSchema()
user_response_schema = UserResponseSchema()


# ═════════════════════════════════════════════════════════════════════════════
#  REGISTER
# ═════════════════════════════════════════════════════════════════════════════

def register_user(request_data):
    """
    Create a new user account.
    - Validates input via Marshmallow
    - Checks for duplicate username/email
    - Hashes password with bcrypt
    - Seeds default categories
    - Returns JWT tokens
    """
    # Validate
    data = register_schema.load(request_data)

    # Check duplicates
    if User.query.filter_by(username=data["username"]).first():
        return error_response("Username already taken", 409)
    if User.query.filter_by(email=data["email"]).first():
        return error_response("Email already registered", 409)

    # Create user
    user = User(
        username=data["username"],
        email=data["email"],
        full_name=data.get("full_name"),
        currency=data.get("currency", "INR"),
    )
    user.set_password(data["password"])
    user.password_changed_at = datetime.now(timezone.utc)

    db.session.add(user)
    db.session.commit()

    # Seed default categories for the new user
    try:
        create_default_categories_for_user(user.id)
    except Exception:
        pass  # Non-critical — user can add categories later

    # Generate tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success_response(
        data={
            "user": user_response_schema.dump(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        message="Account created successfully",
        status_code=201,
    )


# ═════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ═════════════════════════════════════════════════════════════════════════════

def login_user(request_data):
    data = login_schema.load(request_data)
    login_value = data["login"]

    print("Login attempt:", login_value)

    user = User.query.filter_by(email=login_value).first()
    if not user:
        user = User.query.filter_by(username=login_value).first()

    print("User found:", user)

    if user:
        print("Password check:", user.check_password(data["password"]))

    if not user or not user.check_password(data["password"]):
        return error_response("Invalid credentials", 401)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success_response(
        data={
            "user": user_response_schema.dump(user),
            "access_token": access_token,
            "refresh_token": refresh_token,
        },
        message="Login successful",
    )


# ═════════════════════════════════════════════════════════════════════════════
#  REFRESH TOKEN
# ═════════════════════════════════════════════════════════════════════════════

def refresh_access_token():
    """
    Issue a new access token using a valid refresh token.
    The refresh token itself is not rotated.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return error_response("User not found", 404)

    new_access_token = create_access_token(identity=str(user.id))

    return success_response(
        data={"access_token": new_access_token},
        message="Token refreshed",
    )


# ═════════════════════════════════════════════════════════════════════════════
#  LOGOUT  (client-side token discard; server-side blocklist can be added)
# ═════════════════════════════════════════════════════════════════════════════

def logout_user():
    """
    Revoke the current access token so it cannot be used again.
    Requires token blocklist table in the database.
    """
    from app.models.blocklist import TokenBlocklist

    jwt_data = get_jwt()
    jti = jwt_data["jti"]
    token_type = jwt_data["type"]
    user_id = int(get_jwt_identity())
    expires = datetime.fromtimestamp(jwt_data["exp"], tz=timezone.utc)

    entry = TokenBlocklist(
        jti=jti,
        token_type=token_type,
        user_id=user_id,
        expires_at=expires,
    )
    db.session.add(entry)
    db.session.commit()

    return success_response(message="Logged out successfully")


# ═════════════════════════════════════════════════════════════════════════════
#  GET PROFILE
# ═════════════════════════════════════════════════════════════════════════════

def get_user_profile():
    """Return the authenticated user's profile."""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return error_response("User not found", 404)

    return success_response(
        data={"user": user_response_schema.dump(user)},
        message="Profile retrieved",
    )


# ═════════════════════════════════════════════════════════════════════════════
#  UPDATE PROFILE
# ═════════════════════════════════════════════════════════════════════════════

def update_user_profile(request_data):
    """Update the authenticated user's profile fields."""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return error_response("User not found", 404)

    data = update_profile_schema.load(request_data)

    # Check uniqueness if username/email are being changed
    if "username" in data and data["username"] != user.username:
        if User.query.filter_by(username=data["username"]).first():
            return error_response("Username already taken", 409)
        user.username = data["username"]

    if "email" in data and data["email"] != user.email:
        if User.query.filter_by(email=data["email"]).first():
            return error_response("Email already registered", 409)
        user.email = data["email"]

    if "full_name" in data:
        user.full_name = data["full_name"]
    if "currency" in data:
        user.currency = data["currency"]

    db.session.commit()

    log_activity(user.id, "update", "profile", user.id, "Profile updated")

    return success_response(
        data={"user": user_response_schema.dump(user)},
        message="Profile updated successfully",
    )


# ═════════════════════════════════════════════════════════════════════════════
#  UPLOAD AVATAR
# ═════════════════════════════════════════════════════════════════════════════

def upload_user_avatar(request_data):
    """Store a base64-encoded avatar image for the authenticated user."""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return error_response("User not found", 404)

    if not request_data or "avatar" not in request_data:
        return error_response("No avatar data provided", 400)

    avatar_data = request_data["avatar"]

    if not isinstance(avatar_data, str) or len(avatar_data) > 2000000:
        return error_response("Invalid or too large avatar data", 400)

    user.avatar = avatar_data
    db.session.commit()

    log_activity(user.id, "update", "avatar", user.id, "Avatar updated")

    return success_response(
        data={"user": user_response_schema.dump(user)},
        message="Avatar updated successfully",
    )


# ═════════════════════════════════════════════════════════════════════════════
#  CHANGE PASSWORD
# ═════════════════════════════════════════════════════════════════════════════

def change_user_password(request_data):
    """Change password for an authenticated user (requires current password)."""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return error_response("User not found", 404)

    data = change_password_schema.load(request_data)

    if not user.check_password(data["current_password"]):
        return error_response("Current password is incorrect", 401)

    if data["current_password"] == data["new_password"]:
        return error_response("New password must be different from current password", 400)

    user.set_password(data["new_password"])
    db.session.commit()

    log_activity(user.id, "update", "password", user.id, "Password changed")

    return success_response(message="Password changed successfully")


# ═════════════════════════════════════════════════════════════════════════════
#  VALIDATE TOKEN
# ═════════════════════════════════════════════════════════════════════════════

def validate_token():
    """
    Check if the current JWT is still valid.
    Returns the user profile if valid.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return error_response("User not found", 404)

    jwt_data = get_jwt()

    return success_response(
        data={
            "user": user_response_schema.dump(user),
            "token_expires": jwt_data.get("exp"),
        },
        message="Token is valid",
    )
