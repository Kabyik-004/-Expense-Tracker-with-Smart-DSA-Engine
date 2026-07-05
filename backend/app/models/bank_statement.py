from datetime import datetime, timezone
from app import db


class BankStatement(db.Model):
    __tablename__ = "bank_statements"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="uploaded"
    )

    total_rows = db.Column(db.Integer, nullable=True)
    parsed_rows = db.Column(db.Integer, nullable=True, default=0)
    imported_rows = db.Column(db.Integer, nullable=True, default=0)
    skipped_rows = db.Column(db.Integer, nullable=True, default=0)
    duplicate_rows = db.Column(db.Integer, nullable=True, default=0)

    raw_headers = db.Column(db.Text, nullable=True)
    detected_mapping = db.Column(db.Text, nullable=True)
    column_preview = db.Column(db.Text, nullable=True)

    error_log = db.Column(db.Text, nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref=db.backref("bank_statements", lazy="dynamic"))

    __table_args__ = (
        db.Index("ix_bank_statements_user_status", "user_id", "status"),
        db.Index("ix_bank_statements_user_created", "user_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "filename": self.filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "status": self.status,
            "total_rows": self.total_rows,
            "parsed_rows": self.parsed_rows,
            "imported_rows": self.imported_rows,
            "skipped_rows": self.skipped_rows,
            "duplicate_rows": self.duplicate_rows,
            "raw_headers": self.raw_headers,
            "detected_mapping": self.detected_mapping,
            "column_preview": self.column_preview,
            "error_log": self.error_log,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<BankStatement {self.filename} [{self.status}]>"


class ImportLog(db.Model):
    __tablename__ = "import_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    statement_id = db.Column(
        db.Integer, db.ForeignKey("bank_statements.id", ondelete="CASCADE"), nullable=True
    )

    row_index = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.String(20), nullable=False, default="pending"
    )

    raw_data = db.Column(db.Text, nullable=True)
    parsed_data = db.Column(db.Text, nullable=True)
    mapped_data = db.Column(db.Text, nullable=True)

    title = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    date = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    category_name = db.Column(db.String(80), nullable=True)

    created_expense_id = db.Column(
        db.Integer, db.ForeignKey("expenses.id", ondelete="SET NULL"), nullable=True
    )

    confidence_score = db.Column(db.Float, nullable=True)
    skip_reason = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    user = db.relationship("User", backref=db.backref("import_logs", lazy="dynamic"))
    statement = db.relationship("BankStatement", backref=db.backref("import_logs", lazy="dynamic"))
    category = db.relationship("Category", backref=db.backref("import_logs", lazy="dynamic"))
    created_expense = db.relationship("Expense", backref=db.backref("import_log", uselist=False))

    __table_args__ = (
        db.Index("ix_import_logs_statement", "statement_id"),
        db.Index("ix_import_logs_user_status", "user_id", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "statement_id": self.statement_id,
            "row_index": self.row_index,
            "status": self.status,
            "raw_data": self.raw_data,
            "parsed_data": self.parsed_data,
            "mapped_data": self.mapped_data,
            "title": self.title,
            "amount": self.amount,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "category_id": self.category_id,
            "category_name": self.category_name,
            "created_expense_id": self.created_expense_id,
            "confidence_score": self.confidence_score,
            "skip_reason": self.skip_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<ImportLog row={self.row_index} status={self.status}>"
