"""
Income controller — authenticated CRUD operations for income records.
"""

import json
from datetime import datetime

from flask_jwt_extended import get_jwt_identity

from app import db
from app.models.income import Income
from app.models.undo_history import UndoHistory
from app.schemas.income_schema import (
    CreateIncomeSchema,
    UpdateIncomeSchema,
    IncomeResponseSchema,
)
from app.utils.responses import success_response, error_response
from app.controllers.activity_controller import log_activity

create_income_schema = CreateIncomeSchema()
update_income_schema = UpdateIncomeSchema()
income_response_schema = IncomeResponseSchema()


def _serialize_income(income):
    """Convert Income object to JSON-serializable dict for undo snapshot."""
    return {
        "id": income.id,
        "user_id": income.user_id,
        "source": income.source,
        "amount": income.amount,
        "description": income.description,
        "date": income.date.isoformat() if income.date else None,
        "is_recurring": income.is_recurring,
        "notes": income.notes,
    }


def _undo_create(user_id, income):
    """Record undo for income creation."""
    undo_history = UndoHistory(
        user_id=user_id,
        action="CREATE",
        entity_type="income",
        entity_id=income.id,
        snapshot=None,
    )
    db.session.add(undo_history)
    db.session.commit()


def _undo_update(user_id, old_income):
    """Record undo for income update."""
    undo_history = UndoHistory(
        user_id=user_id,
        action="UPDATE",
        entity_type="income",
        entity_id=old_income.id,
        snapshot=json.dumps(_serialize_income(old_income)),
    )
    db.session.add(undo_history)
    db.session.commit()


def _undo_delete(user_id, income):
    """Record undo for income deletion."""
    undo_history = UndoHistory(
        user_id=user_id,
        action="DELETE",
        entity_type="income",
        entity_id=income.id,
        snapshot=json.dumps(_serialize_income(income)),
    )
    db.session.add(undo_history)
    db.session.commit()


def create_income(request_data):
    """Create a new income record for the authenticated user."""
    data = create_income_schema.load(request_data)
    user_id = int(get_jwt_identity())

    income_kwargs = {
        "user_id": user_id,
        "source": data["source"],
        "amount": data["amount"],
        "description": data.get("description"),
        "is_recurring": data.get("is_recurring", False),
        "notes": data.get("notes"),
    }
    if data.get("date") is not None:
        income_kwargs["date"] = data["date"]

    income = Income(**income_kwargs)
    db.session.add(income)
    db.session.commit()

    _undo_create(user_id, income)

    log_activity(user_id, "create", "income", income.id, f"Created income: {income.source}")

    return success_response(
        data={"income": income_response_schema.dump(income)},
        message="Income record created successfully",
        status_code=201,
    )


def get_incomes():
    """Return all incomes for the authenticated user."""
    user_id = int(get_jwt_identity())
    incomes = Income.query.filter_by(user_id=user_id).order_by(Income.date.desc()).all()

    return success_response(
        data={"incomes": income_response_schema.dump(incomes, many=True)},
        message="Incomes retrieved successfully",
    )


def get_income(income_id):
    """Return a single income record owned by the authenticated user."""
    user_id = int(get_jwt_identity())
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return error_response("Income record not found", 404)

    return success_response(
        data={"income": income_response_schema.dump(income)},
        message="Income retrieved successfully",
    )


def update_income(income_id, request_data):
    """Update an income record belonging to the authenticated user."""
    data = update_income_schema.load(request_data)
    user_id = int(get_jwt_identity())
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return error_response("Income record not found", 404)

    old_snapshot = Income(
        id=income.id,
        user_id=income.user_id,
        source=income.source,
        amount=income.amount,
        description=income.description,
        date=income.date,
        is_recurring=income.is_recurring,
        notes=income.notes,
    )

    for field in ["source", "amount", "description", "date", "is_recurring", "notes"]:
        if field in data:
            setattr(income, field, data[field])

    db.session.commit()

    _undo_update(user_id, old_snapshot)

    log_activity(user_id, "update", "income", income.id, f"Updated income: {income.source}")

    return success_response(
        data={"income": income_response_schema.dump(income)},
        message="Income record updated successfully",
    )


def delete_income(income_id):
    """Delete an income record belonging to the authenticated user."""
    user_id = int(get_jwt_identity())
    income = Income.query.filter_by(id=income_id, user_id=user_id).first()

    if not income:
        return error_response("Income record not found", 404)

    _undo_delete(user_id, income)
    db.session.delete(income)
    db.session.commit()

    log_activity(user_id, "delete", "income", income.id, f"Deleted income: {income.source}")

    return success_response(message="Income record deleted successfully")


# ── UNDO OPERATIONS ────────────────────────────────────────────────────────


def undo_last_income_operation(user_id):
    """Undo the last income operation (create, update, or delete)."""
    record = (
        UndoHistory.query.filter_by(user_id=user_id, entity_type="income")
        .order_by(UndoHistory.id.desc())
        .first()
    )
    if not record:
        return error_response("No income undo history available", 400)

    try:
        if record.action == "CREATE":
            income = Income.query.filter_by(
                id=record.entity_id, user_id=user_id
            ).first()
            if income:
                db.session.delete(income)
                db.session.delete(record)
                db.session.commit()
                return success_response(
                    data={"income_id": record.entity_id},
                    message=f"Undo: Deleted income {record.entity_id}",
                )

        elif record.action == "UPDATE":
            old_data = json.loads(record.snapshot)
            income = Income.query.filter_by(
                id=record.entity_id, user_id=user_id
            ).first()
            if income:
                income.source = old_data["source"]
                income.amount = old_data["amount"]
                income.description = old_data["description"]
                income.date = datetime.fromisoformat(old_data["date"]).date() if old_data.get("date") else None
                income.is_recurring = old_data["is_recurring"]
                income.notes = old_data["notes"]
                db.session.delete(record)
                db.session.commit()
                return success_response(
                    data={"income": income_response_schema.dump(income)},
                    message=f"Undo: Restored income {record.entity_id} to previous state",
                )

        elif record.action == "DELETE":
            old_data = json.loads(record.snapshot)
            income = Income(
                id=old_data["id"],
                user_id=user_id,
                source=old_data["source"],
                amount=old_data["amount"],
                description=old_data["description"],
                date=datetime.fromisoformat(old_data["date"]).date() if old_data.get("date") else None,
                is_recurring=old_data["is_recurring"],
                notes=old_data["notes"],
            )
            db.session.add(income)
            db.session.delete(record)
            db.session.commit()
            return success_response(
                data={"income": income_response_schema.dump(income)},
                message=f"Undo: Restored deleted income {record.entity_id}",
            )

        return error_response("Unknown undo operation", 400)
    except Exception as e:
        return error_response(f"Undo failed: {str(e)}", 500)
