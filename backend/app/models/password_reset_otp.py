"""
PasswordResetOTP model
Stores OTP records for the forgot-password flow.
Each record tracks a single OTP sent to a user for password reset.
"""

from datetime import datetime, timezone

from app import db


class PasswordResetOTP(db.Model):
    __tablename__ = "password_reset_otps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_hash = db.Column(db.String(256), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User", backref=db.backref("password_reset_otps", lazy="dynamic"))

    def __repr__(self):
        return f"<PasswordResetOTP user={self.user_id} verified={self.verified}>"
