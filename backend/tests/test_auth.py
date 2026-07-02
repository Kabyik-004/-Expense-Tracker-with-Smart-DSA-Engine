"""
Tests for auth endpoints.
Run with: pytest tests/test_auth.py -v
"""

import json
import pytest

from app import create_app, db
from app.config import TestingConfig
from app.models.user import User


@pytest.fixture
def app():
    """Create a test app with in-memory SQLite database."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create and return a sample user for login tests."""
    with app.app_context():
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
        )
        user.set_password("TestPass1")
        db.session.add(user)
        db.session.commit()
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }


@pytest.fixture
def auth_headers(sample_user, app, client):
    """Return auth headers for the sample user."""
    login_res = client.post("/api/auth/login", json={
        "login": "testuser", "password": "TestPass1",
    })
    access_token = login_res.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


# ═════════════════════════════════════════════════════════════════════════════
#  REGISTER
# ═════════════════════════════════════════════════════════════════════════════

class TestRegister:

    def test_register_success(self, client):
        res = client.post("/api/auth/register", json={
            "username": "newuser", "email": "new@example.com", "password": "SecurePass1",
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["username"] == "newuser"

    def test_register_duplicate_username(self, client, sample_user):
        res = client.post("/api/auth/register", json={
            "username": "testuser", "email": "other@example.com", "password": "SecurePass1",
        })
        assert res.status_code == 409
        assert "already taken" in res.get_json()["message"].lower()

    def test_register_duplicate_email(self, client, sample_user):
        res = client.post("/api/auth/register", json={
            "username": "otheruser", "email": "test@example.com", "password": "SecurePass1",
        })
        assert res.status_code == 409

    def test_register_weak_password(self, client):
        res = client.post("/api/auth/register", json={
            "username": "weakuser", "email": "weak@example.com", "password": "short",
        })
        assert res.status_code == 400

    def test_register_invalid_email(self, client):
        res = client.post("/api/auth/register", json={
            "username": "baduser", "email": "not-an-email", "password": "SecurePass1",
        })
        assert res.status_code == 400

    def test_register_short_username(self, client):
        res = client.post("/api/auth/register", json={
            "username": "ab", "email": "ab@example.com", "password": "SecurePass1",
        })
        assert res.status_code == 400

    def test_register_password_no_uppercase(self, client):
        res = client.post("/api/auth/register", json={
            "username": "noupper", "email": "nu@example.com", "password": "alllowercase1",
        })
        assert res.status_code == 400

    def test_register_password_no_digit(self, client):
        res = client.post("/api/auth/register", json={
            "username": "nodigit", "email": "nd@example.com", "password": "AllLettersNo",
        })
        assert res.status_code == 400

    def test_register_missing_fields(self, client):
        res = client.post("/api/auth/register", json={"username": "test"})
        assert res.status_code == 400
        res = client.post("/api/auth/register", json={})
        assert res.status_code == 400

    def test_register_username_with_special_chars(self, client):
        res = client.post("/api/auth/register", json={
            "username": "user@name!", "email": "special@example.com", "password": "SecurePass1",
        })
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ═════════════════════════════════════════════════════════════════════════════

class TestLogin:

    def test_login_with_email(self, client, sample_user):
        res = client.post("/api/auth/login", json={
            "login": "test@example.com", "password": "TestPass1",
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_login_with_username(self, client, sample_user):
        res = client.post("/api/auth/login", json={
            "login": "testuser", "password": "TestPass1",
        })
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_login_wrong_password(self, client, sample_user):
        res = client.post("/api/auth/login", json={
            "login": "testuser", "password": "WrongPass1",
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/auth/login", json={
            "login": "nobody", "password": "TestPass1",
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post("/api/auth/login", json={})
        assert res.status_code == 400
        res = client.post("/api/auth/login", json={"login": "test"})
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════════════════
#  PROFILE & PROTECTED ROUTES
# ═════════════════════════════════════════════════════════════════════════════

class TestProtectedRoutes:

    def test_profile_without_token(self, client):
        res = client.get("/api/auth/profile")
        assert res.status_code == 401

    def test_profile_with_invalid_token(self, client):
        res = client.get("/api/auth/profile", headers={"Authorization": "Bearer invalidtoken"})
        assert res.status_code == 401

    def test_get_profile(self, client, auth_headers, sample_user):
        res = client.get("/api/auth/profile", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["data"]["user"]["username"] == "testuser"
        assert data["data"]["user"]["email"] == "test@example.com"

    def test_update_profile(self, client, auth_headers):
        res = client.put("/api/auth/profile", json={
            "full_name": "Updated Name", "currency": "USD",
        }, headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()["data"]["user"]
        assert data["full_name"] == "Updated Name"
        assert data["currency"] == "USD"

    def test_validate_token(self, client, auth_headers, sample_user):
        res = client.get("/api/auth/validate", headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert data["data"]["user"]["id"] == sample_user["id"]

    def test_logout_user(self, client, auth_headers):
        res = client.post("/api/auth/logout", headers=auth_headers)
        assert res.status_code == 200

    def test_upload_avatar(self, client, auth_headers):
        import base64
        fake_avatar = base64.b64encode(b"fake_image_data").decode()
        res = client.post("/api/auth/avatar", json={
            "avatar": f"data:image/png;base64,{fake_avatar}",
        }, headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_get_recent_activity(self, client, auth_headers):
        res = client.get("/api/auth/activity", headers=auth_headers)
        assert res.status_code == 200
        assert isinstance(res.get_json()["data"]["activities"], list)


# ═════════════════════════════════════════════════════════════════════════════
#  CHANGE PASSWORD
# ═════════════════════════════════════════════════════════════════════════════

class TestChangePassword:

    def test_change_password_success(self, client, auth_headers):
        res = client.put("/api/auth/change-password", json={
            "current_password": "TestPass1", "new_password": "NewPass123",
        }, headers=auth_headers)
        assert res.status_code == 200

    def test_change_password_wrong_current(self, client, auth_headers):
        res = client.put("/api/auth/change-password", json={
            "current_password": "WrongPass1", "new_password": "NewPass123",
        }, headers=auth_headers)
        assert res.status_code == 401

    def test_change_password_weak_new(self, client, auth_headers):
        res = client.put("/api/auth/change-password", json={
            "current_password": "TestPass1", "new_password": "weak",
        }, headers=auth_headers)
        assert res.status_code == 400

    def test_change_password_missing_fields(self, client, auth_headers):
        res = client.put("/api/auth/change-password", json={}, headers=auth_headers)
        assert res.status_code == 400
        res = client.put("/api/auth/change-password", json={"current_password": "TestPass1"}, headers=auth_headers)
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════════════════
#  REFRESH TOKEN
# ═════════════════════════════════════════════════════════════════════════════

class TestRefreshToken:

    def test_refresh_success(self, client, sample_user):
        login_res = client.post("/api/auth/login", json={
            "login": "testuser", "password": "TestPass1",
        })
        refresh_token = login_res.get_json()["data"]["refresh_token"]
        res = client.post("/api/auth/refresh", json={},
            headers={"Authorization": f"Bearer {refresh_token}"})
        assert res.status_code == 200
        assert "access_token" in res.get_json()["data"]

    def test_refresh_with_access_token_fails(self, client, sample_user):
        login_res = client.post("/api/auth/login", json={
            "login": "testuser", "password": "TestPass1",
        })
        access_token = login_res.get_json()["data"]["access_token"]
        res = client.post("/api/auth/refresh", json={},
            headers={"Authorization": f"Bearer {access_token}"})
        assert res.status_code == 401

    def test_refresh_missing_token(self, client):
        res = client.post("/api/auth/refresh", json={})
        assert res.status_code == 401


# ═════════════════════════════════════════════════════════════════════════════
#  FORGOT / RESET PASSWORD
# ═════════════════════════════════════════════════════════════════════════════

class TestForgotResetPassword:

    def test_forgot_password_existing_email(self, client, sample_user, app):
        with app.app_context():
            res = client.post("/api/auth/forgot-password", json={
                "email": "test@example.com",
            })
            assert res.status_code == 200
            assert res.get_json()["success"] is True
            user = User.query.filter_by(email="test@example.com").first()
            assert user.reset_token is not None
            assert user.reset_token_expires is not None

    def test_forgot_password_nonexistent_email(self, client):
        res = client.post("/api/auth/forgot-password", json={
            "email": "nobody@example.com",
        })
        assert res.status_code == 200
        assert "If an account" in res.get_json()["message"]

    def test_reset_password_success(self, client, sample_user, app):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "test@example.com"})
            user = User.query.filter_by(email="test@example.com").first()
            token = user.reset_token
        res = client.post("/api/auth/reset-password", json={
            "token": token, "new_password": "ResetPass1",
        })
        assert res.status_code == 200
        login_res = client.post("/api/auth/login", json={
            "login": "testuser", "password": "ResetPass1",
        })
        assert login_res.status_code == 200

    def test_reset_password_invalid_token(self, client):
        res = client.post("/api/auth/reset-password", json={
            "token": "invalid-token-123", "new_password": "ResetPass1",
        })
        assert res.status_code == 400

    def test_reset_password_expired_token(self, client, sample_user, app):
        from datetime import datetime, timedelta, timezone
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "test@example.com"})
            user = User.query.filter_by(email="test@example.com").first()
            user.reset_token_expires = datetime.now(timezone.utc) - timedelta(hours=2)
            db.session.commit()
            token = user.reset_token
        res = client.post("/api/auth/reset-password", json={
            "token": token, "new_password": "ResetPass1",
        })
        assert res.status_code == 400

    def test_reset_password_weak_new(self, client, sample_user, app):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "test@example.com"})
            user = User.query.filter_by(email="test@example.com").first()
            token = user.reset_token
        res = client.post("/api/auth/reset-password", json={
            "token": token, "new_password": "weak",
        })
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════════════════
#  AUTH EDGE CASES
# ═════════════════════════════════════════════════════════════════════════════

class TestAuthEdgeCases:

    def test_register_then_login(self, client):
        client.post("/api/auth/register", json={
            "username": "caseuser", "email": "caseuser@example.com", "password": "SecurePass1",
        })
        res = client.post("/api/auth/login", json={
            "login": "caseuser", "password": "SecurePass1",
        })
        assert res.status_code == 200

    def test_register_default_categories_created(self, client, app):
        res = client.post("/api/auth/register", json={
            "username": "defcat", "email": "defcat@example.com", "password": "SecurePass1",
        })
        user_id = res.get_json()["data"]["user"]["id"]
        with app.app_context():
            from app.models.category import Category
            cats = Category.query.filter_by(user_id=user_id).all()
            assert len(cats) == 10

    def test_multiple_consecutive_requests(self, client, auth_headers):
        for _ in range(5):
            res = client.get("/api/auth/profile", headers=auth_headers)
            assert res.status_code == 200
