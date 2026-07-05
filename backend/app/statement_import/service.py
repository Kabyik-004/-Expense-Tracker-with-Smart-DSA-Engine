import json
import os
import uuid
from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import exc as sa_exc

from app import db
from app.models.expense import Expense
from app.models.income import Income
from app.models.category import Category
from app.models.bank_statement import BankStatement, ImportLog
from app.controllers.expense_controller import (
    _apply_expense_to_summaries,
    _track_undo_create,
)
from app.controllers.income_controller import _undo_create as _track_income_undo
from app.controllers.activity_controller import log_activity
from app.statement_import.parser import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, FORMAT_MAP


class ImportService:

    @staticmethod
    def validate_file(file_storage):
        if file_storage is None or file_storage.filename is None:
            return {"valid": False, "error": "No file provided"}

        filename = file_storage.filename.strip()
        if not filename:
            return {"valid": False, "error": "Filename is empty"}

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            return {
                "valid": False,
                "error": f"Unsupported file type '{ext}'. Allowed: {allowed}",
            }

        file_storage.seek(0, os.SEEK_END)
        size = file_storage.tell()
        file_storage.seek(0)

        if size > MAX_FILE_SIZE:
            max_mb = MAX_FILE_SIZE // (1024 * 1024)
            return {
                "valid": False,
                "error": f"File exceeds the maximum size of {max_mb} MB",
            }

        return {
            "valid": True,
            "filename": filename,
            "extension": ext,
            "file_type": FORMAT_MAP.get(ext, "unknown"),
            "file_size": size,
        }

    @staticmethod
    def store_temp_file(file_storage, filename):
        upload_dir = os.path.join(
            current_app.instance_path, "uploads"
        )
        os.makedirs(upload_dir, exist_ok=True)

        file_id = str(uuid.uuid4())
        ext = os.path.splitext(filename)[1].lower()
        stored_name = f"{file_id}{ext}"
        stored_path = os.path.join(upload_dir, stored_name)

        file_storage.seek(0)
        file_storage.save(stored_path)

        return {
            "id": file_id,
            "stored_name": stored_name,
            "stored_path": stored_path,
        }

    @staticmethod
    def parse_and_preview(file_id, user_id=None):
        upload_dir = os.path.join(current_app.instance_path, "uploads")
        found = None
        for fname in os.listdir(upload_dir):
            if fname.startswith(file_id):
                found = os.path.join(upload_dir, fname)
                break
        if not found:
            return {"error": f"No uploaded file found with id '{file_id}'"}

        from app.statement_import.parser import parse_file
        result = parse_file(found, categorize=True)

        if user_id:
            from app.statement_import.detector import attach_duplicates_to_preview
            attach_duplicates_to_preview(result, user_id)

        return {
            "file_id": file_id,
            "stored_name": os.path.basename(found),
            "transactions": result.get("transactions", []),
            "report": result.get("report", {}),
            "metadata": result.get("metadata", {}),
            "duplicate_count": result.get("duplicate_count", 0),
        }

    @staticmethod
    def create_statement_record(user_id, filename, file_type, file_size, total_rows):
        raise NotImplementedError

    @staticmethod
    def auto_detect_columns(headers, sample_rows):
        raise NotImplementedError

    @staticmethod
    def build_preview(statement, mapping):
        raise NotImplementedError

    @staticmethod
    def _resolve_category_id(user_id, category_name):
        if not category_name:
            return None
        cat = Category.query.filter_by(user_id=user_id, name=category_name).first()
        if cat:
            return cat.id
        cat = Category.query.filter_by(is_default=True, name=category_name).first()
        if cat:
            return cat.id
        return None

    @staticmethod
    def _create_expense_from_tx(user_id, tx, category_id):
        expense = Expense(
            user_id=user_id,
            title=(tx.get("description") or "Imported Transaction")[:100],
            amount=abs(tx["amount"]),
            description=tx.get("description"),
            date=datetime.strptime(tx["date"], "%Y-%m-%d").date() if tx.get("date") else datetime.now(timezone.utc).date(),
            category_id=category_id,
            payment_method="bank_transfer",
            is_recurring=False,
            notes=f"Imported from bank statement. Ref: {tx.get('reference_number', 'N/A')}" if tx.get("reference_number") else "Imported from bank statement",
        )
        db.session.add(expense)
        db.session.flush()
        _apply_expense_to_summaries(user_id, expense, add=True)
        return expense

    @staticmethod
    def _create_income_from_tx(user_id, tx):
        income = Income(
            user_id=user_id,
            source=(tx.get("description") or "Imported Income")[:100],
            amount=abs(tx["amount"]),
            description=tx.get("description"),
            date=datetime.strptime(tx["date"], "%Y-%m-%d").date() if tx.get("date") else datetime.now(timezone.utc).date(),
            is_recurring=False,
            notes=f"Imported from bank statement. Ref: {tx.get('reference_number', 'N/A')}" if tx.get("reference_number") else "Imported from bank statement",
        )
        db.session.add(income)
        db.session.flush()
        return income

    @staticmethod
    def execute_import(user_id, transactions, file_id=None, filename=None, file_type=None):
        results = {"imported": 0, "skipped": 0, "replaced": 0, "errors": []}
        created_expenses = []
        created_incomes = []

        try:
            for tx in transactions:
                row_index = tx.get("row_index")
                action = tx.get("action", "import")
                if not tx.get("valid"):
                    results["skipped"] += 1
                    if action != "skip":
                        results["errors"].append({"row": row_index, "error": "Skipped invalid transaction"})
                    continue

                if action == "skip":
                    results["skipped"] += 1
                    continue

                category_id = ImportService._resolve_category_id(user_id, tx.get("suggested_category"))
                is_debit = (tx.get("debit") or 0) > 0

                if action == "replace":
                    dup = tx.get("duplicate_matches") or []
                    if dup:
                        expense_id = dup[0].get("expense_id")
                        existing = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
                        if existing:
                            db.session.delete(existing)
                            db.session.flush()

                if is_debit:
                    expense = ImportService._create_expense_from_tx(user_id, tx, category_id)
                    created_expenses.append(expense)
                    results["imported"] += 1
                else:
                    income = ImportService._create_income_from_tx(user_id, tx)
                    created_incomes.append(income)
                    results["imported"] += 1

                if action == "replace":
                    results["replaced"] += 1
                    results["imported"] -= 1

            if file_id:
                ImportService._record_import_log(user_id, file_id, filename, file_type, results, transactions)

            db.session.commit()

        except (sa_exc.SQLAlchemyError, Exception) as e:
            db.session.rollback()
            return {"success": False, "error": f"Import failed: {str(e)}", "results": results}

        for expense in created_expenses:
            _track_undo_create(user_id, expense)
            log_activity(user_id, "create", "expense", expense.id, f"Imported expense: {expense.title}")
        for income in created_incomes:
            _track_income_undo(user_id, income)
            log_activity(user_id, "create", "income", income.id, f"Imported income: {income.source}")

        return {
            "success": True,
            "results": results,
            "created_expense_ids": [e.id for e in created_expenses],
            "created_income_ids": [i.id for i in created_incomes],
        }

    @staticmethod
    def _record_import_log(user_id, file_id, filename, file_type, results, transactions):
        statement = BankStatement(
            user_id=user_id,
            filename=filename or "unknown",
            file_type=file_type or "unknown",
            file_size=0,
            status="imported",
            total_rows=len(transactions),
            parsed_rows=results["imported"],
            imported_rows=results["imported"],
            skipped_rows=results["skipped"],
            error_log=json.dumps(results["errors"]) if results["errors"] else None,
        )
        db.session.add(statement)
        db.session.flush()

        for log_entry in results.get("errors", []):
            log = ImportLog(
                user_id=user_id,
                statement_id=statement.id,
                row_index=log_entry.get("row"),
                status="skipped",
                skip_reason=log_entry.get("error"),
            )
            db.session.add(log)

    @staticmethod
    def get_history(user_id):
        raise NotImplementedError

    @staticmethod
    def get_detail(user_id, statement_id):
        raise NotImplementedError

    @staticmethod
    def delete_import(user_id, statement_id):
        raise NotImplementedError
