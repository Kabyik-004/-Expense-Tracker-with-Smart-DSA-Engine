"""
Income model
Stores income records linked to a user.
Mirrors the Expense structure for consistent analytics and comparisons.
"""

from datetime import datetime, timezone

from app import db


class Income(db.Model):
    __tablename__ = "incomes"

    # ── Primary key ──────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Foreign keys ─────────────────────────────────────────────────────
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ── Core fields ──────────────────────────────────────────────────────
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(100), nullable=False)          # e.g. "Salary", "Freelance"
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
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
    user = db.relationship("User", back_populates="incomes")

    # ── Indexes ──────────────────────────────────────────────────────────
    __table_args__ = (
        db.Index("ix_incomes_user_date", "user_id", "date"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "source": self.source,
            "amount": self.amount,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "is_recurring": self.is_recurring,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Income ₹{self.amount} – {self.source}>"
