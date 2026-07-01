"""
Category model
User-defined expense categories with optional monthly budget limits.
Used by the DSA Engine's graph service for category-relationship analysis
and by the budget optimizer for Knapsack-style allocation.
"""

from datetime import datetime, timezone

from app import db


class Category(db.Model):
    __tablename__ = "categories"

    # ── Primary key ──────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Foreign keys ─────────────────────────────────────────────────────
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ── Core fields ──────────────────────────────────────────────────────
    name = db.Column(db.String(80), nullable=False)
    icon = db.Column(db.String(50), nullable=True, default="📦")     # emoji or icon key
    color = db.Column(db.String(7), nullable=True, default="#6366f1") # hex color for charts
    budget_limit = db.Column(db.Float, nullable=True)                 # monthly budget cap (optional)
    is_default = db.Column(db.Boolean, nullable=False, default=False) # system-provided defaults

    # ── Timestamps ───────────────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ── Relationships ────────────────────────────────────────────────────
    user = db.relationship("User", back_populates="categories")
    expenses = db.relationship(
        "Expense", back_populates="category", lazy="dynamic"
    )

    # ── Constraints ──────────────────────────────────────────────────────
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_user_category_name"),
        db.Index("ix_categories_user_id", "user_id"),
    )

    def __repr__(self):
        return f"<Category {self.name}>"
