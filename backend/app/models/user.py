"""
User model
Stores account credentials, profile metadata, and currency preferences.
Each user owns their own expenses, incomes, categories, and undo history.
Includes bcrypt password hashing and password-reset token support.
"""

from datetime import datetime, timezone

import bcrypt

from app import db


class User(db.Model):
    __tablename__ = "users"

    # ── Primary key ──────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Profile ──────────────────────────────────────────────────────────
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    currency = db.Column(db.String(3), nullable=False, default="INR")
    avatar = db.Column(db.Text, nullable=True)

    # ── Password reset ───────────────────────────────────────────────────
    reset_token = db.Column(db.String(256), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)

    # ── Timestamps ───────────────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    password_changed_at = db.Column(
        db.DateTime, nullable=True, default=None
    )

    # ── Relationships ────────────────────────────────────────────────────
    expenses = db.relationship(
        "Expense", back_populates="user", lazy="dynamic",
        cascade="all, delete-orphan"
    )
    incomes = db.relationship(
        "Income", back_populates="user", lazy="dynamic",
        cascade="all, delete-orphan"
    )
    categories = db.relationship(
        "Category", back_populates="user", lazy="dynamic",
        cascade="all, delete-orphan"
    )
    undo_history = db.relationship(
        "UndoHistory", back_populates="user", lazy="dynamic",
        cascade="all, delete-orphan"
    )

    # ── Password helpers ─────────────────────────────────────────────────

    def set_password(self, plain_password):
        """Hash a plain-text password with bcrypt and store it."""
        self.password_hash = bcrypt.hashpw(
            plain_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, plain_password):
        """Verify a plain-text password against the stored hash."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )

    # ── Serialization helper ─────────────────────────────────────────────

    def to_dict(self):
        """Return a safe dictionary representation (no password)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "currency": self.currency,
            "avatar": self.avatar,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<User {self.username}>"
