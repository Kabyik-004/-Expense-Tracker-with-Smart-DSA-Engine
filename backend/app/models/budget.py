from datetime import datetime, timezone

from app import db


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )

    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref=db.backref("budgets", lazy="dynamic"))
    category = db.relationship("Category", backref=db.backref("budgets", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("user_id", "category_id", "month", "year", name="uq_user_category_month_year"),
        db.Index("ix_budgets_user_month_year", "user_id", "month", "year"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "category_icon": self.category.icon if self.category else None,
            "category_color": self.category.color if self.category else None,
            "month": self.month,
            "year": self.year,
            "amount": self.amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        cat = f" ({self.category.name})" if self.category else " (Overall)"
        return f"<Budget {self.month}/{self.year}{cat}: ₹{self.amount}>"
