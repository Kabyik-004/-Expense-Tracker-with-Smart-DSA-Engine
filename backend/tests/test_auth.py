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


# ═════════════════════════════════════════════════════════════════════════════
#  REGISTER
# ═════════════════════════════════════════════════════════════════════════════

class TestRegister:

    def test_register_success(self, client):
        res = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass1",
            "full_name": "New User",
        })
        data = res.get_json()
        assert res.status_code == 201
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["user"]["username"] == "newuser"
        # Password hash must never be in response
        assert "password_hash" not in data["data"]["user"]

    def test_register_duplicate_username(self, client, sample_user):
        res = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "other@example.com",
            "password": "SecurePass1",
        })
        assert res.status_code == 409

    def test_register_duplicate_email(self, client, sample_user):
        res = client.post("/api/auth/register", json={
            "username": "otheruser",
            "email": "test@example.com",
            "password": "SecurePass1",
        })
        assert res.status_code == 409

    def test_register_weak_password(self, client):
        res = client.post("/api/auth/register", json={
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "nodigits",
        })
        assert res.status_code == 400

    def test_register_invalid_email(self, client):
        res = client.post("/api/auth/register", json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "SecurePass1",
        })
        assert res.status_code == 400

    def test_register_short_username(self, client):
        res = client.post("/api/auth/register", json={
            "username": "ab",
            "email": "short@example.com",
            "password": "SecurePass1",
        })
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ═════════════════════════════════════════════════════════════════════════════

class TestLogin:

    def test_login_with_email(self, client, sample_user):
        res = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "TestPass1",
        })
        data = res.get_json()
        assert res.status_code == 200
        assert data["success"] is True
        assert "access_token" in data["data"]

    def test_login_with_username(self, client, sample_user):
        res = client.post("/api/auth/login", json={
            "login": "testuser",
            "password": "TestPass1",
        })
        assert res.status_code == 200

    def test_login_wrong_password(self, client, sample_user):
        res = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "WrongPass1",
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post("/api/auth/login", json={
            "login": "nobody@example.com",
            "password": "TestPass1",
        })
        assert res.status_code == 401


# ═════════════════════════════════════════════════════════════════════════════
#  PROTECTED ROUTES
# ═════════════════════════════════════════════════════════════════════════════

class TestProtectedRoutes:

    def _get_token(self, client, sample_user):
        """Helper — login and return access token."""
        res = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "TestPass1",
        })
        return res.get_json()["data"]["access_token"]

    def test_profile_without_token(self, client):
        res = client.get("/api/auth/profile")
        assert res.status_code == 401

    def test_profile_with_invalid_token(self, client):
        res = client.get("/api/auth/profile", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        assert res.status_code == 401

    def test_get_profile(self, client, sample_user):
        token = self._get_token(client, sample_user)
        res = client.get("/api/auth/profile", headers={
            "Authorization": f"Bearer {token}",
        })
        data = res.get_json()
        assert res.status_code == 200
        assert data["data"]["user"]["username"] == "testuser"

    def test_update_profile(self, client, sample_user):
        token = self._get_token(client, sample_user)
        res = client.put("/api/auth/profile",
            json={"full_name": "Updated Name", "currency": "USD"},
            headers={"Authorization": f"Bearer {token}"},
        )
        data = res.get_json()
        assert res.status_code == 200
        assert data["data"]["user"]["full_name"] == "Updated Name"
        assert data["data"]["user"]["currency"] == "USD"

    def test_validate_token(self, client, sample_user):
        token = self._get_token(client, sample_user)
        res = client.get("/api/auth/validate", headers={
            "Authorization": f"Bearer {token}",
        })
        data = res.get_json()
        assert res.status_code == 200
        assert "token_expires" in data["data"]


# ═════════════════════════════════════════════════════════════════════════════
#  CHANGE PASSWORD
# ═════════════════════════════════════════════════════════════════════════════

class TestChangePassword:

    def _get_token(self, client, sample_user):
        res = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "TestPass1",
        })
        return res.get_json()["data"]["access_token"]

    def test_change_password_success(self, client, sample_user):
        token = self._get_token(client, sample_user)
        res = client.put("/api/auth/change-password",
            json={"current_password": "TestPass1", "new_password": "NewPass1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 200

        # Verify new password works
        res2 = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "NewPass1",
        })
        assert res2.status_code == 200

    def test_change_password_wrong_current(self, client, sample_user):
        token = self._get_token(client, sample_user)
        res = client.put("/api/auth/change-password",
            json={"current_password": "WrongPass1", "new_password": "NewPass1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 401


# ═════════════════════════════════════════════════════════════════════════════
#  REFRESH TOKEN
# ═════════════════════════════════════════════════════════════════════════════

class TestRefreshToken:

    def test_refresh_success(self, client, sample_user):
        # Login to get refresh token
        res = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "TestPass1",
        })
        refresh_token = res.get_json()["data"]["refresh_token"]

        # Use refresh token to get new access token
        res2 = client.post("/api/auth/refresh", headers={
            "Authorization": f"Bearer {refresh_token}",
        })
        data = res2.get_json()
        assert res2.status_code == 200
        assert "access_token" in data["data"]

    def test_refresh_with_access_token_fails(self, client, sample_user):
        """Access tokens cannot be used on the refresh endpoint."""
        res = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "TestPass1",
        })
        access_token = res.get_json()["data"]["access_token"]

        res2 = client.post("/api/auth/refresh", headers={
            "Authorization": f"Bearer {access_token}",
        })
        # Should fail — access token is not a refresh token
        assert res2.status_code == 422 or res2.status_code == 401


# ═════════════════════════════════════════════════════════════════════════════
#  FORGOT / RESET PASSWORD
# ═════════════════════════════════════════════════════════════════════════════

class TestForgotResetPassword:

    def test_forgot_password_existing_email(self, client, sample_user):
        res = client.post("/api/auth/forgot-password", json={
            "email": "test@example.com",
        })
        data = res.get_json()
        assert res.status_code == 200
        assert "reset_token" in data["data"]

    def test_forgot_password_nonexistent_email(self, client):
        """Should still return 200 to prevent email enumeration."""
        res = client.post("/api/auth/forgot-password", json={
            "email": "nobody@example.com",
        })
        assert res.status_code == 200

    def test_reset_password_success(self, client, sample_user):
        # Get reset token
        res = client.post("/api/auth/forgot-password", json={
            "email": "test@example.com",
        })
        reset_token = res.get_json()["data"]["reset_token"]

        # Reset password
        res2 = client.post("/api/auth/reset-password", json={
            "token": reset_token,
            "new_password": "ResetPass1",
        })
        assert res2.status_code == 200

        # Verify new password works
        res3 = client.post("/api/auth/login", json={
            "login": "test@example.com",
            "password": "ResetPass1",
        })
        assert res3.status_code == 200

    def test_reset_password_invalid_token(self, client):
        res = client.post("/api/auth/reset-password", json={
            "token": "invalid-token",
            "new_password": "ResetPass1",
        })
        assert res.status_code == 400
