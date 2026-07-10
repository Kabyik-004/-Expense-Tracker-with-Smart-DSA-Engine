import logging
import re
from datetime import datetime, date as date_type
from flask import current_app

from app.assistant.tool_registry import get_tool, TOOLS_BY_INTENT

logger = logging.getLogger(__name__)

_USER_CATEGORIES = {}


def _load_categories(user_id):
    from app.controllers.category_controller import list_categories
    try:
        resp = list_categories()
        data = resp.get("data", {}) if isinstance(resp, dict) else resp[0].get("data", {})
        cats = data.get("categories", [])
        _USER_CATEGORIES[user_id] = cats
        return cats
    except Exception as e:
        logger.warning("Failed to load categories: %s", e)
        return []


def _resolve_category(user_id, category_name):
    cats = _USER_CATEGORIES.get(user_id)
    if cats is None:
        cats = _load_categories(user_id)
    if not category_name:
        return None
    lower_name = category_name.lower().strip()
    for cat in cats:
        if cat.get("name", "").lower() == lower_name:
            return cat["id"]
    for cat in cats:
        if lower_name in cat.get("name", "").lower():
            return cat["id"]
    return None


def _format_date(date_val):
    if date_val is None:
        today = date_type.today()
        return today.isoformat()
    if isinstance(date_val, str):
        if date_val.lower() in ("today",):
            return date_type.today().isoformat()
        if date_val.lower() in ("yesterday",):
            from datetime import timedelta
            return (date_type.today() - timedelta(days=1)).isoformat()
        if date_val.lower() == "this month":
            return date_type.today().isoformat()
        return date_val
    if isinstance(date_val, (datetime, date_type)):
        return date_val.isoformat()
    return str(date_val)


def _import_controller(module_name):
    parts = module_name.split(".")
    mod_path = "app.controllers." + parts[0]
    mod = __import__(mod_path, fromlist=[parts[1]])
    return getattr(mod, parts[1])


def execute_tool(user_id, intent, entities, message=None):
    tool = get_tool(intent)
    if tool is None:
        return _noop_response(intent, entities)

    controller_path = tool["controller"]
    param_mapping = tool["param_mapping"]

    try:
        controller_fn = _import_controller(controller_path)
    except (ImportError, AttributeError) as e:
        logger.error("Failed to import controller %s: %s", controller_path, e)
        return _fallback_response(intent, entities)

    call_params = _build_params(user_id, intent, entities, param_mapping)

    for req in tool["required_params"]:
        if call_params.get(req) is None:
            return _fallback_response(intent, entities, f"Missing required parameter: {req}")

    try:
        if intent in ("add_expense", "update_expense"):
            result = controller_fn(user_id, call_params)
        elif intent == "delete_expense":
            result = controller_fn(user_id, call_params["expense_id"])
        elif intent == "add_income":
            result = controller_fn(call_params)
        elif intent in ("dashboard_query", "analytics_query", "calendar_query"):
            result = controller_fn(user_id)
        elif intent == "search_expense":
            query = call_params.get("q", "")
            result = controller_fn(user_id, query)
        else:
            result = controller_fn(call_params)
    except Exception as e:
        logger.error("Tool execution failed for %s: %s", intent, e)
        return _fallback_response(intent, entities, str(e))

    return _format_result(intent, entities, result, message)


def _build_params(user_id, intent, entities, param_mapping):
    params = {}
    title_parts = []

    for ent_key, api_key in param_mapping.items():
        val = entities.get(ent_key)
        if val is None:
            continue
        if ent_key == "category":
            resolved = _resolve_category(user_id, str(val))
            if resolved is not None:
                params[api_key] = resolved
        elif ent_key == "date":
            params[api_key] = _format_date(val)
        elif api_key == "title":
            title_parts.append(str(val))
        else:
            params[api_key] = val

    if "title" in param_mapping.values() and "title" not in params:
        if title_parts:
            params["title"] = " ".join(title_parts)
        elif entities.get("notes"):
            params["title"] = entities["notes"][:100]
        elif intent == "add_expense":
            params["title"] = entities.get("category", "Expense")
        elif intent == "add_income":
            params["title"] = entities.get("category", "Income")

    if intent == "add_income":
        if "source" not in params or not params.get("source"):
            params["source"] = entities.get("category", "Income")
        params.pop("title", None)

    return params


def _format_result(intent, entities, result, message=None):
    try:
        if isinstance(result, tuple):
            body = result[0]
        elif isinstance(result, dict):
            body = result
        else:
            body = result
    except Exception:
        body = result

    success = body.get("success", True) if isinstance(body, dict) else True

    if not success:
        msg = body.get("message", "Operation failed") if isinstance(body, dict) else "Operation failed"
        return {"reply": f"Sorry, I couldn't complete that. {msg}"}

    if intent == "add_expense":
        data = body.get("data", {}) if isinstance(body, dict) else {}
        expense = data.get("expense", {}) if isinstance(data, dict) else {}
        return {"reply": _expense_created_text(expense, entities)}

    if intent == "add_income":
        data = body.get("data", {}) if isinstance(body, dict) else {}
        income = data.get("income", {}) if isinstance(data, dict) else {}
        return {"reply": _income_created_text(income, entities)}

    if intent == "delete_expense":
        return {"reply": "Got it! That expense has been deleted."}

    if intent == "update_expense":
        return {"reply": "The expense has been updated successfully."}

    if intent in ("dashboard_query",):
        return {"reply": _dashboard_intelligence(message, body, user_id=None)}

    if intent in ("analytics_query",):
        return {"reply": _analytics_intelligence(message, body)}

    if intent in ("calendar_query",):
        return {"reply": _calendar_intelligence(message, body)}

    if intent == "search_expense":
        return {"reply": _search_text(body)}

    msg = body.get("message", "Done!") if isinstance(body, dict) else "Done!"
    return {"reply": msg}


def _dashboard_intelligence(message, body, user_id=None):
    data = body.get("data", body) if isinstance(body, dict) else {}
    lower = (message or "").lower()

    summary = data.get("summary", {}) if isinstance(data, dict) else {}
    extremes = data.get("extremes", {}) if isinstance(data, dict) else {}
    categories = data.get("categories", {}) if isinstance(data, dict) else {}
    time_series = data.get("time_series", {}) if isinstance(data, dict) else {}

    expense = summary.get("total_expense", 0) if isinstance(summary, dict) else 0
    income = summary.get("total_income", 0) if isinstance(summary, dict) else 0
    balance = summary.get("balance", 0) if isinstance(summary, dict) else 0

    highest = extremes.get("highest_expense", {}) if isinstance(extremes, dict) else {}
    avg = extremes.get("average_expense", 0) if isinstance(extremes, dict) else 0

    top_5 = categories.get("top_5", []) if isinstance(categories, dict) else []
    dist = categories.get("distribution", []) if isinstance(categories, dict) else []
    monthly = time_series.get("monthly", {}) if isinstance(time_series, dict) else {}

    if re.search(r"\b(biggest|largest|highest)\b", lower):
        if isinstance(highest, dict) and highest.get("title"):
            return (
                f"Your biggest expense is *{highest['title']}* "
                f"at \u20b9{highest['amount']:,.0f} on {highest.get('date', 'N/A')}."
            )
        return "I don't have enough expense data to determine the biggest expense yet."

    if re.search(r"\b(savings|save|saved)\b", lower) and not re.search(r"\bspend", lower):
        return (
            f"Your current savings (income - expenses) is *\u20b9{balance:,.0f}*.\n"
            f"Total income: \u20b9{income:,.0f}\n"
            f"Total expenses: \u20b9{expense:,.0f}"
        )

    if re.search(r"\b(overspend|overspending|over budget|over spent|exceeded?)\b", lower):
        over_msg = _check_overspend(user_id)
        if over_msg:
            return over_msg
        if balance >= 0:
            return (
                f"You're currently not overspending. Your balance is \u20b9{balance:,.0f}. "
                f"Total expenses: \u20b9{expense:,.0f} vs Total income: \u20b9{income:,.0f}."
            )
        return (
            f"Your expenses (\u20b9{expense:,.0f}) exceed your income (\u20b9{income:,.0f}). "
            f"Your balance is -\u20b9{abs(balance):,.0f}. You may want to review your spending."
        )

    if re.search(r"\b(top category|top cat|most spent)\b", lower):
        if top_5:
            top = top_5[0]
            return (
                f"Your top spending category is *{top['category_name']}* "
                f"at \u20b9{top['total_amount']:,.0f} across {top['expense_count']} transactions."
            )
        return "No category data available yet."

    if re.search(r"\b(average daily|per day|daily average)\b", lower):
        if monthly:
            current_month_key = date_type.today().strftime("%Y-%m")
            current_month_data = monthly.get(current_month_key)
            if current_month_data:
                from datetime import timedelta
                today = date_type.today()
                days_so_far = max(1, today.day)
                month_total = current_month_data.get("total", 0) if isinstance(current_month_data, dict) else current_month_data
                daily_avg = month_total / days_so_far
                return (
                    f"This month you're averaging *\u20b9{daily_avg:,.0f} per day* "
                    f"(total: \u20b9{month_total:,.0f} over {days_so_far} days)."
                )
        if avg:
            return f"Your average expense per transaction is \u20b9{avg:,.0f}."
        return "Not enough data to compute average daily spending."

    if isinstance(summary, dict) and any(k in summary for k in ("total_expense", "total_income", "balance")):
        lines = [f"Total expenses: \u20b9{expense:,.0f}", f"Total income: \u20b9{income:,.0f}", f"Balance: \u20b9{balance:,.0f}"]
        if isinstance(highest, dict) and highest.get("title"):
            lines.append(f"Biggest expense: {highest['title']} (\u20b9{highest['amount']:,.0f})")
        if top_5:
            lines.append(f"Top category: {top_5[0]['category_name']}")
        if avg:
            lines.append(f"Average per transaction: \u20b9{avg:,.0f}")
        return "Here's your financial dashboard summary:\n" + "\n".join(lines)

    return "Here's your dashboard overview."


def _check_overspend(user_id):
    if user_id is None:
        return None
    try:
        from app.controllers.budget_controller import get_budget_status
        today = date_type.today()
        result = get_budget_status(today.month, today.year)
        if isinstance(result, tuple):
            body = result[0]
        else:
            body = result
        data = body.get("data", {}) if isinstance(body, dict) else {}
        if isinstance(data, dict):
            total_budget = data.get("total_budget", 0)
            total_spent = data.get("total_spent", 0)
            pct = data.get("overall_percentage", 0)
            exceeded = data.get("overall_exceeded", False)
            warning = data.get("overall_warning", False)

            if exceeded:
                return (
                    f"You've exceeded your monthly budget! "
                    f"Spent \u20b9{total_spent:,.0f} of \u20b9{total_budget:,.0f} budget ({pct:.0f}%). "
                    f"Consider reducing discretionary spending."
                )
            if warning:
                return (
                    f"You're close to your budget limit! "
                    f"Spent \u20b9{total_spent:,.0f} of \u20b9{total_budget:,.0f} budget ({pct:.0f}%). "
                    f"You have \u20b9{data.get('total_remaining', 0):,.0f} left."
                )
            if total_budget > 0:
                return (
                    f"You're on track with your budget. "
                    f"Spent \u20b9{total_spent:,.0f} of \u20b9{total_budget:,.0f} budget ({pct:.0f}%). "
                    f"Remaining: \u20b9{data.get('total_remaining', 0):,.0f}."
                )
    except Exception as e:
        logger.warning("Budget check failed: %s", e)
    return None


def _analytics_intelligence(message, body):
    data = body.get("data", body) if isinstance(body, dict) else {}
    lower = (message or "").lower()

    if re.search(r"\b(top category|most used|distribution|breakdown)\b", lower):
        most_used = data.get("most_used_category", {}) if isinstance(data, dict) else {}
        top_5 = data.get("top_5_categories", []) if isinstance(data, dict) else []
        dist = data.get("category_distribution", []) if isinstance(data, dict) else []
        lines = []
        if isinstance(most_used, dict) and most_used.get("category_name"):
            lines.append(f"Most used category: *{most_used['category_name']}* ({most_used['count']} transactions)")
        if top_5:
            lines.append("Top categories by spending:")
            for i, cat in enumerate(top_5[:3], 1):
                lines.append(f"  {i}. {cat['category_name']}: \u20b9{cat['total_amount']:,.0f}")
        if not lines:
            return "No category data available yet."
        return "\n".join(lines)

    if isinstance(data, dict):
        expense = data.get("total_expense", 0)
        income_val = data.get("total_income", 0)
        balance = data.get("balance", 0)
        highest = data.get("highest_expense", {})
        avg = data.get("average_expense", 0)
        lines = [
            f"Total expenses: \u20b9{expense:,.0f}",
            f"Total income: \u20b9{income_val:,.0f}",
            f"Balance: \u20b9{balance:,.0f}",
        ]
        if avg:
            lines.append(f"Average expense: \u20b9{avg:,.0f}")
        if isinstance(highest, dict) and highest.get("title"):
            lines.append(f"Highest: {highest['title']} (\u20b9{highest['amount']:,.0f})")
        return "Analytics overview:\n" + "\n".join(lines)
    return "Here's your analytics overview."


def _calendar_intelligence(message, body):
    data = body.get("data", body) if isinstance(body, dict) else {}
    lower = (message or "").lower()
    monthly = data.get("monthly", {}) if isinstance(data, dict) else {}

    this_month_key = date_type.today().strftime("%Y-%m")

    if re.search(r"\b(this month|current month)\b", lower):
        if monthly and this_month_key in monthly:
            m = monthly[this_month_key]
            total = m.get("total", 0) if isinstance(m, dict) else m
            count = m.get("count", 0) if isinstance(m, dict) else 0
            return f"This month you've spent *\u20b9{total:,.0f}* across {count} transactions."
        return "I don't have data for this month yet."

    if monthly:
        sorted_months = sorted(monthly.items(), key=lambda x: x[0])[-6:]
        current_total = monthly.get(this_month_key, {})
        current_amount = current_total.get("total", 0) if isinstance(current_total, dict) else current_total

        if len(sorted_months) >= 2:
            prev_key = sorted_months[-2][0]
            prev_total = sorted_months[-2][1].get("total", 0) if isinstance(sorted_months[-2][1], dict) else sorted_months[-2][1]
            if prev_total > 0:
                change = ((current_amount - prev_total) / prev_total) * 100
                trend = "up" if change > 0 else "down"
                trend_line = f" ({trend} {abs(change):.0f}% from last month)" if abs(change) > 0 else " (same as last month)"
            else:
                trend_line = ""
        else:
            trend_line = ""

        lines = [f"Your monthly spending trend{trend_line}:"]
        for month_str, info in sorted_months:
            total = info.get("total", 0) if isinstance(info, dict) else info
            count = info.get("count", "") if isinstance(info, dict) else ""
            label = f"  {month_str}: \u20b9{total:,.0f}" + (f" ({count} txns)" if count else "")
            lines.append(label)
        return "\n".join(lines)

    daily = data.get("daily", {}) if isinstance(data, dict) else {}
    if daily:
        sorted_days = sorted(daily.items(), key=lambda x: x[0])[-30:]
        total = sum(d.get("total", 0) if isinstance(d, dict) else d for _, d in sorted_days)
        return f"Your spending over the last 30 days: \u20b9{total:,.0f} across {len(sorted_days)} days."

    return "Here's your time-series data."


def _expense_created_text(expense, entities):
    if not expense:
        return "Expense created successfully!"
    parts = []
    if expense.get("amount"):
        parts.append(f"\u20b9{expense['amount']:,.0f}")
    if expense.get("title"):
        parts.append(f"for {expense['title']}")
    if expense.get("category_name"):
        parts.append(f"in {expense['category_name']}")
    if expense.get("payment_method"):
        parts.append(f"via {expense['payment_method']}")
    if expense.get("date"):
        d = expense["date"]
        if isinstance(d, str):
            parts.append(f"on {d}")
    detail = " ".join(parts) if parts else ""
    return f"Done! Recorded expense {detail}."


def _income_created_text(income, entities):
    if not income:
        return "Income created successfully!"
    parts = []
    if income.get("amount"):
        parts.append(f"\u20b9{income['amount']:,.0f}")
    if income.get("source"):
        parts.append(f"from {income['source']}")
    if income.get("date"):
        d = income["date"]
        if isinstance(d, str):
            parts.append(f"on {d}")
    detail = " ".join(parts) if parts else ""
    return f"Done! Recorded income {detail}."


def _search_text(body):
    data = body.get("data", body) if isinstance(body, dict) else {}
    expenses = data.get("expenses", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    if isinstance(expenses, list):
        if not expenses:
            return "No matching expenses found."
        if len(expenses) == 1:
            e = expenses[0]
            return f"Found 1 expense: {e.get('title', 'N/A')} — \u20b9{e.get('amount', 0):,.0f} on {e.get('date', 'N/A')}."
        return f"Found {len(expenses)} expenses. Top result: {expenses[0].get('title', 'N/A')} — \u20b9{expenses[0].get('amount', 0):,.0f}."
    return "Search completed."


def _fallback_response(intent, entities, error=None):
    prefix = "I tried but couldn't complete that."
    if error:
        prefix += f" ({error})"
    fallbacks = {
        "add_expense": f"{prefix} I'll note it manually: expense of {entities.get('amount', 'N/A')} in {entities.get('category', 'general')}.",
        "add_income": f"{prefix} I'll note it manually: income of {entities.get('amount', 'N/A')}.",
        "delete_expense": f"{prefix} No expense was deleted.",
        "dashboard_query": "I tried to load your dashboard, but it's not available right now.",
        "analytics_query": "I tried to load analytics, but they're not available right now.",
    }
    return {"reply": fallbacks.get(intent, f"{prefix} How else can I help?")}


def _noop_response(intent, entities):
    fallbacks = {
        "navigation_help": "You can navigate using the sidebar menu. I'm here if you need help!",
        "general_help": "I can help you track expenses, manage income, view analytics, and more! Try 'Add expense of 500 for food' or 'Show my dashboard'.",
        "bank_statement_query": "I can help import bank statements. Go to the Import section to upload a statement file.",
        "unknown": "I'm not sure what you mean. Try saying 'Help' to see what I can do.",
    }
    return {"reply": fallbacks.get(intent, "How can I help you with your finances?")}
