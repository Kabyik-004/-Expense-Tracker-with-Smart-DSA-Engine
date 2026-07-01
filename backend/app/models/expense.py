"""
Expense model
Stores individual expense records linked to a user and a category.
Supports optional notes, payment method tracking, and recurring flags.
"""

from datetime import datetime, timezone

from app import db


class Expense(db.Model):
    __tablename__ = "expenses"

    # ── Primary key ──────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Foreign keys ─────────────────────────────────────────────────────
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    # ── Core fields ──────────────────────────────────────────────────────
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    date = db.Column(
        db.Date, nullable=False,
        default=lambda: datetime.now(timezone.utc).date()
    )
    payment_method = db.Column(
        db.String(20), nullable=False, default="cash"
    )  # cash | card | upi | bank_transfer
    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.Column(db.Text, nullable=True)

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

    # ── Relationships ────────────────────────────────────────────────────
    user = db.relationship("User", back_populates="expenses")
    category = db.relationship("Category", back_populates="expenses")

    # ── Indexes ──────────────────────────────────────────────────────────
    __table_args__ = (
        db.Index("ix_expenses_user_date", "user_id", "date"),
        db.Index("ix_expenses_user_category", "user_id", "category_id"),
        db.Index("ix_expenses_user_amount", "user_id", "amount"),
    )

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self):
        """Return a dictionary representation for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "payment_method": self.payment_method,
            "is_recurring": self.is_recurring,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Expense ₹{self.amount} – {self.title}>"
