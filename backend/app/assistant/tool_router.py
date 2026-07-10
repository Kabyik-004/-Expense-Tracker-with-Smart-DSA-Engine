import logging
from datetime import datetime, timezone, timedelta
import random

logger = logging.getLogger(__name__)


def _now():
    return datetime.now(timezone.utc)


def _today():
    return _now().date()


def _handle_greeting(entities, user_id):
    return {
        "type": "greeting",
        "text": random.choice([
            "Hello! I'm your AI finance assistant. How can I help you today?",
            "Hi there! Ready to take control of your finances?",
            "Hey! I'm here to help you manage your expenses and budget.",
        ]),
        "suggestions": [
            "Show my recent expenses",
            "Add an expense of ₹500 for food",
            "Give me a spending summary",
        ],
    }


def _handle_help(entities, user_id):
    return {
        "type": "help",
        "text": "Here's what I can help you with:",
        "commands": [
            "Track expenses — \"I spent ₹500 on lunch\"",
            "Add income — \"I earned ₹50000 as salary\"",
            "View summary — \"What's my total spending?\"",
            "Show transactions — \"Show my recent expenses\"",
            "Analytics — \"Give me spending insights\"",
        ],
    }


def _handle_add_expense(entities, user_id):
    amount = entities.get("amount")
    category = entities.get("category")
    desc = entities.get("description")

    if not amount and not category and not desc:
        return {
            "type": "add_expense_prompt",
            "text": "Sure! Please tell me the amount and what you spent on.\n\nExample: *I spent ₹500 on dinner*",
        }

    parts = []
    if amount:
        parts.append(f"₹{amount:,.2f}")
    if category:
        parts.append(f"in **{category.capitalize()}**")
    if desc:
        parts.append(f"for *{desc}*")

    return {
        "type": "add_expense_confirm",
        "text": f"I'd log an expense of {' '.join(parts)}. Shall I save it?",
        "preview": {
            "amount": amount or 0,
            "category": category or "uncategorized",
            "description": desc or "",
            "date": _today().isoformat(),
        },
        "suggestions": ["Yes, save it", "No, cancel"],
    }


def _handle_list_expenses(entities, user_id):
    mock_expenses = [
        {"title": "Lunch at Pizza Hut", "amount": 450.00, "category": "Food & Dining", "date": (_today() - timedelta(days=1)).isoformat()},
        {"title": "Uber ride to office", "amount": 180.00, "category": "Transportation", "date": (_today() - timedelta(days=1)).isoformat()},
        {"title": "Amazon – headphones", "amount": 1299.00, "category": "Shopping", "date": (_today() - timedelta(days=3)).isoformat()},
        {"title": "Netflix subscription", "amount": 649.00, "category": "Entertainment", "date": (_today() - timedelta(days=5)).isoformat()},
        {"title": "Electricity bill", "amount": 2200.00, "category": "Bills & Utilities", "date": (_today() - timedelta(days=7)).isoformat()},
    ]

    category = entities.get("category")
    if category:
        mock_expenses = [e for e in mock_expenses if category.lower() in e["category"].lower()]

    return {
        "type": "expense_list",
        "text": f"Here are your {'filtered ' if category else ''}recent transactions:",
        "expenses": mock_expenses,
        "total": sum(e["amount"] for e in mock_expenses),
    }


def _handle_get_summary(entities, user_id):
    total_income = 85000.00
    total_expense = 29500.00
    balance = total_income - total_expense
    savings_rate = round((balance / total_income) * 100, 1) if total_income else 0

    today = _today()
    top_category = "Food & Dining"
    top_amount = 8250.00

    return {
        "type": "summary",
        "text": f"Here's your financial summary for {today.strftime('%B %Y')}:",
        "income": {"total": total_income, "label": "Total Income", "change": "+5.2% vs last month"},
        "expense": {"total": total_expense, "label": "Total Expenses"},
        "balance": {"total": balance, "label": "Current Balance"},
        "savings_rate": {"value": savings_rate, "label": "Savings Rate"},
        "top_category": {"name": top_category, "amount": top_amount, "label": "Top Spending Category"},
    }


def _handle_add_income(entities, user_id):
    amount = entities.get("amount")
    source = entities.get("source")

    if not amount and not source:
        return {
            "type": "add_income_prompt",
            "text": "Tell me the amount and source of your income.\n\nExample: *I earned ₹50000 as salary*",
        }

    parts = []
    if amount:
        parts.append(f"₹{amount:,.2f}")
    if source:
        parts.append(f"as **{source.capitalize()}**")

    return {
        "type": "add_income_confirm",
        "text": f"I'd log an income of {' '.join(parts)}. Shall I save it?",
        "preview": {
            "amount": amount or 0,
            "source": source or "uncategorized",
            "date": _today().isoformat(),
        },
        "suggestions": ["Yes, save it", "No, cancel"],
    }


def _handle_list_incomes(entities, user_id):
    mock_incomes = [
        {"source": "Salary", "amount": 75000.00, "date": (_today() - timedelta(days=2)).isoformat()},
        {"source": "Freelance", "amount": 8000.00, "date": (_today() - timedelta(days=10)).isoformat()},
        {"source": "Bank Interest", "amount": 2000.00, "date": (_today() - timedelta(days=30)).isoformat()},
    ]

    source = entities.get("source")
    if source:
        mock_incomes = [i for i in mock_incomes if source.lower() in i["source"].lower()]

    return {
        "type": "income_list",
        "text": f"Here are your {'filtered ' if source else ''}income records:",
        "incomes": mock_incomes,
        "total": sum(i["amount"] for i in mock_incomes),
    }


def _handle_get_analytics(entities, user_id):
    return {
        "type": "analytics",
        "text": "Here's a quick look at your spending patterns:",
        "category_breakdown": [
            {"name": "Food & Dining", "amount": 8250.00, "percentage": 28.0},
            {"name": "Bills & Utilities", "amount": 5200.00, "percentage": 17.6},
            {"name": "Shopping", "amount": 4800.00, "percentage": 16.3},
            {"name": "Entertainment", "amount": 4200.00, "percentage": 14.2},
            {"name": "Transportation", "amount": 3800.00, "percentage": 12.9},
            {"name": "Others", "amount": 3250.00, "percentage": 11.0},
        ],
        "insights": [
            "Your food expenses are 28% of total — within healthy range",
            "You spent 16% less on transport this month",
            "Consider setting a shopping budget",
        ],
    }


def _handle_unknown(entities, user_id):
    return {
        "type": "unknown",
        "text": "I'm not sure I understand. Could you rephrase that?",
        "suggestions": [
            "Show my recent expenses",
            "What's my total spending?",
            "Add an expense of ₹200 for coffee",
        ],
    }


_TOOL_MAP = {
    "greeting": _handle_greeting,
    "help": _handle_help,
    "add_expense": _handle_add_expense,
    "list_expenses": _handle_list_expenses,
    "get_summary": _handle_get_summary,
    "add_income": _handle_add_income,
    "list_incomes": _handle_list_incomes,
    "get_analytics": _handle_get_analytics,
    "unknown": _handle_unknown,
}


def route(intent, entities, user_id):
    handler = _TOOL_MAP.get(intent)
    if handler is None:
        logger.warning("No handler for intent '%s'", intent)
        return _handle_unknown(entities, user_id)
    logger.debug("Routing intent '%s' to %s", intent, handler.__name__)
    return handler(entities, user_id)
