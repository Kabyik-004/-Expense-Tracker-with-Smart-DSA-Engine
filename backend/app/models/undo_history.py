"""
UndoHistory model
Stack-based (LIFO) audit log that records every create/update/delete action
on expenses and incomes. Powers the DSA Engine's undo/redo feature using a
stack data structure.

Each entry stores a JSON snapshot of the record *before* the action,
allowing full restoration on undo.
"""

from datetime import datetime, timezone

from app import db


class UndoHistory(db.Model):
    __tablename__ = "undo_history"

    # ── Primary key ──────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Foreign keys ─────────────────────────────────────────────────────
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ── Action metadata ──────────────────────────────────────────────────
    action = db.Column(
        db.String(10), nullable=False
    )  # "CREATE" | "UPDATE" | "DELETE"
    entity_type = db.Column(
        db.String(20), nullable=False
    )  # "expense" | "income"
    entity_id = db.Column(db.Integer, nullable=False)   # PK of the affected record

    # ── Snapshot ─────────────────────────────────────────────────────────
    # JSON-serialized snapshot of the record BEFORE the action.
    # For CREATE actions this is null (nothing existed before).
    # For UPDATE actions this holds the previous field values.
    # For DELETE actions this holds the full record for restoration.
    snapshot = db.Column(db.Text, nullable=True)

    # ── Timestamps ───────────────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────────────────────
    user = db.relationship("User", back_populates="undo_history")

    # ── Indexes ──────────────────────────────────────────────────────────
    __table_args__ = (
        db.Index("ix_undo_user_created", "user_id", "created_at"),
        db.Index("ix_undo_entity", "entity_type", "entity_id"),
    )

    def __repr__(self):
        return f"<UndoHistory {self.action} {self.entity_type}#{self.entity_id}>"
