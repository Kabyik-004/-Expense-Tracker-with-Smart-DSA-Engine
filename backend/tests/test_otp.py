"""
Comprehensive OTP flow tests.
Run with: pytest tests/test_otp.py -v
"""

import pytest

from app import create_app, db
from app.config import TestingConfig
from app.models.user import User
from app.models.password_reset_otp import PasswordResetOTP
from app.models.activity_log import ActivityLog


TEST_OTP = "123456"


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(app):
    from datetime import datetime, timezone
    with app.app_context():
        u = User(username="otptest", email="otptest@test.com")
        u.set_password("TestPass1")
        u.password_changed_at = datetime.now(timezone.utc)
        db.session.add(u)
        db.session.commit()
        return {"id": u.id, "username": u.username, "email": u.email}


@pytest.fixture
def patch_otp(monkeypatch):
    import app.otp.otp_utils as ou
    import app.otp.otp_service as svc
    monkeypatch.setattr(ou, "generate_otp", lambda length=6: TEST_OTP)
    monkeypatch.setattr(svc, "generate_otp", lambda length=6: TEST_OTP)

# ═════════════════════════════════════════════════════════════════════════════
#  FORGOT PASSWORD
# ═════════════════════════════════════════════════════════════════════════════

class TestForgotPassword:

    def test_success(self, client, sample_user):
        res = client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_no_enumeration(self, client):
        res = client.post("/api/auth/forgot-password", json={"email": "ghost@test.com"})
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    def test_invalid_email_format(self, client):
        res = client.post("/api/auth/forgot-password", json={"email": "bad-email"})
        assert res.status_code == 400
        assert "Invalid email" in res.get_json()["message"]

    def test_missing_email(self, client):
        res = client.post("/api/auth/forgot-password", json={})
        assert res.status_code == 400
        assert "Email is required" in res.get_json()["message"]

    def test_rate_limit(self, client, sample_user):
        for i in range(5):
            r = client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            assert r.status_code == 200, f"Request {i+1} should be 200"
        r = client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
        assert r.status_code == 429
        assert "Too many requests" in r.get_json()["message"]

    def test_cooldown_only_one_otp_created(self, client, sample_user, app):
        with app.app_context():
            for _ in range(3):
                client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            count = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).count()
            assert count == 1, f"Expected 1 OTP record due to cooldown, got {count}"

    def test_creates_otp_record(self, client, sample_user, app):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            record = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).first()
            assert record is not None
            assert record.email == "otptest@test.com"
            assert record.verified is False
            assert record.attempts == 0
            assert record.expires_at is not None


# ═════════════════════════════════════════════════════════════════════════════
#  VERIFY OTP
# ═════════════════════════════════════════════════════════════════════════════

class TestVerifyOTP:

    def test_success(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
        res = client.post("/api/auth/verify-otp", json={
            "email": "otptest@test.com", "otp": TEST_OTP,
        })
        assert res.status_code == 200
        assert "verified" in res.get_json()["message"].lower()
        with app.app_context():
            record = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).first()
            assert record.verified is True

    def test_wrong_otp(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
        res = client.post("/api/auth/verify-otp", json={
            "email": "otptest@test.com", "otp": "999999",
        })
        assert res.status_code == 400

    def test_nonexistent_user(self, client):
        res = client.post("/api/auth/verify-otp", json={
            "email": "ghost@test.com", "otp": "123456",
        })
        assert res.status_code == 400

    def test_missing_fields(self, client):
        res = client.post("/api/auth/verify-otp", json={"email": "a@b.com"})
        assert res.status_code == 400
        res = client.post("/api/auth/verify-otp", json={})
        assert res.status_code == 400

    def test_expired_otp(self, client, sample_user, app, patch_otp):
        from datetime import datetime, timedelta, timezone
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            record = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).first()
            record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            db.session.commit()
        res = client.post("/api/auth/verify-otp", json={
            "email": "otptest@test.com", "otp": TEST_OTP,
        })
        assert res.status_code == 400
        assert "expired" in res.get_json()["message"].lower()

    def test_max_attempts(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
        for i in range(5):
            r = client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": "999999",
            })
            assert r.status_code == 400, f"Attempt {i+1} should be 400"
        r = client.post("/api/auth/verify-otp", json={
            "email": "otptest@test.com", "otp": TEST_OTP,
        })
        assert r.status_code == 400
        assert "exceeded" in r.get_json()["message"].lower()

    def test_already_used_otp(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": TEST_OTP,
            })
        r = client.post("/api/auth/verify-otp", json={
            "email": "otptest@test.com", "otp": TEST_OTP,
        })
        assert r.status_code == 400
        assert "used" in r.get_json()["message"].lower()

    def test_invalid_otp_format(self, client, sample_user):
        res = client.post("/api/auth/verify-otp", json={
            "email": "otptest@test.com", "otp": "abcd",
        })
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════════════════
#  RESET PASSWORD
# ═════════════════════════════════════════════════════════════════════════════

class TestResetPassword:

    def test_success(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": TEST_OTP,
            })
        res = client.post("/api/auth/reset-password", json={
            "email": "otptest@test.com", "otp": TEST_OTP, "new_password": "NewPass123",
        })
        assert res.status_code == 200
        assert res.get_json()["success"] is True
        login = client.post("/api/auth/login", json={
            "login": "otptest", "password": "NewPass123",
        })
        assert login.status_code == 200

    def test_wrong_otp(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": TEST_OTP,
            })
        res = client.post("/api/auth/reset-password", json={
            "email": "otptest@test.com", "otp": "999999", "new_password": "NewPass123",
        })
        assert res.status_code == 400

    def test_expired_otp(self, client, sample_user, app, patch_otp):
        from datetime import datetime, timedelta, timezone
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": TEST_OTP,
            })
            record = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).first()
            record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            db.session.commit()
        res = client.post("/api/auth/reset-password", json={
            "email": "otptest@test.com", "otp": TEST_OTP, "new_password": "NewPass123",
        })
        assert res.status_code == 400
        assert "expired" in res.get_json()["message"].lower()

    def test_weak_password(self, client, sample_user):
        res = client.post("/api/auth/reset-password", json={
            "email": "otptest@test.com", "otp": "123456", "new_password": "weak",
        })
        assert res.status_code == 400

    def test_nonexistent_user(self, client):
        res = client.post("/api/auth/reset-password", json={
            "email": "ghost@test.com", "otp": "123456", "new_password": "NewPass123",
        })
        assert res.status_code == 400

    def test_missing_fields(self, client):
        res = client.post("/api/auth/reset-password", json={})
        assert res.status_code == 400
        res = client.post("/api/auth/reset-password", json={"email": "a@b.com"})
        assert res.status_code == 400
        res = client.post("/api/auth/reset-password", json={"email": "a@b.com", "otp": "123456"})
        assert res.status_code == 400

    def test_jwt_invalidation(self, client, sample_user, app, patch_otp):
        with app.app_context():
            old_login = client.post("/api/auth/login", json={
                "login": "otptest", "password": "TestPass1",
            })
            old_token = old_login.get_json()["data"]["access_token"]
            r = client.get("/api/auth/profile", headers={
                "Authorization": f"Bearer {old_token}",
            })
            assert r.status_code == 200

            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": TEST_OTP,
            })
            client.post("/api/auth/reset-password", json={
                "email": "otptest@test.com", "otp": TEST_OTP, "new_password": "NewPass123",
            })

            r = client.get("/api/auth/profile", headers={
                "Authorization": f"Bearer {old_token}",
            })
            assert r.status_code == 401


# ═════════════════════════════════════════════════════════════════════════════
#  AUDIT TRAIL
# ═════════════════════════════════════════════════════════════════════════════

class TestOTPAuditTrail:

    def test_audit_entries_created(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            logs = ActivityLog.query.filter_by(user_id=sample_user["id"]).all()
            assert any(log.action == "request" and log.entity_type == "otp" for log in logs)

            client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": TEST_OTP,
            })
            logs = ActivityLog.query.filter_by(user_id=sample_user["id"]).all()
            assert any(log.action == "verify" and log.entity_type == "otp" for log in logs)

            client.post("/api/auth/reset-password", json={
                "email": "otptest@test.com", "otp": TEST_OTP, "new_password": "NewPass123",
            })
            logs = ActivityLog.query.filter_by(user_id=sample_user["id"]).all()
            assert any(log.action == "reset" and log.entity_type == "password" for log in logs)

    def test_audit_failure_entries(self, client, sample_user, app, patch_otp):
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            client.post("/api/auth/verify-otp", json={
                "email": "otptest@test.com", "otp": "999999",
            })
            logs = ActivityLog.query.filter_by(user_id=sample_user["id"]).all()
            assert any(log.action == "verify_failed" for log in logs)

            client.post("/api/auth/reset-password", json={
                "email": "otptest@test.com", "otp": "999999", "new_password": "NewPass123",
            })
            logs = ActivityLog.query.filter_by(user_id=sample_user["id"]).all()
            assert any(log.action == "reset_failed" for log in logs)


# ═════════════════════════════════════════════════════════════════════════════
#  CLEANUP
# ═════════════════════════════════════════════════════════════════════════════

class TestOTPCleanup:

    def test_delete_expired_otps_removes_stale_records(self, client, sample_user, app, patch_otp):
        from datetime import datetime, timedelta, timezone
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            record = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).first()
            record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            db.session.commit()

            from app.otp.otp_service import delete_expired_otps
            delete_expired_otps()

            record = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).first()
            assert record is None

    def test_cleanup_runs_on_new_otp_request(self, client, sample_user, app, patch_otp):
        from datetime import datetime, timedelta, timezone
        with app.app_context():
            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})
            record = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).first()
            record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            db.session.commit()

            client.post("/api/auth/forgot-password", json={"email": "otptest@test.com"})

            active = PasswordResetOTP.query.filter_by(user_id=sample_user["id"]).all()
            assert len(active) == 1
