"""
Analytics controller — aggregation, trends, and DSA-powered insights.

Provides comprehensive analytics:
- Totals: Total expense, income, balance
- Extremes: Highest/lowest expense, average expense
- Categories: Most used, top 5, distribution
- Time series: Daily, weekly, monthly breakdown
"""

from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func

from app import db
from app.models.expense import Expense
from app.models.income import Income
from app.models.category import Category
from app.utils.responses import success_response, error_response


# ============================================================================
# BASIC ANALYTICS - Totals, Extremes, Averages
# ============================================================================


def get_total_expenses(user_id):
    """Get total sum of all expenses for user."""
    total = db.session.query(func.sum(Expense.amount)).filter_by(
        user_id=user_id
    ).scalar()
    return float(total) if total else 0.0


def get_total_income(user_id):
    """Get total sum of all income for user."""
    total = db.session.query(func.sum(Income.amount)).filter_by(
        user_id=user_id
    ).scalar()
    return float(total) if total else 0.0


def get_balance(user_id):
    """Get balance: Total Income - Total Expense."""
    total_income = get_total_income(user_id)
    total_expense = get_total_expenses(user_id)
    return total_income - total_expense


def get_highest_expense(user_id):
    """Get highest individual expense amount."""
    expense = Expense.query.filter_by(user_id=user_id).order_by(
        Expense.amount.desc()
    ).first()
    
    if not expense:
        return None
    
    return {
        "id": expense.id,
        "title": expense.title,
        "amount": float(expense.amount),
        "date": expense.date.isoformat(),
        "category_id": expense.category_id,
    }


def get_lowest_expense(user_id):
    """Get lowest individual expense amount."""
    expense = Expense.query.filter_by(user_id=user_id).order_by(
        Expense.amount.asc()
    ).first()
    
    if not expense:
        return None
    
    return {
        "id": expense.id,
        "title": expense.title,
        "amount": float(expense.amount),
        "date": expense.date.isoformat(),
        "category_id": expense.category_id,
    }


def get_average_expense(user_id):
    """Get average expense amount across all expenses."""
    count = db.session.query(func.count(Expense.id)).filter_by(
        user_id=user_id
    ).scalar()
    
    if count == 0:
        return 0.0
    
    total = get_total_expenses(user_id)
    return total / count


# ============================================================================
# CATEGORY ANALYTICS
# ============================================================================


def get_most_used_category(user_id):
    """Get category with most expenses."""
    # Query: count expenses per category
    result = db.session.query(
        Expense.category_id,
        func.count(Expense.id).label("count")
    ).filter_by(user_id=user_id).group_by(
        Expense.category_id
    ).order_by(func.count(Expense.id).desc()).first()
    
    if not result or result[0] is None:
        return None
    
    category_id, count = result
    category = db.session.get(Category, category_id)
    
    return {
        "category_id": category_id,
        "category_name": category.name if category else "Uncategorized",
        "count": count,
    }


def get_top_5_categories(user_id):
    """Get top 5 categories by total expense amount."""
    results = db.session.query(
        Expense.category_id,
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count")
    ).filter_by(user_id=user_id).group_by(
        Expense.category_id
    ).order_by(func.sum(Expense.amount).desc()).limit(5).all()
    
    top_categories = []
    for category_id, total, count in results:
        category = db.session.get(Category, category_id) if category_id else None
        top_categories.append({
            "category_id": category_id,
            "category_name": category.name if category else "Uncategorized",
            "total_amount": float(total) if total else 0.0,
            "expense_count": count,
        })
    
    return top_categories


def get_category_distribution(user_id):
    """Get all categories with their totals and percentages."""
    results = db.session.query(
        Expense.category_id,
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count")
    ).filter_by(user_id=user_id).group_by(
        Expense.category_id
    ).order_by(func.sum(Expense.amount).desc()).all()
    
    # Calculate total for percentages
    grand_total = sum(total for _, total, _ in results)
    if grand_total == 0:
        grand_total = 1  # Avoid division by zero
    
    distribution = []
    raw_percentages = []
    for category_id, total, count in results:
        category = db.session.get(Category, category_id) if category_id else None
        total_float = float(total) if total else 0.0
        raw_pct = (total_float / grand_total) * 100
        raw_percentages.append(raw_pct)
        distribution.append({
            "category_id": category_id,
            "category_name": category.name if category else "Uncategorized",
            "total_amount": total_float,
            "expense_count": count,
        })

    rounded = [round(pct, 2) for pct in raw_percentages]
    if rounded:
        drift = round(100.0 - sum(rounded), 2)
        if drift:
            max_idx = max(range(len(raw_percentages)), key=lambda i: raw_percentages[i])
            rounded[max_idx] = round(rounded[max_idx] + drift, 2)

    for i, item in enumerate(distribution):
        item["percentage"] = rounded[i]

    return distribution


# ============================================================================
# TIME-BASED ANALYTICS - Daily, Weekly, Monthly
# ============================================================================


def get_monthly_expenses(user_id):
    """Get total expenses grouped by month (database-agnostic).
    
    Returns: {
        "2026-07": {"total": 150.50, "count": 5},
        "2026-06": {"total": 200.00, "count": 8},
    }
    """
    expenses = Expense.query.filter_by(user_id=user_id).with_entities(
        Expense.date, Expense.amount
    ).all()

    monthly = defaultdict(lambda: {"total": 0.0, "count": 0})
    for expense in expenses:
        key = expense.date.strftime("%Y-%m")
        monthly[key]["total"] += float(expense.amount)
        monthly[key]["count"] += 1

    return dict(sorted(monthly.items(), reverse=True))


def get_weekly_expenses(user_id):
    """Get total expenses grouped by week (database-agnostic).
    
    Returns: {
        "2026-W27": {"total": 150.50, "count": 5},
        "2026-W26": {"total": 200.00, "count": 8},
    }
    """
    expenses = Expense.query.filter_by(user_id=user_id).with_entities(
        Expense.date, Expense.amount
    ).all()

    weekly = defaultdict(lambda: {"total": 0.0, "count": 0})
    for expense in expenses:
        key = expense.date.strftime("%Y-W%W")
        weekly[key]["total"] += float(expense.amount)
        weekly[key]["count"] += 1

    return dict(sorted(weekly.items(), reverse=True))


def get_daily_expenses(user_id):
    """Get total expenses grouped by day (database-agnostic).
    
    Returns: {
        "2026-07-01": {"total": 150.50, "count": 5},
        "2026-06-30": {"total": 200.00, "count": 8},
    }
    """
    expenses = Expense.query.filter_by(user_id=user_id).with_entities(
        Expense.date, Expense.amount
    ).all()

    daily = defaultdict(lambda: {"total": 0.0, "count": 0})
    for expense in expenses:
        key = expense.date.strftime("%Y-%m-%d")
        daily[key]["total"] += float(expense.amount)
        daily[key]["count"] += 1

    return dict(sorted(daily.items(), reverse=True))


# ============================================================================
# COMPREHENSIVE ANALYTICS DASHBOARD
# ============================================================================


def get_analytics_dashboard(user_id):
    """
    Get complete analytics dashboard with all key metrics.
    
    Returns comprehensive JSON with:
    - Totals: expense, income, balance
    - Extremes: highest, lowest, average
    - Categories: most used, top 5, distribution
    - Time series: last 12 months, last 4 weeks, last 30 days
    """
    total_expense = get_total_expenses(user_id)
    total_income = get_total_income(user_id)
    
    return {
        "summary": {
            "total_expense": total_expense,
            "total_income": total_income,
            "balance": get_balance(user_id),
        },
        "extremes": {
            "highest_expense": get_highest_expense(user_id),
            "lowest_expense": get_lowest_expense(user_id),
            "average_expense": round(get_average_expense(user_id), 2),
        },
        "categories": {
            "most_used": get_most_used_category(user_id),
            "top_5": get_top_5_categories(user_id),
            "distribution": get_category_distribution(user_id),
        },
        "time_series": {
            "monthly": get_monthly_expenses(user_id),
            "weekly": get_weekly_expenses(user_id),
            "daily": get_daily_expenses(user_id),
        },
    }


# ============================================================================
# API RESPONSE FUNCTIONS
# ============================================================================


def analytics_overview(user_id):
    """
    Summary of key metrics: totals, balance, extremes.
    
    Returns: {
      "success": true,
      "data": {
        "total_expense": 500.00,
        "total_income": 3000.00,
        "balance": 2500.00,
        "highest_expense": {...},
        "lowest_expense": {...},
        "average_expense": 50.00
      }
    }
    """
    return success_response(
        data={
            "total_expense": get_total_expenses(user_id),
            "total_income": get_total_income(user_id),
            "balance": get_balance(user_id),
            "highest_expense": get_highest_expense(user_id),
            "lowest_expense": get_lowest_expense(user_id),
            "average_expense": round(get_average_expense(user_id), 2),
        }
    )


def category_analytics(user_id):
    """
    Category breakdown: most used, top 5, full distribution.
    
    Returns: {
      "success": true,
      "data": {
        "most_used_category": {...},
        "top_5_categories": [...],
        "category_distribution": [...]
      }
    }
    """
    return success_response(
        data={
            "most_used_category": get_most_used_category(user_id),
            "top_5_categories": get_top_5_categories(user_id),
            "category_distribution": get_category_distribution(user_id),
        }
    )


def time_series_analytics(user_id):
    """
    Time-based breakdown: daily, weekly, monthly.
    
    Returns: {
      "success": true,
      "data": {
        "daily": {...},
        "weekly": {...},
        "monthly": {...}
      }
    }
    """
    return success_response(
        data={
            "daily": get_daily_expenses(user_id),
            "weekly": get_weekly_expenses(user_id),
            "monthly": get_monthly_expenses(user_id),
        }
    )


def dashboard_analytics(user_id):
    """
    Complete analytics dashboard with all metrics.
    
    Returns all analytics in one response.
    """
    return success_response(data=get_analytics_dashboard(user_id))
