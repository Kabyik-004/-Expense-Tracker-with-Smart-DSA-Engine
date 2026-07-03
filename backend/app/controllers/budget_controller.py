from datetime import datetime, timezone

from flask_jwt_extended import get_jwt_identity
from sqlalchemy import func, extract

from app import db
from app.models import Budget, Expense, Category
from app.schemas.budget_schema import SetBudgetSchema, BudgetResponseSchema
from app.utils.responses import success_response, error_response
from app.controllers.activity_controller import log_activity

set_budget_schema = SetBudgetSchema()
budget_response_schema = BudgetResponseSchema()
budget_list_schema = BudgetResponseSchema(many=True)


def list_budgets():
    user_id = int(get_jwt_identity())
    budgets = Budget.query.filter_by(user_id=user_id).order_by(
        Budget.year.desc(), Budget.month.desc(), Budget.category_id.asc().nullsfirst()
    ).all()
    return success_response(
        data={"budgets": budget_list_schema.dump(budgets)},
        message="Budgets retrieved",
    )


def get_budget_status(month=None, year=None):
    user_id = int(get_jwt_identity())
    if month is None:
        month = int(datetime.now(timezone.utc).strftime("%m"))
    if year is None:
        year = int(datetime.now(timezone.utc).strftime("%Y"))

    budgets = Budget.query.filter_by(user_id=user_id, month=month, year=year).all()

    total_budget = 0
    total_spent = 0
    statuses = []

    for budget in budgets:
        spent = 0
        if budget.category_id:
            result = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user_id,
                Expense.category_id == budget.category_id,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            ).scalar()
            spent = float(result)
        else:
            result = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user_id,
                extract("month", Expense.date) == month,
                extract("year", Expense.date) == year,
            ).scalar()
            spent = float(result)

        total_budget += budget.amount
        total_spent += spent
        pct = round((spent / budget.amount) * 100, 1) if budget.amount > 0 else 0

        statuses.append({
            "budget": budget_response_schema.dump(budget),
            "spent": spent,
            "remaining": round(budget.amount - spent, 2),
            "percentage": pct,
            "warning": pct >= 80,
            "exceeded": pct > 100,
        })

    overall_pct = round((total_spent / total_budget) * 100, 1) if total_budget > 0 else 0

    return success_response(
        data={
            "month": month,
            "year": year,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "total_remaining": round(total_budget - total_spent, 2),
            "overall_percentage": overall_pct,
            "overall_warning": overall_pct >= 80,
            "overall_exceeded": overall_pct > 100,
            "budgets": statuses,
        },
        message="Budget status retrieved",
    )


def set_budget(request_data):
    user_id = int(get_jwt_identity())
    data = set_budget_schema.load(request_data)

    cat_id = data.get("category_id")

    existing = Budget.query.filter_by(
        user_id=user_id, category_id=cat_id,
        month=data["month"], year=data["year"],
    ).first()

    if existing:
        existing.amount = data["amount"]
        db.session.commit()
        budget = existing
        msg = "Budget updated"
    else:
        budget = Budget(
            user_id=user_id,
            category_id=cat_id,
            month=data["month"],
            year=data["year"],
            amount=data["amount"],
        )
        db.session.add(budget)
        db.session.commit()
        msg = "Budget created"

    log_activity(user_id, "create" if not existing else "update", "budget", budget.id, msg)

    return success_response(
        data={"budget": budget_response_schema.dump(budget)},
        message=msg,
        status_code=201 if not existing else 200,
    )


def delete_budget(budget_id):
    user_id = int(get_jwt_identity())
    budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
    if not budget:
        return error_response("Budget not found", 404)

    db.session.delete(budget)
    db.session.commit()

    log_activity(user_id, "delete", "budget", budget.id, "Budget deleted")

    return success_response(message="Budget deleted")
